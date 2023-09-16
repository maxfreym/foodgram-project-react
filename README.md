[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![GitHub%20Actions](https://img.shields.io/badge/-GitHub%20Actions-464646?style=flat-square&logo=GitHub%20actions)](https://github.com/features/actions)
# Проект Foodgram - «Продуктовый помощник»
![Build Status](https://github.com/maxfreym/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

### Описание:
Сервис, который позволяет создавать/просматривать рецепты блюд, 
подписываться на авторов, добавлять рецепты в избранное и в список покупок. 
Список покупок выгружается в виде файла (shopping-list.txt), в котором сохранены все
ингредиенты для рецептов из списка покупок.

### Используемые технологии
- Django
- Django Rest Framework
- Docker
- Docker-compose
- Gunicorn
- Nginx
- PostgreSQL

### Workflow
- **tests:** Проверка кода на соответствие PEP8.
- **push Docker image to Docker Hub:** Сборка и публикация образа на DockerHub.
- **deploy:** Автоматический деплой на боевой сервер при пуше в главную ветку main.
- **send_massage:** Отправка уведомления в телеграм-чат.

### Подготовка и запуск проекта
У вас должен быть установлен Docker и вы должны быть зарегистрированы на [DockerHub](https://hub.docker.com/)
- Клонировать проект с помощью git clone или скачать ZIP-архив.
- Перейти в папку \foodgram-project-react\backend и выполнить команды:
```bash
sudo docker build -t <логин на DockerHub>/<название образа для бэкенда, какое хотите)> .
sudo docker login
sudo docker push <логин на DockerHub>/<название образа для бэкенда, которое написали> 
```
- Перейти в папку \foodgram-project-react\frontend и выполнить команды:
```bash
sudo docker build -t <логин на DockerHub>/<название образа для фронтэнда, какое хотите)> .
sudo docker login
sudo docker push <логин на DockerHub>/<название образа для фронтэнда, которое написали> 
```
- Изменить файл \foodgram-project-react\infra\docker-compose.yml:
```
backend:
  image: <логин на DockerHub>/<название образа для бэкенда, которое написали>
  
frontend:
  image: <логин на DockerHub>/<название образа для фронтэнда, которое написали>
```
- Изменить файл \foodgram-project-react\.github\workflows\foodgram_workflow.yml:
```
build_and_push_to_docker_hub:
.......
    tags: ${{ secrets.DOCKER_USERNAME }}/<название образа для бэкенда, которое написали>
    
deploy:
.......
    sudo docker pull ${{ secrets.DOCKER_USERNAME }}/<название образа для бэкенда, которое написали>
```
- Выполнить вход на удаленный сервер
- Установить docker на сервер:
```bash
sudo apt install docker.io 
```
- Установить docker-compose на сервер:
```bash
sudo apt-get update
sudo apt install docker-compose
```
- Скопировать файл docker-compose.yml и nginx.conf из директории infra на сервер:
```bash
scp docker-compose.yml <username>@<host>:/home/<username>/
scp nginx.conf <username>@<host>:/home/<username>/
```
- Для работы с Workflow добавить в Secrets GitHub переменные окружения:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

DOCKER_PASSWORD=<пароль DockerHub>
DOCKER_USERNAME=<имя пользователя DockerHub>

USER=<username для подключения к серверу>
HOST=<IP сервера>
PASSPHRASE=<пароль для сервера, если он установлен>
SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>

TELEGRAM_TO=<ID своего телеграм-аккаунта>
TELEGRAM_TOKEN=<токен вашего бота>
```
- После деплоя изменений в git, дождитесь выполнения всех Actions.
  * Создать суперпользователя Django
    ```bash
    sudo docker-compose exec backend python manage.py createsuperuser
    ```
  * Загрузить подготовленный список ингредиентов
    ```bash
    sudo docker-compose exec backend python manage.py load_ingredients
    ```

- Проект будет доступен по вашему IP-адресу.

#### REST API
Подробная документация API будет доступна по адресу - http://<IP-адрес вашего сервера>/api/docs/

#### Автор:
Окороков Максим - [https://github.com/maxfreym](https://github.com/maxfreym)

#### Юзер для ревью
login: maxfreym
pass: m11m12m87