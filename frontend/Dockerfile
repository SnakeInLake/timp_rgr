# frontend/Dockerfile

# --- ЭТАП 1: Сборка React-приложения ---
# Используем Node.js для сборки
FROM node:18-alpine AS builder
WORKDIR /app

# Копируем package.json и lock-файл
COPY package*.json ./

# Устанавливаем зависимости
RUN npm install

# Копируем остальной код фронтенда
COPY . .

# Собираем приложение для продакшена
RUN npm run build

# --- ЭТАП 2: Настройка Nginx для отдачи статики ---
# Используем официальный легковесный образ nginx
FROM nginx:stable-alpine

# Создаем директорию для SSL сертификатов внутри контейнера
RUN mkdir -p /etc/nginx/ssl

# Копируем SSL сертификат и ключ
# Предполагаем, что сертификаты лежат в папке ssl_certs в контексте сборки (./frontend)
# Если они в корне проекта, путь к ним нужно будет скорректировать в docker-compose.yml
# или скопировать их в ./frontend/ssl_certs перед сборкой
COPY ssl_certs/nginx-selfsigned.crt /etc/nginx/ssl/nginx-selfsigned.crt
COPY ssl_certs/nginx-selfsigned.key /etc/nginx/ssl/nginx-selfsigned.key

# Копируем обновленную конфигурацию nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Копируем собранные статические файлы из этапа 'builder'
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx будет слушать на порту 80 (для редиректа) и 443 (для HTTPS)
EXPOSE 80
EXPOSE 443

# Запускаем nginx
CMD ["nginx", "-g", "daemon off;"]