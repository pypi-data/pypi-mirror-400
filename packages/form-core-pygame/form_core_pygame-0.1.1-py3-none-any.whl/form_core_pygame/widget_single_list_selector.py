# ===================================================================================================================
# Nombre del archivo : widget_single_list_selector.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
"""
Descripción:
    Widget para seleccionar un único ítem de una lista con scroll vertical.
    Este módulo define la clase WidgetSingleListSelector, que permite mostrar una lista de opciones
    desplazables verticalmente mediante botones de scroll. El usuario puede seleccionar un único elemento
    con un clic. El widget gestiona el dibujo del contenido visible, el scroll con autorepeat y el resaltado
    del ítem seleccionado. Se integra fácilmente en un sistema de formularios basado en 
"""

import pygame
from .widget_base import WidgetBase

class WidgetSingleListSelector(WidgetBase):
    """
    Selector de lista que permite una única selección.
    Scroll vertical con botones ↑ ↓ de autorepeat.
    """
    def __init__(self, id, pos, size, opciones):
        super().__init__(id, pos, size)
        self.opciones = opciones
        self.scroll_offset = 0
        self.line_height = 30
        self.font = pygame.font.SysFont("arial", 24)
        self.scroll_btn_height = 30
        self.scroll_bar_width = 25
        self.scroll_repeat_direction = None
        self.scroll_repeat_start_time = 0
        self.scroll_repeat_last_time = 0
        self.scroll_repeat_delay = 400
        self.scroll_repeat_interval = 100
        self.interactivo = True
        self.selected_index = None

    def get_scroll_button_rects(self):
        up = pygame.Rect(self.size[0] - self.scroll_bar_width, 0,
                         self.scroll_bar_width, self.scroll_btn_height)
        down = pygame.Rect(self.size[0] - self.scroll_bar_width,
                           self.size[1] - self.scroll_btn_height,
                           self.scroll_bar_width, self.scroll_btn_height)
        return up, down

    def draw(self, surface):
        area = pygame.Surface(self.size)
        area.fill((230, 230, 230))

        visible_lines = (self.size[1] - self.scroll_btn_height * 2) // self.line_height
        inicio = self.scroll_offset
        fin = min(len(self.opciones), inicio + visible_lines)

        for idx in range(inicio, fin):
            y_offset = self.scroll_btn_height + (idx - inicio) * self.line_height
            self.draw_line(area, idx, y_offset)

        up_rect, down_rect = self.get_scroll_button_rects()
        pygame.draw.rect(area, (180, 180, 180), up_rect)
        pygame.draw.rect(area, (180, 180, 180), down_rect)

        cx_up, cy_up = up_rect.center
        pygame.draw.polygon(area, (0,0,0), [(cx_up, cy_up - 5), (cx_up - 6, cy_up + 4), (cx_up + 6, cy_up + 4)])
        cx_dn, cy_dn = down_rect.center
        pygame.draw.polygon(area, (0,0,0), [(cx_dn, cy_dn + 5), (cx_dn - 6, cy_dn - 4), (cx_dn + 6, cy_dn - 4)])

        surface.blit(area, self.pos)

    def draw_line(self, surface, idx, y_offset):
        texto = self.opciones[idx]
        color_bg = (200, 200, 100) if idx == self.selected_index else (255, 255, 255)
        pygame.draw.rect(surface, color_bg,
                         (0, y_offset, self.size[0] - self.scroll_bar_width, self.line_height))
        render = self.font.render(texto, True, (0, 0, 0))
        surface.blit(render, (5, y_offset + 5))

    def try_click(self, mouse_pos):
        if not self.rect.collidepoint(mouse_pos):
            return False
        mx, my = mouse_pos[0] - self.pos[0], mouse_pos[1] - self.pos[1]
        up_rect, dn_rect = self.get_scroll_button_rects()
        now = pygame.time.get_ticks()

        if up_rect.collidepoint((mx, my)):
            self.scroll_up()
            self.scroll_repeat_direction, self.scroll_repeat_start_time, self.scroll_repeat_last_time = ("up", now, now)
            return True
        if dn_rect.collidepoint((mx, my)):
            self.scroll_down()
            self.scroll_repeat_direction, self.scroll_repeat_start_time, self.scroll_repeat_last_time = ("down", now, now)
            return True

        if my < self.scroll_btn_height or my >= self.size[1] - self.scroll_btn_height:
            return False

        idx_rel = (my - self.scroll_btn_height) // self.line_height
        idx_abs = self.scroll_offset + idx_rel
        if 0 <= idx_abs < len(self.opciones):
            self.on_select(idx_abs)
            return True
        return False

    def on_select(self, idx):
        self.selected_index = idx

    def tick_handler(self):
        if not self.scroll_repeat_direction:
            return
        now = pygame.time.get_ticks()
        if now - self.scroll_repeat_start_time >= self.scroll_repeat_delay:
            if now - self.scroll_repeat_last_time >= self.scroll_repeat_interval:
                if self.scroll_repeat_direction == "up":
                    self.scroll_up()
                else:
                    self.scroll_down()
                self.scroll_repeat_last_time = now

    def scroll_up(self):
        if self.scroll_offset > 0:
            self.scroll_offset -= 1

    def scroll_down(self):
        lines = (self.size[1] - self.scroll_btn_height * 2) // self.line_height
        if self.scroll_offset + lines < len(self.opciones):
            self.scroll_offset += 1

    def get_value(self):
        return self.opciones[self.selected_index] if self.selected_index is not None else None

