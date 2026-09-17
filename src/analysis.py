"""
Agregação dos dados de saída de estoque para descobrir quais peças
mais saem (mais utilizadas), tanto em quantidade quanto em valor.
"""

from __future__ import annotations

import pandas as pd

from data_loader import extrair_codigo_maquina


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


def ranking_por_maquina(
    df_saidas: pd.DataFrame,
    excluir: list[str] | None = None,
    mapa_nomes: dict[str, str] | None = None,
) -> pd.DataFrame:
    """
    Agrupa as saídas pela coluna "destino" (ex.: "P / RE-454",
    "P / CB-041") para descobrir qual máquina/veículo mais consome
    peças do estoque.

    `excluir` permite remover destinos que não representam uma
    máquina de verdade (ex.: "P / OFICINA", "P / ITATIBA"), que
    costumam aparecer no topo só por serem destinos genéricos.

    `mapa_nomes` (opcional) é o dicionário {código: nome/modelo} vindo
    de `data_loader.carregar_mapa_maquinas`; quando informado, o
    ranking ganha uma coluna "nome_maquina" com o nome/modelo da
    máquina (quando não encontrado, fica como "(não identificada)").
    """
    if "destino" not in df_saidas.columns:
        raise ValueError("A planilha não tem a coluna DESTINO.")

    df = df_saidas.dropna(subset=["destino"]).copy()
    df["destino"] = df["destino"].astype(str).str.strip()

    if excluir:
        excluir_normalizado = {d.strip().upper() for d in excluir}
        df = df[~df["destino"].str.upper().isin(excluir_normalizado)]

    agrupado = (
        df.groupby("destino", as_index=False)
        .agg(
            quantidade_total=("quantidade", "sum"),
            valor_total=("valor_unitario", lambda s: (s * df.loc[s.index, "quantidade"]).sum())
            if "valor_unitario" in df.columns
            else ("quantidade", "sum"),
            numero_retiradas=("quantidade", "count"),
        )
        .sort_values("quantidade_total", ascending=False)
        .reset_index(drop=True)
    )

    if mapa_nomes:
        agrupado["nome_maquina"] = agrupado["destino"].apply(
            lambda destino: mapa_nomes.get(extrair_codigo_maquina(destino), "(não identificada)")
        )

    return agrupado


def maquina_com_mais_saida(ranking_maquinas: pd.DataFrame) -> pd.Series:
    """Devolve a linha (destino/máquina) com maior quantidade total de saída."""
    if ranking_maquinas.empty:
        raise ValueError("Não há dados de destino para analisar.")
    return ranking_maquinas.iloc[0]