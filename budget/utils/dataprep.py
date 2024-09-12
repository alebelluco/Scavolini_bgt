# raggruppamento utility
# 26-06-2024

import pandas as pd 
import streamlit as st 
from io import BytesIO
import xlsxwriter
import zipfile



def calcolo_delta(df, articolo, lay, filtro):
    df = df[df.Articolo == articolo]
    df['mese'] = [data.month for data in df['Data doc.']]
    out = df[lay].groupby(by=filtro, as_index=False).min()
    out['delta_listino'] = out["importo_unitario"] - out["importo_unitario"].shift(1)
    out['key'] = None
    out['delta_listino'].iloc[0]=0
    out['key'].iloc[0] = str(out['Articolo'].iloc[0]) + '--' + str(out['mese'].iloc[0])
    for i in range(1,len(out)):
        delta = out["importo_unitario"].iloc[i] - out["importo_unitario"].iloc[i-1]
        if delta != 0:
            out['delta_listino'].iloc[i] = delta
        else:
            out['delta_listino'].iloc[i] = out['delta_listino'].iloc[i-1]
        out['key'].iloc[i] = str(out['Articolo'].iloc[i]) + '--' + str(out['mese'].iloc[i])
        
    return out[['key','delta_listino']]




def unisci_colonne(df, colonne, new):
    new_col = [] 
    for col in colonne:
        try:
            df[col]=df[col].fillna('')
            new_col.append(col)
        except:
            pass
  
    df[new] = None
    for i in range(len(df)):
        key = []
        for col in new_col:
            key.append(str(df[col].iloc[i]))
        df[new].iloc[i] = ''.join(list(set(key))) #list-set-list serve per eliminare eventuali valori doppi popolati su due colonne

    return df

def crea_chiave(df, dic_key):
    df['key']=None
    for i in range(len(df)):
        fornitore = df['Intestatario'].iloc[i]
        colonne = dic_key[fornitore]
        key = []
        for col in colonne:
            key.append(str(df[col].iloc[i]))
        df['key'].iloc[i] = ''.join((key))
    return df

def scarica_excel(df, filename):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1',index=False)
    writer.close()

    st.download_button(
        label="Download Excel workbook",
        data=output.getvalue(),
        file_name=filename,
        mime="application/vnd.ms-excel"
    )

def create_excel_file(df, file_name):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df.to_excel(writer, index=False, sheet_name='Sheet1')
    writer.close()
    processed_data = output.getvalue()
    return processed_data

def create_zip_file(files):
    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'a', zipfile.ZIP_DEFLATED, False) as zip_file:
        for file_name, data in files.items():
            zip_file.writestr(file_name, data)
    return zip_buffer.getvalue()


