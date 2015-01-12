# Gmail checker include
import os, urllib2, feedparser

#VFD_CLR_TIMEOUT = 30

global clrTimer

# Ping an address waiting 'wait' for a response, return boolean response
def pinger(address, wait):

    response = os.system("ping -c 1 -q -W " + str(wait) + " " + address + " > /dev/null 2>&1")
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
