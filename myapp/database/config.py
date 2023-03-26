from decouple import config

user = config("DB_USERNAME")
password = config("DB_PASSWORD")
db = "expense-tracker-test"
