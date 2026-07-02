@echo off
REM ============================================================
REM  FastAPI Lokal Demo baslatici (Docker/K8s GEREKTIRMEZ)
REM  Cift tikla, sonra tarayicida: http://localhost:8000/docs
REM ============================================================
cd /d "%~dp0"
set SQLALCHEMY_DATABASE_URL=sqlite:///./local_demo.db
echo.
echo  Sunucu baslatiliyor...  Tarayicida http://localhost:8000/docs adresini ac
echo  Durdurmak icin: bu pencerede Ctrl+C
echo.
"C:\Users\t27240\AppData\Local\Programs\Python\Python314\python.exe" -m uvicorn local_run:app --host 127.0.0.1 --port 8000
pause
