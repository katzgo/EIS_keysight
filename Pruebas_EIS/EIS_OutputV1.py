import serial

class RP7972A():
    """Esta clase pide y mide los datos de la fuente, para luego ser procesados"""
    def __init__(self, curr_initialFreq=0, curr_finalFreq=0, curr_amplitude=0, curr_sweepPoints=0):
        """Define variables de entrada como variables globales en la clase"""
        self.curr_initialFreq = curr_initialFreq
        self.curr_finalFreq = curr_finalFreq
        self.curr_amplitude = curr_amplitude
        self.curr_sweepPoints = curr_sweepPoints

        # FOR INITIALIZATION OF POWER SOURCE (RP7972A)
        #open serial port
        COM_PORT = "COM"+ input("Escribir # del puerto COM de RP7972A: ") # Instrument port location
        TIMEOUT = 1
        self.USB_scpi = serial.Serial()
        self.USB_scpi.port=COM_PORT
        self.USB_scpi.timeout = TIMEOUT
        self.USB_scpi.open()
        
    
    def scpi_out(self, command):
        """Outputs an encoded scpi string on serial port"""
        while not self.USB_scpi.is_open:
            self.USB_scpi.close() #idk if this is needed for redundancy
            print("!!!Serial not open!!!")
            COM_PORT="COM" + input("enter new COM port: ")
            self.USB_scpi.port= COM_PORT
            self.USB_scpi.open()
 
        self.USB_scpi.write(str(command).encode())  # Send command

prueba = RP7972A()
CHECK_COMMAND = "*IDN?\n"  # Terminate with newline
prueba.scpi_out(CHECK_COMMAND)
response = prueba.USB_scpi.readline().decode()
print("Conectado a: " + response)

#prueba.scpi_out("Escribe el comando aqui")
prueba.USB_scpi.close()