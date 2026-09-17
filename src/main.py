"""
Ponto de entrada do programa.

Uso:
    python src/main.py caminho/para/planilha.xlsx [--top 10] [--csv saida.csv] [--grafico grafico.png]
"""

from __future__ import annotations

import argparse
import sys

from data_loader import carregar_saidas
from analysis import ranking_por_quantidade, peca_mais_utilizada, top_n


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analisa a planilha de controle de estoque e mostra quais peças mais saem."
    )
    parser.add_argument("planilha", help="Caminho para o arquivo .xlsx de controle de estoque")
    parser.add_argument("--top", type=int, default=10, help="Quantidade de peças no ranking (padrão: 10)")
    parser.add_argument("--csv", help="Caminho para salvar o ranking completo em CSV")
    parser.add_argument("--grafico", help="Caminho para salvar um gráfico de barras com o Top N")
    return parser.parse_args()


def imprimir_ranking(ranking, n: int) -> None:
    principais = top_n(ranking, n)
    print(f"\n=== TOP {n} PEÇAS QUE MAIS SAEM DO ESTOQUE ===\n")
    for i, linha in principais.iterrows():
        print(
            f"{i + 1:>2}. [{linha['codigo']}] {linha['descricao']}\n"
            f"     Quantidade total: {linha['quantidade_total']:.0f}"
            f" | Nº de retiradas: {linha['numero_retiradas']}"
            f" | Valor total: R$ {linha['valor_total']:.2f}"
        )

    campea = peca_mais_utilizada(ranking)
    print("\n>>> Peça campeã de saída:")
    print(f"    [{campea['codigo']}] {campea['descricao']} — {campea['quantidade_total']:.0f} unidades")


def gerar_grafico(ranking, n: int, caminho: str) -> None:
    import matplotlib.pyplot as plt

    principais = top_n(ranking, n).iloc[::-1]  # inverte para o maior ficar no topo do gráfico
    plt.figure(figsize=(9, 6))
    plt.barh(principais["descricao"], principais["quantidade_total"], color="#3b7dd8")
    plt.xlabel("Quantidade total de saídas")
    plt.title(f"Top {n} peças que mais saem do estoque")
    plt.tight_layout()
    plt.savefig(caminho)
    print(f"\nGráfico salvo em: {caminho}")


def main() -> None:
    args = parse_args()

    try:
        df_saidas = carregar_saidas(args.planilha)
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {args.planilha}", file=sys.stderr)
        sys.exit(1)

    ranking = ranking_por_quantidade(df_saidas)

    imprimir_ranking(ranking, args.top)

    if args.csv:
        ranking.to_csv(args.csv, index=False, encoding="utf-8-sig")
        print(f"\nRanking completo salvo em: {args.csv}")

    if args.grafico:
        gerar_grafico(ranking, args.top, args.grafico)


if __name__ == "__main__":
    main()