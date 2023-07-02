import asyncio

from aiogram import Dispatcher, types
from aiogram.dispatcher import DEFAULT_RATE_LIMIT
from aiogram.dispatcher.handler import CancelHandler, current_handler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.utils.exceptions import Throttled


def rate_limit(limit: int, key=None):
    """
    Декоратор для настройки ограничения скорости и ключа в различных функциях.

    :param limit:
    :param key:
    :return:
    """

    def decorator(func):
        setattr(func, 'throttling_rate_limit', limit)
        if key:
            setattr(func, 'throttling_key', key)
        return func

    return decorator


class ThrottlingMiddleware(BaseMiddleware):
    """
    Simple middleware
    """

    def __init__(self, limit=DEFAULT_RATE_LIMIT, key_prefix='antiflood_'):
        self.rate_limit = limit
        self.prefix = key_prefix
        super(ThrottlingMiddleware, self).__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        """
        Этот обработчик вызывается, когда диспетчер получает сообщение

        :param message:
        """
        # Получить текущий обработчик
        handler = current_handler.get()

        # Получить диспетчера из контекста
        dispatcher = Dispatcher.get_current()
        # Если обработчик был настроен, получить ограничение скорости и ключ от обработчика
        if handler:
            limit = getattr(handler, 'throttling_rate_limit', self.rate_limit)
            key = getattr(handler, 'throttling_key',
                          f"{self.prefix}_{handler.__name__}")
        else:
            limit = self.rate_limit
            key = f"{self.prefix}_message"

        # Использовать Dispatcher.throttle method.
        try:
            await dispatcher.throttle(key, rate=limit)
        except Throttled as t:
            # Выполнить действие
            await self.message_throttled(message, t)

            # Отменить текущий обработчик
            raise CancelHandler()

    async def message_throttled(self, message: types.Message, throttled: Throttled):
        """
        Уведомлять пользователя только при первом превышении и уведомлять о разблокировке только при последнем превышении

        :param message:
        :param throttled:
        """
        handler = current_handler.get()
        dispatcher = Dispatcher.get_current()
        if handler:
            key = getattr(handler, 'throttling_key',
                          f"{self.prefix}_{handler.__name__}")
        else:
            key = f"{self.prefix}_message"

        # Подсчитайть, сколько времени осталось до конца блока
        delta = throttled.rate - throttled.delta

        # Предотвратить флуд
        if throttled.exceeded_count <= 2:
            await message.reply(f'Пожалуйста, подождите {int(delta)} секунды')

        # Sleep.
        await asyncio.sleep(delta)

        # Проверить состояние блокировки
        thr = await dispatcher.check_key(key)

        # Если текущее сообщение не последнее с текущим ключом - не отправлять сообщение
        if thr.exceeded_count == throttled.exceeded_count:
            await message.reply('Доступ получен 👀')