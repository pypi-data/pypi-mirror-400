# ===================================================================================================================
# Nombre del archivo : container_label_input_text.py
# Autor              : Antonio castro Snurmacher 
# Licencia           : MIT
# Versión Python     : 3.x
# ===================================================================================================================
import pygame
from .container_base import ContainerBase
from .widget_label import LabelWidget

class ContainerLabelInput(ContainerBase):
    def __init__(self, pos=(0, 0), font_size=28, spacing_scale=0.8):
        super().__init__(pos)
        self.font_size = font_size
        self.spacing_scale = spacing_scale
        self.pairs = []
        self.max_label_width = 0

    def add_pair(self, label_text, input_widget):
        label = LabelWidget("label_" + input_widget.id, None, label_text, font_size=self.font_size)
        self.max_label_width = max(self.max_label_width, label.size[0])
        self.pairs.append((label, input_widget))
        self.add([label, input_widget])

    def set_position(self, pos):
        super().set_position(pos)
        self.layout()

    def layout(self, x=None, y=None, width=None, height=None):
        x, y = self.pos
        spacing = int(self.font_size * self.spacing_scale)
        y_inicial = y
        max_input_width = 0

        for label, input_widget in self.pairs:
            label_x = x + self.max_label_width - label.size[0]
            label.set_position((label_x, y))
            input_widget.set_position((x + self.max_label_width + spacing, y))
            alto = max(label.size[1], input_widget.size[1])
            y += alto + spacing
            max_input_width = max(max_input_width, input_widget.size[0])

        ancho_total = self.max_label_width + spacing + max_input_width
        alto_total = y - y_inicial
        self.set_size((ancho_total, alto_total))

    def draw(self, surface):
        for widget in self.get_widgets():
            widget.draw(surface)

    def handle_event(self, event):
        super().handle_event(event)

    def get_widgets(self):
        return [widget for label, input_widget in self.pairs for widget in (label, input_widget)]

