import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Dengue no Brasil", page_icon="🦟", layout="wide")

# Leitura da mesma base usada no notebook
caminho = Path(__file__).parent / "dados" / "simulacao_dengue_brasil.csv"
df = pd.read_csv(caminho)
df["data"] = pd.to_datetime(df["data"])

st.title("Dengue no Brasil")
st.caption("Análise de dados simulados | 2015 a 2024")
st.write("Explore os casos ao longo do tempo e compare regiões e estados.")
st.caption("A base é simulada. Os resultados não representam estatísticas oficiais de saúde.")

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
col4.metric("Óbitos / casos", f"{taxa_mortalidade:.2f}%".replace(".", ","))
total_registros_texto = f"{len(dados):,}".replace(",", ".")
st.caption(
    f"{total_registros_texto} registros · {dados['municipio'].nunique()} municípios · "
    f"{dados['uf'].nunique()} UFs no recorte selecionado"
)

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

incidencia_regiao = (
    dados.groupby("regiao", as_index=False)["incidencia_100k"]
    .mean()
    .sort_values("incidencia_100k")
)
grafico_incidencia = px.bar(
    incidencia_regiao, x="incidencia_100k", y="regiao", orientation="h",
    title="Incidência média por região",
    labels={"regiao": "Região", "incidencia_100k": "Por 100 mil habitantes"},
)
grafico_incidencia.update_traces(marker_color="#2563eb")
grafico_incidencia.update_layout(template="plotly_white", height=420)

col_uf, col_incidencia = st.columns([1.3, 1])
col_uf.plotly_chart(grafico_uf)
col_incidencia.plotly_chart(grafico_incidencia)
st.caption(
    "A incidência exibida é a média dos valores de cada registro da base, "
    "não uma taxa calculada para a população total da região."
)

st.divider()
st.subheader("Mapa por UF")
indicadores_mapa = {
    "Casos": "casos_dengue",
    "Internações": "internacoes",
    "Óbitos": "obitos",
}
indicador_mapa = st.radio(
    "Mostrar no mapa", list(indicadores_mapa), horizontal=True
)
mapa_uf = dados.groupby("uf", as_index=False)[
    ["casos_dengue", "internacoes", "obitos"]
].sum()
codigos_uf = {
    "AM": "13", "BA": "29", "CE": "23", "DF": "53", "ES": "32",
    "GO": "52", "MA": "21", "MG": "31", "MS": "50", "MT": "51",
    "PA": "15", "PB": "25", "PE": "26", "PR": "41", "RJ": "33",
    "RO": "11", "RS": "43", "SC": "42", "SP": "35", "TO": "17",
}
mapa_uf["codigo_ibge"] = mapa_uf["uf"].map(codigos_uf)
malha = json.loads(
    (Path(__file__).parent / "dados" / "malha_estados_ibge.geojson")
    .read_text(encoding="utf-8")
)

grafico_mapa = go.Figure()
grafico_mapa.add_choropleth(
    geojson=malha,
    featureidkey="properties.codarea",
    locations=[estado["properties"]["codarea"] for estado in malha["features"]],
    z=[0] * len(malha["features"]),
    colorscale=[[0, "#e7eef0"], [1, "#e7eef0"]],
    showscale=False,
    marker_line_color="white",
    marker_line_width=0.8,
    hoverinfo="skip",
)
detalhes_mapa = [
    (
        f"<b>{linha.uf}</b><br>Casos: {linha.casos_dengue:,.0f}<br>"
        f"Internações: {linha.internacoes:,.0f}<br>Óbitos: {linha.obitos:,.0f}"
    ).replace(",", ".")
    for linha in mapa_uf.itertuples()
]
grafico_mapa.add_choropleth(
    geojson=malha,
    featureidkey="properties.codarea",
    locations=mapa_uf["codigo_ibge"],
    z=mapa_uf[indicadores_mapa[indicador_mapa]],
    zmin=0,
    zmax=max(int(mapa_uf[indicadores_mapa[indicador_mapa]].max()), 1),
    colorscale=[[0, "#d7f0ed"], [0.5, "#58b3a8"], [1, "#0c7168"]],
    colorbar_title=indicador_mapa,
    marker_line_color="white",
    marker_line_width=0.8,
    text=detalhes_mapa,
    hovertemplate="%{text}<extra></extra>",
)
grafico_mapa.update_geos(fitbounds="locations", visible=False, projection_type="mercator")
grafico_mapa.update_layout(
    height=560,
    margin=dict(l=0, r=0, t=0, b=0),
    separators=",.",
    paper_bgcolor="rgba(0,0,0,0)",
)
st.plotly_chart(grafico_mapa)
st.caption(
    "Passe o mouse sobre uma UF para ver os totais. Em cinza estão as UFs fora "
    "do filtro ou ausentes da base simulada. Contornos: IBGE."
)

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

with st.expander("Chuva, temperatura e casos"):
    corr_chuva = dados["chuva_mm"].corr(dados["casos_dengue"])
    corr_temperatura = dados["temperatura_media"].corr(dados["casos_dengue"])
    texto_chuva = f"{corr_chuva:.2f}".replace(".", ",")
    texto_temperatura = f"{corr_temperatura:.2f}".replace(".", ",")
    st.write(
        f"Correlação com chuva: **{texto_chuva}** · "
        f"Correlação com temperatura: **{texto_temperatura}**. "
        "Os valores mostram associação linear no recorte selecionado; "
        "não indicam que uma variável, sozinha, cause o aumento dos casos."
    )
    grafico_chuva = px.scatter(
        dados, x="chuva_mm", y="casos_dengue", opacity=0.35,
        title="Chuva e casos", color_discrete_sequence=["#0f766e"],
        labels={"chuva_mm": "Chuva (mm)", "casos_dengue": "Casos"},
        hover_data=["municipio", "uf", "ano", "mes"],
    )
    grafico_temperatura = px.scatter(
        dados, x="temperatura_media", y="casos_dengue", opacity=0.35,
        title="Temperatura e casos", color_discrete_sequence=["#2563eb"],
        labels={"temperatura_media": "Temperatura média (°C)", "casos_dengue": "Casos"},
        hover_data=["municipio", "uf", "ano", "mes"],
    )
    grafico_chuva.update_layout(template="plotly_white")
    grafico_temperatura.update_layout(template="plotly_white")
    col_chuva, col_temperatura = st.columns(2)
    col_chuva.plotly_chart(grafico_chuva)
    col_temperatura.plotly_chart(grafico_temperatura)

with st.expander("Ver dados filtrados"):
    st.dataframe(
        dados[["data", "regiao", "uf", "municipio", "casos_dengue",
               "internacoes", "obitos", "incidencia_100k"]]
        .sort_values("data", ascending=False),
        hide_index=True,
        width="stretch",
    )
    st.download_button(
        "Baixar dados filtrados (CSV)",
        dados.to_csv(index=False).encode("utf-8-sig"),
        file_name="dengue_filtrada.csv",
        mime="text/csv",
    )

st.subheader("Interpretação")
ano_maior = casos_ano.loc[casos_ano["casos_dengue"].idxmax(), "ano"]
uf_maior = casos_uf.loc[casos_uf["casos_dengue"].idxmax(), "uf"]
regiao_maior = casos_regiao.loc[casos_regiao["casos_dengue"].idxmax(), "regiao"]
casos_regiao_maior = casos_regiao["casos_dengue"].max()
participacao_regiao = casos_regiao_maior / casos * 100 if casos else 0
taxa_internacao_texto = f"{taxa_internacao:.2f}".replace(".", ",")
participacao_texto = f"{participacao_regiao:.1f}".replace(".", ",")
st.write(
    f"No recorte selecionado, **{ano_maior}** teve mais casos e **{uf_maior}** "
    f"foi a UF com mais registros. A região **{regiao_maior}** reuniu "
    f"**{participacao_texto}%** dos casos. A taxa de internação foi de "
    f"**{taxa_internacao_texto}%**."
)

st.subheader("Conclusão")
st.write(
    "Os casos variam entre anos e regiões. A análise ajuda a identificar "
    "os locais que precisam de mais atenção nas ações de prevenção."
)
