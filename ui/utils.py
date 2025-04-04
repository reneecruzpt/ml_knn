# ui/utils.py
import logging

logger = logging.getLogger(__name__)

def clear_layout(layout):
    """Remove todos os itens de um layout PyQt5 de forma recursiva.
    
    Args:
        layout: Objecto QLayout a ser limpo.
    """
    while layout.count():  # Enquanto houver itens no layout
        item = layout.takeAt(0)  # Remove o primeiro item
        widget = item.widget()
        if widget:
            widget.setParent(None)  # Desassocia o widget do layout
            widget.deleteLater()   # Agenda a eliminação do widget para libertar recursos
        elif item.layout():
            clear_layout(item.layout())  # Limpa sublayouts de forma recursiva
        del item  # Elimina o item do layout