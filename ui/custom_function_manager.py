# ui/custom_function_manager.py
import inspect
import importlib
import logging
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit, QComboBox, QMessageBox

import preprocessing_custom

# Configurar logging para depuração
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CustomFunctionManagerWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gerenciar Funções Personalizadas")
        self.setGeometry(300, 300, 600, 400)
        
        self.app_parent = parent  # Referência à janela ColumnDetailsWindow
        layout = QVBoxLayout()
        
        self.function_selector = QComboBox()
        self.function_selector.addItem("Selecione uma função")
        self.load_functions()
        layout.addWidget(self.function_selector)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome da função")
        layout.addWidget(self.name_input)
        
        self.code_input = QTextEdit()
        self.code_input.setPlaceholderText("Digite o código da função aqui (exemplo:\n"
                                         "def minha_funcao(df, column):\n"
                                         "    # Seu código aqui\n"
                                         "    return df)")
        layout.addWidget(self.code_input)
        
        button_layout = QHBoxLayout()
        add_btn = QPushButton("Adicionar Função")
        add_btn.clicked.connect(self.add_function)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("Editar Função")
        edit_btn.clicked.connect(self.edit_function)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("Excluir Função")
        delete_btn.clicked.connect(self.delete_function)
        button_layout.addWidget(delete_btn)
        
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        self.function_selector.currentIndexChanged.connect(self.load_selected_function)

    def load_functions(self):
        self.function_selector.clear()
        self.function_selector.addItem("Selecione uma função")
        importlib.reload(preprocessing_custom)
        functions = inspect.getmembers(preprocessing_custom, inspect.isfunction)
        logger.debug(f"Funções encontradas em preprocessing_custom: {[name for name, _ in functions]}")
        for name, _ in functions:
            self.function_selector.addItem(name)

    def load_selected_function(self):
        function_name = self.function_selector.currentText()
        if function_name == "Selecione uma função":
            self.name_input.setText("")
            self.code_input.setText("")
            return
        
        importlib.reload(preprocessing_custom)
        function = getattr(preprocessing_custom, function_name, None)
        if function:
            try:
                source = inspect.getsource(function)
                self.name_input.setText(function_name)
                self.code_input.setText(source.strip())
            except Exception as e:
                QMessageBox.warning(self, "Erro", f"Não foi possível carregar o código da função '{function_name}': {str(e)}")
                self.load_functions()
        else:
            QMessageBox.warning(self, "Erro", f"Função '{function_name}' não encontrada.")
            self.load_functions()

    def add_function(self):
        function_name = self.name_input.text().strip()
        function_code = self.code_input.toPlainText().strip()
        
        if not function_name or not function_code:
            QMessageBox.warning(self, "Erro", "O nome e o código da função não podem estar vazios.")
            return
        
        if not function_name.isidentifier():
            QMessageBox.warning(self, "Erro", "O nome da função deve ser um identificador válido (ex.: minha_funcao).")
            return
        
        importlib.reload(preprocessing_custom)
        if hasattr(preprocessing_custom, function_name):
            QMessageBox.warning(self, "Erro", f"A função '{function_name}' já existe. Escolha outro nome ou edite a função existente.")
            return
        
        # Dividir o código em linhas e pular linhas em branco ou comentários
        lines = function_code.splitlines()
        def_line = None
        for line in lines:
            stripped_line = line.strip()
            logger.debug(f"Verificando linha: '{stripped_line}'")
            if stripped_line and not stripped_line.startswith("#"):
                def_line = stripped_line
                break
        
        if not def_line:
            QMessageBox.warning(self, "Erro", "Nenhuma definição de função encontrada no código.")
            return
        
        # Extrair o nome da função do código
        if not def_line.startswith("def "):
            QMessageBox.warning(self, "Erro", "A primeira linha de código deve começar com 'def '.")
            return
        
        try:
            code_function_name = def_line.split('(')[0].split(' ')[1]
            logger.debug(f"Nome da função extraído do código: '{code_function_name}'")
        except IndexError:
            QMessageBox.warning(self, "Erro", "Formato inválido da definição da função. Use 'def nome(df, column):'.")
            return
        
        # Verificar se o nome digitado corresponde ao nome no código
        if code_function_name != function_name:
            QMessageBox.warning(self, "Erro", f"O nome da função no código ('{code_function_name}') não corresponde ao nome digitado ('{function_name}'). Eles devem ser idênticos.")
            return
        
        expected_def = f"def {function_name}(df, column):"
        logger.debug(f"Esperado: '{expected_def}'")
        logger.debug(f"Encontrado: '{def_line}'")
        
        if not def_line.startswith(expected_def):
            QMessageBox.warning(self, "Erro", "A função deve ter a assinatura 'def nome(df, column):' para ser compatível com o sistema.")
            return
        
        try:
            # Ler o conteúdo existente do arquivo
            try:
                with open("preprocessing_custom.py", "r", encoding="utf-8") as f:
                    existing_content = f.read()
            except FileNotFoundError:
                existing_content = ""
            
            # Separar imports e funções existentes
            existing_functions = []
            imports_section = []
            in_function = False
            current_function = []
            
            for line in existing_content.splitlines():
                stripped_line = line.strip()
                if stripped_line.startswith("def "):
                    in_function = True
                    if current_function:
                        existing_functions.append("\n".join(current_function))
                    current_function = [line]
                elif in_function and stripped_line == "":
                    in_function = False
                    existing_functions.append("\n".join(current_function))
                    current_function = []
                elif in_function:
                    current_function.append(line)
                else:
                    imports_section.append(line)
            
            if current_function:
                existing_functions.append("\n".join(current_function))
            
            # Adicionar a nova função
            existing_functions.append(function_code)
            
            # Reconstruir o arquivo com imports e funções
            with open("preprocessing_custom.py", "w", encoding="utf-8") as f:
                # Escrever os imports (evitar duplicatas)
                f.write("import pandas as pd\n")
                f.write("import logging\n")
                f.write("logger = logging.getLogger(__name__)\n")
                f.write("\n")
                # Escrever as funções
                f.write("\n\n".join(existing_functions))
            
            importlib.reload(preprocessing_custom)
            self.load_functions()
            QMessageBox.information(self, "Sucesso", f"Função '{function_name}' adicionada com sucesso!")
            self.name_input.clear()
            self.code_input.clear()
            self.function_selector.setCurrentIndex(0)
            # Atualizar a janela de detalhes (ColumnDetailsWindow)
            self.app_parent.refresh_custom_functions()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar a função: {str(e)}")

    def edit_function(self):
        function_name = self.function_selector.currentText()
        if function_name == "Selecione uma função":
            QMessageBox.warning(self, "Erro", "Selecione uma função para editar.")
            return
        
        new_function_name = self.name_input.text().strip()
        new_function_code = self.code_input.toPlainText().strip()
        
        if not new_function_name or not new_function_code:
            QMessageBox.warning(self, "Erro", "O nome e o código da função não podem estar vazios.")
            return
        
        if not new_function_name.isidentifier():
            QMessageBox.warning(self, "Erro", "O nome da função deve ser um identificador válido (ex.: minha_funcao).")
            return
        
        lines = new_function_code.splitlines()
        def_line = None
        for line in lines:
            stripped_line = line.strip()
            logger.debug(f"Verificando linha: '{stripped_line}'")
            if stripped_line and not stripped_line.startswith("#"):
                def_line = stripped_line
                break
        
        if not def_line:
            QMessageBox.warning(self, "Erro", "Nenhuma definição de função encontrada no código.")
            return
        
        # Extrair o nome da função do código
        if not def_line.startswith("def "):
            QMessageBox.warning(self, "Erro", "A primeira linha de código deve começar com 'def '.")
            return
        
        try:
            code_function_name = def_line.split('(')[0].split(' ')[1]
            logger.debug(f"Nome da função extraído do código: '{code_function_name}'")
        except IndexError:
            QMessageBox.warning(self, "Erro", "Formato inválido da definição da função. Use 'def nome(df, column):'.")
            return
        
        # Verificar se o nome digitado corresponde ao nome no código
        if code_function_name != new_function_name:
            QMessageBox.warning(self, "Erro", f"O nome da função no código ('{code_function_name}') não corresponde ao nome digitado ('{new_function_name}'). Eles devem ser idênticos.")
            return
        
        expected_def = f"def {new_function_name}(df, column):"
        logger.debug(f"Esperado: '{expected_def}'")
        logger.debug(f"Encontrado: '{def_line}'")
        
        if not def_line.startswith(expected_def):
            QMessageBox.warning(self, "Erro", "A função deve ter a assinatura 'def nome(df, column):' para ser compatível com o sistema.")
            return
        
        try:
            with open("preprocessing_custom.py", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            new_lines = []
            in_function = False
            function_found = False
            for line in lines:
                if line.startswith(f"def {function_name}("):
                    function_found = True
                    in_function = True
                    new_lines.append(new_function_code + "\n")
                elif in_function and line.strip() == "":
                    in_function = False
                elif not in_function:
                    new_lines.append(line)
            
            if not function_found:
                QMessageBox.warning(self, "Erro", f"Função '{function_name}' não encontrada no arquivo.")
                return
            
            with open("preprocessing_custom.py", "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            
            importlib.reload(preprocessing_custom)
            self.load_functions()
            QMessageBox.information(self, "Sucesso", f"Função '{function_name}' editada com sucesso!")
            self.name_input.clear()
            self.code_input.clear()
            self.function_selector.setCurrentIndex(0)
            # Atualizar a janela de detalhes (ColumnDetailsWindow)
            self.app_parent.refresh_custom_functions()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao editar a função: {str(e)}")

    def delete_function(self):
        function_name = self.function_selector.currentText()
        if function_name == "Selecione uma função":
            QMessageBox.warning(self, "Erro", "Selecione uma função para excluir.")
            return
        
        reply = QMessageBox.question(self, "Confirmação", 
                                    f"Tem certeza que deseja excluir a função '{function_name}'?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        try:
            with open("preprocessing_custom.py", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            new_lines = []
            in_function = False
            function_found = False
            for line in lines:
                if line.startswith(f"def {function_name}("):
                    function_found = True
                    in_function = True
                elif in_function and line.strip() == "":
                    in_function = False
                elif not in_function:
                    new_lines.append(line)
            
            if not function_found:
                QMessageBox.warning(self, "Erro", f"Função '{function_name}' não encontrada no arquivo.")
                return
            
            with open("preprocessing_custom.py", "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            
            self.function_selector.blockSignals(True)
            importlib.reload(preprocessing_custom)
            self.load_functions()
            self.function_selector.setCurrentIndex(0)
            self.name_input.clear()
            self.code_input.clear()
            self.function_selector.blockSignals(False)
            
            QMessageBox.information(self, "Sucesso", f"Função '{function_name}' excluída com sucesso!")
            # Atualizar a janela de detalhes (ColumnDetailsWindow)
            self.app_parent.refresh_custom_functions()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao excluir a função: {str(e)}")