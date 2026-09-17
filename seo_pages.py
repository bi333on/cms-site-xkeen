"""
SEO-целевые страницы (лендинги) под кластеры низкочастотных запросов.

Каждая запись — словарь с полями модели Page:
    slug, title, meta_description, meta_keywords, content (Markdown),
    is_published, access_level, noindex, show_in_menu, menu_label, sort_order.

Страницы создаются функцией seed_seo_pages() в app.py идемпотентно по slug:
существующие страницы не перезаписываются (контент можно править через админку).
"""

SEO_PAGES = [
    {
        "slug": "nastrojka-keenetic",
        "title": "Настройка роутера Keenetic — пошаговое руководство 2026",
        "meta_description": "Как настроить роутер Keenetic с нуля: вход в веб-интерфейс, установка компонентов OPKG, подключение по SSH и настройка VPN. Полное пошаговое руководство для всех моделей Keenetic.",
        "meta_keywords": "настройка keenetic, как настроить keenetic, настройка роутера keenetic, keenetic настройка, keenetic инструкция настройка, настройка keenetic с нуля, веб интерфейс keenetic",
        "content": """# Настройка роутера Keenetic — пошаговое руководство

Keenetic — это линейка роутеров с собственной операционной системой KeeneticOS. Благодаря модульной архитектуре и встроенному пакетному менеджеру OPKG роутер можно использовать не только для раздачи интернета, но и для более сложных задач: настройки VPN, маршрутизации и управления трафиком.

## С чего начать настройку Keenetic

1. **Подключите роутер** к сети и дождитесь загрузки.
2. **Откройте веб-интерфейс** по адресу `192.168.1.1` или `my.keenetic.net`.
3. **Пройдите мастер первичной настройки** — выберите тип подключения к провайдеру (PPPoE, DHCP, статический IP) и задайте пароль администратора.

## Установка компонентов OPKG

Для расширенных возможностей (в том числе установки сторонних пакетов) включите компоненты:

- перейдите в раздел **«Настройки системы» → «Изменить набор компонентов»**;
- установите **«Пакеты OPKG»**, **«Поддержку открытых пакетов»** и модули ядра для файловых систем;
- дождитесь перезагрузки роутера.

## Подключение по SSH

Для выполнения команд откройте терминал (PuTTY или Termius) и подключитесь к роутеру:

```text
ssh root@192.168.1.1
```

Порт по умолчанию — 22 или 222, логин — `root`.

## Что можно настроить дальше

- [Установка Xray-core на Keenetic](/ustanovka-xray-keenetic/)
- [Настройка OPKG на Keenetic](/nastrojka-opkg-keenetic/)
- [Пошаговая инструкция по настройке VLESS + Reality](/setup/)
- [Совместимые модели Keenetic](/models/)

Базовая настройка Keenetic занимает 10–15 минут. Дальнейшая конфигурация зависит от ваших задач — от создания гостевой Wi-Fi сети до настройки защищённого соединения для всех устройств дома.""",
    },
    {
        "slug": "ustanovka-xray-keenetic",
        "title": "Установка Xray на Keenetic — инструкция по Xray-core 2026",
        "meta_description": "Как установить Xray-core на роутер Keenetic: подготовка OPKG, установка через SSH, настройка конфигурации и автозапуска. Пошаговая инструкция для всех моделей Keenetic.",
        "meta_keywords": "установка xray keenetic, xray keenetic установка, xray-core keenetic, установить xray на keenetic, xray keenetic инструкция, keenetic xray настройка, xray-core установка роутер",
        "content": """# Установка Xray на Keenetic

Xray-core — это ядро прокси-протоколов, которое используется для настройки защищённого соединения на роутере Keenetic. Установка выполняется через пакетный менеджер OPKG и не требует перепрошивки роутера.

## Подготовка

Перед установкой Xray убедитесь, что:

- роутер поддерживает OPKG (все модели с индексом KN-xxxx);
- установлены компоненты **«Пакеты OPKG»** и **«Поддержка открытых пакетов»**;
- у роутера есть свободное место (или подключена флешка с Entware).

## Установка Xray-core

Подключитесь к роутеру по SSH и выполните:

```text
opkg update
opkg install curl
```

Затем запустите скрипт установки XKeen:

```text
opkg update && opkg upgrade && opkg install curl tar && \
curl -sOfL https://raw.githubusercontent.com/RockBlack-VPN/XKeen/main/install.sh && \
chmod +x ./install.sh && ./install.sh
```

В появившемся меню выберите Xray (пункт 1), актуальную версию и включите автообновление раз в неделю.

## Настройка конфигурации

После установки замените файл конфигурации `04_outbounds.json` в папке `/etc/xray/configs/`. Готовый конфиг можно сгенерировать в [Генераторе 04_outbounds.json](/generator/).

## Проверка работы

Запустите Xray командой:

```text
xkeen -start
```

Проверьте логи и убедитесь, что соединение установлено:

```text
logread | grep xray
```

Подробности — в [полной инструкции по настройке VLESS + Reality](/setup/). Если Xray не запускается, посмотрите раздел [частых вопросов](/faq/).""",
    },
    {
        "slug": "nastrojka-opkg-keenetic",
        "title": "Настройка OPKG на Keenetic — установка пакетов и Entware",
        "meta_description": "Как настроить OPKG на роутере Keenetic: установка компонентов, выбор носителя, установка Entware на флешку и работа с пакетами. Подробная инструкция 2026.",
        "meta_keywords": "настройка opkg keenetic, opkg keenetic, установка opkg keenetic, keenetic opkg настройка, opkg keenetic флешка, entware keenetic, opkg пакеты keenetic",
        "content": """# Настройка OPKG на Keenetic

OPKG — это пакетный менеджер KeeneticOS, позволяющий устанавливать сторонние программы (например, Xray-core) прямо на роутер. В связке с Entware он превращает Keenetic в полноценный Linux-сервер.

## Установка компонентов OPKG

1. Зайдите в веб-интерфейс роутера (`192.168.1.1`).
2. Откройте **«Настройки системы» → «Изменить набор компонентов»**.
3. Установите компоненты:
   - **Пакеты OPKG** — менеджер пакетов;
   - **Поддержка открытых пакетов**;
   - **Файловая система Ext**;
   - **Модули ядра для поддержки файловых систем**.
4. Дождитесь перезагрузки роутера.

## Установка Entware на флешку

Если у роутера есть USB-порт, рекомендуем установить Entware на внешний накопитель:

1. Отформатируйте флешку (от 4 ГБ) в файловую систему EXT4.
2. Подключите её к роутеру и создайте папку `install`.
3. Скачайте инсталлер под архитектуру вашей модели и загрузите в папку `install`.
4. В разделе **OPKG** выберите носитель (флешку) и нажмите **Сохранить**.

## Работа с пакетами

После установки OPKG доступны команды:

```text
opkg update          # обновить список пакетов
opkg install <пакет> # установить пакет
opkg remove <пакет>  # удалить пакет
```

Далее можно перейти к [установке Xray-core](/ustanovka-xray-keenetic/) или [настройке VLESS + Reality](/setup/). Полный список поддерживаемых моделей — на странице [«Модели»](/models/).""",
    },
    {
        "slug": "keenetic-hopper-vless",
        "title": "Keenetic Hopper и VLESS + Reality — настройка 2026",
        "meta_description": "Настройка VLESS + Reality на роутере Keenetic Hopper (KN-3812): установка OPKG, Xray-core, конфигурация и проверка работы. Пошаговая инструкция для флагманской модели.",
        "meta_keywords": "keenetic hopper vless, keenetic hopper vless reality, hopper kn-3812 vless, настройка vless keenetic hopper, keenetic hopper настройка vpn, keenetic hopper xray",
        "content": """# Keenetic Hopper и VLESS + Reality

Keenetic Hopper (KN-3812) — флагманская модель линейки с поддержкой Wi-Fi 7. Благодаря производительному процессору Hopper отлично подходит для работы с протоколом VLESS + Reality: скорость соединения достигает 500–900 Мбит/с.

## Почему Hopper подходит для VLESS

- поддержка OPKG и Entware;
- мощный процессор с аппаратным ускорением;
- Wi-Fi 7 и скорость до 6 Гбит/с;
- архитектура, совместимая с Xray-core.

## Настройка на Keenetic Hopper

Порядок настройки не отличается от других моделей:

1. Установите компоненты OPKG в веб-интерфейсе.
2. Подготовьте флешку с Entware (рекомендуется из-за высокой производительности).
3. Установите Xray-core по SSH.
4. Сгенерируйте и замените файл конфигурации.
5. Настройте политику XKeen и запустите соединение.

Полный алгоритм описан в [пошаговой инструкции](/setup/). Установка ядра — в разделе [«Установка Xray на Keenetic»](/ustanovka-xray-keenetic/).

## Особенности модели

На Hopper рекомендуется включить автообновление ядра и настроить выборочную маршрутизацию, чтобы локальные ресурсы работали напрямую. Если соединение не устанавливается — проверьте раздел [частых вопросов](/faq/).

Сравнение Hopper с другими моделями — на странице [«Модели Keenetic»](/models/).""",
    },
    {
        "slug": "keenetic-giga-vless",
        "title": "Keenetic Giga и VLESS + Reality — настройка 2026",
        "meta_description": "Настройка VLESS + Reality на роутере Keenetic Giga (KN-3012): установка OPKG и Xray-core, конфигурация и проверка. Пошаговая инструкция для популярной модели.",
        "meta_keywords": "keenetic giga vless, keenetic giga vless reality, giga kn-3012 vless, настройка vless keenetic giga, keenetic giga vpn, keenetic giga xray",
        "content": """# Keenetic Giga и VLESS + Reality

Keenetic Giga (KN-3012) — одна из самых популярных моделей для домашнего использования. Поддержка Wi-Fi 6 и производительный процессор делают Giga оптимальным выбором для настройки VLESS + Reality.

## Характеристики Giga

- Wi-Fi 6, скорость до 2,5 Гбит/с;
- поддержка OPKG/Entware;
- производительность, достаточная для 200–500 Мбит/с через VLESS.

## Настройка на Keenetic Giga

1. В веб-интерфейсе установите компоненты **OPKG** и **Файловая система Ext**.
2. Подключите флешку и установите Entware.
3. По SSH выполните установку Xray-core.
4. Сгенерируйте конфигурацию в [Генераторе](/generator/) и замените файл `04_outbounds.json`.
5. Создайте политику XKeen и запустите соединение командой `xkeen -start`.

Детальный алгоритм — в [пошаговой инструкции](/setup/). Установка ядра — в разделе [«Установка Xray на Keenetic»](/ustanovka-xray-keenetic/).

## Советы

Для максимальной скорости включите аппаратное ускорение и настройте выборочную маршрутизацию. Ответы на типичные проблемы — в разделе [частых вопросов](/faq/). Полный список совместимых моделей — на странице [«Модели Keenetic»](/models/).""",
    },
    {
        "slug": "keenetic-ultra-vless",
        "title": "Keenetic Ultra и VLESS + Reality — настройка 2026",
        "meta_description": "Настройка VLESS + Reality на роутере Keenetic Ultra (KN-2610): установка OPKG, Xray-core, конфигурация и проверка соединения. Пошаговая инструкция.",
        "meta_keywords": "keenetic ultra vless, keenetic ultra vless reality, ultra kn-2610 vless, настройка vless keenetic ultra, keenetic ultra vpn, keenetic ultra xray",
        "content": """# Keenetic Ultra и VLESS + Reality

Keenetic Ultra (KN-2610) — модель среднего сегмента с отличным соотношением цены и производительности. Поддержка Wi-Fi 6 и двухъядерного процессора позволяет комфортно использовать VLESS + Reality.

## Характеристики Ultra

- Wi-Fi 6, скорость до 1,8 Гбит/с;
- двухъядерный процессор;
- поддержка OPKG/Entware.

## Настройка на Keenetic Ultra

1. Установите компоненты **OPKG** и **Пакет расширения Xtables-addons для Netfilter**.
2. Подготовьте флешку с Entware (или используйте встроенную память при достаточном объёме).
3. Установите Xray-core по SSH.
4. Сгенерируйте конфигурацию и замените `04_outbounds.json`.
5. Создайте политику XKeen и запустите соединение.

Пошаговый алгоритм — в [инструкции по настройке VLESS + Reality](/setup/). Установка ядра — в разделе [«Установка Xray на Keenetic»](/ustanovka-xray-keenetic/).

## Рекомендации

Для Ultra рекомендуем включить аппаратное ускорение и настроить отдельную Wi-Fi сеть под политику XKeen. При возникновении ошибок — раздел [частых вопросов](/faq/). Сравнение моделей — на странице [«Модели Keenetic»](/models/).""",
    },
    {
        "slug": "amneziawg-keenetic",
        "title": "AmneziaWG на Keenetic — настройка и установка 2026",
        "meta_description": "Как настроить AmneziaWG на роутере Keenetic: установка пакетов, создание конфигурации WireGuard и проверка работы. Пошаговая инструкция 2026.",
        "meta_keywords": "amneziawg keenetic, amneziawg keenetic настройка, amnezia wg keenetic, wireguard keenetic настройка, amneziawg установка keenetic, keenetic amneziawg инструкция",
        "content": """# AmneziaWG на Keenetic

AmneziaWG — это модифицированная версия протокола WireGuard с дополнительной маскировкой трафика. KeeneticOS поддерживает WireGuard нативно, а AmneziaWG можно развернуть через OPKG.

## Что нужно для настройки

- роутер Keenetic с поддержкой OPKG;
- установленные компоненты **OPKG** и **Файловая система Ext**;
- доступ по SSH;
- конфигурация AmneziaWG (файл `.conf`).

## Установка и настройка

1. Установите пакеты через OPKG:

```text
opkg update
opkg install amneziawg-go
```

2. Загрузите конфигурацию AmneziaWG на роутер.
3. Создайте интерфейс и пропишите маршруты.
4. Добавьте автозапуск через init.d.

## Проверка

После запуска проверьте состояние интерфейса и IP-адрес. Если нужен более производительный вариант — рассмотрите [VLESS + Reality](/setup/), который обеспечивает более высокую скорость на роутерах Keenetic.

Подробнее о пакетном менеджере — в разделе [«Настройка OPKG на Keenetic»](/nastrojka-opkg-keenetic/). Список поддерживаемых моделей — на странице [«Модели Keenetic»](/models/).""",
    },
    {
        "slug": "keenetic-sprint-vless",
        "title": "Keenetic Sprint и VLESS + Reality — настройка 2026",
        "meta_description": "Настройка VLESS + Reality на роутере Keenetic Sprint (KN-3312): установка OPKG и Xray-core, конфигурация и проверка. Пошаговая инструкция для компактной модели.",
        "meta_keywords": "keenetic sprint vless, keenetic sprint vless reality, sprint kn-3312 vless, настройка vless keenetic sprint, keenetic sprint vpn, keenetic sprint xray",
        "content": """# Keenetic Sprint и VLESS + Reality

Keenetic Sprint (KN-3312) — компактная модель с поддержкой Wi-Fi 6, подходящая для квартир и небольших домов. Sprint поддерживает OPKG и позволяет настроить VLESS + Reality.

## Характеристики Sprint

- Wi-Fi 6, компактный корпус;
- поддержка OPKG/Entware;
- производительность, достаточная для 200–500 Мбит/с через VLESS.

## Настройка на Keenetic Sprint

1. Установите компоненты **OPKG** и **Файловая система Ext** в веб-интерфейсе.
2. Подготовьте флешку с Entware (для Sprint рекомендовано из-за ограниченного объёма памяти).
3. Установите Xray-core по SSH.
4. Сгенерируйте конфигурацию в [Генераторе](/generator/) и замените `04_outbounds.json`.
5. Создайте политику XKeen и запустите соединение.

Подробности — в [пошаговой инструкции](/setup/) и разделе [«Установка Xray на Keenetic»](/ustanovka-xray-keenetic/).

## Рекомендации

На Sprint важно использовать флешку для Entware, чтобы не занимать внутреннюю память роутера. При ошибках — раздел [частых вопросов](/faq/). Полный список моделей — на странице [«Модели Keenetic»](/models/).""",
    },
    {
        "slug": "keenetic-titan-vless",
        "title": "Keenetic Titan и VLESS + Reality — настройка 2026",
        "meta_description": "Настройка VLESS + Reality на роутере Keenetic Titan (KN-3610): установка OPKG и Xray-core, конфигурация, автозапуск. Пошаговая инструкция для мощной модели с Wi-Fi 6E.",
        "meta_keywords": "keenetic titan vless, keenetic titan vless reality, titan kn-3610 vless, настройка vless keenetic titan, keenetic titan vpn, keenetic titan xray",
        "content": """# Keenetic Titan и VLESS + Reality

Keenetic Titan (KN-3610) — производительная модель с поддержкой Wi-Fi 6E и трёх диапазонов. Titan отлично подходит для настройки VLESS + Reality в домах и офисах с высокой нагрузкой на сеть.

## Характеристики Titan

- Wi-Fi 6E (AXE7800), три диапазона;
- поддержка OPKG/Entware;
- USB 3.0 и мощный процессор.

## Настройка на Keenetic Titan

1. В веб-интерфейсе установите компоненты **OPKG**, **Файловая система Ext** и **Пакет расширения Xtables-addons для Netfilter**.
2. Подготовьте флешку с Entware — при высоких нагрузках внешний накопитель предпочтительнее встроенной памяти.
3. По SSH установите Xray-core.
4. Сгенерируйте конфигурацию в [Генераторе](/generator/) и замените файл `04_outbounds.json` в `/etc/xray/configs/`.
5. Создайте политику XKeen и запустите соединение командой `xkeen -start`.

Детальный алгоритм — в [пошаговой инструкции](/setup/). Установка ядра — в разделе [«Установка Xray на Keenetic»](/ustanovka-xray-keenetic/).

## Особенности модели

Titan поддерживает аппаратное ускорение, что позволяет достигать высокой скорости через VLESS. Рекомендуется включить автообновление ядра и настроить отдельную Wi-Fi сеть под политику XKeen. При проблемах — [частые вопросы](/faq/) и [сравнение моделей](/models/).""",
    },
    {
        "slug": "keenetic-peak-vless",
        "title": "Keenetic Peak и VLESS + Reality — настройка 2026",
        "meta_description": "Настройка VLESS + Reality на роутере Keenetic Peak (KN-2710): установка OPKG, Xray-core, конфигурация и проверка. Инструкция для бюджетной модели.",
        "meta_keywords": "keenetic peak vless, keenetic peak vless reality, peak kn-2710 vless, настройка vless keenetic peak, keenetic peak vpn, keenetic peak xray",
        "content": """# Keenetic Peak и VLESS + Reality

Keenetic Peak (KN-2710) — бюджетная модель с поддержкой Wi-Fi 6, подходящая для небольших квартир. Несмотря на доступную цену, Peak поддерживает OPKG и позволяет настроить VLESS + Reality.

## Характеристики Peak

- Wi-Fi 6 (AX1800);
- поддержка OPKG/Entware;
- компактный корпус, нет USB-порта.

## Настройка на Keenetic Peak

Поскольку у Peak нет USB-порта, Entware и Xray-core устанавливаются во внутреннюю память роутера:

1. Установите компоненты **OPKG** и **Файловая система Ext**.
2. Убедитесь, что во встроенном хранилище достаточно свободного места.
3. По SSH установите Xray-core.
4. Сгенерируйте конфигурацию в [Генераторе](/generator/) и замените `04_outbounds.json`.
5. Создайте политику XKeen и запустите соединение.

Подробности — в [пошаговой инструкции](/setup/) и разделе [«Установка Xray на Keenetic»](/ustanovka-xray-keenetic/).

## Советы для бюджетной модели

На Peak следите за свободным местом во встроенной памяти: при нехватке удаляйте неиспользуемые пакеты. При ошибках — раздел [частых вопросов](/faq/). Список всех совместимых моделей — на странице [«Модели Keenetic»](/models/).""",
    },
    {
        "slug": "keenetic-skipper-vless",
        "title": "Keenetic Skipper и VLESS + Reality — настройка 2026",
        "meta_description": "Настройка VLESS + Reality на роутере Keenetic Skipper (KN-2910): установка OPKG, Xray-core, конфигурация и проверка. Пошаговая инструкция.",
        "meta_keywords": "keenetic skipper vless, keenetic skipper vless reality, skipper kn-2910 vless, настройка vless keenetic skipper, keenetic skipper vpn, keenetic skipper xray",
        "content": """# Keenetic Skipper и VLESS + Reality

Keenetic Skipper (KN-2910) — модель среднего сегмента с поддержкой Wi-Fi 6. Skipper поддерживает OPKG и позволяет настроить VLESS + Reality для всех устройств в сети.

## Характеристики Skipper

- Wi-Fi 6 (AX5400);
- поддержка OPKG/Entware;
- USB 2.0 для внешнего накопителя.

## Настройка на Keenetic Skipper

1. В веб-интерфейсе установите компоненты **OPKG** и **Файловая система Ext**.
2. Подключите флешку и установите Entware (рекомендуется, чтобы не занимать внутреннюю память).
3. По SSH установите Xray-core.
4. Сгенерируйте конфигурацию в [Генераторе](/generator/) и замените `04_outbounds.json`.
5. Создайте политику XKeen и запустите соединение.

Детальный алгоритм — в [пошаговой инструкции](/setup/). Установка ядра — в разделе [«Установка Xray на Keenetic»](/ustanovka-xray-keenetic/).

## Рекомендации

Для Skipper рекомендуем использовать флешку для Entware и настроить выборочную маршрутизацию. При проблемах — раздел [частых вопросов](/faq/). Сравнение моделей — на странице [«Модели Keenetic»](/models/).""",
    },
    {
        "slug": "keenetic-giant-vless",
        "title": "Keenetic Giant и VLESS + Reality — настройка 2026",
        "meta_description": "Настройка VLESS + Reality на роутере Keenetic Giant (KN-4010): установка OPKG, Xray-core, конфигурация и проверка. Инструкция для бюджетной модели.",
        "meta_keywords": "keenetic giant vless, keenetic giant vless reality, giant kn-4010 vless, настройка vless keenetic giant, keenetic giant vpn, keenetic giant xray",
        "content": """# Keenetic Giant и VLESS + Reality

Keenetic Giant (KN-4010) — доступная модель с поддержкой Wi-Fi 6. Giant поддерживает OPKG, поэтому на нём можно настроить VLESS + Reality даже при ограниченном бюджете.

## Характеристики Giant

- Wi-Fi 6 (AX1500);
- поддержка OPKG/Entware;
- USB 2.0.

## Настройка на Keenetic Giant

1. Установите компоненты **OPKG** и **Файловая система Ext** в веб-интерфейсе.
2. Подключите флешку с Entware.
3. По SSH установите Xray-core.
4. Сгенерируйте конфигурацию в [Генераторе](/generator/) и замените `04_outbounds.json`.
5. Создайте политику XKeen и запустите соединение.

Подробности — в [пошаговой инструкции](/setup/) и разделе [«Установка Xray на Keenetic»](/ustanovka-xray-keenetic/).

## Советы

На Giant, как и на других бюджетных моделях, важно использовать флешку для Entware. При ошибках — раздел [частых вопросов](/faq/). Полный список моделей — на странице [«Модели Keenetic»](/models/).""",
    },
    {
        "slug": "keenetic-hero-vless",
        "title": "Keenetic Hero и VLESS + Reality — настройка 2026",
        "meta_description": "Настройка VLESS + Reality на роутере Keenetic Hero (KN-2410): установка OPKG, Xray-core, конфигурация и проверка. Инструкция для модели с 4G.",
        "meta_keywords": "keenetic hero vless, keenetic hero vless reality, hero kn-2410 vless, настройка vless keenetic hero, keenetic hero vpn, keenetic hero xray",
        "content": """# Keenetic Hero и VLESS + Reality

Keenetic Hero (KN-2410) — модель со встроенным 4G-модемом, подходящая для загородных домов и дач. Hero поддерживает OPKG и позволяет настроить VLESS + Reality через мобильный интернет.

## Характеристики Hero

- встроенный 4G-модем;
- поддержка OPKG/Entware;
- работа от SIM-карты.

## Настройка на Keenetic Hero

1. В веб-интерфейсе установите компоненты **OPKG** и **Файловая система Ext**.
2. Подготовьте флешку с Entware.
3. По SSH установите Xray-core.
4. Сгенерируйте конфигурацию в [Генераторе](/generator/) и замените `04_outbounds.json`.
5. Создайте политику XKeen и запустите соединение.

Детальный алгоритм — в [пошаговой инструкции](/setup/). Установка ядра — в разделе [«Установка Xray на Keenetic»](/ustanovka-xray-keenetic/).

## Особенности 4G

При работе через мобильный интернет учитывайте лимиты тарифа. Настройте приоритет WAN: сначала 4G, затем Ethernet. При проблемах — раздел [частых вопросов](/faq/). Список моделей — на странице [«Модели Keenetic»](/models/).""",
    },
    {
        "slug": "keenetic-vless-ne-rabotaet",
        "title": "Keenetic VLESS не работает — решение проблем и ошибки",
        "meta_description": "VLESS + Reality не работает на Keenetic? Разбор частых причин: ошибки конфигурации, недоступный сервер, проблемы Xray. Пошаговая диагностика и решения 2026.",
        "meta_keywords": "keenetic vless не работает, vless reality не работает keenetic, ошибка xray keenetic, keenetic vless не подключается, xray не запускается keenetic, решение проблем vless keenetic",
        "content": """# Keenetic VLESS не работает — решение проблем

Если VLESS + Reality перестал работать на роутере Keenetic, причина почти всегда одна из перечисленных ниже. Разберём диагностику по шагам.

## Шаг 1. Проверьте запуск Xray

Выполните по SSH:

```text
xkeen -start
logread | grep xray
```

Если процесс не запускается — проверьте синтаксис конфигурации командой `xray -c /opt/etc/xray/config.json -test`.

## Шаг 2. Проверьте конфигурацию

Убедитесь, что в файле `04_outbounds.json` указаны корректные значения:

- UUID пользователя;
- адрес и порт сервера;
- публичный ключ Reality;
- `serverName` (реальный сайт для маскировки).

## Шаг 3. Проверьте доступность сервера

```text
ping АДРЕС_СЕРВЕРА
telnet АДРЕС_СЕРВЕРА 443
```

Если сервер недоступен — проверьте, не заблокирован ли IP вашего VPS.

## Шаг 4. Смените fingerprint

Если соединение устанавливается, но скорость низкая или соединение рвётся, попробуйте сменить fingerprint: `chrome`, `firefox` или `safari`.

## Частые причины

- устаревший Xray-core — обновите его;
- неправильный `serverName` — сайт должен быть реально доступен;
- не заменён файл `05_routing.json` при выборочной маршрутизации.

Подробности установки — в разделе [«Установка Xray на Keenetic»](/ustanovka-xray-keenetic/). Больше ответов — в [частых вопросах](/faq/) и [пошаговой инструкции](/setup/).""",
    },
    {
        "slug": "obnovit-xray-keenetic",
        "title": "Как обновить Xray на Keenetic — инструкция 2026",
        "meta_description": "Как обновить Xray-core на роутере Keenetic: команды обновления через XKeen, замена файлов конфигурации, перезапуск. Пошаговая инструкция 2026.",
        "meta_keywords": "обновить xray keenetic, обновление xray keenetic, xkeen обновление, обновить xray-core keenetic, xkeen -uk, обновление xray-core роутер",
        "content": """# Как обновить Xray на Keenetic

Регулярное обновление Xray-core важно для стабильной работы и совместимости с протоколом VLESS + Reality. Обновление выполняется через утилиту XKeen.

## Обновление Xray-core

Подключитесь к роутеру по SSH и выполните:

```text
opkg update
xkeen -uk
xkeen -ux
```

Выберите последнюю версию XKeen и подтвердите обновление.

## Замена файлов конфигурации

После обновления замените файлы конфигурации, если они изменились:

- `04_outbounds.json` — исходящие подключения;
- `05_routing.json` — правила маршрутизации.

Файлы находятся в папке `/etc/xray/configs/`. Новую конфигурацию можно сгенерировать в [Генераторе](/generator/).

## Перезапуск

После замены файлов перезапустите XKeen:

```text
xkeen -restart
```

## Проверка

Убедитесь, что Xray запущен и соединение работает:

```text
logread | grep xray
```

Подробности установки — в разделе [«Установка Xray на Keenetic»](/ustanovka-xray-keenetic/). При проблемах после обновления — [частые вопросы](/faq/) и [пошаговая инструкция](/setup/).""",
    },
    {
        "slug": "keenetic-marshrutizaciya-vless",
        "title": "Маршрутизация VLESS на Keenetic — выборочный трафик",
        "meta_description": "Как настроить выборочную маршрутизацию VLESS на Keenetic: политики доступа, файл 05_routing.json, разделение трафика по доменам. Инструкция 2026.",
        "meta_keywords": "маршрутизация vless keenetic, split tunneling keenetic, выборочная маршрутизация keenetic, keenetic vless маршрутизация, 05_routing.json keenetic, политики доступа keenetic",
        "content": """# Маршрутизация VLESS на Keenetic

Выборочная маршрутизация (split tunneling) позволяет направить через VLESS + Reality только нужный трафик, а остальные сайты — напрямую. Это удобно, когда требуется обходить блокировки только части ресурсов.

## Способ 1. Политики доступа

В веб-интерфейсе Keenetic можно создать политики для отдельных устройств:

1. Откройте раздел **«Политики доступа»**.
2. Создайте политику XKeen и отметьте нужное подключение.
3. Привяжите политику к отдельной Wi-Fi сети или устройству.

## Способ 2. Файл 05_routing.json

Для тонкой настройки по доменам используйте файл `05_routing.json` в папке `/etc/xray/configs/`. Например, правило `"geosite:category-ru"` → `"direct"` направляет российские сайты напрямую, а остальные — через VPN.

Замените файл на роутере и перезапустите XKeen:

```text
xkeen -restart
```

## Что выбрать

- Политики доступа — для разделения по устройствам.
- `05_routing.json` — для разделения по доменам и IP.

Подробности — в [пошаговой инструкции](/setup/) и разделе [«Установка Xray на Keenetic»](/ustanovka-xray-keenetic/). Ответы на вопросы — в [частых вопросах](/faq/).""",
    },
]


def get_seo_pages() -> list[dict]:
    """Возвращает список целевых SEO-страниц."""
    return SEO_PAGES
