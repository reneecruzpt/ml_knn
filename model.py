# model.py
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import joblib
from preprocessing_custom import calculate_age

def train_and_save_model(df, selected_columns, valid_values, n_neighbors=5):
    """
    Treina o modelo KNN com as colunas selecionadas e retorna o modelo treinado, o scaler e métricas.
    
    Args:
        df (pd.DataFrame): DataFrame de entrada.
        selected_columns (list): Lista de colunas selecionadas para o treinamento.
        valid_values (dict): Dicionário com os valores válidos para cada coluna.
        n_neighbors (int): Número de vizinhos para o KNN.
    
    Returns:
        tuple: (knn, scaler, accuracy, len(X_train), len(X_test), training_columns)
    
    Raises:
        ValueError: Se houver problemas com os dados (ex.: colunas não numéricas, valores NaN).
    """
    if 'result' not in df.columns:
        raise ValueError("O DataFrame não contém a coluna 'result' necessária para o treinamento.")
    
    if 'result' not in selected_columns:
        raise ValueError("A coluna 'result' deve estar selecionada para o treinamento.")
    
    train_data = df.copy()
    
    # Definir as colunas de treinamento (excluindo 'id' e 'result')
    training_columns = list(set([col for col in selected_columns if col not in ['id', 'result']]))
    
    if not training_columns:
        raise ValueError("Nenhuma coluna válida foi selecionada para o treinamento. Selecione pelo menos uma coluna além de 'id' e 'result'.")
    
    # Validar as colunas selecionadas
    for col in training_columns:
        # Verificar se a coluna é numérica
        if not pd.api.types.is_numeric_dtype(train_data[col]):
            raise ValueError(f"Coluna '{col}' contém valores não numéricos. Use a janela de detalhes para converter a coluna para um formato numérico.")
        
        # Verificar se há valores NaN
        if train_data[col].isnull().any():
            raise ValueError(f"Coluna '{col}' contém valores NaN. Use a janela de detalhes para preencher ou remover os valores nulos.")
    
    # Preparar os dados para o treinamento
    X = train_data[training_columns]
    y = train_data['result']
    
    # Verificar se o DataFrame está vazio
    if X.empty:
        raise ValueError("O DataFrame está vazio após as transformações. Verifique se as colunas selecionadas contêm dados válidos.")
    
    # Dividir os dados em treino e teste
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)
    
    # Escalonar os dados
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    # Treinar o modelo KNN
    knn = KNeighborsClassifier(n_neighbors=n_neighbors)
    knn.fit(X_train, y_train)
    
    # Calcular a acurácia
    accuracy = knn.score(X_test, y_test)
    
    # Não salvar automaticamente, apenas retornar os resultados
    return knn, scaler, accuracy, len(X_train), len(X_test), training_columns

def predict_new_client(new_data, knn, scaler, training_columns):
    """Faz previsões para uma ou várias linhas de dados."""
    new_df = pd.DataFrame(new_data, columns=training_columns)
    new_data_scaled = scaler.transform(new_df)
    predictions = knn.predict(new_data_scaled)
    probabilities = knn.predict_proba(new_data_scaled)
    return predictions, probabilities