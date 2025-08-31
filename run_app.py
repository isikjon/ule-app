#!/usr/bin/env python3
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    host = os.environ.get("HOST", "0.0.0.0")
    
    print(f"🚀 Запускаю ULE Platform на {host}:{port}")
    print(f"🌐 Домен: ylebb.ru")
    print(f"📱 API: http://ylebb.ru:{port}/api/v1")
    print(f"🌍 Веб: http://ylebb.ru:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        access_log=True,
        log_level="info"
    )
