import win32api, win32con
import pyautogui
import random
import time

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

def movimiento_aleatorio_hasta_click(x_objetivo, y_objetivo, pasos=10):
    x_inicio, y_inicio = pyautogui.position()

    
    for _ in range(pasos):
        x_intermedio = random.randint(min(x_inicio, x_objetivo), max(x_inicio, x_objetivo))
        y_intermedio = random.randint(min(y_inicio, y_objetivo), max(y_inicio, y_objetivo))
        
      
        pyautogui.moveTo(x_intermedio, y_intermedio, duration=random.uniform(0.05, 0.2))
        time.sleep(random.uniform(0.05, 0.1))  

   
    pyautogui.moveTo(x_objetivo, y_objetivo, duration=random.uniform(0.1, 0.3))
    pyautogui.click()


