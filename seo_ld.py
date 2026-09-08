"""
Микроразметка JSON-LD (schema.org) для Яндекса и Google.

Модуль содержит:
- функции-хелперы, возвращающие словари JSON-LD;
- единый источник данных для FAQ и HowTo (чтобы HTML и разметка не расходились).

Использование в шаблонах Jinja:
    <script type="application/ld+json">{{ breadcrumb_ld(...) | tojson }}</script>
"""

from config import config

SITE_NAME = "VLESS-Keenetic"
SITE_ORG = "VLESS-Keenetic"
LOGO_URL = f"{config.SITE_URL}/static/images/favicon.svg"


# ---------------------------------------------------------------------------
# Организация и сайт (глобальные, подключаются в base.html)
# ---------------------------------------------------------------------------

def organization_ld() -> dict:
    """Organization — описание организации/площадки."""
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": SITE_ORG,
        "url": config.SITE_URL,
        "logo": LOGO_URL,
        "sameAs": [
            "https://t.me/s_zipok_bot",
            "https://t.me/zipok_bot",
        ],
    }


def website_ld() -> dict:
    """WebSite — описание сайта."""
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": config.SITE_NAME,
        "alternateName": "Настройка Keenetic VLESS Reality",
        "url": config.SITE_URL,
        "inLanguage": "ru",
        "publisher": {
            "@type": "Organization",
            "name": SITE_ORG,
            "url": config.SITE_URL,
        },
    }


# ---------------------------------------------------------------------------
# Хлебные крошки
# ---------------------------------------------------------------------------

def breadcrumb_ld(items: list[tuple[str, str]]) -> dict:
    """BreadcrumbList.

    items — список кортежей (название, url) от корня к текущей странице.
    """
    item_list = []
    for i, (name, url) in enumerate(items, start=1):
        item_list.append({
            "@type": "ListItem",
            "position": i,
            "name": name,
            "item": url,
        })
    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": item_list,
    }


# ---------------------------------------------------------------------------
# Статьи / технические материалы
# ---------------------------------------------------------------------------

def tech_article_ld(headline: str, description: str, url: str,
                    date_published: str = "2026-08-01",
                    date_modified: str = "2026-08-01") -> dict:
    """TechArticle — техническая статья (главная, протокол, модели, страницы)."""
    return {
        "@context": "https://schema.org",
        "@type": "TechArticle",
        "headline": headline,
        "description": description,
        "url": url,
        "mainEntityOfPage": url,
        "inLanguage": "ru",
        "author": {
            "@type": "Organization",
            "name": SITE_ORG,
            "url": config.SITE_URL,
        },
        "publisher": {
            "@type": "Organization",
            "name": SITE_ORG,
            "logo": {
                "@type": "ImageObject",
                "url": LOGO_URL,
            },
        },
        "datePublished": date_published,
        "dateModified": date_modified,
    }


# ---------------------------------------------------------------------------
# FAQ (единый источник данных)
# ---------------------------------------------------------------------------

FAQ_ITEMS = [
    {
        "q": "Какие модели Keenetic точно поддерживают VLESS + Reality?",
        "a": "Все модели с индексом KN-xxxx и поддержкой OPKG/Entware: Hopper (KN-3812), Giga (KN-3012), Ultra (KN-2610), Titan (KN-3610), Sprint (KN-3312), Peak (KN-2710), Skipper (KN-2910), Giant (KN-4010), Hero (KN-2410), Viva (KN-2310) и другие. Модели Keenetic Air и City имеют ограниченную поддержку из-за малого объёма памяти.",
    },
    {
        "q": "Какая скорость будет через VLESS + Reality на Keenetic?",
        "a": "Скорость зависит от модели роутера и интернет-тарифа. На Hopper и Giga — до 500–900 Мбит/с, на Ultra и Sprint — 200–500 Мбит/с, на бюджетных моделях — до 100 Мбит/с. Протокол VLESS + XTLS-Vision даёт минимальные потери (5–10%).",
    },
    {
        "q": "Можно ли настроить VLESS + Reality без USB-накопителя?",
        "a": "Да, если у роутера достаточно встроенной памяти (128+ МБ свободного места). На моделях с малым объёмом памяти (например, Keenetic Air) USB-накопитель обязателен.",
    },
    {
        "q": "Почему Xray не запускается?",
        "a": "Проверьте правильность конфигурационного файла командой xray -c /opt/etc/xray/config.json -test, наличие всех обязательных полей (UUID, адрес сервера, публичный ключ), доступность сервера и логи Xray: logread | grep xray.",
    },
    {
        "q": "Как обновить Xray-core на Keenetic?",
        "a": "Выполните команды: opkg update, затем xkeen -uk и xkeen -ux. Выберите последнюю версию XKeen и подтвердите обновление. После этого замените файлы конфигурации 04_outbounds.json и 05_routing.json и перезапустите XKeen командой xkeen -restart.",
    },
    {
        "q": "Можно ли использовать один 04_outbounds.json для нескольких роутеров Keenetic?",
        "a": "Нет, 04_outbounds.json защищён от использования несколькими клиентами. Для каждого роутера нужно создать отдельную ссылку vless:// (UUID) в Telegram-боте.",
    },
    {
        "q": "Что делать, если перестал работать конфиг?",
        "a": "Обновите Xray-core до последней версии, проверьте актуальность serverName (реальный сайт должен быть доступен), смените fingerprint браузера и проверьте, не заблокирован ли IP вашего VPS.",
    },
    {
        "q": "Влияет ли VPN на скорость домашней сети между устройствами?",
        "a": "Нет, локальный трафик между устройствами в домашней сети не проходит через VPN. Правила маршрутизации исключают приватные IP-адреса (192.168.x.x, 10.x.x.x) из перенаправления.",
    },
    {
        "q": "Как полностью удалить Xray с роутера?",
        "a": "Выполните команды: /opt/etc/init.d/S99xray stop, opkg remove xray-core, rm -rf /opt/etc/xray, rm /opt/etc/init.d/S99xray.",
    },
]


def faq_page_ld(items: list[dict]) -> dict:
    """FAQPage — частые вопросы."""
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["q"],
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": item["a"],
                },
            }
            for item in items
        ],
    }


# ---------------------------------------------------------------------------
# HowTo (единый источник данных)
# ---------------------------------------------------------------------------

HOWTO_STEPS = [
    {
        "name": "Подготовка роутера",
        "text": "Зайдите в веб-интерфейс Keenetic (192.168.1.1 или my.keenetic.net), установите компоненты OPKG, файловую систему Ext и пакет Xtables-addons для Netfilter. При наличии USB-порта отформатируйте флешку в EXT4 и подготовьте папку install для Entware.",
    },
    {
        "name": "Установка Entware в роутере на флешку",
        "text": "Откройте раздел OPKG в основных настройках, выберите носитель (флешку USB) и сохраните. Дождитесь завершения установки в журнале — там будут указаны порт, логин и пароль.",
    },
    {
        "name": "Установка Xray-core",
        "text": "Подключитесь к роутеру по SSH и выполните установку Xray-core через OPKG и скрипт установки XKeen. Выберите пункт 1 для Xray и последней версии, включите автообновление.",
    },
    {
        "name": "Установка конфигурации",
        "text": "Получите ссылку vless:// в Telegram-боте, сгенерируйте файл 04_outbounds.json в генераторе и замените его на роутере в папке /etc/xray/configs/. Перенесите 443 порт роутера на другой командой ip http ssl port 65083 и сохраните конфигурацию.",
    },
    {
        "name": "Настройка политики XKeen",
        "text": "Создайте политику XKeen, отметьте подключение к интернету и сохраните. Создайте отдельную Wi-Fi сеть (например, Keenetic-VPN) с политикой XKeen — все устройства этой сети будут работать через VLESS + Reality.",
    },
    {
        "name": "Тестовый запуск",
        "text": "Запустите XKeen командой xkeen -start, проверьте доступ к сайтам и убедитесь, что ваш IP-адрес изменился на IP VPN-сервера. При необходимости настройте выборочную маршрутизацию файлом 05_routing.json.",
    },
]


def how_to_ld(steps: list[dict], url: str) -> dict:
    """HowTo — пошаговая инструкция."""
    total_time = "PT25M"
    return {
        "@context": "https://schema.org",
        "@type": "HowTo",
        "name": "Настройка VLESS + Reality на роутере Keenetic",
        "description": "Пошаговая инструкция по настройке VLESS + Reality на роутере Keenetic: от установки компонентов до работающего VPN.",
        "url": url,
        "inLanguage": "ru",
        "totalTime": total_time,
        "step": [
            {
                "@type": "HowToStep",
                "position": i + 1,
                "name": step["name"],
                "text": step["text"],
            }
            for i, step in enumerate(steps)
        ],
    }
