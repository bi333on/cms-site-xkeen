import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    SECRET_KEY: str = field(default_factory=lambda: os.getenv("SECRET_KEY", ""))
    SQLALCHEMY_DATABASE_URI: str = os.getenv("DATABASE_URL", "sqlite:///cms.db")
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin123")

    TELEGRAM_BOT_USERNAME: str = os.getenv("TELEGRAM_BOT_USERNAME", "YourBot")

    SITE_URL: str = os.getenv("SITE_URL", "https://keen.z-ip.pro")
    SITE_NAME: str = "Настройка Keenetic VLESS Reality"

    YANDEX_METRIKA_ID: str = os.getenv("YANDEX_METRIKA_ID", "")
    YANDEX_WEBMASTER: str = os.getenv("YANDEX_WEBMASTER", "")

    # IndexNow (ускоренная индексация Яндекс/Bing)
    INDEXNOW_KEY: str = os.getenv("INDEXNOW_KEY", "")

    # reCAPTCHA v3
    RECAPTCHA_SITE_KEY: str = os.getenv("RECAPTCHA_SITE_KEY", "")
    RECAPTCHA_SECRET_KEY: str = os.getenv("RECAPTCHA_SECRET_KEY", "")
    RECAPTCHA_SCORE_THRESHOLD: float = float(os.getenv("RECAPTCHA_SCORE_THRESHOLD", "0.5"))

    # Модули CMS
    CMS_MODULES: list = field(default_factory=lambda: [
        "pages",     # Управление страницами
        "users",     # Управление пользователями
        "seo",       # SEO-инструменты
    ])

    def __post_init__(self) -> None:
        if not self.SECRET_KEY or self.SECRET_KEY == "change-me-in-production-!@#$%":
            import secrets
            object.__setattr__(self, "SECRET_KEY", secrets.token_hex(32))
        if not self.INDEXNOW_KEY:
            import secrets
            object.__setattr__(self, "INDEXNOW_KEY", secrets.token_hex(16))


config = Config()
