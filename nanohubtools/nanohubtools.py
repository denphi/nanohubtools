#  Copyright 2019 HUBzero Foundation, LLC.

#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#  THE SOFTWARE.

#  HUBzero is a registered trademark of Purdue University.

#  Authors:
#  Daniel Mejia (denphi), Purdue University (denphi@denphi.com)


from .api import authenticate, launch_tool, check_status, load_results, load_tool_definition
from IPython.display import clear_output
from floatview import Floatview
from ipywidgets import Output, Tab, ToggleButton, Text, VBox, HBox, Button, Layout
from hublib import ui
import time, threading

class Nanohubtool():

    
    
    widget_output = None    
    session = None
    def __init__(self, credentials, **kwargs):
        self.options = {}
        self.experiments = []
        self.options = {}
        self.window = None
        self.tab = None
        self.debug = kwargs.get('debug', None)
        self.modal = kwargs.get('modal', True)
        self.only_subsets = kwargs.get('only_subsets', False)
        self.output_cont = VBox(layout=Layout(width = '100%', border='1px solid rgba(0, 0, 0, 0.25)'))
        self.options_cont = VBox(layout=Layout(width='100%', height='100%'))
        self.widget_output = VBox(layout=Layout(width='100%', height='100%'))
        self.options_but = Button(description="Run ...", tooltip='Run exploration', icon='check', disable=False)
        self.options_but.on_click(lambda b : Nanohubtool.exploreOptions(self))
        self.option_tab = Tab(layout=Layout(width="750px"))
        self.option_tab.children = [self.options_cont]
        self.option_tab.set_title(0, "Parameters")
        self.option_tab.layout.display = None
        self.parameters = {}
        

        try : 
            self.session = Nanohubsession(credentials)
        except ConnectionError as ce:
            print ("Invalid Authentication, server returned: " + str(ce))
        except:
            print ("Invalid Authentication")
        
        

        self.options_check = ToggleButton(value = True, description="Hide Parameters", icon='cog')
        self.options_check.observe(lambda v:self.showWidget(v["new"]), names='value')

        self.tab = HBox(layout=Layout(width='100%', height='99%'))
        self.tab.children = [self.option_tab, self.output_cont]
        if (self.window == None) :
            if (self.modal == True):
                title = kwargs.get('title', "")
                mode = kwargs.get('mode', "")
                self.window = Floatview(title = title, mode = mode)
                #if ( hasattr(self.window, 'uid') == False or self.window.uid == ''): #running on non lab environment
                #    self.modal = False
                #    self.window = Output()
                #    display(self.window)

            else:
                self.window = Output()
                display(self.window)
            
        self.displayWindow()
           
    def display(self):
        self.displayOutput()
        self.displayOptions()

    def addExperiment(self, experiment):
        self.experiments.append(experiment)
        
    def exploreOptions(self):
        self.parseOptions();

    def parseOptions(self):
        pass;

        
    def displayOutput(self):   
        self.output_cont.children = [self.widget_output]

    def displayWindow(self):   
        with self.window:
            clear_output()
            display(self.options_check) 
            display(self.tab)


    def displayOptions(self): 
        children = []
        if len(self.options) > 0:
            for key, option in self.options.items():
                children.append(option)
        children.append(self.options_but)
        self.options_cont.children = children
                
    def showWidget(self, show):
        if show:
            self.option_tab.layout.display = None
            self.options_check.description = "Hide Parameters"
        else:
            self.option_tab.layout.display = "None"
            self.options_check.description = "Show Parameters"

        
    def createOptionWidgets(self):    
        for param, parameter in self.parameters.items():
            self.options[param] = self.createHublibWidget(param, parameter)    

        
    def createHublibWidget(self, name, parameter ):
        if (parameter['description'] is None):
            parameter['description'] = ''
        if (parameter['units'] is None):
            parameter['units'] = ''
        if (parameter['units'] is not None):            
            if (parameter['min'] is not None):
                parameter['min'] = parameter['min'].replace(parameter['units'],"")
            if (parameter['max'] is not None):
                parameter['max'] = parameter['max'].replace(parameter['units'],"")
            if (parameter['default'] is not None):
                parameter['default'] = parameter['default'].replace(parameter['units'],"")
        if (parameter['type'] == "integer"):
            if (parameter['min'] == None) != (parameter['max'] == None):
                if parameter['min'] == None:
                    return ui.Integer(name=parameter['label'], value=parameter['default'], desc=parameter['description'], min=0, max=parameter['max'])            
                else:
                    return ui.Integer(name=parameter['label'], value=parameter['default'], desc=parameter['description'], min=parameter['min'], max=100000)
            else:
                return ui.Integer(name=parameter['label'], value=parameter['default'], desc=parameter['description'], min=parameter['min'], max=parameter['max'])
        elif (parameter['type'] == "choice"):
            return ui.Dropdown(name=parameter['label'], description=parameter['description'], value=parameter['default'], options=parameter['options'])
        elif (parameter['type'] == "number"):        
            if (parameter['min'] == None) != (parameter['max'] == None):
                if parameter['min'] == None:
                    return ui.Number(name=parameter['label'], value=parameter['default'], desc=parameter['description'], min=0, max=parameter['max'], units=parameter['units'])
                else:
                    return ui.Number(name=parameter['label'], value=parameter['default'], desc=parameter['description'], min=parameter['min'], max=100000, units=parameter['units'])
            else:
                return ui.Number(name=parameter['label'], value=parameter['default'], desc=parameter['description'], min=parameter['min'], max=parameter['max'], units=parameter['units'])
        elif (parameter['type'] == "string"):        
            return ui.String(name=parameter['label'], value=parameter['default'], description=parameter['description'])
        elif (parameter['type'] == "boolean"):        
            return ui.Togglebuttons(name=parameter['label'], value="no", description=parameter['description'], options=['no', 'yes'])
        else:
            return Text(value='',placeholder=parameter['label'],description='',disabled=False)
        

class Nanohubsession():
    credentials = {}
    headers = {}
    authenticated = False
    def __init__(self, credentials, **kwargs):
        self.credentials = credentials
        self.validateSession()
            
    def validateSession(self):
        if self.authenticated == True:
            pass; #TODO: validate session is active;
        if self.authenticated == False:
            try :
                self.headers = authenticate(self.credentials)
                self.authenticated = True
            except AttributeError:
                self.authenticated = False        
                raise ConnectionError("Authentication Token not found")
            except ConnectionError as ce:
                self.authenticated = False        
                raise ce
            except:
                self.authenticated = False        
                raise ConnectionError("invalid Authentication")
                
    #def getSessionId(self, tool, tool_inputs):
    #    self.validateSession() 
    #    if (self.authenticated):
    #        driver_json = get_driver(tool, tool_inputs, self.headers)
    #        session_id = launch_tool(driver_json, self.headers)
    #        return session_id
    #    return None
        
    def getSession(self, driver_json):
        self.validateSession() 
        if (self.authenticated):
            session_id = launch_tool(driver_json, self.headers)
            return session_id
        return None        
        
            
    def checkStatus(self, session_id):
        self.validateSession() 
        if (self.authenticated):
            return check_status({'session_num': session_id}, self.headers)
        return {}
        
    def getResults(self, session_id, run_file):
        self.validateSession() 
        results_json = {
            'session_num': session_id,
            'run_file': run_file
        }
        if (self.authenticated):
            return load_results(results_json, self.headers)
        return ''


    def displayOptions(self): 
        children = []
        if len(self.options) > 0:
            for key, option in self.options.items():
                children.append(option)
        children.append(self.options_but)
        self.options_cont.children = children        


    def getToolDefinition(self, tool):
        return load_tool_definition(tool, self.headers)        
        
class setInterval :
    def __init__(self,interval,action) :
        self.interval=interval
        self.action=action
        self.stopEvent=threading.Event()
        thread=threading.Thread(target=self.__setInterval)
        thread.start()

    def __setInterval(self) :
        nextTime=time.time()+self.interval
        while not self.stopEvent.wait(nextTime-time.time()) :
            nextTime+=self.interval
            self.action()

    def cancel(self) :
        self.stopEvent.set()        

    