from .nanohubtools import Nanohubtool, setInterval
from plotly.graph_objs import FigureWidget
from ipywidgets import IntText, Text, Output, Tab, Button, Accordion, GridBox, Layout, ButtonStyle, Label
from IPython.display import clear_output
from .hubxml import extract_all_results
import numpy as np
import xml.etree.ElementTree as ET
from floatview import Floatview
from threading import Lock

import copy
from base64 import b64decode, b64encode
import zlib
import time

class Qdotexplorer (Nanohubtool):
    
    def __init__(self, credentials, **kwargs):
        Nanohubtool.__init__(self, credentials, **kwargs)
        #self.options['nsample'] = IntText(description = '# samples:', value = 2)
        #self.options['nsample'].observe(lambda v:self.UpdateTraces({'line.width':v['new']}), names='value')                
        self.experiment_container = None
        self.debug_output = Output()
        
        self.parameters = kwargs.get('parameters', [])
        self.units = kwargs.get('units', ['' for i in self.parameters])
        self.sleep_time = 5
        
        while (len(self.parameters) > len(self.units)):
            self.units.append('')
            
        for param in self.parameters:
            self.options[param] = Text(value='',placeholder=param,description='',disabled=False)

        self.updateRender()
        self.inter = setInterval(self.sleep_time, lambda a=self : Qdotexplorer.updateExperiments(a))

        def __del__(self):
            self.inter.cancel()
        
    def createToolWidget(self):    
        self.widget_output.clear_output()
        self.experiment_container = Tab()
        self.experiment_container.children = []
        with self.widget_output:
            display(self.experiment_container)
            
    def createToolWidget(self):    
        self.widget_output.clear_output()
        self.experiment_container = Tab()
        self.experiment_container.children = []
        with self.widget_output:
            display(self.experiment_container)
            display(self.debug_output)
        with self.debug_output:
            print("testing")
            


    def addExperiment(self, experiment):
        experiment['session_id'] = None
        experiment['complete'] = False
        experiment['results'] = ''
        experiment['output'] = Output()
        experiment['status'] = Label(value='New',layout=Layout(width='auto'))
        self.experiments.append(experiment)      
        children = list(self.experiment_container.children)
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
                            experiment['session_id'] = self.session.getSessionId('qdot', experiment['parameters'])
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
                                if 'finished' in status and 'run_file' in status:
                                    if status['finished'] and status['run_file'] != "":
                                        experiment['complete'] = True                                    
                                        with experiment['output']:
                                            but = Button(description='Load results', icon='check', disable=False)
                                            but.on_click(lambda a, b=self, c=experiment, d=status['run_file'] : Qdotexplorer.loadResults(b,c,d))
                                            display(but)
            lock.release()
    
    def loadResults(self, experiment, run_file):
        xml = self.session.getResults(experiment['session_id'], run_file)            
        xml = ET.fromstring(xml)
        experiment['results'] = xml.find('output')
        self.displayExperiment(experiment)

                
    
    
    def loadExperiment(self, session_id):
        experiment = {'parameters':{}}
        if self.session is not None:
            status = self.session.checkStatus(session_id)
            experiment['session_id'] = session_id
            experiment['complete'] = False            
            experiment['results'] = ''
            experiment['output'] = Output()
            experiment['status'] = Label(value='Complete',layout=Layout(width='auto'))
            if 'finished' in status:
                if status['finished']:
                    experiment['complete'] = True            
                    if 'run_file' in status:
                        self.loadResults(experiment, status['run_file'])

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
        grid = GridBox(children=params_b, layout=Layout(grid_template_columns='50% 50%'))            
        out_param = Output()
    
        if (experiment['complete']):
            out_curves = Output()
            out_volumes = Output()    
            accordion = Accordion(children=[out_param, out_curves, out_volumes])
            accordion.set_title(0, 'Parameters')
            accordion.set_title(1, 'Curves')
            accordion.set_title(2, 'Volumes')
                
            experiment['output'].clear_output()
            with experiment['output']:
                display(accordion)
            with out_param:
                display(grid)
            with out_curves:            
                curves = experiment['results'].findall('curve')
                self.actions = [None for c in curves]
                for i in range(len(curves)):
                    el = curves[i]
                    but = Button(description=el.find("about").find("label").text, icon='check', disable=False)
                    but.on_click(lambda a, b=self, c=[curves[i]] : Qdotexplorer.plotXY(b,c))
                    display(but)
            with out_volumes:                            
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
                    but.on_click(lambda a, b=self, c=v, d=component : Qdotexplorer.plotVTK(b,c,d))
                    display(but)
        else:
            accordion = Accordion(children=[out_param])
            accordion.set_title(0, 'Parameters')
            with experiment['output']:
                display(accordion)
            with out_param:
                display(grid)

                
    

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
  
    def plotVTK( self, title, component ):
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
        out = Floatview(title=title, mode = 'split-bottom')
        with out:
            display(fig)        

  
    def plotXY(self, fields):
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
        out = Floatview(title=title, mode = 'split-bottom')
        with out:
            display(fig)

            
    def updateRender(self):		
        self.createToolWidget()
        Nanohubtool.display(self)


