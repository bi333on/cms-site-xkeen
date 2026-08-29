"""
Модуль CMS — Генератор конфига Xray для Keenetic.
Парсит ссылку подписки (vless://, vmess://, trojan://, ss://)
и генерирует готовый config.json (outbounds) для Xray-core на роутере.
"""
from modules import BaseModule
from flask import Blueprint, render_template


class ConfigGeneratorModule(BaseModule):
    module_name = "config_generator"
    display_name = "Генератор конфига Xray"
    description = "Генерация конфига Xray для Keenetic из ссылки подписки (vless/vmess/trojan/ss)"
    version = "1.0.0"
    author = "CMS Team"
    icon = "⚙️"

    def register(self, app) -> bool:
        bp = Blueprint(
            "config_generator",
            __name__,
            template_folder="templates",
            url_prefix="/generator",
        )

        @bp.route("/")
        def generator_index():
            return render_template("generator.html", active_page="generator")

        app.register_blueprint(bp)
        self.blueprint = bp
        return True

    def get_nav_items(self) -> list[dict]:
        return [
            {"label": "Генератор", "url": "/generator/"},
        ]

    def get_admin_menu_items(self) -> list[dict]:
        return []

    def get_config(self) -> dict:
        return {}
