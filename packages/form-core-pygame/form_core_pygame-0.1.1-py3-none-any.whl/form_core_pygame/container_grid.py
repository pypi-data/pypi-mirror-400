# ===================================================================================================================
# Nombre del archivo : container_grid.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
import pygame
from .container_base import ContainerBase

class ContainerGrid(ContainerBase):
    def __init__(self, nfilas, ncolumnas, pos=(0, 0), margen_h=10, margen_v=10):
        super().__init__(pos)
        self.nfilas = nfilas
        self.ncolumnas = ncolumnas
        self.margen_h = margen_h
        self.margen_v = margen_v
        self.celdas = [[None for _ in range(ncolumnas)] for _ in range(nfilas)]
        self.ancho_columnas = [0] * ncolumnas
        self.alto_filas = [0] * nfilas
        self.min_ancho_columnas = [0] * ncolumnas
        self.min_alto_filas = [0] * nfilas
        self.children = []

        # Debug de grid: bordes de celdas (y posibilidad de propagar a hijos)
        self.debug = False

    def set_debug(self, enabled, recursive=True):
        """
        Activa/desactiva depuración visual del grid.
        Si recursive=True, intenta propagar a hijos que soporten debug.
        """
        self.debug = bool(enabled)

        if not recursive:
            return

        for child in self.children:
            if hasattr(child, "set_debug"):
                child.set_debug(enabled, recursive=True)
            elif hasattr(child, "debug"):
                child.debug = bool(enabled)

    def set_min_column_widths(self, widths):
        if len(widths) != self.ncolumnas:
            raise ValueError(f"Se esperaban {self.ncolumnas} anchos mínimos")
        self.min_ancho_columnas = widths

    def set_min_row_heights(self, heights):
        if len(heights) != self.nfilas:
            raise ValueError(f"Se esperaban {self.nfilas} alturas mínimas")
        self.min_alto_filas = heights

    def add(self, fila, columna, elemento, align='top_left'):
        if not hasattr(elemento, 'size') or elemento.size is None:
            raise ValueError(f"El elemento en ({fila},{columna}) no tiene definido .size")

        if not (0 <= fila < self.nfilas and 0 <= columna < self.ncolumnas):
            raise IndexError("Índice fuera del rango del grid")

        if hasattr(elemento, 'layout'):
            elemento.layout()

        self.celdas[fila][columna] = (elemento, align)
        if elemento not in self.children:
            self.children.append(elemento)
        self.layout()

    def set_position(self, pos):
        super().set_position(pos)
        self.layout()

    def layout(self):
        # Calcular dimensiones máximas por columna y fila (respetando mínimos)
        for col in range(self.ncolumnas):
            max_w = self.min_ancho_columnas[col]
            for fila in range(self.nfilas):
                celda = self.celdas[fila][col]
                if celda:
                    elem, _ = celda if isinstance(celda, tuple) else (celda, 'top_left')
                    if elem.size:
                        max_w = max(max_w, elem.size[0])
            self.ancho_columnas[col] = max_w

        for fila in range(self.nfilas):
            max_h = self.min_alto_filas[fila]
            for col in range(self.ncolumnas):
                celda = self.celdas[fila][col]
                if celda:
                    elem, _ = celda if isinstance(celda, tuple) else (celda, 'top_left')
                    if elem.size:
                        max_h = max(max_h, elem.size[1])
            self.alto_filas[fila] = max_h

        alineaciones_validas = {
            "top_left", "top_center", "top_right",
            "middle_left", "center", "middle_right",
            "bottom_left", "bottom_center", "bottom_right"
        }

        # Posicionar elementos
        x0, y0 = self.pos
        for fila in range(self.nfilas):
            for col in range(self.ncolumnas):
                celda = self.celdas[fila][col]
                if celda:
                    elem, align = celda if isinstance(celda, tuple) else (celda, 'top_left')

                    if align not in alineaciones_validas:
                        raise ValueError(
                            f"Alineación no válida: '{align}'\n"
                            f"Debe ser una de las siguientes:\n\n"
                            f"  top_left     top_center     top_right\n"
                            f"  middle_left  center         middle_right\n"
                            f"  bottom_left  bottom_center  bottom_right\n"
                        )

                    w, h = elem.size
                    cell_w = self.ancho_columnas[col]
                    cell_h = self.alto_filas[fila]

                    x = x0 + sum(self.ancho_columnas[:col]) + col * self.margen_h
                    y = y0 + sum(self.alto_filas[:fila]) + fila * self.margen_v

                    offset_x = (
                        0 if "left" in align else
                        (cell_w - w) // 2 if "center" in align else
                        (cell_w - w)
                    )

                    offset_y = (
                        0 if "top" in align else
                        (cell_h - h) // 2 if "middle" in align or align == "center" else
                        (cell_h - h)
                    )

                    elem.set_position((x + offset_x, y + offset_y))

        total_w = sum(self.ancho_columnas) + (self.ncolumnas - 1) * self.margen_h
        total_h = sum(self.alto_filas) + (self.nfilas - 1) * self.margen_v
        self.set_size((total_w, total_h))

    def draw(self, surface):
        for elem in self.children:
            elem.draw(surface)

        # Dibujar bordes de celdas solo si debug está activo
        if not self.debug:
            return
        
        # Dibujar bordes de celdas para depuración
        x0, y0 = self.pos
        for fila in range(self.nfilas):
            for col in range(self.ncolumnas):
                x = x0 + sum(self.ancho_columnas[:col]) + col * self.margen_h
                y = y0 + sum(self.alto_filas[:fila]) + fila * self.margen_v
                w = self.ancho_columnas[col]
                h = self.alto_filas[fila]
                pygame.draw.rect(surface, (0, 0, 255), (x, y, w, h), width=2, border_radius=9)
        

    def handle_event(self, event):
        super().handle_event(event)

    def get_widgets(self):
        widgets = []
        for fila in self.celdas:
            for celda in fila:
                if celda:
                    elem, _ = celda if isinstance(celda, tuple) else (celda, 'top_left')
                    if hasattr(elem, 'get_widgets'):
                        widgets.extend(elem.get_widgets())
                    else:
                        widgets.append(elem)
        return widgets
