#! /usr/bin/python3

# Imports
import googlevoice # For the edge cases where the carrier doesn't have an sms portal. 
import sys # System commands
import time # Time commands
from googlevoice import Voice
from Tkinter import * # For GUI elements
import re # For regular expressions

# For email
import smtplib  # Library for email
from email.MIMEMultipart import MIMEMultipart # For working with the subject line and stuff, eventually.
from email.MIMEText import MIMEText
import socket # For setting the timeout on the socket.

socket.setdefaulttimeout(600)

# Credentials, to a general account or, alternatively, an app-specific password. 
username = 'provoysa97th@gmail.com'
password = 'communications'

# Pound defines, so to speak
ELDERS = 0  # Group definitions
SISTERS = 1

FIRST = 0 # Definitions of the fields that I put into the array that holds all members' informations. 
LAST = 1
PHONE_NUM = 2
SELECTED = 3
GROUP = 4
SMS_NUM = 5
MMS_NUM = 6

NAMETAG = "<NAME>" # For inserting personalized names. This is parsed in parseNames.
voice = Voice() # Open an instance of Google Voice. 

def sign_in(): # To google voice. 
	email = 'speedyswimmer1000@gmail.com'
	password = 'ylamrmtdwkqetxjw'

	voice.login(email, password)

# TODO features: Sort by first or last name
# Select all elders or sisters, eq1, eq2, etc. 

f1 = open('ward_carriers.csv', 'r')

wardNames = []
selected_list = [] # List of selected variables 

# Go through the csv file and split into the parts. Strips the end newlines and commas, then parse into list.
# Format for the csv file, each line: first, last, number, gender, carrier, carrier_sms_gateway (e.g. @tmomail.net), carrier_mms_gateway (for mms)
for line in f1:
	line = line.strip()
	line = line.rstrip(',')
	split_list = line.split(',')
	if len(split_list) != 7:
		# Error handling, such as it is. 
		print "Error! Please review the entry for " + split_list[0] + " " + split_list[1] + ". It has extra fields or is missing a field."
		continue
	# Assign the split line into appropriate variables 
	(first, last, number, gender, carrier, sms_num, mms_num) = split_list 
	#print last + "\n"
	selected = 0  # Default not selected to send a text message to. 
	# The selected field eventually determines whether the text is sent or not.
	gender = gender.rstrip('\r\n')
	if gender == "m" or gender == "M":
		group = ELDERS
	else:
		group = SISTERS
	#print number + first + last
	data = [first, last, number.strip(), selected, group, sms_num, mms_num]
	wardNames.append(data) # Put the data into an array of arrays.
	
# Sorting function	
wardNames = sorted(wardNames, key=lambda stuff: stuff[0]) # Some kind of sorting function...

################ GUI ###############################################

# A couple of special variables. Normal variables can't be set with the TKinter package, so this is how we get the 
# variables from checkboxes and text fields out. 
win = Tk() # New window 
elders_var = BooleanVar()
sisters_var = BooleanVar()
# The elders_ and sisters_var variables are booleans to send to all elders and/or sisters. 
# These don't cause double-messaging. They simply set whether the 'selected' field of the 
# wardnames entry for that person is set non-zero; if that entry was already non-zero or is 
# set so later, that's not any sort of a problem.
contents = StringVar()

# Create a GUI list which has everyone's name.
listbox = Listbox(win, width=50, height=15, selectmode='multiple', exportselection=1)
#listbox.grid(row=0, column=0)
# yscroll = Scrollbar(command=listbox.yview, orient=VERTICAL)
# listbox.configure(yscrollcommand=yscroll.set)

T = Text(win, height = 8, width = 40)  # Initialize the text box.
T.pack()

for i in range(len(wardNames)): # Put everyone's name in the list, first and last name.  
    listbox.insert(END, wardNames[i][FIRST] + " " + wardNames[i][LAST])

### End GUI creation. 	
	
###### Function defs for general GUI function. ##### 

# Called on window close, linked to the "Send Text" button.
def close_window(): 
  get_list() 
  contents.set(T.get(1.0, END))  # Get all the text from the text box and put it in the 'contents' StringVar.
  win.destroy() # Destroy the window, end the loop, get on with the program.
  
def get_list(): # Get the list of all selected entries and put them in selected_list.
	selected_list.append(map(int, listbox.curselection()))

def set(var): # Set a variable. 
  var.set(1)
  
def clear_select(): # Does *not* unset the 'elders' and 'sisters' tags. 
  list_size = listbox.size()
  for x in range (0, list_size):
	listbox.select_clear(x)
	wardNames[x][SELECTED] = 0
	
def insert_name():  # Insert the text '<NAME>' in the string at the cursor location. 
	T.insert(INSERT, NAMETAG)
 
# GUI Title
win.wm_title("Ward List")
frame = Frame(win)
frame.pack()

# Push button which closes the window, sends the texts. 
button = Button(frame)
button['text'] = "Send Text"
button['command'] = close_window
button.pack()

# Clear all selections in the list.
button = Button(frame)
button['text'] = "Clear List"
button['command'] = clear_select
button.pack()

# Checkbuttons - send to all elders and/or all sisters 
ebutton = Checkbutton(frame)
ebutton['text'] ="Elders"
ebutton['command'] = lambda: set(elders_var)
ebutton.pack()

sbutton = Checkbutton(frame)
sbutton['text'] ="Sisters"
sbutton['command'] = lambda: set(sisters_var)
sbutton.pack()

# Check button that will insert the <NAME> tag in the message. 
nameButton = Button(frame)
nameButton["text"] = "Insert name here"
nameButton["command"] = insert_name
nameButton.pack()

#test = IntVar()

# Pack the box and start the GUI running. This function causes the GUI to loop until it's exited.
# It is critical to do the mainloop in front of other functionality. 
listbox.pack()
win.mainloop()

################# END GUI ###################################

selectedIndex = selected_list[0]
print selectedIndex

contents = contents.get() # Contains the message

def sendMessage(message, number, sms_gateway):
	toaddr = number + sms_gateway
	server.sendmail('speedyswimmer1000@gmail.com', toaddr, message)
	
def parseNames(name):
	test = re.sub("<NAME>", name, contents, count = 400) # Also a count of how many there are
	return test

server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username,password)

for x in range(len(selectedIndex)):
	wardNames[selectedIndex[x]][SELECTED] = 1
	
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
