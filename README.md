# Проект парсинга pep
Программа для парсинга документации Python и Pep
#### Технологии
- Python 3.9
#### Запуск проекта в dev-режиме
- Клонируйте репозиторий https://github.com/slayer0k/bs4_parser_pep с помощью команды
````
git clone
````
- Установите и активируйте виртуальное окружение
- Установите зависимости из файла requirements.txt с помощью команды
````
pip install -r requirements.txt
````
- В папке src/ запустите скрипт 
```
python3 main.py (позиционный аргумент) 
```
с позиционным аргументом на выбор:

```
pep
```
выводит список статусов всех PEP на сегодняшний день
```
whats-new
```
выводит ссылки на все версии документации Python и справочную информацию
```
latest-versions 
```
выводит ссылки на версии Python и их статус
```
download
```
загружает в папку downloads/ документации на последнюю версию Python

информации по опциональным аргументам можно получить выполнив скрипт
```
python3 main.py -h
```

### Автор
Дмитрий Самойленко
