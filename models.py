from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()


# =========================================================================
# Telegram Users
# =========================================================================
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    telegram_id = db.Column(db.BigInteger, unique=True, nullable=False, index=True)
    username = db.Column(db.String(64), nullable=True)
    first_name = db.Column(db.String(64), nullable=True)
    last_name = db.Column(db.String(64), nullable=True)
    photo_url = db.Column(db.String(256), nullable=True)
    registered_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime, nullable=True)

    def get_id(self):
        return str(self.id)

    def __repr__(self):
        return f"<User {self.username or self.telegram_id}>"


# =========================================================================
# Admin Users (password-based for /admin)
# =========================================================================
class AdminUser(UserMixin, db.Model):
    __tablename__ = "admin_users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    # 2FA (Google Authenticator / TOTP)
    totp_secret = db.Column(db.String(64), nullable=True)
    totp_enabled = db.Column(db.Boolean, default=False)

    def get_id(self):
        return str(self.id)


# =========================================================================
# Pages (CMS content)
# =========================================================================
class Page(db.Model):
    __tablename__ = "pages"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    slug = db.Column(db.String(128), unique=True, nullable=False, index=True)
    meta_description = db.Column(db.String(320), default="")
    meta_keywords = db.Column(db.String(512), default="")
    content = db.Column(db.Text, default="")
    is_published = db.Column(db.Boolean, default=False)
    # Ограничение доступа: 'public', 'auth_only', 'admin_only'
    access_level = db.Column(db.String(20), default="public")
    # Не индексировать страницу (noindex)
    noindex = db.Column(db.Boolean, default=False)
    # Показывать в главном меню
    show_in_menu = db.Column(db.Boolean, default=False)
    # Короткая надпись кнопки в меню (если пусто — берётся title)
    menu_label = db.Column(db.String(64), default="")
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<Page {self.slug}>"


# =========================================================================
# Modules (CMS modular system)
# =========================================================================
class CmsModule(db.Model):
    __tablename__ = "cms_modules"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True, nullable=False)
    display_name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.String(512), default="")
    version = db.Column(db.String(16), default="1.0.0")
    author = db.Column(db.String(128), default="CMS")
    is_enabled = db.Column(db.Boolean, default=False)
    config_json = db.Column(db.Text, default="{}")
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<CmsModule {self.name}>"


# =========================================================================
# Custom Buttons / Blocks for editor
# =========================================================================
class EditorBlock(db.Model):
    __tablename__ = "editor_blocks"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    block_type = db.Column(db.String(32), nullable=False)  # button, info_box, warning_box, cta_box, code_block, text_block
    label = db.Column(db.String(256), default="")
    style_class = db.Column(db.String(64), default="")  # btn-orange, btn-black, etc.
    html_template = db.Column(db.Text, default="")
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<EditorBlock {self.name}>"


# =========================================================================
# Visitor statistics
# =========================================================================
class VisitStat(db.Model):
    __tablename__ = "visit_stats"

    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(45), index=True)
    city = db.Column(db.String(128), default="")
    country = db.Column(db.String(64), default="")
    path = db.Column(db.String(512), default="/")
    user_agent = db.Column(db.String(512), default="")
    referrer = db.Column(db.String(512), default="")
    is_authenticated = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, nullable=True)
    created_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        index=True,
    )

    def __repr__(self):
        return f"<VisitStat {self.ip} {self.path}>"


# =========================================================================
# Site messages (announcements for users)
# =========================================================================
class SiteMessage(db.Model):
    __tablename__ = "site_messages"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), default="")
    content = db.Column(db.Text, default="")
    is_active = db.Column(db.Boolean, default=False)
    # Период повторного показа (в часах)
    repeat_hours = db.Column(db.Integer, default=3)
    # Отсрочка показа после входа (в секундах)
    show_delay = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self):
        return f"<SiteMessage {self.title}>"


# =========================================================================
# Generated configs (from generator page)
# =========================================================================
class GeneratedConfig(db.Model):
    __tablename__ = "generated_configs"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.Text, unique=True, nullable=False)  # ссылка подписки
    protocol = db.Column(db.String(16), default="")
    address = db.Column(db.String(256), default="")
    port = db.Column(db.Integer, default=0)
    config_json = db.Column(db.Text, default="")
    # Результат TCP-пинга
    ping_ok = db.Column(db.Boolean, default=False)
    ping_time = db.Column(db.Integer, nullable=True)  # мс
    # Локация сервера
    country = db.Column(db.String(64), default="")
    city = db.Column(db.String(128), default="")
    checked_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return f"<GeneratedConfig {self.protocol} {self.address}>"
