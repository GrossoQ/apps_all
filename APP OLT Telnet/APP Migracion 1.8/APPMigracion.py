import asyncio
import telnetlib3
import re
from tkinter import Scrollbar, Menu
import tkinter as tk
from tkinter import ttk
import threading

async def telnet_to_olt(olt, puerto, posicion): # OLT Inicial

    num_olt = olt[:1] + "." + olt[1:]
    
    if olt == "121" or olt == "122" or olt == "123":
        host = f"10.225.{num_olt}"
    elif olt == "321" or olt == "322" or olt == "323" or olt == "521" or olt == "221" or olt == "222":
        host = f"10.253.{num_olt}"
    port = 23
    username = "zte"
    password = "zte"
    

    try:
        global nombre, telefono, serial_number, usuario, contraseña, contador_vlans
        
        mostrar_texto("Obteniendo datos...")
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
        # Ejecuta comando name_tel
        writer.write(f"show running-config interface gpon-onu_{puerto}:{posicion}" + "\n")
        # Leer hasta que se encuentre el delimitador "#"
        data = await reader.readuntil(b"#")
        # Decodificar los datos leídos como una cadena
        datos_str = data.decode()
        # Definimos el patrón de expresión regular para buscar el nombre y el teléfono
        patron_name_tel = r"name\s+(.+)\s+TEL\.\s+(\d+)"
        # Buscamos el patrón en la salida
        name_tel = re.search(patron_name_tel, datos_str, re.IGNORECASE)

        # Si se encuentra el patrón, guardamos los datos en variables
        if name_tel:
            nombre = name_tel.group(1)
            telefono = name_tel.group(2)
        else:
            return await no_datos()
        
        # Ejecuta comando ONU sn
        writer.write(f"show gpon onu baseinfo gpon-olt_{puerto} {posicion}" + "\n")
        # Leer hasta que se encuentre el delimitador "#"
        data = await reader.readuntil(b"#")
        # Decodificar los datos leídos como una cadena
        datos_str = data.decode()
        # Definimos el patrón de expresión regular para buscar el nombre y el teléfono
        patron_sn = r"SN:(\w+)"
        # Buscamos el patrón en la salida
        sn = re.search(patron_sn, datos_str)
        # Si se encuentra el patrón, guardamos los datos en variables
        if sn:
            serial_number = sn.group(1)
        else:
            return await no_datos()
        
        # Ejecuta comando usuario contraseña
        writer.write(f"show onu running config gpon-onu_{puerto}:{posicion}" + "\n")
        # Leer hasta que se encuentre el delimitador "#"
        data = await reader.readuntil(b"#")
        # Decodificar los datos leídos como una cadena
        datos_str = data.decode()
        # Definimos los patrones de expresión regular para buscar el usuario y la contraseña
        # Patrón de búsqueda para usuario y contraseña
        patron_usuario_password = r"user (\w+).*password (\w+)"
        # Definimos el patrón de expresión regular para buscar las VLAN
        patron_vlan = r"vlan port eth_0/\d+ mode tag vlan (\d+)"
        # Buscamos el patrón en la salida
        resultado_usuario_contraseña = re.search(patron_usuario_password, datos_str)
        
        # Verificar si se encontraron coincidencias y guardar en variables
        if resultado_usuario_contraseña:
            usuario = resultado_usuario_contraseña.group(1)
            contraseña = resultado_usuario_contraseña.group(2)
        else:
            return await no_datos()

        # Contamos las VLAN dentro de la parte indicada de la salida
        vlans = re.findall(patron_vlan, datos_str)
        contador_vlans = sum(3000 <= int(vlan) <= 3999 for vlan in vlans)
        
        mostrar_texto("Datos obtenidos:")
        return mostrar_datos()

    except Exception as e:
        return f"Error: {e}"
    
    
async def telnet_to_olt2(olt, puerto, posicion): # OLT Destino
        
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
        await asyncio.wait_for(reader.read(1000), timeout=2)
        writer.write(username + "\n")
        # Esperar a que aparezca el prompt de contraseña
        await asyncio.wait_for(reader.read(1000), timeout=2)
        writer.write(password + "\n")
        
        # Leer hasta que se encuentre el delimitador "#"
        await reader.readuntil(b"#")
        
        # Lista de comandos a ejecutar
        comandos = [
        "config t",
        f"interface gpon-olt_{puerto}",
        f"onu {posicion} type ZXHN-F680 sn {serial_number}",
        "!",
        f"interface gpon-onu_{puerto}:{posicion}",
        f"registration-method sn {serial_number}",
        "!",
        "config t",
        f"interface gpon-onu_{puerto}:{posicion}",
        f"name {nombre} TEL. {telefono}",
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
        
        if contador_vlans == 1:
            # Lista de comandos a ejecutar
            comandos = [
            "!",
            f"pon-onu-mng gpon-onu_{puerto}:{posicion}",
            f"service ppp gemport 1 iphost 1 cos 2 vlan 1{olt}",
            f"service iptv gemport 2 cos 5 vlan 3{olt}",
            f"pppoe 1 nat enable user {usuario} password {contraseña}",
            f"vlan port eth_0/1 mode tag vlan 1{olt} pri 2",
            f"vlan port eth_0/2 mode tag vlan 1{olt} pri 2",
            f"vlan port eth_0/3 mode tag vlan 1{olt} pri 2",
            f"vlan port eth_0/4 mode tag vlan 3{olt} pri 5",
            f"vlan port wifi_0/1 mode tag vlan 1{olt} pri 2",
            f"vlan port wifi_0/5 mode tag vlan 1{olt} pri 2",
            "dhcp-ip ethuni eth_0/1 from-onu",
            "dhcp-ip ethuni eth_0/2 from-onu",
            "dhcp-ip ethuni eth_0/3 from-onu",
            "dhcp-ip ethuni eth_0/4 from-internet",
            "security-mgmt 1 state enable ingress-type lan", 
            "security-mgmt 2 state enable mode forward", 
            "security-mgmt 2 start-src-ip 190.13.224.2 end-src-ip 190.13.224.2"
            ]
            
            # Ejecutar los comandos
            await ejecutar_comandos(writer, reader, comandos)
            
        elif contador_vlans == 2:
            # Lista de comandos a ejecutar
            comandos = [
            "!",
            f"pon-onu-mng gpon-onu_{puerto}:{posicion}",
            f"service ppp gemport 1 iphost 1 cos 2 vlan 1{olt}",
            f"service iptv gemport 2 cos 5 vlan 3{olt}",
            f"pppoe 1 nat enable user {usuario} password {contraseña}",
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
        
        elif contador_vlans == 3:
            # Lista de comandos a ejecutar
            comandos = [
            "!",
            f"pon-onu-mng gpon-onu_{puerto}:{posicion}",
            f"service ppp gemport 1 iphost 1 cos 2 vlan 1{olt}",
            f"service iptv gemport 2 cos 5 vlan 3{olt}",
            f"pppoe 1 nat enable user {usuario} password {contraseña}",
            f"vlan port eth_0/1 mode tag vlan 1{olt} pri 2",
            f"vlan port eth_0/2 mode tag vlan 3{olt} pri 5",
            f"vlan port eth_0/3 mode tag vlan 3{olt} pri 5",
            f"vlan port eth_0/4 mode tag vlan 3{olt} pri 5",
            f"vlan port wifi_0/1 mode tag vlan 1{olt} pri 2",
            f"vlan port wifi_0/5 mode tag vlan 1{olt} pri 2",
            "dhcp-ip ethuni eth_0/1 from-onu",
            "dhcp-ip ethuni eth_0/2 from-internet",
            "dhcp-ip ethuni eth_0/3 from-internet",
            "dhcp-ip ethuni eth_0/4 from-internet",
            "security-mgmt 1 state enable ingress-type lan",
            "security-mgmt 2 state enable mode forward",
            "security-mgmt 2 start-src-ip 190.13.224.2 end-src-ip 190.13.224.2"
            ]
            
            # Ejecutar los comandos
            await ejecutar_comandos(writer, reader, comandos)
            
        elif contador_vlans == 4:
            # Lista de comandos a ejecutar
            comandos = [
            "!",
            f"pon-onu-mng gpon-onu_{puerto}:{posicion}",
            f"service ppp gemport 1 iphost 1 cos 2 vlan 1{olt}",
            f"service iptv gemport 2 cos 5 vlan 3{olt}",
            f"pppoe 1 nat enable user {usuario} password {contraseña}",
            f"vlan port eth_0/1 mode tag vlan 3{olt} pri 5",
            f"vlan port eth_0/2 mode tag vlan 3{olt} pri 5",
            f"vlan port eth_0/3 mode tag vlan 3{olt} pri 5",
            f"vlan port eth_0/4 mode tag vlan 3{olt} pri 5",
            f"vlan port wifi_0/1 mode tag vlan 1{olt} pri 2",
            f"vlan port wifi_0/5 mode tag vlan 1{olt} pri 2",
            "dhcp-ip ethuni eth_0/1 from-internet",
            "dhcp-ip ethuni eth_0/2 from-internet",
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
            f"pppoe 1 nat enable user {usuario} password {contraseña}",
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
            
        mostrar_texto("CONFIGURACION FINALIZADA")
    except Exception as e:
        return f"Error: {e}"
    
    
async def eliminar_posicion_anterior():
    olt = olt_entry_1.get()
    puerto = puerto_entry_1.get()
    posicion = posicion_entry_1.get()
        
    num_olt = olt[:1] + "." + olt[1:]

    if olt == "121" or olt == "122" or olt == "123":
        host = f"10.225.{num_olt}"
    elif olt == "321" or olt == "322" or olt == "323" or olt == "521" or olt == "221" or olt == "222":
        host = f"10.253.{num_olt}"
    port = 23
    username = "zte"
    password = "zte"
    
    try:
        # Crear una conexión Telnet
        reader, writer = await telnetlib3.open_connection(host, port)
        # Esperar a que aparezca el prompt de inicio de sesión
        await asyncio.wait_for(reader.read(1000), timeout=2)
        writer.write(username + "\n")
        # Esperar a que aparezca el prompt de contraseña
        await asyncio.wait_for(reader.read(1000), timeout=2)
        writer.write(password + "\n")
        
        # Leer hasta que se encuentre el delimitador "#"
        await reader.readuntil(b"#")
        comandos = [
            "config t",
            f"interface gpon-olt_{puerto}",
            f"no onu {posicion}"]
        
        # Ejecutar los comandos
        await ejecutar_comandos(writer, reader, comandos)
    
        output_text.insert(tk.END, "ONU Eliminada \n")
            
    except Exception as e:
        return f"Error: {e}"
    
def no_datos():    
    output_text.config(state=tk.NORMAL)  # Habilitar la edición del Text widget
    output_text.delete("1.0", tk.END)    # Limpiar el Text widget
    output_text.insert(tk.END, f"No se encuentran datos\n")
    output_text.see(tk.END)
    
# Función para mostrar el texto en la ventana
def mostrar_datos():
    output_text.config(state=tk.NORMAL)  # Habilitar la edición del Text widget
    output_text.insert(tk.END, f"Nombre: {nombre}\n")
    output_text.insert(tk.END, f"Teléfono: {telefono}\n")
    output_text.insert(tk.END, f"SN: {serial_number}\n")
    output_text.insert(tk.END, f"Usuario: {usuario}\n")
    output_text.insert(tk.END, f"Contraseña: {contraseña}\n")
    output_text.insert(tk.END, f"Vlans IPTV: {contador_vlans}\n")
    output_text.insert(tk.END, "\n")
    output_text.see(tk.END)
    
# Función para mostrar el texto en la ventana
def mostrar_texto(texto):
    output_text.config(state=tk.NORMAL)  # Habilitar la edición del Text widget
    output_text.insert(tk.END, f"{texto}\n")
    output_text.see(tk.END)
    
async def on_connect():
    olt_1 = olt_entry_1.get()
    puerto_1 = puerto_entry_1.get()
    posicion_1 = posicion_entry_1.get()
    olt_2 = olt_entry_2.get()
    puerto_2 = puerto_entry_2.get()
    posicion_2 = posicion_entry_2.get()
    await main(olt_1, puerto_1, posicion_1, olt_2, puerto_2, posicion_2)
    
async def ver_datos2():
    olt_2 = olt_entry_2.get()
    puerto_2 = puerto_entry_2.get()
    posicion_2 = posicion_entry_2.get()
    await telnet_to_olt(olt_2, puerto_2, posicion_2)
    
async def ver_datos():
    olt_1 = olt_entry_1.get()
    puerto_1 = puerto_entry_1.get()
    posicion_1 = posicion_entry_1.get()
    await telnet_to_olt(olt_1, puerto_1, posicion_1)
    
def datos2():
    # Ejecutar la función on_connect en un hilo separado
    thread = threading.Thread(target=run_async_function, args=(ver_datos2,))
    thread.start()
    
def datos1():
    # Ejecutar la función on_connect en un hilo separado
    thread = threading.Thread(target=run_async_function, args=(ver_datos,))
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

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)
        
def limpiar_ventana():
    output_text.delete('1.0', tk.END)
    
def limpiar_datos():
    olt_entry_1.delete(0, tk.END)
    puerto_entry_1.delete(0, tk.END)
    posicion_entry_1.delete(0, tk.END)
    olt_entry_2.delete(0, tk.END)
    puerto_entry_2.delete(0, tk.END)
    posicion_entry_2.delete(0, tk.END)
    
    
# Ejecutar la función
async def main(olt_1, puerto_1, posicion_1, olt_2, puerto_2, posicion_2):
    await telnet_to_olt(olt_1, puerto_1, posicion_1)
    await telnet_to_olt2(olt_2, puerto_2, posicion_2)
    

root = tk.Tk()

# Configurar el icono
icon_path = "C:/Users/Grosso Quimey/Desktop/APP Python/APP OLT Telnet/APP Migracion 1.3/IPTV.ico"
try:
    root.iconbitmap(default=icon_path)
except tk.TclError as e:
    print(f"Error al configurar el icono: {e}")
    
root.title("APP MIGRACION")

# Configurar el tamaño de la ventana
root.geometry("550x480")

# Configurar el estilo del tema
style = ttk.Style()
style.theme_use("clam")

# Configurar colores y fuentes personalizadas
root.configure(bg="#2E3B4E")

# Marco para la sección de OLT Inicial
frame_olt_inicial = tk.Frame(root, bg="#2E3B4E")
frame_olt_inicial.grid(row=0, column=0, padx=10, pady=10)

label_1 = tk.Label(frame_olt_inicial, text="OLT Inicial", font=("Arial", 12), fg="white", bg="#2E3B4E")
label_1.grid(row=0, column=0, padx=5, pady=5)

# Aquí van los widgets para la entrada de datos de la OLT Inicial
olt_label_1 = tk.Label(frame_olt_inicial, text="OLT:", font=("Arial", 12), fg="white", bg="#2E3B4E")
olt_label_1.grid(row=1, column=0, padx=5, pady=5)
olt_entry_1 = tk.Entry(frame_olt_inicial)
olt_entry_1.grid(row=1, column=1, padx=5, pady=5)

puerto_label_1 = tk.Label(frame_olt_inicial, text="Puerto:", font=("Arial", 12), fg="white", bg="#2E3B4E")
puerto_label_1.grid(row=2, column=0, padx=5, pady=5)
puerto_entry_1 = tk.Entry(frame_olt_inicial)
puerto_entry_1.grid(row=2, column=1, padx=5, pady=5)

posicion_label_1 = tk.Label(frame_olt_inicial, text="Posición:", font=("Arial", 12), fg="white", bg="#2E3B4E")
posicion_label_1.grid(row=3, column=0, padx=5, pady=5)
posicion_entry_1 = tk.Entry(frame_olt_inicial)
posicion_entry_1.grid(row=3, column=1, padx=5, pady=5)

# Marco para la sección de OLT Destino
frame_olt_destino = tk.Frame(root, bg="#2E3B4E")
frame_olt_destino.grid(row=0, column=1, padx=10, pady=10)

label_2 = tk.Label(frame_olt_destino, text="OLT Destino", font=("Arial", 12), fg="white", bg="#2E3B4E")
label_2.grid(row=0, column=0, padx=5, pady=5)

# Aquí van los widgets para la entrada de datos de la OLT Destino
olt_label_2 = tk.Label(frame_olt_destino, text="OLT:", font=("Arial", 12), fg="white", bg="#2E3B4E")
olt_label_2.grid(row=1, column=0, padx=5, pady=5)
olt_entry_2 = tk.Entry(frame_olt_destino)
olt_entry_2.grid(row=1, column=1, padx=5, pady=5)

puerto_label_2 = tk.Label(frame_olt_destino, text="Puerto:", font=("Arial", 12), fg="white", bg="#2E3B4E")
puerto_label_2.grid(row=2, column=0, padx=5, pady=5)
puerto_entry_2 = tk.Entry(frame_olt_destino)
puerto_entry_2.grid(row=2, column=1, padx=5, pady=5)

posicion_label_2 = tk.Label(frame_olt_destino, text="Posición:", font=("Arial", 12), fg="white", bg="#2E3B4E")
posicion_label_2.grid(row=3, column=0, padx=5, pady=5)
posicion_entry_2 = tk.Entry(frame_olt_destino)
posicion_entry_2.grid(row=3, column=1, padx=5, pady=5)

connect_button1 = tk.Button(root, text="Migrar", command=connect, bg="gray", fg="white", font=("Arial", 12), padx=10, pady=5, relief="solid", borderwidth=1)
connect_button1.grid(row=1, column=0, columnspan=2, padx=(10,5), pady=10)

connect_button2 = tk.Button(root, text="Datos OLT1", command=datos1, bg="gray", fg="white", font=("Arial", 12), padx=10, pady=5, relief="solid", borderwidth=1)
connect_button2.grid(row=1, column=0, padx=5, pady=10)

connect_button3 = tk.Button(root, text="Datos OLT2", command=datos2, bg="gray", fg="white", font=("Arial", 12), padx=10, pady=5, relief="solid", borderwidth=1)
connect_button3.grid(row=1, column=1, padx=5, pady=10)

# Botón para limpiar la ventana de salida de datos
limpiar_button = tk.Button(root, text="Limpiar Ventana", command=limpiar_ventana, bg="gray", fg="white", font=("Arial", 12), padx=10, pady=5, relief="solid", borderwidth=1)
limpiar_button.grid(row=3, column=0, columnspan=2, pady=10)

# Botón para limpiar la entrada de datos
limpiar_datos_button = tk.Button(root, text="Limpiar Datos", command=limpiar_datos, bg="gray", fg="white", font=("Arial", 12), padx=10, pady=5, relief="solid", borderwidth=1)
limpiar_datos_button.grid(row=3, column=1, columnspan=2, pady=10)

eliminar_posicion_anterior_button = tk.Button(root, text="Elim. Pos. Ant.", command=lambda: asyncio.run(eliminar_posicion_anterior()), bg="gray", fg="white", font=("Arial", 12), padx=10, pady=5, relief="solid", borderwidth=1)
eliminar_posicion_anterior_button.grid(row=3, column=0, columnspan=1, pady=10)

# Ventana de salida de datos
output_text = tk.Text(root, height=10, width=50, bg="white", fg="black", font=("Arial", 12))
output_text.grid(row=2, column=0, columnspan=2, pady=10)
output_text.bind("<Key>", ignore_keypress) # Ignora entrada por teclado
output_text.bind("<Control-c>", copy_text) # Habilita opcion de copiado

# Crear menú contextual para copiar y pegar
context_menu = Menu(root, tearoff=0)
context_menu.add_command(label="Copy", command=lambda: root.event_generate("<Control-c>"))

output_text.bind("<Button-3>", show_context_menu)  # Botón derecho para mostrar el menú contextual

# Barra de desplazamiento
scrollbar = Scrollbar(root, command=output_text.yview)
scrollbar.grid(row=2, column=6, sticky="ns")
output_text.config(yscrollcommand=scrollbar.set)

# Configuración de pesos para que los widgets se expandan correctamente
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(0, weight=1)

root.mainloop()