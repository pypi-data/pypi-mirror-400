# ===================================================================================================================
# Nombre del archivo : container_label_checkbox.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
import pygame
from .container_base import ContainerBase

class ContainerLabelCheckbox(ContainerBase):
    def __init__(self, pos=(0, 0), margin_scale=0.8):
        super().__init__(pos)
        self.margin_scale = margin_scale

    def add_checkbox(self, widget_checkbox):
        self.add(widget_checkbox)

    def set_position(self, pos):
        super().set_position(pos)
        self.layout()

    def layout(self, x=None, y=None, width=None, height=None):
        x, y = self.pos
        max_width = 0
        y_inicial = y
        for checkbox in self.children:
            checkbox.set_position((x, y))
            font_size = getattr(checkbox, "checkbox_size", 28)
            margen = int(font_size * self.margin_scale)
            y += checkbox.size[1] + margen
            max_width = max(max_width, checkbox.size[0])

        alto_total = y - y_inicial
        self.set_size((max_width, alto_total))

    def draw(self, surface):
        for checkbox in self.children:
            checkbox.draw(surface)

    def handle_event(self, event):
        super().handle_event(event)

    def get_widgets(self):
        return self.children[:]

