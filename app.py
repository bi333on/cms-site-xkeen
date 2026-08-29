import hashlib
import hmac
import json
import re
import io
import os
import base64
import ipaddress
from datetime import datetime, timezone
from functools import wraps
from urllib.parse import unquote

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, abort, session, g,
)
from flask_login import (
    LoginManager, login_user, logout_user, login_required,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash

import markdown as md_lib
import pyotp
import qrcode
from sqlalchemy import func

from config import config
from models import db, User, AdminUser, Page, CmsModule, EditorBlock, VisitStat, SiteMessage
from modules import module_registry, BaseModule

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
app = Flask(__name__)
app.config.from_object(config)
app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = "login_page"
login_manager.login_message = "Войдите через Telegram для доступа."


# ---------------------------------------------------------------------------
# Jinja globals
# ---------------------------------------------------------------------------
@app.context_processor
def inject_globals():
    return {
        "site_name": config.SITE_NAME,
        "site_url": config.SITE_URL,
        "ym_id": config.YANDEX_METRIKA_ID,
        "ym_webmaster": config.YANDEX_WEBMASTER,
        "bot_username": config.TELEGRAM_BOT_USERNAME,
        "current_year": datetime.now(timezone.utc).year,
        "enabled_modules": _get_enabled_modules(),
        "nav_items": _get_nav_items(),
    }


def _get_enabled_modules():
    """Возвращает список включённых модулей."""
    try:
        db_modules = CmsModule.query.filter_by(is_enabled=True).all()
    except Exception:
        return []
    return db_modules


def _get_nav_items():
    """Собирает пункты меню: статичные + динамические страницы + модули."""
    items = [
        {"label": "Главная", "url": "/"},
        {"label": "Модели", "url": "/models/"},
        {"label": "VLESS + Reality", "url": "/protocol/"},
        {"label": "Инструкция", "url": "/setup/"},
        {"label": "FAQ", "url": "/faq/"},
    ]
    # Динамические страницы, отмеченные «в меню»
    try:
        menu_pages = Page.query.filter_by(
            is_published=True, show_in_menu=True
        ).order_by(Page.sort_order.asc()).all()
        for p in menu_pages:
            items.append({"label": p.menu_label or p.title, "url": f"/{p.slug}/", "slug": p.slug})
    except Exception:
        pass
    # Пункты из модулей
    try:
        for mod in module_registry.get_all().values():
            items.extend(mod.get_nav_items())
    except Exception:
        pass
    return items


# ---------------------------------------------------------------------------
# User loader
# ---------------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------------------
# DB init + seed
# ---------------------------------------------------------------------------
def init_db():
    with app.app_context():
        db.create_all()

        # Админ по умолчанию
        if not AdminUser.query.filter_by(username=config.ADMIN_USERNAME).first():
            admin = AdminUser(
                username=config.ADMIN_USERNAME,
                password_hash=generate_password_hash(config.ADMIN_PASSWORD),
            )
            db.session.add(admin)

        # Системные модули
        _seed_modules()

        # Предустановленные блоки редактора
        _seed_editor_blocks()

        db.session.commit()


def _seed_modules():
    """Регистрирует системные модули в БД."""
    system_modules = [
        {
            "name": "pages",
            "display_name": "Управление страницами",
            "description": "Создание и редактирование страниц сайта с Markdown-редактором",
            "is_enabled": True,
        },
        {
            "name": "users",
            "display_name": "Управление пользователями",
            "description": "Управление Telegram-пользователями, правами доступа",
            "is_enabled": True,
        },
        {
            "name": "seo",
            "display_name": "SEO-инструменты",
            "description": "Мета-теги, sitemap.xml, robots.txt, Яндекс.Вебмастер",
            "is_enabled": True,
        },
        {
            "name": "blocks",
            "display_name": "Блоки редактора",
            "description": "Управление пользовательскими блоками для редактора страниц",
            "is_enabled": True,
        },
        {
            "name": "recaptcha",
            "display_name": "reCAPTCHA v3",
            "description": "Защита админ-панели через Google reCAPTCHA v3. Проверяет каждый вход администратора.",
            "is_enabled": True,
        },
        {
            "name": "config_generator",
            "display_name": "Генератор конфига Xray",
            "description": "Генерация конфига Xray для Keenetic из ссылки подписки (vless/vmess/trojan/ss)",
            "is_enabled": True,
        },
    ]
    for mod_data in system_modules:
        if not CmsModule.query.filter_by(name=mod_data["name"]).first():
            db.session.add(CmsModule(**mod_data))


def _seed_editor_blocks():
    """Создаёт предустановленные блоки для редактора (добавляет недостающие)."""
    default_blocks = [
        {
            "name": "Оранжевая кнопка",
            "block_type": "button",
            "label": "Нажми меня",
            "style_class": "btn-orange",
            "html_template": '<a href="{url}" class="btn {class}">{text}</a>',
            "sort_order": 1,
        },
        {
            "name": "Чёрная кнопка",
            "block_type": "button",
            "label": "Подробнее",
            "style_class": "btn-black",
            "html_template": '<a href="{url}" class="btn {class}">{text}</a>',
            "sort_order": 2,
        },
        {
            "name": "Инфо-блок",
            "block_type": "info_box",
            "label": "Полезная информация",
            "style_class": "info-box",
            "html_template": '<div class="info-box"><strong>💡 {title}</strong><p>{text}</p></div>',
            "sort_order": 3,
        },
        {
            "name": "Предупреждение",
            "block_type": "warning_box",
            "label": "Важное предупреждение",
            "style_class": "warning-box",
            "html_template": '<div class="warning-box"><strong>⚠️ {title}</strong><p>{text}</p></div>',
            "sort_order": 4,
        },
        {
            "name": "CTA-блок",
            "block_type": "cta_box",
            "label": "Призыв к действию",
            "style_class": "cta-box",
            "html_template": '<div class="cta-box"><h3>{title}</h3><p>{text}</p><a href="{url}" class="btn btn-orange btn-lg">{button_text}</a></div>',
            "sort_order": 5,
        },
        {
            "name": "Блок кода",
            "block_type": "code_block",
            "label": "Код",
            "style_class": "code-block",
            "html_template": '<div class="code-block"><pre><code>{text}</code></pre></div>',
            "sort_order": 6,
        },
        {
            "name": "Текстовый блок",
            "block_type": "text_block",
            "label": "Выделенный текст",
            "style_class": "text-highlight",
            "html_template": '<div class="text-block {class}">{text}</div>',
            "sort_order": 7,
        },
        {
            "name": "Цитата",
            "block_type": "quote",
            "label": "Цитата",
            "style_class": "styled-quote",
            "html_template": '<blockquote class="styled-quote"><p>{text}</p><cite>{author}</cite></blockquote>',
            "sort_order": 8,
        },
        {
            "name": "Изображение",
            "block_type": "image",
            "label": "Изображение",
            "style_class": "content-image",
            "html_template": '<img src="{url}" alt="{alt}" class="content-image">',
            "sort_order": 9,
        },
        {
            "name": "Спойлер",
            "block_type": "spoiler",
            "label": "Спойлер",
            "style_class": "spoiler-block",
            "html_template": '<details class="spoiler-block"><summary>{title}</summary><div class="spoiler-content">{text}</div></details>',
            "sort_order": 10,
        },
        {
            "name": "Таблица",
            "block_type": "table",
            "label": "Таблица",
            "style_class": "compare-table",
            "html_template": '<div class="table-wrapper"><table class="compare-table"><thead><tr><th>Заголовок 1</th><th>Заголовок 2</th></tr></thead><tbody><tr><td>Ячейка</td><td>Ячейка</td></tr></tbody></table></div>',
            "sort_order": 11,
        },
        {
            "name": "Якорь",
            "block_type": "anchor",
            "label": "Якорь",
            "style_class": "anchor-point",
            "html_template": '<a id="{anchor}" class="anchor-point"></a>',
            "sort_order": 12,
        },
    ]
    for block_data in default_blocks:
        if not EditorBlock.query.filter_by(name=block_data["name"]).first():
            db.session.add(EditorBlock(**block_data))

    # Удаляем устаревшие блоки кнопок-якорей (заменены обычными кнопками)
    EditorBlock.query.filter(
        EditorBlock.block_type.in_(["button_anchor_orange", "button_anchor_black"])
    ).delete(synchronize_session=False)


# ---------------------------------------------------------------------------
# Статистика посещений
# ---------------------------------------------------------------------------
def get_client_ip() -> str:
    """Определяет IP посетителя (за Caddy reverse proxy)."""
    forwarded = request.headers.get("X-Forwarded-For", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP", "")
    if real_ip:
        return real_ip.strip()
    return request.remote_addr or "unknown"


def is_bot(user_agent: str) -> bool:
    """Грубая проверка на поисковых ботов и краулеров."""
    ua = (user_agent or "").lower()
    bot_keywords = [
        "bot", "crawler", "spider", "yandex", "googlebot", "bingbot",
        "slurp", "duckduckbot", "facebookexternalhit", "whatsapp",
        "telegrambot", "python-requests", "curl", "wget", "httpclient",
    ]
    return any(k in ua for k in bot_keywords)


def is_private_ip(ip: str) -> bool:
    """Проверяет, является ли IP локальным/приватным (нельзя геолоцировать)."""
    try:
        return ipaddress.ip_address(ip).is_private or ipaddress.ip_address(ip).is_loopback
    except ValueError:
        return True


def resolve_geo(ip: str) -> tuple[str, str]:
    """Определяет город и страну по IP через ip-api.com (бесплатно)."""
    # Локальные IP геолоцировать бессмысленно
    if is_private_ip(ip):
        return "Локальный IP", ""

    try:
        import requests as req_lib
        resp = req_lib.get(
            f"http://ip-api.com/json/{ip}",
            params={"fields": "status,country,city,query", "lang": "ru"},
            timeout=5,
        )
        data = resp.json()
        if data.get("status") == "success":
            return data.get("city", "") or "", data.get("country", "") or ""
    except Exception:
        pass
    return "", ""


@app.before_request
def log_visit():
    """Логирует посещения страниц (кроме служебных и ботов)."""
    path = request.path

    # Пропускаем служебные и статические ресурсы
    if path.startswith(("/static/", "/uploads/", "/admin/", "/telegram-auth/")):
        return
    if path in ("/sitemap.xml", "/robots.txt", "/favicon.ico"):
        return
    if any(path.endswith(ext) for ext in (".ico", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".css", ".js", ".woff", ".woff2", ".map")):
        return

    ua = request.headers.get("User-Agent", "")
    if not ua or is_bot(ua):
        return

    ip = get_client_ip()
    try:
        user_id = current_user.id if current_user.is_authenticated else None
    except Exception:
        user_id = None

    try:
        visit = VisitStat(
            ip=ip,
            path=path[:500],
            user_agent=ua[:500],
            referrer=(request.headers.get("Referer") or "")[:500],
            is_authenticated=user_id is not None,
            user_id=user_id,
        )
        db.session.add(visit)
        db.session.commit()
    except Exception:
        db.session.rollback()


# ---------------------------------------------------------------------------
# Telegram auth helpers
# ---------------------------------------------------------------------------
def verify_telegram_data(data: dict) -> bool:
    """Проверка подписи данных от Telegram Login Widget."""
    if not config.BOT_TOKEN:
        return False

    received_hash = data.pop("hash", None)
    if not received_hash:
        return False

    check_list = []
    for key in sorted(data.keys()):
        check_list.append(f"{key}={data[key]}")
    check_string = "\n".join(check_list)

    secret_key = hashlib.sha256(config.BOT_TOKEN.encode()).digest()
    computed_hash = hmac.new(
        secret_key, check_string.encode(), hashlib.sha256
    ).hexdigest()

    return computed_hash == received_hash


def admin_required(f):
    """Декоратор для админ-маршрутов."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("admin_logged_in"):
            if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
                return jsonify({"ok": False, "error": "Требуется авторизация", "redirect": url_for("admin_login_page")}), 401
            return redirect(url_for("admin_login_page"))
        return f(*args, **kwargs)
    return decorated


def page_access_required(f):
    """Проверяет доступ к странице по её access_level."""
    @wraps(f)
    def decorated(*args, **kwargs):
        page_slug = kwargs.get("slug", "")
        page = Page.query.filter_by(slug=page_slug, is_published=True).first()
        if not page:
            abort(404)

        if page.access_level == "auth_only" and not current_user.is_authenticated:
            flash("Эта страница доступна только авторизованным пользователям.", "warning")
            return redirect(url_for("login_page"))
        if page.access_level == "admin_only":
            if not session.get("admin_logged_in"):
                flash("Эта страница доступна только администраторам.", "warning")
                return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated


# =========================================================================
# Public routes
# =========================================================================

@app.route("/")
def index():
    return render_template("index.html", active_page="home")


@app.route("/models/")
def keenetic_models():
    return render_template("keenetic_models.html", active_page="models")


@app.route("/protocol/")
def vless_reality():
    return render_template("vless_reality.html", active_page="protocol")


@app.route("/setup/")
def setup_guide():
    return render_template("setup_guide.html", active_page="setup")


@app.route("/faq/")
def faq():
    return render_template("faq.html", active_page="faq")


# ---------------------------------------------------------------------------
# Telegram Login
# ---------------------------------------------------------------------------

@app.route("/login/")
def login_page():
    if current_user.is_authenticated:
        return redirect(url_for("profile"))
    return render_template("login.html", active_page="login")


@app.route("/telegram-auth/", methods=["POST"])
def telegram_auth():
    data = request.get_json(force=True)
    if not data:
        return jsonify({"ok": False, "error": "No data"}), 400

    if not verify_telegram_data(dict(data)):
        return jsonify({"ok": False, "error": "Invalid signature"}), 403

    tg_id = int(data["id"])
    user = User.query.filter_by(telegram_id=tg_id).first()

    if not user:
        user = User(
            telegram_id=tg_id,
            username=data.get("username", ""),
            first_name=data.get("first_name", ""),
            last_name=data.get("last_name", ""),
            photo_url=data.get("photo_url", ""),
        )
        db.session.add(user)
        db.session.commit()

    user.last_login = datetime.now(timezone.utc)
    user.username = data.get("username", user.username)
    user.first_name = data.get("first_name", user.first_name)
    user.last_name = data.get("last_name", user.last_name)
    user.photo_url = data.get("photo_url", user.photo_url)
    db.session.commit()

    login_user(user, remember=True)
    return jsonify({"ok": True, "redirect": url_for("profile")})


@app.route("/logout/")
@login_required
def logout():
    logout_user()
    flash("Вы вышли из аккаунта.", "info")
    return redirect(url_for("index"))


@app.route("/profile/")
@login_required
def profile():
    return render_template("profile.html", active_page="profile")


# =========================================================================
# Admin routes
# =========================================================================

@app.route("/admin/")
def admin_login_page():
    return render_template("admin/login.html")


@app.route("/admin/login/", methods=["POST"])
def admin_login():
    data = request.get_json(force=True)
    username = data.get("username", "").strip()
    password = data.get("password", "")

    # Проверка reCAPTCHA v3 (если настроена и модуль включён)
    recaptcha_enabled = (
        config.RECAPTCHA_SITE_KEY
        and config.RECAPTCHA_SECRET_KEY
        and CmsModule.query.filter_by(name="recaptcha", is_enabled=True).first() is not None
    )
    recaptcha_token = data.get("recaptcha_token", "")
    if recaptcha_enabled:
        if not recaptcha_token:
            return jsonify({"ok": False, "error": "Проверка reCAPTCHA не пройдена — токен отсутствует"}), 403
        try:
            import requests as req_lib
            resp = req_lib.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": config.RECAPTCHA_SECRET_KEY,
                    "response": recaptcha_token,
                },
                timeout=5,
            )
            result = resp.json()
            if not result.get("success"):
                return jsonify({"ok": False, "error": "reCAPTCHA не пройдена"}), 403
            if result.get("score", 0.0) < config.RECAPTCHA_SCORE_THRESHOLD:
                return jsonify({"ok": False, "error": "Подозрительная активность. Попробуйте позже."}), 403
        except Exception as e:
            # Ошибка сети — не блокируем вход
            pass

    admin_user = AdminUser.query.filter_by(username=username).first()
    if admin_user and check_password_hash(admin_user.password_hash, password):
        # Если включён 2FA — требуем код
        if admin_user.totp_enabled:
            session["admin_2fa_pending_id"] = admin_user.id
            session["admin_2fa_username"] = username
            return jsonify({"ok": True, "needs_2fa": True})

        session["admin_logged_in"] = True
        session["admin_username"] = username
        return jsonify({"ok": True, "redirect": url_for("admin_dashboard")})

    return jsonify({"ok": False, "error": "Неверный логин или пароль"}), 401


@app.route("/admin/2fa/verify/", methods=["POST"])
def admin_2fa_verify():
    """Проверка кода 2FA (второй шаг входа)."""
    data = request.get_json(force=True) or {}
    code = (data.get("code") or "").strip()

    admin_id = session.get("admin_2fa_pending_id")
    if not admin_id:
        return jsonify({"ok": False, "error": "Сессия истекла. Войдите заново."}), 401

    admin_user = db.session.get(AdminUser, int(admin_id))
    if not admin_user or not admin_user.totp_enabled or not admin_user.totp_secret:
        return jsonify({"ok": False, "error": "2FA не настроен"}), 400

    totp = pyotp.TOTP(admin_user.totp_secret)
    if not totp.verify(code, valid_window=1):
        return jsonify({"ok": False, "error": "Неверный код. Попробуйте снова."}), 401

    session.pop("admin_2fa_pending_id", None)
    session.pop("admin_2fa_username", None)
    session["admin_logged_in"] = True
    session["admin_username"] = admin_user.username
    return jsonify({"ok": True, "redirect": url_for("admin_dashboard")})


@app.route("/admin/2fa/setup/")
@admin_required
def admin_2fa_setup_page():
    """Страница настройки 2FA с QR-кодом."""
    return render_template("admin/2fa_setup.html")


@app.route("/admin/2fa/setup/start/", methods=["POST"])
@admin_required
def admin_2fa_setup_start():
    """Генерирует секрет 2FA и возвращает QR-код + секрет."""
    username = session.get("admin_username", "admin")
    admin_user = AdminUser.query.filter_by(username=username).first()
    if not admin_user:
        return jsonify({"ok": False, "error": "Администратор не найден"}), 404

    if admin_user.totp_enabled:
        return jsonify({"ok": False, "error": "2FA уже включён"}), 400

    # Генерируем секрет (сохраняем в сессии до подтверждения)
    secret = session.get("admin_2fa_secret")
    if not secret:
        secret = pyotp.random_base32()
        session["admin_2fa_secret"] = secret

    issuer = config.SITE_NAME
    provisioning_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=username, issuer_name=issuer
    )

    # Генерируем QR-код в base64
    qr = qrcode.QRCode(box_size=6, border=2)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()

    return jsonify({
        "ok": True,
        "secret": secret,
        "provisioning_uri": provisioning_uri,
        "qr_b64": f"data:image/png;base64,{qr_b64}",
    })


@app.route("/admin/2fa/setup/confirm/", methods=["POST"])
@admin_required
def admin_2fa_setup_confirm():
    """Подтверждает включение 2FA проверкой кода."""
    data = request.get_json(force=True) or {}
    code = (data.get("code") or "").strip()

    secret = session.get("admin_2fa_secret")
    if not secret:
        return jsonify({"ok": False, "error": "Сначала сгенерируйте секрет"}), 400

    totp = pyotp.TOTP(secret)
    if not totp.verify(code, valid_window=1):
        return jsonify({"ok": False, "error": "Неверный код. Попробуйте снова."}), 401

    username = session.get("admin_username", "admin")
    admin_user = AdminUser.query.filter_by(username=username).first()
    if not admin_user:
        return jsonify({"ok": False, "error": "Администратор не найден"}), 404

    admin_user.totp_secret = secret
    admin_user.totp_enabled = True
    db.session.commit()

    session.pop("admin_2fa_secret", None)
    return jsonify({"ok": True, "message": "2FA успешно включён"})


@app.route("/admin/2fa/disable/", methods=["POST"])
@admin_required
def admin_2fa_disable():
    """Отключает 2FA."""
    username = session.get("admin_username", "admin")
    admin_user = AdminUser.query.filter_by(username=username).first()
    if admin_user:
        admin_user.totp_secret = None
        admin_user.totp_enabled = False
        db.session.commit()
        return jsonify({"ok": True})
    return jsonify({"ok": False, "error": "Администратор не найден"}), 404


@app.route("/admin/logout/")
def admin_logout():
    session.pop("admin_logged_in", None)
    session.pop("admin_username", None)
    return redirect(url_for("admin_login_page"))


@app.route("/admin/dashboard/")
@admin_required
def admin_dashboard():
    total = User.query.count()
    active = User.query.filter_by(is_active=True).count()
    today = datetime.now(timezone.utc).date()
    today_users = User.query.filter(
        User.registered_at >= datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    ).count()
    pages_count = Page.query.count()
    modules_count = CmsModule.query.count()
    visits_count = VisitStat.query.count()

    # Статус 2FA текущего админа
    admin_username = session.get("admin_username", "")
    admin_user = AdminUser.query.filter_by(username=admin_username).first()
    totp_enabled = admin_user.totp_enabled if admin_user else False

    return render_template(
        "admin/dashboard.html",
        total=total,
        active=active,
        today_users=today_users,
        pages_count=pages_count,
        modules_count=modules_count,
        visits_count=visits_count,
        totp_enabled=totp_enabled,
    )


# =========================================================================
# Admin — Users
# =========================================================================

@app.route("/admin/users/")
@admin_required
def admin_users():
    return render_template("admin/users.html")


@app.route("/admin/api/users/")
@admin_required
def admin_api_users():
    users = User.query.order_by(User.registered_at.desc()).all()
    result = []
    for u in users:
        result.append({
            "id": u.id,
            "telegram_id": u.telegram_id,
            "username": u.username or "",
            "first_name": u.first_name or "",
            "last_name": u.last_name or "",
            "photo_url": u.photo_url or "",
            "registered_at": u.registered_at.strftime("%d.%m.%Y %H:%M") if u.registered_at else "",
            "last_login": u.last_login.strftime("%d.%m.%Y %H:%M") if u.last_login else "",
            "is_active": u.is_active,
            "is_admin": u.is_admin,
        })
    return jsonify(result)


@app.route("/admin/api/users/<int:user_id>/toggle-active/", methods=["POST"])
@admin_required
def admin_toggle_active(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    return jsonify({"ok": True, "is_active": user.is_active})


@app.route("/admin/api/users/<int:user_id>/toggle-admin/", methods=["POST"])
@admin_required
def admin_toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    user.is_admin = not user.is_admin
    db.session.commit()
    return jsonify({"ok": True, "is_admin": user.is_admin})


@app.route("/admin/api/users/<int:user_id>/delete/", methods=["DELETE"])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"ok": True})


# =========================================================================
# Admin — Pages CRUD
# =========================================================================

@app.route("/admin/pages/")
@admin_required
def admin_pages():
    pages = Page.query.order_by(Page.sort_order.asc(), Page.updated_at.desc()).all()
    return render_template("admin/pages_list.html", pages=pages)


@app.route("/admin/pages/new/", methods=["GET", "POST"])
@admin_required
def admin_page_new():
    if request.method == "POST":
        try:
            data = request.get_json(force=True) or {}
        except Exception:
            return jsonify({"ok": False, "error": "Неверный формат данных"}), 400

        try:
            slug = (data.get("slug", "") or "").strip().lower()
            slug = slug.replace(" ", "-")
            slug = re.sub(r"[^a-z0-9\-]", "", slug)
            slug = slug.strip("-") or "untitled"

            if Page.query.filter_by(slug=slug).first():
                base = slug
                n = 2
                while Page.query.filter_by(slug=f"{base}-{n}").first():
                    n += 1
                slug = f"{base}-{n}"

            page = Page(
                title=data.get("title", "Новая страница"),
                slug=slug,
                meta_description=data.get("meta_description", ""),
                meta_keywords=data.get("meta_keywords", ""),
                content=data.get("content", ""),
                is_published=data.get("is_published", False),
                access_level=data.get("access_level", "public"),
                noindex=data.get("noindex", False),
                show_in_menu=data.get("show_in_menu", False),
                menu_label=data.get("menu_label", ""),
                sort_order=data.get("sort_order", 0),
            )
            db.session.add(page)
            db.session.commit()
            # Уведомляем поисковики о новой странице
            if page.is_published and page.access_level == "public" and not page.noindex:
                indexnow_notify([f"/{page.slug}/"])
            return jsonify({"ok": True, "redirect": url_for("admin_page_edit", page_id=page.id)})
        except Exception as e:
            db.session.rollback()
            return jsonify({"ok": False, "error": f"Ошибка сохранения: {e}"}), 500

    blocks = EditorBlock.query.filter_by(is_active=True).order_by(EditorBlock.sort_order).all()
    return render_template("admin/page_edit.html", page=None, blocks=blocks)


@app.route("/admin/pages/<int:page_id>/edit/", methods=["GET", "POST"])
@admin_required
def admin_page_edit(page_id):
    page = Page.query.get_or_404(page_id)

    if request.method == "POST":
        try:
            data = request.get_json(force=True) or {}
        except Exception:
            return jsonify({"ok": False, "error": "Неверный формат данных"}), 400

        try:
            page.title = data.get("title", page.title)
            new_slug = (data.get("slug", page.slug) or "").strip().lower()
            new_slug = new_slug.replace(" ", "-")
            new_slug = re.sub(r"[^a-z0-9\-]", "", new_slug)
            new_slug = new_slug.strip("-") or page.slug

            if new_slug != page.slug:
                existing = Page.query.filter_by(slug=new_slug).first()
                if existing and existing.id != page.id:
                    new_slug = f"{new_slug}-{page.id}"

            page.slug = new_slug
            page.meta_description = data.get("meta_description", page.meta_description)
            page.meta_keywords = data.get("meta_keywords", page.meta_keywords)
            page.content = data.get("content", page.content)
            page.is_published = data.get("is_published", page.is_published)
            page.access_level = data.get("access_level", page.access_level)
            page.noindex = data.get("noindex", page.noindex)
            page.show_in_menu = data.get("show_in_menu", page.show_in_menu)
            page.menu_label = data.get("menu_label", page.menu_label)
            page.sort_order = data.get("sort_order", page.sort_order)
            db.session.commit()
            # Уведомляем поисковики об изменении страницы
            if page.is_published and page.access_level == "public" and not page.noindex:
                indexnow_notify([f"/{page.slug}/"])
            return jsonify({"ok": True, "slug": page.slug})
        except Exception as e:
            db.session.rollback()
            return jsonify({"ok": False, "error": f"Ошибка сохранения: {e}"}), 500

    blocks = EditorBlock.query.filter_by(is_active=True).order_by(EditorBlock.sort_order).all()
    return render_template("admin/page_edit.html", page=page, blocks=blocks)


@app.route("/admin/pages/<int:page_id>/delete/", methods=["POST"])
@admin_required
def admin_page_delete(page_id):
    page = Page.query.get_or_404(page_id)
    deleted_slug = page.slug
    db.session.delete(page)
    db.session.commit()
    # Уведомляем поисковики об удалении страницы
    indexnow_notify([f"/{deleted_slug}/"])
    return jsonify({"ok": True})


# =========================================================================
# Admin — Modules
# =========================================================================

@app.route("/admin/modules/")
@admin_required
def admin_modules():
    db_modules = CmsModule.query.order_by(CmsModule.name).all()
    return render_template("admin/modules.html", modules=db_modules)


@app.route("/admin/api/modules/")
@admin_required
def admin_api_modules():
    db_modules = CmsModule.query.order_by(CmsModule.name).all()
    result = []
    for m in db_modules:
        result.append({
            "id": m.id,
            "name": m.name,
            "display_name": m.display_name,
            "description": m.description,
            "version": m.version,
            "author": m.author,
            "is_enabled": m.is_enabled,
        })
    return jsonify(result)


@app.route("/admin/api/modules/<int:module_id>/toggle/", methods=["POST"])
@admin_required
def admin_toggle_module(module_id):
    mod = CmsModule.query.get_or_404(module_id)
    mod.is_enabled = not mod.is_enabled
    db.session.commit()
    return jsonify({"ok": True, "is_enabled": mod.is_enabled})


# =========================================================================
# Admin — Статистика посещений
# =========================================================================

@app.route("/admin/stats/")
@admin_required
def admin_stats():
    total = VisitStat.query.count()
    unique_ips = db.session.query(
        func.count(func.distinct(VisitStat.ip))
    ).scalar() or 0

    today = datetime.now(timezone.utc).date()
    today_visits = VisitStat.query.filter(
        VisitStat.created_at >= datetime(today.year, today.month, today.day, tzinfo=timezone.utc)
    ).count()

    # Топ страниц
    top_pages = db.session.query(
        VisitStat.path, func.count(VisitStat.id).label("cnt")
    ).group_by(VisitStat.path).order_by(func.count(VisitStat.id).desc()).limit(10).all()

    # Топ городов
    top_cities = db.session.query(
        VisitStat.city, func.count(VisitStat.id).label("cnt")
    ).filter(VisitStat.city != "").group_by(VisitStat.city).order_by(
        func.count(VisitStat.id).desc()
    ).limit(10).all()

    # Объединённые визиты: группировка по IP + странице с количеством
    grouped_visits = db.session.query(
        VisitStat.ip,
        VisitStat.path,
        func.count(VisitStat.id).label("cnt"),
        func.max(VisitStat.created_at).label("last_seen"),
    ).group_by(VisitStat.ip, VisitStat.path).order_by(
        func.max(VisitStat.created_at).desc()
    ).limit(200).all()

    # Разрешаем гео для уникальных IP из сгруппированного списка
    geo_cache: dict[str, tuple[str, str]] = {}
    changed = False
    for row in grouped_visits:
        ip = row[0]
        if ip in geo_cache or is_private_ip(ip):
            continue
        existing = db.session.query(VisitStat.city, VisitStat.country).filter(
            VisitStat.ip == ip, VisitStat.city != ""
        ).first()
        if existing:
            geo_cache[ip] = (existing[0], existing[1])
        else:
            city, country = resolve_geo(ip)
            geo_cache[ip] = (city, country)
            if city:
                VisitStat.query.filter_by(ip=ip).update(
                    {"city": city, "country": country}
                )
                changed = True
    if changed:
        db.session.commit()

    return render_template(
        "admin/stats.html",
        total=total,
        unique_ips=unique_ips,
        today_visits=today_visits,
        grouped_visits=grouped_visits,
        geo_cache=geo_cache,
        top_pages=top_pages,
        top_cities=top_cities,
    )


# =========================================================================
# Admin — Сообщения для пользователей
# =========================================================================

@app.route("/admin/messages/")
@admin_required
def admin_messages():
    messages = SiteMessage.query.order_by(SiteMessage.created_at.desc()).all()
    return render_template("admin/messages.html", messages=messages)


@app.route("/admin/messages/new/", methods=["POST"])
@admin_required
def admin_message_new():
    data = request.get_json(force=True) or {}
    try:
        msg = SiteMessage(
            title=data.get("title", "").strip(),
            content=data.get("content", "").strip(),
            is_active=data.get("is_active", False),
            repeat_hours=int(data.get("repeat_hours", 3) or 3),
            show_delay=int(data.get("show_delay", 0) or 0),
        )
        db.session.add(msg)
        db.session.commit()
        return jsonify({"ok": True, "redirect": url_for("admin_messages")})
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": f"Ошибка сохранения: {e}"}), 500


@app.route("/admin/messages/<int:msg_id>/edit/", methods=["POST"])
@admin_required
def admin_message_edit(msg_id):
    msg = SiteMessage.query.get_or_404(msg_id)
    data = request.get_json(force=True) or {}
    try:
        msg.title = data.get("title", msg.title).strip()
        msg.content = data.get("content", msg.content).strip()
        msg.is_active = data.get("is_active", msg.is_active)
        msg.repeat_hours = int(data.get("repeat_hours", msg.repeat_hours or 3) or 3)
        msg.show_delay = int(data.get("show_delay", msg.show_delay or 0) or 0)
        db.session.commit()
        return jsonify({"ok": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": f"Ошибка сохранения: {e}"}), 500


@app.route("/admin/messages/<int:msg_id>/toggle/", methods=["POST"])
@admin_required
def admin_message_toggle(msg_id):
    msg = SiteMessage.query.get_or_404(msg_id)
    msg.is_active = not msg.is_active
    db.session.commit()
    return jsonify({"ok": True, "is_active": msg.is_active})


@app.route("/admin/messages/<int:msg_id>/delete/", methods=["POST"])
@admin_required
def admin_message_delete(msg_id):
    msg = SiteMessage.query.get_or_404(msg_id)
    db.session.delete(msg)
    db.session.commit()
    return jsonify({"ok": True})


# Публичный API: возвращает активное сообщение для попапа
@app.route("/api/announcement/")
def api_announcement():
    msg = SiteMessage.query.filter_by(is_active=True).order_by(
        SiteMessage.created_at.desc()
    ).first()
    if msg:
        return jsonify({
            "ok": True,
            "id": msg.id,
            "title": msg.title,
            "content": msg.content,
            "repeat_hours": msg.repeat_hours or 3,
            "show_delay": msg.show_delay or 0,
        })
    return jsonify({"ok": False})


# =========================================================================
# Admin — Editor Blocks
# =========================================================================

@app.route("/admin/blocks/")
@admin_required
def admin_blocks():
    blocks = EditorBlock.query.order_by(EditorBlock.sort_order).all()
    return render_template("admin/blocks.html", blocks=blocks)


@app.route("/admin/api/blocks/")
@admin_required
def admin_api_blocks():
    blocks = EditorBlock.query.order_by(EditorBlock.sort_order).all()
    result = []
    for b in blocks:
        result.append({
            "id": b.id,
            "name": b.name,
            "block_type": b.block_type,
            "label": b.label,
            "style_class": b.style_class,
            "html_template": b.html_template,
            "sort_order": b.sort_order,
            "is_active": b.is_active,
        })
    return jsonify(result)


@app.route("/admin/api/blocks/<int:block_id>/toggle/", methods=["POST"])
@admin_required
def admin_toggle_block(block_id):
    block = EditorBlock.query.get_or_404(block_id)
    block.is_active = not block.is_active
    db.session.commit()
    return jsonify({"ok": True, "is_active": block.is_active})


# =========================================================================
# IndexNow (ускоренная индексация Яндекс/Bing)
# =========================================================================

def indexnow_host() -> str:
    """Возвращает хост без протокола для IndexNow."""
    return config.SITE_URL.replace("https://", "").replace("http://", "").rstrip("/")


def indexnow_notify(urls: list[str]):
    """Уведомляет Яндекс и Bing об изменении страниц через IndexNow."""
    if not urls:
        return
    payload = {
        "host": indexnow_host(),
        "key": config.INDEXNOW_KEY,
        "urlList": urls,
    }
    endpoints = [
        "https://api.indexnow.org/indexnow",
        "https://yandex.com/indexnow",
    ]
    for ep in endpoints:
        try:
            import requests as req_lib
            req_lib.post(ep, json=payload, timeout=5)
        except Exception:
            pass


@app.route("/<key>.txt")
def indexnow_key_file(key):
    """Отдаёт ключ IndexNow: https://site/{key}.txt"""
    if key == config.INDEXNOW_KEY:
        return config.INDEXNOW_KEY, 200, {"Content-Type": "text/plain"}
    abort(404)


# =========================================================================
# Sitemap & robots
# =========================================================================

@app.route("/sitemap.xml")
def sitemap():
    static_pages = [
        {"loc": "/", "priority": "1.0"},
        {"loc": "/models/", "priority": "0.9"},
        {"loc": "/protocol/", "priority": "0.9"},
        {"loc": "/setup/", "priority": "0.8"},
        {"loc": "/faq/", "priority": "0.7"},
        {"loc": "/generator/", "priority": "0.8"},
    ]
    dynamic_pages = Page.query.filter_by(is_published=True).filter(
        Page.access_level == "public", Page.noindex == False
    ).all()
    for p in dynamic_pages:
        static_pages.append({"loc": f"/{p.slug}/", "priority": "0.6"})

    sitemap_xml = '<?xml version="1.0" encoding="UTF-8"?>\n'
    sitemap_xml += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    for p in static_pages:
        sitemap_xml += "  <url>\n"
        sitemap_xml += f"    <loc>{config.SITE_URL}{p['loc']}</loc>\n"
        sitemap_xml += f"    <priority>{p['priority']}</priority>\n"
        sitemap_xml += "  </url>\n"
    sitemap_xml += "</urlset>"
    return app.response_class(sitemap_xml, mimetype="application/xml")


@app.route("/robots.txt")
def robots():
    content = (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /admin\n"
        "Disallow: /login/\n"
        "Disallow: /profile/\n"
        "Disallow: /logout/\n"
        "Disallow: /telegram-auth/\n"
        "Disallow: /static/\n"
        "Disallow: /uploads/\n"
        "Allow: /static/images/favicon\n"
        "Allow: /favicon.ico\n"
        "Allow: /apple-touch-icon.png\n"
        f"Sitemap: {config.SITE_URL}/sitemap.xml\n"
        "Host: " + config.SITE_URL.replace("https://", "") + "\n"
    )
    return app.response_class(content, mimetype="text/plain")


@app.route("/favicon.ico")
def favicon():
    """Отдаёт favicon.ico из корня (проверяется краулерами Яндекс/Google)."""
    from flask import send_from_directory
    return send_from_directory(
        os.path.join(app.root_path, "static", "images"),
        "favicon.ico",
        mimetype="image/x-icon",
    )


@app.route("/apple-touch-icon.png")
def apple_touch_icon():
    """Отдаёт иконку для iOS/Android из корня."""
    from flask import send_from_directory
    return send_from_directory(
        os.path.join(app.root_path, "static", "images"),
        "apple-touch-icon.png",
        mimetype="image/png",
    )


# =========================================================================
# Dynamic pages (catch-all)
# =========================================================================

@app.route("/<path:slug>/")
def dynamic_page(slug):
    slug = slug.rstrip("/")

    # Ищем опубликованную страницу
    page = Page.query.filter_by(slug=slug, is_published=True).first()
    if page:
        # Проверка доступа
        if page.access_level == "auth_only" and not current_user.is_authenticated:
            flash("Эта страница доступна только авторизованным пользователям.", "warning")
            return redirect(url_for("login_page"))
        if page.access_level == "admin_only" and not session.get("admin_logged_in"):
            abort(404)

        # Render Markdown content
        html_content = md_lib.markdown(
            page.content,
            extensions=["extra", "codehilite"],
        )
        return render_template("page.html", page=page, html_content=html_content)

    # Не опубликована → 301
    unpublished = Page.query.filter_by(slug=slug, is_published=False).first()
    if unpublished:
        return redirect("/", code=301)

    # Похожие страницы
    similar = Page.query.filter_by(is_published=True).order_by(Page.sort_order.asc()).limit(5).all()
    return render_template("404.html", similar_pages=similar), 404


# =========================================================================
# Error pages
# =========================================================================

@app.errorhandler(404)
def not_found(_e):
    similar = Page.query.filter_by(is_published=True).order_by(Page.sort_order.asc()).limit(5).all()
    return render_template("404.html", similar_pages=similar), 404


@app.errorhandler(500)
def server_error(_e):
    return render_template("base.html", error_code=500), 500


# =========================================================================
# Миграция БД (добавление новых колонок в существующие таблицы)
# =========================================================================
def migrate_db():
    """Добавляет отсутствующие колонки в существующие таблицы (SQLite)."""
    try:
        from sqlalchemy import inspect, text
        inspector = inspect(db.engine)
        existing_tables = inspector.get_table_names()

        if "admin_users" in existing_tables:
            cols = {c["name"] for c in inspector.get_columns("admin_users")}
            with db.engine.begin() as conn:
                if "totp_secret" not in cols:
                    conn.execute(text("ALTER TABLE admin_users ADD COLUMN totp_secret VARCHAR(64)"))
                if "totp_enabled" not in cols:
                    conn.execute(text("ALTER TABLE admin_users ADD COLUMN totp_enabled BOOLEAN DEFAULT 0"))

        if "pages" in existing_tables:
            cols = {c["name"] for c in inspector.get_columns("pages")}
            with db.engine.begin() as conn:
                if "noindex" not in cols:
                    conn.execute(text("ALTER TABLE pages ADD COLUMN noindex BOOLEAN DEFAULT 0"))
                if "show_in_menu" not in cols:
                    conn.execute(text("ALTER TABLE pages ADD COLUMN show_in_menu BOOLEAN DEFAULT 0"))
                if "menu_label" not in cols:
                    conn.execute(text("ALTER TABLE pages ADD COLUMN menu_label VARCHAR(64) DEFAULT ''"))

        if "site_messages" in existing_tables:
            cols = {c["name"] for c in inspector.get_columns("site_messages")}
            with db.engine.begin() as conn:
                if "repeat_hours" not in cols:
                    conn.execute(text("ALTER TABLE site_messages ADD COLUMN repeat_hours INTEGER DEFAULT 3"))
                if "show_delay" not in cols:
                    conn.execute(text("ALTER TABLE site_messages ADD COLUMN show_delay INTEGER DEFAULT 0"))
    except Exception as e:
        app.logger.warning(f"Миграция БД пропущена: {e}")


# =========================================================================
# Main
# =========================================================================

# Авто-инициализация БД при любом способе запуска (python app.py / flask run / gunicorn)
with app.app_context():
    db.create_all()
    migrate_db()
    _seed_modules()
    _seed_editor_blocks()
    db.session.commit()
    # Обнаружение и регистрация внешних модулей
    module_registry.discover_modules(app)

if __name__ == "__main__":
    app.run(debug=False, host="127.0.0.1", port=5000)
