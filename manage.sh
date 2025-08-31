#!/bin/bash

case "$1" in
    start)
        echo "🚀 Запуск приложения..."
        ./start_app.sh
        ;;
    stop)
        echo "🛑 Остановка приложения..."
        if [ -f "app.pid" ]; then
            kill $(cat app.pid) 2>/dev/null || true
            rm -f app.pid
            echo "✅ Приложение остановлено"
        else
            echo "❌ PID файл не найден"
        fi
        ;;
    restart)
        echo "🔄 Перезапуск приложения..."
        ./manage.sh stop
        sleep 2
        ./manage.sh start
        ;;
    status)
        echo "📊 Статус приложения:"
        if [ -f "app.pid" ]; then
            PID=$(cat app.pid)
            if ps -p $PID > /dev/null; then
                echo "✅ Приложение запущено (PID: $PID)"
                echo "🌐 Доступно: http://ylebb.ru"
                echo "📝 Логи: app.log"
            else
                echo "❌ Процесс не найден, но PID файл существует"
                rm -f app.pid
            fi
        else
            echo "❌ Приложение не запущено"
        fi
        ;;
    logs)
        echo "📝 Показываю логи приложения:"
        if [ -f "app.log" ]; then
            tail -f app.log
        else
            echo "❌ Файл логов не найден"
        fi
        ;;
    nginx)
        echo "🌐 Управление nginx:"
        case "$2" in
            start)
                sudo systemctl start nginx
                ;;
            stop)
                sudo systemctl stop nginx
                ;;
            restart)
                sudo systemctl restart nginx
                ;;
            status)
                sudo systemctl status nginx
                ;;
            reload)
                sudo systemctl reload nginx
                ;;
            *)
                echo "Использование: $0 nginx {start|stop|restart|status|reload}"
                ;;
        esac
        ;;
    *)
        echo "🎯 ULE Platform Manager"
        echo ""
        echo "Использование: $0 {start|stop|restart|status|logs|nginx}"
        echo ""
        echo "Команды:"
        echo "  start   - Запустить приложение"
        echo "  stop    - Остановить приложение"
        echo "  restart - Перезапустить приложение"
        echo "  status  - Показать статус"
        echo "  logs    - Показать логи"
        echo "  nginx   - Управление nginx"
        echo ""
        echo "Примеры:"
        echo "  $0 start"
        echo "  $0 nginx restart"
        echo "  $0 status"
        ;;
esac
