from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import time

# URL de inicio de sesión
login_url = "http://jsat.cooptortu.com.ar:8080/jsat/arenero/login.faces"

# Datos de inicio de sesión
usuario = '296'
contraseña = '@Grosso1736'

def get_data(tel):
    global login_url, usuario, contraseña
    # Configuración del navegador
    options = webdriver.ChromeOptions()
    options.add_argument("--start")
    #options.add_argument("--headless")  # Ejecuta el navegador en modo headless (sin interfaz gráfica)
    driver = webdriver.Chrome(options=options)
    
    try:
        # Abrir la página de inicio de sesión
        driver.get(login_url)

        # Encontrar los campos de usuario y contraseña e ingresar los datos
        usuario_input = driver.find_element(By.ID, 'usuarioTxt')
        usuario_input.send_keys(usuario)
        contraseña_input = driver.find_element(By.ID, '_id5')
        contraseña_input.send_keys(contraseña)

        # Hacer clic en el botón de iniciar sesión
        login_button = driver.find_element(By.ID, 'cmdOk')
        login_button.click()

        driver.get("http://jsat.cooptortu.com.ar:8080/jsat/arenero/mainJSAT.faces")

        menu_button = driver.find_element(By.ID, '_id1select_object')
        menu_button.click()

        service_button = driver.find_element(By.ID, 'Servicios0')
        service_button.click()

        filtro_input = driver.find_element(By.ID, '_id1filtro')
        filtro_input.send_keys(tel)
        filtro_input.send_keys("\n")

        # Esperar a que la página se cargue completamente (puedes ajustar el tiempo según sea necesario)
        driver.implicitly_wait(90)

        # Esperar hasta que el elemento sea clickeable
        primer_elemento = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, '/html/body/table/tbody/tr[1]/td/table/tbody/tr/td/table/tbody/tr/td[2]/table/tbody/tr/td[3]/left/select/option'))
        )
        # Hacer clic en el primer elemento
        primer_elemento.click()
        
        # Encontrar todos los elementos que coincidan con la clase 'ar_window_features_description'
        user_info_elements = driver.find_elements(By.CLASS_NAME, 'ar_window_features_description')
        # Obtener el texto
        nombre_cliente = user_info_elements[0].text
        # Encontrar la posición del carácter "-" y del carácter "("
        indice_inicio = nombre_cliente.find("-") + 1
        indice_fin = nombre_cliente.find("(")
        # Extraer la subcadena deseada
        nombre_cliente = nombre_cliente[indice_inicio:indice_fin].strip()
        print(f"Nombre: {nombre_cliente}")
        print(f"Telefono: {tel}")
        
        for i in range(2, 15):
            buscar_optica_alta = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]')
            if "FIBRA OPTICA" in buscar_optica_alta.text and "Alta" in buscar_optica_alta.text:
                seleccionar_optica = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[3]')
                user_ppoer = seleccionar_optica.text
                if "6722" in user_ppoer:
                    user_ppoer = user_ppoer.replace("6722", "")
                break             
        print(f"User: {user_ppoer}")
        
        buscar_optica_alta.click()
        
        # Encontrar el elemento para el que se simulará el desplazamiento del mouse
        elemento = driver.find_element(By.XPATH, '//*[@id="operacionesServicio2submenuHeader"]')
        # Crear una instancia de ActionChains
        actions = ActionChains(driver)
        # Mover el mouse al elemento
        actions.move_to_element(elemento).perform()
        time.sleep(1)

        recurso_tecnico = driver.find_element(By.XPATH, '//*[@id="itemtcnica_sep_recursostcnicos"]')
        recurso_tecnico.click()
        
        time.sleep(1)
        
    finally:
        # Cerrar el navegador
        driver.quit()

def config_lista():
    # Servicio
    tel_clientes = []
    while True:
        tel = input("Ingrese numero de abonado en Alta: ")
        if tel == '':
            break
        tel_clientes.append(tel)
    print(f"Los abonados ingresados son: {tel_clientes}")

    for tel in tel_clientes:
        get_data(tel)

while True:
    config_lista()