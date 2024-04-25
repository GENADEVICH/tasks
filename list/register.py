import customtkinter
import mysql.connector
from tkinter import messagebox
import subprocess

conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="12345678",
        database="task"
    )
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(255),
                    password VARCHAR(255)
                )''')
conn.commit()

def register():
    username = entry1.get()
    password = entry2.get()

    cursor.execute('''INSERT INTO users (username, password) VALUES (%s, %s)''',
                   (username, password))
    conn.commit()

    messagebox.showinfo("Успех", "Регистрация прошла успешно")

    print("Зарегистрирован")

def avtotis():
    global current_user 
    username = entry3.get()
    password = entry4.get()

  
    cursor.execute('''SELECT * FROM users WHERE username = %s AND password = %s''', (username, password))
    result = cursor.fetchone()

    if result:
        print("Успешная avtotis")
        current_user = result  
        subprocess.Popen(["python", "main.py"])
        rt.destroy()
    else:
        print("Ошибка авторизации")

rt = customtkinter.CTk()
rt.geometry("600x400")

fr_register = customtkinter.CTkFrame(master=rt)

fr_login = customtkinter.CTkFrame(master=rt)

def open_page_reg():
    fr_login.pack_forget()
    fr_register.pack()

def open_page_avto():
    fr_register.pack_forget()
    fr_login.pack()


label_register = customtkinter.CTkLabel(master=fr_register, width=90, height=32, text="Система регистрации", font=("Roboto", 24))
label_register.pack(pady=12, padx=10)

entry1 = customtkinter.CTkEntry(master=fr_register, width=240, height=32, placeholder_text="Имя пользователя")
entry1.pack(pady=12, padx=10)

entry2 = customtkinter.CTkEntry(master=fr_register, width=240, height=32, placeholder_text="Пароль", show="*")
entry2.pack(pady=12, padx=10)

butt_register = customtkinter.CTkButton(master=fr_register, width=240, height=32, text="Зарегистрироваться", command=register)
butt_register.pack(pady=12, padx=10)

label_login = customtkinter.CTkLabel(master=fr_login, width=90, height=32, text="Система авторизации", font=("Roboto", 24))
label_login.pack(pady=12, padx=10)

entry3 = customtkinter.CTkEntry(master=fr_login, width=240, height=32, placeholder_text="Имя пользователя")
entry3.pack(pady=12, padx=10)

entry4 = customtkinter.CTkEntry(master=fr_login, width=240, height=32, placeholder_text="Пароль", show="*")
entry4.pack(pady=12, padx=10)

butt_login = customtkinter.CTkButton(master=fr_login, width=240, height=32, text="Войти", command=avtotis)
butt_login.pack(pady=12, padx=10)

open_page_avto()

button_switch_to_register = customtkinter.CTkButton(master=rt, text="Регистрация", command=open_page_reg)
button_switch_to_register.pack(side="bottom", padx=5, pady=5)

button_switch_to_login = customtkinter.CTkButton(master=rt, text="авторизации", command=open_page_avto)
button_switch_to_login.pack(side="bottom", padx=5, pady=5)

rt.mainloop()

conn.close()
