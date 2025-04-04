# ui/model_interface.py
import os
import logging
import joblib
from model import train_and_save_model, predict_new_client as predict_new_client_model  # Alias para evitar confusão
from ui.visualization import VisualizationWindow

logger = logging.getLogger(__name__)

def train_model(app):
    logger.debug("Iniciando treinamento do modelo...")
    try:
        n_neighbors = app.neighbors_input.value()
        logger.debug(f"Número de vizinhos selecionado: {n_neighbors}")
        app.knn, app.scaler, accuracy, train_size, test_size, app.training_columns = train_and_save_model(
            app.df, app.selected_columns, app.valid_values, n_neighbors=n_neighbors
        )
        logger.debug("Treinamento concluído com sucesso")
        app.result_label.setText(f"Dados de Treino: {train_size}, Dados de Teste: {test_size}\nAcurácia: {accuracy:.2f}")
        logger.debug("Tornando o botão 'Gerar Gráficos' visível...")
        app.plot_btn.setVisible(True)
        logger.debug("Botão 'Gerar Gráficos' agora está visível")
    except ValueError as e:
        logger.error(f"Erro ao treinar o modelo: {str(e)}")
        app.result_label.setText(str(e))
    except Exception as e:
        logger.error(f"Erro inesperado ao treinar o modelo: {str(e)}")
        app.result_label.setText(f"Erro ao treinar o modelo: {str(e)}")

def save_model(app):
    if app.knn and app.scaler and app.training_columns and app.df is not None and app.valid_values:
        joblib.dump(app.knn, 'knn_model.pkl')
        joblib.dump(app.scaler, 'scaler.pkl')
        joblib.dump(app.training_columns, 'training_columns.pkl')
        joblib.dump(app.df, 'dataframe.pkl')
        joblib.dump(app.valid_values, 'valid_values.pkl')
        app.result_label.setText("Modelo, scaler, colunas de treinamento, DataFrame e valores válidos salvos com sucesso!")
    else:
        app.result_label.setText("Treine o modelo antes de salvar.")

def load_model(app):
    from PyQt5.QtWidgets import QFileDialog
    from ui.column_interface import display_columns
    file_name, _ = QFileDialog.getOpenFileName(app, "Carregar Modelo", "", "Pickle Files (*.pkl)")
    if file_name:
        try:
            app.knn = joblib.load(file_name)
            scaler_file = file_name.replace('knn_model.pkl', 'scaler.pkl')
            columns_file = file_name.replace('knn_model.pkl', 'training_columns.pkl')
            dataframe_file = file_name.replace('knn_model.pkl', 'dataframe.pkl')
            valid_values_file = file_name.replace('knn_model.pkl', 'valid_values.pkl')
            
            if os.path.exists(scaler_file):
                app.scaler = joblib.load(scaler_file)
            else:
                raise ValueError("Arquivo scaler.pkl não encontrado.")
            
            if os.path.exists(columns_file):
                app.training_columns = joblib.load(columns_file)
            else:
                raise ValueError("Arquivo training_columns.pkl não encontrado.")
            
            if os.path.exists(dataframe_file):
                app.df = joblib.load(dataframe_file)
            else:
                raise ValueError("Arquivo dataframe.pkl não encontrado.")
            
            if os.path.exists(valid_values_file):
                app.valid_values = joblib.load(valid_values_file)
            else:
                raise ValueError("Arquivo valid_values.pkl não encontrado.")
            
            app.result_label.setText("Modelo, scaler, colunas de treinamento, DataFrame e valores válidos carregados com sucesso!")
            display_columns(app)
        except Exception as e:
            logger.error(f"Erro ao carregar o modelo: {str(e)}")
            app.result_label.setText(f"Erro ao carregar o modelo: {str(e)}")

def predict_new_client(app):
    new_data = []
    unique_columns = list(dict.fromkeys(app.training_columns))
    
    for col in unique_columns:
        value = app.inputs[col].text()
        try:
            float_value = float(value)
        except ValueError:
            app.predict_result.setText(f"Insira um valor numérico válido para '{col}'.")
            return
        
        new_data.append(float_value)
    
    prediction, probability = predict_new_client_model([new_data], app.knn, app.scaler, app.training_columns)
    app.predict_result.setText(f"Previsão: {prediction[0]} (0 = Não, 1 = Sim)\nProbabilidades: Não = {probability[0][0]:.2f}, Sim = {probability[0][1]:.2f}")

def show_plots(app):
    if app.df is not None and app.training_columns:
        plot_window = VisualizationWindow(app.df, app.training_columns, app)
        plot_window.exec_()
    else:
        app.result_label.setText("Treine o modelo antes de gerar gráficos.")