from .api import do_get, do_post, authenticate, launch_tool, get_results, check_status, load_results
from .hubxml import get_driver, extract_results, extract_all_results
from IPython.display import clear_output
from floatview import Floatview
from ipywidgets import Output, Tab, ToggleButton, Text, Dropdown, IntText, VBox, HBox, Accordion, Button
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
        self.output_cont = Output()
        self.output_cont.layout.width = '100%'
        self.options_cont = Output()
        self.margins_cont = Output()
        self.widget_output = Output()
        self.options_but = Button(description="Run ...", tooltip='Run exploration', icon='check', disable=False)
        self.options_but.on_click(lambda b : Nanohubtool.exploreOptions(self))
        self.option_tab = Tab()
        self.option_tab.children = [self.options_cont]
        self.option_tab.set_title(0, "Parameters")
        self.option_tab.layout.display = None

        try : 
            self.session = Nanohubsession(credentials)
        except ConnectionError as ce:
            print ("Invalid Authentication, server returned: " + str(ce))
        except:
            print ("Invalid Authentication")
        
        

        self.options_check = ToggleButton(value = True, description="parameters", icon='cog')
        self.options_check.observe(lambda v:self.showWidget(v["new"]), names='value')

        self.tab = HBox()
        self.tab.children = [self.option_tab, self.output_cont]
        if (self.window == None) :
            if (self.modal == True):
                title = kwargs.get('title', "")
                mode = kwargs.get('mode', "")
                self.window = Floatview(title = title, mode = mode)  
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
        parameters = {}
        for key, val in self.options.items():
            parameters[key] = val.value
            self.options[key].value = ''
        experiment = { 'parameters':parameters }
        self.addExperiment(experiment)

        
    def displayOutput(self):   
        with self.output_cont:
            clear_output()
            display(self.widget_output)

    def displayWindow(self):   
        with self.window:
            clear_output()
            display(self.options_check) 
            display(self.tab)


    def displayOptions(self): 
        with self.options_cont:
            clear_output()
            if len(self.options) > 0:
                for key, option in self.options.items():
                    display(option)
            display(self.options_but)
            
                
    def showWidget(self, show):
        if show:
            self.option_tab.layout.display = None
        else:
            self.option_tab.layout.display = "None"

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
                
    def getSessionId(self, tool, tool_inputs):
        self.validateSession() 
        if (self.authenticated):
            driver_json = get_driver(tool, tool_inputs, self.headers)
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

    