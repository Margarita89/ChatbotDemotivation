from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, NumberAttribute, BooleanAttribute, UnicodeSetAttribute,
    UTCDateTimeAttribute, ListAttribute, MapAttribute)

from secrets import TELE_TOKEN
URL = "https://api.telegram.org/bot{}/".format(TELE_TOKEN)
	
# table_names
TABLE_USER_REMINDER = 'user_reminder_data'
TABLE_TMP_REMINDER_IN_PROGRESS = 'user_temp_reminder_data'

USER_ID = 'user_id'

REMINDER_ID_EXPONENT_MIN = 10
REMINDER_ID_EXPONENT_MAX = 20
REMINDER_NAME = 'reminder_name'
REMINDER_DAYS = 'reminder_days'
REMINDER_FREQUENCY = 'reminder_frequency'
REMINDER_AMOUNT = 'reminder_amount'

DEFAULT_REMINDER_ID = 1
DEFAULT_NAME = "DefaultReminder"
DEFAULT_AMOUNT = 50
DEFAULT_FREQUENCY = 10
DEFAULT_DAYS = 'Weekdays'
DEFAULT_START_TIME_EACH_DAY = 9
DEFAULT_END_TIME_EACH_DAY = 21
DEFAULT_DELTA = 0
DAYS_VOCAB = {
      1: 'Weekdays', 
      2: 'Weekends', 
      3: 'Every day', 
      4: 'Once a week'}
    
class ReminderMap(MapAttribute):
    reminder_id = NumberAttribute(default=DEFAULT_REMINDER_ID)
    name = UnicodeAttribute(default=DEFAULT_NAME)
    amount = NumberAttribute(default=DEFAULT_AMOUNT)
    frequency = NumberAttribute(default=DEFAULT_FREQUENCY)
    days = UnicodeAttribute(default=DEFAULT_DAYS)
    start_time_each_day = NumberAttribute(default=DEFAULT_START_TIME_EACH_DAY)
    end_time_each_day = NumberAttribute(default=DEFAULT_END_TIME_EACH_DAY)
    current_state = NumberAttribute(default=DEFAULT_AMOUNT)
    is_deleted = BooleanAttribute(default=False)


class UserReminder(Model):
    class Meta:
        table_name = TABLE_USER_REMINDER
        region = 'us-east-2'
    user_id = NumberAttribute(hash_key=True)
    registration_time = NumberAttribute()
    time_delta = NumberAttribute(default=DEFAULT_DELTA)
    active_reminders = ListAttribute(default=list, of=ReminderMap)
    passive_reminders = ListAttribute(default=list, of=ReminderMap)
    temp_reminder = ReminderMap(default=ReminderMap)