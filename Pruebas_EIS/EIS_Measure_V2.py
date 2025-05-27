import numpy as np
import pyvisa
import time
import matplotlib.pyplot as plt

class RP7972A():
    """Esta clase pide y mide los datos de la fuente, para luego ser procesados"""
    def __init__(self, rp_USB=None):
        """Define variables de entrada como variables globales en la clase"""

        self.rp_USB=rp_USB
        # FOR INITIALIZATION OF POWER SOURCE (RP7972A)
        rm = pyvisa.ResourceManager()
        devices = rm.list_resources()

        print("Searching for devices...")
        for device in devices:
            try:
                my_instrument = rm.open_resource(str(device))
                device_ID=my_instrument.query('*IDN?')
                if  "RP797" in device_ID:#if the RP7972 is found assign it to rp_USB
                    self.rp_USB=my_instrument
                    print("Found and connected to: "+device_ID)
                    break
                else:#close other devices
                    my_instrument.close()
            except:
                print("no devices were found")
                
        if not self.rp_USB:
                print("No RP7972 power supply was found.")
                rm.close()

        

        
    def measure_voltage(self, measure_time, measure_points):
        """Query the device for voltage points using the MEASure:ARRay:VOLTage[:DC]? command"""
        self.scpi_out(" SENS:SWE:TINT " + str(measure_time) )
        self.scpi_out(" SENS:SWE:POIN " + str(measure_points))
        self.scpi_out("TRIG:ACQ:SOUR TRAN")
        self.scpi_out("INIT:ACQ")
        time.sleep(0.1) #it would be best to query the statur of the ACQ system
        self.scpi_out(" TRIG:ACQ")
        time.sleep(1.5) #it would be best to query the active measurment status to fetch measurement after it is done
        points = self.rp_USB.query("FETC:ARR:VOLT?")
        return points
        #TODO deal with the points returned, separate them and save them in an array that can be accessed by the EIS class
        


    def scpi_out(self, command):
        """Outputs an encoded scpi string on serial port"""
        try:
            self.rp_USB.write(str(command),"\n")
        except:
            print("could not send the message: " + str(command))
    def scpi_points_out(self, values):
        """Outputs the command to set the ARB points and the points as scpi values"""
        try:
            self.rp_USB.write_ascii_values('ARB:CURRent:CDWell', values, "f",",","\n")
        except:
            print("could not send array")
    def scpi_query(self, query):
        try:
            self.rp_USB.query(str(query))
        except:
            print("could not send query: " + str(query))
    def stop(self):
        self.rp_USB.write("ABORt:TRANsient","\n")
        self.rp_USB.write("OUTP OFF","\n")
        self.rp_USB.write("ABORt:ACQuire","\n")
        self.rp_USB.write("ABORt:ELOG","\n")
    def elog_config(self, selector): #maybe we should measure the current as well?
        try:
            """Select the Measurement Function"""
            self.scpi_out("SENS:ELOG:FUNC:CURR ON")
            """ Specify the Integration Period minimum of 102.4 microseconds to a maximum of 60 seconds."""
            self.scpi_out("SENS:ELOG:PER 0.0006")
            """Select the Elog Trigger Source"""
            self.scpi_out(" TRIG:ELOG:SOUR IMM")
            if selector:
                self.scpi_out("FORM[:DATA] REAL")
                self.scpi_out("FORM:BORD NORM")
        except:
            print("ELOG config error")
    def elog_start(self):
        try:
            self.scpi_out("INIT:ELOG")
        except:
            print("ELOG start error")
    def elog_retrieve_data(self, wait, records):
        try:
            time.sleep(wait)
            data=self.rp_USB.query_ascii_values("FETC:ELOG? "+str(records),"f",",",)
        except:
            print("Retrieve data error")
        return data
    def elog_stop(self):
        self.scpi_out("ABOR:ELOG")
    def elog_retrieve_data_binary(self, wait, records):
        try:
            time.sleep(wait)
            data=self.rp_USB.query_binary_values("FETC:ELOG? "+str(records),"f",True)#TODO finish parameters to retrieve binary data
        except:
            print("Retrieve data error")
        return data

         
instrument=RP7972A()
point=instrument.measure_voltage(0.000001,10)
print(point)
#instrument.stop()

