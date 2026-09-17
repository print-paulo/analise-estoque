"""
Leitura e limpeza dos dados da planilha de controle de estoque.

A planilha possui várias abas (ESTOQUE, ENTRADAS, SAÍDAS, ...).
Para descobrir qual peça mais sai do estoque, usamos a aba "SAÍDAS",
que registra cada retirada de peça: código, descrição, quantidade,
valor unitário e data.
"""

from __future__ import annotations

import pandas as pd

ABA_SAIDAS = "SAÍDAS"

COLUNAS_ESPERADAS = {
    "CÓDIGO": "codigo",
    "DESCRIÇÃO": "descricao",
    "SAIDA": "quantidade",
    "V. UNT.": "valor_unitario",
    "DATA": "data",
    "MECÂNICO": "mecanico",
    "DESTINO": "destino",
}


def carregar_saidas(caminho_planilha: str) -> pd.DataFrame:
    """
    Lê a aba de SAÍDAS da planilha e devolve um DataFrame limpo,
    pronto para ser analisado.

    Linhas sem código de peça ou sem quantidade (ex.: anotações como
    "INICIO DO CONTROLE 01/06/2016") são descartadas.
    """
    df = pd.read_excel(caminho_planilha, sheet_name=ABA_SAIDAS)

    # Mantém apenas as colunas que realmente existem na planilha
    colunas_presentes = {
        original: novo
        for original, novo in COLUNAS_ESPERADAS.items()
        if original in df.columns
    }
    df = df[list(colunas_presentes.keys())].rename(columns=colunas_presentes)

    # Remove linhas de anotação / sem dados úteis
    df = df.dropna(subset=["codigo", "quantidade"])

    # Garante tipos corretos
    df["quantidade"] = pd.to_numeric(df["quantidade"], errors="coerce")
    df = df.dropna(subset=["quantidade"])

    if "valor_unitario" in df.columns:
        df["valor_unitario"] = pd.to_numeric(df["valor_unitario"], errors="coerce").fillna(0)

    df["codigo"] = df["codigo"].astype(str).str.strip()
    df["descricao"] = df["descricao"].astype(str).str.strip()

    return df.reset_index(drop=True)