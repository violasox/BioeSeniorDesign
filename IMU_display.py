import Tkinter as tk

class App:
    def __init__(self, master):
        self.root = master
        # Time between updates from IMU, in milliseconds
        self.updateRate = 500
        self.canvasDim = (200, 150)
        self.pitchVal = tk.StringVar()
        self.yawVal = tk.StringVar()
        self.rollVal = tk.StringVar()
        self.xAccelVal = tk.StringVar()
        self.yAccelVal = tk.StringVar()
        self.zAccelVal = tk.StringVar()

        frame = tk.Frame(self.root)
        frame.pack()

        self.dataFrame = tk.Frame(frame)
        self.dataFrame.pack(side=tk.LEFT)
        self.statusCanvas = tk.Canvas(frame, width=self.canvasDim[0], height=self.canvasDim[1])
        self.statusCanvas.pack()

        self.pitchLabel = tk.Label(self.dataFrame, textvariable=self.pitchVal)
        self.pitchLabel.pack(side=tk.TOP)
        self.yawLabel = tk.Label(self.dataFrame, textvariable=self.yawVal)
        self.yawLabel.pack(side=tk.TOP)
        self.rollLabel = tk.Label(self.dataFrame, textvariable=self.rollVal)
        self.rollLabel.pack(side=tk.TOP)
        self.xAccelLabel = tk.Label(self.dataFrame, textvariable=self.xAccelVal)
        self.xAccelLabel.pack(side=tk.TOP)
        self.yAccelLabel = tk.Label(self.dataFrame, textvariable=self.yAccelVal)
        self.yAccelLabel.pack(side=tk.TOP)
        self.zAccelLabel = tk.Label(self.dataFrame, textvariable=self.zAccelVal)
        self.zAccelLabel.pack(side=tk.TOP)

        self.statusCanvas.create_rectangle(0, 0, self.canvasDim[0], self.canvasDim[1], fill="green")
        self.statusCanvas.create_text(0, 0, text="Cannula in")

    def getNewData(self):
        # Dummy values
        pitch = 5.22
        yaw = 3.18
        roll = -5.32
        xAccel = 2.00
        yAccel = 4.44
        zAccel = 0.00
        self.pitchVal.set("Pitch: {0}".format(pitch))
        self.yawVal.set("Yaw: {0}".format(yaw))
        self.rollVal.set("Roll: {0}".format(roll))
        self.xAccelVal.set("X acceleration: {0}".format(xAccel))
        self.yAccelVal.set("Y acceleration: {0}".format(yAccel))
        self.zAccelVal.set("Z acceleration: {0}".format(zAccel))
        status = self.getStatus()
        if (status):
            self.statusCanvas.create_rectangle(0, 0, self.canvasDim[0], self.canvasDim[1], fill="green")
            self.statusCanvas.create_text(50, 20, text="Cannula in")
        else:
            self.statusCanvas.create_rectangle(0, 0, self.canvasDim[0], self.canvasDim[1], fill="red")
            self.statusCanvas.create_text(50, 20, text="Cannula out")
            
        self.root.after(self.updateRate, self.getNewData)

    def getStatus(self):
        return False

root = tk.Tk()
app = App(root)
root.after(500, app.getNewData)
root.mainloop()
