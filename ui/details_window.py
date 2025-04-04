# ui/details_window.py
import inspect
import importlib
import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
                             QLabel, QMessageBox, QApplication)
from preprocessing_generic import (convert_to_numeric, fill_missing_values, encode_categorical, 
                                   convert_to_datetime, remove_outliers)
import preprocessing_custom
from ui.custom_function_manager import CustomFunctionManagerWindow

logger = logging.getLogger(__name__)

class ColumnDetailsWindow(QDialog):
    """Janela para visualizar e transformar uma coluna do DataFrame."""
    
    def __init__(self, column, details, df, update_callback, parent=None):
        """Inicializa a janela com detalhes da coluna e opções de transformação.
        
        Args:
            column: Nome da coluna a visualizar ou transformar.
            details: Texto inicial com os detalhes da coluna.
            df: DataFrame contendo a coluna.
            update_callback: Função de retorno para actualizar a interface pai.
            parent: Janela pai, opcional.
        """
        super().__init__(parent)
        logger.debug(f"Inicializando ColumnDetailsWindow para coluna '{column}'")
        self.setWindowTitle(f"Detalhes da Coluna '{column}'")
        self.setGeometry(200, 200, 600, 500)
        self.column = column
        self.df = df
        self.update_callback = update_callback
        self.df_history = []  # Histórico para desfazer alterações
        self.app_parent = parent
        
        layout = QVBoxLayout()  # Layout principal vertical
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)  # Apenas leitura para exibir detalhes
        self.details_text.setText(details)
        layout.addWidget(self.details_text)
        
        functions_layout = QHBoxLayout()  # Layout horizontal para funções
        
        # Secção de funções genéricas
        generic_layout = QVBoxLayout()
        generic_layout.addWidget(QLabel("Funções Genéricas"))
        for btn_text, action in [
            ("Converter para Numérico", self.convert_to_numeric),
            ("Preencher Nulos com Mediana", lambda: self.fill_missing_values('median')),
            ("Preencher Nulos com Média", lambda: self.fill_missing_values('mean')),
            ("Preencher Nulos com Moda", lambda: self.fill_missing_values('mode')),
            ("Codificar Categóricos (LabelEncoder)", self.encode_categorical),
            ("Converter para Datetime", self.convert_to_datetime),
            ("Remover Outliers (IQR)", self.remove_outliers),
            ("Remover Nulos", self.remove_nulls)
        ]:
            btn = QPushButton(btn_text)
            btn.clicked.connect(action)  # Associa a acção ao botão
            generic_layout.addWidget(btn)
        generic_layout.addStretch()  # Espaço para alinhamento
        functions_layout.addLayout(generic_layout)
        
        # Secção de funções personalizadas
        self.custom_layout = QVBoxLayout()
        self.custom_layout.addWidget(QLabel("Funções Personalizadas"))
        self.custom_buttons_layout = QVBoxLayout()  # Sublayout para botões dinâmicos
        self.custom_layout.addLayout(self.custom_buttons_layout)
        
        self.custom_buttons = {}  # Dicionário para rastrear botões
        logger.debug("Chamando load_custom_functions no __init__")
        self.load_custom_functions()  # Carrega funções personalizadas
        
        manage_btn = QPushButton("Gerenciar Funções Personalizadas")
        manage_btn.clicked.connect(self.open_custom_function_manager)
        self.custom_layout.addWidget(manage_btn)
        self.custom_layout.addStretch()
        functions_layout.addLayout(self.custom_layout)
        
        layout.addLayout(functions_layout)
        
        undo_btn = QPushButton("Desfazer Última Modificação")
        undo_btn.clicked.connect(self.undo_last_modification)
        layout.addWidget(undo_btn)
        
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
        logger.debug("ColumnDetailsWindow inicializado com sucesso")

    def load_custom_functions(self):
        """Carrega funções personalizadas do módulo preprocessing_custom como botões."""
        logger.debug("Iniciando load_custom_functions")
        import preprocessing_custom
        functions = inspect.getmembers(preprocessing_custom, inspect.isfunction)
        logger.debug(f"Funções carregadas: {[name for name, _ in functions]}")
        
        # Remove botões existentes para evitar duplicação
        for name in list(self.custom_buttons.keys()):
            btn = self.custom_buttons.pop(name)
            self.custom_buttons_layout.removeWidget(btn)
            btn.setParent(None)
            btn.deleteLater()
            logger.debug(f"Botão '{name}' removido do layout")
        
        # Adiciona botões para cada função personalizada
        for name, func in functions:
            btn = QPushButton(name.replace('_', ' ').title())  # Formata o nome para legibilidade
            btn.clicked.connect(lambda checked, f=func: self.apply_custom_function(f))
            self.custom_buttons_layout.addWidget(btn)
            self.custom_buttons[name] = btn
            logger.debug(f"Botão '{name}' adicionado ao layout")
        
        QApplication.processEvents()  # Garante actualização da interface
        self.custom_layout.activate()
        self.update()
        self.repaint()
        logger.debug("load_custom_functions concluído")

    def refresh_custom_functions(self):
        """Actualiza a lista de funções personalizadas exibidas."""
        logger.debug("Iniciando refresh_custom_functions")
        self.load_custom_functions()  # Recarrega os botões
        logger.debug("refresh_custom_functions concluído")

    def open_custom_function_manager(self):
        """Abre a janela de gestão de funções personalizadas."""
        logger.debug("Abrindo CustomFunctionManagerWindow")
        CustomFunctionManagerWindow(self).exec_()  # Executa a janela modal
        logger.debug("CustomFunctionManagerWindow fechada")

    def apply_custom_function(self, func):
        """Aplica uma função personalizada à coluna e actualiza o DataFrame."""
        logger.debug(f"Aplicando função personalizada '{func.__name__}' na coluna '{self.column}'")
        self.save_state()  # Guarda o estado antes da alteração
        try:
            result = func(self.df, self.column)
            if result is None:
                logger.error(f"A função '{func.__name__}' retornou None")
                raise ValueError(f"A função {func.__name__} retornou None. Ela deve retornar um DataFrame.")
            self.df = result
            if not hasattr(self.app_parent, 'df'):
                logger.error("self.app_parent não tem atributo 'df'")
                raise AttributeError("self.app_parent não tem atributo 'df'")
            self.app_parent.df = self.df  # Sincroniza com o DataFrame pai
            self.update_callback(self.app_parent)  # Chama a função de retorno
            self.update_details()  # Actualiza os detalhes exibidos
            logger.debug(f"Função '{func.__name__}' aplicada com sucesso")
        except Exception as e:
            logger.error(f"Erro ao aplicar a função '{func.__name__}': {str(e)}")
            self.details_text.setText(self.details_text.toPlainText() + f"\nErro ao aplicar a função: {str(e)}")

    def save_state(self):
        """Guarda o estado actual do DataFrame no histórico para desfazer alterações."""
        logger.debug("Guardando estado do DataFrame no histórico")
        self.df_history.append(self.df.copy())
        logger.debug(f"Histórico agora tem {len(self.df_history)} estados")

    def convert_to_numeric(self):
        """Converte a coluna seleccionada para tipo numérico."""
        logger.debug(f"Convertendo coluna '{self.column}' para numérico")
        self.save_state()
        self.df = convert_to_numeric(self.df, self.column)
        self._apply_changes()

    def fill_missing_values(self, method):
        """Preenche valores nulos na coluna com o método especificado."""
        logger.debug(f"Preenchendo valores nulos na coluna '{self.column}' com método '{method}'")
        self.save_state()
        self.df = fill_missing_values(self.df, self.column, method)
        self._apply_changes()

    def encode_categorical(self):
        """Codifica a coluna categórica usando LabelEncoder."""
        logger.debug(f"Codificando coluna categórica '{self.column}'")
        self.save_state()
        self.df = encode_categorical(self.df, self.column)
        self._apply_changes()

    def convert_to_datetime(self):
        """Converte a coluna para formato datetime."""
        logger.debug(f"Convertendo coluna '{self.column}' para datetime")
        self.save_state()
        self.df = convert_to_datetime(self.df, self.column)
        self._apply_changes()

    def remove_outliers(self):
        """Remove outliers da coluna usando o método IQR."""
        logger.debug(f"Removendo outliers da coluna '{self.column}'")
        self.save_state()
        self.df = remove_outliers(self.df, self.column)
        self._apply_changes()

    def remove_nulls(self):
        """Remove linhas com valores nulos na coluna seleccionada após confirmação."""
        logger.debug(f"Removendo linhas com nulos na coluna '{self.column}'")
        null_count = self.df[self.column].isnull().sum()
        if null_count == 0:
            logger.debug(f"Nenhum valor nulo encontrado na coluna '{self.column}'")
            QMessageBox.information(self, "Sem Nulos", f"A coluna '{self.column}' não contém valores nulos para remover.")
            return
        
        original_size = len(self.df)
        temp_df = self.df.dropna(subset=[self.column])  # Remove linhas com nulos na coluna
        rows_to_remove = original_size - len(temp_df)
        
        message = (f"A remoção de nulos afectará apenas as linhas com valores ausentes na coluna '{self.column}'.\n"
                   f"- Tamanho actual do DataFrame: {original_size} linhas\n"
                   f"- Linhas a remover: {rows_to_remove}\n"
                   f"- Novo tamanho estimado: {len(temp_df)} linhas\n\n"
                   "Deseja continuar?")
        reply = QMessageBox.question(self, "Confirmação de Remoção de Nulos", message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.save_state()
            self.df = temp_df
            self._apply_changes()
            logger.debug(f"{rows_to_remove} linhas removidas")
            QMessageBox.information(self, "Sucesso", f"{rows_to_remove} linhas com nulos removidas.")
        else:
            logger.debug("Remoção de nulos cancelada pelo utilizador")

    def undo_last_modification(self):
        """Desfaz a última modificação aplicada ao DataFrame."""
        logger.debug("Desfazendo última modificação")
        if self.df_history:
            self.df = self.df_history.pop()  # Restaura o estado anterior
            self._apply_changes()
            logger.debug("Modificação desfeita com sucesso")
        else:
            logger.debug("Nenhuma modificação para desfazer")
            self.details_text.setText(self.details_text.toPlainText() + "\nNenhuma modificação para desfazer.")

    def update_details(self):
        """Actualiza os detalhes exibidos da coluna após alterações."""
        logger.debug(f"Actualizando detalhes da coluna '{self.column}'")
        col_data = self.df[self.column]
        dtype = str(col_data.dtype)
        null_count = col_data.isnull().sum()
        unique_values = col_data.dropna().unique()
        
        try:
            unique_values = [float(val) for val in unique_values]  # Tenta converter para float
        except (ValueError, TypeError):
            unique_values = [str(val) for val in unique_values]  # Mantém como string se falhar
        unique_values = sorted(unique_values)
        
        # Limita a exibição dos valores únicos
        unique_str = ", ".join(map(str, unique_values[:5 if len(unique_values) > 10 else len(unique_values)]))
        if len(unique_values) > 10:
            unique_str += f" (primeiros 5 de {len(unique_values)} valores únicos)"
        
        details = f"Detalhes da coluna '{self.column}':\n- Tipo de dados: {dtype}\n- Contagem de valores nulos: {null_count}\n- Valores únicos: {unique_str}"
        self.details_text.setText(details)
        logger.debug("Detalhes actualizados com sucesso")

    def _apply_changes(self):
        """Aplica as alterações ao DataFrame e actualiza a interface."""
        logger.debug("Aplicando mudanças ao DataFrame")
        self.app_parent.df = self.df  # Sincroniza com o DataFrame pai
        self.update_callback(self.app_parent)  # Notifica a interface pai
        self.update_details()  # Actualiza os detalhes exibidos
        logger.debug("Mudanças aplicadas com sucesso")