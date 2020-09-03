from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import pandas as pd
import requests
import time
import re
import csv

options = Options()
#options.add_argument('--headless') # browser doesn't open
options.add_argument('--disable-gpu')
driver = webdriver.Chrome(chrome_options=options, executable_path='C:/Python36/chromedriver.exe')
url = "https://web.cvent.com/event/84f26b13-25ef-458c-9d38-38432d71be09/websitePage:645d57e4-75eb-4769-b2c0-f201a0bfc6ce"
#response = requests.get(url)
#soup = BeautifulSoup(response.text, "html.parser")
#print(soup)

driver.get(url)
time.sleep(10)
page = driver.page_source
driver.quit()
soup = BeautifulSoup(page, 'html.parser')


# extract sessions for date passed in as param
# returns list of dictionaries (list of sessions for that day)
def extractSessions(date):
    session_cards = date.find_all('div', class_='AgendaStyles__sessionContainer___ECftY')
    sessions = [] # list of dictionaries that represent sessions
    #print("DATE: " + str(date) + '\n')
    for session in session_cards:
        session_attrs = dict()
        #name, time, description = ('',)*3
        start_time, end_time = ('',)*2
        name = session.find('div', attrs={'data-cvent-id':re.compile(r'^session.*name$')})
        if name is not None: name = name.text.strip()
        time = session.find('div', attrs={'data-cvent-id':re.compile(r'^session.*time$')})
        if time is not None:
            time = time.text.strip()
            print(time)
            times = time.split('-', 2)
            start_time = times[0]
            end_time = times[1][:-2]
        description = session.find('div', class_="AgendaStyles__sessionDescription___3dGx1")
        if description is not None: description = description.text.strip()
        session_attrs['Session Name'] = name
        session_attrs['Start Time'] = start_time
        session_attrs['End Time'] = end_time
        session_attrs['Description'] = description

        # extract speaker cards
        speaker_cards = session.find_all('div', class_='SessionsStyles__speakerCardContainer___33_zm')
        session_attrs['Speakers'] = extractSpeakers(speaker_cards)

        sessions.append(session_attrs)
        #print("SESSION: " + str(session_attrs) + '\n')

    return sessions

def extractSpeakers(speaker_cards):
    speakers_list = []
    for speaker in speaker_cards:
        #name, title, company = ('',)*3
        speaker_info = dict()
        name = speaker.find('div', attrs={'data-cvent-id': 'speakers-name'})
        if name is not None: name = name.text.strip()
        title = speaker.find('div', attrs={'data-cvent-id': 'speakers-title'})
        if title is not None: title = title.text.strip()
        company = speaker.find('div', attrs={'data-cvent-id': 'speakers-company'})
        if company is not None: company = company.text.strip()

        # assign to values in dictionary
        speaker_info['name'] = name
        speaker_info['title'] = title
        speaker_info['company'] = company

        # append to list of speakers
        speakers_list.append(speaker_info)

    return speakers_list


# extract html for each date
dates_html = soup.find_all('div', attrs={"data-cvent-id":re.compile(r'^sessions-list-.*2020$')})
print("LENGTH OF DATES")
print(len(dates_html))

# extract sessions html for each date:
schedule = dict()
d = 1
for date in dates_html:
    schedule["Day " + str(d)] = extractSessions(date)
    d+=1


# save sessions for each date into csv file
field_names = ['Session Name', 'Start Time', 'End Time', 'Description', 'Speakers']
x = 1
for date in schedule:
    print("DATE")
    print(date)
    with open('Day_' + str(x) + '_Schedule.csv', 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=field_names)
        writer.writeheader()
        for session in schedule[date]: # session is a dictionary
            print("SESSION IN DATE:")
            print(session)
            if not session['Speakers']: session['Speakers'] = ""
        writer.writerows(schedule[date])
    x+=1