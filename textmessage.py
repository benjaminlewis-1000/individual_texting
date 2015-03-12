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

namesListFrame = Frame(win)
buttonFrame = Frame(win)

messageLabel = Label(namesListFrame, text="List of recipients - \nhighlight name to send text")
messageLabel.pack()

scrollbar = Scrollbar(namesListFrame)
scrollbar.pack(side = RIGHT, fill=Y)

listbox = Listbox(namesListFrame, width=50, height=15, selectmode='multiple', exportselection=1, yscrollcommand = scrollbar.set)
scrollbar.config(command=listbox.yview)

messageLabel = Label(buttonFrame, text="Write text message here!")
messageLabel.pack()
T = Text(buttonFrame, height = 8, width = 40)  # Initialize the text box.
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

pushFrame = Frame(buttonFrame)
checkFrame = Frame(buttonFrame)

messageLabel = Label(checkFrame, text="Check to select all \nelders and/or sisters:")
messageLabel.pack()

# Check button that will insert the <NAME> tag in the message. 
nameButton = Button(pushFrame, bg="cyan")
nameButton["text"] = "Insert name at cursor"
nameButton["command"] = insert_name
nameButton.pack()

# Push button which closes the window, sends the texts. 
button = Button(pushFrame, bg="red")
button['text'] = "Send Text"
button['command'] = close_window
button.pack()

# Clear all selections in the list.
button = Button(pushFrame, bg="green")
button['text'] = "Clear List"
button['command'] = clear_select
button.pack()

# Checkbuttons - send to all elders and/or all sisters 
ebutton = Checkbutton(checkFrame)
ebutton['text'] ="Elders"
ebutton['command'] = lambda: set(elders_var)
ebutton.pack()

sbutton = Checkbutton(checkFrame)
sbutton['text'] ="Sisters"
sbutton['command'] = lambda: set(sisters_var)
sbutton.pack()

#test = IntVar()

pushFrame.pack(side=LEFT, expand=YES)
checkFrame.pack(side=LEFT, expand=YES)

buttonFrame.pack(side=LEFT, fill=Y)
namesListFrame.pack(side=BOTTOM, fill=Y)

# Pack the box and start the GUI running. This function causes the GUI to loop until it's exited.
# It is critical to do the mainloop in front of other functionality. 
listbox.pack()
win.mainloop()

################# END GUI ###################################

selectedIndex = selected_list[0] # Unsure, but it seems to be working.
print selectedIndex

contents = contents.get() # Contains the message

if not contents:
	print "Blank message"

def sendMessage(message, number, sms_gateway):
	toaddr = number + sms_gateway # Concatenate the number and the sms gateway.
	if sms_gateway.lower() == "none" or not sms_gateway:  # Edge case. If sms_gateway is empty or equal to none...
		voice.send_sms(number, message)
		print "Sending via google voice"
	else:
	# TODO: Option for MMS gateway.
		server.sendmail('speedyswimmer1000@gmail.com', toaddr, message)
	
def parseNames(name):
	test = re.sub("<NAME>", name, contents, count = 400) # Also a count of how many there are
	# Substitute the "<NAME>" tag with the name of the person. This is called within the function as it prepares to send the name. 
	return test  # Does not and *should* not permanently replace the name tag in the string. 

	# Open an SMTP server to GMail.
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username,password)

def sign_in(): # To google voice. 
	email = 'speedyswimmer1000@gmail.com'
	password = 'ylamrmtdwkqetxjw'

	voice.login(email, password)
	
sign_in() # To google voice.
# TODO: Change this password as well. 

for x in range(len(selectedIndex)):
	wardNames[selectedIndex[x]][SELECTED] = 1
	
# Run through and see which names are selected to send a text message to. 	
for x in range(len(wardNames)):
	# If is an elder (sister) and the 'Elder' ('Sister') check button was checked, set the 'selected' property of that person. 
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
		message = parseNames(wardNames[x][FIRST])  # Replace <NAME> with the name of the person. 
		message = message.rstrip('\n\r') # Strip off trailing newlines
		number = wardNames[x][PHONE_NUM]  # Get the name, number, and SMS gateway of the person. 
		sms_gateway = wardNames[x][SMS_NUM]
		mms_gateway = wardNames[x][MMS_NUM]
		print message
		sendMessage(message, number, sms_gateway) # Send the message via the email gateway. 
		# TODO: Send via google voice if there is not a sms gateway. 


# time.sleep(1)


# voice.send_sms(phoneNumber, message)
