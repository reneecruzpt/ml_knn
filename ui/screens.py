# ui/screens.py
import logging
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QHBoxLayout, QVBoxLayout, QCheckBox, QLineEdit, QSpinBox)
from ui.data_manager import load_csv  # Importar load_csv do módulo correto
from ui.model_interface import train_model, save_model, load_model  # Importar funções de model_interface

# Configurar o logger
logger = logging.getLogger(__name__)

def setup_screen1(app):
    app.screen1_layout.addWidget(QLabel("Ecrã 1: Carregar CSV e Selecionar Colunas"))
    
    # Mensagem informativa sobre a coluna 'result'
    info_label = QLabel("Nota: O CSV deve conter uma coluna chamada 'result' para o treinamento do modelo.")
    info_label.setStyleSheet("color: blue;")
    app.screen1_layout.addWidget(info_label)
    
    app.load_btn = QPushButton("Carregar CSV")
    app.load_btn.clicked.connect(lambda: load_csv(app))  # Usar lambda para passar app
    app.screen1_layout.addWidget(app.load_btn)
    
    # Label "Colunas do CSV" (inicialmente invisível)
    app.columns_header_label = QLabel("Colunas do CSV")
    app.columns_header_label.setVisible(False)
    app.screen1_layout.addWidget(app.columns_header_label)
    
    app.columns_widget = QWidget()
    app.columns_layout = QVBoxLayout(app.columns_widget)
    app.screen1_layout.addWidget(app.columns_widget)
    
    # Botões de navegação
    app.nav_layout_screen1 = QHBoxLayout()
    app.next_btn = QPushButton("Próximo")
    app.next_btn.clicked.connect(app.show_screen2)
    app.nav_layout_screen1.addStretch()
    app.nav_layout_screen1.addWidget(app.next_btn)
    app.screen1_layout.addLayout(app.nav_layout_screen1)
    
    app.screen1_layout.addStretch()

def setup_screen2(app):
    logger.debug("Configurando Ecrã 2...")
    app.screen2_layout.addWidget(QLabel("Ecrã 2: Treinamento do Modelo"))
    
    # Adicionar campo para número de vizinhos
    neighbors_layout = QHBoxLayout()
    neighbors_label = QLabel("Número de Vizinhos (K):")
    app.neighbors_input = QSpinBox()
    app.neighbors_input.setRange(1, 50)  # Intervalo de 1 a 50
    app.neighbors_input.setValue(5)      # Valor padrão
    neighbors_layout.addWidget(neighbors_label)
    neighbors_layout.addWidget(app.neighbors_input)
    app.screen2_layout.addLayout(neighbors_layout)
    logger.debug("Campo para número de vizinhos adicionado")
    
    train_btn = QPushButton("Treinar Modelo")
    train_btn.clicked.connect(lambda: train_model(app))  # Usar lambda para passar app
    app.screen2_layout.addWidget(train_btn)
    logger.debug("Botão 'Treinar Modelo' adicionado")
    
    save_btn = QPushButton("Salvar Modelo")
    save_btn.clicked.connect(lambda: save_model(app))  # Usar lambda para passar app
    app.screen2_layout.addWidget(save_btn)
    logger.debug("Botão 'Salvar Modelo' adicionado")
    
    load_model_btn = QPushButton("Carregar Modelo")
    load_model_btn.clicked.connect(lambda: load_model(app))  # Usar lambda para passar app
    app.screen2_layout.addWidget(load_model_btn)
    logger.debug("Botão 'Carregar Modelo' adicionado")
    
    # Botão para gerar gráficos (inicialmente invisível)
    app.plot_btn = QPushButton("Gerar Gráficos")
    app.plot_btn.clicked.connect(app.show_plots)
    app.plot_btn.setVisible(False)  # Só será visível após o treinamento
    app.screen2_layout.addWidget(app.plot_btn)
    logger.debug("Botão 'Gerar Gráficos' criado e adicionado (inicialmente invisível)")
    
    app.result_label = QLabel("Resultados aparecerão aqui após o treinamento.")
    app.screen2_layout.addWidget(app.result_label)
    logger.debug("Label de resultados adicionada")
    
    # Botões de navegação
    nav_layout = QHBoxLayout()
    prev_btn = QPushButton("Anterior")
    prev_btn.clicked.connect(app.show_screen1)
    next_btn = QPushButton("Próximo")
    next_btn.clicked.connect(app.show_screen3)
    nav_layout.addWidget(prev_btn)
    nav_layout.addStretch()
    nav_layout.addWidget(next_btn)
    app.screen2_layout.addLayout(nav_layout)
    logger.debug("Botões de navegação adicionados")
    
    app.screen2_layout.addStretch()
    logger.debug("Ecrã 2 configurado com sucesso")