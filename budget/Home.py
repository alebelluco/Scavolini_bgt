import streamlit as  st 
import pandas as pd 
from utils import dataprep as dp
from matplotlib import pyplot as plt
import plotly_express as px

st.set_page_config(layout='wide')

#st.image('https://github.com/alebelluco/Scavolini/blob/main/Scav.png?raw=True')
#st.divider()

path1 = st.file_uploader('Caricare entrata merce')
if not path1:
    st.stop()
path2 = st.file_uploader('Caricare db articolo fornitore')
if not path2:
    st.stop()

df = pd.read_excel(path1)
fornitori = pd.read_excel(path2)


#df = pd.read_excel('/Users/Alessandro/Documents/AB/Clienti/ADI!/Scavolini/Budget/estrazioni/23_24.xlsx')
#fornitori = pd.read_excel('/Users/Alessandro/Documents/AB/Clienti/ADI!/Scavolini/Budget/estrazioni/cod_forn.xlsx')

anno = st.radio('selezionare anno', options=[2023,2024])

df = df[[data.year == anno for data in df['Data doc.']]]

layout = [
    "Articolo",
    "Descrizione materiale",
    "Quantità",
    "Importo DI",
    "Data doc.",
    "importo_unitario"
    ]

layout2 = [
    "Articolo",
    "Descrizione materiale",
    "Quantità",
    "Importo DI",
    "Data doc.",
    "importo_unitario",
    'mese'
    ]

filtro_group = [
     "Articolo",
    "Descrizione materiale",
    "mese",
    ]

df['importo_unitario'] = df['Importo DI']/df['Quantità']

df = df[df['importo_unitario'] > 0.01]

df = df[layout]
df['mese'] = [data.month for data in df['Data doc.']]
df['key'] = None
for i in range(len(df)):
    df['key'].iloc[i] = str(df['Articolo'].iloc[i]) + '--' + str(df['mese'].iloc[i])

#st.write(df)
#--------
articoli = list(df.Articolo.unique())
deltas = pd.DataFrame(columns=['key','delta_listino'])

for articolo in articoli:
    out = dp.calcolo_delta(df,articolo,layout2,filtro_group)
    deltas = pd.concat([deltas,out])


#st.write(deltas)


df = df.merge(deltas, how='left', left_on='key',right_on='key')
df['saving'] = -1*df['delta_listino']*df['Quantità']



# QUI INSERIAMO IL FILTRO SUL FORNITORE
#------------------------

colonne=[
  "Materiale",
  "Fornitore",
  "Ragione sociale"
]
fornitori = fornitori[colonne]
#st.write(fornitori)

scelta = st.multiselect('Selezionare il fornitore', options=fornitori['Ragione sociale'].unique())
if not scelta:
    st.stop()
df['chiave_fornitore'] = df['Articolo'].astype(str)
df = df.merge(fornitori, how='left', left_on='chiave_fornitore', right_on='Materiale')
df = df[[any(fornitore in check for fornitore in scelta) for check in df['Ragione sociale'].astype(str)]]
#df = df[[data.year == 2024 for data in df['Data doc.']]]

#------------------------

st.dataframe(df, width=2000)

st.subheader('Saving totale: {:0,.0f} €'.format(df['saving'].sum()).replace(',', '.'))

cum = df[['mese','saving']].groupby(by='mese',as_index=False).sum()
cum['cum'] = cum['saving'].cumsum()



fig = px.line(cum, x="mese", y="cum")

sx, dx = st.columns([5,2])
with sx:
    st.plotly_chart(fig, use_container_width=True)
with dx:
    st.table(cum)



