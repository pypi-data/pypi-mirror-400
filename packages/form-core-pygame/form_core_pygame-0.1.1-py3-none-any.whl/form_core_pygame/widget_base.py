#!/home/antonio/pyenv_goliat/bin/python
# La línea anterior permite ejecutar este programa con la versión de Pyton y el entorno virtual adecuados.
# ===================================================================================================================
# Nombre del archivo : widget_base.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================

"""
widget_base.py

Clase base común para todos los widgets del sistema de formularios.
Establece atributos y comportamientos estándar:
- Posición y tamaño
- Activación (foco)
- Dibujo
- Gestión centralizada del foco (solo un widget activo a la vez)
"""

import pygame


class WidgetBase:

    interactivo = True # Ojo solo interesa tenerlo a True en los widgets que tengan interactividad por teclado .
    foco_actual = None # Valor por defecto. 

    def __init__(self, id, pos, size):
        self.id = id
        self.size = size
        self.active = False
        self.pos = pos
        self.rect = pygame.Rect(pos or (0, 0), size)

    def draw(self, surface):
        """
        Debe ser implementado por cada widget.
        """
        raise NotImplementedError

    def handle_event(self, event):
        """
        Por defecto, los widgets no interactúan con eventos.
        Los widgets activos deben sobrescribir este método.
        """
        pass

    def get_value(self):
        """
        Retorna el valor actual del widget.
        """
        return None

    def set_value(self, valor):
        """
        Establece un nuevo valor en el widget.
        """
        pass

    def set_active(self, estado: bool):
        """
        Marca este widget como activo o inactivo.
        No modifica el foco global.
        """
        self.active = estado

    def is_inside(self, pos):
        """
        Verifica si una posición (x, y) está dentro del área del widget.
        """
        if self.pos is None:
            return False
        x, y = self.pos
        px, py = pos
        return x <= px <= x + self.size[0] and y <= py <= y + self.size[1]


    def try_click(self, pos):
        """
        Intenta activar el widget si se hace clic sobre él.
        """
        if self.is_inside(pos):
            WidgetBase._set_foco(self)
            return True
        return False

    def set_position(self, pos):
        """
        Establece una nueva posición del widget.
        """
        self.pos = pos
        if hasattr(self, "rect"):
            self.rect.topleft = pos

    # ------------- GESTIÓN CENTRAL DE FOCO ------------------

    @classmethod
    def _set_foco(cls, widget):
        """
        Asigna el foco exclusivamente a un único widget,
        evitando llamadas recursivas entre set_active() y _set_foco().
        """
        if cls.foco_actual is widget:
            return

        if cls.foco_actual:
            cls.foco_actual.active = False

        cls.foco_actual = widget
        widget.active = True  # Sin llamar a set_active()

    @classmethod
    def limpiar_foco(cls):
        """
        Elimina cualquier widget activo (foco nulo).
        """
        if cls.foco_actual:
            cls.foco_actual.active = False
        cls.foco_actual = None

    @classmethod
    def widget_con_foco(cls):
        """
        Devuelve el widget actualmente con foco, o None.
        """
        return cls.foco_actual

    @classmethod
    def establecer_foco_inicial(cls, widget):
        """
        Asigna el foco inicial al primer widget del formulario.
        """
        cls._set_foco(widget)

