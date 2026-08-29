"""
Модульная система CMS.
Каждый модуль — это класс, наследующий BaseModule.
Модули автоматически обнаруживаются в папке modules/.
"""
import os
import sys
import importlib
import json
from abc import ABC, abstractmethod
from flask import Blueprint


class BaseModule(ABC):
    """Базовый класс для всех модулей CMS."""

    # Уникальное имя модуля (используется в БД и URL)
    module_name: str = "base"
    # Отображаемое имя
    display_name: str = "Базовый модуль"
    # Описание
    description: str = ""
    # Версия
    version: str = "1.0.0"
    # Автор
    author: str = "CMS"
    # Иконка (эмодзи)
    icon: str = "📦"

    def __init__(self, app=None):
        self.app = app
        self.blueprint: Blueprint | None = None

    @abstractmethod
    def register(self, app) -> bool:
        """
        Регистрирует модуль в приложении Flask.
        Должен вернуть True при успешной регистрации.
        """
        ...

    def get_config(self) -> dict:
        """Возвращает конфигурацию модуля по умолчанию."""
        return {}

    def get_admin_menu_items(self) -> list[dict]:
        """
        Возвращает пункты меню для админ-панели.
        Каждый пункт: {"label": str, "url": str, "icon": str}
        """
        return []

    def get_nav_items(self) -> list[dict]:
        """
        Возвращает пункты для публичного меню сайта.
        Каждый пункт: {"label": str, "url": str}
        """
        return []

    def on_install(self) -> bool:
        """Вызывается при первой установке модуля."""
        return True

    def on_uninstall(self) -> bool:
        """Вызывается при удалении модуля."""
        return True

    def on_enable(self) -> bool:
        """Вызывается при включении модуля."""
        return True

    def on_disable(self) -> bool:
        """Вызывается при выключении модуля."""
        return True


class ModuleRegistry:
    """Реестр всех зарегистрированных модулей."""

    def __init__(self):
        self._modules: dict[str, BaseModule] = {}

    def register(self, module: BaseModule):
        self._modules[module.module_name] = module

    def unregister(self, module_name: str):
        self._modules.pop(module_name, None)

    def get(self, module_name: str) -> BaseModule | None:
        return self._modules.get(module_name)

    def get_all(self) -> dict[str, BaseModule]:
        return dict(self._modules)

    def get_enabled(self, db_modules: list) -> dict[str, BaseModule]:
        """Возвращает только включённые модули."""
        enabled_names = {m.name for m in db_modules if m.is_enabled}
        return {k: v for k, v in self._modules.items() if k in enabled_names}

    def discover_modules(self, app):
        """
        Автоматически находит и загружает модули из папки modules/.
        Каждый модуль должен быть в отдельной папке с файлом module.py,
        содержащим класс, наследующий BaseModule.
        """
        modules_dir = os.path.join(app.root_path, "modules")
        if not os.path.isdir(modules_dir):
            return

        for item in os.listdir(modules_dir):
            item_path = os.path.join(modules_dir, item)
            if not os.path.isdir(item_path):
                continue
            module_file = os.path.join(item_path, "module.py")
            if not os.path.isfile(module_file):
                continue

            try:
                spec = importlib.util.spec_from_file_location(
                    f"cms_modules.{item}", module_file
                )
                mod = importlib.util.module_from_spec(spec)
                # Регистрируем модуль в sys.modules, чтобы Flask мог вычислить
                # корневой путь blueprint (template_folder/static_folder)
                sys.modules[spec.name] = mod
                spec.loader.exec_module(mod)

                # Ищем класс, наследующий BaseModule
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseModule)
                        and attr is not BaseModule
                    ):
                        instance = attr(app)
                        # Регистрируем blueprint в Flask
                        if instance.register(app):
                            self.register(instance)
                            app.logger.info(f"Модуль обнаружен: {instance.module_name}")
                        break
            except Exception as e:
                app.logger.error(f"Ошибка загрузки модуля {item}: {e}")


# Глобальный реестр модулей
module_registry = ModuleRegistry()
