import numpy as np
import pyvisa

class RP7972A():
    """Esta clase pide y mide los datos de la fuente, para luego ser procesados"""
    def __init__(self, curr_amplitude, rp_USB=None):
        """Define variables de entrada como variables globales en la clase"""
        self.curr_amplitude = curr_amplitude

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

    def generate_arb(self, frequency):
        """Para generar las señales de corriente que se envian a la fuente, se tiene que llamar por cada frecuencia, no es sweep"""
        """INFO: service manual, cap 4, Programming an Arbitrary Waveform"""
        arb_cycles, arb_points_per_cycle = self.cycles_per_frequency(frequency)
        arb_points, dwell_time = self.arb_data(frequency, arb_points_per_cycle)
        # Enable arb function
        arb_enable = "CURR:MODE ARB"
        self.scpi_out(arb_enable)
        # Specify arb type
        arb_type = "ARB:FUNC:TYPE CURR"
        self.scpi_out(arb_type)
        # Specify dwell time
        arb_dwell = "ARB:CURR:CDW:DWEL " + str(dwell_time)
        self.scpi_out(arb_dwell)
        # Program arb points
        self.scpi_points_out(arb_points) # with scpi out points function not scipi out
        # Speecify the arb to repeat
        if arb_cycles > 1:
            arb_repeat = "ARB:COUN " + str(arb_cycles)
            self.scpi_out(arb_repeat)
        # Specify the last output
        arb_end = "ARB:END:LAST OFF"
        self.scpi_out(arb_end)

    #TOOLBOX    
    def cycles_per_frequency(self, freq):
        """Switch para definir ciclos por frecuencia, recibe una frequencia saca cantidad de ciclos"""
        if freq <= 2000:
            cycles = 4
            points_per_cycle = 50
        elif 100 <= freq < 1000:
            cycles = 2
            points_per_cycle = 100
        elif 10 <= freq <= 100:
            cycles = 2
            points_per_cycle = 100
        elif 1 <= freq <= 10:
            cycles = 2
            points_per_cycle = 100
        elif 100/1000 <= freq <= 1:
            cycles = 2
            points_per_cycle = 100
        elif 10/1000 <= freq <= 100/1000:
            cycles = 1
            points_per_cycle = 1000
        elif 1/1000 <= freq <= 10/1000:
            cycles = 1
            points_per_cycle = 1000
        return cycles, points_per_cycle
    def arb_data(self, frequency, points_per_cycle):
        """Generates data points for arb generation and dwell time for a frequency that is input.
        Minimum dwell time is 10 us (10*10^-6s)"""
        x = np.linspace(0, 2*np.pi, points_per_cycle)
        sin_points=np.sin(x)
        dwell_time=(1/frequency)/points_per_cycle
        return sin_points, dwell_time
        # Serán 1000 puntos por ciclo máximo, si hay problemas lo reduciremos (dato random)
    def scpi_out(self, command):
        """Outputs an encoded scpi string on serial port"""
        self.rp_USB.write(command,"\n")
        # TODO finish this method
    def scpi_points_out(self, values):
        """Outputs the command to set the ARB points and the points as scpi values"""
        self.rp_USB.write_ascii_values('ARB:CURR:CDW', values, "f",",","\n")
    def stop(self):
        self.rp_USB.write("ABOR:TRAN","\n")
        self.rp_USB.write("OUTP OFF","\n")
        self.rp_USB.write("ABOR:ACQ","\n")
        self.rp_USB.write("ABOR:ELOG","\n")

# Edit the following values of the current signal you wish to generate
amplitude = 1
frequency = 1000

# Calling the class of the instrument
inst = RP7972A(amplitude)
#inst.generate_arb(frequency)
inst.stop()
messages = ["ABOR:TRAN (@1)",
            "ARB:FUNC:TYPE CURR,(@1)",
            "ARB:FUNC:SHAP CDW,(@1)",
            "ARB:COUN INF,(@1)",
            "ARB:TERM:LAST 1,(@1)",
            "CURR:MODE ARB,(@1)",
            "TRIG:ARB:SOUR Bus",
            "ARB:CURR:CDW:DWELL 2.048005E-3,(@1)"]
for mess in messages:
    inst.scpi_out(mess)

inst.scpi_out("ARB:CURR:CDW 0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4")
inst.scpi_out("OUTP 1,(@1)")
inst.scpi_out("INIT:TRAN (@1)")
inst.scpi_out("TRIG:TRAN (@1)")
# Measurements should be made in Keysight's software


