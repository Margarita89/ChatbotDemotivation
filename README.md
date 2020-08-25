# [ChatbotDemotivation](https://t.me/De_motivationBot)

The bot is designed to collect, create, store and send reminders to do numbers of exercises or tasks on a regular basis. 
The reminders are sent with a chosen frequency on a chosen days. 
The user can send an update each time he/she finished some exercises/tasks. If there are some left, the reminder will be sent with the remaining amount.

The chatbot is developed using Python, AWS Lambda and makes use of the database DynamoDB. As the chatbot is created for Telegram Messenger service, the library pyTelegramBotAPI was also used.

The user creates reminder and specifies:
1. Name
1. Number of exercises/tasks per day
1. Frequency of reminders pers day
1. Days to receive reminders - every day, once a week, on weekdays or on weekends

The user can ask to show all existing reminders that belong to him.
The user can send an update on a chosen reminder with a number of exercises/tasks that are done.

Possible extentions:
1. Add keyboard with buttons. Currently the comands for the user are registered in Telegram for the chatbot and are shown as hints.
1. Introduce some motivation system like scores for doing all planned exercise/tasks on several days in a row.

Instructions to run the scripts. You will need:
1. Obtain a Token from Telegram BotFather and put it into layers/python/secrets.py file: 
  TELE_TOKEN='your_token'
1. Create a Chatbot with your own name
1. Register on AWS (free on certain conditions for 12 months)
1. Create 2 lambda-functions "de_motivation_bot_function" and "reminders_sender"
1. Create a layer SharedModels with description "Shared models and constants" and connect it to both lambda-functions
1. Install AWS CLI and set a role that allows to upload new files for lambda functions and layers
1. Run uploader_script.sh which will create zip files 
1. Set a trigger EventBridge (CloudWatch Events) for the lambda-function called "reminders_sender"

Here you are!

