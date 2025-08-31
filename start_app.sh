#!/bin/bash

echo "🚀 Запуск ULE Platform на ylebb.ru"

# Останавливаем предыдущий процесс если есть
if [ -f "app.pid" ]; then
    echo "🛑 Останавливаю предыдущий процесс..."
    kill $(cat app.pid) 2>/dev/null || true
    rm -f app.pid
fi

# Проверяем виртуальное окружение
if [ -d "venv" ]; then
    echo "🐍 Активирую виртуальное окружение..."
    source venv/bin/activate
fi

# Создаем директорию static если её нет
if [ ! -d "app/static" ]; then
    echo "📁 Создаю директорию app/static..."
    mkdir -p app/static
fi

# Запускаем приложение через uvicorn
echo "▶️ Запускаю приложение..."
nohup uvicorn main:app --host 127.0.0.1 --port 8000 > app.log 2>&1 &

# Сохраняем PID
echo $! > app.pid

echo "✅ Приложение запущено с PID: $(cat app.pid)"
echo "📝 Логи: app.log"
echo "🌐 Доступно по адресу: http://ylebb.ru"
echo "📊 Статус:"
sleep 3
curl -s http://127.0.0.1:8000/health | python3 -m json.tool 2>/dev/null || echo "Приложение еще запускается..."
