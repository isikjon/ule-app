#!/bin/bash

echo "🚀 Настройка nginx для ylebb.ru"

# Проверяем, установлен ли nginx
if ! command -v nginx &> /dev/null; then
    echo "📦 Устанавливаю nginx..."
    sudo apt update
    sudo apt install -y nginx
else
    echo "✅ nginx уже установлен"
fi

# Создаем директорию для логов
echo "📁 Создаю директории для логов..."
sudo mkdir -p /var/log/nginx

# Копируем конфигурацию
echo "⚙️ Копирую конфигурацию nginx..."
sudo cp nginx_ylebb.conf /etc/nginx/sites-available/ylebb.ru

# Создаем символическую ссылку
echo "🔗 Активирую сайт..."
sudo ln -sf /etc/nginx/sites-available/ylebb.ru /etc/nginx/sites-enabled/

# Удаляем дефолтный сайт
echo "🗑️ Удаляю дефолтный сайт..."
sudo rm -f /etc/nginx/sites-enabled/default

# Проверяем конфигурацию
echo "🔍 Проверяю конфигурацию nginx..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Конфигурация корректна"
    
    # Перезапускаем nginx
    echo "🔄 Перезапускаю nginx..."
    sudo systemctl restart nginx
    sudo systemctl enable nginx
    
    echo "🎉 nginx настроен и запущен!"
    echo "🌐 Сайт доступен по адресу: http://ylebb.ru"
    echo "📊 Статус nginx:"
    sudo systemctl status nginx --no-pager -l
else
    echo "❌ Ошибка в конфигурации nginx"
    exit 1
fi
