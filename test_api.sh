#!/bin/bash
echo "ТЕСТ БЭКЕНДА"

# 1. СТАТУС
echo "1️⃣ Docker: $(docker-compose ps | grep Up | wc -l)/3"

# 2. USERS
echo -e "\n2️⃣ USERS API:"
curl -s -w "Status: % {http_code}\n" -H "api-key: test" http://localhost/api/users/me

# 3. TWEETS CRUD
echo -e "\n3️⃣ TWEETS CRUD:"
curl -s -w "Status: %{http_code}\n" -H "api-key: test" http://localhost/api/tweets

curl -s -w "Status: %{http_code}\n" -X POST -H "api-key: test" \
  -d "tweet_data=Тест твита #1" http://localhost/api/tweets

curl -s -w "Status: %{http_code}\n" -X POST -H "api-key: test" \
  -d "tweet_data=Тест твита #2" http://localhost/api/tweets

curl -s -w "Status: %{http_code}\n" -H "api-key: test" http://localhost/api/tweets

# 4. LIKES
echo -e "\n4️⃣ LIKES:"
curl -s -w "Status: %{http_code}\n" -X POST -H "api-key: test" \
  http://localhost/api/tweets/1/likes

# 5. FOLLOW
echo -e "\n5️⃣ FOLLOW:"
curl -s -w "Status: %{http_code}\n" -X POST -H "api-key: test" \
  http://localhost/api/users/1/follow

# 6. SWAGGER
echo -e "\n6️⃣ SWAGGER:"
curl -s -w "Status: %{http_code}\n" http://localhost:8000/docs | head -20

# 7. БД — ПОСЛЕ ТЕСТОВ
echo -e "\n7️⃣ БАЗА ДАННЫХ:"
docker exec -it $(docker-compose ps -q db) psql -U postgres -d microblog \
  -c "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM tweets; SELECT COUNT(*) FROM likes;"

echo -e "\n ТЕСТИРОВАНИЕ ЗАВЕРШЕНО!"
