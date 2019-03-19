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
        500e6: 'full',
        200e6: 'b200',
        100e6: 'b100',
        50e6: 'b50',
        20e6: 'b20',
        10e6: 'b10',
        5e6: 'b5',
        2e6: 'b2',
        1e6: 'b1',
        500e3: 'b5hk',
        200e3: 'b2hk',
        100e3: 'b1hk',
        50e3: 'b50k',
        20e3: 'b20k',
        10e3: 'b10k',
        5e3: 'b5k',
        2e3: 'b2k',
        1e3: 'b1k',
        }
AcquisitionInterpolationMapping = dict()

AcquisitionTypeMapping = {
        'normal': 'samp',
        'sample': 'samp',
        'peak_detect': 'pdet',
        'high_resolution': 'hres',
        'average': 'aver',
        'envelope': 'env',
        }
VerticalCouplingMapping = {
        'dc':  'dcl',
        'ac':  'acl',
        # FIXME: No "GND?"
        }
TriggerCouplingMapping = {
        'dc': '', # Is always DC coupled
        'noise_reject_dc': 'mnr', # Is set via "TRIG:MNR"
        }
GlitchConditionMapping = {
        'less_than': 'shor',
        'greater_than': 'long',
        }
WidthConditionMapping = {
        'longer': 'long',
        'shorter': 'shor',
        'equal': 'equ',
        'nequal': 'neq',
        'within': 'rang',
        'outside': 'outs',
        }
SampleModeMapping = dict()
MeasurementFunctionMapping = {
        'rise_time': 'rtim',
        'fall_time': 'ftim',
        'frequency': 'freq',
        'period': 'per',
        'voltage_rms': 'rms',
        'voltage_peak_to_peak': 'pkpk',
        'voltage_max': 'max',
        'voltage_min': 'min',
        'voltage_high': 'topl',
        'voltage_low': 'bas',
        'voltage_average': 'mean',
        'width_negative': 'npul',
        'width_positive': 'ppul',
        'duty_cycle_positive': 'pdcy',
        'duty_cycle_negative': 'ndcy',
        'amplitude': 'ampl',
        'overshoot': 'ovrs',
        'preshoot': 'pres',
        'phase': 'phas',
        'delay': 'del',
        }
MeasurementFunctionMappingDigital = dict()
MeasurementStatusMapping = {
        'complete': 'comp',
        'in_progress': 'stop',
        'running': 'run',
        'break': 'bre',
        }
ScreenshotImageFormatMapping = {
        'png': 'png',
        'jpg': 'jpg',
        'bmp': 'bmp',
        'tiff': 'tiff'
        }
TimebaseModeMapping = dict()
TimebaseReferenceMapping = dict()

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


