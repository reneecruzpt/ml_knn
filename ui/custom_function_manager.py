# ui/custom_function_manager.py
import inspect
import importlib
import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit, QLineEdit, QComboBox, QMessageBox
from PyQt5.QtCore import QTimer
import preprocessing_custom

class CustomFunctionManagerWindow(QDialog):
    """Janela para criar, editar e excluir funções personalizadas de pré-processamento."""
    
    def __init__(self, parent=None):
        """Inicializa a janela de gestão de funções personalizadas.
        
        Args:
            parent: Janela pai, geralmente uma instância de ColumnDetailsWindow.
        """
        super().__init__(parent)
        self.setWindowTitle("Gerenciar Funções Personalizadas")
        self.setGeometry(300, 300, 600, 400)
        self.app_parent = parent
        
        layout = QVBoxLayout()  # Layout vertical principal
        
        # Caixa de selecção para funções existentes
        self.function_selector = QComboBox()
        self.function_selector.addItem("Selecione uma função")
        self.load_functions()  # Carrega funções disponíveis
        layout.addWidget(self.function_selector)
        
        # Campo de entrada para o nome da função
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Nome da função")
        layout.addWidget(self.name_input)
        
        # Campo de texto para o código da função
        self.code_input = QTextEdit()
        self.code_input.setPlaceholderText("Digite o código da função aqui (exemplo:\n"
                                           "def minha_funcao(df, column):\n"
                                           "    # Seu código aqui\n"
                                           "    return df)")
        layout.addWidget(self.code_input)
        
        # Botões de acção num layout horizontal
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
        
        self.function_selector.currentIndexChanged.connect(self.load_selected_function)  # Liga evento de selecção

    def load_functions(self):
        """Carrega as funções personalizadas do módulo preprocessing_custom na caixa de selecção."""
        try:
            with open("preprocessing_custom.py", "r", encoding="utf-8") as f:
                file_content = f.read()  # Verifica se o ficheiro existe
        except Exception as e:
            return  # Sai se houver erro ao abrir o ficheiro
        
        # Recarrega o módulo para garantir a versão mais recente
        if 'preprocessing_custom' in sys.modules:
            del sys.modules['preprocessing_custom']
        import preprocessing_custom
        
        functions = inspect.getmembers(preprocessing_custom, inspect.isfunction)  # Obtém funções do módulo
        
        self.function_selector.clear()  # Limpa a caixa de selecção
        self.function_selector.addItem("Selecione uma função")
        for name, _ in functions:
            self.function_selector.addItem(name)  # Adiciona nomes das funções

    def load_selected_function(self):
        """Carrega o nome e o código da função seleccionada nos campos de entrada."""
        function_name = self.function_selector.currentText()
        
        if function_name == "Selecione uma função" or not function_name:
            self.name_input.setText("")
            self.code_input.setText("")
            return  # Limpa campos se nenhuma função for seleccionada
        
        import preprocessing_custom
        function = getattr(preprocessing_custom, function_name, None)
        if function:
            try:
                source = inspect.getsource(function)  # Obtém o código fonte da função
                self.name_input.setText(function_name)
                self.code_input.setText(source.strip())
            except Exception as e:
                # Tenta recarregar o módulo em caso de erro
                if 'preprocessing_custom' in sys.modules:
                    del sys.modules['preprocessing_custom']
                import preprocessing_custom
                function = getattr(preprocessing_custom, function_name, None)
                if function:
                    try:
                        source = inspect.getsource(function)
                        self.name_input.setText(function_name)
                        self.code_input.setText(source.strip())
                    except Exception as e2:
                        QMessageBox.warning(self, "Erro", f"Não foi possível carregar o código da função '{function_name}': {str(e2)}")
                        self.load_functions()
                else:
                    QMessageBox.warning(self, "Erro", f"Função '{function_name}' não encontrada.")
                    self.load_functions()
        else:
            # Evita erro ao adicionar nova função sem dados preenchidos
            if not self.name_input.text().strip() and not self.code_input.toPlainText().strip():
                return
            QMessageBox.warning(self, "Erro", f"Função '{function_name}' não encontrada.")
            self.load_functions()

    def add_function(self):
        """Adiciona uma nova função ao módulo preprocessing_custom."""
        function_name = self.name_input.text().strip()
        function_code = self.code_input.toPlainText().strip()

        if not function_name or not function_code:
            QMessageBox.warning(self, "Erro", "O nome e o código da função não podem estar vazios.")
            return
        
        if not function_name.isidentifier():
            QMessageBox.warning(self, "Erro", "O nome da função deve ser um identificador válido (ex.: minha_funcao).")
            return
        
        import preprocessing_custom
        if hasattr(preprocessing_custom, function_name):
            QMessageBox.warning(self, "Erro", f"A função '{function_name}' já existe.")
            return
        
        # Valida a assinatura da função
        def_line = next((line.strip() for line in function_code.splitlines() if line.strip() and not line.strip().startswith("#")), None)
        if not def_line or not def_line.startswith("def "):
            QMessageBox.warning(self, "Erro", "A função deve começar com 'def '.")
            return
        
        try:
            code_function_name = def_line.split('(')[0].split(' ')[1]
            if code_function_name != function_name:
                QMessageBox.warning(self, "Erro", f"Nome no código ('{code_function_name}') difere do digitado ('{function_name}').")
                return
            if not def_line.startswith(f"def {function_name}(df, column):"):
                QMessageBox.warning(self, "Erro", "A função deve ter a assinatura 'def nome(df, column):'.")
                return
        except IndexError:
            QMessageBox.warning(self, "Erro", "Formato inválido da função. Use 'def nome(df, column):'.")
            return
        
        # Adiciona a função ao ficheiro preprocessing_custom.py
        try:
            try:
                with open("preprocessing_custom.py", "r", encoding="utf-8") as f:
                    existing_content = f.read()
            except FileNotFoundError:
                existing_content = "import pandas as pd\nimport logging\nlogger = logging.getLogger(__name__)\n\n"
            
            # Separa imports e funções existentes
            existing_functions, imports_section = [], []
            in_function, current_function = False, []
            for line in existing_content.splitlines():
                stripped_line = line.strip()
                if stripped_line.startswith("def "):
                    in_function = True
                    if current_function:
                        existing_functions.append("\n".join(current_function))
                    current_function = [line]
                elif in_function and not stripped_line:
                    in_function = False
                    existing_functions.append("\n".join(current_function))
                    current_function = []
                elif in_function:
                    current_function.append(line)
                else:
                    imports_section.append(line)
            if current_function:
                existing_functions.append("\n".join(current_function))
            
            existing_functions.append(function_code)  # Adiciona a nova função
            with open("preprocessing_custom.py", "w", encoding="utf-8") as f:
                f.write("\n".join(imports_section) + "\n\n" + "\n\n".join(existing_functions))
            
            # Recarrega o módulo actualizado
            if 'preprocessing_custom' in sys.modules:
                del sys.modules['preprocessing_custom']
            import preprocessing_custom
            
            self.load_functions()
            QMessageBox.information(self, "Sucesso", f"Função '{function_name}' adicionada com sucesso!")
            self.name_input.clear()
            self.code_input.clear()
            self.function_selector.setCurrentIndex(0)
            if self.app_parent:
                self.app_parent.refresh_custom_functions()  # Actualiza a janela pai
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao adicionar a função: {str(e)}")

    def edit_function(self):
        """Edita uma função existente no módulo preprocessing_custom."""
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
            QMessageBox.warning(self, "Erro", "O nome da função deve ser um identificador válido.")
            return
        
        # Valida a assinatura da nova função
        def_line = next((line.strip() for line in new_function_code.splitlines() if line.strip() and not line.strip().startswith("#")), None)
        if not def_line or not def_line.startswith("def "):
            QMessageBox.warning(self, "Erro", "A função deve começar com 'def '.")
            return
        
        try:
            code_function_name = def_line.split('(')[0].split(' ')[1]
            if code_function_name != new_function_name:
                QMessageBox.warning(self, "Erro", f"Nome no código ('{code_function_name}') difere do digitado ('{new_function_name}').")
                return
            if not def_line.startswith(f"def {new_function_name}(df, column):"):
                QMessageBox.warning(self, "Erro", "A função deve ter a assinatura 'def nome(df, column):'.")
                return
        except IndexError:
            QMessageBox.warning(self, "Erro", "Formato inválido da função. Use 'def nome(df, column):'.")
            return
        
        # Substitui a função no ficheiro
        try:
            with open("preprocessing_custom.py", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            new_lines, in_function, function_found = [], False, False
            i = 0
            while i < len(lines):
                line = lines[i]
                if line.strip().startswith(f"def {function_name}("):
                    function_found = True
                    in_function = True
                    new_lines.append(new_function_code + "\n")  # Substitui pela nova função
                    i += 1
                    while i < len(lines) and (lines[i].startswith(" ") or lines[i].strip() == ""):
                        i += 1
                else:
                    if not in_function:
                        new_lines.append(line)
                    i += 1
                if in_function and i < len(lines) and not lines[i].strip():
                    in_function = False
            
            if not function_found:
                QMessageBox.warning(self, "Erro", f"Função '{function_name}' não encontrada.")
                return
            
            with open("preprocessing_custom.py", "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            
            # Recarrega o módulo
            if 'preprocessing_custom' in sys.modules:
                del sys.modules['preprocessing_custom']
            try:
                import preprocessing_custom
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Erro ao recarregar o módulo preprocessing_custom: {str(e)}")
                return
            
            self.function_selector.blockSignals(True)  # Evita eventos durante actualização
            self.load_functions()
            self.function_selector.setCurrentIndex(0)
            self.function_selector.blockSignals(False)
            
            self.name_input.clear()
            self.code_input.clear()
            
            QMessageBox.information(self, "Sucesso", f"Função '{function_name}' editada com sucesso!")
            if self.app_parent:
                self.app_parent.refresh_custom_functions()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao editar a função: {str(e)}")

    def delete_function(self):
        """Remove uma função do módulo preprocessing_custom e actualiza a interface."""
        function_name = self.function_selector.currentText()
        if function_name == "Selecione uma função":
            QMessageBox.warning(self, "Erro", "Selecione uma função para excluir.")
            return
        
        # Pede confirmação ao utilizador
        reply = QMessageBox.question(self, "Confirmação", 
                                    f"Tem certeza que deseja excluir a função '{function_name}'?",
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply != QMessageBox.Yes:
            return
        
        try:
            with open("preprocessing_custom.py", "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Remove a função seleccionada
            new_lines = []
            in_function = False
            function_found = False
            i = 0
            while i < len(lines):
                line = lines[i]
                if not line.startswith(" ") and line.strip().startswith(f"def {function_name}("):
                    function_found = True
                    in_function = True
                    i += 1
                    while i < len(lines):
                        if not lines[i].startswith(" ") and (lines[i].strip().startswith("def ") or lines[i].strip() == ""):
                            break
                        i += 1
                    if i < len(lines) and lines[i].strip() == "":
                        i += 1
                    in_function = False
                else:
                    new_lines.append(line)
                    i += 1
            
            if not function_found:
                QMessageBox.warning(self, "Erro", f"Função '{function_name}' não encontrada.")
                return
            
            # Remove linhas em branco extras
            new_lines = [line for line in new_lines if line.strip() != "" or new_lines.index(line) == 0]
            while len(new_lines) > 1 and new_lines[-1].strip() == "":
                new_lines.pop()
            
            with open("preprocessing_custom.py", "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            
            # Recarrega o módulo
            if 'preprocessing_custom' in sys.modules:
                del sys.modules['preprocessing_custom']
            import preprocessing_custom
            
            self.function_selector.blockSignals(True)
            self.load_functions()
            self.function_selector.setCurrentIndex(0)
            self.function_selector.blockSignals(False)
            
            self.name_input.clear()
            self.code_input.clear()
            
            QMessageBox.information(self, "Sucesso", f"Função '{function_name}' excluída com sucesso!")
            if self.app_parent:
                column = self.app_parent.column
                df = self.app_parent.df
                update_callback = self.app_parent.update_callback
                parent = self.app_parent.app_parent
                
                col_data = df[column]
                dtype = str(col_data.dtype)
                null_count = col_data.isnull().sum()
                unique_values = col_data.dropna().unique()
                try:
                    unique_values = [float(val) for val in unique_values]
                except (ValueError, TypeError):
                    unique_values = [str(val) for val in unique_values]
                unique_values = sorted(unique_values)
                unique_str = ", ".join(map(str, unique_values[:5 if len(unique_values) > 10 else len(unique_values)]))
                if len(unique_values) > 10:
                    unique_str += f" (primeiros 5 de {len(unique_values)} valores únicos)"
                details = f"Detalhes da coluna '{column}':\n- Tipo de dados: {dtype}\n- Contagem de valores nulos: {null_count}\n- Valores únicos: {unique_str}"
                
                self.app_parent.close()
                QTimer.singleShot(100, lambda: self.reopen_details_window(column, details, df, update_callback, parent))  # Reabre janela com atraso
            
            self.close()
        except Exception as e:
            raise

    def reopen_details_window(self, column, details, df, update_callback, parent):
        """Reabre a janela de detalhes com os dados fornecidos.
        
        Args:
            column: Nome da coluna a detalhar.
            details: Texto com os detalhes da coluna.
            df: DataFrame actualizado.
            update_callback: Função de retorno para actualizar a interface.
            parent: Janela pai.
        """
        from ui.details_window import ColumnDetailsWindow
        new_details_window = ColumnDetailsWindow(column, details, df, update_callback, parent)
        new_details_window.exec_()  # Mostra a nova janela de detalhes