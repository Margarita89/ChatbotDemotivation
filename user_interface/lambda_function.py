"""

Methods to interact with user

"""
import json
import re
import random
import traceback
from datetime import datetime, timedelta
from typing import Optional, Tuple

import telebot
from telebot import types

from shared_models import (
    TELE_TOKEN, REMINDER_ID_EXPONENT_MIN,
    REMINDER_ID_EXPONENT_MAX, DEFAULT_REMINDER_ID, DEFAULT_NAME, DEFAULT_AMOUNT,
    DEFAULT_FREQUENCY, DEFAULT_DAYS, DAYS_VOCAB,
    UserReminder, ReminderMap)

# https://github.com/eternnoir/pyTelegramBotAPI/issues/161#issuecomment-343873014
bot = telebot.TeleBot(TELE_TOKEN, threaded=False)
PARAMS_AMOUNT_IN_REMINDER_UPDATE = 2

# class ReminderMap(MapAttribute):
#    reminder_id = NumberAttribute(default=DEFAULT_REMINDER_ID)
#    name = UnicodeAttribute(default=DEFAULT_NAME)
#    amount = NumberAttribute(default=DEFAULT_AMOUNT)
#    frequency = NumberAttribute(default=DEFAULT_FREQUENCY)
#    days = UnicodeAttribute(default=DEFAULT_DAYS)
#    start_time_each_day = NumberAttribute(default=DEFAULT_START_TIME_EACH_DAY)
#    end_time_each_day = NumberAttribute(default=DEFAULT_END_TIME_EACH_DAY)
#    current_state = NumberAttribute(default=DEFAULT_AMOUNT)
#    is_deleted = BooleanAttribute(default=DEFAULT_DELETED)


# class UserReminder(Model):
#    class Meta:
#        table_name = TABLE_USER_REMINDER
#        region = 'us-east-2'
#    user_id = NumberAttribute(hash_key=True)
#    registration_time = NumberAttribute()
#    time_delta = NumberAttribute(default=DEFAULT_DELTA)
#    active_reminders = ListAttribute(default=list, of=ReminderMap)
#    passive_reminders = ListAttribute(default=list, of=ReminderMap)
#    temp_reminder = ReminderMap(default=ReminderMap)


def get_or_create_user_reminder(
        user_id: int, time: int) -> UserReminder:
    """Returns UserReminder object with data from existing element or
    creates a new one with specified user_id

    :param user_id: id of user of interest
    :param time: registration time for a new user, should be ignored for
        existing user
    :return: UserReminder object
    """
    try:
        print(f'U_ID: {user_id}')
        user_reminder = UserReminder.get(user_id)
    except UserReminder.DoesNotExist:
        user_reminder = UserReminder(
            user_id=user_id, registration_time=time)
        user_reminder.save()
    return user_reminder


def sign(x: float) -> int:
    return 1 if x >= 0 else -1


def int_from_str(value: str) -> Optional[int]:
    """Coverts to int or returns None instead"""
    try:
        return int(value)
    except ValueError:
        return None


def set_timezone(
        user_reminder: UserReminder,
        message_time: str,
        time_hour_str: str,
) -> None:
    """Calculates timezone from user entered time and inserts it into table

    :param user_reminder: UserReminder object for current user
    :param message_time: time in POSIX format
    :param time_hour_str: time entered by user
    :return: None
    """
    time_hour = int_from_str(time_hour_str)
    if not time_hour or not 0 <= time_hour <= 24:
        bot.send_message(
            user_reminder.user_id,
            text='Enter the hours between 0 and 24. '
                 'Please, use command:\n /set_timezone Hours')
        return
    dt_object = datetime.fromtimestamp(int(message_time))
    delta = time_hour - dt_object.hour
    if abs(delta) > 12:
        delta -= 24 * sign(delta)
        # save delta to user
    user_reminder.update(actions=[
        UserReminder.time_delta.set(delta)
    ])
    bot.send_message(
        user_reminder.user_id,
        text='Great! You can create your new reminder now!\n\n'
             'The reminder should have:\n- Name - give a meaningful name to '
             'help your motivation\n'
             '- Amount - how many times you want to exercise/repeat this task '
             'per day. For example, 50 push-ups\n'
             '- Frequency - how often you want to get reminded from 9 am until 21 pm\n'
             '- Days - which days you want to exerice/repeat your task\n\n'
             'Every day you can check how many exercises/repeats are left to do. '
             'We encourage you to send an update with a number of repeats you '
             'have done every day. So you can track how mush is left.\n\n'
             'Start by using command:\n "/create ReminderName"')


def create_new_reminder(user_reminder: UserReminder, name: str) -> None:
    """Sets name to new reminder, all rest values are set to default

    :param name: name of reminder
    :param user_reminder: UserReminder object for current user
    :return: None
    """
    if not name:
        bot.send_message(
            user_reminder.user_id,
            text='You have not entered the name. Please, use command '
                 '"/create ReminderName"')
        return
    for reminder in user_reminder.active_reminders:
        if reminder.name == name and not reminder.is_deleted:
            bot.send_message(
                user_reminder.user_id,
                text=f'There is already reminder called {name}. Please, choose '
                     'another name. Use command /create ReminderName')
            return
    user_reminder.update(actions=[
        UserReminder.temp_reminder.set(ReminderMap(
            reminder_id=DEFAULT_REMINDER_ID,
            name=name,
            amount=DEFAULT_AMOUNT,
            frequency=DEFAULT_FREQUENCY,
            days=DEFAULT_DAYS,
            current_state=DEFAULT_AMOUNT))
    ])
    bot.send_message(
        user_reminder.user_id,
        text=f'You started to create reminder called {name}. Choose '
             'number of times per day you want to repeat a task. '
             'Please, use command:\n "/set_amount Amount"')


def set_reminder_amount(user_reminder: UserReminder, number_str: str) -> None:
    """Sets reminder number in table temp_reminder

    :param number: amount of reminders per day
    :param user_reminder: UserReminder object for current user
    :return: None
    """
    user_id = user_reminder.user_id
    if user_reminder.temp_reminder.name == DEFAULT_NAME:
        bot.send_message(
            user_id,
            text='Please, start from command /create ReminderName')
        return

    amount = int_from_str(number_str)
    if not amount:
        bot.send_message(
            user_id, text=f'Input "{number_str}" is not a number. Please, use '
                          f'command:\n "/set_amount Amount"')
        return

    cur_temp_reminder = user_reminder.temp_reminder
    cur_temp_reminder.amount = amount
    cur_temp_reminder.current_state = amount
    user_reminder.update(actions=[
        UserReminder.temp_reminder.set(cur_temp_reminder)
    ])
    bot.send_message(
        user_id, text='Please, choose frequency of remineders per day. '
                      'Reminders will be sent between 9 am and 9 pm your time '
                      'with a frequency you will choose. For example, 1 means '
                      'every hour, 2 means every 2 hours and so on. '
                      'Please, use command:\n "/set_frequency Frequency"')


def set_reminder_frequency(
        user_reminder: UserReminder, frequency_str: str) -> None:
    """Sets reminder frequency in temp_reminder

    :param frequency_str: frequency of reminders per day
    :param user_reminder: UserReminder object for current user
    :return: None
    """
    user_id = user_reminder.user_id
    if user_reminder.temp_reminder.name == DEFAULT_NAME:
        bot.send_message(
            user_id,
            text='Please, start from command /create ReminderName')
        return

    frequency = int_from_str(frequency_str)
    if not frequency:
        bot.send_message(
            user_id, text=f'Input "{frequency}" is not a Number. Please, use '
                          f'command"\n "/set_frequency Frequency"')
        return

    cur_temp_reminder = user_reminder.temp_reminder
    cur_temp_reminder.frequency = int(frequency)
    user_reminder.update(actions=[
        UserReminder.temp_reminder.set(cur_temp_reminder)
    ])
    bot.send_message(
        user_id, text='Please, choose days to remind: \n/choose_days\n'
                      '"Weekdays" - press '
                      '1\n"Weekends" - press 2\n "Every day" - press 3\n')


def set_reminder_days(user_reminder: UserReminder, days_str: str) -> None:
    """Sets reminder days in table user_temp_reminder_data

    :param days_str: 1 from offered options for days, need to be converted using
     DAYS_VOCAB
    :param user_reminder: UserReminder object for current user
    :return: None
    """
    user_id = user_reminder.user_id
    if user_reminder.temp_reminder.name == DEFAULT_NAME:
        bot.send_message(
            user_id,
            text='Please, start from command /create ReminderName')
        return

    days = int_from_str(days_str)
    if not days:
        bot.send_message(
            user_id, text=f'Input ({days}) is not valid. Please, choose days to'
                          f' remind:\n /choose_days\n"Weekdays" - press 1\n'
                          f'"Weekends" - press 2\n "Every day" - press 3\n')
        return

    chosen_days = DAYS_VOCAB[int(days)]
    cur_temp_reminder = user_reminder.temp_reminder
    cur_temp_reminder.days = chosen_days
    user_reminder.update(actions=[
        UserReminder.temp_reminder.set(cur_temp_reminder)
    ])
    bot.send_message(
        user_id, text='Please, type "/done" to finish creating this reminder')


def move_reminder_temp2active(user_reminder: UserReminder) -> None:
    """transfer temporarily created reminder to main table 'user_data'

    :param user_reminder: UserReminder object for current user
    :return: None
    """
    user_id = user_reminder.user_id
    if user_reminder.temp_reminder.name == DEFAULT_NAME:
        bot.send_message(
            user_id,
            text='Please, start from command /create ReminderName')
        return
    user_reminder.temp_reminder.reminder_id = random.randint(
        10 ** REMINDER_ID_EXPONENT_MIN, 10 ** REMINDER_ID_EXPONENT_MAX)
    user_reminder.update(actions=[
        UserReminder.active_reminders.set(
            (UserReminder.active_reminders | []).append(
                [user_reminder.temp_reminder])
        )])
    bot.send_message(
        user_id,
        text=f'Reminder {user_reminder.temp_reminder.name}'
             f' was added successfully')
    user_reminder.temp_reminder.name = DEFAULT_NAME
    user_reminder.update(actions=[
        UserReminder.temp_reminder.set(user_reminder.temp_reminder)
    ])


def show_reminders(user_reminder: UserReminder) -> None:
    """Returns reminder if it exists"""
    user_id = user_reminder.user_id
    reminders = []
    for reminder in user_reminder.active_reminders:
        if not reminder.is_deleted:
            cur_data = (
                f'Reminder "{reminder.name}", {reminder.amount} to do per day. '
                f'Today remains {reminder.amount - reminder.current_state}.')
            reminders.append(cur_data)

    if not reminders:
        bot.send_message(user_id, text='Sorry, you have no reminders')

    message = "\n\n".join(reminders)
    bot.send_message(user_id, text=message)


def parse_update_args(update_str: str) -> Tuple[Optional[str], Optional[int]]:
    """Parses string with updates to the reminder. Expects 2 arguments:
    reminder_name and amount
    """
    user_update = update_str.split()
    if (
        len(user_update) != PARAMS_AMOUNT_IN_REMINDER_UPDATE or not
            user_update[1].isdigit()):
        return None, None
    return user_update[0], int(user_update[1])


def update_reminder(user_reminder: UserReminder, today_update: str) -> None:
    """Updates reminder if it exists"""
    reminder_to_update_name, value_to_update = parse_update_args(
        today_update)
    if not reminder_to_update_name:
        bot.send_message(
            user_reminder.user_id,
            text='Enter a number of exercises/updates you did. '
                 'Please, use command:\n /today_amount Name Amount')
        return
    for reminder in user_reminder.active_reminders:
        if reminder.name == reminder_to_update_name and not reminder.is_deleted:
            reminder.current_state -= value_to_update
            user_reminder.update(actions=[
                UserReminder.active_reminders.set(
                    user_reminder.active_reminders)
            ])
            bot.send_message(
                user_reminder.user_id,
                text=f'Great! You have only {reminder.current_state} left to '
                     f'do today')
            return
    bot.send_message(
        user_reminder.user_id,
        text=f'There is no reminder {reminder_to_update_name}. Please, use '
             f'command /show_reminders to show existing reminders.')


def cancel_reminder(user_reminder: UserReminder, name: str) -> None:
    for reminder in user_reminder.active_reminders:
        if reminder.name == name:
            reminder.is_deleted = True
            user_reminder.update(actions=[
                UserReminder.active_reminders.set(
                    user_reminder.active_reminders)
            ])
            bot.send_message(
                user_reminder.user_id,
                text=f'Reminder "{name}" was canceled')
            return
    bot.send_message(
        user_reminder.user_id,
        text=f'There is no reminder called "{name}". Please, use command '
             '/show_reminders to show existing reminders. And then use'
             ' command /cancel_reminder ReminderName')


def process_message(event):
    update = telebot.types.JsonDeserializable.check_json(event["body"])

    # PARSE
    message = update.get('message')
    chat = message.get('chat')
    user = message.get('from')

    def get_command_and_text(text):
        """split message into command and main text"""
        m = re.match('(/[^ @]*)([^ ]*)(.*)', text, re.DOTALL)
        if m:
            # group(3) is a bot name
            return m.group(1), m.group(3)
        else:
            return None, text

    command, main_text = get_command_and_text(message.get('text', ''))

    return {
        'main_text': main_text,
        'command': command,
        'chat': chat,
        'user': user
    }


def lambda_handler(event, context):
    chat_id = None
    try:
        # print(f'Event {event["body"]}')
        data = json.loads(event['body'])
        chat_id = data['message']['chat']['id']
        user_id = data['message']['from']['id']
        timestamp = data['message']['date']

        current_user = get_or_create_user_reminder(
            user_id=user_id, time=timestamp)

        parsed_data = process_message(event)
        command = parsed_data['command']
        value = parsed_data['main_text'].strip()

        if command == '/start':
            bot.send_message(
                chat_id,
                text='How much time in hours is it now? '
                     'We use it to set your timezone for reminders. '
                     'Please, use command:\n "/set_timezone Hours"')
        elif command == '/set_timezone':
            set_timezone(
                user_reminder=current_user,
                message_time=timestamp,
                time_hour_str=value)
        elif command == '/create':
            create_new_reminder(user_reminder=current_user, name=value)
            print('Create')
        elif command == '/set_amount':
            set_reminder_amount(user_reminder=current_user, number_str=value)
        elif command == '/set_frequency':
            set_reminder_frequency(
                user_reminder=current_user, frequency_str=value)
        elif command == '/choose_days':
            set_reminder_days(user_reminder=current_user, days_str=value)
        elif command == '/done':
            move_reminder_temp2active(user_reminder=current_user)
        elif command == '/show_reminders':
            show_reminders(user_reminder=current_user)
        elif command == '/today_amount':
            update_reminder(user_reminder=current_user, today_update=value)
        elif command == '/cancel_reminder':
            cancel_reminder(user_reminder=current_user, name=value)
        elif command:
            bot.send_message(current_user.user_id, text="Unknown command")
        print('Success!')
    except Exception as exc:
        print(
            f'Failed with exception: {exc}. Traceback: {traceback.format_exc()}')
        if chat_id:
            bot.send_message(chat_id, text='Something is wrong:(')
    return {
        'statusCode': 200
    }
