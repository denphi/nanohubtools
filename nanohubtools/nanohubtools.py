from .api import do_get, do_post, authenticate, launch_tool, get_results, check_status, load_results, load_tool_definition
from .hubxml import get_driver, extract_results, extract_all_results
from IPython.display import clear_output
from floatview import Floatview
from ipywidgets import Output, Tab, ToggleButton, Text, Dropdown, IntText, VBox, HBox, Accordion, Button, Layout
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

    def extractParameters(self, parameters, xml):
        inputs = xml.find('input')
        params = {}
        for elem in inputs.iter():
            about = elem.find("about")
            if (about is not None):
                description = elem.find('description')
                if description is not None:
                    description = description.text        
                label = about.find("label")
                if (label is not None):
                    if (label.text in parameters):
                        param = {"type": elem.tag, "description" : description}
                        param['units'] = elem.find('units')
                        if param['units'] is not None:
                            param['units'] = param['units'].text
                        param['units'] = elem.find('units')
                        if param['units'] is not None:
                            param['units'] = param['units'].text
                        param['default'] = elem.find('default')
                        if param['default'] is not None:
                            param['default'] = param['default'].text
                        param['min'] = elem.find('min')
                        if param['min'] is not None:
                            param['min'] = param['min'].text
                        param['max'] = elem.find('max')
                        if param['max'] is not None:
                            param['max'] = param['max'].text
                        param['current'] = elem.find('current')
                        if param['current'] is not None:
                            param['current'] = param['current'].text
                        options = elem.findall('option')
                        opt_list = []
                        for option in options:
                            labout = option.find("about")
                            if (labout is not None):
                                llabel = labout.find("label")
                                if (llabel is not None):
                                    if (llabel.text):
                                        opt_list.append(llabel.text)
                        param['options'] = opt_list
                        params [label.text] = param
        return params;

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
        
    def getToolDefinition(self, tool):
        return load_tool_definition(tool, self.headers)
        
        
            
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

    