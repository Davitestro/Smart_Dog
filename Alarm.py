import os
import requests
import time
import subprocess
from datetime import datetime

with open("api.env", 'r') as file:
    api = file.readlines()[0].strip()
    session = file.readlines()[1].strip()
# Конфигурация Telegram бота
TELEGRAM_BOT_TOKEN = api
TELEGRAM_CHAT_ID = session
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'

# Глобальные переменные для отслеживания состояния
known_ssh_sessions = set()
known_vnc_sessions = set()
known_users = set()
last_check = datetime.now()

def send_telegram_message(text):
    try:
        requests.post(TELEGRAM_API_URL, json={
            'chat_id': TELEGRAM_CHAT_ID,
            'text': text,
            'parse_mode': 'HTML'
        })
    except Exception as e:
        print(f"Ошибка отправки в Telegram: {e}")

def get_active_ssh():
    try:
        output = subprocess.check_output(['who'], text=True)
        sessions = set()
        for line in output.splitlines():
            if 'pts/' in line:
                user = line.split()[0]
                ip = line.split('(')[-1].split(')')[0] if '(' in line else 'local'
                sessions.add(f"{user}@{ip}")
        return sessions
    except:
        return set()

def get_active_vnc():
    try:
        output = subprocess.check_output(['netstat', '-tunp'], text=True)
        sessions = set()
        for line in output.splitlines():
            if 'vnc' in line.lower() and 'ESTABLISHED' in line:
                parts = line.split()
                if len(parts) > 4:
                    ip_port = parts[4].split(':')[0]
                    sessions.add(ip_port)
        return sessions
    except:
        return set()

def get_active_rdp():
    try:
        output = subprocess.check_output(['netstat', '-tunp'], text=True)
        sessions = set()
        for line in output.splitlines():
            if '3389' in line and 'ESTABLISHED' in line:  # RDP порт
                parts = line.split()
                if len(parts) > 4:
                    ip_port = parts[4].split(':')[0]
                    sessions.add(ip_port)
        return sessions
    except:
        return set()

def get_logged_in_users():
    try:
        output = subprocess.check_output(['who'], text=True)
        return {line.split()[0] for line in output.splitlines()}
    except:
        return set()

def check_connections():
    global known_ssh_sessions, known_vnc_sessions, known_users, last_check

    # Проверка SSH
    current_ssh = get_active_ssh()
    new_ssh = current_ssh - known_ssh_sessions
    if new_ssh:
        for session in new_ssh:
            message = f"🚨 <b>Новое SSH-подключение</b> 🚨\n"
            message += f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            message += f"👤 Пользователь: {session}\n"
            message += f"💻 Хост: {os.uname().nodename}"
            send_telegram_message(message)
        known_ssh_sessions.update(new_ssh)

    # Проверка VNC
    current_vnc = get_active_vnc()
    new_vnc = current_vnc - known_vnc_sessions
    if new_vnc:
        for ip in new_vnc:
            message = f"🚨 <b>Новое VNC-подключение</b> 🚨\n"
            message += f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            message += f"🌐 IP адрес: {ip}\n"
            message += f"💻 Хост: {os.uname().nodename}"
            send_telegram_message(message)
        known_vnc_sessions.update(new_vnc)

    # Проверка RDP
    current_rdp = get_active_rdp()
    new_rdp = current_rdp - known_vnc_sessions  # Используем тот же набор для простоты
    if new_rdp:
        for ip in new_rdp:
            message = f"🚨 <b>Новое RDP-подключение</b> 🚨\n"
            message += f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            message += f"🌐 IP адрес: {ip}\n"
            message += f"💻 Хост: {os.uname().nodename}"
            send_telegram_message(message)
        known_vnc_sessions.update(new_rdp)
# Проверка новых пользователей в системе
    current_users = get_logged_in_users()
    new_users = current_users - known_users
    if new_users:
        for user in new_users:
            message = f"🚨 <b>Новый пользователь в системе</b> 🚨\n"
            message += f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
            message += f"👤 Пользователь: {user}\n"
            message += f"💻 Хост: {os.uname().nodename}"
            send_telegram_message(message)
        known_users.update(new_users)

    # Периодическая проверка (раз в сутки)
    if (datetime.now() - last_check).days >= 1:
        message = f"📢 <b>Система мониторинга активна</b> 📢\n"
        message += f"💻 Хост: {os.uname().nodename}\n"
        message += f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
        message += f"🔄 Работает без перебоев"
        send_telegram_message(message)
        last_check = datetime.now()

def main():
    # Первоначальное сообщение
    send_telegram_message(
        f"🟢 <b>Система мониторинга подключений запущена</b> 🟢\n"
        f"💻 Хост: {os.uname().nodename}\n"
        f"⏰ Время: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
    )

    # Инициализация текущих подключений
    global known_ssh_sessions, known_vnc_sessions, known_users
    known_ssh_sessions = get_active_ssh()
    known_vnc_sessions = get_active_vnc()
    known_users = get_logged_in_users()

    print("Мониторинг подключений запущен. Ожидание новых подключений...")

    # Основной цикл проверки
    while True:
        try:
            check_connections()
            time.sleep(5)  # Проверка каждые 5 секунд
        except Exception as e:
            print(f"Ошибка в основном цикле: {e}")
            time.sleep(60)  # При ошибке ждем минуту перед повторной попыткой

if __name__ == "__main__":
    main()