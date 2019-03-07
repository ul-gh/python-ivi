"""

Python Interchangeable Virtual Instrument Library

Copyright (c) 2014-2017 Alex Forencich

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

import io
import sys
from distutils.version import StrictVersion

try:
    import visa
    try:
        # New style PyVISA
        visa_rm = visa.ResourceManager()
        visa_instrument_opener = visa_rm.open_resource
    except OSError:
        visa_rm = visa.ResourceManager('@py')
        visa_instrument_opener = visa_rm.open_resource
    except AttributeError:
        # Old style PyVISA
        visa_instrument_opener = visa.instrument
except ImportError:
    # PyVISA not installed, pass it up
    raise ImportError
except:
    # any other error
    e = sys.exc_info()[1]
    sys.stderr.write("python-ivi: PyVISA is installed, but could not be loaded (%s: %s)\n" %
        (e.__class__.__name__, e.args[0]))
    raise ImportError

def list_resources():
    "List PyVisa resource strings"
    try:
        # New style PyVISA
        return visa_rm.list_resources()
    except AttributeError:
        # Old style PyVISA
        return visa.get_instruments_list()

    return []

class PyVisaInstrument:
    "PyVisa wrapper instrument interface client"
    def __init__(self, resource, *args, **kwargs):
        if type(resource) is str:
            i = visa_instrument_opener(resource, *args, **kwargs)
            # Support for "TCPIPx::aaa.bbb.ccc.ddd::ppppp::SOCKET" resources:
            # These have no separate control channel, thus a termination character
            # is always needed. Default newline is good for most instruments.
            if "socket" in resource.lower():
                if not hasattr(i, "read_termination") or not i.read_termination:
                    i.read_termination = "\n"
                if not hasattr(i, "write_termination") or not i.write_termination:
                    i.write_termination = "\n"
            # Setting up self.write_termination as a shortcut to the respetive
            # VISA instrument class property value. This might speed up the
            # self.write() method further below, although not sure by how much.
            if hasattr(i, "write_termination"):
                self.write_termination = i.write_termination
            else:
                self.write_termination = ""
            # For compatibility with old style PyVISA
            if not hasattr(i, 'assert_trigger'):
                i.assert_trigger = i.trigger
            self.instrument = i
        else:
            self.instrument = resource
        self.buffer = io.BytesIO()

    def __del__(self):
        self.close()

    def close(self):
        if self.instrument:
            self.instrument.close()
        self.instrument = None

    def write_raw(self, data):
        "Write binary data to instrument"
        self.instrument.write_raw(data)

    def read_raw(self, num=-1):
        "Read binary data from instrument"
        # PyVISA only supports reading entire buffer
        #return self.instrument.read_raw()
        data = self.buffer.read(num)
        if len(data) == 0:
            self.buffer = io.BytesIO(self.instrument.read_raw())
            data = self.buffer.read(num)
        return data

    def ask_raw(self, data, num=-1):
        "Write then read binary data"
        self.write_raw(data)
        return self.read_raw(num)

    def write(self, message, encoding = 'utf-8'):
        "Write string to instrument"
        if type(message) is tuple or type(message) is list:
            # recursive call for a list of commands
            for message_i in message:
                self.write(message_i, encoding)
            return
        # Support "TCPIPx::::::SOCKET" resources, see __init__
        if self.write_termination:
            message = str(message) + self.write_termination
        else:
            message = str(message)
        self.write_raw(message.encode(encoding))

    def read(self, num=-1, encoding = 'utf-8'):
        "Read string from instrument"
        return self.read_raw(num).decode(encoding).rstrip('\r\n')

    def ask(self, message, num=-1, encoding = 'utf-8'):
        "Write then read string"
        if type(message) is tuple or type(message) is list:
            # recursive call for a list of commands
            val = list()
            for message_i in message:
                val.append(self.ask(message_i, num, encoding))
            return val
        self.write(message, encoding)
        return self.read(num, encoding)

    def read_stb(self):
        "Read status byte"
        return self.instrument.read_stb()

    def trigger(self):
        "Send trigger command"
        self.instrument.assert_trigger()

    def clear(self):
        "Send clear command"
        self.instrument.clear()

    def remote(self):
        "Send remote command"
        self.instrument.control_ren(visa.constants.VI_GPIB_REN_ASSERT_ADDRESS)

    def local(self):
        "Send local command"
        self.instrument.control_ren(visa.constants.VI_GPIB_REN_ADDRESS_GTL)

    def lock(self):
        "Send lock command"
        self.instrument.lock()

    def unlock(self):
        "Send unlock command"
        self.instrument.unlock()
