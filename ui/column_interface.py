# ui/column_interface.py
import pandas as pd
import logging
from PyQt5.QtWidgets import QCheckBox, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from ui.details_window import ColumnDetailsWindow
from ui.utils import clear_layout

logger = logging.getLogger(__name__)

def display_columns(app):
    """Exibe as colunas do DataFrame como checkboxes com botões de detalhes na Tela 1.
    
    Args:
        app: Instância de MLApp contendo o DataFrame (app.df) e o layout (app.columns_layout).
    """
    # Limpa o layout existente e reinicia a lista de colunas selecionadas
    clear_layout(app.columns_layout)
    app.selected_columns = []

    # Handlers para eventos de checkbox e botão de detalhes
    def make_state_handler(column):
        """Cria um handler para atualizar a seleção da coluna ao mudar o estado do checkbox."""
        def handler(state, col=column):
            update_selected_columns(app, col, state)
        return handler
    
    def make_details_handler(column):
        """Cria um handler para abrir a janela de detalhes da coluna ao clicar no botão."""
        def handler(checked, col=column):
            show_column_details(app, col)
        return handler
    
    # Itera sobre as colunas do DataFrame para criar os widgets
    for column in app.df.columns:
        row_layout = QHBoxLayout()
        
        checkbox = QCheckBox(column)
        if column == 'result':
            # Coluna 'result' é obrigatória e marcada por padrão
            checkbox.setChecked(True)
            checkbox.setEnabled(False)
            app.selected_columns.append(column)
        else:
            checkbox.stateChanged.connect(make_state_handler(column))
        
        # Adiciona aviso se a coluna não for numérica (exceto 'result')
        warning_label = QLabel("")
        if not (pd.api.types.is_numeric_dtype(app.df[column]) or column == 'result'):
            warning_label.setText(f"A coluna '{column}' contém dados não numéricos e pode prejudicar o modelo.")
            warning_label.setStyleSheet("color: red;")
        
        details_btn = QPushButton("Detalhes")
        details_btn.clicked.connect(make_details_handler(column))
        
        # Adiciona os widgets ao layout da linha
        row_layout.addWidget(checkbox)
        row_layout.addWidget(warning_label)
        row_layout.addWidget(details_btn)
        row_layout.addStretch()
        
        app.columns_layout.addLayout(row_layout)

def show_column_details(app, col):
    """Abre a janela de detalhes para uma coluna específica.
    
    Args:
        app: Instância de MLApp contendo o DataFrame (app.df).
        col: Nome da coluna a ser detalhada.
    """
    if app.df is None or col not in app.df.columns:
        return
    
    col_data = app.df[col]
    dtype = str(col_data.dtype)
    null_count = col_data.isnull().sum()
    unique_values = col_data.dropna().unique()
    
    # Tenta converter valores únicos para float; mantém como string se falhar
    try:
        unique_values = [float(val) for val in unique_values]
    except (ValueError, TypeError):
        unique_values = [str(val) for val in unique_values]
    unique_values = sorted(unique_values)
    
    # Limita a exibição a 10 valores únicos ou mostra os 5 primeiros
    unique_str = ", ".join(map(str, unique_values[:5 if len(unique_values) > 10 else len(unique_values)]))
    if len(unique_values) > 10:
        unique_str += f" (primeiros 5 de {len(unique_values)} valores únicos)"
    
    details = f"Detalhes da coluna '{col}':\n- Tipo de dados: {dtype}\n- Contagem de valores nulos: {null_count}\n- Valores únicos: {unique_str}"
    
    # Abre a janela de detalhes com o callback para atualização
    details_window = ColumnDetailsWindow(col, details, app.df, update_after_formatting, app)
    details_window.exec_()

def update_after_formatting(app):
    """Atualiza a interface após alterações no DataFrame.
    
    Args:
        app: Instância de MLApp contendo o DataFrame e layout a serem atualizados.
    """
    display_columns(app)  # Reexibe as colunas com os novos dados
    from ui.data_manager import update_valid_values
    update_valid_values(app)  # Atualiza os valores válidos do DataFrame

def update_selected_columns(app, column, state):
    """Atualiza a lista de colunas selecionadas com base no estado do checkbox.
    
    Args:
        app: Instância de MLApp contendo a lista selected_columns.
        column: Nome da coluna a ser adicionada ou removida.
        state: Estado do checkbox (Qt.Checked ou Qt.Unchecked).
    """
    if state == Qt.Checked and column not in app.selected_columns:
        app.selected_columns.append(column)
    elif state == Qt.Unchecked and column in app.selected_columns:
        app.selected_columns.remove(column)
