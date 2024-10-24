import csv
import os
import time
import keyboard
import urllib.request, json 
import win32api, win32con
from dotenv import load_dotenv
from seleniumwire import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ActionChains
from selenium_authenticated_proxy import SeleniumAuthenticatedProxy

# Cargar las variable de entorno
load_dotenv()
USER_DIR : str = os.getenv("USER_DIR")

# Nombre del archivo de salida
output_file : str = "datos.csv"

# Encabezados para el archvo de salida
data : list[str] = ['NUMERO', 'OPERADOR', 'FECHA DE CONSULTA']

# Verificar si existe el archivo de salida datos.csv
if (os.path.isfile(output_file) == False):
    with open (output_file,'w') as file:
        writer = csv.writer(file)
        writer.writerow(data)
        file.close()

# Funcion para controlar la posicion del mouse y hacer click
def click(x,y):
    x = int(x)
    y = int(y)
    win32api.SetCursorPos((x,y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN,x,y,0,0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP,x,y,0,0)

# Introducir el nombre del archivo, debe estar en formato .csv y estar en el mismo directorio que el script
filename : str = input("Escriba el nombre del archivo .csv a procesar: ")

# Clase inicial del proyecto
class EjecutarScript():
    def __init__(self, filename: str) -> None:
        print(" Iniciando programa")
        self.filename : str = filename
    def AbrirNavegador(self, PROXY: str):
        # configuracion de opciones de chrome -----> aca cambias el usuario para abrir una sesion ya iniciada
        chrome_options = Options()
        if (PROXY == "local"):
            chrome_options.add_argument("user-data-dir=" + USER_DIR)
            chrome_options.add_argument("profile-directory=Default")
    
            # inicializar el driver de chrome
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        else:

            proxy_username = "2bdd8ef305f5ccb8443a"
            proxy_password = "828ce4751e15c0db"
            proxy_address = "gw.dataimpulse.com"
            proxy_port = "823"
            proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}"

            # Configure Proxy Option
            print(" configurando proxy")
            chrome_options.add_argument("user-data-dir=" + USER_DIR)
            chrome_options.add_argument("profile-directory=Default")
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-certificate-errors-spki-list')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.set_capability('acceptInsecureCerts', "True")

            proxy_helper = SeleniumAuthenticatedProxy(proxy_url=proxy_url)
            proxy_helper.enrich_chrome_options(chrome_options)

            # inicializar el driver de chrome
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options,)

        # abrir la pagina
        self.driver.get("https://numeracionyoperadores.cnmc.es/portabilidad/movil")
        time.sleep(5)
        keyboard.press_and_release('enter')
        keyboard.press_and_release('enter')

        # esperar a que la pagina se cargue
        WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "input-1")))

        # Procesar el csv de entrada
        with open(filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            intentos_fallidos = 0
            for row in spamreader:
                contador = self.driver.execute_script('return document.querySelector(".v-alert__content").innerText.match(/(\d+)/)[0]')
                # print("Intentos disponibles: " + contador)
                if (row[0] != 'PHONE_NUMBER'):
                    if self.VerificarNumeroRepetido(numero=row[0]) == 1:
                        pass
                    else:

                        print("Procesando N. " + str(contador) + ": " + str(row[0]))
                        respuesta = self.ProcesarNumero(row[0])
                        if respuesta == "FAILED" :
                            intentos_fallidos = intentos_fallidos + 1
                            print("Intentos fallidos: " + str(intentos_fallidos))
                        if  intentos_fallidos >= 1:
                            self.driver.quit()
                            break
                    if (contador == 0 or contador == "0" or intentos_fallidos >= 10):
                        self.driver.quit()
                        break
    
    def ProcesarNumero(self, numero) -> str:
        campo_numero = self.driver.find_element(By.ID, "input-1")
        campo_numero.send_keys(numero)

        # esperar un momento para asegurarnos de que el campo esta listo
        time.sleep(2)

        # cambiar al iframe del recaptcha
        self.driver.switch_to.frame(self.driver.find_element(By.XPATH, "//iframe[contains(@src, 'recaptcha')]"))

        # esperar y hacer clic en el checkbox del recaptcha
        try:
            recaptcha_checkbox = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.ID, "recaptcha-anchor"))
            )
            recaptcha_checkbox.click()
        except TimeoutException:
            print("El elemento no se ha encontrado")
            self.driver.refresh()
            time.sleep(5)
            return "FAILED"

        # volver al contexto principal
        self.driver.switch_to.default_content()

        # esperar un tiempo para ver los resultados
        time.sleep(5)
        # Hacer click en el boton de captcha
        click(os.getenv("CAPTCHA_X"),os.getenv("CAPTCHA_Y"))
        time.sleep(20)

        try:
            self.driver.find_element(By.TAG_NAME, "button").click()
            time.sleep(5)
            # Rescatar información
            contenido = self.driver.find_element(By.CSS_SELECTOR, ".v-card").text
            lista = contenido.split("\n")

            card = self.driver.execute_script("return document.querySelector('.v-card').innerText")
            if card != "No se ha validado el código captcha":
                with open (output_file,'a') as file:
                    writer = csv.writer(file)
                    writer.writerow([lista[1], lista[3], lista[5]])
                    file.close()
            
            campo_numero.click()
            campo_numero.send_keys(Keys.CONTROL + "a")
            campo_numero.send_keys(Keys.DELETE)
            return "SUCCESS"
        
        except NoSuchElementException:
            print("El captcha no se puede resolver, reintente usando VPN o proxys")
            self.driver.refresh()
            time.sleep(5)
            return "FAILED"
        except ElementClickInterceptedException:
            print("El captcha no se puede resolver, reintente usando VPN o proxys")
            self.driver.refresh()
            time.sleep(5)
            return "FAILED"

        
    def VerificarNumeroRepetido(self, numero):
        # Validar que el numero que se va a procesar no se encuentre ya procesado
        with open(output_file, 'r') as _filehandler:
            csv_file_reader = csv.DictReader(_filehandler)
            for row in csv_file_reader:
                if row['NUMERO'] == numero:
                    return 1
        return 0

# Obtener una lista de Ips 
with urllib.request.urlopen("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=json") as url:
    data : dict = json.load(url)

    # Iniciar la clase
    Scrapper : EjecutarScript = EjecutarScript(filename)
    
    # Recorrer un ciclo que itere los proxies disponibles para cambiarlos cuando sea necesario
    for intento in range(len(data['proxies'])):
        if intento == 0:
            proxy: str = "local"
            print(" Intentando con IP local")
        else:
            proxy : str =  data['proxies'][intento]['ip'] + ":" + str(data['proxies'][intento]['port'])
            print(" Intentando con proxy")
        Scrapper.AbrirNavegador(proxy)
    
 
