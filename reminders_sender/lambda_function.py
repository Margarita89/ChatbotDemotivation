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
    DEFAULT_END_TIME_EACH_DAY, DEFAULT_DELETED, DEFAULT_DELTA, DAYS_VOCAB, 
    UserReminder, ReminderMap)

# https://github.com/eternnoir/pyTelegramBotAPI/issues/161#issuecomment-343873014
bot = telebot.TeleBot(TELE_TOKEN, threaded=False)

CONVERT_WEEKS = {
    'Weekdays' : {0, 1, 2, 3, 4},
    'Weekends' : {5, 6},
    'Every day' : {0, 1, 2, 3, 4, 5, 6}
}


def if_alert(
    day2remind: str, start: int, end: int, freq: int, rest: int, is_deleted: bool, 
    hour_user: int, day_user: int) -> bool:
        if (start <= hour_user <= end and (hour_user - start) % freq == 0 and 
            rest > 0 and day_user in CONVERT_WEEKS[day2remind] and not is_deleted):
            return True
        return False


def send_reminders() -> None:
    users = UserReminder.scan()
    for user in users:
        hour_user = (datetime.now() + timedelta(hours=user.time_delta)).hour
        day_user = (datetime.now() + timedelta(hours=user.time_delta)).weekday()
        user_reminders = []
        print(f'hour_user={hour_user}')
        for reminder in user.active_reminders:
            print(f'is_deleted={reminder.is_deleted}')
            #print(f'reminder.start_time_each_day={reminder.start_time_each_day} '
            #    f'reminder.end_time_each_day={reminder.end_time_each_day} ')
            if if_alert(
                day2remind=reminder.days, hour_user=hour_user, day_user=day_user, 
                start=reminder.start_time_each_day, end=reminder.end_time_each_day,
                freq=reminder.frequency, rest=reminder.current_state, 
                is_deleted=reminder.is_deleted):
                    user_reminders.append(
                        f'You have a task called {reminder.name}\n'
                        f'to repeat {reminder.current_state} times.')
        message = "\n".join(user_reminders)
        print(f'message={message}')
        if message:
            bot.send_message(user.user_id, text=message)
        

def lambda_handler(event, context):
    send_reminders() 
