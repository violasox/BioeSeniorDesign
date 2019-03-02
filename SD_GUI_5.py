# Completed GUI with formatting fixed
# Includes text messaging
# v5 includes GPIO incorporation

######## TO DO ##############
# - Need to run run.py from virtual environment before running this script
# - Close ssh connection??
# NEED TO add multiprocessing to update GUI properly when waiting for an input


import tkinter
from tkinter import *
import time
from time import strftime
import random
from twilio.rest import Client
import os
import re
from dotenv import Dotenv
import subprocess
import sys
from threading import Thread
#from multiprocessing.pool import ThreadPool

import RPi.GPIO as GPIO

class App:
    def __init__(self,master):
        self.top = master

        # Parameters
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.log_path = os.path.join(self.dir_path,'app.log')
        self.canvasDim = (480,320)
        self.alarmThreshold = 2.0
        self._job = None
        self.red = '#CE0000'
        self.green = '#00B700'
        self.blue = '#05009C'
        self.gray = '#D8D8D8'
        self.MATRIX = [
        ["1","2","3","A"],
        ["4","5","6","B"],
        ["7","8","9","C"],
        ["*","0","#","D"]]
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        self.BUZZER = 26
        GPIO.setup(self.BUZZER,GPIO.OUT)
        
        self.ROW1 = 23
        self.ROW2 = 18
        self.ROW3 = 15
        self.ROW4 = 14
        self.COL1 = 22
        self.COL2 = 27
        self.COL3 = 17
        self.COL4 = 4

        self.ROW = [self.ROW1, self.ROW2, self.ROW3, self.ROW4] # BCM numbering
        self.COL = [self.COL1, self.COL2, self.COL3, self.COL4] # BCM numbering
        
        # GPIO pin setup
        for j in range(4):
            GPIO.setup(self.COL[j], GPIO.OUT)
            GPIO.output(self.COL[j], 1)
            
        for i in range(4):
            GPIO.setup(self.ROW[i], GPIO.IN, pull_up_down=GPIO.PUD_UP)

        # Variable initialization

        # Dummy values
        #self.setPressure = '5'
        #self.currentPressure = 5
        #self.highPressureLim = 7
        #self.lowPressureLim = 3
        #self.phoneNum = '7342337513'
    
        #self.setPressurePool = ThreadPool(processes=1)
    
        self.setPressure = ""
        self.newPressureDigit = ""
        self.currentPressure = DoubleVar()
        self.highPressureLim = self.currentPressure.get() + self.alarmThreshold
        self.lowPressureLim = self.currentPressure.get() - self.alarmThreshold
        self.phoneNum = ""
        self.newPhoneDigit = ""


        # widgets
        #self.B_clear = Button(top, text="Clear", bd=5, relief=RAISED, command=self.clear)

        # On every page
        self.B_home = Button(top, text="Home", bd=5, relief=RAISED,padx=15,pady=15,command=self.homePage)
        self.B_home.config(font=("Helvetica", 15))
        self.L_oxydasBig = Label(top, text="Oxy-Das", fg = self.blue, font=("Helvetica", 60, "bold italic"))
        self.L_oxydas = Label(top, text="Oxy-Das", fg = self.blue, font=("Helvetica", 30, "bold italic"))

        # Home page
        self.B_calibrate = Button(top, text="Calibrate", bd=5, relief=RAISED, padx=15,pady=15,command=self.calibrationPage1)
        self.B_calibrate.config(font=("Helvetica", 20))
        self.B_monitor = Button(top, text="Start Monitoring", bd=5, relief=RAISED, padx=15,pady=15,wraplength=120,command=self.enterPhoneNumPage)
        self.B_monitor.config(font=("Helvetica", 20))

        # Enter phone number
        self.L_enterPhoneNum = Label(top, text = "Enter Phone Number", font=("Helvetica", 20))
        self.L_enteredPhoneNum = Label(top, text = self.phoneNum, font=("Helvetica", 20))
        self.B_enterPhoneNum = Button(top, text = "Enter",bd=5, relief=RAISED, padx=15,pady=5,command=self.pressureDisplayPage)
        self.B_enterPhoneNum.config(font=("Helvetica", 15))

        # Pressure Display Page
        self.L_bcpapPressure = Label(top, text = "Bubble CPAP Pressure", font=("Helvetica", 20))
        self.L_units = Label(top, text = "cm H2O", font=("Helvetica", 20))
        #self.L_cannulaOut = Label(top, text = "Cannula Out!")
        #self.L_highPressure = Label(top, text = "High Pressure!")

        # Calibration Page 1
        self.L_pressureSet = Label(top, text = "1. Enter pressure set in bubble CPAP system", font=("Helvetica", 20))
        self.L_pressureSetVal = Label(top, text=self.setPressure, font=("Helvetica", 20))
        self.B_pressureSet = Button(top, text = "Enter",bd=5, relief=RAISED, padx=15,pady=5,command=self.testCalibrationLow)
        self.B_pressureSet.config(font=("Helvetica", 15))

        # Test Calibration
        self.L_test = Label(top, text = "Test device function:",font=("Helvetica", 15))
        self.C_test = Canvas(top,width=self.canvasDim[0]-20,height=80,)
        self.C_test.config(bg=self.gray)

        # Test Calibration Low
        self.L_testLow = Label(top, text = "2. Decrease the pressure and confirm appropriate device response.",bg=self.gray,wraplength=250,font=("Helvetica", 15))
        self.B_testLow = Button(top, text = "Confirm",bd=5, relief=RAISED, padx=15,pady=5,command=self.testCalibrationHigh)
        self.B_testLow.config(font=("Helvetica", 15))

        # Test Calibration High
        self.L_testHigh = Label(top, text = "3. Increase the pressure and confirm appropriate device response.",bg=self.gray,wraplength=250,font=("Helvetica", 15))
        self.B_testHigh = Button(top, text = "Confirm",bd=5, relief=RAISED, padx=15,pady=5,command=self.homePage)
        self.B_testHigh.config(font=("Helvetica", 15))

        ## GPIO pins for the ADC
        self.SPICLK = 21
        self.SPIMISO = 19
        self.SPIMOSI = 20
        self.SPICS = 16
        
        # set up the SPI interface pins
        GPIO.setup(self.SPIMOSI, GPIO.OUT)
        GPIO.setup(self.SPIMISO, GPIO.IN)
        GPIO.setup(self.SPICLK, GPIO.OUT)
        GPIO.setup(self.SPICS, GPIO.OUT)

        # 10k trim pot connected to adc #0
        self.potentiometer_adc = 0;
        # Need to measure what this is
        self.pressureThresholdV = 0;
        self.maxV = 5.0;
        # 10-bit ADC
        self.numTicks = 1024;
        self.zeroPressureV = 0.25;
        self.maxPressureV = 4.0;
        self.zeroPressure = 0.0;
        self.maxPressure = 35.56;
        self.sendTextDelay = 30; # send text every __ seconds
        self.timeSent = 0;
        self.timeElapsed = 0;

        ## MAIN PROGRAM
        # Load the environment variables with Twilio account info and phone numbers
        load_dotenv = Dotenv(os.path.join(os.path.dirname(os.path.realpath(__file__)),".env"))
        os.environ.update(load_dotenv)
        # Your Account Sid and Auth Token from twilio.com/console
        self.account_sid = os.environ['TWILIO_SID']
        self.auth_token = os.environ['TWILIO_AUTH']
        self.client = Client(self.account_sid, self.auth_token)
        self.command=os.environ['COMMAND']

        #self.fwding_host = "sd16-oxydas-U9ms33M2g1h05p1t2l"#os.environ['FWDING_HOST']
        #self.local_port = "5000"#os.environ['LOCAL_PORT']
        #self.command = "serveo.net"
        self.ssh = subprocess.Popen([self.command], shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(self.ssh.communicate())

        self.B_home.grid(row=0,column=0,padx=10,pady=10,sticky=NW)
        self.L_oxydasBig.grid(row=1,padx=110,pady=25,sticky=N)
        self.B_calibrate.grid(row=2,column=0,padx=70,sticky=W)
        self.B_monitor.grid(row=2,column=0,padx=70,sticky=E)
        
        self.startCalibration = False
        self.pressureIsSet = False
        self.startEnterPhoneNum = False
        self.phoneNumIsSet = False
        
        self.textAcknowledged = False
        self.startIdleMode = False
        self.idleModeDuration = 65
        self.idleModeTimeStarted = 0
        self.idleModeTimeElapsed = 0
        

        # Uncomment for testing purposes
        #self.clear()
        #self.L_oxydas.grid(row=0,padx=175,pady=25,sticky=N)

        #self.pressureGuiUpdate();

        #self._job = self.top.after(1000,self.pressureDisplayPage)


    def getNewData(self):
        ## TO USE WITH COMPUITER FOR DEBUGGING ONLY
        #return random.uniform(1.0,10.0)

        # TO USE WITH PRESSURE SENSOR
        curPressureTicks = self.readadc(self.potentiometer_adc, self.SPICLK, self.SPIMOSI, self.SPIMISO, self.SPICS)
        curPressureV = (self.maxV*curPressureTicks) / self.numTicks;
        conversionV2P = (self.maxPressure - self.zeroPressure)/(self.maxPressureV - self.zeroPressureV);
        curPressure = (curPressureV-self.zeroPressureV)*conversionV2P;
        return curPressure

    # Credit to Adafruit for this function
    # read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
    def readadc(self, adcnum, clockpin, mosipin, misopin, cspin):
            if ((adcnum > 7) or (adcnum < 0)):
                    return -1
            GPIO.output(cspin, True)

            GPIO.output(clockpin, False)  # start clock low
            GPIO.output(cspin, False)     # bring CS low

            commandout = adcnum
            commandout |= 0x18  # start bit + single-ended bit
            commandout <<= 3    # we only need to send 5 bits here
            for i in range(5):
                    if (commandout & 0x80):
                            GPIO.output(mosipin, True)
                    else:
                            GPIO.output(mosipin, False)
                    commandout <<= 1
                    GPIO.output(clockpin, True)
                    GPIO.output(clockpin, False)

            adcout = 0
            # read in one empty bit, one null bit and 10 ADC bits
            for i in range(12):
                    GPIO.output(clockpin, True)
                    GPIO.output(clockpin, False)
                    adcout <<= 1
                    if (GPIO.input(misopin)):
                            adcout |= 0x1

            GPIO.output(cspin, True)

            adcout >>= 1       # first bit is 'null' so drop it
            return adcout
        
    def numWriter(self):
        #print('Got to numWriter')
        counter = 0
        num = ""
        while counter == 0:
            for j in range(4):
                GPIO.output(self.COL[j],0)
            
                for i in range(4):
                    if GPIO.input(self.ROW[i]) == 0:
                        num = self.MATRIX[i][j]
                        counter = 1
                        #print(MATRIX[i][j])
                        time.sleep(0.1)
                        while(GPIO.input(self.ROW[i])) == 0:
                            pass
                GPIO.output(self.COL[j],1)
    
        #print('num is ', num)
        return num
    
    def buzz(self):
        GPIO.output(self.BUZZER,GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(self.BUZZER,GPIO.LOW)
        time.sleep(0.5)
    
    def checkAlertAcknowledged(self):
        #checkTimestamp = "[2019-03-02 02:19:28]"
        checkTimestamp = strftime('[%Y-%m-%d %H:%M:%S]')
        checkMin = checkTimestamp[15:17]
        #checkSec = checkTimestamp[19:21]
        #print(checkMin)
        #input("Press enter to continue...")
        with open(self.log_path, "r") as log_file:
            lines = log_file.read().splitlines()
            last_line = lines[-1]
        lastLogMin = last_line[15:17]
        #lastLogSec = last_line[19:21]
        #print(lastLogMin)
        #input("Press enter to continue")
        #print(str(int(checkMin) - int(lastLogMin)))
        #print(str(int(checkSec) - int(lastLogSec)))
        if (int(checkMin) - int(lastLogMin) == 0 or int(checkMin) - int(lastLogMin) == -59):
            if "200 OK" in last_line:
                self.textAcknowledged = True

    def endProcess(self):
        if self._job is not None:
            self.top.after_cancel(self._job)
            self._job = None

    def clear(self):
        widgetsList = self.top.grid_slaves()
        for widget in widgetsList:
            widget.grid_remove()
        self.top.configure(background = "white")
        self.B_home.grid(row=0,column=0,padx=10,pady=10,sticky=NW)


    def homePage(self):
        self.endProcess()
        self.clear()
        self.L_oxydasBig.grid(row=1,padx=110,pady=25,sticky=N)
        self.B_calibrate.grid(row=2,column=0,padx=70,sticky=W)
        self.B_monitor.grid(row=2,column=0,padx=70,sticky=E)
    
    def enterPhoneNumPage(self):
        self.endProcess()
        self.clear()
        self.L_oxydas.grid(row=0,padx=175,pady=25,sticky=N)
        self.L_oxydas.config(fg=self.blue,bg="white")

        self.L_enterPhoneNum.grid(row=1,pady=20)
        #self.L_enteredPhoneNum.grid(row=2)
        #print("showing phone num")
        self.B_enterPhoneNum.grid(row=3,pady=20)
        
        # If phone number has not been entered yet
        if (not self.phoneNumIsSet):
            numDigits = len(self.phoneNum)
            # Iteration 1 to display everything else on the screen
            if (not self.startEnterPhoneNum):
                self.startEnterPhoneNum = True
            # Iterations 2-10
            elif (numDigits < 10):
                self.newPhoneDigit = self.numWriter()
            # Iterations 11+
            else:
                self.newPhoneDigit = ""
                self.phoneNumIsSet = True
            self.phoneNum = "{}{}".format(self.phoneNum, self.newPhoneDigit)
            self.L_enteredPhoneNum.config(text = self.phoneNum)
            self.L_enteredPhoneNum.grid(row=2)
               
        else:
            self.L_enteredPhoneNum.config(text = self.phoneNum)
            self.L_enteredPhoneNum.grid(row=2)
        
        self._job = self.top.after(1000,self.enterPhoneNumPage)

    def getStatus(self, currentPressure, lowPressureLim, highPressureLim):
        # Cannula in
        if currentPressure > lowPressureLim and currentPressure < highPressureLim:
            return 1
        # Cannula out
        elif currentPressure < lowPressureLim:
            return 0
        # High pressure
        else:
            return 2

    def sendText(self):
        message = self.client.messages.create(
                     body="Alert: cannula out in room 5",
                     from_=os.environ['SEND_NUMBER'],
                     to=os.environ['RECV_NUMBER'])#,
                     #status_callback="https://postb.in/b/GbJzpb3m")
        #time.sleep(15) # wait time in seconds
        #self.textTimer == 0
    
    def enterIdleMode(self):
        # if idle mode has been entered, idle mode has started and the text has been acknowledged
        self.startIdleMode = True
        self.textAcknowledged = True
        time.sleep(self.idleModeDuration)
        # at the end of the idle mode period, reset startIdleMode and textAcknowledged
        self.startIdleMode = False
        self.textAcknowledged = False
    
    def pressureGuiUpdate(self):
        self.currentPressure = self.getNewData()
        status = self.getStatus(self.currentPressure, self.lowPressureLim, self.highPressureLim)

        self.L_bcpapPressure.grid(row=1)

        if self.currentPressure >= 10.0:
            currentPressureFormatted = str(round(self.currentPressure))
        else:
            currentPressureFormatted = str(round(self.currentPressure,1))
        L_currentPressure = Label(top, text = currentPressureFormatted,font=("Helvetica", 85))
        L_currentPressure.grid(row=2,column=0,pady=10)

        self.L_units.grid(row=2,column=0,padx=85,pady=25,sticky=SE)

        myWidgets = [self.top,self.L_oxydas,self.L_bcpapPressure,L_currentPressure,self.L_units];

        #print(self.timeElapsed)

        if (status == 1):
            for wid in myWidgets:
                wid.config(bg=self.green)
            L_status = Label(top, text = "Cannula In",font=("Helvetica", 30))
            L_status.config(bg=self.green)
        # when cannula comes out
        elif (status == 2):
            # check if the nurse acknowledged the message only if not already in idle mode
            if (self.startIdleMode is False):
                self.checkAlertAcknowledged()
            print("text acknowledged is ", str(self.textAcknowledged))
            # if nurse hasn't acknowledged the message
            if (self.textAcknowledged is False):
                self.idleModeTimeStarted = 0
                self.idleModeTimeElapsed = 0
                print("Text not seen yet, need to start buzzing")
                # start buzzing
                BuzzThread = Thread(target=self.buzz)
                BuzzThread.start()
                # if a text hasn't been sent or it has been a minute, send a text
                if (self.timeSent == 0 or self.timeElapsed > self.sendTextDelay):
                    print("Text sent")
                    self.sendText()
                    self.timeSent = time.time();
                else:
                    #print("Passed")
                    pass
            # if a nurse has acknowledged the message
            else:
                #print("Text has been seen")
                # go into idle mode if it hasn't already happened
                if (self.idleModeTimeStarted == 0):
                    #self.startIdleMode = True
                    print("STAAAAAART")
                    self.startIdleMode = True
                    self.textAcknowledged = True
                    self.idleModeTimeStarted = time.time()
                elif (self.idleModeTimeElapsed < self.idleModeDuration):
                    print("In IDLE MODE: ", str(self.idleModeTimeElapsed))
                elif (self.idleModeTimeElapsed >= self.idleModeDuration):
                    print("Idle mode complete")
                    self.startIdleMode = False
                    self.textAcknowledged = False
                    #self.idleModeTimeStarted = 0;
                
                
                #self.idleModeDuration = 30
                #self.idleModeTimeStarted = 0
                #self.idleModeTimeElapsed = 0
                #if (self.startIdleMode is False):
                #    print('start idle mode is', self.startIdleMode)
                #    IdleThread = Thread(target=self.enterIdleMode)
                #    IdleThread.start()
                ## if idle mode has already started, don't go into it again
                #else:
                #    print("IN IDLE MODE ", self.startIdleMode)
                #    pass
            for wid in myWidgets:
                wid.config(bg=self.red)
            L_status = Label(top, text = "Low Pressure",font=("Helvetica", 30))
            L_status.config(bg=self.red)
        # when there is high pressure (status = 3)
        else:
            for wid in myWidgets:
                wid.config(bg="orange")
            L_status = Label(top, text = "High Pressure",font=("Helvetica", 30))
            L_status.config(bg="orange")

        self.timeElapsed = time.time() - self.timeSent
        self.idleModeTimeElapsed = time.time() - self.idleModeTimeStarted

        L_status.grid_remove()
        L_status.grid(row=3)

    def pressureDisplayPage(self):
        self.endProcess()
        self.clear()
        
        envPhoneNum = "+1" + self.phoneNum
        ##print(type(envPhoneNum))
        #os.environ['RECV_NUMBER']=envPhoneNum
        self.L_oxydas.grid(row=0,padx=175,pady=25,sticky=N)

        self.pressureGuiUpdate();

        self._job = self.top.after(1000,self.pressureDisplayPage)

    def pressureGuiUpdateCalibration(self):
        self.currentPressure = self.getNewData()
        status = self.getStatus(self.currentPressure, self.lowPressureLim, self.highPressureLim)

        L_bcpapPressure = Label(top, text = "Bubble CPAP Pressure", font=("Helvetica", 20))
        L_bcpapPressure.grid(row=1)

        if self.currentPressure >= 10.0:
            currentPressureFormatted = str(round(self.currentPressure))
        else:
            currentPressureFormatted = str(round(self.currentPressure,1))
        L_currentPressure = Label(top, text = currentPressureFormatted,font=("Helvetica", 30))
        L_currentPressure.grid(row=2,column=0,pady=5)

        L_unitsCal = Label(top, text = "cm H2O", font=("Helvetica", 20))
        L_unitsCal.grid(row=2,column=0,padx=120,pady=8,sticky=SE)

        myWidgets = [self.top,self.L_oxydas,L_bcpapPressure,L_currentPressure,L_unitsCal];

        if (status == 1):
            for wid in myWidgets:
                wid.config(bg=self.green)
            L_status = Label(top, text = "Cannula In",font=("Helvetica", 20))
            L_status.config(bg=self.green)
        elif (status == 2):
            for wid in myWidgets:
                wid.config(bg=self.red)
            L_status = Label(top, text = "Low Pressure",font=("Helvetica", 20))
            L_status.config(bg=self.red)
        else:
            for wid in myWidgets:
                wid.config(bg="orange")
            L_status = Label(top, text = "High Pressure",font=("Helvetica", 20))
            L_status.config(bg="orange")

        L_status.grid_remove()
        L_status.grid(row=3)

    def calibrationPage1(self):
        self.endProcess()
        self.clear()
        self.L_oxydas.grid(row=0,padx=175,pady=25,sticky=N)
        self.L_oxydas.config(bg="white")
        self.L_units.config(bg="white")
        
        self.L_pressureSet.grid(row=1, pady=20)
        self.L_pressureSetVal.grid(row=2,column=0)
        self.L_units.grid(row=2,column=0,padx=120,sticky=E)
        self.B_pressureSet.grid(row=3,pady=30)
        
        # If pressure has not been set yet
        if (not self.pressureIsSet):
            numDigits = len(self.setPressure)
            # Iteration 1
            if (not self.startCalibration):
                self.startCalibration = True
                print('Got here')
            # Iteration 2 - until the first number is pressed
            elif (numDigits == 0):
                self.newPressureDigit= self.numWriter()
                self.setPressure = "{}{}".format(self.setPressure, self.newPressureDigit)
                self.L_pressureSetVal.config(text = self.setPressure)
                if (self.newPressureDigit != "1"):
                    self.pressureIsSet = True
                    print('Pressure is set!')
                else:
                    pass
            # If first digit entered is 1, the second digit entered is only allowed to be 0
            else:
                self.newPressureDigit = self.numWriter()
                if (self.setPressure != "1" or self.newPressureDigit != "0"):
                    self.newPressureDigit = ""
                    print("Only 0 allowed after 1")
                else:
                    self.pressureIsSet = True
                    self.setPressure = "{}{}".format(self.setPressure, self.newPressureDigit)
                    self.L_pressureSetVal.config(text = self.setPressure)
                    print('Pressure is set!')
        else:
            pass
        
        self._job = self.top.after(1000, self.calibrationPage1)
        

    def testCalibrationLow(self):
        self.endProcess()
        self.clear()
        self.L_oxydas.grid(row=0,padx=175,pady=25,sticky=N)

        self.pressureGuiUpdateCalibration();

        self.C_test.grid(row=4,sticky=S)
        self.L_test.grid(row=4,padx=40,pady=30,sticky=NW)
        self.L_testLow.grid(row=4,padx=40,pady=30,sticky=SW)
        self.B_testLow.grid(row=4,padx=50,pady=35,sticky=E)

        self._job = self.top.after(1000,self.testCalibrationLow)

    def testCalibrationHigh(self):
        self.endProcess()
        self.clear()
        self.L_oxydas.grid(row=0,padx=175,pady=25,sticky=N)

        self.pressureGuiUpdateCalibration();

        self.C_test.grid(row=4,sticky=S)
        self.L_test.grid(row=4,padx=40,pady=30,sticky=NW)
        self.L_testHigh.grid(row=4,padx=40,pady=30,sticky=SW)
        self.B_testHigh.grid(row=4,padx=50,pady=35,sticky=E)

        self._job = self.top.after(1000,self.testCalibrationHigh)


top = Tk()
top.geometry("480x320")
app = App(top)
top.after(1000,app.getNewData)
top.mainloop()
