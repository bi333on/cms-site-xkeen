"""
Пример модуля CMS — «Аналитика».
Демонстрирует, как создавать расширения для CMS.
"""
from modules import BaseModule
from flask import Blueprint, render_template


class AnalyticsModule(BaseModule):
    module_name = "analytics"
    display_name = "Аналитика"
    description = "Сбор и отображение статистики посещений сайта"
    version = "1.0.0"
    author = "CMS Team"
    icon = "📈"

    def register(self, app) -> bool:
        bp = Blueprint(
            "analytics",
            __name__,
            template_folder="templates",
            url_prefix="/analytics",
        )

        @bp.route("/")
        def analytics_index():
            return render_template("analytics/index.html")

        app.register_blueprint(bp)
        self.blueprint = bp
        return True

    def get_admin_menu_items(self) -> list[dict]:
        return [
            {"label": "Аналитика", "url": "/admin/analytics/", "icon": "📈"},
        ]

    def get_config(self) -> dict:
        return {
            "track_pageviews": True,
            "track_referrers": True,
            "retention_days": 90,
        }
