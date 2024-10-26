import win32api, win32con

# Funcion para controlar la posicion del mouse y hacer click
def click(x,y):
    x = int(x)
    y = int(y)
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

# Obtener numero de lineas de un archivo
def numeroLineas(filename: str) -> int:
    with open(filename) as f:
        return sum(1 for _ in f)