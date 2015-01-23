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
RED1 = 4;   RED2 = 17;  YEL1 = 22;  YEL2 = 10;   GRN1 = 9;   GRN2 = 11
BUZZ = 8

HOUR_ON  = 8  # Turn Light ON at 08:00
HOUR_OFF = 18 # Turn Light OFF at 18:00
LOOP_CNT = 0 
LAST_MAIL_CNT = 0
NEW_MAIL_CNT = 0

# Serial Ports, retrieve devices named in the config file
vfdPort = webiopi.deviceInstance("vfdPort") 
wgPort  = webiopi.deviceInstance("wgPort")
#serial.writeByte(0xFF)                    # write a single byte
#serial.writeBytes([0x01, 0x02, 0xFF])     # write a byte array
    
# Create http basic auth handler
Auth_handler = urllib2.HTTPBasicAuthHandler()
Auth_handler.add_password('New mail feed', 'https://mail.google.com/',
     gmail_vfd_auth.USERNAME, gmail_vfd_auth.PASSWORD)

# Called at WebIOPi startup
def setup():

    # print python version
    webiopi.debug ("Python ver: %s" % (sys.version))

    t = time.time()
    ts = datetime.datetime.fromtimestamp(t).strftime('%m/%d-%H:%M')

    # Set the output GPIOs
    GPIO.setFunction(RED1, GPIO.OUT);   GPIO.setFunction(YEL1, GPIO.OUT)
    GPIO.setFunction(YEL2, GPIO.OUT);   GPIO.setFunction(BUZZ, GPIO.OUT)
    GPIO.setFunction(RED2, GPIO.OUT);   GPIO.setFunction(GRN1, GPIO.OUT)

    # Init vfd clear timer
    gmail_vfd_include.clrTimer = TimerReset(1, vfdClear, args=[vfdPort])

    vfdOut (vfdPort, "Web Server Started at %s" % ts, 10)

    # Clear out wireless gateway serial port
    while (wgPort.available() > 0):
        wgPort.readString()

# WebIOPi script loop
def loop():
    global LOOP_CNT, NEW_MAIL_CNT, LAST_MAIL_CNT, VFDPORT, SUBJECT 

    #webiopi.debug ("LOOPING!")

    # Check unread gmails once per minute
    if LOOP_CNT == 0:
        t = time.time()
        ts = datetime.datetime.fromtimestamp(t).strftime('%m/%d-%H:%M')

        # Check for new emails, report count and subject of the latest
        GPIO.digitalWrite(YEL2, GPIO.HIGH)
        (NEW_MAIL_CNT, SUBJECT) = gmail_vfd_include.check_mail(webiopi, Auth_handler)
        #webiopi.debug("NEW_MAIL_CNT: %i" % (NEW_MAIL_CNT))
        GPIO.digitalWrite(YEL2, GPIO.LOW)

        if NEW_MAIL_CNT > 0:
            if NEW_MAIL_CNT > LAST_MAIL_CNT :
                GPIO.digitalWrite(GRN1, GPIO.HIGH)
                GPIO.digitalWrite(RED2, GPIO.LOW)
                GPIO.digitalWrite(BUZZ, GPIO.HIGH)
                time.sleep(0.1)
                GPIO.digitalWrite(BUZZ, GPIO.LOW)
                #webiopi.debug("\n%s: You have %i new emails! Last: %i\n" % 
                #    (ts,NEW_MAIL_CNT,LAST_MAIL_CNT))
                LAST_MAIL_CNT = NEW_MAIL_CNT
                vfdPort.write(" " * 25)          
                vfdOut (vfdPort, "Subj: %s" % SUBJECT, 30)
        else:
            GPIO.digitalWrite(GRN1, GPIO.LOW)
            GPIO.digitalWrite(RED2, GPIO.HIGH)
            LAST_MAIL_CNT = 0

    # Read wireless sensor gateway
    if (wgPort.available() > 0):
        data = wgPort.readString() 
        webiopi.debug (data)

    
    # Toggle heartbeat LED each loop
    value = not GPIO.digitalRead(YEL1)
    GPIO.digitalWrite(YEL1, value)
    
    LOOP_CNT += 1
    if LOOP_CNT > 60:
        LOOP_CNT = 0

    # 1 sec loop time
    webiopi.sleep(1)

# Called at WebIOPi shutdown
def destroy():
    GPIO.digitalWrite(RED1, GPIO.LOW);  GPIO.digitalWrite(RED2, GPIO.LOW)
    GPIO.digitalWrite(YEL1, GPIO.LOW);  GPIO.digitalWrite(YEL2, GPIO.LOW)
    GPIO.digitalWrite(BUZZ, GPIO.LOW);  GPIO.digitalWrite(GRN1, GPIO.LOW)

# Macros
@webiopi.macro
def checkMail():
    return "%d,%s" % (NEW_MAIL_CNT, SUBJECT)

@webiopi.macro
def setLightHours(on, off):
    global HOUR_ON, HOUR_OFF
    HOUR_ON = int(on)
    HOUR_OFF = int(off)
    return getLightHours()