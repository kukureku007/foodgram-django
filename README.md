# praktikum_new_diplom

![workflow](https://github.com/kukureku007/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)
Краткое описание проекта
Проект Foodgram позволяет пользователям регистрироваться и создавать свои рецепты.
Основные функции: подписки на других авторов, добавление рецептов в избранное, в список покупок, который потом можно скачать.

# Подготовка к деплою:
На сервер скопировать в корень пользователя скопировать nginx.conf, docker-compose.yml и содержимое папки frontend.
В файле nginx.conf указать server_name. Запустить sudo docker compose up -d --build, далее применить миграции, собрать статику и проект готов к работе. Из модуля foodgram.services можно импортировать демо-базу или просто занести ингредиенты.

Адрес сервера:
http://51.250.107.79

Адрес админки:
http://51.250.107.79/admin/

Описание API:
http://51.250.107.79/api/docs/

# Тестовые данные пользователя:

email: admin@example.com

password: 1234

# Тестовые данные для админ-панели

username: admin

password: 1234