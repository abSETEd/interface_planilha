import pandas as pd
import re
import tkinter as tk
from tkinter import filedialog

def formatar_cnpj(cnpj):
    cnpj = re.sub(r'\D', '', str(cnpj))  # Remove caracteres não numéricos
    if len(cnpj) == 14:
        return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
    return cnpj  # Retorna o CNPJ já formatado corretamente

def formatar_telefone(telefone):
    telefone = re.sub(r'\D', '', str(telefone))  # Remove caracteres não numéricos
    if len(telefone) == 10:  # Telefone fixo
        return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
    elif len(telefone) == 11:  # Celular
        return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
    return telefone 

def selecionar_arquivo():
    root = tk.Tk()
    root.withdraw()
    return filedialog.askopenfilename(title="Selecione a planilha", filetypes=[("Arquivos Excel", "*.xlsx;*.xls;*.ods")])

def remove_duplicates():
    print("Selecione o arquivo da planilha")
    arquivo_entrada = selecionar_arquivo()
    if not arquivo_entrada:
        print("Nenhum arquivo selecionado. Saindo...")
        return
    
    nome_coluna = "Razão Social"

    print("Digite o nome do arquivo de saída (ou pressione Enter para usar o padrão):")
    nome_arquivo = input().strip()
    arquivo_saida = nome_arquivo if nome_arquivo else "planilha_filtrada.xlsx"

    # Carregar todas as abas da planilha
    if arquivo_entrada.endswith(".ods"):
        xls = pd.read_excel(arquivo_entrada, dtype=str, engine="odf", sheet_name=None)
    else:
        xls = pd.read_excel(arquivo_entrada, dtype=str, sheet_name=None)
    
    planilhas_filtradas = {}
    
    for nome_aba, df in xls.items():
        if nome_coluna not in df.columns:
            print(f"A coluna '{nome_coluna}' não foi encontrada na aba '{nome_aba}'. Pulando...")
            continue
        
        df[nome_coluna] = df[nome_coluna].fillna('')
        contagem = df[nome_coluna].value_counts()
        nomes_unicos = contagem[contagem == 1].index
        df_unicos = df[df[nome_coluna].isin(nomes_unicos)].copy()
        
        if 'CNPJ' in df_unicos.columns:
            df_unicos['CNPJ'] = df_unicos['CNPJ'].apply(formatar_cnpj)
        
        if 'Telefone' in df_unicos.columns:
            df_unicos['Telefone'] = df_unicos['Telefone'].apply(formatar_telefone)
        
        if 'Observação' not in df_unicos.columns:
            df_unicos['Observação'] = ''
        else:
            df_unicos['Observação'] = df_unicos['Observação'].astype(str)
        
        df_unicos['Lead Gerado'] = ''
        df_unicos['Data de Contato'] = ''
        
        planilhas_filtradas[nome_aba] = df_unicos
    
    with pd.ExcelWriter(arquivo_saida, engine='openpyxl') as writer:
        for nome_aba, df_filtrado in planilhas_filtradas.items():
            df_filtrado.to_excel(writer, sheet_name=nome_aba, index=False)
    
    print(f'Arquivo salvo como {arquivo_saida} com {sum(len(df) for df in planilhas_filtradas.values())} entradas únicas.')
    print(f"Baixe a planilha aqui: {arquivo_saida}")

# Chamando a função principal
remove_duplicates()
