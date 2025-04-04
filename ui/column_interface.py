# ui/column_interface.py
import pandas as pd
from PyQt5.QtWidgets import QCheckBox, QLabel, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt
from ui.details_window import ColumnDetailsWindow
from ui.utils import clear_layout

def display_columns(app):
    """Exibe as colunas do DataFrame como caixas de selecção com botões de detalhes na Tela 1.
    
    Args:
        app: Instância de MLApp contendo o DataFrame (app.df) e o layout (app.columns_layout).
    """
    clear_layout(app.columns_layout)  # Repõe o layout para evitar widgets duplicados
    app.selected_columns = []  # Inicializa a lista de colunas seleccionadas

    if app.df is None or app.df.empty:
        return  # Sai se o DataFrame não estiver carregado

    # Funções para criar manipuladores de eventos para caixas de selecção e botões
    def make_state_handler(column):
        """Cria um manipulador para actualizar a selecção da coluna ao alterar o estado da caixa."""
        def handler(state, col=column):
            update_selected_columns(app, col, state)
        return handler
    
    def make_details_handler(column):
        """Cria um manipulador para abrir a janela de detalhes da coluna ao clicar no botão."""
        def handler(checked, col=column):
            show_column_details(app, col)
        return handler
    
    for column in app.df.columns:
        row_layout = QHBoxLayout()  # Layout horizontal para os widgets de cada coluna
        
        checkbox = QCheckBox(column)  # Caixa de selecção com o nome da coluna
        if column == 'result':
            checkbox.setChecked(True)  # 'result' é obrigatória e seleccionada por defeito
            checkbox.setEnabled(False)  # Impede a desmarcação de 'result'
            app.selected_columns.append(column)
        else:
            checkbox.stateChanged.connect(make_state_handler(column))  # Associa o manipulador de alteração
        
        # Avisa sobre colunas não numéricas que podem afectar o treino do modelo
        warning_label = QLabel("")
        is_compatible = pd.api.types.is_numeric_dtype(app.df[column]) or column == 'result'
        if not is_compatible:
            warning_label.setText(f"A coluna '{column}' contém dados não numéricos e pode afectar o modelo.")
            warning_label.setStyleSheet("color: red;")
        
        details_btn = QPushButton("Detalhes")  # Botão para ver detalhes da coluna
        details_btn.clicked.connect(make_details_handler(column))
        
        row_layout.addWidget(checkbox)
        row_layout.addWidget(warning_label)
        row_layout.addWidget(details_btn)
        row_layout.addStretch()  # Adiciona espaço para alinhar os widgets à esquerda
        
        app.columns_layout.addLayout(row_layout)  # Adiciona a linha ao layout principal

def show_column_details(app, col):
    """Abre uma janela de detalhes para uma coluna específica com os seus metadados.
    
    Args:
        app: Instância de MLApp contendo o DataFrame (app.df).
        col: Nome da coluna cujos detalhes serão exibidos.
    """
    if app.df is None or col not in app.df.columns:
        return  # Sai se o DataFrame for inválido ou a coluna não existir
    
    col_data = app.df[col]
    dtype = str(col_data.dtype)  # Tipo de dados da coluna
    null_count = col_data.isnull().sum()  # Contagem de valores em falta
    unique_values = col_data.dropna().unique()  # Valores únicos não nulos
    
    # Tenta converter valores únicos para float para ordenação; mantém como string se falhar
    try:
        unique_values = [float(val) for val in unique_values]
    except (ValueError, TypeError):
        unique_values = [str(val) for val in unique_values]
    unique_values = sorted(unique_values)
    
    # Formata valores únicos: mostra todos se ≤ 10, caso contrário os 5 primeiros com contagem
    if len(unique_values) <= 10:
        unique_str = ", ".join(map(str, unique_values))
    else:
        unique_str = ", ".join(map(str, unique_values[:5])) + f" (primeiros 5 de {len(unique_values)} valores únicos)"
    
    details = (
        f"Detalhes da coluna '{col}':\n"  
        f"- Tipo de dados: {dtype}\n"
        f"- Contagem de valores nulos: {null_count}\n"
        f"- Valores únicos: {unique_str}"
    )
    
    # Abre a janela de detalhes com uma função de retorno para actualizar a interface
    details_window = ColumnDetailsWindow(col, details, app.df, update_after_formatting, app)
    details_window.exec_()

def update_after_formatting(app):
    """Actualiza a interface após modificações no DataFrame.
    
    Args:
        app: Instância de MLApp contendo o DataFrame e o layout a actualizar.
    """
    display_columns(app)  # Reexibe as colunas com os dados actualizados
    from ui.data_manager import update_valid_values
    update_valid_values(app)  # Recalcula os valores válidos do DataFrame

def update_selected_columns(app, column, state):
    """Actualiza a lista de colunas seleccionadas com base no estado da caixa de selecção.
    
    Args:
        app: Instância de MLApp contendo a lista selected_columns.
        column: Nome da coluna a adicionar ou remover.
        state: Estado da caixa de selecção (Qt.Checked ou Qt.Unchecked).
    """
    if state == Qt.Checked and column not in app.selected_columns:
        app.selected_columns.append(column)  # Adiciona a coluna se seleccionada
    elif state == Qt.Unchecked and column in app.selected_columns:
        app.selected_columns.remove(column)  # Remove a coluna se desmarcada