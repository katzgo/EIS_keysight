import numpy as np
import pyvisa
import time

class RP7972A():
    """Esta clase pide y mide los datos de la fuente, para luego ser procesados"""
    def __init__(self, curr_amplitude, voltage_limit, rp_USB=None):
        """Define variables de entrada como variables globales en la clase"""
        self.curr_amplitude = curr_amplitude
        self.voltage_limit = voltage_limit

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
        arb_cycles, arb_points_per_cycle = self.cycles_per_frequency(frequency);
        arb_points, dwell_time = self.arb_data(frequency, arb_points_per_cycle);
        ms = {}
        # Set output priority mode to current
        ms['priority_mode'] = "FUNC CURR, (@1)"
        # Set voltage limit (necessary for output priority mode)
        ms['voltage_limit'] = "VOLT:LIM " + str(self.voltage_limit) + ", (@1)"
        # Cancel any transients or arbs
        ms['abort_transient_1'] = "ABOR:TRAN (@1)"
        # Set arbitrary function type to current
        ms['arb_func_type'] = "ARB:FUNC:TYPE CURR,(@1)"
        # Set arbitrary function shape to CDW
        ms['arb_func_shape'] = "ARB:FUNC:SHAP CDW,(@1)"
        # Set the arb to repeat an infinite amount of times
        arb_cycles = "50"
        ms['arb_count'] = "ARB:COUN " + str(arb_cycles) + ", (@1)"
        # Set the last current setting when the arb ends to 1A
        ms['arb_term_last'] = "ARB:TERM:LAST 0,(@1)"
        # Set the mode of the current to be an Arbitrary signal
        ms['curr_mode'] = "CURR:MODE ARB,(@1)"
        # Set the source of the arbitrary trigger to Bus
        ms['trig_arb_source'] = "TRIG:ARB:SOUR Bus"
        # Set the dwell time for the signal (associated with the frequency)
        ms['arb_curr_cdw_dwell'] = "ARB:CURR:CDW:DWELL " + str(dwell_time) + ", (@1)"
        # Set slew rate setting (for testing)
        ms['curr_slew'] = "CURR:SLEW INF"
        # Prepares to send out the current points
        ms['current_points'] = (arb_points*self.curr_amplitude)+self.curr_amplitude
        # Initiates the output
        ms["output_init"] = "OUTP 1,(@1)"
        # Initiates the transient  
        ms["init_tran"] = "INIT:TRAN (@1)"
        # Triggers the transient   
        ms["trig_tran"] = "TRIG:TRAN (@1)"
        for message in ms:
            if message != "current_points":
                self.scpi_out(ms[message])
            else:
                self.scpi_points_out(ms[message])
    #TOOLBOX    
    def cycles_per_frequency(self, freq):
        """Switch para definir ciclos por frecuencia, recibe una frequencia saca cantidad de ciclos"""
        if 1000 < freq <= 2000:
            cycles = 4
            points_per_cycle = 50
        elif 100 < freq <= 1000:
            cycles = 2
            points_per_cycle = 100
        elif 10 < freq <= 100:
            cycles = 2
            points_per_cycle = 100
        elif 1 < freq <= 10:
            cycles = 2
            points_per_cycle = 100
        elif 100/1000 < freq <= 1:
            cycles = 2
            points_per_cycle = 100
        elif 10/1000 < freq <= 100/1000:
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
        try:
            self.rp_USB.write(command,"\n")
        except:
            print("could not send" + str(command))
        # TODO finish this method
    def scpi_points_out(self, values):
        """Outputs the command to set the ARB points and the points as scpi values"""
        try:
            self.rp_USB.write_ascii_values('ARB:CURR:CDW ', values, "f",",","\n")
        except:
            print("could not send ascii values")
    def scpi_query(self, query):
        try:
            response=self.rp_USB.query(str(query))
            return response
        except:
            print("could not send query: " + str(query))
    def stop(self):
        try:
            self.rp_USB.write("ABORt:TRANsient","\n")
            self.rp_USB.write("OUTP OFF","\n")
            self.rp_USB.write("ABORt:ACQuire","\n")
            self.rp_USB.write("ABORt:ELOG","\n")
        except:
            print("could not send stop commands")

# =======================================================================================================
#LOAD DEFINITION
#DUT = input("Input the DUT's characteristics: Resistive Load(R), Battery(B)")
DUT = "R"
if DUT == "R":
    r = 22 #Enter load's resistance in Ohms
    power_capacity = 10 #Enter load's power capacity in Watts
    amplitude = np.sqrt(power_capacity/r)/2
    voltage_limit = r*amplitude*2 + 1
    print(voltage_limit)
    print(amplitude)
else:
    amplitude = 0.1 # If not a resistive load, enter the amplitude of the current to apply to the DUT


# =======================================================================================================
#SIGNAL DEFINITION
# Edit the following values of the current signal you wish to generate
frequency = 1000
freqs=[10,20,30,40,50,60,70,80,90,100]

# =======================================================================================================
#CLASS CALLING
# Calling the class of the instrument
inst = RP7972A(amplitude, voltage_limit)
for i in freqs:
    inst.generate_arb(i)
    status_curr = True
    print("Generating current of frequency " + str(i))
    while(status_curr):
        time.sleep(0.001)
        status=inst.scpi_query("STAT:OPER:COND?")
        #print(status)
        if int(status[1:]) >= 64:
            status_curr = bin(int(status[1:]))[2:][-7]
        else:
            status_curr = 0
        print(status_curr)


# =======================================================================================================
#STOP GENERATING
#input("Enter to stop generating the signal")
#inst.stop()


# Measurements should be made with an Oscilloscope for Testing
# TODO: Alinear los triggers del measure y de la generación
# TODO: Cambiar el trigger source para el measure
# TODO: Usar la función de status, STATUS CHECK
# TODO: Status check de que ya terminó la señal
