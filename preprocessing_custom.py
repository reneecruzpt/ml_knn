#preprocessing_custom.py

import pandas as pd
import logging
logger = logging.getLogger(__name__)

def normalize_bdate(df, bdate_column='bdate'):
    logger.debug(f"Iniciando normalize_bdate para a coluna: {bdate_column}")
    logger.debug(f"Colunas do DataFrame: {list(df.columns)}")

        # Verificar se a coluna existe no DataFrame
    if bdate_column not in df.columns:
        logger.error(f"Coluna '{bdate_column}' não encontrada no DataFrame")
        raise ValueError(f"Coluna '{bdate_column}' não encontrada no DataFrame")

    logger.debug(f"Tipo da coluna '{bdate_column}': {df[bdate_column].dtype}")
    logger.debug(f"Primeiros valores da coluna '{bdate_column}': {df[bdate_column].head().tolist()}")

    # Dividir a coluna de datas
    logger.debug("Dividindo a coluna de datas...")
    try:
        # Inspecionar o tipo de df[bdate_column].str
        logger.debug(f"Tipo de df[{bdate_column}].str: {type(df[bdate_column].str)}")
        logger.debug(f"Tipo de df[{bdate_column}].str.split: {type(df[bdate_column].str.split)}")
        split_dates = df[bdate_column].str.split('.', expand=True)
        logger.debug(f"Resultado de str.split: {split_dates.head()}")
    except Exception as e:
        logger.error(f"Erro ao dividir a coluna '{bdate_column}': {str(e)}")
        raise

    df[['day', 'month', 'year']] = split_dates

    # Converter para numérico
    logger.debug("Convertendo colunas para numérico...")
    df['day'] = pd.to_numeric(df['day'], errors='coerce')
    df['month'] = pd.to_numeric(df['month'], errors='coerce')
    df['year'] = pd.to_numeric(df['year'], errors='coerce')

    # Calcular medianas
    logger.debug("Calculando medianas...")
    day_median = df['day'].median()
    month_median = df['month'].median()
    year_median = df['year'].median()
    logger.debug(f"Medianas - day: {day_median}, month: {month_median}, year: {year_median}")

    # Preencher valores nulos e converter para inteiro
    logger.debug("Preenchendo valores nulos e convertendo para inteiro...")
    df['day'] = df['day'].fillna(day_median).astype(int)
    df['month'] = df['month'].fillna(month_median).astype(int)
    df['year'] = df['year'].fillna(year_median).astype(int)

    # Aplicar limites
    logger.debug("Aplicando limites...")
    df['day'] = df['day'].clip(1, 31)
    df['month'] = df['month'].clip(1, 12)
    df['year'] = df['year'].clip(1900, 2025)

    # Reconstruir a coluna de datas
    logger.debug("Reconstruindo a coluna de datas...")
    df[bdate_column] = df['day'].astype(str) + '.' + df['month'].astype(str) + '.' + df['year'].astype(str)

    # Remover colunas temporárias
    logger.debug("Removendo colunas temporárias...")
    df = df.drop(columns=['day', 'month', 'year'], errors='ignore')
    logger.debug(f"Colunas após remover temporárias: {list(df.columns)}")

    return df

def calculate_age(df, column):
    def calc_age(bdate):
        if pd.isna(bdate) or bdate == "":
            return None
        try:
            parts = bdate.split('.')
            year = int(parts[-1])
            if 1900 <= year <= 2025:
                return 2025 - year
            else:
                return None
        except (ValueError, IndexError):
            return None

    df[f"{column}_age"] = df[column].apply(calc_age)
    return df



def transform_education_status(df, column):
    """
    Transforma a coluna 'education_status' em valores numéricos para treinamento do modelo.
    Args:
        df (pd.DataFrame): DataFrame de entrada.
        column (str): Nome da coluna a ser transformada ('education_status').
    Returns:
        pd.DataFrame: DataFrame com a coluna transformada.
    """
    education_mapping = {
        "Undergraduate applicant": 0,
        "Student (Bachelor's)": 1,
        "Student (Specialist)": 2,
        "Student (Master's)": 3,
        "Alumnus (Bachelor's)": 4,
        "Alumnus (Specialist)": 5,
        "Alumnus (Master's)": 6,
        "PhD": 7,
        "Candidate of Sciences": 8
    }
    df_transformed = df.copy()
    df_transformed[column] = df_transformed[column].apply(
        lambda x: education_mapping.get(x, float('0')) if pd.notnull(x) else float('0')
    )
    return df_transformed

def normalize_education_form(df, column):
    """
    Normaliza a coluna 'education_form' em valores numéricos para treinamento do modelo.
    Args:
        df (pd.DataFrame): DataFrame de entrada.
        column (str): Nome da coluna a ser transformada ('education_form').
    Returns:
        pd.DataFrame: DataFrame com a coluna transformada.
    """
    logger.debug(f"Iniciando normalize_education_form para a coluna: {column}")
    logger.debug(f"Colunas do DataFrame: {list(df.columns)}")
    logger.debug(f"Primeiros valores da coluna '{column}': {df[column].head().tolist()}")
    logger.debug(f"Valores únicos da coluna '{column}' antes da transformação: {df[column].dropna().unique().tolist()}")
    
    # Dicionário de mapeamento para os valores de education_form
    education_form_mapping = {
        "Full-time": 0,
        "Distance Learning": 1,
        "Part-time": 2
    }
    
    df_transformed = df.copy()
    logger.debug("DataFrame copiado com sucesso")
    
    # Função para normalizar education_form com base em occupation_type
    def normalize_value(row):
        education_form = row[column]
        occupation_type = row['occupation_type']
        
        # Se education_form não for nulo e estiver no dicionário, mapear diretamente
        if pd.notnull(education_form) and education_form in education_form_mapping:
            return education_form_mapping[education_form]
        
        # Se education_form for nulo, determinar o valor com base em occupation_type
        if occupation_type == "university":
            return education_form_mapping["Full-time"]  # 0
        elif occupation_type == "work":
            return education_form_mapping["Part-time"]  # 2
        else:
            # Se occupation_type for nulo ou outro valor, assumir "Distance Learning" como padrão
            return education_form_mapping["Distance Learning"]  # 1
    
    # Aplicar a normalização
    df_transformed[column] = df_transformed.apply(normalize_value, axis=1)
    
    logger.debug(f"Colunas após transformação: {list(df_transformed.columns)}")
    logger.debug(f"Primeiros valores da coluna transformada '{column}': {df_transformed[column].head().tolist()}")
    logger.debug(f"Valores únicos da coluna '{column}' após a transformação: {df_transformed[column].unique().tolist()}")
    
    return df_transformed