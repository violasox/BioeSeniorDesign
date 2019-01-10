import Tkinter as tk
import serial
import time

class App:
    def __init__(self, master):
        self.root = master
        # Configurable parameters
        # Time between updates from IMU, in milliseconds
        self.updateRate = 500
        self.canvasDim = (800, 600)
        self.calibrationThreshold = 50
        self.alarmThreshold = 1000
        self.fontSize = 40

        # Variable initialization (don't touch)
        self.pitchVal = tk.StringVar()
        self.yawVal = tk.StringVar()
        self.rollVal = tk.StringVar()
        self.xAccelVal = tk.StringVar()
        self.yAccelVal = tk.StringVar()
        self.zAccelVal = tk.StringVar()
        self.calibrated = False
        self.cannulaOut = False
        self.calibratedRounds = 0
        self.zOffset = 0

        frame = tk.Frame(self.root)
        frame.pack()

        self.dataFrame = tk.Frame(frame, width=self.canvasDim[0], height=self.canvasDim[1])
        self.dataFrame.pack(side=tk.LEFT, fill=None, expand=False)
        self.dataFrame.pack_propagate(False)
        #self.statusFrame = tk.Frame(frame)
        #self.statusFrame.pack(side=tk.LEFT, expand=1)
        #self.statusCanvas = tk.Canvas(self.statusFrame, width=self.canvasDim[0], height=self.canvasDim[1])
        #self.statusCanvas.pack()

        self.pitchLabel = tk.Label(self.dataFrame, textvariable=self.pitchVal, font=("Helvetica", self.fontSize))
        self.pitchLabel.pack(side=tk.TOP, pady=(50,0))
        self.yawLabel = tk.Label(self.dataFrame, textvariable=self.yawVal, font=("Helvetica", self.fontSize))
        self.yawLabel.pack(side=tk.TOP)
        self.rollLabel = tk.Label(self.dataFrame, textvariable=self.rollVal, font=("Helvetica", self.fontSize))
        self.rollLabel.pack(side=tk.TOP)
        self.xAccelLabel = tk.Label(self.dataFrame, textvariable=self.xAccelVal, font=("Helvetica", self.fontSize))
        self.xAccelLabel.pack(side=tk.TOP)
        self.yAccelLabel = tk.Label(self.dataFrame, textvariable=self.yAccelVal, font=("Helvetica", self.fontSize))
        self.yAccelLabel.pack(side=tk.TOP)
        self.zAccelLabel = tk.Label(self.dataFrame, textvariable=self.zAccelVal, font=("Helvetica", self.fontSize))
        self.zAccelLabel.pack(side=tk.TOP)

        #self.statusCanvas.create_rectangle(0, 0, self.canvasDim[0], self.canvasDim[1], fill="green")
        #self.statusCanvas.create_text(0, 0, text="Cannula in")
        self.resetButton = tk.Button(self.dataFrame, text="Reset", command=self.reset, font=("Helvetica", self.fontSize))
        self.resetButton.pack(side=tk.TOP, pady=(50,0))

        self.teensy = serial.Serial('/dev/ttyACM0', 115200)
        print("Established connection with Teensy")

    def getNewData(self):
        # Send any character to get data from teensy
        self.teensy.write('a')
        orientString = self.teensy.readline().split('\t')
        yaw = float(orientString[1])
        pitch = float(orientString[2])
        roll = float(orientString[3])
        accelString = self.teensy.readline().split('\t')
        xAccel = float(accelString[1])
        yAccel = float(accelString[2])
        zAccel = float(accelString[3])
        # Dummy values
        # pitch = 5.22
        # yaw = 3.18
        # roll = -5.32
        # xAccel = 2.00
        # yAccel = 4.44
        # zAccel = 0.00
        self.pitchVal.set("Pitch: {:8.2f}".format(abs(pitch)))
        self.yawVal.set("Yaw: {:8.2f}".format(abs(yaw)))
        self.rollVal.set("Roll: {:8.2f}".format(abs(roll)))
        self.xAccelVal.set("X acceleration: {:8.2f}".format(abs(xAccel)))
        self.yAccelVal.set("Y acceleration: {:8.2f}".format(abs(yAccel)))
        self.zAccelVal.set("Z acceleration: {:8.2f}".format(abs(zAccel - self.zOffset)))
        status = self.getStatus(xAccel, yAccel, zAccel)
        # Cannula in
        if (status == 0):
            self.dataFrame.config(bg="green")
            #self.statusCanvas.create_rectangle(0, 0, self.canvasDim[0], self.canvasDim[1], fill="green")
            #self.statusCanvas.create_text(50, 20, text="Cannula in")
        # IMU calibrating
        elif (status == 1):
            self.dataFrame.config(bg="orange")
            #self.statusCanvas.create_rectangle(0, 0, self.canvasDim[0], self.canvasDim[1], fill="orange")
            #self.statusCanvas.create_text(50, 20, text="IMU calibrating")
        # Cannula out
        elif (status == 2):
            self.dataFrame.config(bg="red")
            #self.statusCanvas.create_rectangle(0, 0, self.canvasDim[0], self.canvasDim[1], fill="red")
            #self.statusCanvas.create_text(50, 20, text="Cannula out")
            
        self.root.after(self.updateRate, self.getNewData)

    def getStatus(self, xAccel, yAccel, zAccel):
        # status = self.teensy.readline()
        if (not self.calibrated):
            if (max((abs(xAccel), abs(yAccel))) < self.calibrationThreshold):
                if self.calibratedRounds > 5:
                    self.calibrated = True
                    self.zOffset = zAccel
                else:
                    self.calibratedRounds += 1
            return 1
        elif (self.cannulaOut):
            return 2
        else:
            maxAccel = max((abs(xAccel), abs(yAccel), abs(zAccel - self.zOffset)))
            if (maxAccel > self.alarmThreshold):
                self.cannulaOut = True
                return 2
            else:
                return 0

    def reset(self):
        self.calibrated = False
        self.cannulaOut = False
        self.zOffset = 0
        self.calibratedRounds = 0

root = tk.Tk()
app = App(root)
root.after(500, app.getNewData)
root.mainloop()
