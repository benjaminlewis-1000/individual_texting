#! /usr/bin/python3

import googlevoice
import sys
import time
from googlevoice import Voice
from Tkinter import *
import re # For regular expressions

# For email
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import socket

socket.setdefaulttimeout(600)

# Credentials
username = 'provoysa97th@gmail.com'
password = 'communications'

# Pound defines, so to speak

ELDERS = 0
SISTERS = 1

FIRST = 0
LAST = 1
PHONE_NUM = 2
SELECTED = 3
GROUP = 4
SMS_NUM = 5
MMS_NUM = 6

NAMETAG = "<NAME> "
voice = Voice()

def sign_in():
	email = 'speedyswimmer1000@gmail.com'
	password = 'ylamrmtdwkqetxjw'

	voice.login(email, password)

win = Tk()
elders_var = BooleanVar()
sisters_var = BooleanVar()
contents = StringVar()

# Features: Sort by first or last name
# Select all elders or sisters, eq1, eq2, etc. 

f1 = open('ward_carriers.csv', 'r')

wardNames = []
a = [] # List of selected variables 

def sendMessage(message, number, sms_gateway):
	toaddr = number + sms_gateway
	server.sendmail('speedyswimmer1000@gmail.com', toaddr, message)

for line in f1:
	line = line.strip()
	line = line.rstrip(',')
	split_list = line.split(',')
	if len(split_list) != 7:
		print "Error! Please review the entry for " + split_list[0] + " " + split_list[1] + ". It has extra fields or is missing a field."
		continue
	# This next line should be fixed... 
	(first, last, number, gender, carrier, sms_num, mms_num) = split_list #line.split(',')
	#print last + "\n"
	selected = 0
	gender = gender.rstrip('\r\n')
	if gender == "m" or gender == "M":
		group = ELDERS
	else:
		group = SISTERS
	#print number + first + last
	data = [first, last, number.strip(), selected, group, sms_num, mms_num]
	wardNames.append(data)
	
# Sorting function	
wardNames = sorted(wardNames, key=lambda stuff: stuff[0])

listbox = Listbox(win, width=50, height=15, selectmode='multiple', exportselection=1)
#listbox.grid(row=0, column=0)
# yscroll = Scrollbar(command=listbox.yview, orient=VERTICAL)
# listbox.configure(yscrollcommand=yscroll.set)

T = Text(win, height = 8, width = 40)
T.pack()

for i in range(len(wardNames)):
    listbox.insert(END, wardNames[i][0] + " " + wardNames[i][1])

def get_list():
	a.append(map(int, listbox.curselection()))

def close_window(): 
  get_list()
  contents.set(T.get(1.0, END))
  win.destroy()
  
def set(var):
  var.set(1)
  
def clear_select():
  list_size = listbox.size()
  for x in range (0, list_size):
	listbox.select_clear(x)
	wardNames[x][SELECTED] = 0
	
def insert_name():
	T.insert(END, NAMETAG)
  
win.wm_title("Ward List")
frame = Frame(win)
frame.pack()

button = Button(frame)
button['text'] = "Send Text"
button['command'] = close_window
button.pack()

button = Button(frame)
button['text'] = "Clear List"
button['command'] = clear_select
button.pack()

ebutton = Checkbutton(frame)
ebutton['text'] ="Elders"
ebutton['command'] = lambda: set(elders_var)
ebutton.pack()

sbutton = Checkbutton(frame)
sbutton['text'] ="Sisters"
sbutton['command'] = lambda: set(sisters_var)
sbutton.pack()

nameButton = Button(frame)
nameButton["text"] = "Insert name here"
nameButton["command"] = insert_name
nameButton.pack()

test = IntVar()

listbox.pack()

win.mainloop()

selectedIndex = a[0]

contents = contents.get() # Contains the message

message = ""
	
def parseNames(name):
	test = re.sub("<NAME>", name, contents, count = 400) # Also a count of how many there are
	return test

server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username,password)

for x in range(len(selectedIndex)):
	wardNames[selectedIndex[x]][SELECTED] = 1
	#print message
	# Use a def here to send message to 'name', 'number'
	
for x in range(len(wardNames)):
	if wardNames[x][GROUP] == ELDERS:
		if elders_var.get() == 1:
			wardNames[x][SELECTED] = 1
	if wardNames[x][GROUP] == SISTERS:
		if sisters_var.get() == 1:
			wardNames[x][SELECTED] = 1
# This is where we iterate through the list and send the message to all who are selected
	if wardNames[x][SELECTED] == 1:
		#message = "This is a test for " + wardNames[x][FIRST] + " " + wardNames[x][LAST] + " at number " + wardNames[x][PHONE_NUM]
		#print message
		message = parseNames(wardNames[x][FIRST])
		message = message.rstrip('\n\r')
		number = wardNames[x][PHONE_NUM]
		sms_gateway = wardNames[x][SMS_NUM]
		mms_gateway = wardNames[x][MMS_NUM]
		print message
		sendMessage(message, number, sms_gateway)


# time.sleep(1)


# voice.send_sms(phoneNumber, message)
