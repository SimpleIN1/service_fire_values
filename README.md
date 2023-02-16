1. Создание volume для хранения данных (volume c данными скину):
    - docker volume create pg-data
2. Запуск докер-контэйнера:
    - БД для пользователей - docker run -d --restart=always --name pg-fires -e POSTGRES_PASSWORD=1234 -v pg-data:/var/lib/postgresql/data/ -p 127.0.0.1:5433:5432 postgres
3. Конфиг .env я скину 
4. Установка виртуального окружения (в папке проекта):
   - python -m venv venv
5. Активация виртуального окружения:
   - venv\Scripts\activate.bat
6. Установка пакетов:
   - pip install -r requirements.txt
7. Перемещаемся в папку AccountsProject:
   - cd Backend/AccountsProject
8. Запуск проекта
   - python manage.py runserver (по умолчанию хост-127.0.0.1, порт-8000. Для изменения указать - если просто порт, то 8080, а если хост и порт, то 127.0.0.1:8000)

