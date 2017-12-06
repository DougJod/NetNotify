#!/usr/bin/python3
import netifaces as ni
import json
import urllib.parse
import urllib.request
import urllib.error
import datetime
import os

LAST_IP_FILE = HOME+'/last_ip.txt'  # this needs to exist. TODO: automatically create this on first run.
IP_LOG_FILE = HOME+'/ip_log.txt'
IF_NAME = 'wlan0'
HOME = os.environ['HOME'] 
SFDC_LOGIN_URL = 'https://login.salesforce.com/services/oauth2/token'
SFDC_KEY = os.environ['SFDC_KEY'] 
SFDC_SECRET = os.environ['SFDC_SECRET'] 
SFDC_MENTION_ID = os.environ['SFDC_MENTION_ID']
SFDC_SUBJECT_ID = os.environ['SFDC_SUBJECT_ID']
SFDC_USER = os.environ['SFDC_USER'] 
SFDC_PASS = os.environ['SFDC_PASS'] 
SFDC_TOKEN = os.environ['SFDC_TOKEN'] 

def logValues() :
    print ('SFDC_SUBJECT_ID: ',SFDC_SUBJECT_ID)
    print ('SFDC_USER: ',SFDC_USER)
    #print ('SFDC_PASS: ',SFDC_PASS)
    #print ('SFDC_TOKEN: ',SFDC_TOKEN)


############################################################################
# Authenticate to SalesForce.
# Return oauth data if successful.
####################################
def sfdcAuthenticate() :
	oauthData = {}
	reqData={}
	reqData['grant_type'] = 'password'
	reqData['client_id'] = SFDC_KEY
	reqData['client_secret'] = SFDC_SECRET
	reqData['username'] = SFDC_USER
	reqData['password'] = SFDC_PASS+SFDC_TOKEN
	reqData = urllib.parse.urlencode(reqData) 
	req = urllib.request.Request(SFDC_LOGIN_URL, data=reqData.encode('utf-8'))
	req.add_header('content-type','application/x-www-form-urlencoded')

	try :
		response = urllib.request.urlopen(req)
		oauthData = json.loads(response.read().decode('utf-8'))
		#print ('got oauthData: ', oauthData)
	except urllib.error.URLError as e:
		print ('could not send request:', e.reason)

	return oauthData

##############################################################################
# Append the old IP address to the ip change log file. 
#######################################################
def logOldIp(oldIp) :
	log = open(IP_LOG_FILE, 'a')
	log.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - Old IP: '+oldIp +'\n')
	log.close()

##############################################################################
# Check if the WiFi IP address has changed.
###########################################
def hasIpChanged(currentIp) :
	ipChanged = False
	# read last IP from file	
	f = open(LAST_IP_FILE, 'r+')
	lastIp = f.read()
	if (lastIp != currentIp) :
		ipChanged = True
		logOldIp(lastIp)
		f.seek(0)
		f.write(currentIp)
		f.truncate()
	f.close()
	return ipChanged

##############################################################################
# Send Chatter Notification to SFDC.
####################################
def sendChangeNotification(currentIp) :

	oauthData = sfdcAuthenticate()
	if 'access_token' in oauthData :
	
		feedUrl = oauthData['instance_url']+'/services/data/v41.0/chatter/feed-elements'
        #groupUrl = oauthData['instance_url']+''

		# message header
		headerSegment = {}
		headerSegment['type']='Text'
		headerSegment['text']='[#AutomatedMessage]\n'
		# @mention
		messageSegment = {}
		messageSegment['type']='Text'
		messageSegment['text']=' - Your Raspberry Pi IP has changed to: '+ currentIp
		# post body
		mentionSegment = {}
		mentionSegment['type']='mention'
		mentionSegment['id']=SFDC_MENTION_ID

		chatterPost = {}
		chatterPost['feedElementType'] = 'FeedItem'
		chatterPost['subjectId'] = SFDC_SUBJECT_ID
		chatterPost['body'] = {} 
		chatterPost['body']['messageSegments'] = [headerSegment, mentionSegment, messageSegment]

		reqData = json.dumps(chatterPost)

		req = urllib.request.Request(feedUrl, data=reqData.encode('utf-8'))
		req.add_header('Content-Type','application/json')
		req.add_header('Authorization','Bearer '+oauthData['access_token'])




		try :
			response = urllib.request.urlopen(req)
			data = json.loads(response.read().decode('utf-8'))
			#print ('got chatter data: ', data)
		except urllib.error.URLError as e:
			print ('chatter post failed: ',e.reason)
		
	else :
		print ('Failed to authenticate to SFDC.')



################################################################################
# PROGRAM ENTRY POINT
#####################

logValues()

# get the current IP of the wifi interface.
currentIp = ni.ifaddresses(IF_NAME)[ni.AF_INET][0]['addr']

# sanity test the IP format.
validIp = (None != currentIp) and (currentIp.count('.') == 3)

# if the IP has changed, send a notification with the new IP.
if (validIp and hasIpChanged(currentIp)) :
	sendChangeNotification(currentIp)

