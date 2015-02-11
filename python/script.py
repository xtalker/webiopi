# Start with: sudo webiopi -d -c /etc/webiopi/config
import webiopi
import datetime, time, sys, urllib2, re, urllib

webiopi.setDebug()

# Add path to my code
sys.path.insert(0, "/home/pi/myNas/RasPi/webiopi/python/include")

from Resetable_timer import TimerReset
from Resetable_timer import vfdClear
from Resetable_timer import vfdOut
import gmail_vfd_include; # Support methods
import gmail_vfd_auth; # Gmail credentials
import ISY

GPIO = webiopi.GPIO
#CHECKMAIL = gmail_vfd_include.check_mail

# RasPi leds: red1=4, buzz=8, grn1=9, yel2=10, grn2=11, red2=17, yel1=22 
RED1 = 4;   RED2 = 17;  YEL1 = 22;  YEL2 = 10;   GRN1 = 9;   GRN2 = 11
BUZZ = 8

HOUR_ON  = 8  # Turn Light ON at 08:00
HOUR_OFF = 18 # Turn Light OFF at 18:00
LOOP_CNT = 60 
LAST_MAIL_CNT = 0;  NEW_MAIL_CNT = 0;
Temp3 = 0;  Humid3 = 0;     Bat3 = 0;
BRAVIATV = '192.168.0.3'
TVState1 = 0;  TVState2 = 0
TS = ''
ThingspeakAPIKey = "D2UM25SKF7NOK8PT"
 
# Serial Ports, retrieve devices named in the config file
vfdPort = webiopi.deviceInstance("vfdPort") 
wgPort  = webiopi.deviceInstance("wgPort")
#serial.writeByte(0xFF)                    # write a single byte
#serial.writeBytes([0x01, 0x02, 0xFF])     # write a byte array
    
# Create http basic auth handler
Auth_handler = urllib2.HTTPBasicAuthHandler()
Auth_handler.add_password('New mail feed', 'https://mail.google.com/',
     gmail_vfd_auth.USERNAME, gmail_vfd_auth.PASSWORD)

# Open connection to ISY, init ISY vars
myisy = ISY.Isy(addr="192.168.0.10", eventupdates=0)
myisy.var_set_value('Gmail', 0)
myisy.var_set_value('TVstate', 0)


# Called at WebIOPi startup
def setup():

    # print python version
    webiopi.debug ("Python ver: %s" % (sys.version))

    t = time.time()
    TS = datetime.datetime.fromtimestamp(t).strftime('%m/%d-%H:%M')

    # Set the output GPIOs
    GPIO.setFunction(RED1, GPIO.OUT);   GPIO.setFunction(YEL1, GPIO.OUT)
    GPIO.setFunction(YEL2, GPIO.OUT);   GPIO.setFunction(BUZZ, GPIO.OUT)
    GPIO.setFunction(RED2, GPIO.OUT);   GPIO.setFunction(GRN1, GPIO.OUT)

    # Init vfd clear timer
    gmail_vfd_include.clrTimer = TimerReset(1, vfdClear, args=[vfdPort])

    vfdOut (vfdPort, "Web Server Started at %s" % TS, 10)

    # Clear out wireless gateway serial port
    while (wgPort.available() > 0):
        wgPort.readString()

# WebIOPi script loop
def loop():
    global LOOP_CNT, NEW_MAIL_CNT, LAST_MAIL_CNT, VFDPORT, SUBJECT, TVState1, TVState2
    global BRAVIATV, Temp3, Humid3, Bat3, TS, ThingspeakAPIKey

    t = time.time()
    TS = datetime.datetime.fromtimestamp(t).strftime('%m/%d-%H:%M')

    #webiopi.debug ("LOOPING!")

    #################################################################
    # Check unread gmails once per minute
    if LOOP_CNT == 60:

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
                #    (TS,NEW_MAIL_CNT,LAST_MAIL_CNT))
                LAST_MAIL_CNT = NEW_MAIL_CNT
                vfdPort.write(" " * 25)          
                vfdOut (vfdPort, "Subj: %s" % SUBJECT, 30)
        else:
            GPIO.digitalWrite(GRN1, GPIO.LOW)
            GPIO.digitalWrite(RED2, GPIO.HIGH)
            LAST_MAIL_CNT = 0


    #################################################################
    # Read wireless sensor gateway
    if (wgPort.available() > 0):
        wgLine = wgPort.readString() 
        webiopi.debug (wgLine)

      # # Motion detect node
        if re.search(':N:2:MOTION:B:', wgLine):
            vfdOut (vfdPort, str(unichr(0x0c)) + TS + " Motion!", 5)
            myisy.var_set_value('Gmail', 100)
            myisy.var_set_value('Gmail', 0)
            #gmail_vfd_include.webDataLog (webiopi, 'field3', 1, 'field3', 0)
            #gmail_vfd_include.webDataLog (webiopi, 3, 0)

        # Temp/humidity sensor node
        match = re.search(':N:3:T:(\d+):H:(\d+):B:([0-9.]+):', wgLine)
        if match:
            Temp3 = match.group(1)
            Humid3 = match.group(2)
            Bat3 = match.group(3)
            vfdOut (vfdPort, str(unichr(0x0c))+TS+" Temp: "+Temp3+" Humid: "+Humid3+" Bat: "+Bat3, 5)
            params = urllib.urlencode({'field1': Temp3, 'field2': Humid3, 'key':ThingspeakAPIKey})
            gmail_vfd_include.webDataLog (webiopi, params)
            #gmail_vfd_include.webDataLog (webiopi, 2, Humid3)


    #################################################################
    # Check if the TV changes state, update an ISY var if it does
    TVState1 = gmail_vfd_include.pinger(BRAVIATV, 1)
    if TVState1 != TVState2:
      if TVState1:
        myisy.var_set_value('TVstate', 1)
        vfdOut (vfdPort, TS + " TV On", 5)
      else:
        myisy.var_set_value('TVstate', 0)
        vfdOut (vfdPort, TS + " TV Off", 5)
      TVState2 = TVState1

    
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
# Email status
def checkMail():
    webiopi.debug("checkMail called")
    return "%d,%s" % (NEW_MAIL_CNT, SUBJECT)

@webiopi.macro
# Wireless temp/humid sensor, node #3
def wsTemp3():
    webiopi.debug("wsTemp3 called: %s" % (TS))
    return "%s,%s,%s,%s" % (Temp3, Humid3, Bat3, TS)

@webiopi.macro
def setLightHours(on, off):
    global HOUR_ON, HOUR_OFF
    HOUR_ON = int(on)
    HOUR_OFF = int(off)
    return getLightHours()