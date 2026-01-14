import pandas as pd

def ler_excel(caminho):
    df = pd.read_excel(f'{caminho}'.xlsx)
    return df