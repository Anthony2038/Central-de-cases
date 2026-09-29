"""Executa o processamento de um lote de pedidos na versao concorrente (v2)."""
import asyncio
import time
from pedido_service import processar_lote

PEDIDOS = [
    {"id": i, "item": f"SKU-{i % 5}", "valor": 100 + i * 10}
    for i in range(1, 11)
]

CONCORRENCIA = 5  # quantos pedidos podem estar "em voo" ao mesmo tempo


async def main():
    print(f"[v2] Processando {len(PEDIDOS)} pedidos concorrentemente (limite={CONCORRENCIA})...\n")
    etapas_concluidas = 0
    total_etapas = len(PEDIDOS) * 4

    def reportar_progresso(pedido_id: int, etapa: str) -> None:
        nonlocal etapas_concluidas
        etapas_concluidas += 1
        barra = "#" * (etapas_concluidas * 24 // total_etapas)
        barra = barra.ljust(24, ".")
        print(
            f"\r[v2] [{barra}] {etapas_concluidas:>2}/{total_etapas} etapas | "
            f"Pedido {pedido_id}: {etapa:<20}",
            end="",
            flush=True,
        )

    inicio = time.perf_counter()
    resultados = await processar_lote(
        PEDIDOS,
        concorrencia=CONCORRENCIA,
        reportar_progresso=reportar_progresso,
    )
    total = time.perf_counter() - inicio
    print("\n")

    for r in resultados:
        print(f"  pedido {r['id']:>2} | status={r['status']:<10} | transacao={r.get('transacao', '-')}")

    print(f"\n[v2] Tempo total: {total:.2f}s  (concorrencia={CONCORRENCIA})")


if __name__ == "__main__":
    asyncio.run(main())
