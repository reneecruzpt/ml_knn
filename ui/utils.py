# ui/utils.py
import logging

logger = logging.getLogger(__name__)

def clear_layout(layout):
    """
    Remove todos os itens de um layout PyQt5 recursivamente.
    
    Args:
        layout (QLayout): O layout a ser limpo.
    """
    logger.debug(f"Iniciando limpeza do layout: {layout}")
    logger.debug(f"Itens no layout antes da limpeza: {layout.count()}")
    while layout.count():
        item = layout.takeAt(0)
        widget = item.widget()
        if widget:
            widget.setParent(None)
            logger.debug(f"Removido widget: {widget}")
            widget.deleteLater()
        elif item.layout():
            clear_layout(item.layout())
        del item
    logger.debug(f"Layout limpo, itens restantes: {layout.count()}")