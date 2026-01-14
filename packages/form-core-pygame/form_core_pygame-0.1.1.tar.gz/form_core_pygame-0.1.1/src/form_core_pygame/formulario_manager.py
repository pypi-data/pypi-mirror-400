# ===================================================================================================================
# Nombre del archivo : formulario_manager.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================

#!/usr/bin/python3
"""
Fecha 29/Dec/2025 Última modificacion: Atajo configurable para modo debug de layout
Descripción: Permite activar/desactivar el renderizado de rectángulos de contenedores/widgets mediante
             una combinación de teclas configurable (0-1 tecla estándar, 0-2 modificadoras).
"""

import pygame
from .widget_base import WidgetBase


class FormularioManager:
    def __init__(self, surface, offset=(0, 0), debug=False, debug_keys=None):
        """
        Argumentos:
            surface (pygame.Surface): Superficie donde se dibujará el formulario.
            offset (tuple): Offset de coordenadas para formularios embebidos en subsuperficies.
            debug (bool): Si es True, activa el modo de depuración visual (bordes de contenedores/widgets).
            debug_keys (list|None): Atajo de teclado para alternar debug (opcional). Si es None, se usa el valor por defecto.
        """
        self.contenedores = []
        self.surface = surface
        self.offset = offset

        # Estado del modo debug (no debe modificarse en draw()).
        self.debug = bool(debug)

        # Configuración del atajo (por defecto F3).
        self._debug_main_key = None
        self._debug_required_mods = 0

        if debug_keys is None:
            self.set_debug_keys([pygame.K_F3]) # Valor por defecto para tecla de activación/desactivación del debug
        else:
            self.set_debug_keys(debug_keys)

    def set_debug_keys(self, set_keys):
        """
        Configura el atajo de teclado para alternar el modo debug.

        Reglas:
        - Lista vacía: deshabilita el atajo.
        - 0 o 1 tecla estándar (ej: pygame.K_F3).
        - 0, 1 o 2 modificadoras (Ctrl/Shift/Alt/Meta), en forma de teclas L/R.

        Parámetros:
            set_keys (list[int]): Lista de constantes pygame.K_*.

        Retorno:
            None

        Excepciones:
            ValueError: si hay más de 1 tecla estándar o más de 2 modificadoras distintas.
        """
        if not set_keys:
            self._debug_main_key = None
            self._debug_required_mods = 0
            return

        modifier_key_to_mask = {
            pygame.K_LCTRL: pygame.KMOD_CTRL,
            pygame.K_RCTRL: pygame.KMOD_CTRL,
            pygame.K_LSHIFT: pygame.KMOD_SHIFT,
            pygame.K_RSHIFT: pygame.KMOD_SHIFT,
            pygame.K_LALT: pygame.KMOD_ALT,
            pygame.K_RALT: pygame.KMOD_ALT,
            pygame.K_LMETA: pygame.KMOD_META,
            pygame.K_RMETA: pygame.KMOD_META,
        }

        required_mods = 0
        main_keys = []
        used_modifier_groups = set()

        for key in set_keys:
            if key in modifier_key_to_mask:
                mask = modifier_key_to_mask[key]
                required_mods |= mask
                used_modifier_groups.add(mask)
            else:
                main_keys.append(key)

        if len(main_keys) > 1:
            raise ValueError("Debug keys: solo se permite 0 o 1 tecla estándar (no modificadora).")

        if len(used_modifier_groups) > 2:
            raise ValueError("Debug keys: solo se permiten 0, 1 o 2 modificadoras distintas (CTRL/SHIFT/ALT/META).")

        if len(main_keys) == 0:
            raise ValueError("Debug keys: si hay modificadoras, debe existir también una tecla estándar.")

        self._debug_main_key = main_keys[0]
        self._debug_required_mods = required_mods

    # Alias “estilo API” si quieres exponerlo así en documentación.
    def SetDebugKey(self, set_keys):
        """Alias de compatibilidad: usa set_debug_keys()."""
        self.set_debug_keys(set_keys)

    def toggle_debug(self):
        """Alterna el modo debug (dibujar rectángulos de contenedores y widgets)."""
        self.debug = not self.debug

    def _is_debug_shortcut(self, event):
        """Comprueba si el evento KEYDOWN coincide con el atajo configurado."""
        if self._debug_main_key is None:
            return False

        if event.key != self._debug_main_key:
            return False

        # Requisito: que estén presentes los modificadores configurados (se permiten extras).
        if (event.mod & self._debug_required_mods) != self._debug_required_mods:
            return False

        return True

    def draw(self):
        self.surface.fill((225, 225, 225))  # Limpieza solo si NO es subsuperficie

        for contenedor in self.contenedores:
            if hasattr(contenedor, "set_debug"):
                contenedor.set_debug(self.debug, recursive=True)
            elif hasattr(contenedor, "debug"):
                contenedor.debug = self.debug
            contenedor.draw(self.surface)

        for widget in self.get_widgets():
            widget.draw(self.surface)
            if self.debug and hasattr(widget, "rect") and isinstance(widget.rect, pygame.Rect):
                pygame.draw.rect(self.surface, (255, 0, 0), widget.rect, width=2, border_radius=9)

        pygame.draw.rect(self.surface, (100, 100, 100), self.surface.get_rect(), width=2, border_radius=9)

    def handle_event(self, evento):
        # 1) Interceptar atajo debug lo antes posible, incluso si hay foco en un widget.
        if evento.type == pygame.KEYDOWN and self._is_debug_shortcut(evento):
            self.toggle_debug()
            return

        # 2) Resto de tu lógica (TAB, foco, etc.)
        if evento.type == pygame.MOUSEBUTTONDOWN:
            pos_relativa = (evento.pos[0] - self.offset[0], evento.pos[1] - self.offset[1])
            for widget in self.get_widgets():
                if widget.try_click(pos_relativa):
                    break

        elif evento.type == pygame.MOUSEBUTTONUP and evento.button == 1:
            for w in self.get_widgets():
                if hasattr(w, "scroll_repeat_direction"):
                    w.scroll_repeat_direction = None

        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_TAB:
                self._navegar_foco(shift=bool(evento.mod & pygame.KMOD_SHIFT))
                return

            widget_activo = WidgetBase.widget_con_foco()
            if widget_activo:
                widget_activo.handle_event(evento)

    def add_contenedor(self, contenedor):
        self.contenedores.append(contenedor)

    def get_widgets(self):
        widgets = []
        for cont in self.contenedores:
            widgets.extend(cont.get_widgets())
        return widgets

    def get_contenedores(self):
        return self.contenedores

    def tick_signal_handler(self):
        """Gestiona actualizaciones temporizadas (scroll, timers, etc.) de los widgets."""
        for w in self.get_widgets():
            if hasattr(w, "tick_handler"):
                w.tick_handler()

    def _navegar_foco(self, shift=False):
        interactivos = [w for w in self.get_widgets() if getattr(w, "interactivo", False)]
        if not interactivos:
            return

        actual = WidgetBase.widget_con_foco()
        idx = interactivos.index(actual) if actual in interactivos else -1
        nuevo_idx = (idx - 1 if shift else idx + 1) % len(interactivos)
        WidgetBase._set_foco(interactivos[nuevo_idx])

    def Test_Design_2D(self):
        resultado = {"colisiones": [], "overflow": [], "mal_definidos": []}

        def validar_elem(elementos, tipo_elementos):
            datos = []
            for elem in elementos:
                elem_id = getattr(elem, 'id', f"{elem.__class__.__name__}_{id(elem)}")

                if hasattr(elem, 'rect') and elem.rect:
                    rect = elem.rect
                elif isinstance(getattr(elem, 'pos', None), tuple) and isinstance(getattr(elem, 'size', None), tuple):
                    rect = pygame.Rect(elem.pos, elem.size)
                else:
                    resultado["mal_definidos"].append(elem_id)
                    continue

                datos.append((elem_id, rect))

            for i, (id1, r1) in enumerate(datos):
                for id2, r2 in datos[i+1:]:
                    if r1.colliderect(r2):
                        resultado["colisiones"].append((id1, id2))

            superficie_rect = pygame.Rect((0,0), self.surface.get_size())
            for elem_id, rect in datos:
                if not superficie_rect.contains(rect):
                    resultado["overflow"].append((elem_id, rect.bottomright))

            lineas = []
            if resultado["colisiones"]:
                lineas.append(f"* [Colisiones detectadas en {tipo_elementos}]")
                for id1, id2 in resultado["colisiones"]:
                    lineas.append(f" - {id1} <--> {id2}")

            if resultado["overflow"]:
                lineas.append(f"* [Overflow detectado en {tipo_elementos}]")
                for elem_id, pos in resultado["overflow"]:
                    lineas.append(f" - {elem_id} fuera de superficie en {pos}")

            if resultado["mal_definidos"]:
                lineas.append(f"* [Elementos con pos/size no definidos correctamente en {tipo_elementos}]")
                for elem_id in resultado["mal_definidos"]:
                    lineas.append(f" - {elem_id}")

            return "\n".join(lineas) if lineas else ""

        result = "\n ****** Chequeo del diseño 2D del formulario ******"
        result += "\n" + validar_elem(self.get_widgets(), "widgets")
        result += "\n" + validar_elem(self.get_contenedores(), "contenedores")
        return result.strip()

    def get_data(self):
        return {w.id: w.get_value() for w in self.get_widgets() if hasattr(w, "get_value")}

    def set_data(self, data_dict):
        for w in self.get_widgets():
            if w.id in data_dict and hasattr(w, "set_value"):
                w.set_value(data_dict[w.id])

    def clear(self):
        for w in self.get_widgets():
            if hasattr(w, "set_value"):
                w.set_value("")

    def disable_all(self):
        for w in self.get_widgets():
            w.set_active(False)
        WidgetBase.limpiar_foco()

    def enable_all(self):
        for w in self.get_widgets():
            w.set_active(False)
        WidgetBase.limpiar_foco()

    def set_foco_inicial(self):
        if not WidgetBase.widget_con_foco():
            for w in self.get_widgets():
                if hasattr(w, "handle_event"):
                    WidgetBase._set_foco(w)
                    break

    def get_help(self):
        return (
            "INSTRUCCIONES DEL FORMULARIO:\n"
            "----------------------------------------\n"
            "- Clic con el rat\u00f3n sobre un campo para activarlo.\n"
            "- Use TAB para pasar al siguiente campo.\n"
            "- Use SHIFT + TAB para retroceder al campo anterior.\n"
            "- Escriba normalmente en los campos activos.\n"
            "- Los campos de texto multilinea permiten saltos de l\u00ednea.\n"
            "- Pulse ESC para cancelar el campo activo (si aplica).\n"
            "- F3: activar/desactivar bordes de layout para contenedores y widgets (para debug de diseños).\n"
            "- Bot\u00f3n 'Mostrar resultado' imprime los datos en consola.\n"
            "- Bot\u00f3n 'Terminar' cierra la aplicaci\u00f3n.\n"
        )

