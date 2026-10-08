from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


st.set_page_config(page_title="Dengue no Brasil", page_icon="🦟", layout="wide")

# Leitura da mesma base usada no notebook
caminho = Path(__file__).parent / "dados" / "simulacao_dengue_brasil.csv"
df = pd.read_csv(caminho)
df["data"] = pd.to_datetime(df["data"])

st.title("Dengue no Brasil")
st.caption("Análise de dados simulados | 2015 a 2024")
st.write("Explore a evolução dos casos e compare os resultados entre regiões e estados.")

# Filtros
st.sidebar.header("Filtros")
st.sidebar.caption("Deixe vazio para mostrar todos os dados.")
anos = st.sidebar.multiselect(
    "Ano", sorted(df["ano"].unique()), placeholder="Todos os anos"
)
regioes = st.sidebar.multiselect(
    "Região", sorted(df["regiao"].unique()), placeholder="Todas as regiões"
)
ufs_disponiveis = df[df["regiao"].isin(regioes)]["uf"] if regioes else df["uf"]
ufs = st.sidebar.multiselect(
    "UF", sorted(ufs_disponiveis.unique()), placeholder="Todas as UFs"
)

dados = df
if anos:
    dados = dados[dados["ano"].isin(anos)]
if regioes:
    dados = dados[dados["regiao"].isin(regioes)]
if ufs:
    dados = dados[dados["uf"].isin(ufs)]

if dados.empty:
    st.warning("Não há dados para os filtros escolhidos.")
    st.stop()

# Indicadores
casos = dados["casos_dengue"].sum()
internacoes = dados["internacoes"].sum()
obitos = dados["obitos"].sum()
taxa_internacao = internacoes / casos * 100 if casos else 0
taxa_mortalidade = obitos / casos * 100 if casos else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("Casos", f"{casos:,}".replace(",", "."))
col2.metric("Internações", f"{internacoes:,}".replace(",", "."))
col3.metric("Óbitos", f"{obitos:,}".replace(",", "."))
col4.metric("Taxa de mortalidade", f"{taxa_mortalidade:.2f}%".replace(".", ","))

st.divider()
st.subheader("Visão dos casos")

casos_ano = dados.groupby("ano", as_index=False)["casos_dengue"].sum()
casos_regiao = dados.groupby("regiao", as_index=False)["casos_dengue"].sum()
casos_uf = dados.groupby("uf", as_index=False)["casos_dengue"].sum()

grafico_ano = px.line(
    casos_ano, x="ano", y="casos_dengue", markers=True,
    title="Evolução por ano",
    labels={"ano": "Ano", "casos_dengue": "Casos"},
)
grafico_ano.update_traces(line_color="#2563eb")
grafico_ano.update_layout(template="plotly_white", xaxis=dict(dtick=1))

grafico_regiao = px.bar(
    casos_regiao.sort_values("casos_dengue", ascending=False),
    x="regiao", y="casos_dengue", title="Casos por região",
    labels={"regiao": "Região", "casos_dengue": "Casos"},
)
grafico_regiao.update_traces(marker_color="#2563eb")
grafico_regiao.update_layout(template="plotly_white")

col_grafico1, col_grafico2 = st.columns(2)
col_grafico1.plotly_chart(grafico_ano)
col_grafico2.plotly_chart(grafico_regiao)

top_ufs = casos_uf.nlargest(10, "casos_dengue").sort_values("casos_dengue")
grafico_uf = px.bar(
    top_ufs, x="casos_dengue", y="uf", orientation="h",
    title="10 UFs com mais casos",
    labels={"uf": "UF", "casos_dengue": "Casos"},
)
grafico_uf.update_traces(marker_color="#0f766e")
grafico_uf.update_layout(template="plotly_white", height=420)
st.plotly_chart(grafico_uf)

with st.expander("Análise temporal: tendência mensal"):
    anos_disponiveis = sorted(dados["ano"].unique())
    ano_temporal = st.selectbox(
        "Ano para analisar mês a mês", anos_disponiveis, index=len(anos_disponiveis) - 1
    )
    dados_ano = dados[dados["ano"] == ano_temporal]
    meses = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
             "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    casos_mes = dados_ano.groupby("mes")["casos_dengue"].sum().reindex(range(1, 13))
    media_movel = casos_mes.rolling(3, min_periods=3).mean()
    variacao_mensal = (casos_mes.pct_change(fill_method=None) * 100).replace(
        [float("inf"), float("-inf")], float("nan")
    )

    tendencia = pd.DataFrame({
        "Mês": meses,
        "Casos": casos_mes.values,
        "Média móvel (3 meses)": media_movel.values,
    })
    grafico_tendencia = px.line(
        tendencia, x="Mês", y=["Casos", "Média móvel (3 meses)"],
        title=f"Casos por mês em {ano_temporal}",
        labels={"value": "Número de casos", "variable": "Série"},
        markers=True,
        category_orders={"Mês": meses},
        color_discrete_map={"Casos": "#2563eb", "Média móvel (3 meses)": "#0f766e"},
    )
    grafico_tendencia.update_layout(template="plotly_white")
    st.plotly_chart(grafico_tendencia)

    tabela_mensal = pd.DataFrame({
        "Mês": meses,
        "Casos": casos_mes.values,
        "Variação em relação ao mês anterior": variacao_mensal.values,
    }).dropna(subset=["Casos"]).tail(6)
    tabela_mensal["Casos"] = tabela_mensal["Casos"].map(
        lambda valor: f"{valor:,.0f}".replace(",", ".")
    )
    tabela_mensal["Variação em relação ao mês anterior"] = tabela_mensal[
        "Variação em relação ao mês anterior"
    ].map(lambda valor: "—" if pd.isna(valor) else f"{valor:+.1f}%".replace(".", ","))
    st.caption("A média móvel começa em março, após três meses de dados. A variação compara cada mês com o anterior.")
    st.dataframe(tabela_mensal, hide_index=True, width="stretch")

with st.expander("Ver dados filtrados"):
    st.dataframe(
        dados[["data", "regiao", "uf", "municipio", "casos_dengue",
               "internacoes", "obitos", "incidencia_100k"]]
        .sort_values("data", ascending=False),
        hide_index=True,
        width="stretch",
    )

st.subheader("Interpretação")
ano_maior = casos_ano.loc[casos_ano["casos_dengue"].idxmax(), "ano"]
uf_maior = casos_uf.loc[casos_uf["casos_dengue"].idxmax(), "uf"]
taxa_internacao_texto = f"{taxa_internacao:.2f}".replace(".", ",")
st.write(
    f"No recorte selecionado, **{ano_maior}** teve mais casos e **{uf_maior}** "
    f"foi a UF com mais registros. A taxa de internação foi de "
    f"**{taxa_internacao_texto}%**."
)

st.subheader("Conclusão")
st.write(
    "Os casos variam entre anos e regiões. A análise ajuda a identificar "
    "os locais que precisam de mais atenção nas ações de prevenção."
)
