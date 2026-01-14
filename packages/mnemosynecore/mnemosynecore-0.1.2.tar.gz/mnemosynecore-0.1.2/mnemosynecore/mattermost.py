import logging
from typing import Optional
from mattermostdriver import Driver

from mnemosynecore.vault import get_secret


def get_mattermost_driver(bot_id: str) -> Driver:
    """
    Создаёт и логинит Mattermost Driver через Vault.
    """
    cfg = get_secret(bot_id)

    driver = Driver({
        "url": cfg["host"],
        "token": cfg["password"],
        "scheme": cfg.get("scheme", "https"),
        "port": int(cfg.get("port", 443)),
        "basepath": cfg.get("basepath", "/api/v4"),
    })

    driver.login()
    return driver


def send_message(
    *,
    channel_id: str,
    bot_id: str,
    text: str,
    silent: bool = False,
) -> None:
    """
    Отправляет сообщение в Mattermost от имени бота.

    :param channel_id: ID канала
    :param bot_id: ID секрета в Vault (токен бота)
    :param text: Markdown-текст сообщения
    :param silent: не логировать успешную отправку
    """
    driver = get_mattermost_driver(bot_id)

    try:
        driver.posts.create_post(
            options={
                "channel_id": channel_id,
                "message": text.strip(),
            }
        )
        if not silent:
            logging.info("Сообщение отправлено в Mattermost: %s", channel_id)

    except Exception as exc:
        logging.exception(
            "Ошибка отправки сообщения в Mattermost (channel_id=%s)",
            channel_id
        )
        raise