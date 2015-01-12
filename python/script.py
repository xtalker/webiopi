# Start with: sudo webiopi -d -c /etc/webiopi/config
import webiopi
import datetime, time, sys, urllib2

webiopi.setDebug()

# Add path to my code
sys.path.insert(0, "/home/pi/myNas/RasPi/webiopi/python/include")

from Resetable_timer import TimerReset
from Resetable_timer import vfdClear
from Resetable_timer import vfdOut
import gmail_vfd_include; # Support methods
import gmail_vfd_auth; # Gmail credentials

GPIO = webiopi.GPIO
#CHECKMAIL = gmail_vfd_include.check_mail

# RasPi leds: red1=4, buzz=8, grn1=9, yel2=10, grn2=11, red2=17, yel1=22 
RED1 = 4 # GPIO pin, red led
YEL1 = 10 # GPIO pin, yellow led

HOUR_ON  = 8  # Turn Light ON at 08:00
HOUR_OFF = 18 # Turn Light OFF at 18:00

# Create http basic auth handler
Auth_handler = urllib2.HTTPBasicAuthHandler()
Auth_handler.add_password('New mail feed', 'https://mail.google.com/',
     gmail_vfd_auth.USERNAME, gmail_vfd_auth.PASSWORD)

# setup function is automatically called at WebIOPi startup
def setup():

    # print python version
    webiopi.debug ("Python ver: %s" % (sys.version))

    t = time.time()
    ts = datetime.datetime.fromtimestamp(t).strftime('%m/%d-%H:%M')

    # set the GPIO used by the light to output
    GPIO.setFunction(RED1, GPIO.OUT)
    GPIO.setFunction(YEL1, GPIO.OUT)

    # Serial Ports
    vfdPort = webiopi.deviceInstance("vfdPort") # retrieve device named "vfdPort" in the config
    #serial.writeByte(0xFF)                    # write a single byte
    #serial.writeBytes([0x01, 0x02, 0xFF])     # write a byte array

    # Init vfd clear timer
    gmail_vfd_include.clrTimer = TimerReset(1, vfdClear, args=[vfdPort])

    vfdOut (vfdPort, "Web Server Started at %s" % ts, 10)

# loop function is repeatedly called by WebIOPi 
def loop():
    t = time.time()
    ts = datetime.datetime.fromtimestamp(t).strftime('%m/%d-%H:%M')

    # Check for new emails
    (newmails, subj) = gmail_vfd_include.check_mail(webiopi, Auth_handler)
    webiopi.debug ("New: %i, Subj: %s" % (newmails,subj))

    # Toggle LED each loop
    value = not GPIO.digitalRead(YEL1)
    GPIO.digitalWrite(YEL1, value)
    
    # gives CPU some time before looping again
    webiopi.sleep(15)

# destroy function is called at WebIOPi shutdown
def destroy():
    GPIO.digitalWrite(RED1, GPIO.LOW)
    GPIO.digitalWrite(YEL1, GPIO.LOW)

# Macros
@webiopi.macro
def getLightHours():
    return "%d;%d" % (HOUR_ON, HOUR_OFF)

@webiopi.macro
def setLightHours(on, off):
    global HOUR_ON, HOUR_OFF
    HOUR_ON = int(on)
    HOUR_OFF = int(off)
    return getLightHours()