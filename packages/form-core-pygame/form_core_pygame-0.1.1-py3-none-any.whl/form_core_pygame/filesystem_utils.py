# ===================================================================================================================
# Nombre del archivo : filesystem_utils.py
# Nombre del proyecto: PyGameGUI
# Autor              : Antonio castro Snurmacher 
# Licencia           : GNU GPL v3 (https://www.gnu.org/licenses/gpl-3.0.html)
# Versión Python     : 3.x
# ===================================================================================================================
import os

def listar_directorio_filtrado(path, extensiones, incluir_directorio_padre=False):
    items = []

    if incluir_directorio_padre:
        items.append(('..', True))

    try:
        for nombre in sorted(os.listdir(path)):
            ruta = os.path.join(path, nombre)
            if os.path.isdir(ruta):
                items.append((nombre, True))
            elif os.path.isfile(ruta):
                if not extensiones:
                    items.append((nombre, False))
                else:
                    for ext in extensiones:
                        if nombre.lower().endswith(ext.lower()):
                            items.append((nombre, False))
                            break
    except Exception as e:
        print(f"[ERROR] No se pudo listar el directorio: {e}")

    return items
