from .nanohubtools import Nanohubtool, setInterval
from plotly.graph_objs import FigureWidget
from ipywidgets import IntText, Text, Output, Tab, Button, Accordion, GridBox, Layout, ButtonStyle, Label, HBox, VBox, HTML, Image
from IPython.display import clear_output
from .hubxml import extract_all_results
import numpy as np
from hublib import ui
import xml.etree.ElementTree as ET
from floatview import Floatview
from threading import Lock

import copy
from base64 import b64decode, b64encode
import zlib
import time

class Qdotexplorer (Nanohubtool):
    
    def __init__(self, credentials, tool, parameters, **kwargs):
        Nanohubtool.__init__(self, credentials, **kwargs)
        #self.options['nsample'] = IntText(description = '# samples:', value = 2)
        #self.options['nsample'].observe(lambda v:self.UpdateTraces({'line.width':v['new']}), names='value')                
        self.experiment_container = None
        self.debug_output = Output()
        self.tool = tool
        
        self.parameters = []
        
        if (self.session):    
            xml = self.session.getToolDefinition(self.tool)
            xml = ET.fromstring(xml)
            self.parameters = self.extractParameters(parameters, xml)
        
        self.sleep_time = 5
                    
        self.createOptionWidgets()
        self.updateRender()
        self.inter = setInterval(self.sleep_time, lambda a=self : Qdotexplorer.updateExperiments(a))

        def __del__(self):
            self.inter.cancel()

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
            return ui.Integer(name=name, value=parameter['default'], desc=parameter['description'], min=parameter['min'], max=parameter['max'])
        elif (parameter['type'] == "choice"):
            return ui.Dropdown(name=name, description=parameter['description'], value=parameter['default'], options=parameter['options'])
        elif (parameter['type'] == "number"):        
            return ui.Number(name=name, value=parameter['default'], desc=parameter['description'], units=parameter['units'])
        elif (parameter['type'] == "string"):        
            return ui.Number(name=name, value=parameter['default'], description=parameter['description'])
        elif (parameter['type'] == "boolean"):        
            return ui.Togglebuttons(name=name, value="no", description=parameter['description'], options=['no', 'yes'])
        else:
            return Text(value='',placeholder=name,description='',disabled=False)
    
    
            
    def createToolWidget(self):    
        self.experiment_container = Tab()
        self.experiment_container.children = []
        self.widget_output.children = [self.experiment_container]
            


    def addExperiment(self, experiment):
        experiment['session_id'] = None
        experiment['complete'] = False
        experiment['results'] = ''
        if self.modal == False:
            experiment['modal'] = Output()
        else:
            experiment['modal'] = None
        experiment['status'] = Label(value='New',layout=Layout(width='auto'))
        experiment['button'] = Button(description='Running ...', icon='check', disabled=True)
        experiment['button'].on_click(lambda a, b=self, c=experiment : Qdotexplorer.loadResults(b,c))
        
        self.experiments.append(experiment)      
        children = list(self.experiment_container.children)
        experiment['output'] = Output()
        children.append(experiment['output'])
        self.experiment_container.children=children
        len_exp = len(self.experiment_container.children)
        self.experiment_container.set_title(len_exp-1, "New")
        self.displayExperiment(experiment)
            
    def updateExperiments(self):
        lock = Lock()
        if (lock.acquire(False)):
            if (self.session):    
                for i, experiment in enumerate(self.experiments):
                    if experiment['session_id'] == None:
                        try:
                            experiment['session_id'] = self.session.getSessionId(self.tool, experiment['parameters'])
                            self.experiment_container.set_title(i, experiment['session_id'])
                        except:
                            experiment['session_id'] = None
                    else: 
                        if experiment['complete'] == False:
                            status = self.session.checkStatus(experiment['session_id'])                                  
                            if 'success' in status and status['success']:
                                if 'status' in status:
                                    if len(status['status']) > 0:
                                        experiment['status'].value = str(status['status'][0])
                                    if 'finished' in status:
                                        if status['finished'] and status['run_file'] != "":
                                            experiment['button'].disabled = False
                                            experiment['button'].description = "Load Results"
            lock.release()
    
    def loadResults(self, experiment):
        if self.session is not None:    
            status = self.session.checkStatus(experiment['session_id'])                                  
            if 'success' in status and status['success']:            
                if 'finished' in status:
                    if status['finished'] and status['run_file'] != "":
                        experiment['complete'] = True                                    
                        xml = self.session.getResults(experiment['session_id'], status['run_file'])            
                        xml = ET.fromstring(xml)
                        parameters = {}
                        for key, val in self.extractParameters(self.parameters, xml).items():
                            parameters[key] = str(val['current'])
                        experiment['parameters']  = parameters
                        
                        experiment['results'] = xml.find('output')
                        self.displayExperiment(experiment)              
    
    
    def loadExperiment(self, session_id):
        experiment = {'parameters':{}}
        if self.session is not None:
            experiment['session_id'] = session_id
            experiment['complete'] = False
            experiment['results'] = ''
            experiment['output'] = Output()
            if self.modal == False:
                experiment['modal'] = Output()
            else:
                experiment['modal'] = None
                
            experiment['status'] = Label(value='Complete',layout=Layout(width='auto'))
            self.loadResults(experiment)

            self.experiments.append(experiment)                        
            children = list(self.experiment_container.children)
            children.append(experiment['output'])
            self.experiment_container.children=children
            len_exp = len(self.experiment_container.children)
            self.experiment_container.set_title(len_exp-1, experiment['session_id'])
            self.displayExperiment(experiment)
            

    def displayExperiment(self, experiment):

        params_b = []
        for k, v in experiment['parameters'].items():
            params_b.append(Button(description=k,layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))
            params_b.append(Label(value=v,layout=Layout(width='auto')))
        params_b.append(Button(description='Status',layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))
        params_b.append(experiment['status'])
        if (experiment['complete'] == False):
            params_b.append(experiment['button'])
        

        out_param = HBox(layout=Layout(width='100%', height='100%'))
        accordionParam = Accordion(children=[out_param])
        accordionParam.set_title(0, 'Parameters')
        
        grid = GridBox(children=params_b, layout=Layout(grid_template_columns='50% 50%'))
        out_param.children = [grid]
        

        if (experiment['complete']):
            out_curves = VBox(layout=Layout(width='100%', height='100%'))
            out_volumes = VBox(layout=Layout(width='100%', height='100%'))
            accordion = Accordion()
            acc_children = []
            acc_titles = []
            acc_item = 0
            if self.modal == False:            
                containerBox = HBox([accordion, experiment['modal']])
            else:
                containerBox = HBox([accordion, Output()])
                
            experiment['output'].clear_output()
            with experiment['output']:
                display(accordionParam)
                display(containerBox)
            oc_children = []
            try:            
                curves = experiment['results'].findall('curve')
                self.actions = [None for c in curves]
                for i in range(len(curves)):
                    el = curves[i]
                    but = Button(description=el.find("about").find("label").text, icon='check', disable=False)
                    but.on_click(lambda a, b=self, c=[curves[i]],d=experiment['modal'] : Qdotexplorer.plotXY(b,c,d))
                    oc_children.append(but)
                out_curves.children = oc_children
                if len(oc_children) > 0:
                    acc_item  = acc_item+1
                    acc_children.append(out_curves)
                    acc_titles.append('Curves') 

            except:
                pass;
            try:
                ov_children = []   
                component = experiment['results'].find("table").find("data").text
                data = component.split('\n')
                data = data[0:-1]
                for i,v in enumerate(data):
                    component = experiment['results']
                    component = self.getData(component, 'sequence') 
                    component = self.getData(component[0], 'element') 
                    component = self.getData(component[i], 'field') 
                    component = self.getData(component[0], 'component') 
                    but = Button(description=v, icon='check', disable=False)
                    but.on_click(lambda a, b=self, c=v, d=component, e=experiment['modal'] : Qdotexplorer.plotVTK(b,c,d,e))
                    ov_children.append(but)
                out_volumes.children = ov_children
                if len(ov_children) > 0:
                    acc_item  = acc_item+1
                    acc_children.append(out_volumes)
                    acc_titles.append('Volumes') 
            except:
                pass;
                    
            accordion.children = acc_children
            for i in range (acc_item):
                accordion.set_title(i, acc_titles[i])
        else:
            with experiment['output']:
                display(accordionParam)

    def parseOptions(self):
        parameters = {}
        for key, val in self.options.items():
            units = ''
            if key in self.parameters and self.parameters[key]['units'] is not None:
                units = str(self.parameters[key]['units'])
            parameters[key] = str(val.value) + units
            try:
                self.options[key].value = ''
            except:
                pass;
        experiment = { 'parameters':parameters }
        self.addExperiment(experiment)

    def getData(self, field, container):
        component = field.findall(container)
        return component

    def getXY(self, field, container):
        list_v = []
        component = self.getData(field, container) 
        for obj in component:
            xy = obj.find("xy").text
            list_v.append(xy)
        return list_v

    def getText(self, obj, fields):
        objf = obj
        text = ''
        try:
            for field in fields:
                objf = objf.find(field)
            text = objf.text
        except: 
            text = ''    
        return text
  
    def getVTK(self, component, container):
        list_v = []
        for obj in component:
            vtk = obj.find("vtk").text
            compressed_header = '@@RP-ENC:zb64\n'
            hlen = len(compressed_header)
            vtk = vtk[hlen:-1]
            datavtk = b64decode(vtk)
            list_v.append(zlib.decompress(datavtk, zlib.MAX_WBITS | 32))
        return list_v
  
    def plotVTK( self, title, component, out ):
        traces = []
        
        component = self.getVTK(component , 'component')
        datavtk = component[0]
        npdata = np.array(datavtk.splitlines())
        dimensions = npdata[4].split()
        dimensions = [int(dimensions[v]) for v in range (1,len(dimensions)) ]
        spacing = npdata[5].split()
        spacing = [float(spacing[v]) for v in range (1,len(spacing)) ]
        origin = npdata[6].split()
        origin = [float(origin[v]) for v in range (1,len(origin)) ]
        values = [np.fromstring(npdata[i], dtype=float, sep=" ") for i in range(10, len(npdata))]
        self.V = np.concatenate(values)
        x = 2
        y = 1
        z = 0
        X,Y,Z = np.mgrid[origin[x]:(spacing[x]*dimensions[x]):spacing[x], origin[y]:(spacing[y]*dimensions[y]):spacing[y], origin[z]:(spacing[z]*dimensions[z]):spacing[z]]
        self.X = X.flatten().tolist()
        self.Y = Y.flatten().tolist()
        self.Z = Z.flatten().tolist()
        min_val = np.amin(self.V)
        max_val = np.amax(self.V) 
        ncontours = 12
        n_value = np.linspace(min_val, max_val, num=ncontours + 2);

        trace = {
            "type": "volume",
            "x": self.X,
            "y": self.Y,
            "z": self.Z,
            #'marker' : {
            #    'color' : self.V,
            #    'opacity' : 0.35,
            #},
            "value": self.V,
            #"isomin": n_value[1],
            #"isomax": n_value[len(n_value)-2],
            "spaceframe": { "show": False, "fill": 0.0  },
            "surface": { "show": True, "fill": 1.0, "count":ncontours},
            "caps": {
              "x": { "show": True, "fill": 1.0 },
              "y": { "show": True, "fill": 1.0 },
              "z": { "show": True, "fill": 1.0 }
            },      
            "slices": {
              "x": { "show": False, },
              "y": { "show": False, },
              "z": { "show": False, }
            },      
            "colorscale": "Viridis",
            "reversescale": False,
            "opacity":0.8,
            "opacityscale":"max",
            "lighting" :{
                "ambient" : 1.0,
                "diffuse" : 0.0,
                "specular" : 0.0,
                "roughness" : 0.0,
                "fresnel" : 0.0,
            },
            "lightposition":{
                "x" : 10000,
                "y" : 10000,
                "z" : 0,
            }      
        }
        traces.append(trace)
        layout = {
        } 
        
        fig = FigureWidget({
            'data': traces,
            'layout': layout
        })
        
        if out == None:
            out = Floatview(title=title, mode = 'split-bottom')
        out.clear_output()
        with out:
            display(fig)
        return fig
      

  
    def plotXY(self, fields, out):
        traces = []
        for field in fields:
            component = self.getXY(field, 'component')
            label = self.getText(field, ["about","label"])
            title = self.getText(field, ["about","group"])
            xaxis = self.getText(field, ["xaxis","label"])
            xunits = self.getText(field, ["xaxis","units"])
            xscale = self.getText(field, ["xaxis","scale"])
            if xscale == "":
                xscale = "linear"
                yaxis = self.getText(field, ["yaxis","label"])
                yunits = self.getText(field, ["yaxis","units"])
                yscale = self.getText(field, ["yaxis","scale"])    
            if yscale == "":
                yscale = "linear"
            for obj in component:
                xy = obj.strip()
                xy = np.array(xy.splitlines())
                xy = xy[(xy != '')]
                xy = [np.fromstring(xy[i], dtype=float, sep=" ") for i in range(len(xy))]
                xy = np.concatenate(xy)
                xy = xy.reshape(int(len(xy)/2),2)
                trace1 = {
                    'type' : 'scatter',
                    'x' : xy[:,0],
                    'y' : xy[:,1],
                    'mode' : 'lines',
                    'name' : label
                }
                traces.append(trace1)
        
        layout = {
            'title' : title,
            'xaxis' : {
                'title' : xaxis + " [" + xunits + "]",
                'type' : xscale,
                'autorange' : True,
                'exponentformat' :  "e",
            },
            'yaxis' : {
                'title' : yaxis + " [" + yunits + "]",
                'type' : yscale,
                'autorange' : True,
                'exponentformat' : "e"
            },
            'legend' : { 'orientation' : 'h'},          
        }    
        fig = FigureWidget({
            'data': traces,
            'layout': layout
        })
        if out == None:
            out = Floatview(title=title, mode = 'split-bottom')
        out.clear_output()    
        with out:
            display(fig)
        return fig

            
    def updateRender(self):		
        self.createToolWidget()
        Nanohubtool.display(self)



class SimpleQuantumDot (Qdotexplorer):
    def __init__(self, credentials, **kwargs):
        self.parameters_structure = [
            '_Simple Quantum Dot Options', 
            'Shape', 
            'X Dimensions', 
            'Y Dimensions', 
            'Z Dimensions', 
            'Lattice Constant', 
            'Energy gap', 
            'Effective Mass',
            'Number of States',
        ]
        self.parameters_optical = [
            '_Light Polarization',
            'Angle Theta',
            'Angle Phi',
            '_Absortion',
            'Absolute Fermi Level',
            'Electron Fermi Level',
            'Temperature',
            'State Broadening',
            '_Sweep',
            'Sweep Parameter:',
            'Minimum',
            'Maximum',
            'Number of Points'
        ]
        Qdotexplorer.__init__(self, credentials, "qdot", self.parameters_structure + self.parameters_optical, **kwargs)
        self.experiment_container = None
        self.debug_output = Output()
               

        self.updateRender()
        self.inter = setInterval(self.sleep_time, lambda a=self : Qdotexplorer.updateExperiments(a))

        
    def displayOptions(self):
        html = '''
        <b><font size = "3.5">Welcome to Quantum Dot Lab !</font></b>
        <li>Quantum Dot Lab allows users to simulate quantum dots of various shapes and sizes and understand the impact of material properties and dimensions on optical absorption.</li>
        <li>Users can choose a variety of materials and shapes, perform effective mass or a 10 band tight binding simulation.</li>
        <li>We hope that this tool deepens your understanding on quantum dots and confined electronic systems.</li>
        <li>For more information, please check out the User Guide or send a ticket to nanoHUB.</li>
        '''
    
        
        container_structure = VBox(layout=Layout(width='100%', height='100%'))
        children_structure = []
        container_optical = VBox(layout=Layout(width='100%', height='100%'))
        children_optical = []
        container_introduction = VBox(layout=Layout(width='100%', height='100%'))
        children_introduction = []
        children_introduction.append(HTML(value=html))

        image = open("intro.png", "rb").read()
        children_introduction.append(Image(value=image,format='png',width=400))
        

        for p in self.parameters_structure :
            if p in self.options:            
                children_structure.append(self.options[p])
            else:
                children_structure.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))
        for p in self.parameters_optical :
            if p in self.options:            
                children_optical.append(self.options[p])
            else:
                children_optical.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))

        sqdottab = Tab()
        
        children_optical.append(self.options_but)
        children_structure.append(self.options_but)
        children_introduction.append(self.options_but)
        
        container_optical.children = children_optical
        container_structure.children = children_structure
        container_introduction.children = children_introduction
        sqdottab.children = [container_introduction, container_structure, container_optical]
        sqdottab.set_title(0, "Introduction")
        sqdottab.set_title(2, "Optical")
        sqdottab.set_title(1, "Structure")
                
        self.options_cont.children = [sqdottab]