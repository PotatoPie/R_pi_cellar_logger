# Based almost completely on Adafruit's tutorials for DHT and Google Doc updater (see below)
# Written by Paul Shamble, Dec 2014

# Depends on the 'gspread' package being installed.  If you have pip installed
# execute:
#   sudo pip install gspread

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import sys
import time
import datetime

import gspread
import Adafruit_DHT

# Set type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.DHT22

# Set pin number
DHT_PIN  = 23

# Google Docs account email, password, and spreadsheet name.
GDOCS_EMAIL            = 'INPUT REQUIRED'
GDOCS_PASSWORD         = ''
GDOCS_SPREADSHEET_NAME = ''

# Set parameters
time_bw_recordings = 15 # in minutes
strikes_bf_restart = 8 # consecutive fails before reboot triggers

# Set local log file
local_log = 'Data-log-file.txt'

# Intialize basic counters, do basic things
strikes = 0
time_bw_recordings = time_bw_recordings * 60 # convert to seconds

# Quick check
if GDOCS_EMAIL == 'INPUT REQUIRED'
	print('Program halted--Input email, password, spreadsheet names')
	sys.exit()

# function to get into spreadsheet
def login_open_sheet(email, password, spreadsheet):
	"""Connect to Google Docs spreadsheet and return the first worksheet."""
	try:
		gc = gspread.login(email, password)
		worksheet = gc.open(spreadsheet).sheet1
		return worksheet
	except:
		print ('Login failed--waiting a few seconds to try again')
		print (datetime.datetime.now)

# Open spreadsheet
worksheet = None
while True:
	# Login if necessary.
	if worksheet is None:
		worksheet = login_open_sheet(GDOCS_EMAIL, GDOCS_PASSWORD, GDOCS_SPREADSHEET_NAME)
	
	# Attempt data grab from sensor
	humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)
	# if readings fails, wait a bit and retry
	if humidity is None or temp is None:
		time.sleep(2)
		continue
	
	# Append the data in the spreadsheet and to local log
	try:
		worksheet.append_row((datetime.datetime.now(), temp, humidity)) # to gDoc
		dateToLog = strftime("%d %b %Y %H:%M:%S", localtime())
		logFile_handle = open(local_log, "a")
		logFile_handle.write(dateToLog + "\t" + str(temp) + "\t" + str(humidity) + "\n")
		logFile_handle.close()
		strikes = 0
	except:
		# Error appending data, most likely because credentials are stale.
		# Null out the worksheet so a login is performed at the top of the loop.
		strikes = strikes + 1
		if strikes > strikes_bf_restart:
			import os
			os.system("reboot")
		print ('Append error, waiting 2 sec to relog and retrying. Error at:')
		print ((datetime.datetime.now))
		worksheet = None
		time.sleep(2)
		continue

	# Wait desired time before repeating
	print ('Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME))
	print (dateToLog)
	print(worksheet)
	time.sleep(time_bw_recordings)
