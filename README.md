Микроблоги — Дипломный проект Skillbox Python Advanced

---------------------------------
Быстрый запуск (1 команда)
---------------------------------

docker-compose up -d --build

-----------------------------------
Проверка работоспособности
-----------------------------------

### Полный тест API
./test_api.sh

### Тестирование

```bash```
make ci      # Все сразу
make test    # → 3 GREEN API теста
make cov     # → htmlcov/index.html (45%)
make report  # → Открыть отчёт


-----------------------------------
Доступ к сервису
-----------------------------------
Frontend: http://localhost
Swagger API: http://localhost:8000/docs
Backend: http://localhost:8000
PostgreSQL: localhost:5433

-----------------------------------
Архитектура проекта
-----------------------------------
Docker Compose (3 сервиса):
- PostgreSQL (microblog БД)
- FastAPI (REST API + 9 endpoints)
- NGINX (reverse proxy + static)

База данных:
- users (api_key, name)
- tweets (content, author_id)  
- likes (user_id, tweet_id)
- follows (follower_id, following_id)
- medias (filename, path)

Аутентификация: api-key header

Функционал:
1. Создать твит: POST /api/tweets
2. Загрузить медиа: POST /api/medias 
3. Удалить твит: DELETE /api/tweets/{id}
4. Поставить лайк: POST /api/tweets/{id}/likes
5. Убрать лайк: DELETE /api/tweets/{id}/likes
6. Подписаться: POST /api/users/{id}/follow
7. Отписаться: DELETE /api/users/{id}/follow
8. Лента твитов: GET /api/tweets
9. Мой профиль: GET /api/users/me
Профиль юзера: GET /api/users/{id}

NGINX proxy: localhost/api/* → backend

Технический стек

Python 3.12 + FastAPI + SQLAlchemy async
PostgreSQL 16 + Alembic migrations
Docker Compose + NGINX reverse proxy
Vue.js 3 Frontend (готовый)
Swagger OpenAPI документация
Тесты: test_api.sh (9 endpoints)

Критерии ТЗ — Выполнено

- Все 9 endpoints реализованы
- Docker Compose up -d (1 команда)  
- Данные сохраняются между запусками
- Swagger документация доступна
- README с инструкцией
- Pythonic код + типизация
- Тесты покрывают функционал

