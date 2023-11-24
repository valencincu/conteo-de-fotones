# -*- coding: utf-8 -*-
"""
    lantz.drivers.tektronix.tds1002B
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implements the drivers to control an oscilloscope.

    :copyright: 2012 by Lantz Authors, see AUTHORS for more details.
    :license: BSD, see LICENSE for more details.
    
    Source: Tektronix Manual
"""

from numpy import array, arange

from lantz.feat import Feat
from lantz.action import Action
from lantz.visa import USBVisaDriver
from lantz.errors import InvalidCommand

class TDS1002B(USBVisaDriver):
    """Tektronix TDS1002B 60MHz 2 Channel Digital Storage Oscilloscope
    """
    ENCODING = 'ascii'

    RECV_TERMINATION = '\n'
    SEND_TERMINATION = '\n'
    TIMEOUT = -1    # Avoids timeout while acquiring a curve. May not be the 
                    # best option.
        
    @Action()
    def initiate(self):
        """ Initiates the acquisition in the osciloscope.
        """
        self.send(':ACQ:STATE ON')
            
    @Feat(read_once=True)
    def idn(self):
        """ Identify the Osciloscope
        """
        return self.query('*IDN?')
        
    @Action()
    def autoset(self):
        """ Adjust the vertical, horizontal and trigger controls to display a 
            stable waveform.
        """
        self.send('AUTOS EXEC')
    
    @Action()
    def autocal(self):
        """ Autocalibration of osciloscope. It may take several minutes to 
            complete
        """
        return self.send('*CAL')
       
    @Feat(limits=(1,2))
    def datasource(self):
        """ Retrieves the data source from which data is going to be taken. 
            TDS1012 has 2 channels
        """
        return self.query('DAT:SOU?')
    
    @datasource.setter
    def datasource(self,value):
        """ Sets the data source for the acquisition of data.
        """
        self.send('DAT:SOU CH{}'.format(value))
    
    @Action()
    def acquire_parameters(self):
        """ Acquire parameters of the osciloscope.
            It is intended for adjusting the values obtained in acquire_curve
        """
        values = 'XZE?;XIN?;PT_OF?;YZE?;YMU?;YOF?;'
        answer = self.query('WFMP:{}'.format(values))
        parameters = {}
        for v, j in zip(values.split('?;'), answer.split(';')):
            parameters[v] = float(j)#.split(' ', 1)[1])
        return parameters
    
    @Action()
    def data_setup(self):
        """ Sets the way data is going to be encoded for sending. 
        """
        self.send('DAT:ENC ASCI;WID 2') #ASCII is the least efficient way, but
                                        # couldn't make the binary mode to work

    @Action()
    def acquire_curve(self, start=1, stop=100):
        """ Gets data from the oscilloscope. It accepts setting the start and 
            stop points of the acquisition (by default the entire range).
        """
        parameters = self.acquire_parameters()
        self.data_setup() 
        self.send('DAT:STAR {}'.format(start))
        self.send('DAT:STOP {}'.format(stop))
        data = self.query('CURV?')
        data = data[6:].split(',')
        data = array(list(map(float, data)))
        ydata = (data - parameters['YOF']) * parameters['YMU']\
                + parameters['YZE']
        xdata = arange(len(data))*parameters['XIN'] + parameters['XZE']
        return list(xdata), list(ydata)
        
    
    @Action()
    def forcetrigger(self):
        """ Creates a trigger event. 
        """
        self.send('TRIG:FORC')
        return
        
    @Action()
    def triggerlevel(self):
        """ Sets the trigger level to 50% of the minimum and maximum values of 
            the signal. 
        """
        self.send('TRIG:MAI SETL')
    
    @Feat(values={'AUTO', 'NORMAL'})
    def trigger(self):
        """ Retrieves trigger state.
        """
        return self.query('TRIG:MAIN:MODE?')
    
    @trigger.setter
    def trigger(self,state):
        """ Sets the trigger state.
        """
        self.send('TRIG:MAI:MOD {}'.format(state))
        return
        
    @Feat()
    def horizontal_division(self):
        """ Horizontal time base division. 
        """
        return float(self.query('HOR:MAI:SCA?'))
    
    @horizontal_division.setter
    def horizontal_division(self,value):
        """ Sets the horizontal time base division. 
        """
        self.send('HOR:MAI:SCA {}'.format(value))
        return
        
    @Feat(values={0, 4, 16, 64, 128})
    def number_averages(self):
        """ Number of averages
        """
        answer = self.query('ACQ?')
        answer = answer.split(';')
        if answer[0] == 'SAMPLE':
            return 0
        elif answer[0] == 'AVERAGE':
            return int(self.query('ACQ:NUMAV?'))
        else:
            raise InvalidCommand
    
    @number_averages.setter
    def number_averages(self,value):
        """ Sets the number of averages. If 0, the it is a continous sample.
        """
        if value == 0:
            self.send('ACQ:MOD SAMPLE')
        else:
            self.send('ACQ:MOD AVE;NUMAV {}'.format(value))
        
    @Action(values={'FREQ', 'MINI', 'MAXI', 'MEAN'})
    def _measure(self, mode):
        """ Measures the Frequency, Minimum, Maximum or Mean of a signal.
        """
        self.send('MEASU:IMM:TYP {}'.format(mode))
        return float(self.query('MEASU:IMM:VAL?'))
    
    def measure_mean(self):
        """ Gets the mean of the signal.
        """
        answer = self._measure('MEAN')
        return answer
 
    def measure_frequency(self):
        """ Gets the frequency of the signal.
        """
        answer = self._measure('FREQ')
        return answer
        
    def measure_minimum(self):
        """ Gets the minimum of the signal.
        """
        answer = self._measure('MINI')
        return answer        
       
    def measure_maximum(self):
        """ Gets the mean of the signal.
        """
        answer = self._measure('MAXI')
        return answer
