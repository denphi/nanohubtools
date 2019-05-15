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


from .nanohubtools import Nanohubtool, setInterval
from .plotlywidget import FigureWidget
from ipywidgets import IntText, Text, Output, Tab, Button, Accordion, GridBox, Layout, ButtonStyle, Label, HBox, VBox, HTML, Image, Textarea
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
        
        if (self.session):    
            xml = self.session.getToolDefinition(self.tool)
            self.xml = ET.fromstring(xml)
            self.extract_method = kwargs.get('extract_method', "label")
            if (self.extract_method == "id"):
                self.parameters = self.extractParametersById(parameters, self.xml)
            else:
                self.parameters = self.extractParameters(parameters, self.xml)
        
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
            return ui.Integer(name=parameter['label'], value=parameter['default'], desc=parameter['description'], min=parameter['min'], max=parameter['max'])
        elif (parameter['type'] == "choice"):
            return ui.Dropdown(name=parameter['label'], description=parameter['description'], value=parameter['default'], options=parameter['options'])
        elif (parameter['type'] == "number"):        
            return ui.Number(name=parameter['label'], value=parameter['default'], desc=parameter['description'], units=parameter['units'])
        elif (parameter['type'] == "string"):        
            return ui.String(name=parameter['label'], value=parameter['default'], description=parameter['description'])
        elif (parameter['type'] == "boolean"):        
            return ui.Togglebuttons(name=parameter['label'], value="no", description=parameter['description'], options=['no', 'yes'])
        else:
            return Text(value='',placeholder=parameter['label'],description='',disabled=False)
    
    
            
    def createToolWidget(self):    
        self.experiment_container = Tab()
        self.experiment_container.children = []
        self.widget_output.children = [self.experiment_container]
            


    def addExperiment(self, experiment):
        experiment['session_id'] = None
        experiment['complete'] = False
        experiment['results'] = ''
        if self.modal == False:
            experiment['modal'] = Output(layout=Layout(width='95%',height='auto'))
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
                            driver_json = self.generateDriver(experiment)
                            #experiment['session_id'] = self.session.getSessionId(self.tool, experiment['parameters'])
                            experiment['session_id'] = self.session.getSession(driver_json)
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
                        
                        if (self.extract_method == "id"):
                            list_parameters = self.extractParametersById(list(self.parameters.keys()), xml)
                        else:
                            list_parameters = self.extractParameters(list(self.parameters.keys()), xml)
                        
                        parameters = {}
                        for key, val in list_parameters.items():
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
                experiment['modal'] = Output(layout=Layout(width='95%',height='auto'))
            else:
                experiment['modal'] = None
                
            experiment['status'] = Label(value='Complete',layout=Layout(width='auto'))

            experiment['button'] = Button(description='Running ...', icon='check', disabled=True)
            experiment['button'].on_click(lambda a, b=self, c=experiment : Qdotexplorer.loadResults(b,c))
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
            value = self.parameters[k]
            params_b.append(Button(description=value["label"]+" (" + value["id"] + ")",layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))
            params_b.append(Label(value=v,layout=Layout(width='auto')))
        params_b.append(Button(description='Status',layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))
        params_b.append(experiment['status'])
        if (experiment['complete'] == False):
            params_b.append(experiment['button'])
        

        out_param = HBox(layout=Layout(width='99%', height='99%'))
        accordionParam = Accordion(children=[out_param])
        accordionParam.set_title(0, 'Parameters')
        
        grid = GridBox(children=params_b, layout=Layout(grid_template_columns='50% 50%'))
        out_param.children = [grid]
        

        if (experiment['complete']):
            out_curves = VBox(layout=Layout(width='99%', height='100%'))
            out_volumes = VBox(layout=Layout(width='99%', height='100%'))
            out_tables = VBox(layout=Layout(width='99%', height='100%'))
            out_logs = VBox(layout=Layout(width='99%', height='100%'))
            accordion = Accordion(layout=Layout(width='300px'))
            acc_children = []
            acc_titles = []
            acc_item = 0
            layout = Layout(width='99%')
            if self.modal == False:            
                containerBox = HBox([accordion, experiment['modal']], layout=Layout(width='auto'))
            else:
                containerBox = HBox([accordion, Output()], layout=Layout(width='auto'))
                
            experiment['output'].clear_output()
            accordionParam.selected_index=None
            with experiment['output']:
                display(accordionParam)
                display(containerBox)

            oc_children = []
            try:            
                curves = experiment['results'].findall('curve')
                groups = {}
                for i in range(len(curves)):
                    el = curves[i]
                    but = Button(description=self.getText(el, ["about","label"]), icon='check', disable=False, layout=layout)
                    but.on_click(lambda a, b=self, c=[curves[i]],d=experiment['modal'] : Qdotexplorer.plotXY(b,c,d))
                    oc_children.append(but)
                    ab = el.find('about')
                    if ab is not None:
                        for g  in ab.findall("group"):
                            if g.text in groups:
                                groups[g.text].append(el)
                            else:
                                groups[g.text] = [el]

                for k,g in groups.items():
                    if len(g) > 1:
                        but = Button(description=k, icon='check', disable=False, layout=layout)
                        but.on_click(lambda a, b=self, c=g,d=experiment['modal'] : Qdotexplorer.plotXY(b,c,d))
                        oc_children.append(but)
                out_curves.children = oc_children
                if len(oc_children) > 0:
                    acc_item  = acc_item+1
                    acc_children.append(out_curves)
                    acc_titles.append('Curves') 

            except:
                pass;

            ot_children = []
            try:            
                tables = experiment['results'].findall('table')
                for i in range(len(tables)):
                    el = tables[i]
                    but = Button(description=el.find("about").find("label").text, icon='check', disable=False, layout=layout)
                    but.on_click(lambda a, b=self, c=tables[i],d=experiment['modal'] : Qdotexplorer.plotTable(b,c,d))
                    ot_children.append(but)
                out_tables.children = ot_children
                if len(ot_children) > 0:
                    acc_item  = acc_item+1
                    acc_children.append(out_tables)
                    acc_titles.append('Tables') 

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
                    but = Button(description=v, icon='check', disable=False, layout=layout)
                    but.on_click(lambda a, b=self, c=v, d=component, e=experiment['modal'] : Qdotexplorer.plotVTK(b,c,d,e))
                    ov_children.append(but)
                out_volumes.children = ov_children
                if len(ov_children) > 0:
                    acc_item  = acc_item+1
                    acc_children.append(out_volumes)
                    acc_titles.append('Volumes') 
            except:
                pass

            try:
                ol_children = []

                logs = experiment['results'].findall('log')
                for i in range(len(logs)):
                    el = logs[i]
                    but = Button(description='Log', icon='check', disable=False, layout=layout)
                    but.on_click(lambda a, b=self, c=logs[i],d=experiment['modal'] : Qdotexplorer.plotLog(b,c,d))
                    ol_children.append(but)
                strings = experiment['results'].findall('string')
                for i in range(len(strings)):
                    el = strings[i]
                    but = Button(description=el.find("about").find("label").text, icon='check', disable=False, layout=layout)
                    but.on_click(lambda a, b=self, c=el.find('current'),d=experiment['modal'] : Qdotexplorer.plotLog(b,c,d))
                    ol_children.append(but)
                out_logs.children = ol_children
                if len(ol_children) > 0:
                    acc_item  = acc_item+1
                    acc_children.append(out_logs)
                    acc_titles.append('Logs')
            except:
                pass
                    
            accordion.children = acc_children
            for i in range (acc_item):
                accordion.set_title(i, acc_titles[i])
            accordion.selected_index=0
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
  
    def plotVTK( self, title, componentv, out ):
        traces = []
        fig = None
        if out == None:
            out = Floatview(title=title, mode = 'split-bottom')
        out.clear_output()
        with out:
        
            component = self.getVTK(componentv , 'component')
            component_id = [c.attrib['id'] for c in componentv]

            for ii, datavtk in enumerate(component):
            
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
                Z,Y,X = np.mgrid[origin[x]:((spacing[x]*dimensions[x])+origin[x]):dimensions[x]*1j, origin[y]:((spacing[y]*dimensions[y])+origin[y]):dimensions[y]*1j, origin[z]:((spacing[z]*dimensions[z])+origin[z]):dimensions[z]*1j]
                self.X = X.flatten().tolist()
                self.Y = Y.flatten().tolist()
                self.Z = Z.flatten().tolist()
                #min_val = np.amin(self.V)
                #max_val = np.amax(self.V) 
                ncontours = 20
                colorscale = "Viridis"
                showscale = True
                type = 'volume'
                opacity = 1.0
                fill = 1.0
                id = component_id[ii]
                #print (id)
                if id == 'shape':
                    ncontours = 1
                    colorscale = "Greens"
                    showscale = False
                    opacity = 0.05
                    type = 'isosurface'
                trace = {
                    "type": type,
                    "name" : id,
                    "x": self.X,
                    "y": self.Y,
                    "z": self.Z,
                    #'marker' : {
                    #    'color' : self.V,
                    #    'opacity' : 0.35,
                    #},
                    "value": self.V,
                                  
                                               
                    "spaceframe": { "show": False, "fill": 0.0  },
                    "surface": { "show": True, "fill": 1.0, "count":ncontours},
                    "caps": {
                        "x": { "show": True, "fill": fill },
                        "y": { "show": True, "fill": fill },
                        "z": { "show": True, "fill": fill }
                    },      
                    "slices": {
                        "x": { "show": False, },
                        "y": { "show": False, },
                        "z": { "show": False, }
                    },      
                    "colorscale": colorscale,
                    "reversescale": False,
                    "opacity":opacity,
                                 
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
                    },
                    "showscale":showscale,
                }
                if type == "volume":
                    trace["opacityscale"]=[[0, 0], [0.1, 0.5], [0.2, 1], [1, 1]]
                else:
                    trace['isomin'] = 0.99
                    trace['isomax'] = 1.0

                traces.append(trace)
            layout = {
                'title': {
                    'text':title
                }
            } 
            
            fig = FigureWidget({
                'data': traces,
                'layout': layout
            })
            display(fig)
        return fig
      

    def plotTable(self, field, out):
        traces = []
        title = self.getText(field, ["about","label"])
        if out == None:
            out = Floatview(title=title, mode = 'split-bottom')
        out.clear_output()
        with out:
            columns = field.findall("column") 
            col_list = []
            for col in columns:
                col_list.append( "<b>" + self.getText(col, ["label"] ) + "</b>")
            tot_col = len(col_list)
            cell_list = [[] for i in col_list]
            data = field.find("data").text
            data = data.split('\n')
            for d in data:
                d = d.rsplit(sep=' ', maxsplit=(tot_col-1))
                if (len(d) > 1):
                    for i, v in enumerate(d):
                        cell_list[i].append(v)
                    
            trace1 = {
                'type' : 'table',
                'header' : {
                    'values' : col_list,
                },
                'cells' : {
                    'values' : cell_list,
                }
            }
            traces.append(trace1)

            layout = {
                'height': 400
            }
            fig = FigureWidget({
                'data': traces,
                'layout': layout
            })
            display(fig)
        return fig
  

    def plotLog(self, field, out):
        traces = []
        title = self.getText(field, ["about","label"])
        if out == None:
            out = Floatview(title=title, mode = 'split-bottom')
        out.clear_output()
        with out:            
            display(Textarea(value=field.text, layout=Layout(width='auto', height='400px')))


    def plotXY(self, fields, out, labels=None):
        traces = []
        for i, field in enumerate(fields):
            component = self.getXY(field, 'component')
            label = self.getText(field, ["about","label"])
            if labels is not None:
                label = label + " " + labels[i]
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
            'legend' : { 'orientation' : 'h', 'x':0.1, 'y':1.1 },
        }    
        fig = FigureWidget({
            'data': traces,
            'layout': layout
        })
        if out == None:
            out = Floatview(title=title, mode = 'split-bottom')
        out.clear_output()    
        but = Button(description="Compare Data", icon='check', disable=False, layout=layout)
        but.on_click(lambda a, b=self, c=fields[0], d=out : Qdotexplorer.compareXY(b,c,d))
        with out:
            display(fig)
            display(but)
        return fig

            
    def updateRender(self):		
        self.createToolWidget()
        Nanohubtool.display(self)

    def compareXY (self, field, out):
        ab = field.find('about')
        group = ""
        if ab is not None:
            grp = ab.find("group")
            if grp is not None:
                group = grp.text
        explist = []
        labels = []
        if group != "":
            for experiment in self.experiments:
                for result in experiment['results'] :
                    ab = result.find('about')
                    if ab is not None:
                        grp = ab.find("group")
                        if grp is not None and grp.text == group:
                            explist.append(result)
                            labels.append(experiment['session_id'])
        self.plotXY(explist, out, labels)

class SimpleQuantumDot (Qdotexplorer):
    def __init__(self, credentials, **kwargs):
                                            
        #self.parameters_structure = [
        #    '_Simple Quantum Dot Options', 
        #    'Shape', 
        #    'X Dimensions', 
        #    'Y Dimensions', 
        #    'Z Dimensions', 
        #    'Lattice Constant', 
        #    'Energy gap', 
        #    'Effective Mass',
        #    'Number of States',
        #]
        #self.parameters_optical = [
        #    '_Light Polarization',
        #    'Angle Theta',
        #    'Angle Phi',
        #    '_Absortion',
        #    'Absolute Fermi Level',
        #    'Electron Fermi Level',
        #    'Temperature',
        #    'State Broadening',
        #    '_Sweep',
        #    'Sweep Parameter:',
        #    'Minimum',
        #    'Maximum',
        #    'Number of Points'
        #]        
        self.parameters_structure = [
            '_Simple Quantum Dot Options', 
            'shape', 
            'dotx', 
            'doty', 
            'dotz', 
            'lattice', 
            'Eg', 
            'emass',
            'nstates',
        ]
        self.parameters_optical = [
            '_Light Polarization',
            'theta',
            'phi',
            '_Absortion',
            'absolute_Ef',
            'Ef',
            'temperature',
            'gamma',
            '_Sweep',
            'sweep',
            'min',
            'max',
            'npts'
        ]
        Qdotexplorer.__init__(self, credentials, "qdot", self.parameters_structure + self.parameters_optical, extract_method="id", **kwargs)
        self.experiment_container = None
        self.debug_output = Output()
               

        self.updateRender()
        self.inter = setInterval(self.sleep_time, lambda a=self : Qdotexplorer.updateExperiments(a))

        
    def displayOptions(self):
        html = '''
        <b><font size = "3.5">Welcome to Simple Quantum Dot App !</font></b>
        <li>Simple Quantum Dot App allows users to simulate quantum dots of various shapes and sizes and understand the impact of material properties and dimensions on optical absorption.</li>
        <li>Users can choose a variety of shapes, and perform effective mass simulations.</li>
        <li>We hope that this tool deepens your understanding on quantum dots</li>
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

        
class StackedQuantumDot (Qdotexplorer):
    def __init__(self, credentials, **kwargs):
                                            
        self.parameters_structure = [
            '_Stacked Quantum Dot Options', 
            'nstates_cb', 
            'nstates_vb', 
            'modeling',
            'materials_vbcb',
            'strain',
            'bandstructure',
            'Alloy_Disorder', 
            'Distribution_Type', 
            'Mole_fraction', 
            'Random_seed', 
            'shape',
            'dimx',
            'dimy',
        ]
        self.parameters_optical = [
            '_Light Polarization',
            'theta',
            'phi',
            '_Absortion',
            'absolute_Ef',
            'Ef',
            'temperature',
            'gamma',
            '_Sweep',
            'sweep',
            'min',
            'max',
            'npts'
        ]
        self.parameters_additional = [
            'structchoice'
        ]
        parameters = self.parameters_structure + self.parameters_optical + self.parameters_additional
        Qdotexplorer.__init__(self, credentials, "qdot", parameters, extract_method="id", **kwargs)
        self.options[self.parameters_additional[0]] = ui.String(name='Quantum Dot Structure', value='Multi-Layer Quantum Dot', description='Quantum Dot Structure')
        self.experiment_container = None
        self.debug_output = Output()
             

        self.updateRender()
        self.inter = setInterval(self.sleep_time, lambda a=self : Qdotexplorer.updateExperiments(a))

        
    def displayOptions(self):
        html = '''
        <b><font size = "3.5">Welcome to Stacked Quantum Dot App !</font></b>
        <li>Stacked Quantum Dot App allows users to simulate quantum dots of various shapes and sizes and understand the impact of material properties and dimensions on optical absorption.</li>
        <li>Users can choose a variety of materials and shapes, perform effective mass or a 10 band tight binding simulation.</li>
        <li>We hope that this tool deepens your understanding on quantum dots and confined electronic systems.</li>
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
