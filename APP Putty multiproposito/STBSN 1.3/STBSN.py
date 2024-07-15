import tkinter as tk
from tkinter import ttk
from tkinter import Label, Entry, Button, Text, Scrollbar, Tk, Text, Menu, Frame
import paramiko
import threading

class SSHConnection:
    def __init__(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.password = password
        self.client = None
        self.connection = False

    def connect(self):
        # Revisar si el cliente ya está conectado
        if ssh.connection:
            result_text.insert(tk.END, "YA CONECTADO AL SERVIDOR.\n")
            return
            # Ya existe una conexión establecida, no hacer nada
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.ip, username=self.user, password=self.password)
            self.connection = True
            result_text.see(tk.END)  # Hacer que la barra de desplazamiento se mueva hacia abajo
            return "CONEXION EXITOSA."
        except paramiko.AuthenticationException:
            return "Error de autenticación. Verifica el usuario y la contraseña."
        except paramiko.SSHException as e:
            return f"Error de conexión: {str(e)}"
        except Exception as e:
            return f"Error desconocido: {str(e)}"

    def disconnect(self):
        global ssh
        if ssh.client:
            ssh.client.close()
            ssh = None
            print("CONEXIÓN CERRADA")

    def execute_command(self, command):
        if self.connection:
            try:
                def timeout():
                    self.client.exec_command("kill -9 $PPID")  # Detener el proceso en el servidor
                temporizador = threading.Timer(3, timeout)  # Temporizador de 3 segundos
                stdin, stdout, stderr = self.client.exec_command(command)

                # Iniciar el temporizador
                temporizador.start()
                output = stdout.read().decode('utf-8')

                # Cancelar el temporizador ya que el proceso ha terminado
                temporizador.cancel()

                return output
            except paramiko.SSHException as e:
                return f"Error de IP, VUELVE A CONECTAR CON EL SERVIDOR, REVISE QUE LA IP SEA CORRECTA, O QUE EL STB TENGA CONEXION."
            except Exception as e:
                return f"Error desconocido al ejecutar el comando: {str(e)}"
        else:
            return "No hay conexión establecida."

def on_connect(ip, user, password):
    result_text.see(tk.END)  # Hacer que la barra de desplazamiento se mueva hacia abajo
    root.update()

    global ssh
    ssh = SSHConnection(ip, user, password)
    result_text.insert(tk.END, ssh.connect() + "\n")

def clear_output():
    result_text.delete(1.0, tk.END)


# Nuevas funciones para los botones   
def get_sn_amino():
    try:
        ip = command_entry.get()
        if not ip:
            result_text.insert(tk.END, "Error: Ingresa una IP antes de conectar.\n")
            return
        # Verificar si la conexión SSH está establecida
        if not ssh.connection:
            result_text.insert(tk.END, "Error: Debes establecer la conexión antes de ejecutar comandos SSH.\n")
            return

        command = f"ssh-keyscan -H {ip} >> ~/.ssh/known_hosts"
        result_text.insert(tk.END, f"EJECUTANDO COMANDO: {command}\n")
        output = ssh.execute_command(command)
        command = f"ssh {ip} libconfig-get NORFLASH.SERIAL_ID"
        result_text.insert(tk.END, f"EJECUTANDO COMANDO: {command}\n")
        output = ssh.execute_command(command)
        result_text.insert(tk.END, f"SALIDA:\n{output}\n")
        result_text.see(tk.END)  # Hacer que la barra de desplazamiento se mueva hacia abajo

    except NameError:
        result_text.insert(tk.END, "Error de conexión: Asegúrate de establecer la conexión.\n")
    
def get_sn_kamai():
    try:
        ip = command_entry.get()  # Obtener la IP desde el Entry
        if not ip:
            result_text.insert(tk.END, "Error: Ingresa una IP antes de conectar.\n")
            return

        # Verificar si la conexión SSH está establecida
        if not ssh.connection:
            result_text.insert(tk.END, "Error: Debes establecer la conexión antes de ejecutar comandos SSH.\n")
            return

        ip = command_entry.get()
        command = f"ssh {ip} -p 10022 -i /root/.ssh/id_rsa_entone -o 'CheckHostIP=no' -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no 'cd diag/general/; cat status'"
        result_text.insert(tk.END, f"EJECUTANDO COMANDO: {command}\n")
        output = ssh.execute_command(command)
        result_text.insert(tk.END, f"SALIDA:\n{output}\n")
        result_text.see(tk.END)  # Hacer que la barra de desplazamiento se mueva hacia abajo

    except NameError:
        result_text.insert(tk.END, "Error de conexión: Asegúrate de establecer la conexión.\n")


# Nuevas funciones para los ventana de impresion
def ignore_keypress(event):
    return "break"

def copy_text(event):
    selected_text = result_text.get("sel.first", "sel.last")
    root.clipboard_clear()
    root.clipboard_append(selected_text)

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

# Establecer credenciales predeterminadas
default_ip = "172.30.159.7"
default_user = "root"
default_password = "pontis2017"


# Crear la ventana principal
root = tk.Tk()
# Configurar el icono
icon_path = "C:/Users/Grosso Quimey/Desktop/APP Python/APP Putty multiproposito/STBSN 1.3/iptv-icon.ico"
try:
    root.iconbitmap(default=icon_path)
except tk.TclError as e:
    print(f"Error al configurar el icono: {e}")
# Configurar el título de la ventana
root.title("STB SN")

# Configurar el estilo del tema
style = ttk.Style()
style.theme_use("clam")  # Puedes cambiar "clam" a otros temas disponibles (aquí uso "clam" como ejemplo)

# Configurar colores y fuentes personalizadas
root.configure(bg="#2E3B4E")  # Fondo de la ventana

# Crear y colocar widgets en la ventana
input_frame = tk.Frame(root, bg="#2E3B4E")
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

label_ip = Label(input_frame, text="IP:", font=("Arial", 12), fg="white", background="#2E3B4E")
label_ip.grid(row=0, column=0, padx=10, pady=10)

entry_ip = Entry(input_frame)
entry_ip.grid(row=0, column=1, padx=10, pady=10)
entry_ip.insert(0, default_ip)  # Establecer valor predeterminado

label_user = Label(input_frame, text="Usuario:", font=("Arial", 12), fg="white", background="#2E3B4E")
label_user.grid(row=1, column=0, padx=10, pady=10)

entry_user = Entry(input_frame)
entry_user.grid(row=1, column=1, padx=10, pady=10)
entry_user.insert(0, default_user)  # Establecer valor predeterminado

label_password = Label(input_frame, text="Contraseña:", font=("Arial", 12), fg="white", background="#2E3B4E")
label_password.grid(row=2, column=0, padx=10, pady=10)

entry_password = Entry(input_frame, show="*")
entry_password.grid(row=2, column=1, padx=10, pady=10)
entry_password.insert(0, default_password)  # Establecer valor predeterminado

# Cambiar el texto del botón
connect_button = Button(root, text="Conectar Multipropósito", bg="gray", fg="white", font=("Arial", 12), padx=1, pady=1, relief="solid", borderwidth=1, command=lambda: on_connect(entry_ip.get(), entry_user.get(), entry_password.get()))
connect_button.grid(row=1, column=0, pady=10)

label_command = Label(root, text="IP STB:", font=("Arial", 12), fg="white", background="#2E3B4E")
label_command.grid(row=0, column=2, padx=10, pady=10)

command_entry = Entry(root)
command_entry.grid(row=0, column=3, padx=10, pady=10)

# Botones nuevos
get_sn_amino_button = Button(root, text="Obtener S/N Amino", command=get_sn_amino, bg="gray", fg="white", font=("Arial", 12), padx=1, pady=1, relief="solid", borderwidth=1)
get_sn_amino_button.grid(row=1, column=3, pady=10)

get_sn_kamai_button = Button(root, text="Obtener S/N Kamai/Aria", command=get_sn_kamai, bg="gray", fg="white", font=("Arial", 12), padx=1, pady=1, relief="solid", borderwidth=1)
get_sn_kamai_button.grid(row=1, column=2, pady=10)

# Botón para limpiar la ventana
clear_button = Button(root, text="Limpiar Ventana", command=clear_output, bg="gray", fg="white", font=("Arial", 12), padx=1, pady=1, relief="solid", borderwidth=1)
clear_button.grid(row=2, column=2, pady=10)

# Ventana para mostrar resultados
result_text = Text(root, height=15, width=50)
result_text.grid(row=3, column=0, columnspan=4, padx=10, pady=10)
result_text.bind("<Key>", ignore_keypress) # Ignora entrada por teclado
result_text.bind("<Control-c>", copy_text) # Habilita opcion de copiado

# Crear menú contextual para copiar y pegar
context_menu = Menu(root, tearoff=0)
context_menu.add_command(label="Copy", command=lambda: root.event_generate("<Control-c>"))

result_text.bind("<Button-3>", show_context_menu)  # Botón derecho para mostrar el menú contextual

# Barra de desplazamiento
scrollbar = Scrollbar(root, command=result_text.yview)
scrollbar.grid(row=3, column=6, sticky="ns")
result_text.config(yscrollcommand=scrollbar.set)

# Configuración de pesos para que los widgets se expandan correctamente
root.grid_rowconfigure(3, weight=1)
root.grid_columnconfigure(0, weight=1)

# Iniciar el bucle principal
root.mainloop()

# Asegurarse de cerrar la conexión al salir
if 'ssh' in globals():
    ssh.disconnect()