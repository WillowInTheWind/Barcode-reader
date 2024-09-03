import json
from dataclasses import dataclass
from time import sleep

import pynput
from termcolor import colored
import datetime
import os
print(colored(
    "Launching Barcode Reader - Do not press the p or enter keys or else something may break - press cntr C to stop the program",
    'green'))


@dataclass
class Student:
    name: str
    id: int
    grade: int
    checked_in: datetime.datetime


people = open("library_patrons.json")
people_and_ids = json.load(people)
ids = [names_and_grades[0] for names_and_grades in list(people_and_ids.values())]
grades = [names_and_grades[1] for names_and_grades in list(people_and_ids.values())]
names = list(people_and_ids.keys())
recording = False
key_presses = []
max_students_per_grade = 12
currently_entered_students = {12: {}, 11: {}, 10: {}, 9: {}}
url: str = os.environ.get("SUPABASE_URL")
db_key: str = os.environ.get("SUPABASE_KEY")



def on_press(key):
    global recording, key_presses
    try:
        if key == pynput.keyboard.Key.esc:
            return False
        if recording:
            if key == pynput.keyboard.Key.enter:
                id = "".join(key_presses)
                try:
                    person_index = ids.index(int(id))
                    now = datetime.datetime.now()
                    user = Student(names[person_index], ids[person_index], grades[person_index], now)
                    print(user)
                    if len(currently_entered_students[user.grade]) <= max_students_per_grade - 1:
                        currently_entered_students[user.grade].append(user)
                    else:
                        print(colored(
                            f"The {user.grade}th grade class has EXCEEDED the maximum {max_students_per_grade} students allowed",
                            'red'))
                    recording = False
                except ValueError:
                    recording = False
                key_presses = []
                id = ""
            else:
                key_presses.append(key.char)
    except AttributeError:
        # Handle special keys
        if recording:
            key_presses.append(f"<{key.name}>")


def on_release(key):
    global recording
    # Start recording when 'p' is pressed
    if key == pynput.keyboard.KeyCode.from_char('p'):
        recording = True

# Start the listener
with pynput.keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    for _ in range(60*60*24):
        time = datetime.datetime.now()
        for grade in currently_entered_students:
            for user in currently_entered_students[grade]:
                if (time -user.checked_in).total_seconds() > 45*60:
                    currently_entered_students[grade].remove(user)
        sleep(1)
        if not listener.running:
            break

#
# with pynput.keyboard.Listener(on_press=on_press()) as listener:
#     for _ in range(50):
#         print('still running...')
#         sleep(1)
#         if not listener.running:
#             break