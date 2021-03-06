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
Motion2 = 0; Node2TS=""; Bat2=0;
Temp3 = 0;  Humid3 = 0;  Light3 = 0; Bat3 = 0; Node3TS="";
Temp4 = 0;  Humid4 = 0;  Light4 = 0; Bat4 = 0; Node4TS="";
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
    global BRAVIATV, ThingspeakAPIKey
    global Motion2, Node2TS, Bat2
    global Temp3, Humid3, Light3, Bat3, Node3TS 
    global Temp4, Humid4, Light4, Bat4, Node4TS 

    t = time.time()
    TS = datetime.datetime.fromtimestamp(t).strftime('%m/%d-%H:%M')


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

        # Motion detect node #2
        match = re.search(':N:2:MOTION:B:([0-9.]+):', wgLine)
        if match:
            Bat2 = match.group(1)
            # Set Motion for node2 (reset every minute when logged to web)
            Motion2 = 1
            Node2TS = TS
            # Toggle an ISY var that will light a keypad indicator
            myisy.var_set_value('Gmail', 100)
            myisy.var_set_value('Gmail', 0)
            vfdOut (vfdPort, str(unichr(0x0c)) + Node2TS + " Motion! Bat: " + Bat2, 5)
 
        # Temp/humidity sensor, node #3
        match = re.search(':N:3:T:(\d+):H:(\d+):L:(\d+):B:([0-9.]+):', wgLine)
        if match:
            Temp3 = match.group(1)
            Humid3 = match.group(2)
            Light3 = match.group(3)
            Bat3 = match.group(4)
            Node3TS = TS
            #webiopi.debug ("Light3: %s Bat3: %s" % (Light3,Bat3))
            vfdOut (vfdPort, str(unichr(0x0c))+"    "+Node3TS+" Temp: "+Temp3+" Humid: "+Humid3+" Light: "+Light3+" Bat: "+Bat3, 5)

        # Temp/humidity sensor, node #4
        match = re.search(':N:4:T:(\d+):H:(\d+):L:(\d+):B:([0-9.]+):', wgLine)
        if match:
            Temp4 = match.group(1)
            Humid4 = match.group(2)
            Light4 = match.group(3)
            Bat4 = match.group(4)
            Node4TS = TS
            #webiopi.debug ("Light4: %s Bat4: %s" % (Light4,Bat4))
            #vfdOut (vfdPort, str(unichr(0x0c))+"    "+Node4TS+" Temp: "+Temp4+" Humid: "+Humid4+" Light: "+Light4+" Bat: "+Bat4, 5)

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
    
    ####### Update timers and counters #######

    # Count up to 60 seconds then reset
    LOOP_CNT += 1
    if LOOP_CNT > 60:
        LOOP_CNT = 0

        ####### Event that happen once per minute #######

        # Log stuff to Thingspeak (can only log stuff once every 15 secs max)
        if Humid3 != 0:
            #webiopi.debug ("T: %s, H: %s, L: %s, B: %s, M: %s" % (Temp3,Humid3,Light3,Bat3,Motion2))
            params = urllib.urlencode({'field1': Temp3, 'field2': Humid3, 'field3': Motion2, 'key':ThingspeakAPIKey})
            gmail_vfd_include.webDataLog (webiopi, params)
            Motion2 = 0
 

    ####### 1 sec loop time #########
    webiopi.sleep(1)

# Called at WebIOPi shutdown
def destroy():
    GPIO.digitalWrite(RED1, GPIO.LOW);  GPIO.digitalWrite(RED2, GPIO.LOW)
    GPIO.digitalWrite(YEL1, GPIO.LOW);  GPIO.digitalWrite(YEL2, GPIO.LOW)
    GPIO.digitalWrite(BUZZ, GPIO.LOW);  GPIO.digitalWrite(GRN1, GPIO.LOW)

#### Macros called by javascript ######

@webiopi.macro
# Email status
def checkMail():
    #webiopi.debug("checkMail called")
    return "%d,%s" % (NEW_MAIL_CNT, SUBJECT)

@webiopi.macro
# Wireless motion sensor, node #2
def wsNode2():
    #webiopi.debug("wsNode2 called: %s" % (Motion2))
    return "%s,%s,%s" % (Motion2, Bat2, Node2TS)

@webiopi.macro
# Wireless temp/humid sensor, node #3
def wsNode3():
    #webiopi.debug("wsNode3 called: %s" % (Light3))
    return "%s,%s,%s,%s,%s" % (Temp3, Humid3, Light3, Bat3, Node3TS)

@webiopi.macro
# Wireless temp/humid sensor, node #4
def wsNode4():
    #webiopi.debug("wsNode4 called: %s" % (Light4))
    return "%s,%s,%s,%s,%s" % (Temp4, Humid4, Light4, Bat4, Node4TS)
