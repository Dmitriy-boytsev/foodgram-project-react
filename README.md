
  
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white)
![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB)
![SQLite](https://img.shields.io/badge/sqlite-%2307405e.svg?style=for-the-badge&logo=sqlite&logoColor=white)
![Postgres](https://img.shields.io/badge/postgres-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)



[![Main Kittygram workflow](https://github.com/dmitriy-boytsev/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/dmitriy-boytsev/foodgram-project-react/actions/workflows/main.yml)



<div align="center">
  
![Screenshot of a comment on a GitHub issue showing an image, added in the Markdown, of an Octocat smiling and raising a tentacle.](https://linkphoto.ru/wp-content/uploads/2020/07/knigi-po-fud-fotografii-na-russkom.jpg)




  
# Footgram - блог для любителей еды. 

</div>


 
## Описание проекта: 
 
Проект Foodgram даёт возможность пользователям поделиться  рецептами своих любимых блюд. Зарегистрированные пользователи могут создавать, просматривать, редактировать и удалять свои рецепты, а также подписыватся на других пользователей и добавлять их рецепты в "список покупок". "Prod версия" проверена, протестирована и готова для внедрения в производственную среду или в реальное использование пользователями.

## Стек проекта:

- Docker
- Postgres
- Python 3.x 
- Node.js 9.x.x 
- Git 
- Nginx 
- Gunicorn 
- Django (backend) 
- React (frontend)

##  Cсылка на развёрнутое приложение в сети: 
- #### https://diplompraktikum.ddns.net/

##  Cсылка на документацию в сети: 
- #### https://diplompraktikum.ddns.net/api/docs/


## Как развернуть: 
 
 - Клонироуйте репозиторий:
 
    ```bash
    git clone git@github.com:Dmitriy-boytsev/foodgram-project-react.git
    ```
 - Создайте файл .env

    ```bash
    touch .env
    ```
- Заполните файл переменными окружения

    ```bash
    POSTGRES_DB=<БазаДанных>
    POSTGRES_USER=<имя пользователя>
    POSTGRES_PASSWORD=<пароль>
    DB_NAME=<имя Базы Данных>
    DB_HOST=db
    DB_PORT=5432
    SECRET_KEY=<ключ Django>
    DEBUG=<DEBUG True/False>
    ALLOWED_HOSTS=<foodgram.ru localhost>
    ```
- Перейдите в папку infra

    ```bash
    cd infra
    ```
- Запустите Dockercompose

    ```bash
    sudo docker compose -f docker-compose.yml up -d
    ```

- Сделайте миграции и соберите статику и наполните базу тегами и ингредиентами

   ```bash
    sudo docker compose -f docker-compose.yml exec backend python manage.py migrate
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py import_ingredients
    sudo docker compose -f docker-compose.production.yml exec backend python manage.py create_tags
    sudo docker compose -f docker-compose.yml exec backend python manage.py collectstatic
    sudo docker compose -f docker-compose.production.yml exec backend cp -r /app/collected_static/. /static/static/ 

    ``` 
    




 ## Автор 
 
Бойцев Дмитрий 


  
![](https://github-profile-summary-cards.vercel.app/api/cards/profile-details?username=Dmitriy-boytsev)
