# ui/column_interface.py
import pandas as pd
import logging
from PyQt5.QtWidgets import QCheckBox, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from ui.details_window import ColumnDetailsWindow
from ui.utils import clear_layout

logger = logging.getLogger(__name__)

def display_columns(app):
    logger.debug(f"Estado do DataFrame antes de limpar o layout: {list(app.df.columns)}")
    logger.debug("Limpando o layout...")
    clear_layout(app.columns_layout)
    logger.debug("Layout limpo")
    app.selected_columns = []
    logger.debug(f"Colunas exibidas no display_columns: {list(app.df.columns)}")
    
    def make_state_handler(column):
        def handler(state, col=column):
            logger.debug(f"Sinal stateChanged disparado para a coluna: {col}, estado: {state}")
            update_selected_columns(app, col, state)
        return handler
    
    def make_details_handler(column):
        def handler(checked, col=column):
            logger.debug(f"Sinal clicked disparado para o botão de detalhes da coluna: {col}")
            show_column_details(app, col)
        return handler
    
    for column in app.df.columns:
        logger.debug(f"Processando coluna: {column}")
        row_layout = QHBoxLayout()
        
        logger.debug(f"Criando checkbox para a coluna: {column}")
        checkbox = QCheckBox(column)
        
        # Tratar a coluna 'result' de forma especial
        if column == 'result':
            checkbox.setChecked(True)
            checkbox.setEnabled(False)
            app.selected_columns.append(column)
        else:
            logger.debug(f"Conectando sinal stateChanged para a coluna: {column}")
            checkbox.stateChanged.connect(make_state_handler(column))
        
        logger.debug("Criando warning_label...")
        warning_label = QLabel("")
        logger.debug(f"Verificando compatibilidade da coluna '{column}'...")
        is_compatible = pd.api.types.is_numeric_dtype(app.df[column]) or column == 'result'
        if not is_compatible:
            logger.debug(f"Coluna '{column}' não é compatível, definindo mensagem de aviso")
            warning_label.setText(f"A coluna '{column}' contém dados não numéricos e pode prejudicar o modelo.")
            warning_label.setStyleSheet("color: red;")
        
        logger.debug(f"Criando botão de detalhes para a coluna: {column}")
        details_btn = QPushButton("Detalhes")
        logger.debug(f"Conectando sinal clicked para o botão de detalhes da coluna: {column}")
        details_btn.clicked.connect(make_details_handler(column))
        
        logger.debug(f"Adicionando widgets ao layout para a coluna: {column}")
        row_layout.addWidget(checkbox)
        row_layout.addWidget(warning_label)
        row_layout.addWidget(details_btn)
        row_layout.addStretch()
        
        logger.debug(f"Adicionando row_layout ao columns_layout para a coluna: {column}")
        app.columns_layout.addLayout(row_layout)
    logger.debug(f"Colunas exibidas após recriar o layout: {[checkbox.text() for checkbox in app.columns_widget.findChildren(QCheckBox)]}")

def show_column_details(app, col):
    if app.df is None or col not in app.df.columns:
        return
    
    col_data = app.df[col]
    dtype = str(col_data.dtype)
    null_count = col_data.isnull().sum()
    unique_values = col_data.dropna().unique()
    
    try:
        unique_values = [float(val) for val in unique_values]
    except (ValueError, TypeError):
        unique_values = [str(val) for val in unique_values]
    unique_values = sorted(unique_values)
    
    if len(unique_values) <= 10:
        unique_str = ", ".join(map(str, unique_values))
    else:
        unique_str = ", ".join(map(str, unique_values[:5])) + " (primeiros 5 de " + str(len(unique_values)) + " valores únicos)"
    
    details = (
        f"Detalhes da coluna '{col}':\n"  
        f"- Tipo de dados: {dtype}\n"
        f"- Contagem de valores nulos: {null_count}\n"
        f"- Valores únicos: {unique_str}"
    )
    
    details_window = ColumnDetailsWindow(col, details, app.df, update_after_formatting, app)
    details_window.exec_()

def update_after_formatting(app):
    logger.debug("Iniciando update_after_formatting")
    logger.debug(f"Colunas no update_after_formatting: {list(app.df.columns)}")
    logger.debug("Chamando display_columns...")
    display_columns(app)
    logger.debug("display_columns concluído")
    logger.debug("Chamando update_valid_values...")
    from ui.data_manager import update_valid_values
    update_valid_values(app)
    logger.debug("update_valid_values concluído")

def update_selected_columns(app, column, state):
    if state == Qt.Checked:
        if column not in app.selected_columns:
            app.selected_columns.append(column)
    else:
        if column in app.selected_columns:
            app.selected_columns.remove(column)