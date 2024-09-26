![example workflow](https://github.com/4t0n/foodgram/actions/workflows/main.yml/badge.svg)
# Сервис FoodGramm «Продуктовый помощник»

## Описание проекта

Foodgram — это сайт, который может быть полезен как начинающим кулинарам, так и гурманам. Здесь пользователи могут делиться своими рецептами, подписываться на других пользователей и добавлять понравившиеся рецепты в избранное.

Можно создавать и скачивать список продуктов, которые понадобятся для приготовления выбранного вами блюд.

Проект реализован с использованием Docker-контейнеров. В него входят:

    API (backend-приложение);
    база данных PostgreSQL;
    сервер Nginx;
    frontend-контейнер.

В проекте реализовано CI/CD. При внесении изменений в основную ветку проекта происходит автоматическое тестирование на соответствие требованиям PEP8. Если тесты пройдены успешно, то на git-платформе создаётся образ backend-контейнера Docker и автоматически размещается в облачном хранилище DockerHub. Размещённый образ автоматически разворачивается на рабочем сервере вместе с контейнером веб-сервера nginx и базой данных PostgreSQL.

Сайт доступен по адресу freefoodgram.sytes.net или 89.169.173.93.

## Используемые технологии

* Python 3.9
* Django 3.2
* Rest API
* PostgreSQL
* Nginx
* Docker
* React
* GitHub Actions (CI/CD)

## Установка


Для установки проекта необходимо выполнить следующие шаги:

1. Установить Docker и Docker Compose согласно инструкции на сайте https://www.docker.com/

2. В корневой папке проекта необходимо создать файл .env с настройками по примеру .env.example.

3. Клонировать репозиторий с помощью команды:

```
git clone https://github.com/4t0n/foodgram.git
```

4. Для запуска проекта необходимо в корневой папке проекта выполнить команду:

```
docker compose -f docker-compose.production.yml up -d
```

5. Выполнить миграции и собрать статику:

```
docker compose -f docker-compose.production.yml exec backend python manage.py migrate
```

```
docker compose -f docker-compose.production.yml exec backend python manage.py collectstatic
```

```
docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /backend_static/static/
```

6. Загрузить список ингредиентов:

```
docker compose -f docker-compose.production.yml exec backend python manage.py load_ingredients
```

После выполнения данных шагов вы можете начать пользоваться приложением FoodGramm.
