# ui/data_manager.py
import pandas as pd
import logging
from PyQt5.QtWidgets import QFileDialog, QTableWidgetItem
from preprocessing_generic import update_valid_values as update_valid_values_generic  # Usar alias
from ui.column_interface import display_columns
from model import predict_new_client

logger = logging.getLogger(__name__)

def load_csv(app):
    file_name, _ = QFileDialog.getOpenFileName(app, "Abrir CSV", "", "CSV Files (*.csv)")
    if file_name:
        try:
            app.df = pd.read_csv(file_name)
            logger.debug(f"Colunas após carregar CSV: {list(app.df.columns)}")
            
            if 'result' not in app.df.columns:
                app.result_label.setText("Este CSV não é um CSV de treinamento. A coluna 'result' é obrigatória.")
                app.df = None
                app.columns_header_label.setVisible(False)
                return
            
            display_columns(app)
            update_valid_values(app)  # Chama a função local
            app.columns_header_label.setVisible(True)
        except Exception as e:
            logger.error(f"Erro ao carregar o CSV: {str(e)}")
            app.df = None
            app.columns_header_label.setVisible(False)

def load_test_csv(app):
    file_name, _ = QFileDialog.getOpenFileName(app, "Abrir CSV de Teste", "", "CSV Files (*.csv)")
    if not file_name:
        return
    
    try:
        test_df = pd.read_csv(file_name)
        logger.debug(f"Colunas do CSV de teste: {list(test_df.columns)}")
        
        missing_cols = [col for col in app.training_columns if col not in test_df.columns]
        if missing_cols:
            app.predict_result.setText(f"Colunas faltando no CSV de teste: {', '.join(missing_cols)}")
            return
        
        for col in app.training_columns:
            if not pd.api.types.is_numeric_dtype(test_df[col]):
                app.predict_result.setText(f"A coluna '{col}' no CSV de teste contém valores não numéricos.")
                return
            if test_df[col].isnull().any():
                app.predict_result.setText(f"A coluna '{col}' no CSV de teste contém valores NaN.")
                return
        
        if 'bdate_age' in app.training_columns:
            invalid_rows = test_df[(test_df['bdate_age'] < 16) | (test_df['bdate_age'] > 75)]
            if not invalid_rows.empty:
                app.predict_result.setText(f"A coluna 'bdate_age' contém valores fora do intervalo (16 a 75 anos).")
                return
        
        X_test = test_df[app.training_columns]
        predictions, probabilities = predict_new_client(X_test.values, app.knn, app.scaler, app.training_columns)
        
        app.test_result_table.setRowCount(len(predictions))
        for i, (pred, prob) in enumerate(zip(predictions, probabilities)):
            app.test_result_table.setItem(i, 0, QTableWidgetItem(str(test_df['id'].iloc[i] if 'id' in test_df else i)))
            app.test_result_table.setItem(i, 1, QTableWidgetItem(f"{pred} (Prob: {prob[1]:.2f})"))
        
        test_df['prediction'] = predictions
        test_df['probability'] = [prob[1] for prob in probabilities]
        output_file = file_name.replace('.csv', '_predictions.csv')
        test_df.to_csv(output_file, index=False)
        app.predict_result.setText(f"Previsões concluídas! Resultados salvos em {output_file}")
    except Exception as e:
        logger.error(f"Erro ao processar o CSV de teste: {str(e)}")
        app.predict_result.setText(f"Erro ao processar o CSV de teste: {str(e)}")

def update_valid_values(app):
    logger.debug("Iniciando update_valid_values...")
    logger.debug(f"Colunas do DataFrame antes de atualizar valores válidos: {list(app.df.columns)}")
    app.valid_values = update_valid_values_generic(app.df)  # Chama a função de preprocessing_generic
    logger.debug(f"Valores válidos atualizados: {app.valid_values}")
    logger.debug("update_valid_values concluído")