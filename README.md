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

Скачать программу sqlite3.exe и поместить ее в корневую папку проекта api_yamdb:

```
https://www.sqlite.org/download.html
```

В терминале программы sqlite3.exe выполнить следующие команды для каждого .csv файла:

```
sqlite> .open db.sqlite3
sqlite> .mode csv
sqlite> .import --skip 1 <имя_файла_csv> <имя_соответсвующей_таблицы в db.sqlite3>
```

В случае несоответствия последовательности полей в .csv файле полям таблицы, необходимо пересортировать поля в .csv файле.
Для VSCode можно воспользоваться плагином **Edit csv**:

```
https://marketplace.visualstudio.com/items?itemName=janisdd.vscode-edit-csv
```
