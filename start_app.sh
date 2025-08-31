#!/bin/bash

echo "🚀 Запуск ULE Platform на ylebb.ru"

# Останавливаем предыдущий процесс если есть
if [ -f "app.pid" ]; then
    echo "🛑 Останавливаю предыдущий процесс..."
    kill $(cat app.pid) 2>/dev/null || true
    rm -f app.pid
fi

# Запускаем приложение в фоне
echo "▶️ Запускаю приложение..."
nohup python3 run_app.py > app.log 2>&1 &

# Сохраняем PID
echo $! > app.pid

echo "✅ Приложение запущено с PID: $(cat app.pid)"
echo "📝 Логи: app.log"
echo "🌐 Доступно по адресу: http://ylebb.ru"
echo "📊 Статус:"
sleep 2
curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo "Приложение еще запускается..."
