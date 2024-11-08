import os
import time
import keyboard
import csv
from dotenv import load_dotenv
from seleniumwire import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import SessionNotCreatedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from selenium_authenticated_proxy import SeleniumAuthenticatedProxy
from src.utils import click, movimiento_aleatorio_hasta_click

# Cargar las variable de entorno
load_dotenv()
USER_DIR : str = os.getenv("USER_DIR")

# Clase inicial del proyecto
class EjecutarScript():
    def __init__(self, filename: str, output_file: str) -> None:
        print(" Iniciando programa")
        self.filename : str = filename
        self.output_file: str = output_file
    def AbrirNavegador(self, PROXY: bool):
        # configuracion de opciones de chrome -----> aca cambias el usuario para abrir una sesion ya iniciada
        chrome_options: Options = Options()
        if (PROXY):
            chrome_options.add_argument("user-data-dir=" + USER_DIR)
            chrome_options.add_argument("profile-directory=Default")
    
            # inicializar el driver de chrome
            try:
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
            except SessionNotCreatedException:
                print(" La sesion no se ha logrado crear, cierre todos los navegadores que se esten ejecutando")
        else:
            print("TEST")
            proxy_username : str = "2bdd8ef305f5ccb8443a"
            proxy_password = "828ce4751e15c0db"
            proxy_address = "gw.dataimpulse.com"
            proxy_port = "823"
            proxy_url = f"http://{proxy_username}:{proxy_password}@{proxy_address}:{proxy_port}"

            # Configure Proxy Option
            print(" Configurando proxy")
            chrome_options.add_argument("user-data-dir=" + USER_DIR)
            chrome_options.add_argument("profile-directory=Default")
            #chrome_options.add_argument("--incognito")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled") 
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-certificate-errors-spki-list')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.set_capability('acceptInsecureCerts', "True")

            proxy_helper = SeleniumAuthenticatedProxy(proxy_url=proxy_url)
            proxy_helper.enrich_chrome_options(chrome_options)

            # inicializar el driver de chrome
            try:
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options,)
            except SessionNotCreatedException:
                print(" La sesion no se ha logrado crear, cierre todos los navegadores que se esten ejecutando")

        # abrir la pagina
        self.driver.get("https://numeracionyoperadores.cnmc.es/portabilidad/movil")
        time.sleep(5)
        keyboard.press_and_release('enter')
        keyboard.press_and_release('enter')

        # esperar a que la pagina se cargue
        
        try:
           WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "input-1")))
        except TimeoutException:
            return
        except NoSuchElementException:
            return

        # Procesar el csv de entrada
        with open(self.filename, newline='') as csvfile:
            spamreader = csv.reader(csvfile, delimiter=',')
            intentos_fallidos : int = 0
            for row in spamreader:
                contador = self.driver.execute_script('return document.querySelector(".v-alert__content").innerText.match(/(\d+)/)[0]')
                # print("Intentos disponibles: " + contador)
                if (row[0] != 'PHONE_NUMBER'):
                    if self.VerificarNumeroRepetido(numero=row[0]) == 1 or row[0][0] == '7':
                        pass
                    else:
                        print(" Procesando N. " + str(contador) + ": " + str(row[0]))
                        respuesta = self.ProcesarNumero(row[0])
                        if respuesta == "FAILED" :
                            intentos_fallidos = intentos_fallidos + 5
                            print(" Intentos fallidos: " + str(intentos_fallidos))
                        if  intentos_fallidos >= 1:
                            self.driver.quit()
                            break
                    if (contador == 0 or contador == "0" or intentos_fallidos >= 10):
                        self.driver.quit()
                        break
    
    def ProcesarNumero(self, numero) -> str:
        movimiento_aleatorio_hasta_click(500, 400)
        campo_numero = self.driver.find_element(By.ID, "input-1")
        campo_numero.send_keys(numero)

        # esperar un momento para asegurarnos de que el campo esta listo
        time.sleep(2)

        # cambiar al iframe del recaptcha
        try:
            self.driver.switch_to.frame(self.driver.find_element(By.XPATH, "//iframe[contains(@src, 'recaptcha')]"))
        except NoSuchElementException:
            print("El elemento no se ha encontrado")
            self.driver.refresh()
            time.sleep(5)
            return "FAILED"

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
                with open (self.output_file,'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([lista[1], lista[3], lista[5]])
                    file.close()
            
            campo_numero.click()
            campo_numero.send_keys(Keys.CONTROL + "a")
            campo_numero.send_keys(Keys.DELETE)
            return "SUCCESS"
        
        except NoSuchElementException:
            print(" El captcha no se puede resolver, reintente usando VPN o proxys")
            self.driver.refresh()
            time.sleep(5)
            return "FAILED"
        except ElementClickInterceptedException:
            print(" El captcha no se puede resolver, reintente usando VPN o proxys")
            self.driver.refresh()
            time.sleep(5)
            return "FAILED"
    
    def VerificarNumeroRepetido(self, numero) -> int:
        # Validar que el numero que se va a procesar no se encuentre ya procesado
        with open(self.output_file, 'r') as _filehandler:
            csv_file_reader = csv.DictReader(_filehandler)
            for row in csv_file_reader:
                if row['NUMERO'] == numero:
                    return 1
        return 0