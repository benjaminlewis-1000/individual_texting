import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText

import socket

socket.setdefaulttimeout(600)

fromaddr = 'speedyswimmer1000@gmail.com'
toaddr  = '3852083735@tmomail.net'

# msg = MIMEMultipart()

# msg['From'] = fromaddr
# msg['To'] = toaddr
# msg['Subject'] = ""

# body = "Python test mail"
# msg.attach(MIMEText(body, 'plain'))

msg = """Test email!"""


# Credentials (if needed)
username = 'provoysa97th@gmail.com'
password = 'communications'

# The actual mail send
server = smtplib.SMTP('smtp.gmail.com:587')
server.starttls()
server.login(username,password)

for i in range(300):
	server.sendmail(fromaddr, toaddr, msg)
	print "sent message"
server.quit()