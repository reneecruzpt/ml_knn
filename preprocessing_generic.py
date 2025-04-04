# preprocessing_generic.py
import pandas as pd
from sklearn.preprocessing import LabelEncoder

def convert_to_numeric(df, column):
    """Converte uma coluna para tipo numérico, substituindo valores inválidos por NaN.
    
    Args:
        df: DataFrame de entrada.
        column: Nome da coluna a converter.
    
    Returns:
        DataFrame com a coluna convertida.
    """
    df[column] = pd.to_numeric(df[column], errors='coerce')  # Força conversão, valores inválidos tornam-se NaN
    return df

def fill_missing_values(df, column, method='median'):
    """Preenche valores nulos numa coluna com o método especificado.
    
    Args:
        df: DataFrame de entrada.
        column: Nome da coluna a preencher.
        method: Método de preenchimento ('mean', 'median', 'mode'; padrão: 'median').
    
    Returns:
        DataFrame com valores nulos preenchidos.
    """
    if method == 'mean':
        fill_value = df[column].mean()  # Usa a média da coluna
    elif method == 'median':
        fill_value = df[column].median()  # Usa a mediana da coluna
    elif method == 'mode':
        fill_value = df[column].mode()[0]  # Usa a moda (primeiro valor mais frequente)
    df[column] = df[column].fillna(fill_value)  # Preenche os nulos com o valor calculado
    return df

def encode_categorical(df, column):
    """Converte uma coluna categórica em valores numéricos usando LabelEncoder.
    
    Args:
        df: DataFrame de entrada.
        column: Nome da coluna a codificar.
    
    Returns:
        DataFrame com a coluna codificada.
    """
    encoder = LabelEncoder()  # Instancia o codificador de etiquetas
    df[column] = encoder.fit_transform(df[column].astype(str))  # Converte para string antes de codificar
    return df

def convert_to_datetime(df, column):
    """Converte uma coluna para formato datetime, substituindo valores inválidos por NaT.
    
    Args:
        df: DataFrame de entrada.
        column: Nome da coluna a converter.
    
    Returns:
        DataFrame com a coluna convertida.
    """
    df[column] = pd.to_datetime(df[column], errors='coerce')  # Converte para datetime, inválidos tornam-se NaT
    return df

def remove_outliers(df, column):
    """Remove valores extremos de uma coluna numérica usando o método IQR.
    
    Args:
        df: DataFrame de entrada.
        column: Nome da coluna a analisar.
    
    Returns:
        DataFrame sem valores extremos na coluna especificada.
    """
    Q1 = df[column].quantile(0.25)  # Primeiro quartil
    Q3 = df[column].quantile(0.75)  # Terceiro quartil
    IQR = Q3 - Q1  # Intervalo interquartil
    lower_bound = Q1 - 1.5 * IQR  # Limite inferior
    upper_bound = Q3 + 1.5 * IQR  # Limite superior
    return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]  # Filtra valores dentro dos limites

def update_valid_values(df):
    """Calcula os valores válidos para cada coluna do DataFrame.
    
    Args:
        df: DataFrame de entrada.
    
    Returns:
        dict: Dicionário com os valores válidos para cada coluna.
    """
    valid_values = {}
    for col in df.columns:
        if col == 'bdate_age':
            valid_values[col] = list(range(16, 76))  # Define intervalo fixo de 16 a 75 para 'bdate_age'
        else:
            unique_values = df[col].dropna().unique()  # Obtém valores únicos, ignorando nulos
            try:
                unique_values = [float(val) for val in unique_values]  # Tenta converter para float
            except (ValueError, TypeError):
                unique_values = [str(val) for val in unique_values]  # Usa string se a conversão falhar
            valid_values[col] = sorted(unique_values)  # Armazena valores ordenados
    return valid_values