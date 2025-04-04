# ui/main_window.py
import logging
from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton, QHBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem
from ui.screens import setup_screen1, setup_screen2
from ui.data_manager import load_csv, load_test_csv
from ui.column_interface import display_columns
from ui.model_interface import train_model, save_model, load_model, predict_new_client, show_plots
from ui.utils import clear_layout

# Configurar logging para depuração
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MLApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aplicação KNN - Machine Learning")
        self.setGeometry(100, 100, 800, 600)
        
        # Variáveis globais
        self.df = None
        self.knn = None
        self.scaler = None
        self.selected_columns = []
        self.training_columns = []
        self.valid_values = {}
        
        # Configuração das telas com QStackedWidget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.stacked_widget = QStackedWidget()
        self.layout.addWidget(self.stacked_widget)
        
        # Inicializar os ecrãs
        self.screen1_widget = QWidget()
        self.screen1_layout = QVBoxLayout(self.screen1_widget)
        setup_screen1(self)
        
        self.screen2_widget = QWidget()
        self.screen2_layout = QVBoxLayout(self.screen2_widget)
        setup_screen2(self)
        
        self.screen3_widget = QWidget()
        self.screen3_layout = QVBoxLayout(self.screen3_widget)
        
        # Adicionar os ecrãs ao QStackedWidget
        self.stacked_widget.addWidget(self.screen1_widget)  # Índice 0
        self.stacked_widget.addWidget(self.screen2_widget)  # Índice 1
        self.stacked_widget.addWidget(self.screen3_widget)  # Índice 2
        
        # Exibir o Ecrã 1
        self.show_screen1()

    def show_screen1(self, checked=False):
        self.stacked_widget.setCurrentIndex(0)
        if self.df is not None:
            display_columns(self)

    def show_screen2(self, checked=False):
        if self.df is not None and self.selected_columns:
            self.stacked_widget.setCurrentIndex(1)
        else:
            self.result_label.setText("Carregue um CSV e selecione colunas antes de prosseguir.")

    def show_screen3(self, checked=False):
        clear_layout(self.screen3_layout)
        self.screen3_layout.addWidget(QLabel("Ecrã 3: Prever Novo Cliente"))
        
        if self.knn and self.scaler and self.training_columns:
            self.inputs = {}
            unique_columns = list(dict.fromkeys(self.training_columns))
            for col in unique_columns:
                self.screen3_layout.addWidget(QLabel(f"{col}:"))
                self.inputs[col] = QLineEdit()
                self.screen3_layout.addWidget(self.inputs[col])
            
            predict_btn = QPushButton("Prever")
            predict_btn.clicked.connect(lambda: self.predict_new_client())
            self.screen3_layout.addWidget(predict_btn)
            
            self.predict_result = QLabel("Resultado da previsão aparecerá aqui.")
            self.screen3_layout.addWidget(self.predict_result)
            
            load_test_btn = QPushButton("Carregar CSV de Teste")
            load_test_btn.clicked.connect(lambda: load_test_csv(self))
            self.screen3_layout.addWidget(load_test_btn)
            
            self.test_result_table = QTableWidget()
            self.test_result_table.setColumnCount(2)
            self.test_result_table.setHorizontalHeaderLabels(["ID", "Previsão"])
            self.screen3_layout.addWidget(self.test_result_table)
        else:
            self.screen3_layout.addWidget(QLabel("Treine ou carregue um modelo com colunas definidas para fazer previsões."))
        
        nav_layout = QHBoxLayout()
        prev_btn = QPushButton("Anterior")
        prev_btn.clicked.connect(self.show_screen2)
        nav_layout.addWidget(prev_btn)
        nav_layout.addStretch()
        self.screen3_layout.addLayout(nav_layout)
        
        self.screen3_layout.addStretch()
        self.stacked_widget.setCurrentIndex(2)

    # Métodos delegados de model_interface
    def train_model(self):
        train_model(self)

    def save_model(self):
        save_model(self)

    def load_model(self):
        load_model(self)

    def predict_new_client(self):
        predict_new_client(self)

    def show_plots(self):
        show_plots(self)