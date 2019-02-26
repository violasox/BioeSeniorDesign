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
import random
from twilio.rest import Client
import os
from dotenv import Dotenv
import subprocess
import sys
from threading import Thread
from multiprocessing.pool import ThreadPool

import RPi.GPIO as GPIO

class App:
    def __init__(self,master):
        self.top = master

        # Parameters
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
    
        self.setPressurePool = ThreadPool(processes=1)
    
        self.setPressure = "0"
        self.currentPressure = DoubleVar()
        self.highPressureLim = self.currentPressure.get() + self.alarmThreshold
        self.lowPressureLim = self.currentPressure.get() - self.alarmThreshold
        self.phoneNumArray = [0,0,0,0,0,0,0,0,0,0]
        self.phoneNumStr = ""


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
        self.T_enterPhoneNum = Text(top, height=1,width=12,font=("Helvetica", 20))
        self.B_enterPhoneNum = Button(top, text = "Enter",bd=5, relief=RAISED, padx=15,pady=5,command=self.pressureDisplayPage)
        self.B_enterPhoneNum.config(font=("Helvetica", 15))

        # Pressure Display Page
        self.L_bcpapPressure = Label(top, text = "Bubble CPAP Pressure", font=("Helvetica", 20))
        self.L_units = Label(top, text = "cm H2O", font=("Helvetica", 20))
        #self.L_cannulaOut = Label(top, text = "Cannula Out!")
        #self.L_highPressure = Label(top, text = "High Pressure!")

        # Calibration Page 1
        self.L_pressureSet = Label(top, text = "1. Enter pressure set in bubble CPAP system", font=("Helvetica", 20))
        self.T_pressureSet = Text(top, height=1,width=3,font=("Helvetica", 20))
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
        self.sendTextDelay = 15; # send text every __ seconds
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
        

        # Uncomment for testing purposes
        #self.clear()
        #self.L_oxydas.grid(row=0,padx=175,pady=25,sticky=N)

        #self.pressureGuiUpdate();

        #self._job = self.top.after(1000,self.pressureDisplayPage)


    def getNewData(self):
        return random.uniform(1.0,10.0)

        ## TO USE WITH PRESSURE SENSOR
        #curPressureTicks = self.readadc(self.potentiometer_adc, self.SPICLK, self.SPIMOSI, self.SPIMISO, self.SPICS)
        #curPressureV = (self.maxV*curPressureTicks) / self.numTicks;
        #conversionV2P = (self.maxPressure - self.zeroPressure)/(self.maxPressureV - self.zeroPressureV);
        #curPressure = (curPressureV-self.zeroPressureV)*conversionV2P;
        #return curPressure

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
        print('Got here 3')
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
                        time.sleep(0.5)
                        while(GPIO.input(self.ROW[i])) == 0:
                            pass
                GPIO.output(self.COL[j],1)
    
        print('Got here 4')
        return num


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
        self.clear();
        self.L_oxydas.grid(row=0,padx=175,pady=25,sticky=N)
        self.L_oxydas.config(fg=self.blue,bg="white")

        self.L_enterPhoneNum.grid(row=1,pady=20)
        #self.E_enterPhoneNum.grid(row=2)
        self.B_enterPhoneNum.grid(row=3,pady=20)
        
        tempPhoneStr = ""
        for x in range(10):
            self.phoneNumArray[x]=self.numWriter()
            for k in range(x+1):
                tempPhoneStr += self.phoneNumArray[k]
            self.phoneNumStr = tempPhoneStr
            #print(tempPhoneStr)
            tempPhoneStr = ""
        
        self.T_enterPhoneNum.insert(INSERT, self.phoneNumStr)
        self.T_enterPhoneNum.grid(row=2,column=0)
        
        #print(self.phoneNumStr)
        #print(type(self.phoneNumStr))

    def getStatus(self, currentPressure, lowPressureLim, highPressureLim):
        # Cannula in
        if currentPressure > lowPressureLim and currentPressure < highPressureLim:
            return 1
        # Cannula out
        elif currentPressure < lowPressureLim:
            return 0
        # Tubing kinked
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
        elif (status == 2):
            if (self.timeSent == 0 or self.timeElapsed > self.sendTextDelay):
                #print("Text sent")
                self.sendText()
                self.timeSent = time.time();
            else:
                #print("Passed")
                pass
            for wid in myWidgets:
                wid.config(bg=self.red)
            L_status = Label(top, text = "Low Pressure",font=("Helvetica", 30))
            L_status.config(bg=self.red)
        else:
            for wid in myWidgets:
                wid.config(bg="orange")
            L_status = Label(top, text = "High Pressure",font=("Helvetica", 30))
            L_status.config(bg="orange")

        self.timeElapsed = time.time() - self.timeSent

        L_status.grid_remove()
        L_status.grid(row=3)

    def pressureDisplayPage(self):
        envPhoneNum = "+1" + self.phoneNumStr
        #print(type(envPhoneNum))
        #os.environ['RECV_NUMBER']=envPhoneNum

        self.clear()
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
        self.clear()
        self.L_oxydas.grid(row=0,padx=175,pady=25,sticky=N)
        self.L_oxydas.config(bg="white")
        self.L_units.config(bg="white")

        self.L_pressureSet.grid(row=1, pady=20)

        self.L_units.grid(row=2,column=0,padx=120,sticky=E)
        self.B_pressureSet.grid(row=3,pady=30)
        
        
        
        #async_result = self.setPressurePool.apply_async(self.numWriter)
        #self.setPressure = async_result.get()
        #print(self.setPressure)

        if (not self.startCalibration):
            self.startCalibration = True
            newDigit = ""
            print('Got here')
        else:
            newDigit= self.numWriter()
            print('Got here 2')
        # self.setPressure = self.numWriter()
        #newDigit = self.numWriter()
        self.setPressure = "{}{}".format(self.setPressure, newDigit)
        L_pressureSet = Label(top,text=self.setPressure)
        L_pressureSet.grid(row=2,column=0)
        self.top.after(1000, self.calibrationPage1)
            
        #print(self.setPressure)

        #self.T_pressureSet.insert(INSERT, self.setPressure)
        #self.T_pressureSet.grid(row=2,column=0)
        

    def testCalibrationLow(self):
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




top = Tk()
top.geometry("480x320")
app = App(top)
top.after(1000,app.getNewData)
top.mainloop()
