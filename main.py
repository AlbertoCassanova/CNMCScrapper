import csv
import os
import mysql.connector
from src.utils import numeroLineas
from src.scrapper import EjecutarScript

# Nombre del archivo de salida
output_file : str = "datos.csv"

# Encabezados para el archvo de salida
data : list[str] = ['NUMERO', 'OPERADOR', 'FECHA DE CONSULTA']

# Introducir el nombre del archivo, debe estar en formato .csv y estar en el mismo directorio que el script
filename : str = input("Escriba el nombre del archivo .csv a procesar: ")

# Iniciar la clase
Scrapper : EjecutarScript = EjecutarScript(filename, output_file)

# Verificar si existe el archivo de salida datos.csv
if (os.path.isfile(output_file) == False):
    with open (output_file,'w') as file:
        writer = csv.writer(file)
        writer.writerow(data)
        file.close()
    
# Recorrer un ciclo que itere los proxies disponibles para cambiarlos cuando sea necesario
for intento in range(numeroLineas(filename) -1):
    if intento == 0:
        proxy_local: bool = True
        print(" Intentando con IP local")
    else:
        proxy_local : bool =  True
        print(" Intentando con proxy")
    Scrapper.AbrirNavegador(proxy_local)
