import numpy as np
import pyvisa

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

    def scpi_out(self, command):
        """Outputs an encoded scpi string on serial port"""
        self.rp_USB.write(command,"\n")
        # TODO finish this method

inst = RP7972A()
inst.scpi_out("SENS:SWE:TINT 2")
inst.scpi_out("SENS:SWE:POIN 200")
inst.scpi_out("MEASure:ARRay:VOLTage[:DC]?")