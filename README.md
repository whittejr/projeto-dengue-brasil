# Análise da dengue no Brasil

- **Projeto:** Avaliação G1 — Tema 1
- **Disciplina:** Linguagem de Programação — Análise e Visualização de Dados com Python
- **Aluno:** Alessandro Davi
- **Professor:** Alexandre Neves Louzada

Este é meu projeto da avaliação G1 de Análise e Visualização de Dados com Python. Usei uma base simulada de dengue no Brasil para comparar os casos entre 2015 e 2024, observar diferenças entre regiões e estados e montar um dashboard com filtros.

Os dados são **simulados**. A base tem 4.440 registros de 37 municípios em 20 UFs; portanto, os números não são estatísticas oficiais de saúde nem cobrem todos os municípios do país.

## O que eu analisei

No [notebook](notebooks/analise_dengue.ipynb), fiz a leitura e preparação da base, calculei indicadores e criei gráficos. Também analisei a relação dos casos com chuva e temperatura. No [dashboard](app.py), é possível filtrar por ano, região e UF, comparar casos e incidência, acompanhar a tendência mensal e baixar o recorte em CSV.

Na base completa, encontrei 3.560.562 casos, 178.670 internações e 5.314 óbitos. O ano com mais casos foi 2018. O Sudeste teve mais casos em números absolutos, enquanto o Nordeste apresentou a maior média do indicador de incidência da base. Isso mostra por que vale olhar tanto os totais quanto as taxas.

## Como executar o dashboard

Com Python instalado, abra um terminal na pasta do projeto e rode:

```bash
pip install -r requirements.txt
streamlit run app.py
```

O arquivo CSV precisa permanecer na pasta `dados/`, pois é ele que o notebook e o dashboard utilizam.

## Arquivos principais

- `notebooks/analise_dengue.ipynb`: análise completa.
- `app.py`: dashboard em Streamlit.
- `dados/simulacao_dengue_brasil.csv`: base simulada utilizada.
- `index.html`: página de apresentação para o GitHub Pages.
- `requirements.txt`: bibliotecas necessárias para executar o app.

Usei Pandas, Matplotlib e Seaborn na análise; o dashboard usa Streamlit e Plotly.

## Links da entrega

- [Repositório no GitHub](https://github.com/whittejr/projeto-dengue-brasil)
- [Página do projeto](https://whittejr.github.io/projeto-dengue-brasil/)
- [Dashboard interativo](https://projeto-dengue-brasill.streamlit.app/)
