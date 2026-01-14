# ===================================================================================================================
# Nombre del archivo : widget_input_text.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
import pygame
from .widget_base import WidgetBase

class InputTextWidget(WidgetBase):
    def __init__(self, id, pos, size, texto="", font=None, font_size=28, color_texto=(0, 0, 0), editable=True):
        self.texto = texto
        self.cursor_pos = len(texto)
        self.scroll_x = 0
        self.font_size = font_size
        self.font = font or pygame.font.SysFont("arial", font_size)
        self.color_texto = color_texto
        self.margin = font_size // 6  # margen superior reducido
        self.editable = editable

        super().__init__(id, pos, size)

        self.cursor_visible = True
        self.cursor_timer = 0

    def draw(self, surface):
        if self.pos is None:
            return  # Aún no se ha posicionado, no se puede dibujar

        area = pygame.Surface(self.size)
        area.fill((225, 225, 225))                                                  # Fondo externo gris claro
        pygame.draw.rect(area, (255,255,255), (0, 0, *self.size), border_radius=9)  # Fondo interno blanco   
        pygame.draw.rect(area, (0, 0, 0), (0, 0, *self.size), 2, border_radius=9)   # Borde negro

        render = self.font.render(self.texto, True, self.color_texto)

        cursor_x_px = self.font.size(self.texto[:self.cursor_pos])[0]

        visible_width = self.size[0] - 2 * self.margin
        if cursor_x_px - self.scroll_x > visible_width:
            self.scroll_x = cursor_x_px - visible_width + self.font.size(" ")[0]
        elif cursor_x_px - self.scroll_x < 0:
            self.scroll_x = max(0, cursor_x_px - self.font.size(" ")[0])

        area.blit(render, (self.margin - self.scroll_x, self.margin))

        if self.active and self.editable:
            self.cursor_timer += 1
            if self.cursor_timer >= 15:
                self.cursor_visible = not self.cursor_visible
                self.cursor_timer = 0

            if self.cursor_visible:
                cx = self.margin + cursor_x_px - self.scroll_x
                cy = self.margin
                h = self.font.get_height()
                pygame.draw.line(area, (0, 0, 0), (cx, cy), (cx, cy + h), 2)

        surface.blit(area, self.pos)

    def handle_event(self, event):
        if not self.editable:
            return

        delay, interval = pygame.key.get_repeat()
        if not self.active:
            if delay != 0:
                pygame.key.set_repeat(0)
            return
        if delay == 0:
            pygame.key.set_repeat(500, 100)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if self.cursor_pos > 0:
                    self.texto = self.texto[:self.cursor_pos - 1] + self.texto[self.cursor_pos:]
                    self.cursor_pos -= 1
            elif event.key == pygame.K_DELETE:
                if self.cursor_pos < len(self.texto):
                    self.texto = self.texto[:self.cursor_pos] + self.texto[self.cursor_pos + 1:]
            elif event.key == pygame.K_LEFT:
                if self.cursor_pos > 0:
                    self.cursor_pos -= 1
            elif event.key == pygame.K_RIGHT:
                if self.cursor_pos < len(self.texto):
                    self.cursor_pos += 1
            elif event.key == pygame.K_HOME:
                self.cursor_pos = 0
            elif event.key == pygame.K_END:
                self.cursor_pos = len(self.texto)
            elif event.key == pygame.K_RETURN:
                pass  # no hace nada en input de una línea
            elif event.key == pygame.K_TAB:
                pass  # manejado por formulario
            elif event.unicode:
                self.texto = self.texto[:self.cursor_pos] + event.unicode + self.texto[self.cursor_pos:]
                self.cursor_pos += 1

    def get_value(self):
        return self.texto

    def set_value(self, text: str):
        self.texto = text
        self.cursor_pos = len(text)
        self.scroll_x = 0
        if hasattr(self, "rect"):
            self.rect.size = self.size
