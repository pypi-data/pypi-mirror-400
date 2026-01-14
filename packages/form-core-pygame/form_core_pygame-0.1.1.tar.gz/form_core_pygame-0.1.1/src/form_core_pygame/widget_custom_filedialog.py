# ===================================================================================================================
# Nombre del archivo : widget_custom_filedialog.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
import os
import pygame
from .widget_base import WidgetBase
from .filesystem_utils import listar_directorio_filtrado

class CustomFileDialogWidget(WidgetBase):
    def __init__(self, id, pos, size, initialdir='.', allowed_extensions=None):
        super().__init__(id, pos, size)
        self.interactivo = True
        self.allowed_extensions = allowed_extensions or []
        self.initialdir = os.path.abspath(initialdir)
        self.current_dir = self.initialdir
        self.items = []
        self.selected_path = None
        self.scroll_offset = 0
        self.line_height = 30
        self.font = pygame.font.SysFont("arial", 24)
        self.scroll_btn_height = 30
        self.scroll_bar_width = 25
        self.scroll_repeat_direction = None  # "up" o "down"
        self.scroll_repeat_start_time = 0
        self.scroll_repeat_last_time = 0
        self.scroll_repeat_delay = 400       # ms antes de repetir
        self.scroll_repeat_interval = 100    # ms entre pasos repetidos
        self.scroll_repeat_direction = None  # "up" o "down"
        self.scroll_repeat_start_time = 0
        self.scroll_repeat_last_time = 0
        self.scroll_repeat_delay = 400       # ms antes del primer repeat
        self.scroll_repeat_interval = 100    # ms entre repeticiones
        self.refresh()

    def refresh(self):
        self.items = listar_directorio_filtrado(
            self.current_dir,
            self.allowed_extensions,
            incluir_directorio_padre=(self.current_dir != self.initialdir)
        )
        self.selected_path = None
        self.scroll_offset = 0

    def get_scroll_button_rects(self):
        up = pygame.Rect(
            self.size[0] - self.scroll_bar_width, self.line_height,
            self.scroll_bar_width, self.scroll_btn_height)
        down = pygame.Rect(
            self.size[0] - self.scroll_bar_width,
            self.size[1] - self.scroll_btn_height,
            self.scroll_bar_width, self.scroll_btn_height)
        return up, down

    def tick_handler(self):
        if not self.scroll_repeat_direction:
            return

        now = pygame.time.get_ticks()
        if now - self.scroll_repeat_start_time >= self.scroll_repeat_delay:
            if now - self.scroll_repeat_last_time >= self.scroll_repeat_interval:
                espacio_listado = self.size[1] - self.line_height - self.scroll_btn_height * 2
                visible_lines = espacio_listado // self.line_height
                max_offset = max(0, len(self.items) - visible_lines)

                if self.scroll_repeat_direction == "up":
                    if self.scroll_offset > 0:
                        self.scroll_offset -= 1
                elif self.scroll_repeat_direction == "down":
                    if self.scroll_offset < max_offset:
                        self.scroll_offset += 1

                self.scroll_repeat_last_time = now

    def draw(self, surface):
        area = pygame.Surface(self.size)
        area.fill((230, 230, 230))

        # Cabecera
        header_color = (122, 0, 0)
        header_font = pygame.font.SysFont("arial", 24, bold=True)
        if self.selected_path:
            header_text = f"Seleccionado: {os.path.basename(self.selected_path)}"
        else:
            header_text = "Selección de fichero"


        # Render del texto
        header_render = header_font.render(header_text, True, header_color)

        header_x = (self.size[0] - header_render.get_width()) // 2
        header_x = max(5, header_x)  # evita X negativa si el texto es largo

        area.blit(header_render, (header_x, 5))

        # Área de listado
        espacio_listado = self.size[1] - self.line_height  # self.line_height es cabecera
        visible_lines = (espacio_listado // self.line_height) - 1  # Quitamos 1 línea

        inicio = self.scroll_offset
        fin = min(len(self.items), inicio + visible_lines)

        for idx in range(inicio, fin):
            nombre, es_dir = self.items[idx]
            color = (0, 0, 255) if es_dir else (0, 0, 0)
            y_offset = self.line_height + (idx - inicio) * self.line_height + self.scroll_btn_height

            if self.selected_path and os.path.basename(self.selected_path) == nombre:
                pygame.draw.rect(area, (200, 200, 100),
                                 (0, y_offset, self.size[0] - self.scroll_bar_width, self.line_height))

            render = self.font.render(nombre, True, color)
            area.blit(render, (5, y_offset))

        # Botones de scroll
        up_button_rect, down_button_rect = self.get_scroll_button_rects()
        pygame.draw.rect(area, (180, 180, 180), up_button_rect)
        pygame.draw.rect(area, (180, 180, 180), down_button_rect)

        # Flechas
        cx_up, cy_up = up_button_rect.center
        pygame.draw.polygon(area, (0, 0, 0), [(cx_up, cy_up - 5), (cx_up - 6, cy_up + 4), (cx_up + 6, cy_up + 4)])
        cx_down, cy_down = down_button_rect.center
        pygame.draw.polygon(area, (0, 0, 0), [(cx_down, cy_down + 5), (cx_down - 6, cy_down - 4), (cx_down + 6, cy_down - 4)])

        surface.blit(area, self.pos)

    def try_click(self, mouse_pos):
        if not self.rect.collidepoint(mouse_pos):
            return False

        rel_x = mouse_pos[0] - self.pos[0]
        rel_y = mouse_pos[1] - self.pos[1]

        up_button_rect, down_button_rect = self.get_scroll_button_rects()
        now = pygame.time.get_ticks()

        if up_button_rect.collidepoint((rel_x, rel_y)):
            self.scroll_offset = max(0, self.scroll_offset - 1)
            self.scroll_repeat_direction = "up"
            self.scroll_repeat_start_time = now
            self.scroll_repeat_last_time = now
            return True

        if down_button_rect.collidepoint((rel_x, rel_y)):
            espacio_listado = self.size[1] - self.line_height - self.scroll_btn_height * 2
            visible_lines = espacio_listado // self.line_height
            if self.scroll_offset + visible_lines < len(self.items):
                self.scroll_offset += 1
            self.scroll_repeat_direction = "down"
            self.scroll_repeat_start_time = now
            self.scroll_repeat_last_time = now
            return True

        if rel_x > self.size[0] - self.scroll_bar_width:
            return False

        if rel_y < self.line_height + self.scroll_btn_height:
            return False

        rel_y_adjusted = rel_y - self.line_height - self.scroll_btn_height
        idx_rel = rel_y_adjusted // self.line_height
        idx_abs = self.scroll_offset + idx_rel

        if 0 <= idx_abs < len(self.items):
            nombre, es_dir = self.items[idx_abs]
            path = os.path.join(self.current_dir, nombre)
            if es_dir:
                self.current_dir = os.path.abspath(path)
                self.refresh()
            else:
                self.selected_path = os.path.abspath(path)
        return True

    def update(self):
        if not self.scroll_repeat_direction:
            return

        now = pygame.time.get_ticks()
        delay = self.scroll_repeat_delay
        interval = self.scroll_repeat_interval

        if now - self.scroll_repeat_start_time >= delay:
            if now - self.scroll_repeat_last_time >= interval:
                espacio_listado = self.size[1] - self.line_height - self.scroll_btn_height * 2
                visible_lines = espacio_listado // self.line_height
                max_offset = max(0, len(self.items) - visible_lines)

                if self.scroll_repeat_direction == "up":
                    if self.scroll_offset > 0:
                        self.scroll_offset -= 1
                elif self.scroll_repeat_direction == "down":
                    if self.scroll_offset < max_offset:
                        self.scroll_offset += 1

                self.scroll_repeat_last_time = now

    def get_value(self):
        return self.selected_path

