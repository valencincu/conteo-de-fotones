import pyvisa as visa
import numpy as np
import time

class TDS1002B:
    """Clase para el manejo osciloscopio TDS2000 usando PyVISA de interfaz
    """
    
    def __init__(self, name):
        self._osci = visa.ResourceManager().open_resource(name)
        self._osci.query("*IDN?")

        # Modo de transmision: Binario positivo.
        self._osci.write('DAT:ENC RPB')

        # 1 byte de dato. Con RPB 127 es la mitad de la pantalla
        self._osci.write('DAT:WID 1')

        # La curva mandada inicia en el primer dato
        self._osci.write("DAT:STAR 1") 

        # La curva mandada finaliza en el último dato
        self._osci.write("DAT:STOP 2500") 

        #Adquisición por sampleo
        self._osci.write("ACQ:MOD SAMP")
		
        # Bloquea el control del osciloscopio
        self._osci.write("LOC")
        
        def __del__(self):
            self._osci.close()			

    def unlock(self):
        # Desbloquea el control del osciloscopio
        self._osci.write("UNLOC")

    def set_channel(self, channel, scale, zero = 0):
        self._osci.write("CH{0}:SCA {1}".format(channel, scale))
        self._osci.write("CH{0}:POS {1}".format(channel, zero))
	
    def get_channel(self, channel):
        return self._osci.query("CH{0}?".format(channel))
		
    def set_time(self, scale, zero=0):
        self._osci.write("HOR:SCA {0}".format(scale))
        self._osci.write("HOR:POS {0}".format(zero))	
	
    def get_time(self):
        return self._osci.query("HOR?")
	
    def read_data(self, channel):
        # Hace aparecer el canal en pantalla. Por si no está habilitado
        self._osci.write("SEL:CH{0} ON".format(channel))
        # Selecciona el canal
        self._osci.write("DAT:SOU CH{0}".format(channel)) 

    	# xze primer punto de la waveform, xin intervalo de sampleo,
        # ymu factor de escala vertical, yoff offset vertical
        xze, xin, yze, ymu, yoff = self._osci.query_ascii_values('WFMPRE:XZE?;XIN?;YZE?;YMU?;YOFF?;', 
                                                                 separator=';') 
        data = (self._osci.query_binary_values('CURV?', datatype='B', 
                                               container=np.array) - yoff) * ymu + yze        
        time = xze + np.arange(len(data)) * xin
        return time, data
    
    def get_range(self):
        xze, xin, yze, ymu, yoff = self._osci.query_ascii_values('WFMPRE:XZE?;XIN?;YZE?;YMU?;YOFF?;', 
                                                                 separator=';')         
        rango = (np.array((0, 255))-yoff)*ymu +yze
        return rango
    
    
    def set_trigger(self, channel, level = None, slope = None):
        self._osci.write(f"TRIGger:MAIn:MODe EDGE")
        self._osci.write(f"TRIGger:MAIn:EDGE:SOUrce CH{channel}")
        if level != None: self._osci.write(f"TRIGger:MAIn:LEVel {level}")
        if slope != None: self._osci.write(f"TRIGger:MAIn:EDGE:SLOpe {slope}") 
        return self._osci.write("TRIGger:MAIn:EDGE?")
    
    def force_trigger(self):
        self._osci.write("TRIG")
        return None
    

class OSCI_SIM:
    def __init__(self):
        return None
    
    def set_time(self, scale, zero):
        return None
    
    def get_time(self):
        return None
    
    def set_channel(self, channel, scale):
        return None
    
    def get_channel(self, channel):
        return None
    
    def set_trigger(self, channel, level, slope):
        return None
    
    def force_trigger(self):
        return None
    
    def read_data(self, channel):
        time.sleep(0.005)
        t = np.linspace(0, 0.01, 2500)
        return t, np.sin(200*np.pi*t)