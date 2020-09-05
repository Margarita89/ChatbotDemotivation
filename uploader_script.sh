rm user_interface/user_interface.zip 
zip -r user_interface/user_interface.zip user_interface/
rm reminders_sender/reminders_sender.zip 
zip -r reminders_sender/reminders_sender.zip reminders_sender/
rm layers/python_libs.zip
pip3 install -r requirements.txt -t layers/python/
rm -r layers/python/botocore/
rm -r layers/python/botocore-1.17.*
zip -r layers/python_libs.zip layers/python
# zip -r layers/python_libs.zip layers/
# aws lambda update-function-code --function-name  de_motivation_bot_function --zip-file fileb://user_interface/user_interface.zip
# aws lambda update-function-code --function-name  de_motivation_bot_function --zip-file fileb://reminders_sender/reminders_sender.zip
# aws lambda publish-layer-version --layer-name SharedModels --description "Shared models and constants" --zip-file fileb://layers/python_libs.zip --compatible-runtimes python3.8 