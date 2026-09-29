# v1 — Monólito com I/O bloqueante

## O que é
Pipeline de processamento de pedidos onde cada etapa (verificar estoque,
cobrar pagamento, enviar e-mail, atualizar estoque) é uma chamada **síncrona**
que bloqueia a thread até responder. Os pedidos são processados **um de
cada vez**, em sequência.

## Como rodar
```bash
python main.py
```

Durante a execucao, o terminal atualiza uma barra de progresso a cada etapa
concluida do pedido atual.

## O gargalo
Cada pedido leva ~1.4s de I/O simulado. Como não há concorrência entre
pedidos, o tempo total escala linearmente com N:

```
tempo_total ≈ N × 1.4s
```

Para 10 pedidos, isso são ~14 segundos, mesmo que as etapas de pedidos
diferentes não dependam umas das outras — o gargalo é puramente
arquitetural (falta de concorrência), não de capacidade real do sistema.


# v2 — Refatorado para concorrência (I/O não-bloqueante)

## O que mudou
As mesmas quatro etapas de I/O agora são `async`/`await` (asyncio). Um
`asyncio.Semaphore` limita quantos pedidos são processados
concorrentemente por vez (evita, por exemplo, saturar um gateway de
pagamento real).

## Como rodar
```bash
python main.py
```

Durante a execucao, o terminal atualiza uma barra de progresso a cada etapa
concluida. As atualizacoes refletem o trabalho dos pedidos concorrentes.

## O ganho
Com concorrência = 5, o tempo total deixa de ser N × 1.4s e passa a se
aproximar de:

```
tempo_total ≈ ceil(N / concorrencia) × 1.4s
```

Para 10 pedidos com concorrência 5, isso são ~2 "ondas" de 1.4s ≈ 2.8s,
em vez de 14s — um ganho de ~5x, sem trocar hardware, só a forma como o
I/O é orquestrado.
