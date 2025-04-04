# ui/visualization.py
import matplotlib
matplotlib.use('Qt5Agg')  # Define o backend para integração com PyQt5

import pandas as pd
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout, QStackedWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import seaborn as sns
import logging

logger = logging.getLogger(__name__)

class VisualizationWindow(QDialog):
    """Janela para exibir gráficos comparativos das colunas de treino."""
    
    def __init__(self, df, training_columns, parent=None):
        """Inicializa a janela com gráficos paginados.
        
        Args:
            df: DataFrame contendo os dados a serem exibidos nos gráficos.
            training_columns: Lista de colunas a visualizar.
            parent: Instância de MLApp, opcional, como janela pai.
        """
        super().__init__(parent)
        self.setWindowTitle("Gráficos de Perfil de Clientes")
        self.setGeometry(200, 200, 800, 600)
        
        self.df = df
        self.training_columns = training_columns
        self.current_page = 0  # Página inicial dos gráficos
        self.pages = []  # Lista para armazenar as páginas de gráficos
        
        main_layout = QVBoxLayout()  # Layout principal vertical
        self.stacked_widget = QStackedWidget()  # GERE a exibição das páginas
        main_layout.addWidget(self.stacked_widget)
        
        self.create_plot_pages()  # Gera as páginas de gráficos
        
        # Botões de navegação entre páginas
        nav_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Anterior")
        self.prev_btn.clicked.connect(self.show_previous_page)
        self.prev_btn.setEnabled(False)  # Desactiva na primeira página
        nav_layout.addWidget(self.prev_btn)
        
        self.next_btn = QPushButton("Próximo")
        self.next_btn.clicked.connect(self.show_next_page)
        self.next_btn.setEnabled(len(self.training_columns) > 2)  # Activa se houver mais de 2 colunas
        nav_layout.addWidget(self.next_btn)
        
        close_btn = QPushButton("Fechar")
        close_btn.clicked.connect(self.close)
        nav_layout.addWidget(close_btn)
        
        main_layout.addLayout(nav_layout)
        self.setLayout(main_layout)

    def create_plot_pages(self):
        """Cria páginas de gráficos, com 2 colunas (4 gráficos) por página."""
        columns_per_page = 2  # Número máximo de colunas por página
        for i in range(0, len(self.training_columns), columns_per_page):
            page_columns = self.training_columns[i:i + columns_per_page]  # Divide as colunas por página
            num_columns = len(page_columns)
            
            # Configura uma figura com subgráficos para compradores e não compradores
            figure, axes = plt.subplots(num_columns, 2, figsize=(10, 5 * num_columns))
            figure.subplots_adjust(hspace=0.5, wspace=0.3, top=0.85, bottom=0.1)  # Ajusta espaçamento
            if num_columns == 1:
                axes = [axes]  # Converte para lista 2D para consistência
            
            # Separa os dados em compradores (1) e não compradores (0)
            buyers = self.df[self.df['result'] == 1]
            non_buyers = self.df[self.df['result'] == 0]
            
            for idx, column in enumerate(page_columns):
                if column not in self.df.columns:
                    logger.error(f"Coluna '{column}' não encontrada no DataFrame")
                    continue  # Ignora colunas ausentes
                
                # Gráfico para compradores
                ax_buyers = axes[idx][0]
                if self.df[column].dtype in ['int64', 'float64']:
                    if len(buyers) > 0:
                        sns.histplot(data=buyers, x=column, ax=ax_buyers, color='blue', kde=True)  # Histograma para dados numéricos
                    else:
                        ax_buyers.text(0.5, 0.5, "Nenhum dado disponível", ha='center', va='center')
                else:
                    if len(buyers) > 0:
                        sns.countplot(data=buyers, x=column, ax=ax_buyers, color='blue')  # Gráfico de contagem para categóricos
                    else:
                        ax_buyers.text(0.5, 0.5, "Nenhum dado disponível", ha='center', va='center')
                ax_buyers.set_title(f"Potenciais Compradores - {column}")
                
                # Gráfico para não compradores
                ax_non_buyers = axes[idx][1]
                if self.df[column].dtype in ['int64', 'float64']:
                    if len(non_buyers) > 0:
                        sns.histplot(data=non_buyers, x=column, ax=ax_non_buyers, color='red', kde=True)
                    else:
                        ax_non_buyers.text(0.5, 0.5, "Nenhum dado disponível", ha='center', va='center')
                else:
                    if len(non_buyers) > 0:
                        sns.countplot(data=non_buyers, x=column, ax=ax_non_buyers, color='red')
                    else:
                        ax_non_buyers.text(0.5, 0.5, "Nenhum dado disponível", ha='center', va='center')
                ax_non_buyers.set_title(f"Não Compradores - {column}")
            
            # Integra a figura no layout da página
            canvas = FigureCanvas(figure)
            page_widget = QVBoxLayout()
            page_widget.addWidget(canvas)
            self.pages.append(page_widget)
            self.stacked_widget.addWidget(canvas)

    def show_previous_page(self):
        """Mostra a página anterior de gráficos e actualiza os botões de navegação."""
        if self.current_page > 0:
            self.current_page -= 1
            self.stacked_widget.setCurrentIndex(self.current_page)  # Retrocede uma página
        self.prev_btn.setEnabled(self.current_page > 0)  # Activa/desactiva botão "Anterior"
        self.next_btn.setEnabled(self.current_page < len(self.pages) - 1)  # Activa/desactiva botão "Próximo"

    def show_next_page(self):
        """Mostra a próxima página de gráficos e actualiza os botões de navegação."""
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.stacked_widget.setCurrentIndex(self.current_page)  # Avança uma página
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < len(self.pages) - 1)