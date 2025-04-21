class RP7972A():
    """Esta clase pide y mide los datos de la fuente, para luego ser procesados"""
    def __init__(self, curr_initialFreq, curr_finalFreq, curr_amplitude, curr_Freqs, points_per_decade, rp_USB=None):
        """Define variables de entrada como variables globales en la clase"""
        self.curr_initialFreq = curr_initialFreq
        self.curr_finalFreq = curr_finalFreq
        self.curr_amplitude = curr_amplitude
        self.curr_Freqs = curr_Freqs #an array of the frequencies used for the sweep
        self.points_per_decade = points_per_decade # the points per decade to generate the frequencies for the sweep

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

