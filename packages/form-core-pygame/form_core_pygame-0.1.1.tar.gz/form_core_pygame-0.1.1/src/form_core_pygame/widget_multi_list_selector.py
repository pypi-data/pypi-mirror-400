# ===================================================================================================================
# Nombre del archivo : widget_multi_list_selector.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
"""
Descripción:
     Widget para seleccionar múltiples ítems de una lista con scroll vertical.
     Este módulo define la clase WidgetMultiListSelector, que extiende WidgetSingleListSelector para permitir
     la selección múltiple. El usuario puede alternar elementos clicando sobre ellos, y la selección se refleja
     visualmente. Hereda el sistema de scroll vertical con autorepeat, el renderizado y el posicionamiento.
     Se usa para recoger varias opciones desde un único campo en interfaces con Pygame.
"""

import pygame
from .widget_single_list_selector import WidgetSingleListSelector

class WidgetMultiListSelector(WidgetSingleListSelector):
    """
    Selector múltiple: hereda scroll y rendering, pero on_select alterna selección.
    """
    def __init__(self, id, pos, size, opciones):
        super().__init__(id, pos, size, opciones)
        self.selected_indices = set()

    def draw_line(self, surface, idx, y_offset):
        texto = self.opciones[idx]
        color_bg = (180, 180, 255) if idx in self.selected_indices else (255, 255, 255)
        pygame.draw.rect(surface, color_bg,
                         (0, y_offset, self.size[0] - self.scroll_bar_width, self.line_height))
        render = self.font.render(texto, True, (0, 0, 0))
        surface.blit(render, (5, y_offset + 5))

    def on_select(self, idx):
        if idx in self.selected_indices:
            self.selected_indices.remove(idx)
        else:
            self.selected_indices.add(idx)

    def get_value(self):
        return [self.opciones[i] for i in sorted(self.selected_indices)]

