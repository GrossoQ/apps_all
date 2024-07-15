from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time
import asyncio
import telnetlib3
import re
from tkinter import Scrollbar, Menu
import tkinter as tk
from tkinter import ttk
import threading
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_datos():
    mostrar_texto("Iniciando sesion...")
    global onu_gpon, nombre_cliente, tel_cliente, user_ppoer, cont, contra, olt, puerto, posicion
    # URL de inicio de sesión
    login_url = "http://jsat.cooptortu.com.ar:8080/jsat/arenero/login.faces"

    # Datos de inicio de sesión
    usuario = '296'
    contraseña = '@Grosso1736'

    # Servicio
    tel_cliente = abonado_entry_1.get()
    contra = "1234"

    # Configuración del navegador
    options = webdriver.ChromeOptions()
    options.add_argument("--start")
    driver = webdriver.Chrome(options=options)

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

    # Verificar si el inicio de sesión fue exitoso
    current_url = driver.current_url
    if current_url != login_url:
        mostrar_texto("Inicio de sesión exitoso.")
        # Puedes hacer otras solicitudes aquí después de iniciar sesión, si es necesario
    else:
        mostrar_texto("Error al iniciar sesión. Verifica tus credenciales.")

    menu_button = driver.find_element(By.ID, '_id1select_object')
    menu_button.click()

    service_button = driver.find_element(By.ID, 'Servicios0')
    service_button.click()

    filtro_input = driver.find_element(By.ID, '_id1filtro')
    filtro_input.send_keys(tel_cliente)
    filtro_input.send_keys("\n")

    # Esperar a que la página se cargue completamente (puedes ajustar el tiempo según sea necesario)
    driver.implicitly_wait(90)
    time.sleep(1)
    
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
    mostrar_texto(f"Nombre: {nombre_cliente}")
    mostrar_texto(f"Telefono: {tel_cliente}")

    elemento_optica = None
    for i in range(2, 15):  
        try:
            sector_optica = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[2]')
            sector_alta = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[4]')
            if "FIBRA OPTICA" in sector_optica.text and "Alta" in sector_alta.text:
                elemento_optica = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[3]')
                sector_total = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]')
                user_ppoer = elemento_optica.text
                if "6722" in user_ppoer:
                    user_ppoer = user_ppoer.replace("6722", "")
                break
        except NoSuchElementException:
            continue
        
    elemento_iptv = None
    cont = 0
    for i in range(2, 15):  
        try:
            sector_iptv = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[2]')
            sector_iptv_vinculado = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[5]')
            sector_iptv_alta = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[4]')
            if "Envio" not in sector_iptv.text:
                if "Acceso IPTV" in sector_iptv.text and "Alta" in sector_iptv_alta.text:
                    if tel_cliente in sector_iptv_vinculado.text or user_ppoer in sector_iptv_vinculado.text:
                        elemento_iptv = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[3]')
                        id_iptv = elemento_iptv.text
                        break
                    else:
                        mostrar_texto("Hay un IPTV NO vinculado")
                        cont+=1
            else:
                if cont < 1:
                    mostrar_texto("No hay IPTV")
                    break
                else:
                    break
        except NoSuchElementException:
            continue

    if elemento_iptv is not None:
        mostrar_texto(f"IPTV: {id_iptv}")

    if elemento_optica is not None:
        mostrar_texto(f"Usuario: {user_ppoer}")
        mostrar_texto(f"Contraseña: {contra}")
        sector_total.click()
    else:
        mostrar_texto("No se encuentra sector con FIBRA OPTICA y Alta")

    # Encontrar el elemento para el que se simulará el desplazamiento del mouse
    elemento = driver.find_element(By.XPATH, '//*[@id="operacionesServicio2submenuHeader"]')
    # Crear una instancia de ActionChains
    actions = ActionChains(driver)
    # Mover el mouse al elemento
    actions.move_to_element(elemento).perform()
    time.sleep(1)

    recurso_tecnico = driver.find_element(By.XPATH, '//*[@id="itemtcnica_sep_recursostcnicos"]')
    recurso_tecnico.click()

    # Buscar el sector que contiene "ONT"
    onu_gpon = None
    for i in range(2, 15):  # Cambia el rango según tu necesidad
        sector = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[2]')
        if "ONT" in sector.text:
            onu_gpon = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[3]')
            onu_gpon = onu_gpon.text
            break

    if onu_gpon is not None:
        mostrar_texto(f"SN: {onu_gpon}")
    else:
        mostrar_texto("No se encuentra sector con ONT")
        
    # Buscar el sector que contiene "ONT"
    olt_puerto_posicion = None
    for i in range(2, 15):  # Cambia el rango según tu necesidad
        sector_olt = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[2]')
        if "GPON" in sector_olt.text:
            olt_puerto_posicion = driver.find_element(By.XPATH, f'//*[@id="grid"]/tbody/tr[{i}]/td[3]')
            olt_puerto_posicion = olt_puerto_posicion.text
            break

    if olt_puerto_posicion is not None:
        mostrar_texto(f"GPON: {olt_puerto_posicion}")
    else:
        mostrar_texto("No se encuentra sector con GPON")

    # Usar expresiones regulares para extraer la información requerida
    olt_match = re.search(r'-(.*?)-', olt_puerto_posicion)
    olt = olt_match.group(1)

    puerto_match = re.search(r'\[(.*?)\]', olt_puerto_posicion)
    puerto_str = puerto_match.group(1)
    puerto = '/'.join(puerto_str.split(', ')[0:-1])

    posicion_match = re.search(r'(\d+)\]$', olt_puerto_posicion)
    posicion = posicion_match.group(1)        

    # Cerrar el navegador
    driver.quit()
    
# Función para mostrar el texto en la ventana
def mostrar_texto(texto):
    output_text.config(state=tk.NORMAL)  # Habilitar la edición del Text widget
    output_text.insert(tk.END, f"{texto}\n")
    output_text.see(tk.END)

async def on_connect():
    await main()
    
def handle_enter(event):
    # Ejecutar la función on_connect en un hilo separado
    thread = threading.Thread(target=run_async_function, args=(on_connect,))
    thread.start()
    
def run_async_function(func):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(func())
    loop.close()

def connect():
    # Ejecutar la función on_connect en un hilo separado
    thread = threading.Thread(target=run_async_function, args=(on_connect,))
    thread.start()

async def enviar_comando(writer, reader, comando):
    writer.write(comando + "\n")
    respuesta = await reader.readuntil(b"#")
    if b"%Code 78438:" in respuesta:
        mostrar_texto("Write en proceso, configurar mas tarde")

async def ejecutar_comandos(writer, reader, comandos):
    for comando in comandos:
        await enviar_comando(writer, reader, comando)  
        
        
# Nuevas funciones para los ventana de impresion
def ignore_keypress(event):
    return "break"

def copy_text(event):
    selected_text = output_text.get("sel.first", "sel.last")
    root.clipboard_clear()
    root.clipboard_append(selected_text)
    
def paste_text(event):
    if event.widget != output_text:
        return  # No hacer nada si el evento no proviene del widget de texto
    # Obtener texto del portapapeles
    text_from_clipboard = root.clipboard_get()
    # Insertar el texto en la posición del cursor
    output_text.insert("insert", text_from_clipboard)

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)
        
def limpiar_ventana():
    output_text.delete('1.0', tk.END)
    

async def telnet_to_olt2(): # OLT Destino
    num_olt = olt[:1] + "." + olt[1:]
    if olt == "121" or olt == "122" or olt == "123":
        host = f"10.225.{num_olt}"
    elif olt == "321" or olt == "322" or olt == "323" or olt == "521" or olt == "221" or olt == "222":
        host = f"10.253.{num_olt}"
    port = 23
    username = "zte"
    password = "zte"
    
    try:
        mostrar_texto("Configurando abonado...")
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
        f"name {nombre_cliente} TEL. {tel_cliente}",
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
        
        output_text.insert(tk.END, f"CONFIGURACION FINALIZADA\n\n")
        output_text.see(tk.END)  # Hacer que la barra de desplazamiento se mueva hacia abajo
            
    except Exception as e:
        return f"Error: {e}"
    

# Ejecutar la función
async def main():
    get_datos()
    await telnet_to_olt2()
    

root = tk.Tk()

# Configurar el icono
icon_path = "C:/Users/Grosso Quimey/Desktop/APP Python/APP Listas/IPTV.ico"
try:
    root.iconbitmap(default=icon_path)
except tk.TclError as e:
    print(f"Error al configurar el icono: {e}")
    
root.title("APP LISTAS")

# Configurar el tamaño de la ventana
root.geometry("500x390")

# Configurar el estilo del tema
style = ttk.Style()
style.theme_use("clam")

# Configurar colores y fuentes personalizadas
root.configure(bg="#2E3B4E")

# Marco para la sección del Abonado
frame_olt_inicial = tk.Frame(root, bg="#2E3B4E")
frame_olt_inicial.grid(row=0, column=0, padx=10, pady=10)


# Aquí van los widgets para la entrada de datos del Abonado
abonado_label_1 = tk.Label(frame_olt_inicial, text="Abonado:", font=("Arial", 12), fg="white", bg="#2E3B4E")
abonado_label_1.grid(row=1, column=0, padx=5, pady=5)
abonado_entry_1 = tk.Entry(frame_olt_inicial)
abonado_entry_1.grid(row=1, column=1, padx=5, pady=5)
abonado_entry_1.bind("<Button-3>", show_context_menu)  # Botón derecho del mouse
# Vincular la función on_connect al presionar Enter
abonado_entry_1.bind("<Return>", handle_enter)

connect_button1 = tk.Button(root, text="Configurar Abonado", command=connect, bg="gray", fg="white", font=("Arial", 12), padx=10, pady=5, relief="solid", borderwidth=1)
connect_button1.grid(row=1, column=0, columnspan=2, padx=(10,5), pady=10)

# Botón para limpiar la ventana de salida de datos
limpiar_button = tk.Button(root, text="Limpiar", command=limpiar_ventana, bg="gray", fg="white", font=("Arial", 12), padx=10, pady=5, relief="solid", borderwidth=1)
limpiar_button.grid(row=3, column=0, columnspan=2, pady=10)

# Ventana de salida de datos
output_text = tk.Text(root, height=10, width=50, bg="white", fg="black", font=("Arial", 12))
output_text.grid(row=2, column=0, columnspan=2, pady=10)
output_text.bind("<Key>", ignore_keypress) # Ignora entrada por teclado
output_text.bind("<Control-c>", copy_text) # Habilita opcion de copiado
output_text.bind("<Control-v>", paste_text) # Habilita opcion de copiado

# Crear menú contextual para copiar y pegar
context_menu = Menu(root, tearoff=0)
context_menu.add_command(label="Copy", command=lambda: root.event_generate("<Control-c>"))
context_menu.add_command(label="Paste", command=lambda: root.event_generate("<Control-v>"))

output_text.bind("<Button-3>", show_context_menu)  # Botón derecho para mostrar el menú contextual

# Barra de desplazamiento
scrollbar = Scrollbar(root, command=output_text.yview)
scrollbar.grid(row=2, column=6, sticky="ns")
output_text.config(yscrollcommand=scrollbar.set)

# Configuración de pesos para que los widgets se expandan correctamente
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()