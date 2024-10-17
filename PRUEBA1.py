import random
import time
import csv
import os
import win32api, win32con
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException

output_file = "datos.csv"
data = ['NUMERO', 'OPERADOR', 'FECHA DE CONSULTA']

# Verificar si existe el archivo de salida datos.csv
if (os.path.isfile(output_file) == False):
    with open (output_file,'w') as file:
        writer = csv.writer(file)
        writer.writerow(data)
        file.close()


def click(x,y):
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

# Introducir el nombre del archivo, debe estar en formato .csv y estar en el mismo directorio que el script
filename = input("Escriba el nombre del archivo .csv a procesar: ")

PROXY = "101.255.166.241:8080"

# configuracion de opciones de chrome -----> aca cambias el usuario para abrir una sesion ya iniciada
chrome_options = Options()
chrome_options.add_argument('--proxy-server=%s' % PROXY)
chrome_options.add_argument("user-data-dir=C:\\Users\\Judah\\AppData\\Local\\Google\\Chrome\\User Data")
chrome_options.add_argument("profile-directory=Default")

# inicializar el driver de chrome
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# abrir la pagina
driver.get("https://numeracionyoperadores.cnmc.es/portabilidad/movil")

# esperar a que la pagina se cargue
WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "input-1")))

def ProcesarNumero(numero):
    campo_numero = driver.find_element(By.ID, "input-1")
    campo_numero.send_keys(numero)

    # esperar un momento para asegurarnos de que el campo esta listo
    time.sleep(2)

    # cambiar al iframe del recaptcha
    print("Esperando el iframe del recaptcha...")
    driver.switch_to.frame(driver.find_element(By.XPATH, "//iframe[contains(@src, 'recaptcha')]"))

    # esperar y hacer clic en el checkbox del recaptcha
    print("Iframe del recaptcha encontrado. Haciendo clic en el checkbox...")
    recaptcha_checkbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
    )
    recaptcha_checkbox.click()

    # volver al contexto principal
    driver.switch_to.default_content()

    # esperar a que aparezcan los botones de desafio
    print("Esperando los botones de desafío a que aparezcan...")

    # esperar un tiempo para ver los resultados
    time.sleep(5)

    # Hacer click en el boton de captcha
    click(393,938)
    time.sleep(20)

    try:
        driver.find_element(By.TAG_NAME, "button").click()
        time.sleep(5)
        # Rescatar información
        contenido = driver.find_element(By.CSS_SELECTOR, ".v-card").text
        lista = contenido.split("\n")

        card = driver.execute_script("return document.querySelector('.v-card').innerText")
        if card != "No se ha validado el código captcha":
            with open (output_file,'a') as file:
                writer = csv.writer(file)
                writer.writerow([lista[1], lista[3], lista[5]])
                file.close()
        
        campo_numero.click()
        campo_numero.send_keys(Keys.CONTROL + "a")
        campo_numero.send_keys(Keys.DELETE)
    except NoSuchElementException:
        print("El captcha no se puede resolver, reintente usando VPN o proxys")
        driver.refresh()
        time.sleep(5)
        return
    except ElementClickInterceptedException:
        print("El captcha no se puede resolver, reintente usando VPN o proxys")
        driver.refresh()
        time.sleep(5)
        return


def VerificarNumeroRepetido(numero):
    # Validar que el numero que se va a procesar no se encuentre ya procesado
    with open(output_file, 'r') as _filehandler:
        csv_file_reader = csv.DictReader(_filehandler)
        for row in csv_file_reader:
            if row['NUMERO'] == numero:
                return 1
    return 0

# Procesar el csv de entrada
with open(filename, newline='') as csvfile:
    spamreader = csv.reader(csvfile, delimiter=',')
    for row in spamreader:
        contador = driver.execute_script('return document.querySelector(".v-alert__content").innerText.match(/(\d+)/)[0]')
        print("Intentos disponibles: " + contador)
        if (row[0] != 'PHONE_NUMBER'):
            if VerificarNumeroRepetido(numero=row[0]) == 1:
                print("El numero: " + row[0] + " ya se encuentra validado")
                pass
            else:
                print("Procesando N. " + str(contador) + ": " + str(row[0]))
                ProcesarNumero(row[0])
            if (contador == 0 or contador == "0"):
                break

# cerrar el navegador se puede comentar para mantenerlo abierto
# driver.quit()  #lo comente para evitar cerrar el navegador