"""

Scan user reminders and send them according to their schedule

"""
from datetime import datetime, timedelta

import telebot

from shared_models import (
    TELE_TOKEN, URL, TABLE_USER_REMINDER, 
    TABLE_TMP_REMINDER_IN_PROGRESS, USER_ID, REMINDER_ID_EXPONENT_MIN,
    REMINDER_ID_EXPONENT_MAX, REMINDER_NAME, REMINDER_DAYS, REMINDER_FREQUENCY,
    REMINDER_AMOUNT, DEFAULT_REMINDER_ID, DEFAULT_NAME, DEFAULT_AMOUNT,
    DEFAULT_FREQUENCY, DEFAULT_DAYS, DEFAULT_START_TIME_EACH_DAY, 
    DEFAULT_END_TIME_EACH_DAY, DEFAULT_DELTA, DAYS_VOCAB, 
    UserReminder, ReminderMap)

# https://github.com/eternnoir/pyTelegramBotAPI/issues/161#issuecomment-343873014
bot = telebot.TeleBot(TELE_TOKEN, threaded=False)


def send_reminders() -> None:
    users = UserReminder.scan()
    for user in users:
        hour_in_user = (datetime.now() + timedelta(hours=user.time_delta)).hour
        user_reminders = []
        print(f'hour_in_user={hour_in_user}')
        for reminder in user.active_reminders:
            print(f'reminder.start_time_each_day={reminder.start_time_each_day}'
                f'reminder.end_time_each_day={reminder.end_time_each_day}')
            if (reminder.start_time_each_day <= hour_in_user and
                hour_in_user < reminder.end_time_each_day):
                user_reminders.append(f'You have a task called {reminder.name}\n'
                                      f'to repeat {reminder.amount} times.')
        message = "\n".join(user_reminders)
        bot.send_message(user.user_id, text=message)
        

def lambda_handler(event, context):
    send_reminders() 
