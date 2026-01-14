# ===================================================================================================================
# Nombre del archivo : widget_radio_group.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
"""
Descripción:
    Widget de selección única con botones de tipo radio (vertical).
    Este módulo define la clase RadioGroupWidget, que permite mostrar un conjunto de opciones
    tipo "radio button", alineadas verticalmente. Solo una opción puede estar seleccionada
    a la vez. Cada botón se representa con un círculo, y la selección se refleja visualmente
    con un círculo interior. El widget es interactivo y usable dentro de formularios PyGameGUI.
"""

import pygame
from .widget_base import WidgetBase

class RadioGroupWidget(WidgetBase):
    def __init__(self, id, pos, opciones, font_size=24, spacing=10):
        font = pygame.font.SysFont("arial", font_size)
        self.opciones = opciones
        self.selected_index = None
        self.radio_radius = 12
        self.spacing = spacing
        self.font = font
        self.line_height = font_size + 8

        width = max(font.size(text)[0] for text in opciones) + 3 * self.radio_radius + 10
        height = len(opciones) * (self.line_height + spacing) - spacing

        super().__init__(id, pos, (width, height))
        self.interactivo = True

    def draw(self, surface):
        area = pygame.Surface(self.size, pygame.SRCALPHA)
        area.fill((255, 255, 255, 0))

        for idx, texto in enumerate(self.opciones):
            y = idx * (self.line_height + self.spacing)
            cx = self.radio_radius
            cy = y + self.line_height // 2
            pygame.draw.circle(area, (0, 0, 0), (cx, cy), self.radio_radius, 3)
            if self.selected_index == idx:
                pygame.draw.circle(area, (0, 0, 0), (cx, cy), self.radio_radius - 6)

            render = self.font.render(texto, True, (0, 0, 0))
            area.blit(render, (2 * self.radio_radius + 5, y))

        surface.blit(area, self.pos)

    def try_click(self, mouse_pos):
        if not self.rect.collidepoint(mouse_pos):
            return False

        rel_x = mouse_pos[0] - self.pos[0]
        rel_y = mouse_pos[1] - self.pos[1]

        for idx in range(len(self.opciones)):
            y = idx * (self.line_height + self.spacing)
            cy = y + self.line_height // 2
            cx = self.radio_radius
            dist = ((rel_x - cx)**2 + (rel_y - cy)**2) ** 0.5
            if dist <= self.radio_radius:
                self.selected_index = idx
                return True

        return False

    def get_value(self):
        if self.selected_index is not None:
            return self.opciones[self.selected_index]
        return None

    def set_value(self, value):
        if value in self.opciones:
            self.selected_index = self.opciones.index(value)

    def set_active(self, valor):
        self.activo = valor


