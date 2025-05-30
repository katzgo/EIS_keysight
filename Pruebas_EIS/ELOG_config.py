#To be written inside the Instrument class at the end
#======================== ELOG config (no longer used) ==================================
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
