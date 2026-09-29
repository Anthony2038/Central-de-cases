"""Executa o processamento de um lote de pedidos na versao monolitica (v1)."""
import time
from pedido_service import processar_lote

PEDIDOS = [
    {"id": i, "item": f"SKU-{i % 5}", "valor": 100 + i * 10}
    for i in range(1, 11)
]

if __name__ == "__main__":
    print(f"[v1] Processando {len(PEDIDOS)} pedidos de forma sequencial/bloqueante...\n")
    etapas_concluidas = 0
    total_etapas = len(PEDIDOS) * 4

    def reportar_progresso(pedido_id: int, etapa: str) -> None:
        global etapas_concluidas
        etapas_concluidas += 1
        barra = "#" * (etapas_concluidas * 24 // total_etapas)
        barra = barra.ljust(24, ".")
        print(
            f"\r[v1] [{barra}] {etapas_concluidas:>2}/{total_etapas} etapas | "
            f"Pedido {pedido_id}: {etapa:<20}",
            end="",
            flush=True,
        )

    inicio = time.perf_counter()
    resultados = processar_lote(PEDIDOS, reportar_progresso)
    total = time.perf_counter() - inicio
    print("\n")

    for r in resultados:
        print(f"  pedido {r['id']:>2} | status={r['status']:<10} | transacao={r.get('transacao', '-')}")

    print(f"\n[v1] Tempo total: {total:.2f}s  (~{total / len(PEDIDOS):.2f}s por pedido, em serie)")
