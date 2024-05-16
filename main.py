import keras
from ctypes import windll
import cv2, sys, sqlite3
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk

model = keras.models.load_model('effnet.h5')

conn = sqlite3.connect('database.db')
c = conn.cursor()


p = None
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


windll.shcore.SetProcessDpiAwareness(1)


# Функция, вызываемая при нажатии на кнопку
def predict_button_click():
    # Открытие диалогового окна для выбора файла
    file_path = filedialog.askopenfilename()

    # Открытие изображения
    image = Image.open(file_path)
    if image.height > 400:
        image = image.resize((int(image.width * 400 / image.height), 400))
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


def on_closing():
    sys.exit()


root = tk.Tk()
root.title("MRI-scan")
root.protocol("WM_DELETE_WINDOW", on_closing)
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f'{int(screen_width * 0.5)}x{int(screen_height * 0.8)}')

style = ttk.Style()
style.configure("TFrame", background="#1a1a1a", bordercolor="#40e0d0")

frame = ttk.Frame(root, style="TFrame")
frame.pack(expand=True, fill=tk.BOTH)

# Создание кнопки
but_img = Image.open("scan.png")
but_img = ImageTk.PhotoImage(but_img)

predict_button = tk.Button(root, pady=6, padx=10, text='DETECT', command=predict_button_click,
                           activebackground="#60f7e8", bg='#40e0d0', borderwidth=0, relief='raised')
predict_button.place(anchor='center', rely=0.8, relx=0.5)

frame_pred = ttk.Frame(root, padding="10", style="TFrame")
frame_pred.place(y=0, relwidth=1.0)

photo_label = ttk.Label(frame_pred, background="#1a1a1a")
photo_label.pack()

result_label = tk.Label(frame_pred, wraplength=500, text="", foreground='white', background='#1a1a1a', height=5,
                        highlightcolor='#40e0d0')
result_label.pack()


def add_record():
    c.execute('''CREATE TABLE IF NOT EXISTS persons (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 fio TEXT,
                 birth_date DATE,
                 gender TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS results (
                 id INTEGER PRIMARY KEY AUTOINCREMENT,
                 pacientId INTEGER,
                 result TEXT,
                 FOREIGN KEY (pacientId) REFERENCES persons(id))''')
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
    else:
        print('Введи больше данных')
    fio_entry.delete(0, tk.END)
    birth_date_entry.delete(0, tk.END)


# Поле ввода ФИО
fio_label = ttk.Label(root, text="ФИО:")
fio_label.pack(side=tk.LEFT, padx=5, pady=5)
fio_entry = ttk.Entry(root)
fio_entry.pack(side=tk.LEFT, padx=5, pady=5, fill=tk.X, expand=True)

# Поле ввода даты рождения
birth_date_label = ttk.Label(root, text="Дата рождения:")
birth_date_label.pack(side=tk.LEFT, padx=5, pady=5)
birth_date_entry = ttk.Entry(root)
birth_date_entry.pack(side=tk.LEFT, padx=5, pady=5)

# Выбор пола
gender_label = ttk.Label(root, text="Пол:")
gender_label.pack(side=tk.LEFT, padx=5, pady=5)
gender_var = tk.StringVar()
male_radio = ttk.Radiobutton(root, text="М", variable=gender_var, value="М")
male_radio.pack(side=tk.LEFT, padx=5, pady=5)
female_radio = ttk.Radiobutton(root, text="Ж", variable=gender_var, value="Ж")
female_radio.pack(side=tk.LEFT, padx=5, pady=5)

# Кнопка сохранения
image_save = Image.open('save.png')
image_save = image_save.resize((32, int(32 / image_save.width * image_save.height)))
photo_save = ImageTk.PhotoImage(image_save)
save_button = tk.Button(root, command=add_record, image=photo_save, background='#1a1a1a', activebackground="#1a1a1a",
                        borderwidth=0)
save_button.pack(side=tk.LEFT, padx=5, pady=5)

root.mainloop()
