# ===================================================================================================================
# Nombre del archivo : widget_checkbox.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
"""
Descripción:
    Widget tipo checkbox con texto descriptivo.
    Hereda de WidgetBase para integrarse en formularios.
"""

import pygame
from .widget_base import WidgetBase

class CheckboxWidget(WidgetBase):
    def __init__(
        self, id, pos, texto="Checkbox", marcado=False,
        font=None, font_size=28, color_texto=(0, 0, 0)
    ):
        self.interactivo = False
        self.texto = texto
        self.marcado = marcado
        self.font = font or pygame.font.SysFont("arial", font_size)
        self.color_texto = color_texto
        self.checkbox_size = font_size

        # Precalcular tamaño
        texto_render = self.font.render(self.texto, True, self.color_texto)
        texto_w, texto_h = texto_render.get_size()
        ancho_total = self.checkbox_size + 10 + texto_w
        alto_total = max(self.checkbox_size, texto_h)

        super().__init__(id, pos, (ancho_total, alto_total))

    def draw(self, surface):
        if self.pos is None:
            return  # Aún no se ha posicionado, no se puede dibujar

        x, y = self.pos
        w, h = self.size
        cx, cy = x, y + (h - self.checkbox_size) // 2

        # Dibujar caja
        pygame.draw.rect(surface, (255,255,255), (cx, cy, self.checkbox_size, self.checkbox_size), border_radius=7)
        pygame.draw.rect(surface, (0, 0, 0), (cx, cy, self.checkbox_size, self.checkbox_size), 2, border_radius=7)

        # Dibujar marca si está marcado
        if self.marcado:
            margen = 4
            pygame.draw.line(surface, (0, 0, 0), (cx + margen, cy + margen),
                             (cx + self.checkbox_size - margen, cy + self.checkbox_size - margen), 4)
            pygame.draw.line(surface, (0, 0, 0), (cx + margen, cy + self.checkbox_size - margen),
                             (cx + self.checkbox_size - margen, cy + margen), 4)

        # Dibujar texto
        texto_render = self.font.render(self.texto, True, self.color_texto)
        surface.blit(texto_render, (cx + self.checkbox_size + 10, y + (h - texto_render.get_height()) // 2))

    def handle_event(self, event):
        pass  # No hace falta nada aquí por ahora

    def try_click(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            WidgetBase._set_foco(self)
            self.marcado = not self.marcado
            return True
        return False

    def get_value(self):
        return self.marcado

    def set_value(self, estado: bool):
        self.marcado = estado

