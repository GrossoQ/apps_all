from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time

def migrar_M10():
    # URL de inicio de sesión
    login_url = "https://engage.aminoengage.com/engage/#dashboard/main"

    # Datos de inicio de sesión
    usuario = 'qgrosso@cooptortu.com.ar'
    contraseña = '@Quimey1736'
    
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
    driver = webdriver.Chrome(options=options)

    # Abrir la página de inicio de sesión
    driver.get(login_url)
    
    # Esperar a que la página se cargue completamente (puedes ajustar el tiempo según sea necesario)
    driver.implicitly_wait(90)

    # Encontrar los campos de usuario y contraseña e ingresar los datos
    usuario_input = driver.find_element(By.XPATH, '//*[@id="username"]')
    usuario_input.send_keys(usuario)

    contraseña_input = driver.find_element(By.XPATH, '//*[@id="password"]')
    contraseña_input.send_keys(contraseña)

    # Hacer clic en el botón de iniciar sesión
    login_button = driver.find_element(By.XPATH, '/html/body/main/form/fieldset/div[6]/div/button')
    login_button.click()

    driver.get('https://ensure.aminoengage.com/ensure?operator=11583251')

    # Esperar a que la página se cargue completamente (puedes ajustar el tiempo según sea necesario)
    driver.implicitly_wait(90)

    manage_button = driver.find_element(By.XPATH, '/html/body/div/div[3]/div[3]/div[2]/a[1]/div')
    manage_button.click()
    
    escribir_mac_xpath = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div[2]/div/div[3]/div/div[2]/table/thead/tr[2]/td[3]/input')
    
    for mc in macs:
        if not '' in escribir_mac_xpath.text:
            mac_input = escribir_mac_xpath
            mac_input.send_keys(mc)
        else:
            escribir_mac_xpath.clear()
            mac_input = escribir_mac_xpath
            mac_input.send_keys(mc)
        
        time.sleep(1)
        
        tilde_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div[2]/div/div[3]/div/div[2]/table/tbody/tr[1]/td[1]/input')
        tilde_button.click()
        
        select_element = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div[2]/div/div[3]/div/div[3]/div[1]/select')
        select = Select(select_element)
        
        filtro = driver.find_element(By.XPATH,'/html/body/div[1]/div[4]/div[2]/div/div[3]/div/div[2]/table/tbody/tr[1]/td[5]')
        filtro_text = filtro.text
        
        if '49' == filtro_text:
            select.select_by_index(6)
        elif '85' == filtro_text:
            select.select_by_index(4)
        elif 'Ax5x' == filtro_text:
            select.select_by_index(2)
        elif 'Ax4x' == filtro_text:
            select.select_by_index(0)
        else:
            select.select_by_index(4)
            
        join_button = driver.find_element(By.XPATH, '/html/body/div[1]/div[4]/div[2]/div/div[3]/div/div[3]/div[1]/button')
        join_button.click()     
        

    # Cerrar el navegador
    driver.quit()

# Bucle principal para reiniciar el script
while True:
    migrar_M10()
    # Esperar unos segundos antes de reiniciar el script
    time.sleep(1)  # Ajusta el tiempo de espera según sea necesario