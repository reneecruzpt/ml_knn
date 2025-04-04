# ui/main_window.py
import logging
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem
from ui.screens import setup_screen1, setup_screen2
from ui.data_manager import load_csv, load_test_csv
from ui.column_interface import display_columns
from ui.model_interface import train_model, save_model, load_model, predict_new_client, show_plots
from ui.utils import clear_layout

logger = logging.getLogger(__name__)

class MLApp(QMainWindow):
    """Classe principal da aplicação, gere as telas e o estado global."""
    
    def __init__(self):
        """Inicializa a janela principal com três telas usando QStackedWidget."""
        super().__init__()
        self.setWindowTitle("Aplicação KNN - Machine Learning")
        self.setGeometry(100, 100, 800, 600)
        
        # Estado global da aplicação
        self.df = None  # DataFrame carregado
        self.knn = None  # Modelo KNN treinado
        self.scaler = None  # Normalizador para os dados
        self.selected_columns = []  # Colunas seleccionadas para treino
        self.training_columns = []  # Colunas usadas no treino
        self.valid_values = {}  # Valores válidos das colunas
        
        # Configura o widget central com um layout para alternar telas
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.stacked_widget = QStackedWidget()  # Permite alternar entre telas
        self.layout.addWidget(self.stacked_widget)
        
        # Inicializa as três telas da aplicação
        self.screen1_widget = QWidget()
        self.screen1_layout = QVBoxLayout(self.screen1_widget)
        setup_screen1(self)  # Configura a Tela 1
        
        self.screen2_widget = QWidget()
        self.screen2_layout = QVBoxLayout(self.screen2_widget)
        setup_screen2(self)  # Configura a Tela 2
        
        self.screen3_widget = QWidget()
        self.screen3_layout = QVBoxLayout(self.screen3_widget)  # Tela 3 será configurada dinamicamente
        
        # Adiciona as telas ao QStackedWidget
        self.stacked_widget.addWidget(self.screen1_widget)  # Tela 1: Carregar CSV
        self.stacked_widget.addWidget(self.screen2_widget)  # Tela 2: Treino
        self.stacked_widget.addWidget(self.screen3_widget)  # Tela 3: Previsão
        
        self.show_screen1()  # Mostra a Tela 1 por defeito

    def show_screen1(self, checked=False):
        """Mostra a Tela 1 e actualiza as colunas se o DataFrame estiver carregado.
        
        Args:
            checked: Estado do evento (não utilizado), padrão False.
        """
        self.stacked_widget.setCurrentIndex(0)  # Define a Tela 1 como activa
        if self.df is not None:
            display_columns(self)  # Actualiza a exibição das colunas

    def show_screen2(self, checked=False):
        """Mostra a Tela 2 se o DataFrame e as colunas estiverem definidos.
        
        Args:
            checked: Estado do evento (não utilizado), padrão False.
        """
        if self.df is not None and self.selected_columns:
            self.stacked_widget.setCurrentIndex(1)  # Define a Tela 2 como activa
        else:
            self.result_label.setText("Carregue um CSV e seleccione colunas antes de prosseguir.")

    def show_screen3(self, checked=False):
        """Mostra a Tela 3 com campos para previsão ou uma mensagem de erro.
        
        Args:
            checked: Estado do evento (não utilizado), padrão False.
        """
        clear_layout(self.screen3_layout)  # Limpa o layout para reconstrução
        self.screen3_layout.addWidget(QLabel("Ecrã 3: Prever Novo Cliente"))
        
        if self.knn and self.scaler and self.training_columns:
            # Cria campos de entrada para cada coluna de treino
            self.inputs = {}
            unique_columns = list(dict.fromkeys(self.training_columns))  # Remove duplicados
            for col in unique_columns:
                self.screen3_layout.addWidget(QLabel(f"{col}:"))
                self.inputs[col] = QLineEdit()  # Campo para entrada de dados
                self.screen3_layout.addWidget(self.inputs[col])
            
            predict_btn = QPushButton("Prever")
            predict_btn.clicked.connect(lambda: self.predict_new_client())  # Associa a previsão
            self.screen3_layout.addWidget(predict_btn)
            
            self.predict_result = QLabel("Resultado da previsão aparecerá aqui.")
            self.screen3_layout.addWidget(self.predict_result)
            
            load_test_btn = QPushButton("Carregar CSV de Teste")
            load_test_btn.clicked.connect(lambda: load_test_csv(self))  # Carrega CSV de teste
            self.screen3_layout.addWidget(load_test_btn)
            
            self.test_result_table = QTableWidget()
            self.test_result_table.setColumnCount(2)
            self.test_result_table.setHorizontalHeaderLabels(["ID", "Previsão"])  # Configura tabela de resultados
            self.screen3_layout.addWidget(self.test_result_table)
        else:
            self.screen3_layout.addWidget(QLabel("Treine ou carregue um modelo com colunas definidas para fazer previsões."))
        
        # Adiciona navegação para voltar à Tela 2
        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("Anterior")
        prev_btn.clicked.connect(self.show_screen2)
        nav_layout.addWidget(prev_btn)
        nav_layout.addStretch()  # Espaço para alinhamento
        self.screen3_layout.addLayout(nav_layout)
        
        self.screen3_layout.addStretch()
        self.stacked_widget.setCurrentIndex(2)  # Define a Tela 3 como activa

    # Métodos delegados ao model_interface
    def train_model(self):
        """Treina o modelo KNN usando os dados seleccionados."""
        train_model(self)

    def save_model(self):
        """Guarda o modelo treinado em ficheiro."""
        save_model(self)

    def load_model(self):
        """Carrega um modelo previamente guardado."""
        load_model(self)

    def predict_new_client(self):
        """Realiza a previsão para um novo cliente com base nas entradas."""
        predict_new_client(self)

    def show_plots(self):
        """Mostra gráficos relacionados com o modelo treinado."""
        show_plots(self)