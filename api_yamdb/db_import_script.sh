#!/bin/bash
csv_file_name=$1
table_name=$2
is_table=`echo "SELECT name FROM sqlite_master WHERE type='table' AND name='reviews_${table_name}'"| ./sqlite3 db.sqlite3`
if [ "$is_table" != "reviews_${table_name}" ]
then
  echo "таблица reviews_${table_name} в базе данных не найдена"
else
  count_before=`echo "SELECT COUNT(*) as count FROM reviews_${table_name}"| ./sqlite3 db.sqlite3`
  echo "количество записей в таблице reviews_${table_name} до импорта: $count_before"
  echo -e ".mode csv\n.import --skip 1 ./static/data/${csv_file_name}.csv reviews_${table_name}"| ./sqlite3 db.sqlite3
  count_after=`echo "SELECT COUNT(*) as count FROM reviews_${table_name}"| ./sqlite3 db.sqlite3`
  if [[ $count_after -gt $count_before ]]
  then
    echo "данные из файла ${csv_file_name}.csv импортированы в таблицу reviews_${table_name}"
    echo "количество записей в таблице reviews_${table_name} после импорта: $count_after"
  else
    echo "Не удалось импортировать данные из файла ${csv_file_name}.csv в таблицу reviews_${table_name}"
  fi
fi