from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
import telnetlib3
import asyncio
import time
import re

# URL de inicio de sesión
login_url = "http://jsat.cooptortu.com.ar:8080/jsat/arenero/login.faces"

# Configuración del navegador
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--log-level=3")  # Esto minimiza los mensajes de advertencia en la consola del navegador
#options.add_argument("--start")  # Ejecuta el navegador con entorno grafico
driver = webdriver.Chrome(options=options)

# Datos de inicio de sesión
usuario = '296'
contraseña = '@Grosso1736'
contra = "1234"

async def get_data(tel):
    global driver, login_url, usuario, contraseña, olt, puerto, posicion, nombre_cliente, cont, user_ppoer, contra, onu_gpon
    
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
        print(f"Contra: {contra}")
        
        cont = 0
        for i in range(2, 15):  
            sector_iptv = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[2]')
            sector_iptv_vinculado = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[5]')
            sector_iptv_alta = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[4]')
            if "Envio" not in sector_iptv.text:
                if "Acceso IPTV" in sector_iptv.text and "Alta" in sector_iptv_alta.text:
                    if tel in sector_iptv_vinculado.text or user_ppoer in sector_iptv_vinculado.text:
                        elemento_iptv = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[3]')
                        id_iptv = elemento_iptv.text
                        print(f"IPTV: {id_iptv}")
                        break
                    else:
                        print("Hay un IPTV NO vinculado")
                        print(f"IPTV: {id_iptv}")
                        cont+=1
            else:
                if cont < 1:
                    print("No hay IPTV")
                    break
                else:
                    break
        
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
        
        # Buscar el sector que contiene "ONT"
        onu_gpon = None
        for i in range(2, 15):  # Cambia el rango según tu necesidad
            sector = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[2]')
            if "ONT" in sector.text:
                onu_gpon = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[3]')
                onu_gpon = onu_gpon.text
                break

        if onu_gpon is not None:
            print(f"SN: {onu_gpon}")
        else:
            print("No se encuentra sector con ONT")
        
        # Buscar el sector que contiene "ONT"
        olt_puerto_posicion = None
        for i in range(2, 15):  # Cambia el rango según tu necesidad
            sector_olt = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[2]')
            if "GPON" in sector_olt.text:
                olt_puerto_posicion = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[3]')
                olt_puerto_posicion = olt_puerto_posicion.text
                break

        if olt_puerto_posicion is not None:
            print(f"GPON: {olt_puerto_posicion}")
        else:
            print("No se encuentra sector con GPON")

        # Usar expresiones regulares para extraer la información requerida
        olt_match = re.search(r'-(.*?)-', olt_puerto_posicion)
        olt = olt_match.group(1)

        puerto_match = re.search(r'\[(.*?)\]', olt_puerto_posicion)
        puerto_str = puerto_match.group(1)
        puerto = '/'.join(puerto_str.split(', ')[0:-1])

        posicion_match = re.search(r'(\d+)\]$', olt_puerto_posicion)
        posicion = posicion_match.group(1)    
            
    except Exception as e:
        print(f"Error al obtener datos para el teléfono {tel}: {e}")

async def telnet_to_olt(tel): # OLT Destino
    num_olt = olt[:1] + "." + olt[1:]
    if olt == "121" or olt == "122" or olt == "123":
        host = f"10.225.{num_olt}"
    elif olt == "321" or olt == "322" or olt == "323" or olt == "521" or olt == "221" or olt == "222":
        host = f"10.253.{num_olt}"
    port = 23
    username = "zte"
    password = "zte"
    
    try:
        print("Configurando abonado...")
        # Crear una conexión Telnet
        reader, writer = await telnetlib3.open_connection(host, port)
        # Esperar a que aparezca el prompt de inicio de sesión
        await asyncio.wait_for(reader.read(1000), timeout=1)
        writer.write(username + "\n")
        # Esperar a que aparezca el prompt de contraseña
        await asyncio.wait_for(reader.read(1000), timeout=1)
        writer.write(password + "\n")
        
        # Leer hasta que se encuentre el delimitador "#"
        await reader.readuntil(b"#")
        
        # Lista de comandos a ejecutar
        comandos = [
        "config t",
        f"interface gpon-olt_{puerto}",
        f"onu {posicion} type ZXHN-F680 sn {onu_gpon}",
        "!",
        f"interface gpon-onu_{puerto}:{posicion}",
        f"registration-method sn {onu_gpon}",
        "!",
        "config t",
        f"interface gpon-onu_{puerto}:{posicion}",
        f"name {nombre_cliente} TEL. {tel}",
        "tcont 1 profile YABIRU_1G_BE",
        "tcont 2 profile IPTV-F",
        "gemport 1 tcont 1 queue 1",
        "gemport 2 tcont 2 queue 1",
        f"service-port 1 vport 1 user-vlan 1{olt} user-etype PPPOE vlan 1{olt}",
        f"service-port 2 vport 2 user-vlan 3{olt} vlan 3{olt}",
        "ip dhcp snooping enable vport 2",
        "dhcpv4-l2-relay-agent enable vport 2",
        "dhcpv4-l2-relay-agent trust true replace vport 2"
        ]

        # Ejecutar los comandos
        await ejecutar_comandos(writer, reader, comandos)
        if cont < 0:
            # Lista de comandos a ejecutar
            comandos = [
            "!",
            f"pon-onu-mng gpon-onu_{puerto}:{posicion}",
            f"service ppp gemport 1 iphost 1 cos 2 vlan 1{olt}",
            f"service iptv gemport 2 cos 5 vlan 3{olt}",
            f"pppoe 1 nat enable user {user_ppoer} password {contra}",
            f"vlan port eth_0/1 mode tag vlan 1{olt} pri 2",
            f"vlan port eth_0/2 mode tag vlan 1{olt} pri 2",
            f"vlan port eth_0/3 mode tag vlan 3{olt} pri 5",
            f"vlan port eth_0/4 mode tag vlan 3{olt} pri 5",
            f"vlan port wifi_0/1 mode tag vlan 1{olt} pri 2",
            f"vlan port wifi_0/5 mode tag vlan 1{olt} pri 2",
            "dhcp-ip ethuni eth_0/1 from-onu",
            "dhcp-ip ethuni eth_0/2 from-onu",
            "dhcp-ip ethuni eth_0/3 from-internet",
            "dhcp-ip ethuni eth_0/4 from-internet",
            "security-mgmt 1 state enable ingress-type lan", 
            "security-mgmt 2 state enable mode forward", 
            "security-mgmt 2 start-src-ip 190.13.224.2 end-src-ip 190.13.224.2"
            ]
            
            # Ejecutar los comandos
            await ejecutar_comandos(writer, reader, comandos)
            
        else:
            # Lista de comandos a ejecutar
            comandos = [
            "!",
            f"pon-onu-mng gpon-onu_{puerto}:{posicion}",
            f"service ppp gemport 1 iphost 1 cos 2 vlan 1{olt}",
            f"service iptv gemport 2 cos 5 vlan 3{olt}",
            f"pppoe 1 nat enable user {user_ppoer} password {contra}",
            f"vlan port eth_0/1 mode tag vlan 1{olt} pri 2",
            f"vlan port eth_0/2 mode tag vlan 1{olt} pri 2",
            f"vlan port eth_0/3 mode tag vlan 1{olt} pri 2",
            f"vlan port eth_0/4 mode tag vlan 1{olt} pri 2",
            f"vlan port wifi_0/1 mode tag vlan 1{olt} pri 2",
            f"vlan port wifi_0/5 mode tag vlan 1{olt} pri 2",
            "dhcp-ip ethuni eth_0/1 from-onu",
            "dhcp-ip ethuni eth_0/2 from-onu",
            "dhcp-ip ethuni eth_0/3 from-onu",
            "dhcp-ip ethuni eth_0/4 from-onu",
            "security-mgmt 1 state enable ingress-type lan", 
            "security-mgmt 2 state enable mode forward", 
            "security-mgmt 2 start-src-ip 190.13.224.2 end-src-ip 190.13.224.2"
            ]
            
            # Ejecutar los comandos
            await ejecutar_comandos(writer, reader, comandos)
            
        comandos = [
            "!",
            "config t",
            f"igmp mvlan 3{olt} receive-port gpon-onu_{puerto}:{posicion} vport 2"]
        # Ejecutar los comandos
        await ejecutar_comandos(writer, reader, comandos)
        
        print("CONFIGURACION FINALIZADA")
            
    except Exception as e:
        print(f"Error en configuración Telnet para el teléfono {tel}: {e}")
    
async def ejecutar_comandos(writer, reader, comandos):
    for comando in comandos:
        await enviar_comando(writer, reader, comando) 
        
async def enviar_comando(writer, reader, comando):
    writer.write(comando + "\n")
    respuesta = await reader.readuntil(b"#")
    if b"%Code 78438:" in respuesta:
        print("Write en proceso, configurar mas tarde")

async def config_lista():
    # Servicio
    tel_clientes = []
    while True:
        tel = input("Ingrese numero de abonado en Alta (Enter para finalizar): ")
        if tel == '':
            break
        tel_clientes.append(tel)
    print(f"Los abonados ingresados son: {tel_clientes}")

    for tel in tel_clientes:
        await get_data(tel)
        await telnet_to_olt(tel)

async def main():
    try:
        while True:
            await config_lista()
    except KeyboardInterrupt:
        pass
    finally:
        # Cerrar el navegador al finalizar
        driver.quit()

if __name__ == "__main__":
    asyncio.run(main())