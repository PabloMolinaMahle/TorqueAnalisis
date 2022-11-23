# -*- coding: utf-8 -*-
"""
Created on Tue Nov  8 12:43:40 2022

@author: M0188337
"""

from textwrap import wrap
import tkinter as tk
import tkinter as tk
import tkinter.filedialog as fd
import csv

class RawDataMessage:
    time: float
    torque: float
    deltaTime: float
    slope: float
    smoothSlope: float
    slope2: float

class Section:
    deltaT: float
    initialTime: float
    finalTime: float
    initialTorque: float
    finalTorque: float
            
class Main():
    def run(self):
        
        # Read data
        data, odometer = self.ReadData()
        
        sections = []
        sections.clear()
        
        # Debug
        # for item in data:
            # print("Time: " + str(item.time) + " Torque: " + str(item.torque))
        
        # Eport Torque data
        self.ExportTorqueData(data)
        
        # Calculate delta time
        self.CalculateDeltaTime(data)
        
        # Calculate first order slope
        self.CalculateSlope(data)
        
        # Calculate second order slope
        self.CalculateSlope2(data)
        
        # Calculate slope smooth
        self.SmoothSlope(data, 30)
        
        # Analize and export odometer data
        self.AnalizeOdometer(odometer)
        
        # Demographic torque
        self.DemograficTorque(data)
        
        # Analice data to find sections
        # self.BuscarTramos(data, sections, 0)
        
        # Show section statistics
        # self.ShowSectionStats(sections)
        
        # Export data
        # self.ExportToCsvBasic(data)
        
        # Section statistics
        self.SimulateStrength(data)
        
    def AnalizeOdometer(self, odometer):
        
        if len(odometer) > 2:
            
            f = open('Export\Odometer.csv', 'w', newline='')
            writer = csv.writer(f, delimiter =';')
            
            print("File odometer: " + str(f) + "  " + str(f.name))
            
            headder = ["Initial odometer", "Final odometer"]
            writer.writerow(headder)
            
            print("Odometer lenght: " + str(len(odometer)))
            row = [str(odometer[0]).replace(".", ","), str(odometer[len(odometer) - 1]).replace(".", ",")]
            writer.writerow(row)
               
            f.close()
        
    def ExportTorqueData(self, data):
        
        f = open('Export\Torque.csv', 'w', newline='')
        writer = csv.writer(f, delimiter =';')
        
        print("File torque analisis: " + str(f) + "  " + str(f.name))
        
        headder = ["Torque"]
        writer.writerow(headder)
        
        for currData in data:
            row = [str(currData.torque).replace(".", ",")]
            writer.writerow(row)
           
        f.close()
    
    def DemograficTorque(self, data):
        
        TorqueGroups = []
        
        for i in range(0, 30, 1):
            TorqueGroups.append(0)
        
        for item in data:
            index = int(item.torque/10)
            # print("Index: " + str(index) + " Original: " + str(item.torque))
            TorqueGroups[index] += 1
            
        f = open('Export\Demographic_Torque.csv', 'w', newline='')
        writer = csv.writer(f, delimiter =';')
        
        print("File demographic analisis: " + str(f) + "  " + str(f.name))
        
        headder = ["Group", "Count"]
        writer.writerow(headder)
        
        for j in range(0, 30, 1):
            row = ["(" + str(10*j) + ", " + str(10*(j + 1)) + ")", str(TorqueGroups[j])]
            writer.writerow(row)
           
        f.close()     
    
    def SimulateStrength(self, data):
        
        sections = []
        
        for s in range(30, 31, 5):
            sections.clear()
            self.SmoothSlope(data, 30)
            for f in range(10, 11, 2):
                # print("s: " + str(s))
                sections.clear()
                self.BuscarTramos(data, sections, f)
                # self.GuardarSecciones(data, sections, s, f)
        
        self.GuardarSeccionesCSV(sections)
            
    def GuardarSecciones(self, data, sections, s, f):
        
        file1 = open("Export\Sections.txt","a")
        
        # Headder
        # file1.write("Slope smooth strength: " + str(s) + " previous items used for average" + " Filter: " + str(f) + "torque difference" + "\n")
        
        # Summary
        file1.write("Summary: Smooth: " + str(s) + " Filter: " + str(f) + " => " + str(len(sections)) + " sections\n")
        
        # file1.write("\n")
        # Data
        for section in sections:
            file1.write("Time : " + str(section.initialTime) + " | " + str(section.finalTime) + " Torque: " + str(section.initialTorque) + " | " + str(section.finalTorque) + " SmoothDeltaT: " + str(section.deltaT) + "\n")

        # file1.write("\n")
        
        file1.close()
        
    def GuardarSeccionesCSV(self, sections):
            
        f = open('Export\sections.csv', 'w', newline='')
        writer = csv.writer(f, delimiter =';')
        
        print("File: " + str(f) + "  " + str(f.name))
        
        headder = ["InitialTime", "FinalTime", "InitialTorque", "FinalTorque", "TorqueDiff", "DeltaT", "ThroughZero"]
        writer.writerow(headder)
        
        for section in sections:
            
            goThroughZero = 0
            
            if section.initialTorque > 10 and section.finalTorque <= 2:
                goThroughZero = 1
            else:
                goThroughZero = 0
            
            row = [str(section.initialTime).replace(".", ","), str(section.finalTime).replace(".", ","), str(section.initialTorque).replace(".", ","), str(section.finalTorque).replace(".", ","), str(abs(section.finalTorque - section.initialTorque)).replace(".", ",") ,str(section.deltaT).replace(".", ","), str(goThroughZero)]
            writer.writerow(row)
           
        f.close()
        
    def BuscarTramos(self, data, sections, minTorque):
        # Recorre el vector de data
        i = 0
        
        while (i < len(data)):
            i = self.CreateSection(data, i, sections, minTorque)
            # print("i: " + str(i))
        
    def CreateSection(self, data, startIndex, sections, minTorque):
        # Set initial variables
        currIndex = startIndex
        finalTorque = 0.0
        finalTime = 0.0
        initialTime = data[currIndex].time
        initialTorque = data[currIndex].torque
        
        # print("Condition: " + str(data[currIndex].smoothSlope) + " bool: " + str((data[currIndex].smoothSlope > 0)))
        
        if(currIndex < len(data) and data[currIndex].smoothSlope >= 0):
            while(currIndex < len(data) and data[currIndex].smoothSlope >= 0):
                finalTorque = data[currIndex].torque
                finalTime = data[currIndex].time
                currIndex += 1
        elif (currIndex < len(data) and data[currIndex].smoothSlope < 0):
            while(currIndex < len(data) and data[currIndex].smoothSlope < 0):
                finalTorque = data[currIndex].torque
                finalTime = data[currIndex].time
                currIndex += 1
            
        # Create section
        currSection = Section()
        currSection.initialTime = initialTime
        currSection.finalTime = finalTime
        currSection.initialTorque = initialTorque
        currSection.finalTorque = finalTorque
        
        if(finalTime != initialTime):
            currSection.deltaT = (float(finalTorque) - float(initialTorque))/(float(finalTime) - float(initialTime))
        else:
            currSection.deltaT = 0
        
        # Filter sections
        if abs(currSection.finalTorque - currSection.initialTorque) > minTorque:
            # print("Tramo aceptado")
            sections.append(currSection)
        
        # print("Time : " + str(currSection.initialTime) + " | " + str(currSection.finalTime) + " Torque: " + str(currSection.initialTorque) + " | " + str(currSection.finalTorque) + " deltaT: " + str(currSection.deltaT))
        
        # print("CurrIndex: " + str(currIndex))
        
        return currIndex
    
    def ShowSectionStats(self, sections):
        
        print("Total sections: " + str(len(sections)))
        
        index = 0
        
        for section in sections:
            print("Section: " + str(index) + " time: " + str(section.initialTime) + " | " + str(section.finalTime) + " torque: " + str(section.initialTorque) + " | " + str(section.finalTorque))
            index += 1
        
    def ExportToStimulus(self, data):
        
        f = open('Export\export.csv', 'w', newline='')
        writer = csv.writer(f, delimiter =';')
        
        headder = ["time", "Wbielas", "Tbielas", "modulation" , "Speed", "Voltaje", "c", "extra"]
        writer.writerow(headder)
        
        for item in data:
            row = [str(item.deltaTime), 0.0, str(item.torque), 0.0, 0.0, 0.0, 0.0]
            writer.writerow(row)
           
        f.close()
    
    
    def ExportToCsvBasic(self, data):
        
        f = open('Export\export.csv', 'w', newline='')
        writer = csv.writer(f, delimiter =';')
        
        print("File: " + str(f) + "  " + str(f.name))
        
        headder = ["Time", "Torque", "DeltaTime", "Slope", "Slope2"]
        writer.writerow(headder)
        
        for item in data:
            row = [str(item.time).replace(".", ","), str(item.torque).replace(".", ","), str(item.deltaTime).replace(".", ","), str(item.slope).replace(".", ","), str(item.slope2).replace(".", ",")]
            writer.writerow(row)
           
        f.close()
    
    def CalculateDeltaTime(self, data):
        
        firstElement = True
        currTimeDelta = 0.0
        prevTime = 0.0
        
        for item in data:
            if firstElement:
                currTimeDelta = 0.0
                firstElement = False
                prevTime = float(item.time)
            else:
                currTimeDelta = float(item.time)-float(prevTime)
                prevTime = float(item.time)
                
            item.deltaTime = currTimeDelta
        
    def CalculateSlope(self, data):
        prevTime = 0.0
        prevTorque = 0.0
        firstElement = True
        
        for item in data:
            tempDelta = 0
            if firstElement:
                tempDelta = 0.0
                firstElement = False
            else:
                tempDelta = (float(item.torque)-float(prevTorque))/(float(item.time)-float(prevTime))
                # print("dT= " + str(float(item.torque)-float(prevTorque)) + " dt= " + str(float(item.time)-float(prevTime)) + " dT/dt= " + str(tempDelta))
            
            item.slope = tempDelta
            
            prevTime = item.time
            prevTorque = item.torque
    
    def CalculateSlope2(self, data):
        prevTime = 0.0
        prevSlope = 0.0
        firstElement = True
        
        for item in data:
            tempDelta = 0
            if firstElement:
                tempDelta = 0.0
                firstElement = False
            else:
                tempDelta = (float(item.slope)-float(prevSlope))/(float(item.time)-float(prevTime))
                # print("dT= " + str(float(item.torque)-float(prevTorque)) + " dt= " + str(float(item.time)-float(prevTime)) + " dT/dt= " + str(tempDelta))
            
            item.slope2 = tempDelta
            
            prevTime = item.time
            prevSlope = item.slope
    
    def SmoothSlope(self, data, strength):
        
        for i in range(0, len(data), 1):
            if i == 0:
                data[i].smoothSlope = data[i].slope
            else:
                data[i].smoothSlope = self.MovilAverage(data, strength, i)
    
    def MovilAverage(self, data, strength, currIndex):
    
        currStrength = 0
        
        # Calcula la longitud total
        if(currIndex >= strength):
            currStrength = strength
        else:
            currStrength = currIndex
        
        sumatory = 0
        
        # print("Average indexes: " + str(currIndex - currStrength) + " end: " + str(currIndex))
        
        # Calculate sumatory
        for i in range(currIndex - currStrength, currIndex, 1):
            
            sumatory += data[i].slope   
        
        # Calculate average
        average = sumatory/currStrength
        
        return average
    
    def ReadData(self):

        root = tk.Tk()

        filetypes = (('text files', '*.txt'), ('All files', '*.*'))
        fileNames = fd.askopenfilenames(parent=root, title='Select route files', initialdir='/', filetypes=filetypes)
        
        root.destroy()
        
        concatenatedData = []
        concatenatedData.clear()
        
        concatenatedOdometer = []
        concatenatedOdometer.clear()
        
        for file in fileNames:
            print("File name: " + str(file))
            currentData, currentOdometer = self.ReadAndAnalizeFile(file)
            print("Current data lenght: " + str(len(currentData)))
            concatenatedData += currentData
            concatenatedOdometer += currentOdometer
            
        print("Complete data lenght: " + str(len(concatenatedData)))
            
        return concatenatedData, concatenatedOdometer
             
    
    def ReadAndAnalizeFile(self, file_path):
        
        # Debug
        # print("File datalogger: " + file_path)
        
        # Open file
        data = open(file_path, "r", encoding="utf8")
        
        # Read file data
        datos = data.readlines()
        
        # List to store splited data
        splitedData = []
        splitedData.clear()
        
        # List to store odometer data
        odometerData = []
        odometerData.clear()
        
        # Start reading data and spliting
        for item in datos:
            # Check if is a line to process
            if item[0] != "#" and item[0] != "T" and item[0] != "" and item[0] != " " and item[0] != "\n":
                
                # First split
                # print("Line: " + item)
                time, messageType, can, trace = item.replace("\n", "").split(";")
                
                # Debug
                # print("Can: " + str(can) + " Trace: " + str(trace))
                
                # Filter Torque sensor 1 messages                
                if can == "100":
                    
                    # print("Can: " + str(can) + " Trace: " + str(trace))
                    
                    # initzialice new raw data variable
                    currRawDatamessage = RawDataMessage()
    
                    # process time
                    #self.currRawDatamessage.time = self.processTime(self.time)
                    currRawDatamessage.time = self.processTime(time)
                    
                    # process can message and extract torque info
                    currRawDatamessage.torque = self.GetTorqueValue(trace)
                    
                    # append data
                    splitedData.append(currRawDatamessage)
                    
                    # print("Torque: " + str(currRawDatamessage.torque))
                if can == "201":
                    
                    # process can message and extract odometer info
                    odometer = self.GetOdometerValue(trace)
                    
                    # Debug
                    # print("Odometer value: " + str(odometer))
                    
                    # append data
                    odometerData.append(odometer)
                    
                    # print("Torque: " + str(currRawDatamessage.torque))
        # Debug
        # for item in self.splitedData:
        #     print(item)
            
        return splitedData, odometerData
    
    # Method to process time variable
    def processTime(self, timeToProcess):

        lenght = len(timeToProcess)
        
        # print("Time to process: " + timeToProcess)
        
        mili = timeToProcess[lenght - 3:lenght]
        
        # print("Mili: " + mili)
        
        second = timeToProcess[lenght - 5:lenght - 3]
        
        # print("second: " + second)
        
        minute = timeToProcess[lenght - 7:lenght - 5]
        
        # print("minute: " + minute)
        
        hour = timeToProcess[lenght - 9:lenght - 7]
        
        # prisnt("hour: " + hour)
        
        # day = timeToProcess[lenght - 11:lenght - 9]
        
        # print("day: " + day)
        
        # year = timeToProcess[:4]
        
        # month = timeToProcess[4:6]
        
        # day = timeToProcess[6:8]
        
        # hour = timeToProcess[8:10]
        
        # minute = timeToProcess[10:12]
        
        # second = timeToProcess[12:14]
        
        # mili = timeToProcess[4:6]
        
        dateAndTime = str(int(second) + int(minute)*60 + int(hour)*3600) + "." + str(mili)
        
        # Debug
        # print("Date and time: " + dateAndTime)
        
        return dateAndTime
    
    def GetTorqueValue(self, message):
        
        # print("Message: " + message)
        
        orderedMessage = self.PrepareMessage(message)
        
        # print("orderedMessage: " + orderedMessage)
        
        variableRawData = self.VariableDataFromMessage(orderedMessage, 20, 16)

        # print("Ordered message: " + orderedMessage + " Raw variable: " + variableRawData)

        # Convert to dec
        decResult = int(variableRawData, 2)
        # Debug
        # print("Extract Dec: " + str(decResult))
        
        # Apply gain
        decResult *= float(0.01)
        
        # Apply offset
        decResult += float(-327.67)
        
        # Debug
        # print ("Processed Dec: " + str(decResult))
        
        return decResult
    
    def GetOdometerValue(self, message):
        
        # print("Message: " + message)
        
        orderedMessage = self.PrepareMessage(message)
        
        # print("orderedMessage: " + orderedMessage)
        
        variableRawData = self.VariableDataFromMessage(orderedMessage, 0, 32)

        # print("Ordered message: " + orderedMessage + " Raw variable: " + variableRawData)

        # Convert to dec
        decResult = int(variableRawData, 2)
        # Debug
        # print("Extract Dec: " + str(decResult))
        
        # Apply gain
        decResult *= float(0.001)
        
        # Apply offset
        decResult += float(0)
        
        # Debug
        # print ("Processed Dec: " + str(decResult))
        
        return decResult
    
    def PrepareMessage(self, message):
        # Get message lenght
        messageLength = 4*len(message)
        
        # print("Message lenght: " + str(messageLength) + " lenght: " + str(len(message)) + " Message: " + str(message))
        
        # print("Binary lenght: " + str(len(message)) + " str: " + str(message))
        
        # Convert HEX message to BIN and remove "0b" characters
        messageBinary = bin(int(message,16))[2:]
        
        # print("Bin message: " + str(messageBinary) + " lenght: " + str(len(messageBinary)))
        
        # Fill with 0 on the left to the message lenght
        messageBinaryString = messageBinary.zfill(messageLength)
        # print("zfill lenght: " + str(len(messageBinaryString)) + " str: " + str(messageBinaryString))
        
        # Fill with 0 on the right to 64 bit lenght
        
        # print("Message zero left: " + messageBinaryString + " Lenght: " + str(len(messageBinaryString)))
        messageBinaryString =  messageBinaryString.ljust(64, '0')
        # print("Message zero right: " + str(messageBinaryString) + " lenght: " + str(len(messageBinaryString)))
        
        # print("Message zero complete: " + messageBinaryString + " Force zeros: " + messageBinaryString.ljust(64, '0'))
        
        # Split number in groups of 8 (1 bytes) and return it
        byteList = wrap(messageBinaryString, 8)
        
        # Debug
        # for byte in byteList:
        #     print("Byte: " + str(byte))
        
        # Invert bytes and concatenate
        
        orderedMessage = ""
        
        for byte in byteList:
            orderedMessage += str(byte[::-1])
            
        # Debug
        # print("Ordered message: " + orderedMessage)
                
        # print("Message 1: " + DecodeAlgorithm.VariableDataFromMessage(orderedMessage, 0, 8))
        # print("Message 2: " + DecodeAlgorithm.VariableDataFromMessage(orderedMessage, 20, 16))
        # print("Message 3: " + DecodeAlgorithm.VariableDataFromMessage(orderedMessage, 36, 10))
        
        return orderedMessage
    
    def VariableDataFromMessage(self, orderedMessage, bitpos, lenght):
        
        # print("Message: " + orderedMessage + " Bitpos: " + str(bitpos) + " lenght: " + str(lenght))
        
        parcialMessage = orderedMessage[bitpos:(bitpos+lenght)]
        
        # print("Variable: " + parcialMessage[::-1])
                
        return parcialMessage[::-1]
    
    
    
if __name__ == '__main__':
    Main().run()
    
