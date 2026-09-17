# Análise de Estoque

Programa em Python que analisa a planilha de controle de estoque
(`CONTROLE_DE_ESTOQUE_GRAM_PAV.xlsx`) e identifica quais peças mais saem
do estoque (mais utilizadas/vendidas), a partir da aba **SAÍDAS**.

## Estrutura do projeto

```
analise-estoque/
├── README.md
├── requirements.txt
├── data/                  # coloque aqui a planilha .xlsx (não versionada)
└── src/
    ├── data_loader.py     # leitura e limpeza dos dados da planilha
    ├── analysis.py        # lógica de agregação e ranking das peças
    └── main.py            # ponto de entrada (CLI)
```

## Instalação

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Uso

```bash
python src/main.py caminho/para/CONTROLE_DE_ESTOQUE_GRAM_PAV.xlsx
```

Parâmetros opcionais:

```bash
python src/main.py planilha.xlsx --top 10 --csv relatorio.csv --grafico grafico.png
```

- `--top N` : quantidade de peças a exibir no ranking (padrão: 10)
- `--csv arquivo.csv` : salva o ranking completo em CSV
- `--grafico arquivo.png` : gera um gráfico de barras com o Top N

## Saída

O programa imprime no terminal uma tabela com:

- Código da peça
- Descrição
- Quantidade total de saídas
- Valor total movimentado (quando disponível)

E aponta a peça campeã de saída.
