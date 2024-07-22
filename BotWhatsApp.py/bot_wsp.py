from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import schedule
import time

# Inicia el WebDriver
driver = webdriver.Chrome()

# Abre WhatsApp Web
driver.get('https://web.whatsapp.com')

# Pausa para escanear el código QR manualmente
print("Escanea el código QR y presiona Enter...")
input()

# Función para enviar el mensaje
def enviar_mensaje(contacto, mensaje):
    search_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]')
    search_box.clear()
    search_box.send_keys(contacto)
    search_box.send_keys(Keys.ENTER)
    time.sleep(2)
    
    message_box = driver.find_element(By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]')
    message_box.send_keys(mensaje)
    message_box.send_keys(Keys.ENTER)

# Ejemplo de uso
contacto = 'Chuli'
mensaje = 'Recordatorio: Depositar dinero en tu cuenta para pagar las tarjetas.'

# Programar el mensaje
def job():
    enviar_mensaje(contacto, mensaje)

schedule.every().day.at("09:00").do(job)

job()

while True:
    schedule.run_pending()
    time.sleep(1)
