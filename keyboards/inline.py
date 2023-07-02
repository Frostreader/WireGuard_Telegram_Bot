from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import selector as select


async def device_kb(user_id: int):
    """возвращает встроенную клавиатуру с различными вариантами выбора cfg"""
    kb = InlineKeyboardMarkup(row_width=2,)

    existing_devices = [item[0].split(
        '_')[-1] for item in select.all_user_configs(user_id=user_id)]

    if 'PC' not in existing_devices:
        kb.insert(InlineKeyboardButton(
            text='💻 ПК',
            callback_data='pc_config_create_request'))
    if 'PHONE' not in existing_devices:
        kb.insert(InlineKeyboardButton(
            text='📱 Смартфон',
            callback_data='phone_config_create_request'))

    kb.add(InlineKeyboardButton(
        text='❌Отмена❌', callback_data='cancel_config_creation'))

    return kb


async def cancel_payment_kb():
    """возвращает встроенную клавиатуру с кнопкой отмены оплаты"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(InlineKeyboardButton(
        text='❌Отмена❌', callback_data='cancel_payment'))
    return kb

if __name__ == '__main__':
    ...