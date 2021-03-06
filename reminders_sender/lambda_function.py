"""

Scan user reminders and send them according to their schedule

"""
from datetime import datetime, timedelta

import telebot

from shared_models import (
    TELE_TOKEN, CONVERT_WEEKS, UserReminder, ReminderMap)

# https://github.com/eternnoir/pyTelegramBotAPI/issues/161#issuecomment-343873014
bot = telebot.TeleBot(TELE_TOKEN, threaded=False)


def if_alert(
    day2remind: str, 
    start: int, 
    end: int, 
    freq: int, 
    rest: int,
    is_deleted: bool, 
    hour_user: int, 
    day_user: int
) -> bool:
    is_inside_interval = start <= hour_user <= end
    # send reminder only on hours that have a zero remainder
    is_correct_remainder = (hour_user - start) % freq == 0
    is_correct_day = day_user in CONVERT_WEEKS[day2remind] 
    return (is_inside_interval and is_correct_remainder and rest > 0 and is_correct_day and not is_deleted)


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
            rest_amount = reminder.amount - reminder.current_state
            if if_alert(
                day2remind=reminder.days, hour_user=hour_user, day_user=day_user, 
                start=reminder.start_time_each_day, end=reminder.end_time_each_day,
                freq=reminder.frequency, rest=rest_amount, 
                is_deleted=reminder.is_deleted):
                    user_reminders.append(
                        f'You have a task called {reminder.name}\n'
                        f'to repeat {rest_amount} times.')
        message = "\n".join(user_reminders)
        print(f'message={message}')
        if message:
            bot.send_message(user.user_id, text=message)
        

def lambda_handler(event, context):
    send_reminders() 
