import logging
from datetime import datetime
from typing import List, Optional

from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.config import settings
from app.localization.loader import DEFAULT_LANGUAGE
from app.localization.texts import get_texts
from app.utils.pricing_utils import format_period_description, apply_percentage_discount, get_remaining_months
from app.utils.subscription_utils import (
    get_display_subscription_link,
    get_happ_cryptolink_redirect_link,
)
from shared import keyboard, button, buttons_row

logger = logging.getLogger(__name__)

_LANGUAGE_DISPLAY_NAMES = {
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}


def get_rules_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.RULES_ACCEPT, "rules_accept"),
         (texts.RULES_DECLINE, "rules_decline")],
    )


def get_channel_sub_keyboard(
        channel_link: str,
        language: str = DEFAULT_LANGUAGE,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.t("CHANNEL_SUBSCRIBE_BUTTON", "🔗 Подписаться"), channel_link)],  # URL-кнопка
        [(texts.t("CHANNEL_CHECK_BUTTON", "✅ Я подписался"), "sub_channel_check")],  # callback
    )


def get_post_registration_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.t("POST_REGISTRATION_TRIAL_BUTTON", "🚀 Подключиться бесплатно 🚀"), "trial_activate")],
        [(texts.t("SKIP_BUTTON", "Пропустить ➡️"), "back_to_menu")],
    )


def get_language_selection_keyboard(
        current_language: Optional[str] = None,
        *,
        include_back: bool = False,
        language: str = DEFAULT_LANGUAGE,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    available_languages = settings.get_available_languages()

    normalized_current = (current_language or "").lower()

    # Собираем кортежи (text, callback)
    items: List[tuple[str, str]] = []
    for code in available_languages:
        norm = code.lower()
        display = _LANGUAGE_DISPLAY_NAMES.get(norm, norm.upper())
        prefix = "✅ " if norm == normalized_current and normalized_current else ""
        items.append((f"{prefix}{display}", f"language_select:{norm}"))

    # Бьём по 2 в ряд
    rows: List[List[tuple[str, str]]] = [items[i:i + 2] for i in range(0, len(items), 2)]

    if include_back:
        rows.append([(texts.BACK, "back_to_menu")])

    return keyboard(*rows)


def get_main_menu_keyboard(
        language: str = DEFAULT_LANGUAGE,
        is_admin: bool = False,
        has_had_paid_subscription: bool = False,
        has_active_subscription: bool = False,
        subscription_is_active: bool = False,
        balance_kopeks: int = 0,
        subscription=None,
        show_resume_checkout: bool = False,
        *,
        is_moderator: bool = False,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    connect_text = texts.t("CONNECT_BUTTON", "🔗 Подключиться")

    if settings.DEBUG:
        print(f"DEBUG KEYBOARD: language={language}, is_admin={is_admin}, has_had_paid={has_had_paid_subscription}, "
              f"has_active={has_active_subscription}, sub_active={subscription_is_active}, balance={balance_kopeks}")

    balance_button_text = (
        texts.BALANCE_BUTTON.format(balance=texts.format_price(balance_kopeks))
        if hasattr(texts, "BALANCE_BUTTON") and balance_kopeks > 0
        else texts.t("BALANCE_BUTTON_DEFAULT", "💰 Баланс: {balance}").format(balance=texts.format_price(balance_kopeks))
    )

    rows: list[list[InlineKeyboardButton | tuple[str, str]]] = []

    # Подключение (если активна подписка)
    if has_active_subscription and subscription_is_active:
        connect_mode = settings.CONNECT_BUTTON_MODE
        subscription_link = get_display_subscription_link(subscription)

        match connect_mode:
            case "miniapp_subscription":
                web_app = types.WebAppInfo(url=subscription_link)
                rows.append([InlineKeyboardButton(text=connect_text, web_app=web_app)])
            case "miniapp_custom":
                web_app = types.WebAppInfo(url=settings.MINIAPP_CUSTOM_URL)
                rows.append([InlineKeyboardButton(text=connect_text, web_app=web_app)])
            case "link":
                rows.append([(connect_text, subscription_link)])
            case "happ_cryptolink":
                rows.append([(connect_text, "open_subscription_link")])
            case _:
                rows.append([(connect_text, "subscription_connect")])

        if happ_download := get_happ_download_button_row(texts):
            rows.append(happ_download)

        rows.append([
            (balance_button_text, "menu_balance"),
            (texts.MENU_SUBSCRIPTION, "menu_subscription"),
        ])
    else:
        rows.append([(balance_button_text, "menu_balance")])

    sub_row = []
    sub_row += [(texts.MENU_TRIAL, "menu_trial")] if (
            not has_had_paid_subscription and not has_active_subscription) else []
    sub_row += [(texts.MENU_BUY_SUBSCRIPTION, "menu_buy")] if (
            not has_active_subscription or not subscription_is_active) else []
    if sub_row:
        rows.append(sub_row)

    if show_resume_checkout:
        rows.append([(texts.RETURN_TO_SUBSCRIPTION_CHECKOUT, "subscription_resume_checkout")])

    rows.append([
        (texts.MENU_PROMOCODE, "menu_promocode"),
        (texts.MENU_REFERRALS, "menu_referrals"),
    ])

    # Статус серверов
    server_status_mode = settings.get_server_status_mode()
    server_status_text = texts.t("MENU_SERVER_STATUS", "📊 Статус серверов")
    if server_status_mode in ("external_link", "external_link_miniapp"):
        status_url = settings.get_server_status_external_url()
        if status_url:
            if server_status_mode == "external_link":
                rows.append([(server_status_text, status_url)])
            else:
                rows.append([InlineKeyboardButton(
                    text=server_status_text,
                    web_app=types.WebAppInfo(url=status_url),
                )])
    elif server_status_mode == "xray":
        rows.append([(server_status_text, "menu_server_status")])

    # Поддержка + Правила
    try:
        from app.services.support_settings_service import SupportSettingsService
        support_enabled = SupportSettingsService.is_support_menu_enabled()
    except Exception:
        support_enabled = settings.SUPPORT_MENU_ENABLED

    support_row: list[InlineKeyboardButton | tuple[str, str]] = []
    if support_enabled:
        support_row.append((texts.MENU_SUPPORT, "menu_support"))
    support_row.append((texts.MENU_RULES, "menu_rules"))
    rows.append(support_row)

    # Язык
    if settings.is_language_selection_enabled():
        rows.append([(texts.MENU_LANGUAGE, "menu_language")])

    # Админ / Модерация
    if is_admin:
        rows.append([(texts.MENU_ADMIN, "admin_panel")])
    elif is_moderator:
        rows.append([("🧑‍⚖️ Модерация", "moderator_panel")])

    return keyboard(*rows)


def get_happ_download_button_row(texts) -> Optional[List[InlineKeyboardButton]]:
    if not settings.is_happ_download_button_enabled():
        return None
    return buttons_row((texts.t("HAPP_DOWNLOAD_BUTTON", "⬇️ Скачать Happ"), "subscription_happ_download"))


def get_happ_cryptolink_keyboard(
        subscription_link: str,
        language: str = DEFAULT_LANGUAGE,
        redirect_link: Optional[str] = None,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    final_redirect_link = redirect_link or get_happ_cryptolink_redirect_link(subscription_link)

    rows: list[list[tuple[str, str] | InlineKeyboardButton]] = []

    if final_redirect_link:
        rows.append([(texts.t("CONNECT_BUTTON", "🔗 Подключиться"), final_redirect_link)])  # URL

    rows += [
        [(texts.t("HAPP_PLATFORM_IOS", "🍎 iOS"), "happ_download_ios")],
        [(texts.t("HAPP_PLATFORM_ANDROID", "🤖 Android"), "happ_download_android")],
        [(texts.t("HAPP_PLATFORM_MACOS", "🖥️ Mac OS"), "happ_download_macos")],
        [(texts.t("HAPP_PLATFORM_WINDOWS", "💻 Windows"), "happ_download_windows")],
        [(texts.t("BACK_TO_MAIN_MENU_BUTTON", "⬅️ В главное меню"), "back_to_menu")],
    ]
    return keyboard(*rows)


def get_happ_download_platform_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.t("HAPP_PLATFORM_IOS", "🍎 iOS"), "happ_download_ios")],
        [(texts.t("HAPP_PLATFORM_ANDROID", "🤖 Android"), "happ_download_android")],
        [(texts.t("HAPP_PLATFORM_MACOS", "🖥️ Mac OS"), "happ_download_macos")],
        [(texts.t("HAPP_PLATFORM_WINDOWS", "💻 Windows"), "happ_download_windows")],
        [(texts.BACK, "happ_download_close")],
    )


def get_happ_download_link_keyboard(language: str, link: str) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.t("HAPP_DOWNLOAD_OPEN_LINK", "🔗 Открыть ссылку"), link)],
        [(texts.BACK, "happ_download_back")],
    )


def get_back_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard([(texts.BACK, "back_to_menu")])


def get_server_status_keyboard(
        language: str,
        current_page: int,
        total_pages: int,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)

    rows = [[(texts.t("SERVER_STATUS_REFRESH", "🔄 Обновить"), f"server_status_page:{current_page}")]]

    if total_pages > 1:
        nav_row: list[tuple[str, str]] = []
        if current_page > 1:
            nav_row.append((texts.t("SERVER_STATUS_PREV_PAGE", "⬅️ Назад"),
                            f"server_status_page:{current_page - 1}"))
        if current_page < total_pages:
            nav_row.append((texts.t("SERVER_STATUS_NEXT_PAGE", "Вперед ➡️"),
                            f"server_status_page:{current_page + 1}"))
        if nav_row:
            rows.append(nav_row)

    rows.append([(texts.BACK, "back_to_menu")])

    return keyboard(*rows)


def get_insufficient_balance_keyboard(
        language: str = DEFAULT_LANGUAGE,
        resume_callback: str | None = None,
        amount_kopeks: int | None = None,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    kb = get_payment_methods_keyboard(amount_kopeks or 0, language)
    rows = kb.inline_keyboard

    def _is_back_row(row: list[InlineKeyboardButton]) -> bool:
        return (
                len(row) == 1
                and isinstance(row[0], InlineKeyboardButton)
                and getattr(row[0], "callback_data", None) in {"menu_balance", "back_to_menu"}
        )

    back_idx: int | None = None
    if rows and _is_back_row(rows[-1]):
        rows[-1][0] = button(texts.t("PAYMENT_RETURN_HOME_BUTTON", "🏠 На главную"), "back_to_menu")
        back_idx = len(rows) - 1

    if resume_callback:
        return_row = [button(texts.RETURN_TO_SUBSCRIPTION_CHECKOUT, resume_callback)]
        rows.insert(back_idx if back_idx is not None else len(rows), return_row)

    return kb


def get_subscription_keyboard(
        language: str = DEFAULT_LANGUAGE,
        has_subscription: bool = False,
        is_trial: bool = False,
        subscription=None,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    rows: list[list[tuple[str, str] | InlineKeyboardButton]] = []

    if has_subscription:
        subscription_link = get_display_subscription_link(subscription) if subscription else None

        if subscription_link:
            mode = settings.CONNECT_BUTTON_MODE
            if mode == "miniapp_subscription":
                rows.append([
                    InlineKeyboardButton(
                        text=texts.t("CONNECT_BUTTON", "🔗 Подключиться"),
                        web_app=types.WebAppInfo(url=subscription_link),
                    )
                ])
            elif mode == "miniapp_custom":
                if settings.MINIAPP_CUSTOM_URL:
                    rows.append([
                        InlineKeyboardButton(
                            text=texts.t("CONNECT_BUTTON", "🔗 Подключиться"),
                            web_app=types.WebAppInfo(url=settings.MINIAPP_CUSTOM_URL),
                        )
                    ])
                else:
                    rows.append([(texts.t("CONNECT_BUTTON", "🔗 Подключиться"), "subscription_connect")])
            elif mode == "link":
                rows.append([
                    InlineKeyboardButton(
                        text=texts.t("CONNECT_BUTTON", "🔗 Подключиться"),
                        url=subscription_link,
                    )
                ])
            elif mode == "happ_cryptolink":
                rows.append([(texts.t("CONNECT_BUTTON", "🔗 Подключиться"), "open_subscription_link")])
            else:
                rows.append([(texts.t("CONNECT_BUTTON", "🔗 Подключиться"), "subscription_connect")])
        elif settings.CONNECT_BUTTON_MODE == "miniapp_custom":
            rows.append([
                InlineKeyboardButton(
                    text=texts.t("CONNECT_BUTTON", "🔗 Подключиться"),
                    web_app=types.WebAppInfo(url=settings.MINIAPP_CUSTOM_URL),
                )
            ])
        else:
            rows.append([(texts.t("CONNECT_BUTTON", "🔗 Подключиться"), "subscription_connect")])

        happ_row = get_happ_download_button_row(texts)
        if happ_row:
            rows.append(happ_row)  # уже список InlineKeyboardButton

        if not is_trial:
            rows.append([(texts.MENU_EXTEND_SUBSCRIPTION, "subscription_extend")])
            rows.append([(texts.t("AUTOPAY_BUTTON", "💳 Автоплатеж"), "subscription_autopay")])

        if is_trial:
            rows.append([(texts.MENU_BUY_SUBSCRIPTION, "subscription_upgrade")])
        else:
            rows.append([(texts.t("SUBSCRIPTION_SETTINGS_BUTTON", "⚙️ Настройки подписки"), "subscription_settings")])

    rows.append([(texts.BACK, "back_to_menu")])
    return keyboard(*rows)


def get_payment_methods_keyboard_with_cart(
        language: str = "ru",
        amount_kopeks: int = 0,
) -> InlineKeyboardMarkup:
    keyboard = get_payment_methods_keyboard(amount_kopeks, language)

    # Добавляем кнопку "Очистить корзину"
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(
            text="🗑️ Очистить корзину и вернуться",
            callback_data="clear_saved_cart"
        )
    ])

    return keyboard


def get_subscription_confirm_keyboard_with_cart(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("✅ Подтвердить покупку", "subscription_confirm")],
        [("🗑️ Очистить корзину", "clear_saved_cart")],
        [("🔙 Назад", "back_to_menu")],
    )


def get_insufficient_balance_keyboard_with_cart(
        language: str = "ru",
        amount_kopeks: int = 0,
) -> InlineKeyboardMarkup:
    base = get_insufficient_balance_keyboard(language, amount_kopeks=amount_kopeks)
    return keyboard(
        [("🗑️ Очистить корзину и вернуться", "clear_saved_cart")],
        *base.inline_keyboard,  # существующие ряды как есть
    )


def get_trial_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.t("TRIAL_ACTIVATE_BUTTON", "🎁 Активировать"), "trial_activate"),
         (texts.BACK, "back_to_menu")],
    )


def get_subscription_period_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    available_periods = settings.get_available_subscription_periods()

    period_texts = {
        14: texts.PERIOD_14_DAYS,
        30: texts.PERIOD_30_DAYS,
        60: texts.PERIOD_60_DAYS,
        90: texts.PERIOD_90_DAYS,
        180: texts.PERIOD_180_DAYS,
        360: texts.PERIOD_360_DAYS,
    }

    rows = [
        [(period_texts[d], f"period_{d}")]
        for d in available_periods
        if d in period_texts
    ]
    rows.append([(texts.BACK, "back_to_menu")])
    return keyboard(*rows)


def get_traffic_packages_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    if settings.is_traffic_fixed():
        return get_back_keyboard(language)

    texts = get_texts(language)
    rows = []

    for package in settings.get_traffic_packages():
        gb = package["gb"]
        price = package["price"]
        enabled = package["enabled"]

        if not enabled:
            continue

        if gb == 0:
            text = f"♾️ Безлимит - {settings.format_price(price)}"
        else:
            text = f"📊 {gb} ГБ - {settings.format_price(price)}"

        rows.append([(text, f"traffic_{gb}")])

    if not rows:
        rows.append([(texts.t("TRAFFIC_PACKAGES_NOT_CONFIGURED", "⚠️ Пакеты трафика не настроены"),
                      "no_traffic_packages")])

    rows.append([(texts.BACK, "subscription_config_back")])
    return keyboard(*rows)


def get_countries_keyboard(
        countries: List[dict],
        selected: List[str],
        language: str = DEFAULT_LANGUAGE
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    rows = []

    for country in countries:
        if not country.get("is_available", True):
            continue

        emoji = "✅" if country["uuid"] in selected else "⚪"
        price_text = (
            f" (+{texts.format_price(country['price_kopeks'])})"
            if country["price_kopeks"] > 0
            else " (Бесплатно)"
        )

        rows.append([
            (f"{emoji} {country['name']}{price_text}", f"country_{country['uuid']}")
        ])

    if not rows:
        rows.append([(texts.t("NO_SERVERS_AVAILABLE", "❌ Нет доступных серверов"), "no_servers")])

    rows.append([(texts.t("CONTINUE_BUTTON", "✅ Продолжить"), "countries_continue")])
    rows.append([(texts.BACK, "subscription_config_back")])

    return keyboard(*rows)


def get_devices_keyboard(current: int, language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)

    start_devices = settings.DEFAULT_DEVICE_LIMIT
    max_devices = settings.MAX_DEVICES_LIMIT if settings.MAX_DEVICES_LIMIT > 0 else 50
    end_devices = min(max_devices + 1, start_devices + 10)

    btns: list[InlineKeyboardButton] = []
    for devices in range(start_devices, end_devices):
        price = max(0, devices - settings.DEFAULT_DEVICE_LIMIT) * settings.PRICE_PER_DEVICE
        price_text = f" (+{texts.format_price(price)})" if price > 0 else " (вкл.)"
        emoji = "✅" if devices == current else "⚪"
        btns.append(InlineKeyboardButton(text=f"{emoji} {devices}{price_text}",
                                         callback_data=f"devices_{devices}"))

    rows: list[list[InlineKeyboardButton]] = []
    for i in range(0, len(btns), 2):
        rows.append(btns[i:i + 2])

    rows += [
        [InlineKeyboardButton(text=texts.t("CONTINUE_BUTTON", "✅ Продолжить"), callback_data="devices_continue")],
        [InlineKeyboardButton(text=texts.BACK, callback_data="subscription_config_back")],
    ]
    return keyboard(*rows)


def _get_device_declension(count: int) -> str:
    if count % 10 == 1 and count % 100 != 11:
        return "устройство"
    elif count % 10 in (2, 3, 4) and count % 100 not in (12, 13, 14):
        return "устройства"
    return "устройств"


def get_subscription_confirm_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.CONFIRM, "subscription_confirm"), (texts.CANCEL, "subscription_cancel")]
    )


def get_balance_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.BALANCE_HISTORY, "balance_history"),
         (texts.BALANCE_TOP_UP, "balance_topup")],
        [(texts.BACK, "back_to_menu")],
    )


def get_payment_methods_keyboard(amount_kopeks: int, language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    rows: list[list[tuple[str, str]]] = []

    amount_kopeks = max(0, int(amount_kopeks or 0))

    def _build_callback(method: str) -> str:
        return f"topup_amount|{method}|{amount_kopeks}" if amount_kopeks > 0 else f"topup_{method}"

    # локальные тексты
    stars_text = texts.t("PAYMENT_TELEGRAM_STARS", "⭐ Telegram Stars")
    yookassa_text = texts.t("PAYMENT_CARD_YOOKASSA", "💳 Банковская карта (YooKassa)")
    yookassa_sbp_text = texts.t("PAYMENT_SBP_YOOKASSA", "🏦 Оплатить по СБП (YooKassa)")
    tribute_text = texts.t("PAYMENT_CARD_TRIBUTE", "💳 Банковская карта (Tribute)")
    mulenpay_text = texts.t("PAYMENT_CARD_MULENPAY", "💳 Банковская карта (Mulen Pay)")
    pal24_text = texts.t("PAYMENT_CARD_PAL24", "🏦 СБП (PayPalych)")
    cryptobot_text = texts.t("PAYMENT_CRYPTOBOT", "🪙 Криптовалюта (CryptoBot)")
    support_text = texts.t("PAYMENT_VIA_SUPPORT", "🛠️ Через поддержку")
    unavailable_text = texts.t("PAYMENTS_TEMPORARILY_UNAVAILABLE", "⚠️ Способы оплаты временно недоступны")

    if settings.TELEGRAM_STARS_ENABLED:
        rows.append([(stars_text, _build_callback("stars"))])

    if settings.is_yookassa_enabled():
        rows.append([(yookassa_text, _build_callback("yookassa"))])
        if settings.YOOKASSA_SBP_ENABLED:
            rows.append([(yookassa_sbp_text, _build_callback("yookassa_sbp"))])

    if settings.TRIBUTE_ENABLED:
        rows.append([(tribute_text, _build_callback("tribute"))])

    if settings.is_mulenpay_enabled():
        rows.append([(mulenpay_text, _build_callback("mulenpay"))])

    if settings.is_pal24_enabled():
        rows.append([(pal24_text, _build_callback("pal24"))])

    if settings.is_cryptobot_enabled():
        rows.append([(cryptobot_text, _build_callback("cryptobot"))])

    rows.append([(support_text, "topup_support")])

    if len(rows) == 1:
        rows.insert(0, [(unavailable_text, "payment_methods_unavailable")])

    rows.append([(texts.BACK, "menu_balance")])

    return keyboard(*rows)


def get_yookassa_payment_keyboard(
        payment_id: str,
        amount_kopeks: int,
        confirmation_url: str,
        language: str = DEFAULT_LANGUAGE,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [InlineKeyboardButton(text=texts.t("PAY_NOW_BUTTON", "💳 Оплатить"), url=confirmation_url)],
        [(texts.t("CHECK_STATUS_BUTTON", "📊 Проверить статус"), f"check_yookassa_status_{payment_id}")],
        [(texts.t("MY_BALANCE_BUTTON", "💰 Мой баланс"), "menu_balance")],
    )


def get_autopay_notification_keyboard(subscription_id: int, language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.t("TOPUP_BALANCE_BUTTON", "💳 Пополнить баланс"), "balance_topup")],
        [(texts.t("MY_SUBSCRIPTION_BUTTON", "📱 Моя подписка"), "menu_subscription")],
    )


def get_subscription_expiring_keyboard(subscription_id: int, language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.MENU_EXTEND_SUBSCRIPTION, "subscription_extend")],
        [(texts.t("TOPUP_BALANCE_BUTTON", "💳 Пополнить баланс"), "balance_topup")],
        [(texts.t("MY_SUBSCRIPTION_BUTTON", "📱 Моя подписка"), "menu_subscription")],
    )


def get_referral_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.t("CREATE_INVITE_BUTTON", "📝 Создать приглашение"), "referral_create_invite")],
        [(texts.t("SHOW_QR_BUTTON", "📱 Показать QR код"), "referral_show_qr")],
        [(texts.t("REFERRAL_LIST_BUTTON", "👥 Список рефералов"), "referral_list")],
        [(texts.t("REFERRAL_ANALYTICS_BUTTON", "📊 Аналитика"), "referral_analytics")],
        [(texts.BACK, "back_to_menu")],
    )


def get_support_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    try:
        from app.services.support_settings_service import SupportSettingsService
        tickets_enabled = SupportSettingsService.is_tickets_enabled()
        contact_enabled = SupportSettingsService.is_contact_enabled()
    except Exception:
        tickets_enabled = True
        contact_enabled = True

    rows: list[list[tuple[str, str] | InlineKeyboardButton]] = []

    if tickets_enabled:
        rows.append([(texts.t("CREATE_TICKET_BUTTON", "🎫 Создать тикет"), "create_ticket")])
        rows.append([(texts.t("MY_TICKETS_BUTTON", "📋 Мои тикеты"), "my_tickets")])

    if contact_enabled and settings.get_support_contact_url():
        rows.append([
            InlineKeyboardButton(
                text=texts.t("CONTACT_SUPPORT_BUTTON", "💬 Связаться с поддержкой"),
                url=settings.get_support_contact_url() or "https://t.me/",
            )
        ])

    rows.append([(texts.BACK, "back_to_menu")])
    return keyboard(*rows)


def get_pagination_keyboard(
        current_page: int,
        total_pages: int,
        callback_prefix: str,
        language: str = DEFAULT_LANGUAGE,
) -> list[list[InlineKeyboardButton]]:
    texts = get_texts(language)
    rows: list[list[InlineKeyboardButton]] = []

    if total_pages > 1:
        row: list[InlineKeyboardButton] = []
        if current_page > 1:
            row.append(InlineKeyboardButton(
                text=texts.t("PAGINATION_PREV", "⬅️"),
                callback_data=f"{callback_prefix}_page_{current_page - 1}",
            ))
        row.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="current_page"))
        if current_page < total_pages:
            row.append(InlineKeyboardButton(
                text=texts.t("PAGINATION_NEXT", "➡️"),
                callback_data=f"{callback_prefix}_page_{current_page + 1}",
            ))
        rows.append(row)

    return rows


def get_confirmation_keyboard(
        confirm_data: str,
        cancel_data: str = "cancel",
        language: str = DEFAULT_LANGUAGE,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.YES, confirm_data), (texts.NO, cancel_data)],
    )


def get_autopay_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.t("ENABLE_BUTTON", "✅ Включить"), "autopay_enable"),
         (texts.t("DISABLE_BUTTON", "❌ Выключить"), "autopay_disable")],
        [(texts.t("AUTOPAY_SET_DAYS_BUTTON", "⚙️ Настроить дни"), "autopay_set_days")],
        [(texts.BACK, "menu_subscription")],
    )


def _get_days_suffix(days: int) -> str:
    if days == 1:
        return "ь"
    if 2 <= days <= 4:
        return "я"
    return "ей"


def get_autopay_days_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    rows = [
        [(f"{days} дн{_get_days_suffix(days)}", f"autopay_days_{days}")]
        for days in (1, 3, 7, 14)
    ]
    rows.append([(texts.BACK, "subscription_autopay")])
    return keyboard(*rows)


def get_extend_subscription_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)

    periods = [
        (14, f"📅 14 дней - {settings.format_price(settings.PRICE_14_DAYS)}"),
        (30, f"📅 30 дней - {settings.format_price(settings.PRICE_30_DAYS)}"),
        (60, f"📅 60 дней - {settings.format_price(settings.PRICE_60_DAYS)}"),
        (90, f"📅 90 дней - {settings.format_price(settings.PRICE_90_DAYS)}"),
    ]

    rows = [[(text, f"extend_period_{days}")] for days, text in periods]
    rows.append([(texts.BACK, "menu_subscription")])
    return keyboard(*rows)


def get_add_traffic_keyboard(
        language: str = DEFAULT_LANGUAGE,
        subscription_end_date: datetime | None = None,
        discount_percent: int = 0,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)

    months_multiplier = 1
    period_text = ""
    if subscription_end_date:
        months_multiplier = get_remaining_months(subscription_end_date)
        if months_multiplier > 1:
            period_text = f" (за {months_multiplier} мес)"

    packages = settings.get_traffic_packages()
    enabled_packages = [pkg for pkg in packages if pkg["enabled"]]

    if not enabled_packages:
        return keyboard(
            [(texts.t("NO_TRAFFIC_PACKAGES", "❌ Нет доступных пакетов"), "no_traffic_packages")],
            [(texts.BACK, "menu_subscription")],
        )

    rows: list[list[tuple[str, str]]] = []

    for package in enabled_packages:
        gb = package["gb"]
        price_per_month = package["price"]
        discounted_pm, discount_pm = apply_percentage_discount(price_per_month, discount_percent)
        total_price = discounted_pm * months_multiplier
        total_discount = discount_pm * months_multiplier

        if gb == 0:
            text = (
                f"♾️ Безлимитный трафик - {total_price // 100} ₽{period_text}"
                if language == "ru"
                else f"♾️ Unlimited traffic - {total_price // 100} ₽{period_text}"
            )
        else:
            text = (
                f"📊 +{gb} ГБ трафика - {total_price // 100} ₽{period_text}"
                if language == "ru"
                else f"📊 +{gb} GB traffic - {total_price // 100} ₽{period_text}"
            )

        if discount_percent > 0 and total_discount > 0:
            text += f" (скидка {discount_percent}%: -{total_discount // 100}₽)"

        rows.append([(text, f"add_traffic_{gb}")])

    rows.append([(texts.BACK, "menu_subscription")])
    return keyboard(*rows)


def get_change_devices_keyboard(
        current_devices: int,
        language: str = DEFAULT_LANGUAGE,
        subscription_end_date: datetime | None = None,
        discount_percent: int = 0,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)

    months_multiplier = 1
    period_text = ""
    if subscription_end_date:
        months_multiplier = get_remaining_months(subscription_end_date)
        if months_multiplier > 1:
            period_text = f" (за {months_multiplier} мес)"

    device_price_per_month = settings.PRICE_PER_DEVICE
    rows: list[list[tuple[str, str]]] = []

    max_devices = settings.MAX_DEVICES_LIMIT if settings.MAX_DEVICES_LIMIT > 0 else 20
    start_range = max(1, min(current_devices - 3, max_devices - 6))
    end_range = min(max_devices + 1, max(current_devices + 4, 7))

    for devices_count in range(start_range, end_range):
        if devices_count == current_devices:
            emoji = "✅"
            action_text = " (текущее)"
            price_text = ""
        elif devices_count > current_devices:
            emoji = "➕"
            action_text = ""
            current_chargeable = max(0, current_devices - settings.DEFAULT_DEVICE_LIMIT)
            new_chargeable = max(0, devices_count - settings.DEFAULT_DEVICE_LIMIT)
            chargeable_devices = new_chargeable - current_chargeable

            if chargeable_devices > 0:
                price_pm = chargeable_devices * device_price_per_month
                discounted_pm, discount_pm = apply_percentage_discount(price_pm, discount_percent)
                total_price = discounted_pm * months_multiplier
                price_text = f" (+{total_price // 100}₽{period_text})"
                if discount_percent > 0 and discount_pm * months_multiplier > 0:
                    price_text += f" (скидка {discount_percent}%: -{(discount_pm * months_multiplier) // 100}₽)"
            else:
                price_text = " (бесплатно)"
        else:
            emoji = "➖"
            action_text = ""
            price_text = " (без возврата)"

        btn_text = f"{emoji} {devices_count} устр.{action_text}{price_text}"
        rows.append([(btn_text, f"change_devices_{devices_count}")])

    if current_devices < start_range or current_devices >= end_range:
        rows.insert(0, [(f"✅ {current_devices} устр. (текущее)", f"change_devices_{current_devices}")])

    rows.append([(texts.BACK, "subscription_settings")])
    return keyboard(*rows)


def get_confirm_change_devices_keyboard(
        new_devices_count: int,
        price: int,
        language: str = DEFAULT_LANGUAGE,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.t("CONFIRM_CHANGE_BUTTON", "✅ Подтвердить изменение"),
          f"confirm_change_devices_{new_devices_count}_{price}")],
        [(texts.CANCEL, "subscription_settings")],
    )


def get_reset_traffic_confirm_keyboard(price_kopeks: int, language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    if settings.is_traffic_fixed():
        return get_back_keyboard(language)

    texts = get_texts(language)
    return keyboard(
        [(f"✅ Сбросить за {settings.format_price(price_kopeks)}", "confirm_reset_traffic")],
        [(texts.t("PENDING_CANCEL_BUTTON", "⌛ Отмена"), "menu_subscription")],
    )


def get_manage_countries_keyboard(
    countries: list[dict],
    selected: list[str],
    current_subscription_countries: list[str],
    language: str = DEFAULT_LANGUAGE,
    subscription_end_date: datetime | None = None,
    discount_percent: int = 0,
) -> InlineKeyboardMarkup:

    texts = get_texts(language)
    months_multiplier = 1
    if subscription_end_date:
        months_multiplier = get_remaining_months(subscription_end_date)
        logger.info(f"🔍 Расчет для управления странами: осталось {months_multiplier} месяцев до {subscription_end_date}")

    rows: list[list[tuple[str, str]]] = []
    total_cost = 0

    for country in countries:
        if not country.get("is_available", True):
            continue

        uuid = country["uuid"]
        name = country["name"]
        price_per_month = country["price_kopeks"]

        discounted_pm, discount_pm = apply_percentage_discount(price_per_month, discount_percent)

        if uuid in current_subscription_countries:
            icon = "✅" if uuid in selected else "➖"
        else:
            if uuid in selected:
                icon = "➕"
                total_cost += discounted_pm * months_multiplier
            else:
                icon = "⚪"

        if uuid not in current_subscription_countries and uuid in selected:
            total_price = discounted_pm * months_multiplier
            if months_multiplier > 1:
                price_text = f" ({discounted_pm // 100}₽/мес × {months_multiplier} = {total_price // 100}₽)"
                logger.info(
                    "🔍 Сервер %s: %.2f₽/мес × %s мес = %.2f₽ (скидка %.2f₽)",
                    name,
                    discounted_pm / 100,
                    months_multiplier,
                    total_price / 100,
                    (discount_pm * months_multiplier) / 100,
                )
            else:
                price_text = f" ({total_price // 100}₽)"
            if discount_percent > 0 and discount_pm * months_multiplier > 0:
                price_text += f" (скидка {discount_percent}%: -{(discount_pm * months_multiplier)//100}₽)"
            display_name = f"{icon} {name}{price_text}"
        else:
            display_name = f"{icon} {name}"

        rows.append([(display_name, f"country_manage_{uuid}")])

    if total_cost > 0:
        apply_text = f"✅ Применить изменения ({total_cost // 100} ₽)"
        logger.info(f"🔍 Общая стоимость новых серверов: {total_cost / 100}₽")
    else:
        apply_text = "✅ Применить изменения"

    rows.append([(apply_text, "countries_apply")])
    rows.append([(texts.BACK, "menu_subscription")])
    return keyboard(*rows)


def get_device_selection_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)

    rows: list[list[tuple[str, str]]] = [
        [(texts.t("DEVICE_GUIDE_IOS", "📱 iOS (iPhone/iPad)"), "device_guide_ios"),
         (texts.t("DEVICE_GUIDE_ANDROID", "🤖 Android"), "device_guide_android")],
        [(texts.t("DEVICE_GUIDE_WINDOWS", "💻 Windows"), "device_guide_windows"),
         (texts.t("DEVICE_GUIDE_MAC", "🎯 macOS"), "device_guide_mac")],
        [(texts.t("DEVICE_GUIDE_ANDROID_TV", "📺 Android TV"), "device_guide_tv")],
    ]

    if settings.CONNECT_BUTTON_MODE == "guide":
        rows.append([(texts.t("SHOW_SUBSCRIPTION_LINK", "📋 Показать ссылку подписки"), "open_subscription_link")])

    rows.append([(texts.BACK, "menu_subscription")])
    return keyboard(*rows)


def get_connection_guide_keyboard(
    subscription_url: str,
    app: dict,
    language: str = DEFAULT_LANGUAGE,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    rows: list[list[InlineKeyboardButton | tuple[str, str]]] = []

    if "installationStep" in app and "buttons" in app["installationStep"]:
        app_buttons: list[InlineKeyboardButton] = []
        for btn in app["installationStep"]["buttons"]:
            btn_text = btn["buttonText"].get(language, btn["buttonText"]["en"])
            app_buttons.append(InlineKeyboardButton(text=f"📥 {btn_text}", url=btn["buttonLink"]))
            if len(app_buttons) == 2:
                rows.append(app_buttons)
                app_buttons = []
        if app_buttons:
            rows.append(app_buttons)

    if settings.is_happ_cryptolink_mode():
        copy_btn = (texts.t("COPY_SUBSCRIPTION_LINK", "📋 Скопировать ссылку подписки"), "open_subscription_link")
    else:
        rows.append([InlineKeyboardButton(
            text=texts.t("COPY_SUBSCRIPTION_LINK", "📋 Скопировать ссылку подписки"),
            url=subscription_url
        )])
        copy_btn = None

    if copy_btn:
        rows.append([copy_btn])

    rows.append([(texts.t("CHOOSE_ANOTHER_DEVICE", "📱 Выбрать другое устройство"), "subscription_connect")])
    rows.append([(texts.t("BACK_TO_SUBSCRIPTION", "⬅️ К подписке"), "menu_subscription")])
    return keyboard(*rows)


def get_app_selection_keyboard(
    device_type: str,
    apps: list,
    language: str = DEFAULT_LANGUAGE
) -> InlineKeyboardMarkup:
    texts = get_texts(language)

    rows: list[list[tuple[str, str]]] = []
    for app in apps:
        app_name = f"⭐ {app['name']}" if app.get("isFeatured") else app["name"]
        rows.append([(app_name, f"app_{device_type}_{app['id']}")])

    rows += [
        [(texts.t("CHOOSE_ANOTHER_DEVICE", "📱 Выбрать другое устройство"), "subscription_connect")],
        [(texts.t("BACK_TO_SUBSCRIPTION", "⬅️ К подписке"), "menu_subscription")],
    ]
    return keyboard(*rows)


def get_specific_app_keyboard(
    subscription_url: str,
    app: dict,
    device_type: str,
    language: str = DEFAULT_LANGUAGE
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    rows: list[list[tuple[str, str] | InlineKeyboardButton]] = []

    if "installationStep" in app and "buttons" in app["installationStep"]:
        pair: list[InlineKeyboardButton] = []
        for btn in app["installationStep"]["buttons"]:
            btn_text = btn["buttonText"].get(language, btn["buttonText"]["en"])
            pair.append(InlineKeyboardButton(text=f"📥 {btn_text}", url=btn["buttonLink"]))
            if len(pair) == 2:
                rows.append(pair)
                pair = []
        if pair:
            rows.append(pair)

    if settings.is_happ_cryptolink_mode():
        copy_btn = InlineKeyboardButton(
            text=texts.t("COPY_SUBSCRIPTION_LINK", "📋 Скопировать ссылку подписки"),
            callback_data="open_subscription_link",
        )
    else:
        copy_btn = InlineKeyboardButton(
            text=texts.t("COPY_SUBSCRIPTION_LINK", "📋 Скопировать ссылку подписки"),
            url=subscription_url,
        )
    rows.append([copy_btn])

    if "additionalAfterAddSubscriptionStep" in app and "buttons" in app["additionalAfterAddSubscriptionStep"]:
        for btn in app["additionalAfterAddSubscriptionStep"]["buttons"]:
            btn_text = btn["buttonText"].get(language, btn["buttonText"]["en"])
            rows.append([InlineKeyboardButton(text=btn_text, url=btn["buttonLink"])])

    rows += [
        [(texts.t("OTHER_APPS_BUTTON", "📋 Другие приложения"), f"app_list_{device_type}")],
        [(texts.t("CHOOSE_ANOTHER_DEVICE", "📱 Выбрать другое устройство"), "subscription_connect")],
        [(texts.t("BACK_TO_SUBSCRIPTION", "⬅️ К подписке"), "menu_subscription")],
    ]
    return keyboard(*rows)


def get_extend_subscription_keyboard_with_prices(language: str, prices: dict) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    rows: list[list[tuple[str, str]]] = []

    available_periods = settings.get_available_renewal_periods()
    for days in available_periods:
        if days in prices:
            period_display = format_period_description(days, language)
            rows.append([(f"📅 {period_display} - {texts.format_price(prices[days])}", f"extend_period_{days}")])

    rows.append([(texts.BACK, "menu_subscription")])
    return keyboard(*rows)


def get_cryptobot_payment_keyboard(
    payment_id: str,
    local_payment_id: int,
    amount_usd: float,
    asset: str,
    bot_invoice_url: str,
    language: str = DEFAULT_LANGUAGE
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [InlineKeyboardButton(text=texts.t("PAY_WITH_COINS_BUTTON", "🪙 Оплатить"), url=bot_invoice_url)],
        [(texts.t("CHECK_STATUS_BUTTON", "📊 Проверить статус"), f"check_cryptobot_{local_payment_id}")],
        [(texts.t("MY_BALANCE_BUTTON", "💰 Мой баланс"), "menu_balance")],
    )


def get_devices_management_keyboard(
    devices: list[dict],
    pagination,
    language: str = DEFAULT_LANGUAGE
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    rows: list[list[tuple[str, str] | InlineKeyboardButton]] = []

    for i, device in enumerate(devices):
        platform = device.get("platform", "Unknown")
        model = device.get("deviceModel", "Unknown")
        info = f"{platform} - {model}"
        if len(info) > 25:
            info = info[:22] + "..."
        rows.append([(f"🔄 {info}", f"reset_device_{i}_{pagination.page}")])

    if pagination.total_pages > 1:
        nav: list[InlineKeyboardButton] = []
        if getattr(pagination, "has_prev", False):
            nav.append(InlineKeyboardButton(
                text=texts.t("PAGINATION_PREV", "⬅️"),
                callback_data=f"devices_page_{pagination.prev_page}",
            ))
        nav.append(InlineKeyboardButton(text=f"{pagination.page}/{pagination.total_pages}", callback_data="current_page"))
        if getattr(pagination, "has_next", False):
            nav.append(InlineKeyboardButton(
                text=texts.t("PAGINATION_NEXT", "➡️"),
                callback_data=f"devices_page_{pagination.next_page}",
            ))
        rows.append(nav)

    rows.append([(texts.t("RESET_ALL_DEVICES_BUTTON", "🔄 Сбросить все устройства"), "reset_all_devices")])
    rows.append([(texts.BACK, "subscription_settings")])
    return keyboard(*rows)


def get_updated_subscription_settings_keyboard(
    language: str = DEFAULT_LANGUAGE,
    show_countries_management: bool = True,
) -> InlineKeyboardMarkup:
    from app.config import settings

    texts = get_texts(language)
    rows: list[list[tuple[str, str]]] = []

    if show_countries_management:
        rows.append([(texts.t("ADD_COUNTRIES_BUTTON", "🌐 Добавить страны"), "subscription_add_countries")])

    if settings.is_traffic_selectable():
        rows.append([(texts.t("SWITCH_TRAFFIC_BUTTON", "🔄 Переключить трафик"), "subscription_switch_traffic")])
        rows.append([(texts.t("RESET_TRAFFIC_BUTTON", "🔄 Сбросить трафик"), "subscription_reset_traffic")])

    rows.extend([
        [(texts.t("CHANGE_DEVICES_BUTTON", "📱 Изменить устройства"), "subscription_change_devices")],
        [(texts.t("MANAGE_DEVICES_BUTTON", "🔧 Управление устройствами"), "subscription_manage_devices")],
    ])

    rows.append([(texts.BACK, "menu_subscription")])
    return keyboard(*rows)


def get_device_reset_confirm_keyboard(
    device_info: str,
    device_index: int,
    page: int,
    language: str = DEFAULT_LANGUAGE,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.t("RESET_DEVICE_CONFIRM_BUTTON", "✅ Да, сбросить это устройство"),
          f"confirm_reset_device_{device_index}_{page}")],
        [(texts.CANCEL, f"devices_page_{page}")],
    )


def get_device_management_help_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.t("DEVICE_CONNECTION_HELP", "❓ Как подключить устройство заново?"), "device_connection_help")],
        [(texts.t("MANAGE_DEVICES_BUTTON", "🔧 Управление устройствами"), "subscription_manage_devices")],
        [(texts.t("BACK_TO_SUBSCRIPTION", "⬅️ К подписке"), "menu_subscription")],
    )


# ==================== TICKET KEYBOARDS ====================

def get_ticket_cancel_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=texts.t("CANCEL_TICKET_CREATION", "❌ Отменить создание тикета"),
                callback_data="cancel_ticket_creation"
            )
        ]
    ])


def get_my_tickets_keyboard(
        tickets: List[dict],
        current_page: int = 1,
        total_pages: int = 1,
        language: str = DEFAULT_LANGUAGE,
        page_prefix: str = "my_tickets_page_"
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    keyboard = []

    for ticket in tickets:
        status_emoji = ticket.get('status_emoji', '❓')
        # Override status emoji for closed tickets in admin list
        if ticket.get('is_closed', False):
            status_emoji = '✅'
        title = ticket.get('title', 'Без названия')[:25]
        button_text = f"{status_emoji} #{ticket['id']} {title}"

        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"view_ticket_{ticket['id']}"
            )
        ])

    # Пагинация
    if total_pages > 1:
        nav_row = []

        if current_page > 1:
            nav_row.append(
                InlineKeyboardButton(
                    text=texts.t("PAGINATION_PREV", "⬅️"),
                    callback_data=f"{page_prefix}{current_page - 1}"
                )
            )

        nav_row.append(
            InlineKeyboardButton(
                text=f"{current_page}/{total_pages}",
                callback_data="current_page"
            )
        )

        if current_page < total_pages:
            nav_row.append(
                InlineKeyboardButton(
                    text=texts.t("PAGINATION_NEXT", "➡️"),
                    callback_data=f"{page_prefix}{current_page + 1}"
                )
            )

        keyboard.append(nav_row)

    keyboard.append([
        InlineKeyboardButton(text=texts.BACK, callback_data="menu_support")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_ticket_view_keyboard(
        ticket_id: int,
        is_closed: bool = False,
        language: str = DEFAULT_LANGUAGE
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    keyboard = []

    if not is_closed:
        keyboard.append([
            InlineKeyboardButton(
                text=texts.t("REPLY_TO_TICKET", "💬 Ответить"),
                callback_data=f"reply_ticket_{ticket_id}"
            )
        ])

    if not is_closed:
        keyboard.append([
            InlineKeyboardButton(
                text=texts.t("CLOSE_TICKET", "🔒 Закрыть тикет"),
                callback_data=f"close_ticket_{ticket_id}"
            )
        ])

    keyboard.append([
        InlineKeyboardButton(text=texts.BACK, callback_data="my_tickets")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def get_ticket_reply_cancel_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text=texts.t("CANCEL_REPLY", "❌ Отменить ответ"),
                callback_data="cancel_ticket_reply"
            )
        ]
    ])


# ==================== ADMIN TICKET KEYBOARDS ====================

def get_admin_tickets_keyboard(
    tickets: List[dict],
    current_page: int = 1,
    total_pages: int = 1,
    language: str = DEFAULT_LANGUAGE,
    scope: str = "all",
    *,
    back_callback: str = "admin_submenu_support",
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    rows: list[list[InlineKeyboardButton | tuple[str, str]]] = []

    open_rows, closed_rows = [], []
    for ticket in tickets:
        status_emoji = "✅" if ticket.get("is_closed", False) else ticket.get("status_emoji", "❓")
        user_name = ticket.get("user_name", "Unknown")[:15]
        username, telegram_id = ticket.get("username"), ticket.get("telegram_id")

        contact_parts = []
        if username:
            contact_parts.append(f"@{username}")
        if telegram_id:
            contact_parts.append(str(telegram_id))

        name_display = user_name
        if contact_parts:
            name_display += f" ({' | '.join(contact_parts)})"

        title = ticket.get("title", "Без названия")[:20]
        locked_emoji = ticket.get("locked_emoji", "")
        button_text = f"{status_emoji} #{ticket['id']} {locked_emoji} {name_display}: {title}".replace("  ", " ")

        row = [InlineKeyboardButton(text=button_text, callback_data=f"admin_view_ticket_{ticket['id']}")]
        (closed_rows if ticket.get("is_closed", False) else open_rows).append(row)

    # Переключатель scope
    rows.append([
        (texts.t("OPEN_TICKETS", "🔴 Открытые"), "admin_tickets_scope_open"),
        (texts.t("CLOSED_TICKETS", "🟢 Закрытые"), "admin_tickets_scope_closed"),
    ])

    if open_rows and scope in ("all", "open"):
        rows.append([(texts.t("OPEN_TICKETS_HEADER", "Открытые тикеты"), "noop")])
        rows.extend(open_rows)
    if closed_rows and scope in ("all", "closed"):
        rows.append([(texts.t("CLOSED_TICKETS_HEADER", "Закрытые тикеты"), "noop")])
        rows.extend(closed_rows)

    if total_pages > 1:
        nav_row: list[InlineKeyboardButton | tuple[str, str]] = []
        if current_page > 1:
            nav_row.append((texts.t("PAGINATION_PREV", "⬅️"), f"admin_tickets_page_{scope}_{current_page - 1}"))
        nav_row.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="current_page"))
        if current_page < total_pages:
            nav_row.append((texts.t("PAGINATION_NEXT", "➡️"), f"admin_tickets_page_{scope}_{current_page + 1}"))
        rows.append(nav_row)

    rows.append([(texts.BACK, back_callback)])
    return keyboard(*rows)


def get_admin_ticket_view_keyboard(
    ticket_id: int,
    is_closed: bool = False,
    language: str = DEFAULT_LANGUAGE,
    *,
    is_user_blocked: bool = False,
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    rows: list[list[tuple[str, str]]] = []

    if not is_closed:
        rows.append([(texts.t("REPLY_TO_TICKET", "💬 Ответить"), f"admin_reply_ticket_{ticket_id}")])
        rows.append([(texts.t("CLOSE_TICKET", "🔒 Закрыть тикет"), f"admin_close_ticket_{ticket_id}")])

    if is_user_blocked:
        rows.append([(texts.t("UNBLOCK", "✅ Разблокировать"), f"admin_unblock_user_ticket_{ticket_id}")])
    else:
        rows.append([
            (texts.t("BLOCK_FOREVER", "🚫 Заблокировать"), f"admin_block_user_perm_ticket_{ticket_id}"),
            (texts.t("BLOCK_BY_TIME", "⏳ Блок по времени"), f"admin_block_user_ticket_{ticket_id}"),
        ])

    rows.append([(texts.BACK, "admin_tickets")])
    return keyboard(*rows)


def get_admin_ticket_reply_cancel_keyboard(language: str = DEFAULT_LANGUAGE) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.t("CANCEL_REPLY", "❌ Отменить ответ"), "cancel_admin_ticket_reply")],
    )
