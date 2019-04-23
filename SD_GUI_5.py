# - Need to run run_log.py from virtual environment before running this script

import tkinter
from tkinter import *
import datetime
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


import RPi.GPIO as GPIO

class App:
    def __init__(self,master):
        self.top = master

        # Parameters
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.log_path = os.path.join(self.dir_path,'app.log')
        self.canvasDim = (800,450)
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
        GPIO.output(self.BUZZER,0)
        
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
        self.activationButtonText = "Activate Alarm"
        self.setPressure = ""
        self.setPressureNum = 0
        self.newPressureDigit = ""
        self.setFlowRate = ""
        self.setFlowRateNum = 1
        self.newFlowRateDigit = ""
        self.currentPressure = DoubleVar()
        self.highPressureLim = self.setPressureNum + self.alarmThreshold
        self.lowPressureLim = 1.0
        self.offset = 0.0
        self.phoneNum = ""
        self.newPhoneDigit = ""

        # widgets
        # On every page
        self.B_home = Button(top, text="Home", bd=5, relief=RAISED,padx=15,pady=15,command=self.homePage)
        self.B_home.config(font=("Helvetica", 15))
        self.B_info = Button(top, text = "i",bd=5, relief=RAISED,padx=15,pady=10,command=self.infoPage)
        self.B_info.config(font=("Times", 25, "bold"))
        self.L_oxydasBig = Label(top, text="Oxy-Das", fg = self.blue, bg = "white",font=("Helvetica", 60, "bold italic"))
        self.L_oxydas = Label(top, text="Oxy-Das", fg = self.blue, font=("Helvetica", 30, "bold italic"))

        # Home page
        self.B_calibrate = Button(top, text="Calibrate", bd=5, relief=RAISED, padx=15,pady=15,command=self.calibrationPage1)
        self.B_calibrate.config(font=("Helvetica", 20))
        self.B_monitor = Button(top, text="Start Monitoring", bd=5, relief=RAISED, padx=15,pady=15,wraplength=130,command=self.pressureDisplayPage)
        self.B_monitor.config(font=("Helvetica", 20))
        
        # Info page
        self.L_infoSetPressure = Label(top, text = "Set Pressure:", font=("Helvetica", 20))
        self.L_infoSetPressureVal = Label(top, text = self.setPressure, font=("Helvetica", 20))
        self.B_infoSetPressureEdit = Button(top,text="Edit",relief=RAISED, padx=15,pady=15,command=self.pressureReset)
        self.B_infoSetPressureEdit.config(font=("Helvetica", 15))

        self.L_infoSetFlowRate = Label(top, text = "Oxygen Flow Rate:", font=("Helvetica", 20))
        self.L_infoSetFlowRateVal = Label(top, text = self.setFlowRate, font=("Helvetica", 20))
        self.B_infoSetFlowRateEdit = Button(top,text="Edit",relief=RAISED, padx=15,pady=15,command=self.flowRateReset)
        self.B_infoSetFlowRateEdit.config(font=("Helvetica", 15))

        self.L_infoPhoneNum = Label(top, text = "Phone Number:", font=("Helvetica", 20))
        self.L_infoPhoneNumVal = Label(top, text = self.phoneNum, font=("Helvetica", 20))
        self.B_infoPhoneNumEdit = Button(top,text="Edit",relief=RAISED, padx=15,pady=15,command=self.phoneNumReset)
        self.B_infoPhoneNumEdit.config(font=("Helvetica", 15))
        
        # Enter phone number
        self.L_enterPhoneNum = Label(top, text = "Enter Phone Number", bg="white", font=("Helvetica", 30))
        self.L_enteredPhoneNum = Label(top, text = self.phoneNum, bg="white", font=("Helvetica", 30))
        self.B_enterPhoneNum = Button(top, text = "Enter",bd=5, relief=RAISED, padx=15,pady=5,command=self.pressureDisplayPage)
        self.B_enterPhoneNum.config(font=("Helvetica", 25))

        # Pressure Display Page
        self.L_bcpapPressure = Label(top, text = "Bubble CPAP Pressure", font=("Helvetica", 30))
        self.L_pressureUnits = Label(top, text = "cm H2O", font=("Helvetica", 20))
        self.B_activate = Button(top, text = self.activationButtonText,bd=5, relief=RAISED, padx=15,pady=5,command=self.alarmActivation);
        self.B_activate.config(font=("Helvetica", 15))

        # Calibration Page 1 - CPAP pressure
        self.L_pressureSet = Label(top, text = "Enter pressure set in bubble CPAP system", bg="white",font=("Helvetica", 25))
        self.L_pressureSetVal = Label(top, text=self.setPressure, bg="white",font=("Helvetica", 40))
        self.B_pressureSet = Button(top, text = "Enter",bd=5, relief=RAISED, padx=15,pady=5,command=self.calibrationPage2)
        self.B_pressureSet.config(font=("Helvetica", 15))
        
        # Calibration Page 2 - air flow rate
        self.L_flowRateSet = Label(top, text = "Enter oxygen flow rate", bg="white",font=("Helvetica", 25))
        self.L_flowRateSetVal = Label(top, text=self.setFlowRate, bg="white",font=("Helvetica", 40))
        self.L_flowRateUnits = Label(top,text = "L/min",font=("Helvetica", 20))
        self.B_flowRateSet = Button(top, text = "Enter",bd=5, relief=RAISED, padx=15,pady=5,command=self.testCalibrationSet)
        self.B_flowRateSet.config(font=("Helvetica", 15))

        # Test Calibration
        self.C_test = Canvas(top,width=self.canvasDim[0]-20,height=140)
        self.C_test.config(bg=self.gray)
        
        # Test Calibration Set
        self.L_testSet = Label(top, text = "Test device function\n\n 1. Confirm correct pressure display.",bg=self.gray,wraplength=450,font=("Helvetica", 15))
        self.B_testSet = Button(top, text = "Confirm",bd=5, relief=RAISED, padx=15,pady=5,command=self.testCalibrationLow)
        self.B_testSet.config(font=("Helvetica", 15))
        
        # Test Calibration Low
        self.L_testLow = Label(top, text = "Test device function\n\n 2. Decrease the pressure and confirm appropriate device response.",bg=self.gray,wraplength=450,font=("Helvetica", 15))
        self.B_testLow = Button(top, text = "Confirm",bd=5, relief=RAISED, padx=15,pady=5,command=self.testCalibrationHigh)
        self.B_testLow.config(font=("Helvetica", 15))

        # Test Calibration High
        self.L_testHigh = Label(top, text = "Test device function\n\n 3. Increase the pressure and confirm appropriate device response.",bg=self.gray,wraplength=450,font=("Helvetica", 15))
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
        
        self.alarmActivation = False
        self.startCalibration = False
        self.pressureIsSet = False
        self.startEnterPhoneNum = False
        self.phoneNumIsSet = False
        self.flowRateIsSet = False
        self.startEnterFlowRate = False
        
        self.textAcknowledged = False
        self.startIdleMode = False
        self.idleModeDuration = 60
        self.idleModeTimeStarted = 0
        self.idleModeTimeElapsed = 0
        self.refreshRate = 750
        self.outputTextFile = "trial" + datetime.datetime.now().strftime("%y-%m-%d-%H-%M") + ".txt"
    
    def alarmActivation(self):
        self.alarmActivation = not self.alarmActivation
        if (self.alarmActivation is True):
            self.activationButtonText = "Deactivate Alarm"
            self.B_activate.config(text=self.activationButtonText)
            self.B_activate.config(relief=SUNKEN)
        else:
            self.activationButtonText = "Activate Alarm"
            self.B_activate.config(text=self.activationButtonText)
            self.B_activate.config(relief=RAISED)
        
        #print(self.activationButtonText)
        self.pressureDisplayPage()
        
    def pressureReset(self):
        self.setPressure = ""
        self.newPressureDigit = ""
        self.L_pressureSetVal.config(text = self.setPressure)
        
        self.startCalibration = False
        self.pressureIsSet = False
        
        self.calibrationPage1()
    
    def flowRateReset(self):
        self.setFlowRate = ""
        self.newFlowRateDigit = ""
        self.L_flowRateSetVal.config(text = self.setFlowRate)
        
        self.startEnterFlowRate = False
        self.flowRateIsSet = False
        
        self.calibrationPage2()
    
    def phoneNumReset(self):
        self.phoneNum = ""
        self.newPhoneDigit = ""
        self.L_enteredPhoneNum.config(text = self.phoneNum)
        
        self.startEnterPhoneNum = False
        self.phoneNumIsSet = False
        
        self.enterPhoneNumPage()
    
    def openCircuitPressureAdjust(self, airFlowrate):
        if airFlowrate is 1:
            self.offset = 0.0
        elif airFlowrate is 2:
            self.offset = 0.1
        elif airFlowrate is 3:
            self.offset = 0.3
        elif airFlowrate is 4:
            self.offset = 0.4
        elif airFlowrate is 5:
            self.offset = 0.6
        elif airFlowrate is 6:
            self.offset = 0.8
        elif airFlowrate is 7:
            self.offset = 1.1
        elif airFlowrate is 8:
            self.offset = 1.5
        elif airFlowrate is 9:
            self.offset = 1.9
        elif airFlowrate is 10:
            self.offset = 2.3
    
    def setLowPressureAlertThreshold(self, cpapPressure):
        if cpapPressure <= 3:
            self.lowPressureLim = 1.0
        elif cpapPressure is 4:
            self.lowPressureLim = 1.8
        elif cpapPressure is 5:
            self.lowPressureLim = 2.5
        elif cpapPressure is 6:
            self.lowPressureLim = 3.3
        elif cpapPressure is 7:
            self.lowPressureLim = 4.0
        elif cpapPressure is 8:
            self.lowPressureLim = 4.8
        elif cpapPressure is 9:
            self.lowPressureLim = 5.5
        elif cpapPressure is 10:
            self.lowPressureLim = 6.3
    
    def getNewData(self):
        ## TO USE WITH COMPUITER FOR DEBUGGING ONLY
        #return random.uniform(1.0,10.0)

        # TO USE WITH PRESSURE SENSOR
        curPressureTicks = self.readadc(self.potentiometer_adc, self.SPICLK, self.SPIMOSI, self.SPIMISO, self.SPICS)
        curPressureV = (self.maxV*curPressureTicks) / self.numTicks;
        conversionV2P = (self.maxPressure - self.zeroPressure)/(self.maxPressureV - self.zeroPressureV);
        curPressure = (curPressureV-self.zeroPressureV)*conversionV2P;
        curPressureCorrected = curPressure - self.offset
        
        return curPressureCorrected

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
        self.B_info.grid(row=0,column=0,padx=10,pady=10,sticky=NE)


    def homePage(self):
        self.endProcess()
        self.clear()
        self.L_oxydasBig.grid(row=1,padx=230,pady=25,sticky=N)
        self.B_calibrate.grid(row=2,column=0,padx=150,pady=25,sticky=W)
        self.B_monitor.grid(row=2,column=0,padx=150,pady=25,sticky=E)
    
    def infoPage(self):
        self.endProcess()
        self.clear()
        self.L_oxydas.grid(row=0,padx=310,pady=25,sticky=N)
        self.L_oxydas.config(fg=self.blue,bg="white")

        self.L_infoSetPressure.grid(row=1,padx=20,pady=20,sticky=W)
        self.L_infoSetPressure.config(bg="white")
        self.L_infoSetPressureVal.grid(row=1,pady=20)
        self.L_infoSetPressureVal.config(text = self.setPressure,bg="white")
        self.B_infoSetPressureEdit.grid(row=1,padx=20,pady=20,sticky=E)

        self.L_infoSetFlowRate.grid(row=2,padx=20,pady=20,sticky=W)
        self.L_infoSetFlowRate.config(bg="white")
        self.L_infoSetFlowRateVal.grid(row=2,pady=20)
        self.L_infoSetFlowRateVal.config(text=self.setFlowRate,bg="white")
        self.B_infoSetFlowRateEdit.grid(row=2,padx=20,pady=20,sticky=E)

        self.L_infoPhoneNum.grid(row=3,padx=20,pady=20,sticky=W)
        self.L_infoPhoneNum.config(bg="white")
        self.L_infoPhoneNumVal.grid(row=3,pady=20)
        self.L_infoPhoneNumVal.config(text=self.phoneNum,bg="white")
        self.B_infoPhoneNumEdit.grid(row=3,padx=20,pady=20,sticky=E)
    
    def enterPhoneNumPage(self):
        self.endProcess()
        self.clear()
        self.L_oxydas.grid(row=0,padx=310,pady=25,sticky=N)
        self.L_oxydas.config(fg=self.blue,bg="white")

        self.L_enterPhoneNum.grid(row=1,pady=40)
        self.L_enteredPhoneNum.grid(row=2)
        #print("showing phone num")
        self.B_enterPhoneNum.grid(row=3,pady=40)
        
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
        
        self._job = self.top.after(300,self.enterPhoneNumPage)

    def getStatus(self, currentPressure, lowPressureLim, highPressureLim):
        # Cannula in
        if currentPressure > lowPressureLim and currentPressure < highPressureLim:
            return 0
        # Cannula out
        elif currentPressure < lowPressureLim:
            return 1
        # High pressure
        elif currentPressure > highPressureLim:
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
     
        if (status == 0):
            statusText = "In range"
        elif (status == 1):
            statusText = "Low pressure"
        else:
            statusText = "High pressure"
        

        self.L_bcpapPressure.grid(row=1)

        if self.currentPressure >= 10.0:
            currentPressureFormatted = str(round(self.currentPressure))
        else:
            currentPressureFormatted = str(round(self.currentPressure,1))
        timePressureMeasured = time.time() - self.start
        self.file.write("\n" + str("{:.3f}".format(timePressureMeasured)) + "\t" + "Current pressure measured: " + "\t" + currentPressureFormatted + "\t" + statusText)
        L_currentPressure = Label(top, text = currentPressureFormatted,font=("Helvetica", 85))
        L_currentPressure.grid(row=2,column=0,pady=10)

        self.L_pressureUnits.grid(row=2,column=0,padx=85,pady=25,sticky=SE)

        myWidgets = [self.top,self.L_oxydas,self.L_bcpapPressure,L_currentPressure,self.L_pressureUnits];

        #print(self.timeElapsed)

        if (status == 0):
            for wid in myWidgets:
                wid.config(bg=self.green)
            L_status = Label(top, text = "Cannula In",font=("Helvetica", 30))
            L_status.config(bg=self.green)
        # when cannula comes out
        elif (status == 1):
            if (self.alarmActivation is True):
                # check if the nurse acknowledged the message only if not already in idle mode
                if (self.startIdleMode is False):
                    self.checkAlertAcknowledged()
                    #print("text acknowledged is ", str(self.textAcknowledged))
                # if nurse hasn't acknowledged the message
                if (self.textAcknowledged is False):
                    self.idleModeTimeStarted = 0
                    self.idleModeTimeElapsed = 0
                    #print("Text not seen yet, need to start buzzing")
                
                    # start buzzing
                    BuzzThread = Thread(target=self.buzz)
                    BuzzThread.start()
                    # if a text hasn't been sent or it has been a minute, send a text
                    if (self.timeSent == 0 or self.timeElapsed > self.sendTextDelay):
                        #print("Text sent")
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
                        #print("STAAAAAART")
                        self.startIdleMode = True
                        self.textAcknowledged = True
                        self.idleModeTimeStarted = time.time()
                    elif (self.idleModeTimeElapsed < self.idleModeDuration):
                        pass
                        #print("In IDLE MODE: ", str(self.idleModeTimeElapsed))
                    elif (self.idleModeTimeElapsed >= self.idleModeDuration):
                        #print("Idle mode complete")
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
            else:
                pass
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
        self.L_oxydas.grid(row=0,padx=310,pady=25,sticky=N)
        self.B_activate.grid(row=4,pady=20)
        
        self.pressureGuiUpdate();
        
        self._job = self.top.after(self.refreshRate,self.pressureDisplayPage)

    def pressureGuiUpdateCalibration(self):
        self.currentPressure = self.getNewData()
        status = self.getStatus(self.currentPressure, self.lowPressureLim, self.highPressureLim)

        L_bcpapPressure = Label(top, text = "Bubble CPAP Pressure", font=("Helvetica", 25))
        L_bcpapPressure.grid(row=1)

        if self.currentPressure >= 10.0:
            currentPressureFormatted = str(round(self.currentPressure))
        else:
            currentPressureFormatted = str(round(self.currentPressure,1))
        L_currentPressure = Label(top, text = currentPressureFormatted,font=("Helvetica", 40))
        L_currentPressure.grid(row=2,column=0,pady=15)

        L_pressureUnitsCal = Label(top, text = "cm H2O", font=("Helvetica", 20))
        L_pressureUnitsCal.grid(row=2,column=0,padx=220,pady=18,sticky=SE)

        myWidgets = [self.top,self.L_oxydas,L_bcpapPressure,L_currentPressure,L_pressureUnitsCal];

        if (status == 0):
            for wid in myWidgets:
                wid.config(bg=self.green)
            L_status = Label(top, text = "Cannula In",font=("Helvetica", 20))
            L_status.config(bg=self.green)
        elif (status == 1):
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
    
    # water pressure
    def calibrationPage1(self):
        self.endProcess()
        self.clear()
        self.L_oxydas.grid(row=0,padx=310,pady=25,sticky=N)
        self.L_oxydas.config(bg="white")
        self.L_pressureUnits.config(bg="white")
        
        self.L_pressureSet.grid(row=1, pady=20)
        self.L_pressureSetVal.grid(row=2,column=0,pady=40)
        self.L_pressureUnits.grid(row=2,column=0,padx=220,pady=45,sticky=E)
        self.B_pressureSet.grid(row=3,pady=30)
        #print("did this")

           
        # If pressure has not been set yet
        if (not self.pressureIsSet):
            numDigits = len(self.setPressure)
            # Iteration 1
            if (not self.startCalibration):
                self.startCalibration = True
                #print('Starting calibration')
            # Iteration 2 - until the first number is pressed
            elif (numDigits == 0):
                self.newPressureDigit= self.numWriter()
                self.setPressure = "{}{}".format(self.setPressure, self.newPressureDigit)
                self.setPressureNum = int(self.setPressure)
                #print(self.setPressure)
                self.highPressureLim = self.setPressureNum + self.alarmThreshold
                self.setLowPressureAlertThreshold(self.setPressureNum)
                self.L_pressureSetVal.config(text = self.setPressure)
                if (self.newPressureDigit != "1"):
                    self.pressureIsSet = True
                    timePressureSet = time.time() - self.start
                    self.file.write("\n" + str("{:.3f}".format(timePressureSet)) + "\t" + "CPAP pressure set to: " + "\t" + self.setPressure)
                    #print('Pressure is set!')
                else:
                    pass
            # If first digit entered is 1, the second digit entered is only allowed to be 0
            else:
                self.newPressureDigit = self.numWriter()
                if (self.setPressure != "1" or self.newPressureDigit != "0"):
                    self.newPressureDigit = ""
                    #print("Only 0 allowed after 1")
                else:
                    self.pressureIsSet = True
                    timePressureSet = time.time() - self.start
                    self.file.write("\n" + str("{:.3f}".format(timePressureSet)) + "\t" + "CPAP pressure set to: " + "\t" + self.setPressure)
                    self.setPressure = "{}{}".format(self.setPressure, self.newPressureDigit)
                    self.setPressureNum = int(self.setPressure)
                    #print(self.setPressure)
                    self.highPressureLim = self.setPressureNum + self.alarmThreshold
                    self.setLowPressureAlertThreshold(self.setPressureNum)
                    self.L_pressureSetVal.config(text = self.setPressure)
                    
                    #print('Pressure is set!')
        else:
            pass
        
        self._job = self.top.after(self.refreshRate, self.calibrationPage1)
        
    # oxygen flow rate
    def calibrationPage2(self):
        self.endProcess()
        self.clear()
        self.L_oxydas.grid(row=0,padx=310,pady=25,sticky=N)
        self.L_oxydas.config(bg="white")
        self.L_flowRateUnits.config(bg="white")
        
        self.L_flowRateSet.grid(row=1, pady=20)
        self.L_flowRateSetVal.grid(row=2,column=0,pady=40)
        self.L_flowRateUnits.grid(row=2,column=0,padx=220,pady=45,sticky=E)
        self.B_flowRateSet.grid(row=3,pady=30)
        #print("did this")

           
        # If pressure has not been set yet
        if (not self.flowRateIsSet):
            numDigits = len(self.setFlowRate)
            # Iteration 1
            if (not self.startEnterFlowRate):
                self.startEnterFlowRate = True
                #print('Starting calibration')
            # Iteration 2 - until the first number is pressed
            elif (numDigits == 0):
                self.newFlowRateDigit= self.numWriter()
                self.setFlowRate = "{}{}".format(self.setFlowRate, self.newFlowRateDigit)
                self.setFlowRateNum = int(self.setFlowRate)
                self.openCircuitPressureAdjust(self.setFlowRateNum)
                #print(self.offset)
                self.L_flowRateSetVal.config(text = self.setFlowRate)
                if (self.newFlowRateDigit != "1"):
                    self.flowRateIsSet = True
                    timeFlowRateSet = time.time() - self.start
                    self.file.write("\n" + str("{:.3f}".format(timeFlowRateSet)) + "\t" + "Oxygen flow rate set to: " + "\t" + self.setFlowRate)
                    #print('Flow rate is set!')
                else:
                    pass
            # If first digit entered is 1, the second digit entered is only allowed to be 0
            else:
                self.newFlowRateDigit = self.numWriter()
                if (self.setFlowRate != "1" or self.newFlowRateDigit != "0"):
                    self.newFlowRateDigit = ""
                    #print("Only 0 allowed after 1")
                else:
                    self.flowRateIsSet = True
                    timeFlowRateSet = time.time() - self.start
                    self.file.write("\n" + str("{:.3f}".format(timeFlowRateSet)) + "\t" + "Oxygen flow rate set to: " + "\t" + self.setFlowRate)
                    self.setFlowRate = "{}{}".format(self.setFlowRate, self.newFlowRateDigit)
                    self.setFlowRateNum = int(self.setFlowRate)
                    self.openCircuitPressureAdjust(self.setFlowRateNum)
                    #print(self.offset)
                    self.L_flowRateSetVal.config(text = self.setFlowRate)
                    #print('Pressure is set!')
        else:
            pass
        
        self._job = self.top.after(self.refreshRate, self.calibrationPage2)
    
    def testCalibrationSet(self):
        self.endProcess()
        self.clear()
        self.L_oxydas.grid(row=0,padx=310,pady=25,sticky=N)

        self.pressureGuiUpdateCalibration();

        self.C_test.grid(row=4,sticky=S)
        self.L_testSet.grid(row=4,padx=40,pady=50,sticky=SW)
        self.B_testSet.grid(row=4,padx=50,pady=50,sticky=E)

        self._job = self.top.after(self.refreshRate,self.testCalibrationSet)
    
    def testCalibrationLow(self):
        self.endProcess()
        self.clear()
        self.L_oxydas.grid(row=0,padx=310,pady=25,sticky=N)

        self.pressureGuiUpdateCalibration();
        
        self.C_test.grid(row=4,pady=0,sticky=S)
        self.L_testLow.grid(row=4,padx=40,pady=35,sticky=SW)
        self.B_testLow.grid(row=4,padx=50,pady=35,sticky=E)
        

        self._job = self.top.after(self.refreshRate,self.testCalibrationLow)

    def testCalibrationHigh(self):
        self.endProcess()
        self.clear()
        self.L_oxydas.grid(row=0,padx=310,pady=25,sticky=N)

        self.pressureGuiUpdateCalibration();

        self.C_test.grid(row=4,pady=0,sticky=S)
        self.L_testHigh.grid(row=4,padx=40,pady=35,sticky=SW)
        self.B_testHigh.grid(row=4,padx=50,pady=35,sticky=E)

        self._job = self.top.after(self.refreshRate,self.testCalibrationHigh)
    
    def on_closing(self):
        GPIO.output(self.BUZZER,0)
        self.ssh.stdin.close()
        self.top.destroy()
        self.file.close()
        
    def main(self):
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
        self.ssh = subprocess.Popen([self.command], shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(self.ssh.communicate())
            
        self.top.configure(background = "white")
        self.B_home.grid(row=0,column=0,padx=10,pady=10,sticky=NW)
        self.B_info.grid(row=0,column=0,padx=10,pady=10,sticky=NE)
        self.L_oxydasBig.grid(row=1,padx=230,pady=25,sticky=N)
        self.B_calibrate.grid(row=2,column=0,padx=150,pady=25,sticky=W)
        self.B_monitor.grid(row=2,column=0,padx=150,pady=25,sticky=E)
        
        self.file = open(self.outputTextFile,"w")
        self.start = time.time()
        

top = Tk()
top.geometry("800x450")
app = App(top)
top.after(1000,app.main)
top.protocol("WM_DELETE_WINDOW", app.on_closing)
top.mainloop()
