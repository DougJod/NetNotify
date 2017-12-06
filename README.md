# NetNotify


### Description
This python script was developed to run on a headless Raspberry Pi (no keyboard/monitor/mouse). The purpose is to send a notification (via SalesForce Chatter Post) when the network IP address has changed.

### Setup
Install the required netifaces python module

~~~
sudo apt-get install python3-netifaces
~~~


This script requires the following environment variables to be set:  
* SFDC_KEY - Connected App OAUTH Key
* SFDC_SECRET - Connected App OAUTH Secret
* SFDC\_SUBJECT\_ID - ID of the chatter group to post, or 'me' for the current user feed.
* SFDC\_MENTION\_ID - SalesForce User ID to @mention in the Chatter Post
* SFDC_USER - SalesForce username for oauth connection.
* SFDC_PASS - SalesForce password for oauth connection.
* SFDC_TOKEN - SalesForce security token for oauth connection.


### Crontab
The best way to run this script is as a cron job. Run the following command to edit your local crontab:
~~~
crontab -e
~~~
  

The followign example will run the script once per day.
~~~
# m h  dom mon dow   command
0 0 * * * /<path to this repo>/NetNotify/netcheck.py
~~~