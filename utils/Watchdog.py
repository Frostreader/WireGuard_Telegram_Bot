# ASYNC daemon который следит за пользователями, у которых есть дата окончания подписки, и отправляет им сообщение
# первый раз : за 2 дня до даты окончания
# второй раз: за 1 день до даты окончания
# ретий раз : дата окончания
# четвертый раз: через 1 день после даты окончания отправить kb бесплатно пользователю

from loguru import logger
from database.selector import get_user_ids_enddate_N_days
import keyboards as kb
from loader import bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loader import vpn_config


class Watchdog:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def run(self):
        """ start watchdog coroutine every day at 00:00 Moscow time"""
        self.scheduler.add_job(self.check_end_date, 'cron', hour=2, minute=0)
        # self.scheduler.add_job(self.check_end_date, 'interval', seconds=5)
        self.scheduler.start()
        logger.success(
            '[+] Watchdog coroutine created and started successfully')

    async def check_end_date(self):
        logger.info('[+] Checking for users with end date')
        notified_users = []
        user_ids = get_user_ids_enddate_N_days(-1)
        notified_users += user_ids
        for user_id in user_ids:
            await bot.send_message(user_id, 'Ваша подписка закончилась, но вы можете продлить ее =)',
                                   reply_markup=await kb.reply.free_user_kb(user_id=user_id))
            # отключить пользователя от vpn, закомментировав его конфиг внутри wg0.conf
            vpn_config.disconnect_peer(user_id)
            logger.warning(
                f'[+] user {user_id} notified about end date yesterday')

        user_ids = get_user_ids_enddate_N_days(0)
        for user_id in user_ids:
            if user_id not in notified_users:
                await bot.send_message(user_id, 'Сегодня заканчивается ваша подписка, не забудьте продлить ее =)',)
                notified_users.append(user_id)
                logger.warning(
                    f'[+] user {user_id} notified about end date today')

        user_ids = get_user_ids_enddate_N_days(1)
        for user_id in user_ids:
            if user_id not in notified_users:
                await bot.send_message(user_id, 'Ваша подписка заканчивается завтра, не забудьте продлить ее =)',)
                notified_users.append(user_id)
                logger.warning(
                    f'[+] user {user_id} notified about end date in 1 day')

        user_ids = get_user_ids_enddate_N_days(2)
        for user_id in user_ids:
            if user_id not in notified_users:
                await bot.send_message(user_id, 'Ваша подписка заканчивается через 2 дня, не забудьте продлить ее =)',)
                notified_users.append(user_id)
                logger.warning(
                    f'[+] user {user_id} notified about end date in 2 days')

        logger.info('Завершена проверка пользователей с датой окончания')

    def stop(self):
        self.scheduler.shutdown()