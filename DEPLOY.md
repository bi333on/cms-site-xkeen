# 🚀 Установка CMS VLESS-Keenetic на VPS Ubuntu 24.04 + Caddy

## 📋 Предварительные требования

- **VPS** с Ubuntu 24.04 LTS (минимально 1 vCPU, 512 MB RAM, 10 GB SSD)
- **Домен**, привязанный к IP-адресу сервера (A-запись в DNS)
- **Telegram-бот**, созданный через [@BotFather](https://t.me/BotFather)
- **SSH-доступ** к серверу с правами root или sudo

---

## 🔧 Шаг 1: Подготовка сервера

Подключитесь к VPS по SSH:

```bash
ssh root@ВАШ_IP_СЕРВЕРА
```

Обновите систему и установите необходимые пакеты:

```bash
apt update && apt upgrade -y
apt install -y python3 python3-venv python3-pip git curl
```

---

## 🔧 Шаг 2: Копирование файлов на сервер

### Способ А: Через SCP (с вашего ПК)

Скопируйте папку `CMS_Site` на сервер:

```bash
# На вашем ПК (Windows PowerShell):
scp -r C:\Users\Angor\telegram_bot\CMS_Site root@ВАШ_IP:/opt/cms-site-temp
```

Затем на сервере:

```bash
mv /opt/cms-site-temp /opt/cms-site
```

### Способ Б: Через Git

Если проект в репозитории:

```bash
cd /opt
git clone https://github.com/your-username/cms-keenetic.git cms-site
```

---

## 🔧 Шаг 3: Настройка Python-окружения

```bash
cd /opt/cms-site

# Создание виртуального окружения
python3 -m venv venv

# Активация и установка зависимостей
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 🔧 Шаг 4: Настройка переменных окружения

Создайте файл `.env`:

```bash
nano /opt/cms-site/.env
```

Заполните **обязательные** поля:

```ini
# Сгенерируйте секретный ключ командой:
# python3 -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=сгенерированный_ключ_64_символа

# Токен Telegram-бота (получить у @BotFather)
BOT_TOKEN=1234567890:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

# Имя бота в Telegram (без @)
TELEGRAM_BOT_USERNAME=YourBotName

# Данные для входа в админ-панель
ADMIN_USERNAME=admin
ADMIN_PASSWORD=ваш_сложный_пароль

# URL сайта
SITE_URL=https://keen.z-ip.pro
SITE_NAME=Настройка Keenetic VLESS Reality

# База данных
DATABASE_URL=sqlite:///cms.db

# Яндекс.Метрика (необязательно)
YANDEX_METRIKA_ID=00000000
YANDEX_WEBMASTER=xxxxxxxx
```

Сохраните: `Ctrl+O`, `Enter`, `Ctrl+X`.

---

## 🔧 Шаг 5: Тестовый запуск

Проверьте, что приложение запускается:

```bash
cd /opt/cms-site
source venv/bin/activate
python app.py
```

Откройте второй терминал и проверьте:

```bash
curl http://127.0.0.1:5000
```

Если видите HTML — всё работает. Нажмите `Ctrl+C` для остановки.

---

## 🔧 Шаг 6: Настройка systemd-сервиса

Скопируйте и настройте сервис-файл:

```bash
cp /opt/cms-site/cms-site.service /etc/systemd/system/
systemctl daemon-reload
```

Если пользователь `www-data` не существует — создайте:

```bash
useradd -r -s /bin/false www-data
```

Настройте права:

```bash
chown -R www-data:www-data /opt/cms-site
chmod -R 755 /opt/cms-site
```

Запустите сервис:

```bash
systemctl enable cms-site
systemctl start cms-site
systemctl status cms-site
```

Должен быть статус `active (running)`.

---

## 🔧 Шаг 7: Установка и настройка Caddy

Установите Caddy:

```bash
apt install -y debian-keyring debian-archive-keyring apt-transport-https curl
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install -y caddy
```

Скопируйте конфигурацию Caddy:

```bash
cp /opt/cms-site/Caddyfile /etc/caddy/Caddyfile
```

**Важно:** замените `keen.z-ip.pro` в Caddyfile на ваш реальный домен:

```bash
nano /etc/caddy/Caddyfile
# Замените keen.z-ip.pro на ваш-домен.ru
```

Создайте папку для логов:

```bash
mkdir -p /var/log/caddy
chown caddy:caddy /var/log/caddy
```

Перезапустите Caddy:

```bash
systemctl restart caddy
systemctl status caddy
```

---

## 🔧 Шаг 8: Проверка

Откройте в браузере `https://ваш-домен.ru`. Должен открыться сайт.

Войдите в админ-панель: `https://ваш-домен.ru/admin/`

- Логин: `admin` (или ваш `ADMIN_USERNAME`)
- Пароль: ваш `ADMIN_PASSWORD`

---

## 🔧 Шаг 9: Настройка Telegram Login Widget

1. Откройте [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/setdomain`
3. Выберите вашего бота
4. Введите ваш домен (например, `keen.z-ip.pro`)

---

## 🛠️ Полезные команды

```bash
# Статус сервиса
systemctl status cms-site

# Перезапуск
systemctl restart cms-site

# Логи
journalctl -u cms-site -f

# Логи Caddy
journalctl -u caddy -f

# Перезапуск Caddy
systemctl restart caddy

# Обновление сертификатов
systemctl reload caddy
```

---

## 📁 Структура проекта на сервере

```
/opt/cms-site/
├── app.py                  # Главный файл Flask
├── config.py               # Конфигурация
├── models.py               # Модели БД
├── requirements.txt        # Зависимости Python
├── Caddyfile               # Конфигурация Caddy
├── cms-site.service        # Systemd-сервис
├── .env                    # Переменные окружения
├── modules/                # Модули расширения
│   ├── __init__.py
│   └── analytics/
│       └── module.py       # Пример модуля
├── static/                 # Статические файлы
│   ├── css/style.css
│   └── js/
│       ├── stars.js        # Анимация звёзд
│       └── admin.js
├── templates/              # HTML-шаблоны
│   ├── base.html
│   ├── index.html
│   ├── keenetic_models.html
│   ├── vless_reality.html
│   ├── setup_guide.html
│   ├── faq.html
│   ├── login.html
│   ├── profile.html
│   ├── 404.html
│   ├── page.html
│   └── admin/
│       ├── login.html
│       ├── dashboard.html
│       ├── users.html
│       ├── pages_list.html
│       ├── page_edit.html
│       ├── modules.html
│       └── blocks.html
├── uploads/                # Загруженные файлы
└── cms.db                  # База данных SQLite (создаётся автоматически)
```

---

## 📦 Установка дополнительных модулей

1. Создайте папку модуля: `mkdir -p /opt/cms-site/modules/имя_модуля/`
2. Создайте файл `module.py` с классом, наследующим `BaseModule`
3. Перезапустите сервис: `systemctl restart cms-site`

Пример модуля — в `modules/analytics/module.py`.

---

## 🔒 Безопасность

- Установите сложный `SECRET_KEY` (64 символа)
- Используйте надёжный пароль для админ-панели
- Регулярно обновляйте систему: `apt update && apt upgrade -y`
- Настройте брандмауэр: `ufw allow 80/tcp && ufw allow 443/tcp && ufw enable`
- Caddy автоматически обновляет SSL-сертификаты Let's Encrypt

---

## ⚠️ Устранение неполадок

### «502 Bad Gateway»
Проверьте, что Gunicorn запущен: `systemctl status cms-site`

### «Не работает Telegram-вход»
Проверьте:
- `BOT_TOKEN` в `.env` правильный
- Домен привязан к боту через `/setdomain`
- JS-виджет Telegram загружается (проверьте консоль браузера F12)

### «Не сохраняются страницы»
Проверьте права на папку с БД:
```bash
chown www-data:www-data /opt/cms-site
chmod 755 /opt/cms-site
```

### «Ошибка при входе в админ-панель»
Сбросьте пароль администратора:
```bash
cd /opt/cms-site
source venv/bin/activate
python3 -c "
from app import app, db
from models import AdminUser
from werkzeug.security import generate_password_hash
with app.app_context():
    admin = AdminUser.query.filter_by(username='admin').first()
    if admin:
        admin.password_hash = generate_password_hash('новый_пароль')
        db.session.commit()
        print('Пароль изменён')
"
```
