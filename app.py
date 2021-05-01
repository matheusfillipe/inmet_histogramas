import subprocess
import datetime
import glob
from pathlib import Path
from zipfile import ZipFile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
import SessionState

zips = [name for name in glob.glob(r"data/[0-9][0-9][0-9][0-9].zip")]
if len(zips) < 1:
    subprocess.Popen("./download.pl" , shell=True)

subprocess.Popen("./update.pl" , shell=True)


def list_zips():
    i = -1
    zip_file = ZipFile(zips[i])
    for text_file in zip_file.infolist():
        if text_file.filename.upper().endswith(".CSV"):
            yield text_file.filename.lower()[6:-28]


def display(search):
    column = 'PRECIPITAÇÃO TOTAL, HORÁRIO (mm)'

    @st.cache
    def getData():
        dfs = []
        years = []
        for zip_filename in zips:
            zip_file = ZipFile(zip_filename)
            new = { text_file.filename:
                pd.read_csv(
                    zip_file.open(text_file.filename),
                    header=8,
                    sep=";",
                    quotechar='"',
                    encoding="ISO-8859-1",
                )
                for text_file in zip_file.infolist()
                if text_file.filename.upper().endswith(".CSV")
                and search.upper().strip() in Path(text_file.filename.upper()).stem.strip()
            }
            year = Path(zip_filename).stem
            if len(new) == 0:
                continue
            _, new = list(new.items())[0]
            try:
                new["time"] = new["Data"].apply(
                    lambda x: datetime.datetime.strptime(x, "%Y/%m/%d")
                )
            except KeyError:
                new["time"] = new["DATA (YYYY-MM-DD)"].apply(
                    lambda x: datetime.datetime.strptime(str(datetime.datetime.strptime(x, "%Y-%m-%d"))[:-9], "%Y-%m-%d")
                )

            new[column] = new[column].str.replace("-9999", "0")
            new[column] = new[column].str.replace(",", ".").astype(float)
            dfs += [new]
            years.append(year)
        return years, dfs


    years, dfs = getData()
    left_column, right_column = st.beta_columns(2)
    with left_column:
        year = st.selectbox("Ano: ", years)

    if year in years:
        i = years.index(year)
        df = dfs[i]

        with right_column:
            daily = st.selectbox("Modo", ["monthly", "daily"]) == "daily"
            if daily:
                s = df.groupby(pd.Grouper(freq="d", key="time"))[column].sum()
            else:
                s = df.groupby(pd.Grouper(freq="M", key="time"))[column].sum()

        a = df.groupby(pd.Grouper(freq="Y", key="time"))[column].sum().to_frame()
        total_label="Precipitação Total Anual(mm)"
        a = a.rename(columns={column: total_label})

        time = []
        data = []
        for k,v in s.items():
            time.append(str(k)[:-9])
            data.append(v)
        df = pd.DataFrame()
        df['Data'] = time
        df["Precipitação mm"] = data

        fig = px.histogram(df, x='Data', y="Precipitação mm", labels={'x': "Data", 'y': "mm"}, nbins=len(df['Data']))
        fig.update_layout(width=900,height=450)
        "* * *"


        desc = f"### {search.upper().replace('_', ' ')} - {year}"
        st.markdown(desc)
        hold = st.button("Keep")

        avg = round(a[total_label][0]/len(df['Data']), 3)
        if not daily:
            avg_lbl=f"**Média mensal no ano:** {avg} mm"
        else:
            avg_lbl=f"**Média diária no ano:** {avg} mm"
        st.markdown(avg_lbl)
        st.write(a)

        st.plotly_chart(fig)


        return hold, fig, a, desc, avg_lbl



# PAGE
st.set_page_config(  # Alternate names: setup_page, page, layout
	layout="wide",  # Can be "centered" or "wide". In the future also "dashboard", etc.
	initial_sidebar_state="auto",  # Can be "auto", "expanded", "collapsed"
	page_title=None,  # String or None. Strings get appended with "• Streamlit". 
	page_icon=None,  # String, anything supported by st.image, or None.
)

with open("style.css") as f:
    st.markdown('<style>{}</style>'.format(f.read()), unsafe_allow_html=True)
session_state = SessionState.get(plots=[])
st.title("Precipitação Mensal")
"**Mapa das estações:** https://mapas.inmet.gov.br"
search = st.selectbox("Estação", [Path(name).stem for name in list_zips()])

hold, fig, a, desc, lbl = display(search)

if hold:
    session_state.plots.append((fig, a, desc, lbl))

if len(session_state.plots) > 0 and st.button('clear'):
    session_state.plots = []

for fig, a, desc, lbl in session_state.plots:
    st.markdown(desc)
    st.write(a)
    st.markdown(lbl)
    st.plotly_chart(fig)



"* * *"
components.iframe("https://mapas.inmet.gov.br/", height=700)
