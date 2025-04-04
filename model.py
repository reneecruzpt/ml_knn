# model.py
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib

def train_and_save_model(df, selected_columns, valid_values, n_neighbors=5):
    """Treina um modelo KNN com as colunas seleccionadas e devolve os resultados.
    
    Args:
        df: DataFrame de entrada com os dados a treinar.
        selected_columns: Lista de colunas seleccionadas para o treino.
        valid_values: Dicionário com valores válidos para cada coluna (não usado directamente aqui).
        n_neighbors: Número de vizinhos para o KNN (padrão: 5).
    
    Returns:
        tuple: (knn, scaler, accuracy, len(X_train), len(X_test), training_columns)
    
    Raises:
        ValueError: Se 'result' não estiver presente, colunas forem inválidas ou dados inconsistentes.
    """
    if 'result' not in df.columns or 'result' not in selected_columns:
        raise ValueError("A coluna 'result' é obrigatória no DataFrame e na selecção.")
    
    train_data = df.copy()  # Cria uma cópia para evitar modificar o original
    training_columns = list(set(col for col in selected_columns if col not in ['id', 'result']))  # Exclui 'id' e 'result'
    
    if not training_columns:
        raise ValueError("Nenhuma coluna válida seleccionada além de 'id' e 'result'.")
    
    # Verifica se as colunas são numéricas e não contêm valores nulos
    for col in training_columns:
        if not pd.api.types.is_numeric_dtype(train_data[col]):
            raise ValueError(f"Coluna '{col}' contém valores não numéricos.")
        if train_data[col].isnull().any():
            raise ValueError(f"Coluna '{col}' contém valores NaN.")
    
    X = train_data[training_columns]  # Dados de entrada
    y = train_data['result']  # Variável alvo
    
    if X.empty:
        raise ValueError("O DataFrame está vazio após as transformações.")
    
    # Divide os dados em conjuntos de treino e teste (25% para teste)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    # Normaliza os dados com StandardScaler
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)  # Ajusta e transforma o conjunto de treino
    X_test = scaler.transform(X_test)  # Apenas transforma o conjunto de teste
    
    # Cria e treina o modelo KNN
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(X_train, y_train)
    
    accuracy = knn.score(X_test, y_test)  # Calcula a acurácia no conjunto de teste
    return knn, scaler, accuracy, len(X_train), len(X_test), training_columns

def predict_new_client(new_data, knn, scaler, training_columns):
    """Faz previsões para uma ou várias linhas de dados usando o modelo treinado.
    
    Args:
        new_data: Lista ou array com os dados a prever.
        knn: Modelo KNN treinado.
        scaler: Normalizador usado no treino.
        training_columns: Lista de colunas usadas no treino.
    
    Returns:
        tuple: (predictions, probabilities) com previsões e probabilidades.
    """
    new_df = pd.DataFrame(new_data, columns=training_columns)  # Converte os dados num DataFrame
    new_data_scaled = scaler.transform(new_df)  # Normaliza os novos dados
    predictions = knn.predict(new_data_scaled)  # Gera as previsões
    probabilities = knn.predict_proba(new_data_scaled)  # Calcula as probabilidades
    return predictions, probabilities