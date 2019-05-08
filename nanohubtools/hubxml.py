"""
Manipulate XML for nanoHUB tools

Benjamin P. Haley, Purdue University (bhaley@purdue.edu)

Copyright 2017 HUBzero Foundation, LLC.

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.

HUBzero is a registered trademark of Purdue University.
"""

import json
import numpy as np
import xml.etree.ElementTree as et
from .api import launch_tool, get_results

# Driver template for the drivergen tool
template = """<?xml version="1.0"?>
<run>
    <input>
        <string id="toolname"><current>{0}</current></string>
        <string id="inputs"><current>{1}</current></string>
    </input>
</run>
"""

def get_driver(tool_name, inputs, headers):
    """Get the driver XML for running a nanoHUB tool with specific inputs"""
    drivergen_json = {
        'app': 'drivergen',
        'xml': template.format(tool_name, json.dumps(inputs))
    }
    session_id = launch_tool(drivergen_json, headers)
    run_xml = get_results(session_id, headers)
    xml = et.fromstring(run_xml)  # <run>
    driver_str  = '<?xml version="1.0"?>\n'
    driver_str += xml.find('./output/string/current').text
    return {'app': tool_name, 'xml': driver_str}

def extract_results(run_xml, outputs):
    """
    Parse run_xml to extract the specified output; return a dict with the 
    output label as a key.  The returned values will be floats for <number> 
    outputs, (x,y) tuples of numpy arrays for <curve> outputs, and strings
    for all other output types.
    """
    d = {}
    xml = et.fromstring(run_xml)  # <run>
    for el in xml.find('output'):
        lel = el.find('./about/label')
        if lel is not None and lel.text in outputs:
            cel = el.find('current')
            val = cel.text
            if el.tag == 'number':
                val = float(val)
            elif el.tag == 'curve':
                lines = val.split('\n')
                n = len(lines)
                x = np.zeros(n)
                y = np.zeros(n)
                for i in range(n):
                    words = lines[i].split()
                    x[i] = float(words[0])
                    y[i] = float(words[1])
                val = (x,y)
            d[lel.text] = val
    return d

def extract_all_results(run_xml):
    """
    Parse run_xml to extract the specified output; return a dict with the 
    output label as a key.  The returned values will be floats for <number> 
    outputs, (x,y) tuples of numpy arrays for <curve> outputs, and strings
    for all other output types.
    """
    d = {}
    xml = et.fromstring(run_xml)  # <run>
    for el in xml.find('output'):
        lel = el.find('./about/label')
        cel = el.find('current')
        val = cel.text
        if el.tag == 'number':
            val = float(val)
        elif el.tag == 'curve':
            lines = val.split('\n')
            n = len(lines)
            x = np.zeros(n)
            y = np.zeros(n)
            for i in range(n):
                words = lines[i].split()
                x[i] = float(words[0])
                y[i] = float(words[1])
            val = (x,y)
        d[lel.text] = val
    return d