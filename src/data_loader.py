"""
Leitura e limpeza dos dados da planilha de controle de estoque.

A planilha possui várias abas (ESTOQUE, ENTRADAS, SAÍDAS, ...).
Para descobrir qual peça mais sai do estoque, usamos a aba "SAÍDAS",
que registra cada retirada de peça: código, descrição, quantidade,
valor unitário e data.
"""

from __future__ import annotations

import re

import pandas as pd

ABA_SAIDAS = "SAÍDAS"
ABA_ESTOQUE = "ESTOQUE"

# Reconhece descrições da aba ESTOQUE que começam com o código da máquina,
# ex.: "TE-310 TRATOR DE ESTEIRA CATERPILLAR D6" -> código "TE-310"
PADRAO_CODIGO_MAQUINA = re.compile(r"^([A-Z]{1,4}-\d+)\s+(.+)$")

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


def carregar_mapa_maquinas(caminho_planilha: str) -> dict[str, str]:
    """
    Lê a aba ESTOQUE e monta um dicionário {código da máquina: nome/modelo},
    a partir dos itens de patrimônio (código "IMO.*") cuja descrição começa
    com o código da máquina, ex.:

        "TE-310 TRATOR DE ESTEIRA CATERPILLAR D6" -> {"TE-310": "TRATOR DE ESTEIRA CATERPILLAR D6"}

    Nem toda máquina que aparece na coluna DESTINO das saídas está
    cadastrada como patrimônio na aba ESTOQUE (ex.: alguns caminhões),
    então o mapa retornado pode não cobrir 100% dos códigos.
    """
    df = pd.read_excel(caminho_planilha, sheet_name=ABA_ESTOQUE)

    mapa: dict[str, str] = {}
    for codigo, descricao in zip(df.get("CÓDIGO", []), df.get("DESCRIÇÃO", [])):
        if not isinstance(codigo, str) or not codigo.upper().startswith("IMO"):
            continue
        if not isinstance(descricao, str):
            continue

        casamento = PADRAO_CODIGO_MAQUINA.match(descricao.strip())
        if casamento:
            codigo_maquina, nome_maquina = casamento.groups()
            mapa[codigo_maquina] = nome_maquina.strip()

    return mapa


def extrair_codigo_maquina(destino: str) -> str:
    """
    Extrai o código da máquina a partir do texto da coluna DESTINO,
    ex.: "P / TE-310" -> "TE-310".
    """
    return destino.split("/")[-1].strip()