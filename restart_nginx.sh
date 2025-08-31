#!/bin/bash

echo "🔄 Перезапуск nginx с новой конфигурацией..."

# Копируем новую конфигурацию
echo "⚙️ Копирую новую конфигурацию..."
sudo cp nginx_ylebb.conf /etc/nginx/sites-available/ylebb.ru

# Проверяем конфигурацию
echo "🔍 Проверяю конфигурацию..."
sudo nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Конфигурация корректна"
    
    # Перезапускаем nginx
    echo "🔄 Перезапускаю nginx..."
    sudo systemctl reload nginx
    
    echo "🎉 nginx перезапущен!"
    echo "📊 Статус:"
    sudo systemctl status nginx --no-pager -l
else
    echo "❌ Ошибка в конфигурации nginx"
    exit 1
fi
