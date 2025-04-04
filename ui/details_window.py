# ui/details_window.py
import inspect
import importlib
import logging
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, 
                             QLineEdit, QComboBox, QMessageBox, QLabel, QTableWidget, QTableWidgetItem)
from preprocessing_generic import (convert_to_numeric, fill_missing_values, encode_categorical, 
                                  convert_to_datetime, remove_outliers)
import preprocessing_custom
from ui.custom_function_manager import CustomFunctionManagerWindow

# Configurar logging para depuração
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ColumnDetailsWindow(QDialog):
    def __init__(self, column, details, df, update_callback, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detalhes da Coluna '{column}'")
        self.setGeometry(200, 200, 600, 500)
        
        self.column = column
        self.df = df
        self.update_callback = update_callback
        self.df_history = []
        self.app_parent = parent
            
        layout = QVBoxLayout()
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setText(details)
        layout.addWidget(self.details_text)
        
        functions_layout = QHBoxLayout()
        
        generic_layout = QVBoxLayout()
        generic_layout.addWidget(QLabel("Funções Genéricas"))
        
        numeric_btn = QPushButton("Converter para Numérico")
        numeric_btn.clicked.connect(self.convert_to_numeric)
        generic_layout.addWidget(numeric_btn)
        
        fill_btn_median = QPushButton("Preencher Nulos com Mediana")
        fill_btn_median.clicked.connect(lambda: self.fill_missing_values('median'))
        generic_layout.addWidget(fill_btn_median)
        
        fill_btn_mean = QPushButton("Preencher Nulos com Média")
        fill_btn_mean.clicked.connect(lambda: self.fill_missing_values('mean'))
        generic_layout.addWidget(fill_btn_mean)
        
        fill_btn_mode = QPushButton("Preencher Nulos com Moda")
        fill_btn_mode.clicked.connect(lambda: self.fill_missing_values('mode'))
        generic_layout.addWidget(fill_btn_mode)
        
        encode_btn = QPushButton("Codificar Categóricos (LabelEncoder)")
        encode_btn.clicked.connect(self.encode_categorical)
        generic_layout.addWidget(encode_btn)
        
        datetime_btn = QPushButton("Converter para Datetime")
        datetime_btn.clicked.connect(self.convert_to_datetime)
        generic_layout.addWidget(datetime_btn)
        
        outliers_btn = QPushButton("Remover Outliers (IQR)")
        outliers_btn.clicked.connect(self.remove_outliers)
        generic_layout.addWidget(outliers_btn)
        
        remove_nulls_btn = QPushButton("Remover Nulos")
        remove_nulls_btn.clicked.connect(self.remove_nulls)
        generic_layout.addWidget(remove_nulls_btn)
        
        generic_layout.addStretch()
        functions_layout.addLayout(generic_layout)
        
        self.custom_layout = QVBoxLayout()
        self.custom_layout.addWidget(QLabel("Funções Personalizadas"))
        
        self.custom_buttons = {}
        self.load_custom_functions()
        
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

    def load_custom_functions(self):
        importlib.reload(preprocessing_custom)
        functions = inspect.getmembers(preprocessing_custom, inspect.isfunction)
        logger.debug(f"Funções personalizadas carregadas: {[name for name, _ in functions]}")
        
        for btn in self.custom_buttons.values():
            btn.deleteLater()
        self.custom_buttons.clear()
        
        def make_handler(func):
            def handler(checked, f=func):
                logger.debug(f"Botão clicado, chamando apply_custom_function com func: {f.__name__}")
                self.apply_custom_function(f)
            return handler

        for name, func in functions:
            btn = QPushButton(name.replace('_', ' ').title())
            btn.clicked.connect(make_handler(func))
            logger.debug(f"Conectando função {name} ao botão: {func}")
            self.custom_layout.insertWidget(1, btn)
            logger.debug(f"Botão '{name}' inserido no índice 1 do layout custom_layout")
            self.custom_buttons[name] = btn

    def refresh_custom_functions(self):
        logger.debug("Atualizando funções personalizadas na janela de detalhes...")
        self.load_custom_functions()

    def open_custom_function_manager(self):
        manager_window = CustomFunctionManagerWindow(self)
        manager_window.exec_()

    def apply_custom_function(self, func):
        self.save_state()
        try:
            logger.debug(f"Tipo de func: {type(func)}, Nome: {func.__name__ if hasattr(func, '__name__') else 'Desconhecido'}")
            result = func(self.df, self.column)
            if result is None:
                logger.error(f"A função {func.__name__} retornou None. Ela deve retornar um DataFrame.")
                raise ValueError(f"A função {func.__name__} retornou None. Ela deve retornar um DataFrame.")
            self.df = result
            logger.debug("Função aplicada com sucesso")
            if not hasattr(self.app_parent, 'df'):
                logger.error(f"self.app_parent não tem atributo 'df'. self.app_parent: {self.app_parent}")
                raise AttributeError("self.app_parent não tem atributo 'df'")
            self.app_parent.df = self.df
            logger.debug("DataFrame global atualizado com sucesso")
            logger.debug(f"Colunas após aplicar {func.__name__}: {list(self.df.columns)}")
            logger.debug("Chamando update_callback...")
            self.update_callback(self.app_parent)  # Passar self.app_parent como argumento
            logger.debug("update_callback concluído com sucesso")
            logger.debug("Chamando update_details...")
            self.update_details()
            logger.debug("update_details concluído com sucesso")
        except TypeError as e:
            logger.error(f"Erro TypeError capturado: {str(e)}")
            self.details_text.setText(self.details_text.toPlainText() + 
                                    f"\nErro ao aplicar a função: {str(e)}\n"
                                    "A função deve ter a assinatura 'def nome(df, column):' e retornar o DataFrame modificado.")
        except Exception as e:
            logger.error(f"Erro Exception capturado: {str(e)}")
            self.details_text.setText(self.details_text.toPlainText() + f"\nErro ao aplicar a função: {str(e)}")

    def save_state(self):
        self.df_history.append(self.df.copy())

    def convert_to_numeric(self):
        self.save_state()
        self.df = convert_to_numeric(self.df, self.column)
        self.app_parent.df = self.df
        self.update_callback(self.app_parent)  # Passar self.app_parent
        self.update_details()

    def fill_missing_values(self, method):
        self.save_state()
        self.df = fill_missing_values(self.df, self.column, method)
        self.app_parent.df = self.df
        self.update_callback(self.app_parent)  # Passar self.app_parent
        self.update_details()

    def encode_categorical(self):
        self.save_state()
        self.df = encode_categorical(self.df, self.column)
        self.app_parent.df = self.df
        self.update_callback(self.app_parent)  # Passar self.app_parent
        self.update_details()

    def convert_to_datetime(self):
        self.save_state()
        self.df = convert_to_datetime(self.df, self.column)
        self.app_parent.df = self.df
        self.update_callback(self.app_parent)  # Passar self.app_parent
        self.update_details()

    def remove_outliers(self):
        self.save_state()
        self.df = remove_outliers(self.df, self.column)
        self.app_parent.df = self.df
        self.update_callback(self.app_parent)  # Passar self.app_parent
        self.update_details()

    def remove_nulls(self):
        null_count = self.df[self.column].isnull().sum()
        
        if null_count == 0:
            QMessageBox.information(self, "Sem Nulos", f"A coluna '{self.column}' não contém valores nulos para remover.")
            return
        
        original_size = len(self.df)
        temp_df = self.df.dropna(subset=[self.column])
        new_size = len(temp_df)
        rows_to_remove = original_size - new_size
        
        message = (
            f"A remoção de nulos afetará apenas as linhas com valores ausentes na coluna '{self.column}'.\n"
            f"- Tamanho atual do DataFrame: {original_size} linhas\n"
            f"- Linhas a remover: {rows_to_remove}\n"
            f"- Novo tamanho estimado: {new_size} linhas\n\n"
            "Essa operação removerá apenas as linhas com nulos nesta coluna, preservando nulos em outras colunas. "
            "Considere preencher os nulos como alternativa antes de remover. Deseja continuar?"
        )
        reply = QMessageBox.question(self, "Confirmação de Remoção de Nulos", message,
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.save_state()
            self.df = temp_df
            self.app_parent.df = self.df
            self.update_callback(self.app_parent)  # Passar self.app_parent
            self.update_details()
            QMessageBox.information(self, "Sucesso", f"{rows_to_remove} linhas com nulos na coluna '{self.column}' foram removidas. Novo tamanho: {new_size} linhas.")
        else:
            logger.debug("Remoção de nulos cancelada pelo usuário.")

    def undo_last_modification(self):
        if self.df_history:
            self.df = self.df_history.pop()
            self.app_parent.df = self.df
            self.update_callback(self.app_parent)  # Passar self.app_parent
            self.update_details()
        else:
            self.details_text.setText(self.details_text.toPlainText() + "\nNenhuma modificação para desfazer.")

    def update_details(self):
        col_data = self.df[self.column]
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
            f"Detalhes da coluna '{self.column}':\n"
            f"- Tipo de dados: {dtype}\n"
            f"- Contagem de valores nulos: {null_count}\n"
            f"- Valores únicos: {unique_str}"
        )
        
        self.details_text.setText(details)