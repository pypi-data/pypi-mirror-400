# ===================================================================================================================
# Nombre del archivo : container_floating_elements.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
import pygame
from .container_base import ContainerBase

class ContainerFloatingElements(ContainerBase):
    def __init__(self, pos=(0,0), size=None):
        super().__init__(pos)
        self._child_info = []  # Lista de (widget, rel_pos)

    def add_widget(self, widget, rel_pos):
        self._child_info.append((widget, rel_pos))
        self.children.append(widget)
        self.layout()  # asegurar layout inmediato

    def set_position(self, pos):
        super().set_position(pos)
        self.layout()

    def layout(self, x=None, y=None, width=None, height=None):
        gx, gy = self.pos
        max_w, max_h = 0, 0
        for widget, rel_pos in self._child_info:
            rx, ry = rel_pos
            widget.set_position((gx + rx, gy + ry))
            if widget.size:
                max_w = max(max_w, rx + widget.size[0])
                max_h = max(max_h, ry + widget.size[1])
        self.set_size((max_w, max_h))

    def draw(self, surface):
        for widget in self.children:
            widget.draw(surface)

    def handle_event(self, event):
        super().handle_event(event)

