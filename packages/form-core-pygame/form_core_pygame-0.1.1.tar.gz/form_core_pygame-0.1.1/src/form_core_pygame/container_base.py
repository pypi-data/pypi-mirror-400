# ===================================================================================================================
# Nombre del archivo : container_base.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
import pygame

class ContainerBase:
    def __init__(self, pos=None, size=None):
        """
        Contenedor base para cualquier tipo de layout.
        Los hijos pueden ser widgets o sub-contenedores.
        """
        self.pos = pos or (0, 0)
        if size is None or size == (0, 0):
            self.size = pygame.display.get_surface().get_size()
        else:
            self.size = size

        self.rect = pygame.Rect(self.pos, self.size)
        self.children = []

    def set_position(self, pos):
        self.pos = pos
        self.rect.topleft = pos

    def set_size(self, size):
        self.size = size
        self.rect.size = size

    def add(self, widget_or_widgets):
        """
        Añadir un widget o una lista de widgets.
        """
        if isinstance(widget_or_widgets, list):
            self.children.extend(widget_or_widgets)
        else:
            self.children.append(widget_or_widgets)

    def handle_event(self, event):
        for child in self.children:
            if hasattr(child, "handle_event"):
                child.handle_event(event)

    def get_widgets(self):
        """
        Devuelve una lista plana de widgets, incluso si hay sub-contenedores.
        """
        result = []
        for child in self.children:
            if hasattr(child, "get_widgets"):
                result.extend(child.get_widgets())
            else:
                result.append(child)
        return result

    def layout(self, x, y, width, height):
        """
        Método abstracto: cada tipo de contenedor debe implementar su distribución.
        """
        raise NotImplementedError("Cada contenedor debe implementar layout()")

