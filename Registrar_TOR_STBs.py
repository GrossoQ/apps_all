from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def migrar_M10():
    # URL de inicio de sesión
    login_url = "https://3.216.128.89:4446/maui#/login"

    # Datos de inicio de sesión
    usuario = 'portiz'
    contraseña = 'moreno1160*'
    
    tor = input('Ingrese TOR: ')
    
    macs = []
    while True:
        mac = input('Ingrese la MAC (o ingrese Enter para terminar de ingresar MACs): ')
        if mac.lower() == '':
            break
        macs.append(mac)
    print("MACs ingresadas: ", macs)

    # Configuración del navegador
    options = webdriver.ChromeOptions()
    options.add_argument("--start")
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    driver = webdriver.Chrome(options=options)

    try:
        # Abrir la página de inicio de sesión
        driver.get(login_url)
        
        # Esperar a que la página se cargue completamente
        WebDriverWait(driver, 90).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="username"]'))
        )

        # Encontrar los campos de usuario y contraseña e ingresar los datos
        usuario_input = driver.find_element(By.XPATH, '//*[@id="username"]')
        usuario_input.send_keys(usuario)

        contraseña_input = driver.find_element(By.XPATH, '//*[@id="password"]')
        contraseña_input.send_keys(contraseña)

        # Hacer clic en el botón de iniciar sesión
        login_button = driver.find_element(By.XPATH, '//*[@id="container"]/section/ng-component/div[1]/div[2]/form/div[3]/button')
        login_button.click()

        # Esperar a que la página de dispositivos se cargue completamente
        WebDriverWait(driver, 90).until(
            EC.presence_of_element_located((By.XPATH, '/html/body/app-root/section/section/app-devices/section/section[2]/form/div[1]/div[1]/div/button'))
        )
        
        time.sleep(1)

        for mc in macs:
            add_device_button = driver.find_element(By.XPATH, '/html/body/app-root/section/section/app-devices/section/section[2]/form/div[1]/div[1]/div/button')
            add_device_button.click()

            escribir_mac_xpath = WebDriverWait(driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, '/html/body/ngb-modal-window/div/div/form/div[2]/div[2]/div/input'))
            )

            # Ingresar la MAC
            escribir_mac_xpath.clear()
            escribir_mac_xpath.send_keys(mc)

            customer_id = driver.find_element(By.XPATH, '/html/body/ngb-modal-window/div/div/form/div[2]/div[4]/div/input')
            customer_id.send_keys(tor)

            submit_button = driver.find_element(By.XPATH, '/html/body/ngb-modal-window/div/div/form/div[3]/button[1]')
            submit_button.click()

            # Esperar a que el modal desaparezca antes de continuar
            WebDriverWait(driver, 30).until(EC.staleness_of(submit_button))

            # Esperar a que el botón "Add Device" esté disponible antes de continuar
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/app-root/section/section/app-devices/section/section[2]/form/div[1]/div[1]/div/button'))
            )

    finally:
        # Cerrar el navegador
        driver.quit()

# Bucle principal para reiniciar el script
while True:
    migrar_M10()
    # Esperar unos segundos antes de reiniciar el script
    time.sleep(1)  # Ajusta el tiempo de espera según sea necesario
