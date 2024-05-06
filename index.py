import tkinter as tk
from tkinter import messagebox
from tkinter import simpledialog
from tkinter import font
import pywhatkit as pw
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import threading
import pandas as pd

class Usuario:
    def __init__(self, nombre, apellido, correo, telefono):
        self.nombre = nombre
        self.apellido = apellido
        self.correo = correo
        self.telefono = telefono

class Programa:
    def __init__(self):
        self.usuarios = []
        self.cargar_usuarios()

    def cargar_usuarios(self):
        archivo_existe = True
        try:
            df = pd.read_csv('usuarios.txt')
        except FileNotFoundError:
            archivo_existe = False

        if archivo_existe:
            if 'Nombre' in df.columns and 'Apellido' in df.columns and 'Correo' in df.columns and 'Telefono' in df.columns:
                for _, row in df.iterrows():
                    self.usuarios.append(Usuario(row['Nombre'], row['Apellido'], row['Correo'], row['Telefono']))
            else:
                print("El archivo 'usuarios.txt' no tiene el formato esperado.")

    def guardar_usuario(self, usuario):
        with open('usuarios.txt', 'a') as file:
            file.write(f"{usuario.nombre},{usuario.apellido},{usuario.correo},{usuario.telefono}\n")

    def agregar_usuario(self, nombre, apellido, correo, telefono):
        if self.validar_datos(nombre, apellido, correo, telefono):
            if not self.buscar_usuario_por_correo(correo):
                usuario = Usuario(nombre, apellido, correo, telefono)
                self.usuarios.append(usuario)
                self.guardar_usuario(usuario)
                threading.Thread(target=self.enviar_mensaje_whatsapp, args=(usuario,)).start()
                threading.Thread(target=self.enviar_correo, args=(usuario,)).start()
                messagebox.showinfo("Éxito", "Usuario registrado correctamente.")
            else:
                messagebox.showerror("Error", "El correo ya está registrado.")
        else:
            messagebox.showerror("Error", "Por favor, ingrese datos válidos.")

    def validar_datos(self, nombre, apellido, correo, telefono):
        if nombre and apellido and correo and telefono:
            return True
        return False

    def buscar_usuario_por_correo(self, correo):
        for usuario in self.usuarios:
            if usuario.correo == correo:
                return usuario
        return None

    def eliminar_usuario_por_correo(self, correo):
        usuario = self.buscar_usuario_por_correo(correo)
        if usuario:
            self.usuarios.remove(usuario)
            self.actualizar_archivo()
            messagebox.showinfo("Éxito", "Usuario eliminado correctamente.")
        else:
            messagebox.showerror("Error", "El correo no está registrado.")

    def actualizar_archivo(self):
        df = pd.DataFrame([(u.nombre, u.apellido, u.correo, u.telefono) for u in self.usuarios],
                          columns=['Nombre', 'Apellido', 'Correo', 'Telefono'])
        df.to_csv('usuarios.txt', index=False)

    def enviar_mensaje_whatsapp(self, usuario):
        mensaje = f"Bienvenido {usuario.nombre} {usuario.apellido}!"
        pw.sendwhatmsg_instantly(usuario.telefono, mensaje)
    
    def enviar_correo(self, usuario):
        email = 'tu_correo@gmail.com'
        password = 'tu_contraseña'

        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = usuario.correo
        msg['Subject'] = 'Bienvenido'

        body = f"Bienvenido {usuario.nombre} {usuario.apellido}!"
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)
        text = msg.as_string()
        server.sendmail(email, usuario.correo, text)
        server.quit()

class Interfaz:
    def __init__(self, programa):
        self.programa = programa
        self.ventana = tk.Tk()
        self.ventana.title("Registro de Usuarios")

        self.frame = tk.Frame(self.ventana)
        self.frame.pack(padx=20, pady=20)
        self.ventana.geometry("600x400")

        font_size = font.Font(size=15)
        self.label_nombre = tk.Label(self.frame, text="Nombre:", font=font_size)
        self.label_nombre.grid(row=0, column=0, padx=5, pady=5)
        self.entry_nombre = tk.Entry(self.frame, font=font_size)
        self.entry_nombre.grid(row=0, column=1, padx=5, pady=5)

        self.label_apellido = tk.Label(self.frame, text="Apellido:", font=font_size)
        self.label_apellido.grid(row=1, column=0, padx=5, pady=5)
        self.entry_apellido = tk.Entry(self.frame, font=font_size)
        self.entry_apellido.grid(row=1, column=1, padx=5, pady=5)

        self.label_correo = tk.Label(self.frame, text="Correo:", font=font_size)
        self.label_correo.grid(row=2, column=0, padx=5, pady=5)
        self.entry_correo = tk.Entry(self.frame, font=font_size)
        self.entry_correo.grid(row=2, column=1, padx=5, pady=5)

        self.label_telefono = tk.Label(self.frame, text="Teléfono:", font=font_size)
        self.label_telefono.grid(row=3, column=0, padx=5, pady=5)
        self.entry_telefono = tk.Entry(self.frame, font=font_size)
        self.entry_telefono.grid(row=3, column=1, padx=5, pady=5)

        #botones para agregar, eliminar y asi
        self.boton_agregar = tk.Button(self.frame, text="Agregar Usuario", command=self.agregar_usuario)
        self.boton_agregar.grid(row=4, column=0,  padx=1, pady=5, sticky="WE")

        self.boton_listar = tk.Button(self.frame, text="Listar Usuarios", command=self.listar_usuarios)
        self.boton_listar.grid(row=4, column=2,  padx=1, pady=5, sticky="WE")

        self.boton_buscar = tk.Button(self.frame, text="Buscar Usuario", command=self.buscar_usuario)
        self.boton_buscar.grid(row=5, column=2,  padx=1, pady=5, sticky="WE")

        self.boton_eliminar = tk.Button(self.frame, text="Eliminar Usuario", command=self.eliminar_usuario)
        self.boton_eliminar.grid(row=5, column=0,  padx=1, pady=5, sticky="WE")

        self.boton_detener = tk.Button(self.frame, text="Detener Programa", command=self.ventana.quit)
        self.boton_detener.grid(row=7, column=1,  padx=1, pady=5, sticky="WE")

    def agregar_usuario(self):
        nombre = self.entry_nombre.get()
        apellido = self.entry_apellido.get()
        correo = self.entry_correo.get()
        telefono = self.entry_telefono.get()
        self.programa.agregar_usuario(nombre, apellido, correo, telefono)

    def listar_usuarios(self):
        usuarios = '\n'.join([f"{u.nombre.capitalize()} {u.apellido.capitalize()} - {u.correo} - {u.telefono}" for u in self.programa.usuarios])
        messagebox.showinfo("Usuarios Registrados", usuarios)

    def buscar_usuario(self):
        correo = simpledialog.askstring("Buscar Usuario", "Ingrese el correo del usuario a buscar:")
        if correo:
            usuario = self.programa.buscar_usuario_por_correo(correo)
            if usuario:
                messagebox.showinfo("Usuario Encontrado", f"{usuario.nombre} {usuario.apellido} - {usuario.telefono}")
            else:
                messagebox.showerror("Error", "Usuario no encontrado.")

    def eliminar_usuario(self):
        correo = simpledialog.askstring("Eliminar Usuario", "Ingrese el correo del usuario a eliminar:")
        if correo:
            self.programa.eliminar_usuario_por_correo(correo)

    def run(self):
        self.ventana.mainloop()

programa = Programa()
interfaz = Interfaz(programa)
interfaz.run()
