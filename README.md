# Cafe-Control

<!-- ```poetry export --without-hashes --format=requirements.txt > requirements.txt``` -->

Развернутый сервис находится по адресу:

* [cafe-control-production.up.railway.app](https://cafe-control-production.up.railway.app/)

## Install

Перед установкой создайте .env файл, используя за основу .env-example, и заполните его

* requirements.txt

```python -m venv name_venv```


```name_venv\Scripts\activate.bat```

or

```source name_venv/bin/activate```

* poetry

```poetry install```

* Docker
```docker compose build```

## Run

* requirements.txt

```python app/manage.py runserver 0.0.0.0:8080```

* poetry

```poetry run python app/manage.py runserver 0.0.0.0:8080```

* Docker

```docker compose up -d```

Сервис будет доступен по адресу: [localhost:8080](http://localhost:8080)

## Создать суперпользователя можно с помощью

* requirements.txt

```python app/manage.py createsuperuser```

* poetry

```poetry run python app/manage.py createsuperuser```

* Docker

```docker compose exec -t django_service python app/manage.py createsuperuser```

## Применить миграции 

* requirements.txt

```python app/manage.py migrate```

* poetry

```poetry run python app/manage.py migrate```

* Docker

```docker compose exec -t django_service python app/manage.py migrate```

## Добавить блюдо (item) можно в [панеле администратора](http://localhost:8080/admin/)

* [items](http://localhost:8080/admin/cafe_control/item/)

