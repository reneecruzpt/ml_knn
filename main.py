# main.py
import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MLApp

if __name__ == '__main__':
    """Ponto de entrada da aplicação KNN Machine Learning."""
    app = QApplication(sys.argv)  # Inicializa a aplicação PyQt5
    window = MLApp()  # Cria a janela principal da aplicação
    window.show()  # Exibe a janela
    sys.exit(app.exec_())  # Inicia o ciclo de eventos e termina a aplicação ao fechar