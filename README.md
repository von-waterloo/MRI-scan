Приложение на Windows для распознавания опухоли головного мозга на основе обученной модели: https://www.kaggle.com/code/jaykumar1607/brain-tumor-mri-classification-tensorflow-cnn/notebook

Запуск через IDE:

1) клонирование репозитория:

git init

git clone https://github.com/von-waterloo/MRI-scan.git

2) установка виртуального окружения и зависимостей:

python -m venv venv

venv/Scripts/activate

pip install -r requirements.txt

3) запускаем main.py

Для упаковки программы в .exe:

pyinstaller -F -n MRI-scan --noconsole --icon=icon.ico main.py
___________________________________________________________________

MRI-scan = имя .exe на выходе,

--noconsole = бесконсольный режим,  

icon.ico = файл иконки, лежащий в корневной директории,

main.py = имя исполняемого файла программы

Готовый .exe залетает в папку dict.

Обратите внимание, что готовая программа требует модель и медиа, лежащие в директории с exe-файлом в папках с соответствующими названиями

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

The Windows-application to recognition a brain tumor based on a trained model: https://www.kaggle.com/code/jaykumar1607/brain-tumor-mri-classification-tensorflow-cnn/notebook

Run via IDE:

1) cloning the repository:

git init

git clone https://github.com/von-waterloo/MRI-scan.git

2) installation of virtual environment and dependencies:

python -m venv venv

venv/Scripts/activate

pip install -r requirements.txt

3) run main.py

To package the program in .exe:

pyinstaller -F -n MRI scan --noconsole --icon=icon.ico main.py
___________________________________________________________________

MRI scan = output .exe name,

--noconsole = no console mode,

icon.ico = icon files, discussions in the root directory,

main.py = name of the program executable file

The finished .exe flies into the dict cursor.

Please note that the finished program requires a model and multimedia, adding it to the directory with the exe file in folders with matching names.
