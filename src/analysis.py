"""
Agregação dos dados de saída de estoque para descobrir quais peças
mais saem (mais utilizadas), tanto em quantidade quanto em valor.
"""

from __future__ import annotations

import pandas as pd


def ranking_por_quantidade(df_saidas: pd.DataFrame) -> pd.DataFrame:
    """
    Agrupa as saídas por peça (código + descrição) e soma as
    quantidades retiradas do estoque, do maior para o menor.
    """
    agrupado = (
        df_saidas.groupby(["codigo", "descricao"], as_index=False)
        .agg(
            quantidade_total=("quantidade", "sum"),
            valor_total=("valor_unitario", lambda s: (s * df_saidas.loc[s.index, "quantidade"]).sum())
            if "valor_unitario" in df_saidas.columns
            else ("quantidade", "sum"),
            numero_retiradas=("quantidade", "count"),
        )
        .sort_values("quantidade_total", ascending=False)
        .reset_index(drop=True)
    )
    return agrupado


def peca_mais_utilizada(ranking: pd.DataFrame) -> pd.Series:
    """Devolve a linha (peça) com maior quantidade total de saída."""
    if ranking.empty:
        raise ValueError("Não há dados de saída para analisar.")
    return ranking.iloc[0]


def top_n(ranking: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Devolve as N peças mais utilizadas."""
    return ranking.head(n)
