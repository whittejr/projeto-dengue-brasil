# Análise da dengue no Brasil

Este é meu projeto da avaliação G1 de Análise e Visualização de Dados com Python. Usei uma base simulada de dengue no Brasil para comparar os casos entre 2015 e 2024, observar diferenças entre regiões e estados e montar um dashboard com filtros.

Os dados são **simulados**. Os números apresentados aqui não são estatísticas oficiais de saúde.

## O que eu analisei

No [notebook](notebooks/analise_dengue.ipynb), fiz a leitura e preparação da base, calculei indicadores e criei gráficos. Também analisei a relação dos casos com chuva e temperatura. No [dashboard](app.py), é possível filtrar os dados por ano, região e UF e ver como os resultados mudam.

Na base completa, encontrei 3.560.562 casos, 178.670 internações e 5.314 óbitos. O ano com mais casos foi 2018. A região Sudeste e o estado do Rio de Janeiro tiveram os maiores totais em suas categorias.

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