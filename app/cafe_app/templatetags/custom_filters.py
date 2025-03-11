import logging
import typing

from django import template

register = template.Library()

logger = logging.getLogger(__name__)


@register.filter
def index(sequence, position):
    try:
        position = int(position)
        logger.debug(sequence[position])
        return sequence[position]
    except (IndexError, TypeError) as exc:
        logger.error(exc)
        return None  # Или можно вернуть "", чтобы не было ошибок в шаблоне


@register.filter
def dict_key(d, key):
    try:
        return d.get(str(key)) or d.get(int(key))
    except (IndexError, TypeError) as exc:
        logger.error(exc)
        return None


@register.filter
def get_item_by_id(items_list, item_id):
    """Находит элемент списка по id."""
    return next(
        (item for item in items_list if str(item.get("id")) == str(item_id)),
        None,
    )
