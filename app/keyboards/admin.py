from typing import List, Optional, Tuple, Any, Iterable

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.localization.texts import get_texts
from shared import keyboard

DEFAULT_BROADCAST_BUTTONS = ("home",)

BROADCAST_BUTTONS = {
    "balance": {"text": "💰 Пополнить баланс", "callback": "balance_topup"},
    "referrals": {"text": "🤝 Партнерка", "callback": "menu_referrals"},
    "promocode": {"text": "🎫 Промокод", "callback": "menu_promocode"},
    "connect": {"text": "🔗 Подключиться", "callback": "subscription_connect"},
    "subscription": {"text": "📱 Подписка", "callback": "menu_subscription"},
    "support": {"text": "🛠️ Техподдержка", "callback": "menu_support"},
    "home": {"text": "🏠 На главную", "callback": "back_to_menu"},
}

BROADCAST_BUTTON_ROWS: tuple[tuple[str, ...], ...] = (
    ("balance", "referrals"),
    ("promocode", "connect"),
    ("subscription", "support"),
    ("home",),
)

BROADCAST_BUTTON_LABELS = {key: value["text"] for key, value in BROADCAST_BUTTONS.items()}


def _toggle_label(base_text: str, selected: bool) -> str:
    # Если текст вида "🟦 Текст", то меняем на "✅ Текст". Иначе просто добавляем префикс.
    if not selected:
        return base_text
    if " " in base_text:
        return f"✅ {base_text.split(' ', 1)[1]}"
    return f"✅ {base_text}"


def get_admin_main_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    texts = get_texts(language)

    return keyboard(
        [("👥 Юзеры/Подписки", "admin_submenu_users")],
        [("💰 Промокоды/Статистика", "admin_submenu_promo")],
        [("🛟 Поддержка", "admin_submenu_support")],
        [("📨 Сообщения", "admin_submenu_communications")],
        [("⚙️ Настройки", "admin_submenu_settings")],
        [("🛠️ Система", "admin_submenu_system")],
        [(texts.BACK, "back_to_menu")],
    )


def get_admin_users_submenu_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    texts = get_texts(language)

    return keyboard(
        [(texts.ADMIN_USERS, "admin_users"),
         (texts.ADMIN_REFERRALS, "admin_referrals")],
        [(texts.ADMIN_SUBSCRIPTIONS, "admin_subscriptions")],
        [("⬅️ Назад", "admin_panel")],
    )

def get_admin_promo_submenu_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    texts = get_texts(language)

    return keyboard(
        [(texts.ADMIN_PROMOCODES, "admin_promocodes"),
         (texts.ADMIN_STATISTICS, "admin_statistics")],
        [(texts.ADMIN_CAMPAIGNS, "admin_campaigns")],
        [(texts.ADMIN_PROMO_GROUPS, "admin_promo_groups")],
        [("⬅️ Назад", "admin_panel")],
    )

def get_admin_communications_submenu_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    texts = get_texts(language)

    return keyboard(
        [(texts.ADMIN_MESSAGES, "admin_messages")],
        [("👋 Приветственный текст", "welcome_text_panel"),
         ("📢 Сообщения в меню", "user_messages_panel")],
        [("⬅️ Назад", "admin_panel")],
    )

def get_admin_support_submenu_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("🎫 Тикеты поддержки", "admin_tickets")],
        [("🧾 Аудит модераторов", "admin_support_audit")],
        [("🛟 Настройки поддержки", "admin_support_settings")],
        [("⬅️ Назад", "admin_panel")],
    )

def get_admin_settings_submenu_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    texts = get_texts(language)

    return keyboard(
        [(texts.ADMIN_REMNAWAVE, "admin_remnawave"),
         (texts.ADMIN_MONITORING, "admin_monitoring")],
        [("🧩 Конфигурация бота", "admin_bot_config")],
        [(texts.t("ADMIN_MONITORING_SETTINGS", "⚙️ Настройки мониторинга"), "admin_mon_settings")],
        [(texts.ADMIN_RULES, "admin_rules"),
         ("🔧 Техработы", "maintenance_panel")],
        [("⬅️ Назад", "admin_panel")],
    )

def get_admin_system_submenu_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    texts = get_texts(language)

    return keyboard(
        [("📄 Обновления", "admin_updates"),
         ("🗄️ Бекапы", "backup_panel")],
        [("🧾 Логи", "admin_system_logs")],
        [(texts.t("ADMIN_REPORTS", "📊 Отчеты"), "admin_reports")],
        [("⬅️ Назад", "admin_panel")],
    )

def get_admin_reports_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("📆 За вчера", "admin_reports_daily")],
        [("🗓️ За неделю", "admin_reports_weekly")],
        [("📅 За месяц", "admin_reports_monthly")],
        [("⬅️ Назад", "admin_panel")],
    )

def get_admin_report_result_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    texts = get_texts(language)

    return keyboard(
        [(texts.t("REPORT_CLOSE", "❌ Закрыть"), "admin_close_report")],
    )

def get_admin_users_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("👥 Все пользователи", "admin_users_list"),
         ("🔍 Поиск", "admin_users_search")],
        [("📊 Статистика", "admin_users_stats"),
         ("🗑️ Неактивные", "admin_users_inactive")],
        [("⚙️ Фильтры", "admin_users_filters")],
        [("⬅️ Назад", "admin_submenu_users")],
    )

def get_admin_users_filters_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("💰 По балансу", "admin_users_balance_filter")],
        [("⬅️ Назад", "admin_users")],
    )

def get_admin_subscriptions_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("📱 Все подписки", "admin_subs_list"),
         ("⏰ Истекающие", "admin_subs_expiring")],
        [("⚙️ Настройки цен", "admin_subs_pricing"),
         ("🌍 Управление странами", "admin_subs_countries")],
        [("📊 Статистика", "admin_subs_stats")],
        [("⬅️ Назад", "admin_submenu_users")],
    )

def get_admin_promocodes_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("🎫 Все промокоды", "admin_promo_list"),
         ("➕ Создать", "admin_promo_create")],
        [("📊 Общая статистика", "admin_promo_general_stats")],
        [("⬅️ Назад", "admin_submenu_promo")],
    )

def get_admin_campaigns_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    texts = get_texts(language)

    return keyboard(
        [("📋 Список кампаний", "admin_campaigns_list"),
         ("➕ Создать", "admin_campaigns_create")],
        [("📊 Общая статистика", "admin_campaigns_stats")],
        [(texts.BACK, "admin_submenu_promo")],
    )

def get_campaign_management_keyboard(
    campaign_id: int, is_active: bool, language: str = "ru"
) -> InlineKeyboardMarkup:
    status_text = "🔴 Выключить" if is_active else "🟢 Включить"

    return keyboard(
        [
            ("📊 Статистика", f"admin_campaign_stats_{campaign_id}"),
            (status_text, f"admin_campaign_toggle_{campaign_id}"),
        ],
        [("✏️ Редактировать", f"admin_campaign_edit_{campaign_id}")],
        [("🗑️ Удалить", f"admin_campaign_delete_{campaign_id}")],
        [("⬅️ К списку", "admin_campaigns_list")],
    )

def get_campaign_edit_keyboard(
    campaign_id: int,
    *,
    is_balance_bonus: bool,
    language: str = "ru",
) -> InlineKeyboardMarkup:
    texts = get_texts(language)

    rows: list[list[tuple[str, str]]] = [
        [("✏️ Название", f"admin_campaign_edit_name_{campaign_id}"),
         ("🔗 Параметр", f"admin_campaign_edit_start_{campaign_id}")]
    ]

    if is_balance_bonus:
        rows.append([("💰 Бонус на баланс", f"admin_campaign_edit_balance_{campaign_id}")])
    else:
        rows += [
            [("📅 Длительность", f"admin_campaign_edit_sub_days_{campaign_id}"),
             ("🌐 Трафик", f"admin_campaign_edit_sub_traffic_{campaign_id}")],
            [("📱 Устройства", f"admin_campaign_edit_sub_devices_{campaign_id}"),
             ("🌍 Серверы", f"admin_campaign_edit_sub_servers_{campaign_id}")],
        ]

    rows.append([(texts.BACK, f"admin_campaign_manage_{campaign_id}")])

    return keyboard(*rows)

def get_campaign_bonus_type_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [("💰 Бонус на баланс", "campaign_bonus_balance"),
         ("📱 Подписка", "campaign_bonus_subscription")],
        [(texts.BACK, "admin_campaigns")],
    )


def get_promocode_management_keyboard(promo_id: int, language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("✏️ Редактировать", f"promo_edit_{promo_id}"),
         ("🔄 Статус", f"promo_toggle_{promo_id}")],
        [("📊 Статистика", f"promo_stats_{promo_id}"),
         ("🗑️ Удалить", f"promo_delete_{promo_id}")],
        [("⬅️ К списку", "admin_promo_list")],
    )


def get_admin_messages_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("📨 Всем пользователям", "admin_msg_all"),
         ("🎯 По подпискам", "admin_msg_by_sub")],
        [("🔍 По критериям", "admin_msg_custom"),
         ("📋 История", "admin_msg_history")],
        [("⬅️ Назад", "admin_submenu_communications")],
    )


def get_admin_monitoring_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("▶️ Запустить", "admin_mon_start"),
         ("⏸️ Остановить", "admin_mon_stop")],
        [("📊 Статус", "admin_mon_status"),
         ("📋 Логи", "admin_mon_logs")],
        [("⚙️ Настройки", "admin_mon_settings")],
        [("⬅️ Назад", "admin_submenu_settings")],
    )


def get_admin_remnawave_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("📊 Системная статистика", "admin_rw_system"),
         ("🖥️ Управление нодами", "admin_rw_nodes")],
        [("🔄 Синхронизация", "admin_rw_sync"),
         ("🌐 Управление сквадами", "admin_rw_squads")],
        [("📈 Трафик", "admin_rw_traffic")],
        [("⬅️ Назад", "admin_submenu_settings")],
    )


def get_admin_statistics_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("👥 Пользователи", "admin_stats_users"),
         ("📱 Подписки", "admin_stats_subs")],
        [("💰 Доходы", "admin_stats_revenue"),
         ("🤝 Партнерка", "admin_stats_referrals")],
        [("📊 Общая сводка", "admin_stats_summary")],
        [("⬅️ Назад", "admin_submenu_promo")],
    )

def get_user_management_keyboard(
    user_id: int,
    user_status: str,
    language: str = "ru",
    back_callback: str = "admin_users_list",
) -> InlineKeyboardMarkup:
    texts = get_texts(language)

    rows = [
        [("💰 Баланс", f"admin_user_balance_{user_id}"),
         ("📱 Подписка и настройки", f"admin_user_subscription_{user_id}")],
        [(texts.ADMIN_USER_PROMO_GROUP_BUTTON, f"admin_user_promo_group_{user_id}")],
        [("📊 Статистика", f"admin_user_statistics_{user_id}")],
        [("📋 Транзакции", f"admin_user_transactions_{user_id}")]
    ]

    if user_status == "active":
        rows.append([
            ("🚫 Заблокировать", f"admin_user_block_{user_id}"),
            ("🗑️ Удалить", f"admin_user_delete_{user_id}")
        ])
    elif user_status == "blocked":
        rows.append([
            ("✅ Разблокировать", f"admin_user_unblock_{user_id}"),
            ("🗑️ Удалить", f"admin_user_delete_{user_id}")
        ])
    elif user_status == "deleted":
        rows.append([
            ("❌ Пользователь удален", "noop")
        ])

    rows.append([("⬅️ Назад", back_callback)])

    return keyboard(*rows)

def get_user_promo_group_keyboard(
    promo_groups: List[Tuple[Any, int]],
    user_id: int,
    current_group_id: Optional[int],
    language: str = "ru"
) -> InlineKeyboardMarkup:
    texts = get_texts(language)

    rows: List[List[tuple[str, str]]] = []
    for group, members_count in promo_groups:
        prefix = "✅" if current_group_id is not None and group.id == current_group_id else "👥"
        count_text = f" ({members_count})" if members_count else ""
        rows.append([(f"{prefix} {group.name}{count_text}", f"admin_user_promo_group_set_{user_id}_{group.id}")])

    rows.append([(texts.ADMIN_USER_PROMO_GROUP_BACK, f"admin_user_manage_{user_id}")])
    return keyboard(*rows)

def get_confirmation_keyboard(
    confirm_action: str,
    cancel_action: str = "admin_panel",
    language: str = "ru"
) -> InlineKeyboardMarkup:
    texts = get_texts(language)
    return keyboard(
        [(texts.YES, confirm_action), (texts.NO, cancel_action)]
    )

def get_promocode_type_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("💰 Баланс", "promo_type_balance"), ("📅 Дни подписки", "promo_type_days")],
        [("🎁 Триал", "promo_type_trial")],
        [("⬅️ Назад", "admin_promocodes")],
    )

def get_promocode_list_keyboard(
    promocodes: list, page: int, total_pages: int, language: str = "ru"
) -> InlineKeyboardMarkup:
    rows: List[List[tuple[str, str]]] = []

    for promo in promocodes:
        status_emoji = "✅" if promo.is_active else "❌"
        type_emoji = {
            "balance": "💰",
            "subscription_days": "📅",
            "trial_subscription": "🎁",
        }.get(promo.type, "🎫")
        rows.append([(f"{status_emoji} {type_emoji} {promo.code}", f"promo_manage_{promo.id}")])

    if total_pages > 1:
        pagination_row: List[tuple[str, str]] = []
        if page > 1:
            pagination_row.append(("⬅️", f"admin_promo_list_page_{page - 1}"))
        pagination_row.append((f"{page}/{total_pages}", "current_page"))
        if page < total_pages:
            pagination_row.append(("➡️", f"admin_promo_list_page_{page + 1}"))
        rows.append(pagination_row)

    rows.append([("➕ Создать", "admin_promo_create")])
    rows.append([("⬅️ Назад", "admin_promocodes")])
    return keyboard(*rows)

def get_broadcast_target_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("👥 Всем", "broadcast_all"), ("📱 С подпиской", "broadcast_active")],
        [("🎁 Триал", "broadcast_trial"), ("❌ Без подписки", "broadcast_no_sub")],
        [("⏰ Истекающие", "broadcast_expiring"), ("🔚 Истекшие", "broadcast_expired")],
        [("🧊 Активна 0 ГБ", "broadcast_active_zero"), ("🥶 Триал 0 ГБ", "broadcast_trial_zero")],
        [("⬅️ Назад", "admin_messages")],
    )

def get_custom_criteria_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("📅 Сегодня", "criteria_today"), ("📅 За неделю", "criteria_week")],
        [("📅 За месяц", "criteria_month"), ("⚡ Активные сегодня", "criteria_active_today")],
        [("💤 Неактивные 7+ дней", "criteria_inactive_week"),
         ("💤 Неактивные 30+ дней", "criteria_inactive_month")],
        [("🤝 Через рефералов", "criteria_referrals"),
         ("🎫 Использовали промокоды", "criteria_promocodes")],
        [("🎯 Прямая регистрация", "criteria_direct")],
        [("⬅️ Назад", "admin_messages")],
    )

def get_broadcast_history_keyboard(page: int, total_pages: int, language: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[tuple[str, str] | InlineKeyboardButton]] = []

    if total_pages > 1:
        pagination_row: list[tuple[str, str] | InlineKeyboardButton] = []
        if page > 1:
            pagination_row.append(("⬅️", f"admin_msg_history_page_{page - 1}"))
        pagination_row.append((f"{page}/{total_pages}", "current_page"))  # no-op
        if page < total_pages:
            pagination_row.append(("➡️", f"admin_msg_history_page_{page + 1}"))
        rows.append(pagination_row)

    rows += [
        [("🔄 Обновить", "admin_msg_history")],
        [("⬅️ Назад", "admin_messages")],
    ]
    return keyboard(*rows)

def get_sync_options_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("🔄 Полная синхронизация", "sync_all_users")],
        [("🆕 Только новые", "sync_new_users")],
        [("📈 Обновить данные", "sync_update_data")],
        [("🔍 Валидация", "sync_validate"), ("🧹 Очистка", "sync_cleanup")],
        [("💡 Рекомендации", "sync_recommendations")],
        [("⬅️ Назад", "admin_remnawave")],
    )

def get_sync_confirmation_keyboard(sync_type: str, language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("✅ Подтвердить", f"confirm_{sync_type}")],
        [("❌ Отмена", "admin_rw_sync")],
    )

def get_sync_result_keyboard(sync_type: str, has_errors: bool = False, language: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[tuple[str, str]]] = []

    if has_errors:
        rows.append([("🔄 Повторить", f"sync_{sync_type}")])

    if sync_type != "all_users":
        rows.append([("🔄 Полная синхронизация", "sync_all_users")])

    rows += [
        [("📊 Статистика", "admin_rw_system"), ("🔍 Валидация", "sync_validate")],
        [("⬅️ К синхронизации", "admin_rw_sync")],
        [("🏠 В главное меню", "admin_remnawave")],
    ]
    return keyboard(*rows)

def get_period_selection_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("📅 Сегодня", "period_today"), ("📅 Вчера", "period_yesterday")],
        [("📅 Неделя", "period_week"), ("📅 Месяц", "period_month")],
        [("📅 Все время", "period_all")],
        [("⬅️ Назад", "admin_statistics")],
    )

def get_node_management_keyboard(node_uuid: str, language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("▶️ Включить", f"node_enable_{node_uuid}"),
         ("⏸️ Отключить", f"node_disable_{node_uuid}")],
        [("🔄 Перезагрузить", f"node_restart_{node_uuid}"),
         ("📊 Статистика", f"node_stats_{node_uuid}")],
        [("⬅️ Назад", "admin_rw_nodes")],
    )

def get_squad_management_keyboard(squad_uuid: str, language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("👥 Добавить всех пользователей", f"squad_add_users_{squad_uuid}")],
        [("❌ Удалить всех пользователей", f"squad_remove_users_{squad_uuid}")],
        [("✏️ Редактировать", f"squad_edit_{squad_uuid}"),
         ("🗑️ Удалить сквад", f"squad_delete_{squad_uuid}")],
        [("⬅️ Назад", "admin_rw_squads")],
    )

def get_squad_edit_keyboard(squad_uuid: str, language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("🔧 Изменить инбаунды", f"squad_edit_inbounds_{squad_uuid}")],
        [("✏️ Переименовать", f"squad_rename_{squad_uuid}")],
        [("⬅️ Назад к сквадам", f"admin_squad_manage_{squad_uuid}")],
    )

def get_monitoring_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("▶️ Запустить", "admin_mon_start"),
         ("⏹️ Остановить", "admin_mon_stop")],
        [("🔄 Принудительная проверка", "admin_mon_force_check"),
         ("📋 Логи", "admin_mon_logs")],
        [("🧪 Тест уведомлений", "admin_mon_test_notifications"),
         ("📊 Статистика", "admin_mon_statistics")],
        [("⬅️ Назад в админку", "admin_panel")],
    )

def get_monitoring_logs_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("🔄 Обновить", "admin_mon_logs"),
         ("🗑️ Очистить старые", "admin_mon_clear_logs")],
        [("⬅️ Назад", "admin_monitoring")],
    )

def get_monitoring_logs_navigation_keyboard(
    current_page: int,
    total_pages: int,
    has_logs: bool = True
) -> InlineKeyboardMarkup:
    rows: list[list[tuple[str, str]]] = []

    # пагинация
    if total_pages > 1:
        nav_row: list[tuple[str, str]] = []
        if current_page > 1:
            nav_row.append(("⬅️", f"admin_mon_logs_page_{current_page - 1}"))
        nav_row.append((f"{current_page}/{total_pages}", "current_page_info"))
        if current_page < total_pages:
            nav_row.append(("➡️", f"admin_mon_logs_page_{current_page + 1}"))
        rows.append(nav_row)

    # управление логами
    if has_logs:
        rows.append([
            ("🔄 Обновить", "admin_mon_logs"),
            ("🗑️ Очистить", "admin_mon_clear_logs"),
        ])
    else:
        rows.append([
            ("🔄 Обновить", "admin_mon_logs"),
        ])

    # возврат
    rows.append([
        ("⬅️ Назад к мониторингу", "admin_monitoring"),
    ])

    return keyboard(*rows)

def get_log_detail_keyboard(log_id: int, current_page: int = 1) -> InlineKeyboardMarkup:
    return keyboard(
        [("🗑️ Удалить этот лог", f"admin_mon_delete_log_{log_id}")],
        [("⬅️ К списку логов", f"admin_mon_logs_page_{current_page}")],
    )

def get_monitoring_clear_confirm_keyboard() -> InlineKeyboardMarkup:
    return keyboard(
        [("✅ Да, очистить", "admin_mon_clear_logs_confirm"),
         ("❌ Отмена", "admin_mon_logs")],
        [("🗑️ Очистить ВСЕ логи", "admin_mon_clear_all_logs")],
    )

def get_monitoring_status_keyboard(is_running: bool, last_check_ago_minutes: int = 0) -> InlineKeyboardMarkup:
    rows: list[list[tuple[str, str]]] = []

    # старт/стоп
    if is_running:
        rows.append([("⏹️ Остановить", "admin_mon_stop"),
                     ("🔄 Перезапустить", "admin_mon_restart")])
    else:
        rows.append([("▶️ Запустить", "admin_mon_start")])

    # проверка
    if not is_running or last_check_ago_minutes > 10:
        rows.append([("⚡ Срочная проверка", "admin_mon_force_check")])
    else:
        rows.append([("🔄 Проверить сейчас", "admin_mon_force_check")])

    rows.append([("📋 Логи", "admin_mon_logs"),
                 ("📊 Статистика", "admin_mon_statistics")])
    rows.append([("🧪 Тест уведомлений", "admin_mon_test_notifications")])
    rows.append([("⬅️ Назад", "admin_submenu_settings")])

    return keyboard(*rows)

def get_monitoring_settings_keyboard() -> InlineKeyboardMarkup:
    return keyboard(
        [("⏱️ Интервал проверки", "admin_mon_set_interval"),
         ("🔔 Уведомления", "admin_mon_toggle_notifications")],
        [("💳 Настройки автооплаты", "admin_mon_autopay_settings"),
         ("🧹 Автоочистка логов", "admin_mon_auto_cleanup")],
        [("⬅️ К мониторингу", "admin_monitoring")],
    )

def get_log_type_filter_keyboard() -> InlineKeyboardMarkup:
    return keyboard(
        [("✅ Успешные", "admin_mon_logs_filter_success"),
         ("❌ Ошибки", "admin_mon_logs_filter_error")],
        [("🔄 Циклы мониторинга", "admin_mon_logs_filter_cycle"),
         ("💳 Автооплаты", "admin_mon_logs_filter_autopay")],
        [("📋 Все логи", "admin_mon_logs"),
         ("⬅️ Назад", "admin_monitoring")],
    )

def get_admin_servers_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("📋 Список серверов", "admin_servers_list"),
         ("🔄 Синхронизация", "admin_servers_sync")],
        [("➕ Добавить сервер", "admin_servers_add"),
         ("📊 Статистика", "admin_servers_stats")],
        [("⬅️ Назад", "admin_subscriptions")],
    )

def get_server_edit_keyboard(server_id: int, is_available: bool, language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("✏️ Название", f"admin_server_edit_name_{server_id}"),
         ("💰 Цена", f"admin_server_edit_price_{server_id}")],
        [("🌍 Страна", f"admin_server_edit_country_{server_id}"),
         ("👥 Лимит", f"admin_server_edit_limit_{server_id}")],
        [("📝 Описание", f"admin_server_edit_desc_{server_id}")],
        [("❌ Отключить" if is_available else "✅ Включить",
          f"admin_server_toggle_{server_id}")],
        [("🗑️ Удалить", f"admin_server_delete_{server_id}"),
         ("⬅️ Назад", "admin_servers_list")],
    )

def get_admin_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str,
    back_callback: str = "admin_panel",
    language: str = "ru"
) -> InlineKeyboardMarkup:
    rows: list[list[tuple[str, str]]] = []

    if total_pages > 1:
        row: list[tuple[str, str]] = []

        if current_page > 1:
            row.append(("⬅️", f"{callback_prefix}_page_{current_page - 1}"))

        row.append((f"{current_page}/{total_pages}", "current_page"))  # no-op

        if current_page < total_pages:
            row.append(("➡️", f"{callback_prefix}_page_{current_page + 1}"))

        rows.append(row)

    rows.append([("⬅️ Назад", back_callback)])

    return keyboard(*rows)

def get_maintenance_keyboard(
    language: str,
    is_maintenance_active: bool,
    is_monitoring_active: bool,
    panel_has_issues: bool = False
) -> InlineKeyboardMarkup:

    maintenance_button = "🟢 Выключить техработы" if is_maintenance_active else "🔧 Включить техработы"
    monitoring_button = "⏹️ Остановить мониторинг" if is_monitoring_active else "▶️ Запустить мониторинг"

    return keyboard(
        [(maintenance_button, "maintenance_toggle")],
        [(monitoring_button, "maintenance_monitoring")],
        [
            ("🔍 Проверить API", "maintenance_check_api"),
            (f"🌐 Статус панели{'⚠️' if panel_has_issues else ''}", "maintenance_check_panel"),
        ],
        [("📢 Отправить уведомление", "maintenance_manual_notify")],
        [
            ("🔄 Обновить", "maintenance_panel"),
            ("⬅️ Назад", "admin_submenu_settings"),
        ],
    )

def get_sync_simplified_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("🔄 Полная синхронизация", "sync_all_users")],
        [("⬅️ Назад", "admin_remnawave")],
    )

def get_welcome_text_keyboard(language: str = "ru", is_enabled: bool = True) -> InlineKeyboardMarkup:
    toggle_text = "🔴 Отключить" if is_enabled else "🟢 Включить"

    return keyboard(
        [(toggle_text, "toggle_welcome_text")],
        [("📝 Изменить текст", "edit_welcome_text"),
         ("👁️ Показать текущий", "show_welcome_text")],
        [("👁️ Предпросмотр", "preview_welcome_text"),
         ("🔄 Сбросить", "reset_welcome_text")],
        [("🏷️ HTML форматирование", "show_formatting_help"),
         ("💡 Плейсхолдеры", "show_placeholders_help")],
        [("⬅️ Назад", "admin_submenu_communications")],
    )

def get_broadcast_media_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("📷 Добавить фото", "add_media_photo"),
         ("🎥 Добавить видео", "add_media_video")],
        [("📄 Добавить документ", "add_media_document"),
         ("⏭️ Пропустить медиа", "skip_media")],
        [("❌ Отмена", "admin_messages")],
    )


def get_media_confirm_keyboard(language: str = "ru") -> InlineKeyboardMarkup:
    return keyboard(
        [("✅ Использовать это медиа", "confirm_media"),
         ("🔄 Заменить медиа", "replace_media")],
        [("⏭️ Без медиа", "skip_media"),
         ("❌ Отмена", "admin_messages")],
    )


def get_updated_message_buttons_selector_keyboard_with_media(
    selected_buttons: Iterable[str] | None,
    has_media: bool = False,
    language: str = "ru",
) -> InlineKeyboardMarkup:
    selected = set(selected_buttons or [])
    rows: list[list[tuple[str, str]]] = []

    for row_keys in BROADCAST_BUTTON_ROWS:
        row: list[tuple[str, str]] = []
        for key in row_keys:
            cfg = BROADCAST_BUTTONS[key]
            text = _toggle_label(cfg["text"], key in selected)
            row.append((text, f"btn_{key}"))
        if row:
            rows.append(row)

    if has_media:
        rows.append([("🖼️ Изменить медиа", "change_media")])

    rows += [
        [("✅ Продолжить", "buttons_confirm")],
        [("❌ Отмена", "admin_messages")],
    ]

    return keyboard(*rows)
