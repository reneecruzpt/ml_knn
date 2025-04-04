# ui/model_interface.py
import os
import logging
import joblib
from model import train_and_save_model, predict_new_client as predict_new_client_model
from ui.visualization import VisualizationWindow
from PyQt5.QtWidgets import QFileDialog
from ui.column_interface import display_columns

logger = logging.getLogger(__name__)

def train_model(app):
    """Treina o modelo KNN com os dados e parâmetros da aplicação.
    
    Args:
        app: Instância de MLApp contendo df, selected_columns, valid_values e widgets da UI.
    """
    try:
        n_neighbors = app.neighbors_input.value()  # Obtém o número de vizinhos definido pelo utilizador
        app.knn, app.scaler, accuracy, train_size, test_size, app.training_columns = train_and_save_model(
            app.df, app.selected_columns, app.valid_values, n_neighbors=n_neighbors
        )
        app.result_label.setText(f"Dados de Treino: {train_size}, Dados de Teste: {test_size}\nAcurácia: {accuracy:.2f}")
        app.plot_btn.setVisible(True)  # Mostra o botão de gráficos após o treino
    except ValueError as e:
        logger.error(f"Erro ao treinar o modelo: {str(e)}")
        app.result_label.setText(str(e))
    except Exception as e:
        logger.error(f"Erro inesperado ao treinar o modelo: {str(e)}")
        app.result_label.setText(f"Erro ao treinar o modelo: {str(e)}")

def save_model(app):
    """Guarda o modelo treinado, normalizador e dados relacionados em ficheiros .pkl.
    
    Args:
        app: Instância de MLApp com knn, scaler, training_columns, df e valid_values.
    """
    if app.knn and app.scaler and app.training_columns and app.df is not None and app.valid_values:
        joblib.dump(app.knn, 'knn_model.pkl')  # Guarda o modelo KNN
        joblib.dump(app.scaler, 'scaler.pkl')  # Guarda o normalizador
        joblib.dump(app.training_columns, 'training_columns.pkl')  # Guarda as colunas de treino
        joblib.dump(app.df, 'dataframe.pkl')  # Guarda o DataFrame
        joblib.dump(app.valid_values, 'valid_values.pkl')  # Guarda os valores válidos
        app.result_label.setText("Modelo, normalizador, colunas de treino, DataFrame e valores válidos guardados com sucesso!")
    else:
        app.result_label.setText("Treine o modelo antes de guardar.")

def load_model(app):
    """Carrega um modelo guardado e actualiza o estado da aplicação.
    
    Args:
        app: Instância de MLApp para armazenar knn, scaler, training_columns, df e valid_values.
    """
    file_name, _ = QFileDialog.getOpenFileName(app, "Carregar Modelo", "", "Pickle Files (*.pkl)")
    if not file_name:
        return  # Sai se nenhum ficheiro for seleccionado
    
    try:
        app.knn = joblib.load(file_name)  # Carrega o modelo KNN
        scaler_file = file_name.replace('knn_model.pkl', 'scaler.pkl')
        columns_file = file_name.replace('knn_model.pkl', 'training_columns.pkl')
        dataframe_file = file_name.replace('knn_model.pkl', 'dataframe.pkl')
        valid_values_file = file_name.replace('knn_model.pkl', 'valid_values.pkl')
        
        # Verifica e carrega cada ficheiro relacionado
        for file_path, attr_name in [
            (scaler_file, 'scaler'), (columns_file, 'training_columns'),
            (dataframe_file, 'df'), (valid_values_file, 'valid_values')
        ]:
            if os.path.exists(file_path):
                setattr(app, attr_name, joblib.load(file_path))
            else:
                raise ValueError(f"Ficheiro {os.path.basename(file_path)} não encontrado.")
        
        app.result_label.setText("Modelo, normalizador, colunas de treino, DataFrame e valores válidos carregados com sucesso!")
        display_columns(app)  # Actualiza a exibição das colunas
    except Exception as e:
        logger.error(f"Erro ao carregar o modelo: {str(e)}")
        app.result_label.setText(f"Erro ao carregar o modelo: {str(e)}")

def predict_new_client(app):
    """Realiza a previsão para um novo cliente usando entradas da Tela 3.
    
    Args:
        app: Instância de MLApp com inputs, knn, scaler e training_columns.
    """
    new_data = []
    unique_columns = list(dict.fromkeys(app.training_columns))  # Remove duplicados das colunas de treino
    
    for col in unique_columns:
        value = app.inputs[col].text()
        try:
            new_data.append(float(value))  # Converte entrada para float
        except ValueError:
            app.predict_result.setText(f"Insira um valor numérico válido para '{col}'.")
            return
    
    prediction, probability = predict_new_client_model([new_data], app.knn, app.scaler, app.training_columns)
    app.predict_result.setText(f"Previsão: {prediction[0]} (0 = Não, 1 = Sim)\nProbabilidades: Não = {probability[0][0]:.2f}, Sim = {probability[0][1]:.2f}")

def show_plots(app):
    """Abre a janela de visualização de gráficos do modelo treinado.
    
    Args:
        app: Instância de MLApp com df e training_columns.
    """
    if app.df is not None and app.training_columns:
        VisualizationWindow(app.df, app.training_columns, app).exec_()  # Mostra a janela de gráficos
    else:
        app.result_label.setText("Treine o modelo antes de gerar gráficos.")