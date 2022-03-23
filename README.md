# api_yamdb
api_yamdb

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/.../
```

```
cd ...
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv env
```

```
source env/bin/activate
```

```
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
cd ..
```

Выполнить миграции:

```
python3 manage.py migrate
```

Запустить проект:

```
python3 manage.py runserver
```
____
### Как импортировать данные из прилагаемых .csv файлов (api_yamdb\static\data\) в database проекта:

#### Файлы csv должны располагаться по умолчанию в подпапке проекта ./static/data/..., ,база данных должна иметь расположение и имя по умолчанию (db.sqlite3)

Скачать программу sqlite3.exe и поместить ее в корневую папку проекта api_yamdb:

```
https://www.sqlite.org/download.html
```

В случае несоответствия последовательности полей в .csv файле полям таблицы, необходимо пересортировать поля в .csv файле.
Для VSCode можно воспользоваться плагином **Edit csv**:

```
https://marketplace.visualstudio.com/items?itemName=janisdd.vscode-edit-csv
```

В терминале bash сделать прилагаемый скрипт db_import_script.sh испоняемым следующей командой:

```
chmod +x ./db_import_script.sh
```

Запустить выполнение скрипта с указанием двух обязательных аргументов - имя файла csv (без расширения), имя модели (таблицы) в базе данных (без префикса reviews_):

```
./db_import_script.sh <имя_файла> <имя_модели>
```

Повторить выполнение скрипта для каждой пары файл-таблица.
