import logging

log = logging.getLogger(__name__)

DEFAULT_MODE = "general"
DEFAULT_SUBMODE = "standard"

MODE_KEY = "ollama_mode"
SUBMODE_KEY = "ollama_submode"


def get_ollama_mode(context):
    """
    Получить текущий режим Ollama для пользователя (user_data).
    Возвращает (mode, submode).
    """
    mode = context.user_data.get(MODE_KEY, DEFAULT_MODE)
    submode = context.user_data.get(SUBMODE_KEY, DEFAULT_SUBMODE)
    return mode, submode


def set_ollama_mode(context, mode, submode=None):
    """
    Установить режим Ollama для пользователя (user_data).
    Если submode не указан — не менять подрежим.
    """
    prev_mode = context.user_data.get(MODE_KEY, DEFAULT_MODE)
    prev_submode = context.user_data.get(SUBMODE_KEY, DEFAULT_SUBMODE)
    context.user_data[MODE_KEY] = mode
    if submode is not None:
        context.user_data[SUBMODE_KEY] = submode
        log.info(f"Смена режима Ollama: {prev_mode}/{prev_submode} -> {mode}/{submode}")
    else:
        log.info(f"Смена режима Ollama: {prev_mode} -> {mode}")


def get_ollama_submode(context):
    """
    Получить текущий подрежим Ollama для пользователя.
    """
    return context.user_data.get(SUBMODE_KEY, DEFAULT_SUBMODE)


def set_ollama_submode(context, submode):
    """
    Установить подрежим Ollama для пользователя.
    """
    prev_submode = context.user_data.get(SUBMODE_KEY, DEFAULT_SUBMODE)
    context.user_data[SUBMODE_KEY] = submode
    log.info(f"Смена подрежима Ollama: {prev_submode} -> {submode}")


def get_mode_button_text(mode):
    """
    Вернуть текст кнопки режима для главного меню.
    """
    if mode == "couple":
        return "Режим: Пара 👩‍❤️‍👨"
    elif mode == "general":
        return "Режим: Ассистент 🤖"
    else:
        return f"Режим: {mode}" 