# ===================================================================================================================
# Nombre del archivo : widget_text_area.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
import pygame
from .widget_base import WidgetBase

class TextAreaWidget(WidgetBase):
    def __init__(self, id, pos, size, texto_inicial="", font=None, font_size=28, color_texto=(0, 0, 0)):
        self.font_size = font_size
        self.font = font or pygame.font.SysFont("arial", font_size)
        self.color_texto = color_texto
        self.margin = font_size // 2
        self.line_spacing = int(font_size * 1.2)
        self.text_lines = texto_inicial.split("\n") if texto_inicial else [""]

        self.cursor_line = len(self.text_lines) - 1
        self.cursor_col = len(self.text_lines[-1])

        self.cursor_visible = True
        self.cursor_timer = 0
        self.scroll_x = 0
        self.scroll_y = 0

        self.scroll_speed = 10
        self.cursor_width = 2

        super().__init__(id, pos, size)

    def draw(self, surface):
        if self.pos is None:
            return  # Aún no se ha posicionado, no se puede dibujar

        area = pygame.Surface(self.size)
        area.fill((225, 225, 225))  # fondo externo gris claro
        pygame.draw.rect(area, (255, 255, 255), (0, 0, *self.size), border_radius=9) # fondo interno blanco
        pygame.draw.rect(area, (0, 0, 0), (0, 0, *self.size), 2, border_radius=9)

        start_y = self.margin - self.scroll_y
        for i, line in enumerate(self.text_lines):
            text_surf = self.font.render(line, True, self.color_texto)
            y_pos = start_y + i * self.line_spacing
            if -self.line_spacing <= y_pos <= self.size[1]:
                area.blit(text_surf, (self.margin - self.scroll_x, y_pos))

        if self.active and self.cursor_visible:
            cursor_x = self.font.size(self.text_lines[self.cursor_line][:self.cursor_col])[0]
            cx = self.margin + cursor_x - self.scroll_x
            cy = self.margin + self.cursor_line * self.line_spacing - self.scroll_y
            if 0 <= cy < self.size[1] and 0 <= cx < self.size[0]:
                pygame.draw.line(area, (0, 0, 0), (cx, cy), (cx, cy + self.font_size), self.cursor_width)

        surface.blit(area, self.pos)

        self.cursor_timer += 1
        if self.cursor_timer >= 15:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0

    def handle_event(self, event):
        delay, interval = pygame.key.get_repeat()
        if not self.active:
            if delay != 0:
                pygame.key.set_repeat(0)
            return
        if delay == 0:
            pygame.key.set_repeat(500, 100)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                line = self.text_lines[self.cursor_line]
                self.text_lines[self.cursor_line] = line[:self.cursor_col]
                self.text_lines.insert(self.cursor_line + 1, line[self.cursor_col:])
                self.cursor_line += 1
                self.cursor_col = 0

            elif event.key == pygame.K_BACKSPACE:
                if self.cursor_col > 0:
                    line = self.text_lines[self.cursor_line]
                    self.text_lines[self.cursor_line] = line[:self.cursor_col - 1] + line[self.cursor_col:]
                    self.cursor_col -= 1
                elif self.cursor_line > 0:
                    prev = self.text_lines[self.cursor_line - 1]
                    self.cursor_col = len(prev)
                    self.text_lines[self.cursor_line - 1] += self.text_lines[self.cursor_line]
                    del self.text_lines[self.cursor_line]
                    self.cursor_line -= 1

            elif event.key == pygame.K_DELETE:
                line = self.text_lines[self.cursor_line]
                if self.cursor_col < len(line):
                    self.text_lines[self.cursor_line] = line[:self.cursor_col] + line[self.cursor_col + 1:]
                elif self.cursor_line < len(self.text_lines) - 1:
                    self.text_lines[self.cursor_line] += self.text_lines[self.cursor_line + 1]
                    del self.text_lines[self.cursor_line + 1]

            elif event.key == pygame.K_LEFT:
                if self.cursor_col > 0:
                    self.cursor_col -= 1
                elif self.cursor_line > 0:
                    self.cursor_line -= 1
                    self.cursor_col = len(self.text_lines[self.cursor_line])

            elif event.key == pygame.K_RIGHT:
                if self.cursor_col < len(self.text_lines[self.cursor_line]):
                    self.cursor_col += 1
                elif self.cursor_line < len(self.text_lines) - 1:
                    self.cursor_line += 1
                    self.cursor_col = 0

            elif event.key == pygame.K_UP:
                if self.cursor_line > 0:
                    self.cursor_line -= 1
                    self.cursor_col = min(self.cursor_col, len(self.text_lines[self.cursor_line]))

            elif event.key == pygame.K_DOWN:
                if self.cursor_line < len(self.text_lines) - 1:
                    self.cursor_line += 1
                    self.cursor_col = min(self.cursor_col, len(self.text_lines[self.cursor_line]))

            elif event.key == pygame.K_HOME:
                self.cursor_col = 0

            elif event.key == pygame.K_END:
                self.cursor_col = len(self.text_lines[self.cursor_line])

            elif event.key == pygame.K_ESCAPE:
                self.set_active(False)

            else:
                if event.unicode and event.unicode.isprintable():
                    line = self.text_lines[self.cursor_line]
                    self.text_lines[self.cursor_line] = line[:self.cursor_col] + event.unicode + line[self.cursor_col:]
                    self.cursor_col += 1

            self._ajustar_scroll()

    def _ajustar_scroll(self):
        cursor_x_px = self.font.size(self.text_lines[self.cursor_line][:self.cursor_col])[0]
        cursor_y_px = self.cursor_line * self.line_spacing

        visible_w, visible_h = self.size
        margin = self.margin

        umbral_x = self.font.size("W")[0]  # ancho típico de carácter
        umbral_y = self.line_spacing        # alto de una línea

        if cursor_x_px + margin > self.scroll_x + visible_w - umbral_x:
            self.scroll_x = cursor_x_px + margin - (visible_w - umbral_x)
        elif cursor_x_px < self.scroll_x + margin:
            self.scroll_x = max(0, cursor_x_px - margin)

        if cursor_y_px + margin > self.scroll_y + visible_h - umbral_y:
            self.scroll_y = cursor_y_px + margin - (visible_h - umbral_y)
        elif cursor_y_px < self.scroll_y + margin:
            self.scroll_y = max(0, cursor_y_px - margin)

    def get_value(self):
        return "\n".join(self.text_lines)

    def set_value(self, text):
        self.text_lines = text.split("\n")
        self.cursor_line = len(self.text_lines) - 1
        self.cursor_col = len(self.text_lines[-1])
        self.scroll_x = 0
        self.scroll_y = 0

