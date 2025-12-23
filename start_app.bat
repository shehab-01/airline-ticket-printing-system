@echo off
echo Starting Airline Ticket Printing System...

REM ===============================
REM Backend (Python 3.11 venv)
REM ===============================
start "Backend Server" cmd /k ^
cd /d C:\Github\airline-ticket-printing-system\backend ^&^& ^
call .venv\Scripts\activate ^&^& ^
python main.py

REM ===============================
REM Frontend
REM ===============================
start "Frontend Server" cmd /k ^
cd /d C:\Github\airline-ticket-printing-system\frontend ^&^& ^
npm run dev
