#!/usr/bin/env python2

# Licence #
# Licence Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0) (https://creativecommons.org/licenses/by-nc-sa/4.0/)

# Add scrpt to crontab :
# - crontab -e
# Adjust and add line :
# */1 * * * * python /home/bananapro/domoticz/scripts/firetv.py

# To find current active process :
# - adb start-server
# - adb connect <FIRETV_IP>
# - adb shell dumpsys window windows | grep mCurrentFocus
#       Example : mCurrentFocus=Window{c915ce0 u0 tv.pluto.android/tv.pluto.android.ui.main.LeanbackMainActivity}
#       string :  tv.pluto.android
#       Channel Name : Pluto TV
# - adb kill-server

import subprocess
import requests
from requests.auth import HTTPBasicAuth

###     --- CONFIG ---      ###
DEBUG=True

# Don't change this one !
loopMaxErrors=3

domoticz_ip="192.168.1.2"
domoticz_port="8080"
domoticz_user=""
domoticz_password="YOUR_PASSWORD"

firetv_ip="192.168.1.13"

firetv_channel_IDX="66" # Dummy text sensor to show the current active channel
firetv_switch_IDX="67"  # Dummy switch sensor to show if the FireTV is active or not (On or Off)
display_switch_IDX="68" # Dummy switch sensor to show the display state (On or Off)

# List of channels / activity strings to search with their friendly name to show in the dummy text sensor, 
#    and if this channel / activity should enable the FireTV dummy switch
# Enable debug to view the channel string

#           string                          Channel Name            FireTV switch active
channels = {    
            'netflix' :                     [ 'Netflix',            True],
            'molotov' :                     [ 'Molotov TV',         True],
            'amazon.firebat.landing' :      [ 'Amazon (Launcher)',  False],
            'amazon.firebat.detail' :       [ 'Amazon (Details)',   False],
			'amazon.avod.playbackclient' :  [ 'Amazon (Playing)',   True],
            'disney' :                      [ 'Disney',             True],
            #'kodi' :                        [ 'Kodi',               True],
            'iplayer' :                     [ 'iplayer',            True],
            'twitch' :                      [ 'Twitch',             True],
            'ted.android' :                 [ 'TED',                True],
            'tv.arte.plus7' :               [ 'ARTE',               True],
            'firetv.youtube' :              [ 'Youtube',            True],
            'smartyoutubetv' :              [ 'Youtube TV',         True],
            'videomanager.kids' :          	[ 'Youtube Kids',       True],
            'tunein.player' :               [ 'TuneIn Radio',       True],
            'cast.receiver' :               [ 'AllCast Receiver',   True],
            'tv.pluto.android' :            [ 'Pluto TV',           True],
            'com.limelight' :               [ 'Moonlight',          True],
            'launcher' :                    [ 'Launcher',           False]
            }
# Apps links :
# Downloader (easy file downloader and apk installer) : https://www.amazon.fr/gp/product/B01N0BP507/
# SmartYoutube / SmartYoutube Kids (No ads) : https://smartyoutubetv.github.io/ 
# TuneIn Radio : https://www.amazon.fr/gp/product/B004GYY714/   
# AllCast Receiver : https://www.amazon.fr/ClockworkMod-AllCast-for-Fire-TV/dp/B00JHMPP9S/       

###     --- END OF CONFIG ---      ###

def send_data(val_url):
    req='http://'+domoticz_ip+':'+domoticz_port+val_url
    r=requests.get(req,auth=HTTPBasicAuth(domoticz_user,domoticz_password))
    if  r.status_code != 200:
        print "Erreur API Domoticz"
        
def send_logMsg(logMsg, level):
    msg = '/json.htm?type=command&param=addlogmessage&message='+str(logMsg)
    msg+='&level='+str(level)
    send_data(msg)
          
# Connect to FireTV
subprocess.call("adb kill-server", shell=True)
subprocess.call("adb start-server", shell=True)
subprocess.call("adb connect "+firetv_ip, shell=True)

# Check current focus
error=0
while error<loopMaxErrors:
    try:
        currentFocus = subprocess.check_output("adb shell dumpsys window windows | grep mCurrentFocus", shell=True)
    except:
        error+=1
        continue
    break
if error>0:
    send_logMsg("FireTV+python+ADB+ERROR+:+currentFocus,+"+str(error), 4)  
currentFocusErrors = error

# Check display state 
error=0
while error<loopMaxErrors:
    try:
        displayPower = subprocess.check_output("adb shell dumpsys power | grep 'Display Power'", shell=True)
    except:
        error+=1
        continue
    break
if error>0:
    send_logMsg("FireTV+python+ADB+ERROR+:+displayPower,+"+str(i), 4)   
displayPowerErrors = error

# Close connection
subprocess.call("adb disconnect", shell=True)

# Default results
active=False
channel="Unknown"

# Loop inside list            
for channel_string, data in channels.items():
    if (currentFocus.find(channel_string) != -1):
        channel=data[0]
        active=data[1]
        break
   
# Convert boolean to string   
if active:
    active="On"
else:
    active="Off"
      
if (displayPower.find('ON') != -1):
    display="On"
else:
    display="Off"
        
if DEBUG:
    print "-- DEBUG START --"
    print "Current channel string : "+currentFocus
    print "Current Channel : "+channel
    print "FireTV active : "+active
    print "Display state : "+display
    print "currentFocus loop Errors : "+str(currentFocusErrors)
    print "displayPower loop Errors : "+str(displayPowerErrors)
    print "-- DEBUG END --"

# Send firetv state (dummy switch sensor)
url='/json.htm?type=command&param=switchlight&idx='+str(firetv_switch_IDX)
url+='&switchcmd='+str(active)
send_data(url)
    
# Send firetv current channel (dummy text sensor)
url='/json.htm?type=command&param=udevice&idx='+str(firetv_channel_IDX)
url+='&svalue='+str(channel)
send_data(url)

# Send display power state (dummy switch sensor)
url='/json.htm?type=command&param=switchlight&idx='+str(display_switch_IDX)
url+='&switchcmd='+str(display)
send_data(url)

