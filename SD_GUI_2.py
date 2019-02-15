# Attempt 2 for Oxy-Das GUI
# Multiple pages

import tkinter
from tkinter import *
import time
import random

class App:
    def __init__(self,master):
        self.top = master

        # Parameters
        self.canvasDim = (480,320)
        self.alarmThreshold = 2.0
        self._job = None

        # Variable initialization

        # Dummy values
        #self.setPressure = '5'
        #self.currentPressure = 5
        #self.highPressureLim = 7
        #self.lowPressureLim = 3
        #self.phoneNum = '7342337513'

        self.setPressure = StringVar()
        self.currentPressure = DoubleVar()
        self.highPressureLim = self.currentPressure.get() + self.alarmThreshold
        self.lowPressureLim = self.currentPressure.get() - self.alarmThreshold
        self.phoneNum = StringVar()


        # widgets
        #self.B_clear = Button(top, text="Clear", bd=5, relief=RAISED, command=self.clear)

        # On every page
        self.B_home = Button(top, text="Home", bd=5, relief=RAISED, command=self.homePage)
        self.L_oxydas = Label(top, text="Oxy-Das", fg = "blue", bg="yellow", font="Verdana 12 bold")

        # Home page
        self.B_calibrate = Button(top, text="Calibrate", bd=5, relief=RAISED, command=self.calibrationPage1)
        self.B_monitor = Button(top, text="Start Monitoring", bd=5, relief=RAISED, command=self.enterPhoneNumPage)

        # Enter phone number
        self.L_enterPhoneNum = Label(top, text = "Enter Phone Number")
        self.E_enterPhoneNum = Entry(top, bd = 1, justify=CENTER, textvariable=self.phoneNum)
        self.B_enterPhoneNum = Button(top, text = "Enter",bd=5, relief=RAISED, command=self.pressureDisplayPage)

        # Pressure Display Page
        self.L_bcpapPressure = Label(top, text = "Bubble CPAP Pressure")
        self.L_units = Label(top, text = "cm H2O")
        #self.L_cannulaOut = Label(top, text = "Cannula Out!")
        #self.L_highPressure = Label(top, text = "High Pressure!")

        # Calibration Page 1
        self.L_pressureSet = Label(top, text = "Enter pressure set in bubble CPAP system (cm H2O)")
        self.E_pressureSet = Entry(top, bd = 1, justify=CENTER, textvariable=self.setPressure)
        self.B_pressureSet = Button(top, text = "Enter",bd=5, relief=RAISED, command=self.testCalibrationLow)

        # Test Calibration
        self.L_test = Label(top, text = "Test device function.")

        # Test Calibration Low
        self.L_testLow = Label(top, text = "Decrease the pressure.")
        self.B_testLow = Button(top, text = "Appropriate Device Response",bd=5, relief=RAISED, command=self.testCalibrationHigh)

        # Test Calibration High
        self.L_testHigh = Label(top, text = "Increase the pressure.")
        self.B_testHigh = Button(top, text = "Appropriate Device Response",bd=5, relief=RAISED, command=self.homePage)


        # MAIN PROGRAM
        # self.B_clear.grid(row=1)
        self.B_home.grid(row=0)
        self.L_oxydas.grid(row=1)
        self.B_calibrate.grid(row=2)
        self.B_monitor.grid(row=3)

    def getNewData(self):
        return random.uniform(1.0,10.0)

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

    def endProcess(self):
        if self._job is not None:
            self.top.after_cancel(self._job)
            self._job = None

    def clear(self):
        widgetsList = self.top.grid_slaves()
        for widget in widgetsList:
            widget.grid_remove()
        self.top.configure(background = "white")

    def homePage(self):
        self.endProcess()
        self.clear()
        self.B_home.grid(row=0)
        self.L_oxydas.grid(row=1)

        self.B_calibrate.grid(row=2)
        self.B_monitor.grid(row=3)

    def enterPhoneNumPage(self):
        self.clear();
        self.B_home.grid(row=0)
        self.L_oxydas.grid(row=1)

        self.L_enterPhoneNum.grid(row=2)
        self.E_enterPhoneNum.grid(row=3)
        self.B_enterPhoneNum.grid(row=4)

    def pressureGuiUpdate(self):
        self.currentPressure = self.getNewData()
        status = self.getStatus(self.currentPressure, self.lowPressureLim, self.highPressureLim)

        self.L_bcpapPressure.grid(row=2)

        L_currentPressure = Label(top, text = str(round(self.currentPressure,2)))
        L_currentPressure.grid(row=3,column=0)

        self.L_units.grid(row=3,column=1)


        if (status == 1):
            self.top.config(bg="green")
            L_status = Label(top, text = "Cannula In")
        elif (status == 2):
            self.top.config(bg="red")
            L_status = Label(top, text = "Cannula Out")
        else:
            self.top.config(bg="orange")
            L_status = Label(top, text = "Tubing Kinked")

        L_status.grid_remove()
        L_status.grid(row=4)

    def pressureDisplayPage(self):
        self.clear()
        self.B_home.grid(row=0)
        self.L_oxydas.grid(row=1)

        self.pressureGuiUpdate();

        self._job = self.top.after(1000,self.pressureDisplayPage)

    def calibrationPage1(self):
        self.clear()
        self.B_home.grid(row=0)
        self.L_oxydas.grid(row=1)

        self.L_pressureSet.grid(row=2)
        self.E_pressureSet.grid(row=3)
        self.B_pressureSet.grid(row=4)

    def testCalibrationLow(self):
        self.clear()
        self.B_home.grid(row=0)
        self.L_oxydas.grid(row=1)

        self.L_testLow.grid(row=5)
        self.B_testLow.grid(row=6)

        self.pressureGuiUpdate();

    def testCalibrationHigh(self):
        self.clear()
        self.B_home.grid(row=0)
        self.L_oxydas.grid(row=1)

        self.L_testHigh.grid(row=5)
        self.B_testHigh.grid(row=6)

        self.pressureGuiUpdate();


top = Tk()
top.geometry("480x320")
app = App(top)
top.after(1000,app.getNewData)
top.mainloop()
