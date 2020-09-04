
from quickstart import get_calendar_service
from datetime import datetime

calendar_id = 'h4lg1vbb4egs3ssrbhqut2ngao@group.calendar.google.com'
def createGoogleCalEvents(event_dict, date):
    service = get_calendar_service()
    start_date = date + ' ' + event_dict['Start Time']
    dt_start = datetime.strptime(start_date, '%m/%d/%y %I:%M %p')

    end_date = date + ' ' + event_dict['End Time']
    dt_end = datetime.strptime(end_date, '%m/%d/%y %I:%M %p')
    descrip = ''
    if event_dict['Description'] is not None: descrip += event_dict['Description']
    if len(event_dict['Speakers']) > 0: descrip += '\nSpeakers: ' + str(event_dict['Speakers'])
    event = {
        'summary': event_dict['Session Name'],
        'description': descrip,
        'start': {
            'dateTime': dt_start.isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': dt_end.isoformat(),
            'timeZone': 'America/Los_Angeles',
        },
    }

    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))