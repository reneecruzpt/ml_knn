# ui/data_manager.py
import pandas as pd
import logging
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem, QMessageBox
from preprocessing_generic import update_valid_values as update_valid_values_generic
from ui.column_interface import display_columns
from model import predict_new_client

logger = logging.getLogger(__name__)

def load_csv(app):
    """Carrega um ficheiro CSV e actualiza a interface da Tela 1.
    
    Args:
        app: Instância de MLApp contendo o estado global (df, result_label, columns_header_label).
    """
    file_name, _ = QFileDialog.getOpenFileName(app, "Abrir CSV", "", "CSV Files (*.csv)")
    if not file_name:
        return  # Sai se nenhum ficheiro for seleccionado
    
    try:
        app.df = pd.read_csv(file_name)  # Carrega o CSV para o DataFrame
        logger.debug(f"Colunas do DataFrame após carregamento: {list(app.df.columns)}")
        if 'result' not in app.df.columns:
            logger.warning("Coluna 'result' não encontrada no CSV")
            app.result_label.setText("Este CSV não é um CSV de treino. A coluna 'result' é obrigatória.")
            QMessageBox.warning(app, "Coluna Ausente", 
                                "O CSV carregado não contém a coluna 'result', que é obrigatória para o treino do modelo. "
                                "Por favor, carregue um CSV que contenha a coluna 'result'.")
            app.df = None  # Repõe o DataFrame para None
            app.columns_header_label.setVisible(False)  # Esconde o cabeçalho das colunas
            display_columns(app)  # Actualiza a interface para mostrar o estado vazio
            return
        
        display_columns(app)  # Mostra as colunas na interface
        update_valid_values(app)  # Calcula os valores válidos
        app.columns_header_label.setVisible(True)  # Torna o cabeçalho visível
    except Exception as e:
        logger.error(f"Erro ao carregar o CSV: {str(e)}")
        app.df = None
        app.columns_header_label.setVisible(False)
        display_columns(app)  # Reflecte o erro na interface
        QMessageBox.critical(app, "Erro", f"Erro ao carregar o CSV: {str(e)}")

def load_test_csv(app):
    """Carrega um CSV de teste e gera previsões para múltiplas linhas na Tela 3.
    
    Args:
        app: Instância de MLApp com training_columns, knn, scaler e test_result_table.
    """
    file_name, _ = QFileDialog.getOpenFileName(app, "Abrir CSV de Teste", "", "CSV Files (*.csv)")
    if not file_name:
        return  # Sai se nenhum ficheiro for seleccionado
    
    try:
        test_df = pd.read_csv(file_name)  # Carrega o CSV de teste
        
        # Verifica se todas as colunas de treino estão presentes
        missing_cols = [col for col in app.training_columns if col not in test_df.columns]
        if missing_cols:
            app.predict_result.setText(f"Colunas em falta no CSV de teste: {', '.join(missing_cols)}")
            return
        
        # Garante que as colunas sejam numéricas e sem valores nulos
        for col in app.training_columns:
            if not pd.api.types.is_numeric_dtype(test_df[col]):
                app.predict_result.setText(f"A coluna '{col}' no CSV de teste contém valores não numéricos.")
                return
            if test_df[col].isnull().any():
                app.predict_result.setText(f"A coluna '{col}' no CSV de teste contém valores NaN.")
                return
        
        # Valida o intervalo de 'bdate_age', se aplicável
        if 'bdate_age' in app.training_columns:
            invalid_rows = test_df[(test_df['bdate_age'] < 16) | (test_df['bdate_age'] > 75)]
            if not invalid_rows.empty:
                app.predict_result.setText(f"A coluna 'bdate_age' contém valores fora do intervalo (16 a 75 anos).")
                return
        
        # Prepara os dados e gera previsões com o modelo treinado
        X_test = test_df[app.training_columns]
        predictions, probabilities = predict_new_client(X_test.values, app.knn, app.scaler, app.training_columns)
        
        # Preenche a tabela com os resultados das previsões
        app.test_result_table.setRowCount(len(predictions))
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            app.test_result_table.setItem(i, 0, QTableWidgetItem(str(test_df['id'].iloc[i] if 'id' in test_df else i)))
            app.test_result_table.setItem(i, 1, QTableWidgetItem(f"{pred} (Prob: {prob[1]:.2f})"))
        
        # Guarda o CSV com as previsões
        test_df['prediction'] = predictions
        test_df['probability'] = [prob[1] for prob in probabilities]
        output_file = file_name.replace('.csv', '_predictions.csv')
        test_df.to_csv(output_file, index=False)
        app.predict_result.setText(f"Previsões concluídas! Resultados guardados em {output_file}")
    except Exception as e:
        logger.error(f"Erro ao processar o CSV de teste: {str(e)}")
        app.predict_result.setText(f"Erro ao processar o CSV de teste: {str(e)}")

def update_valid_values(app):
    """Actualiza os valores válidos do DataFrame usando a função de preprocessing_generic.
    
    Args:
        app: Instância de MLApp contendo o DataFrame (app.df) e o dicionário valid_values.
    """
    app.valid_values = update_valid_values_generic(app.df)  # Calcula e armazena os valores válidos