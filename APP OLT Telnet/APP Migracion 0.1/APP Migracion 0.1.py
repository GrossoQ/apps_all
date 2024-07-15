import asyncio
import telnetlib3
import re

async def telnet_to_olt(): # OLT Inicial
    olt = "122"
    puerto = "1/3/4"
    posicion = "8"
    
    num_olt = f"{int(olt[0])}.{int(olt[1:])}"

    host = f"10.225.{num_olt}"
    port = 23
    username = "zte"
    password = "zte"
    

    try:
        global nombre, telefono, serial_number, usuario, contraseña, contador_vlans
        
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
            return print("No se encontraron datos.")
        
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
            return print("No se encontraron datos.")
        
        # Ejecuta comando usuario contraseña
        writer.write(f"show onu running config gpon-onu_{puerto}:{posicion}" + "\n")
        # Leer hasta que se encuentre el delimitador "#"
        data = await reader.readuntil(b"#")
        # Decodificar los datos leídos como una cadena
        datos_str = data.decode()
        # Definimos los patrones de expresión regular para buscar el usuario y la contraseña
        patron_usuario = r"pppoe \d+ nat enable user (\w+)"
        patron_contraseña = r"pppoe \d+ nat enable user \w+ password (\w+)"
        # Definimos el patrón de expresión regular para buscar las VLAN
        patron_vlan = r"vlan port eth_0/\d+ mode tag vlan (\d+)"
        # Buscamos el patrón en la salida
        resultado_usuario = re.search(patron_usuario, datos_str)
        resultado_contraseña = re.search(patron_contraseña, datos_str)

        # Si se encuentra el patrón, guardamos el usuario y la contraseña en variables
        if resultado_usuario and resultado_contraseña:
            usuario = resultado_usuario.group(1)
            contraseña = resultado_contraseña.group(1)
        else:
            return print("No se encontraron datos.")
        
        # Contamos las VLAN dentro de la parte indicada de la salida
        vlans = re.findall(patron_vlan, datos_str)
        contador_vlans = sum(3000 <= int(vlan) <= 3999 for vlan in vlans)
        
        return print("Nombre:", nombre, "Teléfono:", telefono, "SN:", serial_number, "Usuario:", usuario, "Contraseña:", contraseña, "Vlans IPTV:", contador_vlans)

    except Exception as e:
        return f"Error: {e}"
    

async def enviar_comando(writer, reader, comando):
    writer.write(comando + "\n")
    await reader.readuntil(b"#")

async def ejecutar_comandos(writer, reader, comandos):
    for comando in comandos:
        await enviar_comando(writer, reader, comando)    
    

async def telnet_to_olt2(): # OLT Destino
    olt = "122"
    puerto = "1/17/3"
    posicion = "5"
    
    num_olt = f"{int(olt[0])}.{int(olt[1:])}"

    host = f"10.225.{num_olt}"
    port = 23
    username = "zte"
    password = "zte"
    
    try:
        # Crear una conexión Telnet
        reader, writer = await telnetlib3.open_connection(host, port)
        # Esperar a que aparezca el prompt de inicio de sesión
        await asyncio.wait_for(reader.read(1000), timeout=1)
        writer.write(username + "\n")
        # Esperar a que aparezca el prompt de contraseña
        await asyncio.wait_for(reader.read(1000), timeout=1)
        writer.write(password + "\n")
        
        # Leer hasta que se encuentre el delimitador "#"
        print (await reader.readuntil(b"#"))
        
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
            "!",
            f"igmp  mvlan 3{olt} receive-port gpon-onu_{puerto}:{posicion} vport 2",
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
            f"pppoe 1 nat enable user {nombre} password {contraseña}"
            "!",
            f"igmp  mvlan 3{olt} receive-port gpon-onu_{puerto}:{posicion} vport 2",
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
            "!",
            f"igmp  mvlan 3{olt} receive-port gpon-onu_{puerto}:{posicion} vport 2",
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
            "!",
            f"igmp  mvlan 3{olt} receive-port gpon-onu_{puerto}:{posicion} vport 2",
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
            "!",
            f"igmp  mvlan 3{olt} receive-port gpon-onu_{puerto}:{posicion} vport 2"
            ]
            
            # Ejecutar los comandos
            await ejecutar_comandos(writer, reader, comandos)
            
        print(f"pppoe 1 nat enable user {usuario} password {contraseña}")
        
    except Exception as e:
        return f"Error: {e}"
    

# Ejecutar la función
async def main():
    # Llamar a las funciones de conexión Telnet
    await telnet_to_olt()
    await telnet_to_olt2()

# Ejecutar la función principal
asyncio.run(main())