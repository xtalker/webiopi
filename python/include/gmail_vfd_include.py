# Gmail checker include
import os, urllib2, feedparser, httplib, urllib

#VFD_CLR_TIMEOUT = 30

global clrTimer, motion1Timer

# Log data to online logging service (thingspeak.com)
# Field#s: 1=Temp3, 2=Humid3, 3=Motion1 
def webDataLog(webiopi, params):

    # fieldName =""
    # if field1:
    #   fieldName = fieldName + "field" + str(field1) + ": " + data1 + ", "
    # if field2: 
    #   fieldName = fieldName + "field" + str(field2) + ": " + data2 + ", "
    # fieldName = "{" + fieldName + "'key':'D2UM25SKF7NOK8PT'}"  
    # webiopi.debug("webDataLog: fieldName: "+fieldName)
    
    #params = urllib.urlencode(fieldName)

    # field1 = "'" + field1 + "'"
    # field2 = "'" + field2 + "'"
    # params = urllib.urlencode({field1: data1, field2: data2, 'key':'D2UM25SKF7NOK8PT'})
    headers = {"Content-type": "application/x-www-form-urlencoded","Accept": "text/plain"}
    conn = httplib.HTTPConnection("api.thingspeak.com:80")
    resp = 0  
    try:
        conn.request("POST", "/update", params, headers)
        response = conn.getresponse()
        webiopi.debug ("webDataLog: logged to Thingspeak.com: status: %s" % (response.reason))
        resp = response.read()
        conn.close()
    except:
        webiopi.debug("webDataLog: Thingspeak connection failed")

    return resp

# Ping an address waiting 'wait' for a response, return boolean response
def pinger(address, wait):

    response = os.system("ping -c 1 -q -W " + str(wait) + " " + address + " > /dev/null 2>&1")
    #response = os.system("nmap -sn --max-retries " + str(wait) + " " + address + " > /dev/null 2>&1")
    # 256 = no response, 0 = responded

    #print "Pinger: Response: " + str(response) 

    if response == 0:
        return True
    else:
        return False

def check_mail(webiopi, Auth_handler):
  try:
    # Open url using the auth handler
    opener = urllib2.build_opener(Auth_handler)
    feed_file = opener.open('https://mail.google.com/mail/feed/atom/')
  except Exception:
    webiopi.debug("check_mail: URL Open Exception!")
    #webiopi.sleep(5)
    return 0, "none"

  try:
    # Parse feed using feedparser
    emails = feedparser.parse(feed_file)
    newmails = int(emails.feed.fullcount)
  except Exception:
    webiopi.debug("check_mail: Feed Parse Exception!")
    #webiopi.sleep(5)
    return 0, "none"

  if newmails > 0:
    subj = emails.entries[0].title
  else:
    subj = 'none'

  return newmails, subj
