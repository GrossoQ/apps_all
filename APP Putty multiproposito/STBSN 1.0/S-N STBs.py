import tkinter as tk
from tkinter import Label, Entry, Button, Text, Scrollbar
import paramiko

class SSHConnection:
    def __init__(self, ip, user, password):
        self.ip = ip
        self.user = user
        self.password = password
        self.client = None
        self.connection = None

    def connect(self):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.ip, username=self.user, password=self.password)
            self.connection = True
            return "Conexión exitosa."
        except paramiko.AuthenticationException:
            return "Error de autenticación. Verifica el usuario y la contraseña."
        except paramiko.SSHException as e:
            return f"Error de conexión: {str(e)}"
        except Exception as e:
            return f"Error desconocido: {str(e)}"

    def disconnect(self):
        if self.connection:
            self.client.close()

    def execute_command(self, command):
        if self.connection:
            try:
                stdin, stdout, stderr = self.client.exec_command(command)
                output = stdout.read().decode('utf-8')
                return output
            except paramiko.SSHException as e:
                return f"Error al ejecutar el comando: {str(e)}"
            except Exception as e:
                return f"Error desconocido al ejecutar el comando: {str(e)}"
        else:
            return "No hay conexión establecida."

def on_connect(ip, user, password):
    result_text.insert(tk.END, "Conectando...\n")
    connect_button.config(state=tk.DISABLED)
    root.update()

    global ssh
    ssh = SSHConnection(ip, user, password)
    result_text.insert(tk.END, ssh.connect() + "\n")

    connect_button.config(state=tk.NORMAL)
    root.update()

def clear_output():
    result_text.delete(1.0, tk.END)

# Nuevas funciones para los botones
def connect_amino():
    ip = command_entry.get()
    command = f"ssh-keyscan -H {ip} >> ~/.ssh/known_hosts"
    result_text.insert(tk.END, f"Ejecutando comando: {command}\n")
    output = ssh.execute_command(command)
    result_text.insert(tk.END, f"Salida:\n{output}\n")

def get_sn_amino():
    ip = command_entry.get()
    command = f"ssh {ip} libconfig-get NORFLASH.SERIAL_ID"
    result_text.insert(tk.END, f"Ejecutando comando: {command}\n")
    output = ssh.execute_command(command)
    result_text.insert(tk.END, f"Salida:\n{output}\n")

def get_sn_kamai():
    ip = command_entry.get()
    command = f"ssh {ip} -p 10022 -i /root/.ssh/id_rsa_entone -o 'CheckHostIP=no' -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no 'cd diag/general/; cat status'"
    result_text.insert(tk.END, f"Ejecutando comando: {command}\n")
    output = ssh.execute_command(command)
    result_text.insert(tk.END, f"Salida:\n{output}\n")

# Establecer credenciales predeterminadas
default_ip = "172.30.159.7"
default_user = "root"
default_password = "pontis2017"

# Crear la ventana principal
root = tk.Tk()
root.title("SSH Connection")

# Crear y colocar widgets en la ventana
input_frame = tk.Frame(root)
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

label_ip = Label(input_frame, text="IP:")
label_ip.grid(row=0, column=0, padx=10, pady=10)

entry_ip = Entry(input_frame)
entry_ip.grid(row=0, column=1, padx=10, pady=10)
entry_ip.insert(0, default_ip)  # Establecer valor predeterminado

label_user = Label(input_frame, text="Usuario:")
label_user.grid(row=1, column=0, padx=10, pady=10)

entry_user = Entry(input_frame)
entry_user.grid(row=1, column=1, padx=10, pady=10)
entry_user.insert(0, default_user)  # Establecer valor predeterminado

label_password = Label(input_frame, text="Contraseña:")
label_password.grid(row=2, column=0, padx=10, pady=10)

entry_password = Entry(input_frame, show="*")
entry_password.grid(row=2, column=1, padx=10, pady=10)
entry_password.insert(0, default_password)  # Establecer valor predeterminado

# Cambiar el texto del botón
connect_button = Button(root, text="Conectar Multipropósito", command=lambda: on_connect(entry_ip.get(), entry_user.get(), entry_password.get()))
connect_button.grid(row=1, column=0, pady=10)

label_command = Label(root, text="IP STB:")
label_command.grid(row=0, column=2, padx=10, pady=10)

command_entry = Entry(root)
command_entry.grid(row=0, column=3, padx=10, pady=10)

# Botones nuevos
connect_amino_button = Button(root, text="Conectar Amino", command=connect_amino)
connect_amino_button.grid(row=1, column=3, pady=10)

get_sn_amino_button = Button(root, text="Obtener S/N Amino", command=get_sn_amino)
get_sn_amino_button.grid(row=1, column=4, pady=10)

get_sn_kamai_button = Button(root, text="Obtener S/N Kamai/Aria", command=get_sn_kamai)
get_sn_kamai_button.grid(row=1, column=5, pady=10)

# Botón para limpiar la ventana
clear_button = Button(root, text="Limpiar Ventana", command=clear_output)
clear_button.grid(row=2, column=2, pady=10)

# Ventana para mostrar resultados
result_text = Text(root, height=15, width=50)
result_text.grid(row=3, column=0, columnspan=6, padx=10, pady=10)

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