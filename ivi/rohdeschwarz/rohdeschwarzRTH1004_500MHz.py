"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2017-2018 Acconeer AB

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

"""

from .rohdeschwarzBaseScope import *

BandwidthMapping = {
        500e6: 'FULL',
        200e6: 'B200',
        100e6: 'B100',
        50e6: 'B50',
        20e6: 'B20',
        10e6: 'B10',
        5e6: 'B5',
        2e6: 'B2',
        1e6: 'B1',
        500e3: 'B5HK',
        200e3: 'B2HK',
        100e3: 'B1HK',
        50e3: 'B50K',
        20e3: 'B20K',
        10e3: 'B10K',
        5e3: 'B5K',
        2e3: 'B2K',
        1e3: 'B1K',
        }

AcquisitionInterpolationMapping = dict()

AcquisitionTypeMapping = {
        'normal': 'SAMP',
        'sample': 'SAMP',
        'peak_detect': 'PDET',
        'high_resolution': 'HRES',
        'average': 'AVER',
        'envelope': 'ENV',
        }

VerticalCouplingMapping = {
        'dc':  'DCL',
        'ac':  'ACL',
        # FIXME: No "GND?"
        }

TriggerCouplingMapping = {
        'dc': '', # Is always DC coupled
        'noise_reject_dc': 'MNR', # Is set via "TRIG:MNR"
        }


class rohdeschwarzRTH1004_500MHz(rohdeschwarzBaseScope):
    "Rohde&Schwarz RTH1004 with 500MHz bandwidth option IVI oscilloscope driver"
    
    def __init__(self, *args, **kwargs):
        self.__dict__.setdefault('_instrument_id', 'RTH1004_500MHz')
        
        super().__init__(*args, **kwargs)
        
        self._analog_channel_count = 4
        self._digital_channel_count = 0
        self._channel_count = self._analog_channel_count + self._digital_channel_count
        self._bandwidth = 500e6
        self._horizontal_divisions = 10
        self._vertical_divisions = 8
        self._trigger_holdoff_min = 8.0e-9
        self._trigger_holdoff_max = 10.0e-0
        self._channel_offset_max = 400
        
        self._init_channels()

    def _get_acquisition_type(self):
        if not self._driver_operation_simulate and not self._get_cache_valid():
            value = self._ask("ACQ:MODE?")
            self._acquisition_type = [k for k,v in AcquisitionTypeMapping.items() if v==value][0]
            self._set_cache_valid()
        return self._acquisition_type

    def _set_acquisition_type(self, value):
        if value not in AcquisitionTypeMapping:
            raise ivi.ValueNotSupportedException()
        if not self._driver_operation_simulate:
            self._write(f"ACQ:MODE {AcquisitionTypeMapping[value]}")
        self._acquisition_type = value
        self._set_cache_valid()


