# Попугаи

Веб-приложение на Django для изучения видов попугаев. Реализовано два режима:
- **Текстовый квиз** – пользователь отвечает на вопросы о видах попугаев.
- **Фото-квиз** – нужно определить вид по изображению.

За каждый правильный ответ начисляется очко, игра завершается при первой ошибке или досрочно. Результаты сохраняются в таблицу лидеров.

---

## Как использовать

1. **Скачать репозиторий** или клонировать его:
 
   git clone https://github.com/username/parrot-quiz.git
   cd parrot-quiz
Установить зависимости:

pip install -r requirements.txt
Создать файл .env в корне проекта (см. раздел «Корректное хранение секретов и токенов»).

Выполнить миграции:
```
bash
python manage.py migrate
```
Создать суперпользователя для доступа администратора:
```
bash
python manage.py createsuperuser
```
Загрузить тестовые данные (виды и вопросы):
```
bash
python manage.py loaddata initial_data.json
```
Запустить сервер разработки:
```
bash
python manage.py runserver
```
Открыть браузер по адресу http://127.0.0.1:8000/ и начать игру.

#Корректное хранение секретов и токенов
Для безопасного хранения секретов используется библиотека python-dotenv. Все секретные данные выносятся в файл .env, который не попадает в репозиторий.

Создать в корне проекта файл .env со следующим содержимым:

text
SECRET_KEY=<набор символов>
SECRET_KEY можно сгенерировать командой:
bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
#Функциональность
Главная страница – форма ввода имени, случайное изображение попугая

Текстовый квиз – вопросы с 4 вариантами ответа (правильный + 3 случайных).

Фото-квиз – изображение вида, 4 варианта ответа.

Таблица лидеров – лучшие результаты всех игроков.
Возможность добавление видов и вопросов к ним, редактирование

**Структура проекта**
```
parrot_project/
├── manage.py
├── requirements.txt
├── README.md
├── .env                     # секреты (не в репозитории)
├── .gitignore
├── initial_data.json     
├── parrot_project         
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── quiz/            
    ├── models.py
    ├── views.py
    ├── forms.py
    ├── urls.py
    ├── admin.py
    ├── templates/quiz/
    │   ├── base.html
    │   ├── index.html
    │   ├── quiz.html
    │   ├── photo_quiz.html
    │   ├── result.html
    │   ├── photo_result.html
    │   ├── leaderboard.html
    │   ├── species_list.html
    │   ├── species_detail.html
    │   ├── species_form.html
    │   └── question_form.html
    └── static/quiz/
        ├── styles.css
        └── images/
```

