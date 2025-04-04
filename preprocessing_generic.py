# preprocessing_generic.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder

def convert_to_numeric(df, column):
    """Converte uma coluna para tipo numérico, substituindo valores inválidos por NaN."""
    df[column] = pd.to_numeric(df[column], errors='coerce')
    return df

def fill_missing_values(df, column, method='median'):
    """Preenche valores nulos em uma coluna com o método especificado (mean, median, mode)."""
    if method == 'mean':
        df[column] = df[column].fillna(df[column].mean())
    elif method == 'median':
        df[column] = df[column].fillna(df[column].median())
    elif method == 'mode':
        df[column] = df[column].fillna(df[column].mode()[0])
    return df

def encode_categorical(df, column):
    """Converte uma coluna categórica em valores numéricos usando LabelEncoder."""
    encoder = LabelEncoder()
    df[column] = encoder.fit_transform(df[column].astype(str))
    return df

def convert_to_datetime(df, column):
    """Converte uma coluna para formato datetime, substituindo valores inválidos por NaT."""
    df[column] = pd.to_datetime(df[column], errors='coerce')
    return df

def remove_outliers(df, column):
    """Remove outliers de uma coluna numérica usando o método IQR."""
    Q1 = df[column].quantile(0.25)
    Q3 = df[column].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    df = df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    return df

def update_valid_values(df):
    """
    Calcula os valores válidos para cada coluna do DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame de entrada.
    
    Returns:
        dict: Dicionário com os valores válidos para cada coluna.
    """
    valid_values = {}
    for col in df.columns:
        if col == 'bdate_age':
            # Para a coluna 'bdate_age', definir um intervalo de valores válidos
            valid_values[col] = list(range(16, 76))  # Valores de 16 a 75
        else:
            # Para outras colunas, usar os valores únicos
            unique_values = df[col].dropna().unique()
            try:
                unique_values = [float(val) for val in unique_values]
            except (ValueError, TypeError):
                unique_values = [str(val) for val in unique_values]
            valid_values[col] = sorted(unique_values)
    return valid_values