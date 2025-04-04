# ui/screens.py
import logging
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QSpinBox
from ui.data_manager import load_csv
from ui.model_interface import train_model, save_model, load_model

logger = logging.getLogger(__name__)

def setup_screen1(app):
    """Configura a Tela 1 para carregamento de CSV e selecção de colunas.
    
    Args:
        app: Instância de MLApp para adicionar widgets ao screen1_layout.
    """
    app.screen1_layout.addWidget(QLabel("Ecrã 1: Carregar CSV e Seleccionar Colunas"))
    
    # Informa o utilizador sobre a necessidade da coluna 'result'
    info_label = QLabel("Nota: O CSV deve conter uma coluna chamada 'result' para o treino do modelo.")
    info_label.setStyleSheet("color: blue;")  # Destaca a informação em azul
    app.screen1_layout.addWidget(info_label)
    
    app.load_btn = QPushButton("Carregar CSV")
    app.load_btn.clicked.connect(lambda: load_csv(app))  # Associa o carregamento do CSV
    app.screen1_layout.addWidget(app.load_btn)
    
    # Cabeçalho das colunas, visível apenas após carregamento do CSV
    app.columns_header_label = QLabel("Colunas do CSV")
    app.columns_header_label.setVisible(False)
    app.screen1_layout.addWidget(app.columns_header_label)
    
    # Área dedicada à exibição das colunas
    app.columns_widget = QWidget()
    app.columns_layout = QVBoxLayout(app.columns_widget)
    app.screen1_layout.addWidget(app.columns_widget)
    
    # Navegação para avançar para a Tela 2
    app.nav_layout_screen1 = QHBoxLayout()
    app.next_btn = QPushButton("Próximo")
    app.next_btn.clicked.connect(app.show_screen2)
    app.nav_layout_screen1.addStretch()  # Alinha o botão à direita
    app.nav_layout_screen1.addWidget(app.next_btn)
    app.screen1_layout.addLayout(app.nav_layout_screen1)
    
    app.screen1_layout.addStretch()  # Adiciona espaço vertical no fim

def setup_screen2(app):
    """Configura a Tela 2 para treino e gestão do modelo.
    
    Args:
        app: Instância de MLApp para adicionar widgets ao screen2_layout.
    """
    app.screen2_layout.addWidget(QLabel("Ecrã 2: Treino do Modelo"))
    
    # Campo para definir o número de vizinhos (K) do KNN
    neighbors_layout = QHBoxLayout()
    neighbors_label = QLabel("Número de Vizinhos (K):")
    app.neighbors_input = QSpinBox()
    app.neighbors_input.setRange(1, 50)  # Define intervalo permitido
    app.neighbors_input.setValue(5)  # Valor inicial padrão
    neighbors_layout.addWidget(neighbors_label)
    neighbors_layout.addWidget(app.neighbors_input)
    app.screen2_layout.addLayout(neighbors_layout)
    
    # Botões para acções relacionadas com o modelo
    train_btn = QPushButton("Treinar Modelo")
    train_btn.clicked.connect(lambda: train_model(app))  # Inicia o treino
    app.screen2_layout.addWidget(train_btn)
    
    save_btn = QPushButton("Guardar Modelo")
    save_btn.clicked.connect(lambda: save_model(app))  # Guarda o modelo treinado
    app.screen2_layout.addWidget(save_btn)
    
    load_model_btn = QPushButton("Carregar Modelo")
    load_model_btn.clicked.connect(lambda: load_model(app))  # Carrega um modelo existente
    app.screen2_layout.addWidget(load_model_btn)
    
    # Botão para gráficos, mostrado apenas após o treino
    app.plot_btn = QPushButton("Gerar Gráficos")
    app.plot_btn.clicked.connect(app.show_plots)
    app.plot_btn.setVisible(False)
    app.screen2_layout.addWidget(app.plot_btn)
    
    app.result_label = QLabel("Resultados aparecerão aqui após o treino.")
    app.screen2_layout.addWidget(app.result_label)
    
    # Navegação entre telas
    nav_layout = QHBoxLayout()
    prev_btn = QPushButton("Anterior")
    prev_btn.clicked.connect(app.show_screen1)  # Volta à Tela 1
    next_btn = QPushButton("Próximo")
    next_btn.clicked.connect(app.show_screen3)  # Avança para a Tela 3
    nav_layout.addWidget(prev_btn)
    nav_layout.addStretch()  # Espaço para alinhar os botões
    nav_layout.addWidget(next_btn)
    app.screen2_layout.addLayout(nav_layout)
    
    app.screen2_layout.addStretch()  # Adiciona espaço vertical no fim