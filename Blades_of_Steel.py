"""
This is a program that scrapes Dave's hockey site for his team's
games and organizes the data in a list of tuples.  The data from
the lists are then used to create google calendar events.

Can access indexes of tuples using list[i][i] - ie. 
div_11_records[1][0]

"""
from __future__ import print_function
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import datetime
import requests
import hashlib
from googleapiclient.errors import HttpError
import json

#Global Constants
calID = 'primary'

def initiateGoogleCalendar():
	global SCOPES
	SCOPES = 'https://www.googleapis.com/auth/calendar'
	global store
	store = file.Storage('token.json')
	global creds
	creds = store.get()
	global flow
	if not creds or creds.invalid:
	    flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
	    creds = tools.run_flow(flow, store)
	global GCAL
	GCAL = discovery.build('calendar', 'v3', http=creds.authorize(Http()))
	global GMT_OFF
	GMT_OFF = '-04:00'      # EST/GMT-4

def createEvent(title,location,starting_time,ending_time,colour):
	eventIDStr = calID+title+starting_time+ending_time
	eventID = hashlib.md5(eventIDStr.encode('utf-8')).hexdigest()
	print("event ID = %s" %(eventID))

	EVENT = {
		'colorId': colour,
		'id':eventID,
    	'summary': title,
    	'location': location,
    	'start':  {'dateTime': starting_time + GMT_OFF},
    	'end':    {'dateTime': ending_time + GMT_OFF}
	}

	print(json.dumps(EVENT, indent=2))
	#print("event json = %s" %(EVENT))

	try:
		e = GCAL.events().insert(calendarId='primary',
   	    	sendNotifications=True, body=EVENT).execute()
	except HttpError as err:
		e = GCAL.events().update(calendarId='primary', eventId=eventID,
        	sendNotifications=True, body=EVENT).execute()

	print('''*** %r event added:
    	Start: %s
    	End:   %s
    	ID: %s''' % (e['summary'].encode('utf-8'),
        			e['start']['dateTime'], e['end']['dateTime'],e['id']))


initiateGoogleCalendar()
r1 = requests.get('https://ottawatravellers.ca/Win18/upcoming-games/Div11/')
r2 = requests.get('https://ottawatravellers.ca/Win18/upcoming-games/Div13/')

from bs4 import BeautifulSoup
#parsing for division 11 teams
soup1 = BeautifulSoup(r1.text, 'html.parser')
results1 = soup1.find_all('tr')

#parsing for division 13
soup2 = BeautifulSoup(r2.text, 'html.parser')
results2 = soup2.find_all('tr')

#The New Jerseys
div_11_records = []
for result in results1:
	if 'The New Jerseys' in result.contents[7] or 'The New Jerseys' in result.contents[9]:
		date = result.contents[1].text.split('\xa0')
		date = " ".join(date)
		date = datetime.datetime.strptime(date, "%A %b %d, %y").strftime("%Y-%m-%d")
		time = result.contents[3].text
		end_time = datetime.datetime.strptime(time, "%I:%M %p").strftime("%H%M%S")
		end_time = int(end_time) + 10000
		end_time = str(end_time)
		time = datetime.datetime.strptime(time, "%I:%M %p").strftime("%H:%M:%S")
		end_time = datetime.datetime.strptime(end_time, "%H%M%S").strftime("%H:%M:%S")
		date_time = []
		date_time.extend([date, time])	
		date_time = "T".join(date_time)
		end_date_time = []
		end_date_time.extend([date, end_time])	
		end_date_time = "T".join(end_date_time)
		event_location = result.contents[5].text
		event_name = result.contents[7].text + " vs " + result.contents[9].text
		game_type = result.contents[11].text
		colour = '5'
		createEvent(event_name,event_location,date_time,end_date_time,colour)

#The Pile-Ons	
div_13_records = []
for result in results2:
	if 'Pile-Ons' in result.contents[7] or 'Pile-Ons' in result.contents[9]:
		date = result.contents[1].text.split('\xa0')
		date = " ".join(date)
		date = datetime.datetime.strptime(date, "%A %b %d, %y").strftime("%Y-%m-%d")
		time = result.contents[3].text
		end_time = datetime.datetime.strptime(time, "%I:%M %p").strftime("%H%M%S")
		end_time = int(end_time) + 10000
		end_time = str(end_time)		
		time = datetime.datetime.strptime(time, "%I:%M %p").strftime("%H:%M:%S")
		end_time = datetime.datetime.strptime(end_time, "%H%M%S").strftime("%H:%M:%S")
		date_time = []
		date_time.extend([date, time])
		date_time = "T".join(date_time)		
		end_date_time = []
		end_date_time.extend([date, end_time])	
		end_date_time = "T".join(end_date_time)		
		event_location = result.contents[5].text
		event_name = result.contents[7].text + " vs " + result.contents[9].text
		game_type = result.contents[11].text
		colour = '9'
		createEvent(event_name,event_location,date_time,end_date_time,colour)