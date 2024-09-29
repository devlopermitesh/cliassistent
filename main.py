import json
from cerberus import Validator
from datetime import datetime
import requests
import os
import xml.etree.ElementTree as ET
import random

class NoEscapeEncoder(json.JSONEncoder):
    def encode(self, obj):
        return super().encode(obj).encode('utf-8').decode('unicode_escape')
def getlocation():
    try:
        url = "https://ipinfo.io/json"
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        data = response.json()
        return data['city'], data['region'], data['country']
    except requests.RequestException as e:
        print(f"Error fetching location: {e}")
        return "Unknown City", "Unknown State", "Unknown Country"
    
# //fetching language by user location
def getlanguages():
 city,state,country =getlocation()
 try:
    response=requests.get(f"https://restcountries.com/v3.1/alpha/{country}")
    data=response.json()
    return data[0]['languages']
 except:
    return []
 



# Define schema for user data validation
schema = {
    'name': {'type': 'string', 'minlength': 1, 'maxlength': 50},
    'email': {'type': 'string', 'regex': r'^[^@]+@[^@]+\.[^@]+$'},
    'username': {'type': 'string', 'minlength': 1, 'maxlength': 20},
    'date_of_birth': {'type': 'string', 'regex': r'^\d{4}-\d{2}-\d{2}$'},
    'gender': {'type': 'string', 'allowed': ['male', 'female', 'other']},
    'country': {'type': 'string', 'minlength': 1, 'maxlength': 50},
    'state': {'type': 'string', 'minlength': 1, 'maxlength': 50},
    'city': {'type': 'string', 'minlength': 1, 'maxlength': 50},
    'password': {'type': 'string', 'minlength': 6},
    'likenews': {'type': 'string', 'allowed': ['yes', 'no']},
    'langauge': {'type': 'string', 'allowed':list(getlanguages().keys())},
    'news_time': {'type': 'string', 'regex':r'^(0?[1-9]|1[0-2]):([0-5][0-9])(\s(AM|PM))?$'},
    'fav_news_channel': {'type': 'string', 'allowed': ['aaj tak', 'zee news', 'hindustan times', 'ndtv', 'bbc', 'cnn']},
    'haveHabits': {'type': 'string', 'allowed': ['yes', 'no']},
    
}

v = Validator(schema)

def load_user_data():
    try:
        with open("userData.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_user_data(data):
    with open("userData.json", "w") as f:
        json.dump(data, f, indent=4, cls=NoEscapeEncoder)

def validate_input(validator,field, value):
      # Validate the input
    is_valid = validator.validate({field: value})
    
    # If validation fails, print errors
    if not is_valid:
        print(f"Invalid input for {field}. Allowed values are: {validator.schema[field].get('allowed', 'No specific values allowed')}")
        for error in validator.errors.get(field, []):
            print(f" - {field}: {error}")
    
    return is_valid

def validate_date_of_birth(date_of_birth):
    try:
        birth_date = datetime.strptime(date_of_birth, '%Y-%m-%d')
    except ValueError:
        return False

    today = datetime.now()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age >= 8

def create_account(mode):
    if mode =="user":
        userdata = {
            'task': [],
            'habit': [],
        }
        while True:
            userdata['city'], userdata['state'], userdata['country'] = getlocation()
            
            for field in schema.keys():
                # answer = userdata[field] if field == 'city' or field=='state' or field=='country' else ''
                print(field)
                answer = lambda field:{'news_time':datetime.now().strftime("%I:%M %p"),'city':userdata['city'],'state':userdata['state'],'country':userdata['country'] }[field] if field == 'news_time' or field=='city' or field=='state'or field=='country' else ''
                while True:
                    value = input(f"What is your {field.replace('_', ' ')}: {answer(field)} ").strip().lower()
                    if field == 'city' or field=='state' or field=='country' or field == 'news_time':
                        if field == 'news_time':
                            value=answer(field)
                        else:
                         value = userdata[field]  
                        
                    if field == 'date_of_birth':
                        if validate_date_of_birth(value):
                            userdata[field] = value
                            break
                        else:
                            print("Invalid date of birth. Must be in the format YYYY-MM-DD and at least 8 years old.")
                    elif validate_input(v,field, value):
                        userdata[field] = value
                        break
                    else:
                        allowed_values = schema[field].get('allowed', 'No specific values allowed')
                        print(f"Invalid input for {field}. Allowed values are: {allowed_values}")
                        for field, errors in v.errors.items():
                            for error in errors:
                                print(f" - {field}: {error}")

            existing_users = load_user_data()
            existing_users.append(userdata)
            save_user_data(existing_users)
            print("Account created successfully!")
            break
    elif mode == "guest":
        userdata = {
             'task': [],
            'habit': {

                'goodhabit': [],
                'badhabit': [],

            },
        }
        print("Hi, Guest!")
        name=input("Enter your name:")
        if len(name) == 0:
            name = "Guest"
        userdata['name']=name
        while True:
            userdata['city'], userdata['state'], userdata['country'] = getlocation()
            existing_users = load_user_data()
            existing_users.append(userdata)
            save_user_data(existing_users)
            print("guest created successfully!")
            break
1
 

# schema for tasks 
taskshema={
    'taskname':{'type': 'string', 'minlength': 1, 'maxlength': 50},
    'description':{'type': 'string', 'minlength': 1, 'maxlength': 250},
    'date':{'type': 'string', 'regex': r'^\d{4}-\d{2}-\d{2}$'},
    'time':{'type': 'string', 'regex': r'^\d{2}:\d{2}$'},
    'completed':{'type': 'string', 'allowed': ['yes', 'no']},
    

}

v2=Validator(taskshema)


def time_remaining(target_date_str, target_time_str):
    if len(target_time_str) == 5:  # Format is HH:MM
        target_time_str += ":00"  # Add seconds

    target_datetime_str = f"{target_date_str} {target_time_str}"
    target_datetime = datetime.strptime(target_datetime_str, "%Y-%m-%d %H:%M:%S")

    current_datetime = datetime.now()
    time_difference = target_datetime - current_datetime

    if time_difference.total_seconds() < 0:
        return "The specified time has already passed."

    days, remainder = divmod(time_difference.total_seconds(), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)

    return f" {int(days)} days, {int(hours)} hours, {int(minutes)} minutes, and {int(seconds)} seconds."

#show task to function 
def show_tasks(data):
    if not data:
        print("Something went wrong")
    else:
        tasks=data[0]['task']
        print("*"*40)
        if not tasks:
            print("No tasks found")
        else:
            
         for task in tasks:
            if task is not None:
                print(f"task id : {task['taskId']}")
                print(f"task name : {task['taskname']}")
                print(f"description : {task['description']}")
                print(f"date : {task['date']}")
                print(f"time : {task['time']}")
                print(f"completed : {task['completed']}")
                print(f"time remaining : {time_remaining(task['date'],task['time'])}")
            else:
                print("No tasks found")
        print("*"*40)
        
    
def add_tasks(data):
    if not data:
        print("Something went wrong")
    else:
        todate=datetime.now().strftime("%Y-%m-%d")
        time=datetime.now().strftime("%H:%M")
        task_data={
            'taskId': len(data[0]['task'])+1,
        }
        while True:
            for field in taskshema.keys():
                print(field)
                answer=lambda field:{'date':todate,'time':time}[field] if field == 'date' or field=='time' else ''
                while True:
                    value = input(f"What is your task {field.replace('_', ' ')}: {answer(field)} ").strip().lower()
                    if field == 'date' or field == 'time':
                        value=answer(field)
                    if validate_input(v2,field, value):
                        print(v2)
                        print(field)
                        print(value)
                        task_data[field] = value
                        break
                    else:
                        allowed_values = taskshema[field].get('allowed', 'No specific values allowed')
                        print(f"Invalid input for {field}. Allowed values are: {allowed_values} ")
                        for field, errors in v.errors.items():
                            for error in errors:
                                print(f" - {field}: {error}")


            data[0]['task'].append(task_data)
            save_user_data(data)
            break


def delete_task(data):
    if not data:
        print("Something went wrong")
    else:
        tasks=data[0]['task']
        
        show_tasks(data)
        taskid=int(input("Enter task id to delete :"))
        if 0 < taskid <= len(tasks):
            del tasks[taskid-1]
            save_user_data(data)
            print("task deleted successfully")
        else:
            print("Invalid task id")
    
def update_task(data):
    if not data:
        print("Something went wrong")
    else:
        tasks=data[0]['task']
        show_tasks(data)
        taskid=int(input("Enter task id to update :"))
        for field in taskshema.keys():
            answer=lambda field:{'name':tasks[taskid-1]['taskname'],'description':tasks[taskid-1]['description'],'date':tasks[taskid-1]['date'],'time':tasks[taskid-1]['time'],'time':tasks[taskid-1]['time'],'completed':tasks[taskid-1]['completed']}[field] if field == 'name' or field=='description' else ''
            while True:
                value = input(f"What is your task {field.replace('_', ' ')}: ").strip().lower()
                if validate_input(v2,field, value):
                    tasks[taskid-1][field]=value
                    save_user_data(data)
                    break
                else:
                    allowed_values = taskshema[field].get('allowed', 'No specific values allowed')
                    print(f"Invalid input for {field}. Allowed values are: {allowed_values} ")

#habit schema here
habitschema={

    "name":{'type':"string", "minlength":1, "maxlength":50},
    "description":{'type':"string", "minlength":1, "maxlength":50},
    "timemost":{'type':"string", "regex":r'^\d{2}:\d{2}$'},
    "typehabit":{'type':"string", "allowed":['badhabit','goodhabit']},
    "status":{'type':"string", "allowed":['low','medium','high']},
    "motivation":{'type':"string", "minlength":1, "maxlength":50},
    "frequency":{'type':"string", "allowed":['everyday','everyweek','everymonth']},
    "day":{'type':"string", "allowed":['monday','tuesday','wednesday','thursday','friday','saturday','sunday']},
    "start_date": {'type': "string", "regex": r'^\d{4}-\d{2}-\d{2}$'},
    "progress": {'type': "string", "allowed": ['not started', 'in progress', 'completed']},

}

v3=Validator(habitschema)


def show_habits(data):
    if not data:
        print("Something went wrong")
    else:
        habits=data[0]['habit']
        print("*"*40)
        if not habits:
            print("No habits found")
        else:
            habits=data[0]['habit']
            print("*"*40)

            print("Habits:")
            for habit in habits:
                print(f"Name : {habit['name']}")
                print(f"Description : {habit['description']}")
                print(f"Time Most : {habit['timemost']}")
                print(f"Type Habit : {habit['typehabit']}")
                print(f"Status : {habit['status']}")
                print(f"Motivation : {habit['motivation']}")
                print(f"Frequency : {habit['frequency']}")
                print(f"Day : {habit['day']}")
                print(f"Start Date : {habit['start_date']}")
                print(f"Progress : {habit['progress']}")
            print("*"*40)
            
                
        
def getquestion(field,answer=''):
    default=f"default:{answer}" if len(answer)>0 and answer is not None and answer else ''
    if field == 'name':
        return f"What is your habit name ?{default} "
    elif field == 'description':
        return f"What is your habit description ?{default} "
    elif field == 'timemost':
        return f"What is your time most ?{default} "
    elif field == 'typehabit':
        return f"What is your type habit ? {default}"
    elif field == 'status':
        return f"What is your status ? {default}"
    elif field == 'motivation':
        return f"What is your motivation ? {default}"
    elif field == 'frequency':
        return f"What is your frequency ? {default}"
    elif field == 'day':
        return f"What is your day when you are most active toward your habits? ? {default}"
    elif field == 'progress':
        return f"What is your progress ? {default}"
    else:
        return f"What is your habit  ? {default}"
    

def add_habit(data):
    habit_data={
        'habitId':len(data[0]['habit'])+1
    }
    if not data:
        print("Something went wrong")
    else:
        day=datetime.now().strftime("%A").lower()
        time=datetime.now().strftime("%H:%M")
        todate=datetime.now().strftime("%Y-%m-%d")
        while True:
            for field in habitschema.keys():
                # get question 
                answer=lambda field:{'day':day,'time':time,'start_date':todate}[field] if field == 'day' or field=='time' or field=='start_date' else ''
                question =getquestion(field,answer=answer(field))
                while True:
                    value = input(f"{question} ").strip().lower()
                    if validate_input(v3,field, value):
                        habit_data[field]=value
                        break
                    else:
                        allowed_values = habitschema[field].get('allowed', 'No specific values allowed')
                        print(f"Invalid input for {field}. Allowed values are: {allowed_values} ")

            
            data[0]['habit'].append(habit_data)
            save_user_data(data)
            print("Habit added successfully! i am tracking...")
            break

    
def delete_habit(data):
    if not data:
        print("Something went wrong")
    else:
        habit=data[0]['habit']
        show_habits(data)
        habitid=int(input("Enter habit id to delete :"))
        if 0<habitid<=len(habit):
            habit.pop(habitid-1)
            save_user_data(data)
            print("Habit deleted successfully")
        else:
            print("Invalid habit id")

def update_habit(data):
    if not data:
        print("Something went wrong")
    else:
        pass

def readAajtak():
    try:
        url="https://www.aajtak.in/rssfeeds/news-sitemap.xml"
        response=requests.get(url)
        root=ET.fromstring(response.content)
        articles=[]
        for url in root.findall('{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
            loc=url.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc').text
            title=url.find('.//{http://www.google.com/schemas/sitemap-news/0.9}title').text
            articles.append({'title':title,'link':loc})
            if articles:
                while True:
                    random_article=random.choice(articles)
                    print("Title:",random_article['title'])
                    print("Link:",random_article['link'])
                    next=input("Do you want to read next article(yes/no):").strip().lower()
                    if next=='yes':
                        continue
                    elif next=='no':
                        break
                    else:
                        continue
                

            else:
                print("No articles found")
                
                
                
    except Exception as e:
        print(f"An error occurred: {e}")


def hear_news(data):
    if not data:
        print("Something went wrong")
    else:
        newchannel=data[0]['fav_news_channel']
        match newchannel:
            case "aaj tak":
                readAajtak(3)
                pass
            case "zee news":
                pass
            case "hindustan times":
                pass
            case "ndtv":
                pass
            case "bbc":
                pass
            case "cnn":
                pass
            case _:
                print("invalid news channel")
                

        
    
        



def deletefile():
    current_directory=os.getcwd()
    file_path=os.path.join(current_directory,'userData.json')
    try:
        os.remove(file_path)
        print(f"your accound is  deleted successfully.")
    except FileNotFoundError:
        print(f"you account is not found.")
    except PermissionError:
        print(f"you do not have permission to log out")
    except Exception as e:
        print(f"An error occurred: {e}")
def logout(user_data):
    if not user_data:
        print("Something went wrong")
    else:
        while True:
            askagain=input("are you sure you want to log out?(yes/no)").strip().lower() 
            if askagain =='no':
                print("ohh! you just afaird me!!hiuu..")
                return 
            elif askagain=='yes':
                deletefile()
                break
            
            else:
                continue
            




def main():
    user_data = load_user_data()
    while True:
        print("Hi, Assistant here!")
        if not user_data:
            print("Oh wow, new user? Most welcome!")
            user_type = input("Do you want to create an account or guest? (create/guest): ").strip().lower()
            if user_type == "create":
                create_account("user")
                user_data = load_user_data()  # Reload user data after creating an account
            elif user_type == "guest":
                create_account("guest")
            else:
                print("Invalid input, please try again.")
        
        else:
            print("Welcome back!")
            print("What would you like to do today?")
            print("1. Show tasks")
            print("2. Add tasks")
            print("3. Delete task")
            print("4. update task")
            print("5. Add habit")
            print("6. Delete habit")
            print("7. Update habit")
            print("8. hear news")
            print("9. Logout")
            choice=input("Enter your choice :").strip().lower()
            match choice:
                case "1":
                    show_tasks(user_data)
                case "2":
                    add_tasks(user_data)
                    pass
                case "3":
                    delete_task(user_data)
                    pass
                case "4":
                    update_task(user_data)
                    pass
                case "5":
                    add_habit(user_data)
                    pass
                case "6":
                    delete_habit(user_data)
                    pass
                case "7":
                    update_habit(user_data)
                    pass
                case "8":
                    hear_news(user_data)
                    pass
                case "9":
                    logout(user_data)
                    break
                case _:
                    print("Invalid input, please try again.")

                
            break

if __name__ == "__main__":
    main()
