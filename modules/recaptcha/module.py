"""
Модуль CMS — reCAPTCHA v3 для админ-панели.
Защищает форму входа администратора от брутфорса.
"""
import requests
from modules import BaseModule
from flask import Blueprint, render_template, request, jsonify


class RecaptchaModule(BaseModule):
    module_name = "recaptcha"
    display_name = "reCAPTCHA v3"
    description = "Защита админ-панели через Google reCAPTCHA v3. Проверяет каждый вход администратора."
    version = "1.0.0"
    author = "CMS Team"
    icon = "🛡️"

    def register(self, app) -> bool:
        bp = Blueprint(
            "recaptcha",
            __name__,
            template_folder="templates",
            url_prefix="/recaptcha",
        )

        @bp.route("/verify/", methods=["POST"])
        def recaptcha_verify():
            """
            API для проверки reCAPTCHA-токена.
            Используется админ-логином через вызов verify_token().
            """
            data = request.get_json(force=True) or {}
            token = data.get("recaptcha_token", "")
            result = self.verify_token(token)
            return jsonify(result)

        app.register_blueprint(bp)
        self.blueprint = bp

        # Добавляем глобальную переменную reCAPTCHA для шаблонов
        @app.context_processor
        def inject_recaptcha():
            return {
                "recaptcha_site_key": app.config.get("RECAPTCHA_SITE_KEY", ""),
                "recaptcha_enabled": bool(
                    app.config.get("RECAPTCHA_SITE_KEY")
                    and app.config.get("RECAPTCHA_SECRET_KEY")
                ),
            }

        return True

    def verify_token(self, token: str) -> dict:
        """
        Проверяет reCAPTCHA v3 токен через Google API.
        Возвращает {"ok": True} или {"ok": False, "error": ...}.
        """
        from config import config

        if not token:
            return {"ok": False, "error": "Токен не передан"}

        if not config.RECAPTCHA_SECRET_KEY:
            # Если ключ не настроен — пропускаем (для разработки)
            return {"ok": True, "score": 0.0, "warning": "reCAPTCHA не настроен"}

        try:
            resp = requests.post(
                "https://www.google.com/recaptcha/api/siteverify",
                data={
                    "secret": config.RECAPTCHA_SECRET_KEY,
                    "response": token,
                },
                timeout=5,
            )
            result = resp.json()
        except Exception as e:
            # Ошибка сети — пропускаем (не блокируем вход)
            return {"ok": True, "score": 0.0, "warning": f"Ошибка проверки: {e}"}

        if not result.get("success"):
            error_codes = result.get("error-codes", [])
            return {"ok": False, "error": f"reCAPTCHA не пройдена: {', '.join(error_codes)}"}

        score = result.get("score", 0.0)
        threshold = config.RECAPTCHA_SCORE_THRESHOLD

        if score < threshold:
            return {
                "ok": False,
                "error": f"Подозрительная активность (score: {score:.2f}, порог: {threshold})",
                "score": score,
            }

        return {"ok": True, "score": score}

    def get_admin_menu_items(self) -> list[dict]:
        return []

    def get_config(self) -> dict:
        return {
            "score_threshold": 0.5,
        }
