"""
v2 - Refatorado para concorrencia (assincrono)
================================================
As mesmas quatro etapas de I/O agora sao nao-bloqueantes (asyncio).
Multiplos pedidos sao processados concorrentemente: enquanto um pedido
esta "esperando" o gateway de pagamento responder, a CPU ja pode
avancar outro pedido. O tempo total deixa de ser proporcional a N
(quantidade de pedidos) e passa a ser proporcional a etapa mais lenta
de UM pedido, dado um grau de concorrencia suficiente.
"""

import asyncio
import time
from typing import Callable


async def verificar_estoque(item: str) -> bool:
    await asyncio.sleep(0.3)
    return True


async def processar_pagamento(pedido_id: int, valor: float) -> str:
    await asyncio.sleep(0.5)
    return f"TX-{pedido_id:04d}"


async def enviar_confirmacao_email(pedido_id: int) -> None:
    await asyncio.sleep(0.4)


async def atualizar_estoque(item: str) -> None:
    await asyncio.sleep(0.2)


async def processar_pedido(
    pedido: dict,
    semaforo: asyncio.Semaphore,
    reportar_progresso: Callable[[int, str], None],
) -> dict:
    """
    Mesmo pipeline de negocio da v1, mas cada etapa 'cede' o controle
    (await) em vez de travar a thread. O semaforo limita quantos
    pedidos rodam concorrentemente ao mesmo tempo (evita saturar o
    gateway de pagamento simulado, por exemplo).
    """
    async with semaforo:
        inicio = time.perf_counter()

        if not await verificar_estoque(pedido["item"]):
            reportar_progresso(pedido["id"], "sem estoque")
            return {**pedido, "status": "sem_estoque"}
        reportar_progresso(pedido["id"], "estoque verificado")

        transacao = await processar_pagamento(pedido["id"], pedido["valor"])
        reportar_progresso(pedido["id"], "pagamento aprovado")
        await enviar_confirmacao_email(pedido["id"])
        reportar_progresso(pedido["id"], "e-mail enviado")
        await atualizar_estoque(pedido["item"])
        reportar_progresso(pedido["id"], "estoque atualizado")

        duracao = time.perf_counter() - inicio
        return {**pedido, "status": "concluido", "transacao": transacao, "duracao_s": round(duracao, 3)}


async def processar_lote(
    pedidos: list[dict],
    concorrencia: int = 5,
    reportar_progresso: Callable[[int, str], None] | None = None,
) -> list[dict]:
    """Processa todos os pedidos concorrentemente, respeitando um limite de concorrencia."""
    if reportar_progresso is None:
        reportar_progresso = lambda pedido_id, etapa: None
    semaforo = asyncio.Semaphore(concorrencia)
    tarefas = [processar_pedido(p, semaforo, reportar_progresso) for p in pedidos]
    return await asyncio.gather(*tarefas)
