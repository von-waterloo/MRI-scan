import time
from ctypes import windll
import cv2, sys, sqlite3
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk, ImageSequence
import threading
import base64


p = None
model = None

def model_loading():
    global model
    import keras
    model = keras.models.load_model('effnet.h5')
    thread_loading.join()
    photo_label.image = None
    result_label.configure(text='', font=font_for_other, pady=15)
    make_ui()

thread_load_model = threading.Thread(target=model_loading)

def gif_in_ui():

    image_gif = Image.open('AqCa.gif')
    for index,frame in enumerate(ImageSequence.Iterator(image_gif)):
        image = frame
        if image.height > 350:
            image = image.resize((int(image.width * 350 / image.height), 350))
        photo = ImageTk.PhotoImage(image)
        photo_label.configure(image=photo)
        photo_label.image = photo
        root.update()
        if index == 0:
            result_label.configure(text='Подготовка модели', foreground='white', font=('Comic Sans MS', 16))
        time.sleep(0.04)
def loading():
    frame_pred.place(y=0, relwidth=1.0)
    photo_label.pack(pady=15)
    result_label.pack(pady=0)
    while not model:
        gif_in_ui()


thread_loading = threading.Thread(target=loading)

def short_message(text, foreground):
    message_label.configure(text=text, foreground=foreground)
    time.sleep(3)
    message_label.configure(text='')


def predict_image(image):
    opencvImage = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    img = cv2.resize(opencvImage, (150, 150))
    img = img.reshape((1, 150, 150, 3))
    global p

    p = model.predict(img, verbose=None)
    p = np.argmax(p, axis=1)[0]

    if p == 0:
        p = "На снимке обнаружена опухоль. Тип опухоли: глиома. Глиома — опухоль, поражающая глиальные клетки головного или спинного мозга, входящая в гетерогенную группу и имеющая нейроэктодермальное происхождение."
    elif p == 1:
        p = "Опухоль не обнаружена."
    elif p == 2:
        p = "На снимке обнаружена опухоль. Тип опухоли: менингиома. Менингиома (арахноидэндотелиома) — опухоль, растущая из клеток паутинной мозговой оболочки, а именно арахноидального эндотелия — ткани, окружающей мозг."
    else:
        p = "На снимке обнаружена опухоль. Тип опухоли: опухоль гипофиза. Опухоль гипофиза – это доброкачественная опухоль, которая образуется из клеток передней доли железы внутренней секреции, играющей огромную роль в поддержании нормального гормонального баланса организма."

    return p

def predict_button_click():
    # Открытие диалогового окна для выбора файла
    file_path = filedialog.askopenfilename()

    # Открытие изображения
    image = Image.open(file_path)
    if image.height > 350:
        image = image.resize((int(image.width * 350 / image.height), 350))
    if image.height < 350:
        image = image.resize((int(image.width * 350 / image.height), 350))
    photo = ImageTk.PhotoImage(image)

    # Создание виджета Label для отображения изображения
    photo_label.configure(image=photo)
    photo_label.image = photo
    root.update()

    # Получение предсказания
    prediction = predict_image(image)

    # Отображение результата в GUI
    if 'Опухоль не обнаружена' not in prediction:
        color_pred = 'red'
    else:
        color_pred = 'green'
    result_label.config(text=prediction, foreground=color_pred)
    make_save_ui()

def on_closing():
    sys.exit()

#Создание окна
windll.shcore.SetProcessDpiAwareness(1)
root = tk.Tk()
root.title("MRI-scan")
root.protocol("WM_DELETE_WINDOW", on_closing)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f'{int(screen_width * 0.5)}x{int(screen_height * 0.75)}')

font_for_btn = ('Tahoma', 15)
font_for_other = ('Tahoma', 12)

frame = tk.Frame(root, background="#101010")
frame.pack(expand=True, fill=tk.BOTH)


predict_button = tk.Button(root, pady=5, padx=10, text='DETECT', command=predict_button_click, font=font_for_btn, foreground='white',
                               activebackground="white", bg='#101010', borderwidth=5, activeforeground='black')
frame_pred = tk.Frame(root, background="#101010")
photo_label = ttk.Label(frame_pred, background="#101010")
result_label = tk.Label(frame_pred, wraplength=500, text="", font=font_for_other, background='#101010', height=6, anchor='n')

def make_ui():
    predict_button.place(anchor='center', rely=0.82, relx=0.5)

# Сохранение в базу

def add_record():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS persons (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 fio TEXT,
                 birth_date DATE,
                 gender TEXT
                 )''')
    c.execute('''PRAGMA foreign_keys = ON''')
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS results (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 pacientId INTEGER,
                 result TEXT,
                 FOREIGN KEY (pacientId) REFERENCES persons(id) ON DELETE CASCADE)
                 ''')
    fio = fio_entry.get()
    birth_date = birth_date_entry.get()
    gender = gender_var.get()
    if gender and birth_date and gender and p:
        c.execute('''INSERT INTO persons (fio, birth_date, gender) VALUES (?, ?, ?)''', (fio, birth_date, gender))
        pacientId = c.execute('''SELECT MAX(id) FROM persons''').fetchone()[0]
        result_list = {'глиома': 'glioma_tumor',
                       'менингиома': 'meningioma_tumor',
                       'опухоль гипофиза': 'pituitary_tumor',
                       'не обнаружена': 'no_tumor'}
        result = [value for key,value in result_list.items() if key in p][0]

        c.execute('''INSERT INTO results (pacientId, result) VALUES (?, ?)''', (pacientId, result))
        conn.commit()
        conn.close()
        text_for_message, foregraund = 'Запись успешно сохранена', 'green'
        short_message_thread = threading.Thread(target=short_message, args=(text_for_message, foregraund,))
        short_message_thread.start()

    else:
        text_for_message, foregraund = 'Недостаточно данных для сохранения', 'red'
        short_message_thread = threading.Thread(target=short_message, args=(text_for_message, foregraund,))
        short_message_thread.start()
        conn.close()

    fio_entry.delete(0, tk.END)
    birth_date_entry.delete(0, tk.END)

frame_save = tk.Frame(root, background='#101010')
# Поле ввода ФИО
fio_label = ttk.Label(frame_save, text="ФИО:", background='#101010', font=font_for_other, foreground='white')
fio_entry = ttk.Entry(frame_save, font=font_for_other, foreground='black')
# Поле ввода даты рождения
birth_date_label = ttk.Label(frame_save, text="Дата рождения:", background='#101010', font=font_for_other, foreground='white')
birth_date_entry = ttk.Entry(frame_save, width=10, font=font_for_other, foreground='black')
# Выбор пола
gender_label = ttk.Label(frame_save, text="Пол:", background='#101010', font=font_for_other, foreground='white')
gender_var = tk.StringVar()

style_save = ttk.Style()

# Настраиваем стиль для RadioButton
style_save.map("TRadiobutton",
          background=[("active", "#101010"), ("!disabled", "#101010")],
          fieldbackground=[("active", "#101010"), ("!disabled", "#101010")],
          foreground=[("active", "white"), ("!disabled", "white")]
          )

male_radio = ttk.Radiobutton(frame_save, text="М", variable=gender_var, value="М", style='TRadiobutton')
female_radio = ttk.Radiobutton(frame_save, text="Ж", variable=gender_var, value="Ж", style='TRadiobutton')
# Кнопка сохранения
image_save = Image.open('save.png')
image_save = image_save.resize((48, int(48 / image_save.width * image_save.height)))
photo_save = ImageTk.PhotoImage(image_save)
save_button = tk.Button(frame_save, command=add_record, image=photo_save, background='#1a1a1a', activebackground="#1a1a1a",
                        borderwidth=0)
message_label = tk.Label(frame_save, wraplength=500, text="", font=('Comic Sans MS',10),background='#101010', anchor='se', padx=10)

def make_save_ui():
    message_label.pack(side=tk.TOP, fill=tk.X)
    fio_label.pack(side=tk.LEFT, padx=5, pady=5)
    fio_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)
    birth_date_label.pack(side=tk.LEFT, padx=5, pady=5)
    birth_date_entry.pack(side=tk.LEFT, padx=5, pady=5)
    gender_label.pack(side=tk.LEFT, padx=5, pady=5)
    male_radio.pack(side=tk.LEFT, padx=5, pady=5)
    female_radio.pack(side=tk.LEFT, padx=5, pady=5)
    save_button.pack(side=tk.LEFT, padx=10, pady=10)

    frame_save.pack(side=tk.BOTTOM, fill=tk.X)

# Создание фрейма для размещения элементов формы по центру
frame_login = tk.Frame(frame, background="#101010")
frame_login.place(relx=0.5, rely=0.5, anchor="center")

# Поле для ввода логина
username_label = ttk.Label(frame_login, text="Логин:", font=font_for_other, foreground='white', background='#101010')
username_label.grid(row=1, column=0, padx=10, pady=5)
username_entry = ttk.Entry(frame_login, font=font_for_other, foreground='black')
username_entry.grid(row=1, column=1, padx=10, pady=5)

# Поле для ввода пароля
password_label = ttk.Label(frame_login, text="Пароль:", font=font_for_other, foreground='white', background='#101010')
password_label.grid(row=2, column=0, padx=10, pady=5)
password_entry = ttk.Entry(frame_login, show="*", font=font_for_other, foreground='black')
password_entry.grid(row=2, column=1, padx=10, pady=5)


#Функция авторизации
def login(event=None):
    username = username_entry.get()
    password = password_entry.get()
    # Здесь можно добавить код для проверки логина и пароля
    if username == 'admin' and password == 'admin' or username == password:
        frame_login.destroy()
        thread_loading.start()
        thread_load_model.start()
    else:
        warning_message = ttk.Label(frame_login, text="Неверные логин и пароль", font=font_for_other, foreground='red',
                                   background='#101010')
        warning_message.grid(row=0, column=1, padx=10, pady=5)

password_entry.bind("<Return>", login)
username_entry.bind("<Return>", login)
# Кнопка "Войти"
login_button = tk.Button(frame_login, command=login, text="Войти", bg='#101010', foreground='white', font=font_for_btn, borderwidth=4)
login_button.grid(row=3, column=1, columnspan=20, padx=10, pady=10)

root.mainloop()
