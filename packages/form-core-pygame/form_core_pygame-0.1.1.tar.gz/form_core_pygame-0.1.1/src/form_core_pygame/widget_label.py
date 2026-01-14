# ===================================================================================================================
# Nombre del archivo : widget_label.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
import pygame
from .widget_base import WidgetBase

class LabelWidget(WidgetBase):
    def __init__(self, id, pos, texto, font=None, font_size=28, color_texto=(0, 0, 0), margin_scale=0.1):
        self.interactivo = False  # No es interactivo
        self.font_size = font_size
        self.font = font or pygame.font.SysFont("arial", font_size)
        self.texto = texto
        self.color_texto = color_texto
        self.margin = int(font_size * margin_scale)

        render = self.font.render(self.texto, True, self.color_texto)
        text_w, text_h = render.get_size()
        ancho_total = text_w + 2 * self.margin
        alto_total = text_h + 2 * self.margin

        super().__init__(id, pos, (ancho_total, alto_total))

    def draw(self, surface):
        if not hasattr(self, "rect") or self.rect.topleft is None:
            return  # No se ha posicionado aún

        area = pygame.Surface(self.size, pygame.SRCALPHA)
        area.fill((255, 255, 255, 0))  # Transparente

        render = self.font.render(self.texto, True, self.color_texto)
        text_rect = render.get_rect(topleft=(self.margin, self.margin))
        area.blit(render, text_rect)

        surface.blit(area, self.rect.topleft)

    def set_value(self, text):
        self.texto = text  # ❗ No se recalcula tamaño
        # Esto preserva la geometría asignada por layout

    def handle_event(self, event):
        pass

    def get_value(self):
        return self.texto

