#ui/visualization.py
import matplotlib
matplotlib.use('Qt5Agg')  # Configurar o backend para PyQt5

import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QStackedWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

class VisualizationWindow(QDialog):
    def __init__(self, df, training_columns, parent=None):
        super().__init__(parent)
        logger.debug("Iniciando criação da janela de visualização...")
        self.setWindowTitle("Gráficos de Perfil de Clientes")
        self.setGeometry(200, 200, 800, 600)
        
        self.df = df
        self.training_columns = training_columns
        self.current_page = 0  # Página atual
        self.pages = []  # Lista para armazenar as páginas de gráficos
        
        # Layout principal
        main_layout = QVBoxLayout()
        
        # Stacked widget para gerenciar as páginas de gráficos
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Criar as páginas de gráficos
        self.create_plot_pages()
        
        # Botões de navegação
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Anterior")
        self.prev_btn.clicked.connect(self.show_previous_page)
        self.prev_btn.setEnabled(False)  # Desabilitado na primeira página
        nav_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Próximo")
        self.next_btn.clicked.connect(self.show_next_page)
        if len(self.training_columns) <= 2:  # Desabilitado se houver 2 ou menos colunas (1 página)
            self.next_btn.setEnabled(False)
        nav_layout.addWidget(self.next_btn)
        
        # Botão para fechar a janela
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.close)
        nav_layout.addWidget(close_btn)
        
        main_layout.addLayout(nav_layout)
        self.setLayout(main_layout)
        logger.debug("Janela de visualização configurada com sucesso")

    def create_plot_pages(self):
        """Cria páginas de gráficos, com 2 colunas (4 gráficos) por página."""
        logger.debug("Criando páginas de gráficos...")
        # Dividir as colunas em grupos de 2
        columns_per_page = 2
        for i in range(0, len(self.training_columns), columns_per_page):
            page_columns = self.training_columns[i:i + columns_per_page]
            logger.debug(f"Criando página para as colunas: {page_columns}")
            
            # Criar uma figura para a página
            num_columns = len(page_columns)
            figure, axes = plt.subplots(num_columns, 2, figsize=(10, 5 * num_columns))
            # Ajustar o espaço entre os subplots para evitar sobreposição
            figure.subplots_adjust(hspace=0.5, wspace=0.3, top=0.85, bottom=0.1)
            
            # Garantir que axes seja uma lista 2D mesmo com uma única coluna
            if num_columns == 1:
                axes = [axes]
            
            # Separar os dados em potenciais compradores e não compradores
            buyers = self.df[self.df['result'] == 1]
            non_buyers = self.df[self.df['result'] == 0]
            
            # Gerar gráficos para as colunas da página
            for idx, column in enumerate(page_columns):
                logger.debug(f"Gerando gráficos para a coluna: {column}")
                if column not in self.df.columns:
                    logger.error(f"Coluna '{column}' não encontrada no DataFrame")
                    continue
                
                # Gráfico para potenciais compradores
                ax_buyers = axes[idx][0]
                if self.df[column].dtype in ['int64', 'float64']:
                    # Para colunas numéricas, usar histograma
                    logger.debug(f"Plotando histograma para potenciais compradores - {column}")
                    if len(buyers) > 0:
                        sns.histplot(data=buyers, x=column, ax=ax_buyers, color='blue', kde=True)
                    else:
                        ax_buyers.text(0.5, 0.5, "Nenhum dado disponível", ha='center', va='center')
                    ax_buyers.set_title(f"Potenciais Compradores - {column}")
                else:
                    # Para colunas categóricas, usar gráfico de contagem
                    logger.debug(f"Plotando countplot para potenciais compradores - {column}")
                    if len(buyers) > 0:
                        sns.countplot(data=buyers, x=column, ax=ax_buyers, color='blue')
                    else:
                        ax_buyers.text(0.5, 0.5, "Nenhum dado disponível", ha='center', va='center')
                    ax_buyers.set_title(f"Potenciais Compradores - {column}")
                
                # Gráfico para não compradores
                ax_non_buyers = axes[idx][1]
                if self.df[column].dtype in ['int64', 'float64']:
                    logger.debug(f"Plotando histograma para não compradores - {column}")
                    if len(non_buyers) > 0:
                        sns.histplot(data=non_buyers, x=column, ax=ax_non_buyers, color='red', kde=True)
                    else:
                        ax_non_buyers.text(0.5, 0.5, "Nenhum dado disponível", ha='center', va='center')
                    ax_non_buyers.set_title(f"Não Compradores - {column}")
                else:
                    logger.debug(f"Plotando countplot para não compradores - {column}")
                    if len(non_buyers) > 0:
                        sns.countplot(data=non_buyers, x=column, ax=ax_non_buyers, color='red')
                    else:
                        ax_non_buyers.text(0.5, 0.5, "Nenhum dado disponível", ha='center', va='center')
                    ax_non_buyers.set_title(f"Não Compradores - {column}")
            
            # Criar um widget para a página
            page_widget = QVBoxLayout()
            canvas = FigureCanvas(figure)
            page_widget.addWidget(canvas)
            self.pages.append(page_widget)
            self.stacked_widget.addWidget(canvas)
            logger.debug(f"Página de gráficos criada para as colunas: {page_columns}")
        
        logger.debug("Todas as páginas de gráficos foram criadas")

    def show_previous_page(self):
        """Exibe a página anterior de gráficos."""
        if self.current_page > 0:
            self.current_page -= 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            logger.debug(f"Exibindo página anterior: {self.current_page}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < len(self.pages) - 1)

    def show_next_page(self):
        """Exibe a próxima página de gráficos."""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.stacked_widget.setCurrentIndex(self.current_page)
            logger.debug(f"Exibindo próxima página: {self.current_page}")
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < len(self.pages) - 1)