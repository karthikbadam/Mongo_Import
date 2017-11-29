import pandas as pd
import json, pymongo
from datetime import datetime
from titlecase import titlecase

EMPTY_DATUM = "None"

# read data from file
crimes = pd.read_csv('input/crime-baltimore.csv')
crimes_json = json.loads(crimes.to_json(orient='records'))


def validate(date, pattern):
    try:
        return datetime.strptime(date, pattern)
    except ValueError:
        return

def title_case(line):
    return titlecase(line)


# put in mongoDB
mongo_client = pymongo.MongoClient()
mongo_collection = mongo_client.crime.baltimore
mongo_collection.drop()  # throw out what's there
for crime in crimes_json:

    for key in crime.keys():
        if crime[key] == "" or crime[key] is None:
            crime[key] = "None"
        elif isinstance(crime[key], unicode):
            crime[key] = title_case(crime[key])

    crime["CrimeDate"] = datetime.strptime(crime["CrimeDate"], "%m/%d/%y")
    crime["Month"] = datetime.strftime(crime["CrimeDate"], "%B")
    if not validate(crime["CrimeTime"], "%H:%M:%S"):
        if not validate(crime["CrimeTime"], "%H"):
            if not validate(crime["CrimeTime"], "%H%M"):
                crime["CrimeTime"] = datetime.strptime("12:00:00", "%H:%M:%S")
            else:
                crime["CrimeTime"] = datetime.strptime(crime["CrimeTime"], "%H%M")
        else:
            crime["CrimeTime"] = datetime.strptime(crime["CrimeTime"], "%H")
    else:
        crime["CrimeTime"] = datetime.strptime(crime["CrimeTime"], "%H:%M:%S")

    mongo_collection.insert_one(crime)


# create index by specific columns
mongo_collection.create_index('Description')
mongo_collection.create_index('Weapon')
mongo_collection.create_index('CrimeDate')
mongo_collection.create_index('CrimeTime')


# close connection
mongo_client.close()