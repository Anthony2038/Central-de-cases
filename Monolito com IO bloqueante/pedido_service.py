"""
v1 - Monolito com I/O bloqueante
=================================
Cada pedido e processado de forma inteiramente sincrona: o programa
"trava" (bloqueia) em cada chamada de I/O simulada (rede, banco de dados,
gateway de pagamento, envio de e-mail) antes de seguir para a proxima.

Gargalo: pedidos sao processados um de cada vez, em sequencia. Se cada
pedido leva ~1.4s de I/O, processar 10 pedidos leva ~14s, mesmo que as
etapas de cada pedido sejam totalmente independentes entre si.
"""

import time
from typing import Callable


def verificar_estoque(item: str) -> bool:
    """Simula uma consulta sincrona ao banco de dados de estoque."""
    time.sleep(0.3)
    return True


def processar_pagamento(pedido_id: int, valor: float) -> str:
    """Simula uma chamada sincrona a um gateway de pagamento externo."""
    time.sleep(0.5)
    return f"TX-{pedido_id:04d}"


def enviar_confirmacao_email(pedido_id: int) -> None:
    """Simula o envio sincrono de e-mail via SMTP."""
    time.sleep(0.4)


def atualizar_estoque(item: str) -> None:
    """Simula a escrita sincrona no banco de dados de estoque."""
    time.sleep(0.2)


def processar_pedido(pedido: dict, reportar_progresso: Callable[[int, str], None]) -> dict:
    """
    Pipeline monolitico: cada etapa bloqueia a thread principal ate
    terminar, e o proximo pedido so comeca a ser processado depois
    que o pedido atual passou por TODAS as etapas.
    """
    inicio = time.perf_counter()

    if not verificar_estoque(pedido["item"]):
        reportar_progresso(pedido["id"], "sem estoque")
        return {**pedido, "status": "sem_estoque"}
    reportar_progresso(pedido["id"], "estoque verificado")

    transacao = processar_pagamento(pedido["id"], pedido["valor"])
    reportar_progresso(pedido["id"], "pagamento aprovado")
    enviar_confirmacao_email(pedido["id"])
    reportar_progresso(pedido["id"], "e-mail enviado")
    atualizar_estoque(pedido["item"])
    reportar_progresso(pedido["id"], "estoque atualizado")

    duracao = time.perf_counter() - inicio
    return {**pedido, "status": "concluido", "transacao": transacao, "duracao_s": round(duracao, 3)}


def processar_lote(
    pedidos: list[dict], reportar_progresso: Callable[[int, str], None]
) -> list[dict]:
    """Processa todos os pedidos em sequencia, um apos o outro."""
    return [processar_pedido(p, reportar_progresso) for p in pedidos]
