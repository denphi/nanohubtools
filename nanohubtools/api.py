"""
Copyright 2019 HUBzero Foundation, LLC.

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

Authors:
Benjamin P. Haley, Purdue University (bhaley@purdue.edu)
Daniel Mejia (denphi), Purdue University (denphi@denphi.com)
"""

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    from urllib2 import urlopen, Request, HTTPError
except ImportError:
    from urllib.request import urlopen, Request, HTTPError

import sys, json, time
import requests
import json

url = r'https://nanohub.org/api'
sleep_time = 1.5

def do_get(url, path, data, hdrs, json = True):
    request = requests.get('{0}/{1}'.format(url, path) , data=data, headers=hdrs)
    if (json):
        return request.json()    
    else:
        return request.text

def do_post(url, path, data, hdrs, json = True):
    request = requests.post('{0}/{1}'.format(url, path) , data=data, headers=hdrs)
    if (json):
        return request.json()    
    else:
        return request.text
    
def validate_request (auth_json):
    if 'errors' in auth_json:
        raise ConnectionError(json.dumps(auth_json['errors']))


def authenticate(auth_data):
    auth_json = do_post(url, 'developer/oauth/token', auth_data, hdrs={})
    validate_request(auth_json)
    if 'access_token' in auth_json:
        return {'Authorization': 'Bearer {}'.format(auth_json['access_token'])}
    else :
        raise AttributeError('access_token')
        
def launch_tool(driver_json, headers):
    """Start a tool session; return the session id"""
    run_json = do_post(url, 'tools/run', driver_json, headers)
    if 'session' in run_json:
        return run_json['session']
    else:
        msg = 'launch_tool failed ({0}): {1}\n'.format(run_json['code'], run_json['message'])
        sys.stderr.write(msg)
        sys.exit(1)

def load_tool_definition(tool_name, headers):
    try :
        tool_xml = do_get(url, 'tools/' + tool_name + '/rappturexml', {}, headers, False)
        return tool_xml
    except:
        return ""
        
def check_status(session_json, headers):
    """Start a tool session; return the session id"""
    status_json = do_post(url, 'tools/status', session_json, headers)
    return status_json
        
def get_results(session_id, headers):
    """Wait for the tool session to finish; return the run XML"""
    status_data = {'session_num': session_id}
    while True:
        time.sleep(sleep_time)
        status_json = do_post(url, 'tools/status', status_data, headers)
        if 'finished' in status_json : 
            if status_json['finished'] is True:
                break
    time.sleep(sleep_time)  # let the DB update
    result_data = {
        'session_num': session_id,
        'run_file': status_json['run_file']
    }
    result_json = do_post(url, 'tools/output', result_data, headers)
    return result_json['output']

    
def load_results(run_json, headers):
    result_json = do_post(url, 'tools/output', run_json, headers)
    if 'output' in result_json:
        return result_json['output'];
    else:
        return '';
