import tkinter as tk
from tkinter import ttk
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time
import re
import threading


def configurar_wifi():
    ssid = "NOC"
    password = "sistemas"
    
    # URL de inicio de sesión
    login_url = "http://170.78.111.148/"
    
    # Datos de inicio de sesión
    usuario = 'admin'
    contraseña = 'admin'
    
    # Configuración del navegador
    options = webdriver.ChromeOptions()
    options.add_argument("--start")
    driver = webdriver.Chrome(options=options)
    
    # Abrir la página de inicio de sesión
    driver.get(login_url)
    
    # Encontrar los campos de usuario y contraseña e ingresar los datos
    usuario_input = driver.find_element(By.XPATH, '//*[@id="Frm_Username"]')
    usuario_input.send_keys(usuario)

    contraseña_input = driver.find_element(By.XPATH, '//*[@id="Frm_Password"]')
    contraseña_input.send_keys(contraseña)

    # Hacer clic en el botón de iniciar sesión
    login_button = driver.find_element(By.XPATH, '//*[@id="LoginId"]')
    login_button.click()
    
    # Verificar si el inicio de sesión fue exitoso
    current_url = driver.current_url
    if current_url != login_url:
        print("Inicio de sesión exitoso.")
        # Puedes hacer otras solicitudes aquí después de iniciar sesión, si es necesario
    else:
        print("Error al iniciar sesión. Verifica tus credenciales.")
        
    driver.implicitly_wait(5)
        
    text_hmtl = driver.find_element(By.XPATH,'//*[@id="title_path"]')
    print (text_hmtl)    
        
    login_out_button = driver.find_element(By.XPATH,'//*[@id="content"]/div[2]/div[3]/a')  
    login_out_button.click()  
        
    network_button = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, '/html/body/div[3]/div[1]/div[1]/table/tbody/tr/td/table/tbody/tr[6]'))) # Esperar a que el elemento esté presente
    network_button = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[3]/div[1]/div[1]/table/tbody/tr/td/table/tbody/tr[6]'))) # Esperar a que el elemento sea interactivo
    network_button.click()

    wlan_button = driver.find_element(By.XPATH, '//*[@id="menu0"]/table/tbody/tr/td/table/tbody/tr[10]/td[2]')
    wlan_button.click()
    
    ssid_button = driver.find_element(By.XPATH, '//*[@id="menu0"]/table/tbody/tr/td/table/tbody/tr[6]/td[2]')
    ssid_button.click()
    
    ssid_input = driver.find_element(By.XPATH, '//*[@id="Frm_ESSID"]')
    ssid_input.send_keys(ssid)
    
    submit_button = driver.find_element(By.XPATH, '//*[@id="Btn_Submit"]')
    submit_button.click()
    
    # Esperar a que la página se cargue completamente (puedes ajustar el tiempo según sea necesario)
    driver.implicitly_wait(90)
    
configurar_wifi()