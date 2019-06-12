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
from ipywidgets import Output, Tab, Button, Accordion, GridBox, Layout, ButtonStyle, Label, HBox, VBox, Textarea, SelectionSlider, Play
import numpy as np
import xml.etree.ElementTree as ET
from floatview import Floatview
from threading import Lock
import math


import copy
from base64 import b64decode, b64encode
import zlib

class Rappturetool (Nanohubtool):

    samples = 16
    resize = .1
    phi = np.linspace(0, 2*np.pi, samples)
    theta = np.linspace(-np.pi/2, np.pi/2, samples)
    thetat = np.linspace(0,2*np.pi,samples)
    phit = np.linspace(0,np.pi,samples)
    xt = np.outer(np.cos(thetat),np.sin(phit)) * 4 * resize
    yt = np.outer(np.sin(thetat),np.sin(phit)) * 4 * resize
    zt = np.outer(np.ones(samples),np.cos(phit)) * 4 * resize
    cosphi = np.cos(phi) * resize
    sinphi = np.sin(phi) * resize
    phi, theta=np.meshgrid(phi, theta)
    x = np.cos(theta) * np.sin(phi)
    y = np.cos(theta) * np.cos(phi)
    z = np.sin(theta)
    x = x.flatten() * 4 * resize
    y = y.flatten() * 4 * resize
    z = z.flatten() * 4 * resize
    discardtags = ["phase", "group", "option"]
    jcpk = {
        'H' : 'rgb([255,255,255)',
        'He' : 'rgb(217,255,255)',
        'Li' : 'rgb(204,128,255)',
        'Be' : 'rgb(194,255,0)',
        'B' : 'rgb(255,181,181)',
        'C' : 'rgb(144,144,144)',
        'N' : 'rgb(48,80,248)',
        'O' : 'rgb(255,13,13)',
        'F' : 'rgb(144,224,80)',
        'Ne' : 'rgb(179,227,245)',
        'Na' : 'rgb(171,92,242)',
        'Mg' : 'rgb(138,255,0)',
        'Al' : 'rgb(191,166,166)',
        'Si' : 'rgb(240,200,160)',
        'P' : 'rgb(255,128,0)',
        'S' : 'rgb(255,255,48)',
        'Cl' : 'rgb(31,240,31)',
        'Ar' : 'rgb(128,209,227)',
        'K' : 'rgb(143,64,212)',
        'Ca' : 'rgb(61,255,0)',
        'Sc' : 'rgb(230,230,230)',
        'Ti' : 'rgb(191,194,199)',
        'V' : 'rgb(166,166,171)',
        'Cr' : 'rgb(138,153,199)',
        'Mn' : 'rgb(156,122,199)',
        'Fe' : 'rgb(224,102,51)',
        'Co' : 'rgb(240,144,160)',
        'Ni' : 'rgb(80,208,80)',
        'Cu' : 'rgb(200,128,51)',
        'Zn' : 'rgb(125,128,176)',
        'Ga' : 'rgb(194,143,143)',
        'Ge' : 'rgb(102,143,143)',
        'As' : 'rgb(189,128,227)',
        'Se' : 'rgb(255,161,0)',
        'Br' : 'rgb(166,41,41)',
        'Kr' : 'rgb(92,184,209)',
        'Rb' : 'rgb(112,46,176)',
        'Sr' : 'rgb(0,255,0)',
        'Y' : 'rgb(148,255,255)',
        'Zr' : 'rgb(148,224,224)',
        'Nb' : 'rgb(115,194,201)',
        'Mo' : 'rgb(84,181,181)',
        'Tc' : 'rgb(59,158,158)',
        'Ru' : 'rgb(36,143,143)',
        'Rh' : 'rgb(10,125,140)',
        'Pd' : 'rgb(0,105,133)',
        'Ag' : 'rgb(192,192,192)',
        'Cd' : 'rgb(255,217,143)',
        'In' : 'rgb(166,117,115)',
        'Sn' : 'rgb(102,128,128)',
        'Sb' : 'rgb(158,99,181)',
        'Te' : 'rgb(212,122,0)',
        'I' : 'rgb(148,0,148)',
        'Xe' : 'rgb(66,158,176)',
        'Cs' : 'rgb(87,23,143)',
        'Ba' : 'rgb(0,201,0)',
        'La' : 'rgb(112,212,255)',
        'Ce' : 'rgb(255,255,199)',
        'Pr' : 'rgb(217,255,199)',
        'Nd' : 'rgb(199,255,199)',
        'Pm' : 'rgb(163,255,199)',
        'Sm' : 'rgb(143,255,199)',
        'Eu' : 'rgb(97,255,199)',
        'Gd' : 'rgb(69,255,199)',
        'Tb' : 'rgb(48,255,199)',
        'Dy' : 'rgb(31,255,199)',
        'Ho' : 'rgb(0,255,156)',
        'Er' : 'rgb(0,230,117)',
        'Tm' : 'rgb(0,212,82)',
        'Yb' : 'rgb(0,191,56)',
        'Lu' : 'rgb(0,171,36)',
        'Hf' : 'rgb(77,194,255)',
        'Ta' : 'rgb(77,166,255)',
        'W' : 'rgb(33,148,214)',
        'Re' : 'rgb(38,125,171)',
        'Os' : 'rgb(38,102,150)',
        'Ir' : 'rgb(23,84,135)',
        'Pt' : 'rgb(208,208,224)',
        'Au' : 'rgb(255,209,35)',
        'Hg' : 'rgb(184,184,208)',
        'Tl' : 'rgb(166,84,77)',
        'Pb' : 'rgb(87,89,97)',
        'Bi' : 'rgb(158,79,181)',
        'Po' : 'rgb(171,92,0)',
        'At' : 'rgb(117,79,69)',
        'Rn' : 'rgb(66,130,150)',
        'Fr' : 'rgb(66,0,102)',
        'Ra' : 'rgb(0,125,0)',
        'Ac' : 'rgb(112,171,250)',
        'Th' : 'rgb(0,186,255)',
        'Pa' : 'rgb(0,161,255)',
        'U' : 'rgb(0,143,255)',
        'Np' : 'rgb(0,128,255)',
        'Pu' : 'rgb(0,107,255)',
        'Am' : 'rgb(84,92,242)',
        'Cm' : 'rgb(120,92,227)',
        'Bk' : 'rgb(138,79,227)',
        'Cf' : 'rgb(161,54,212)',
        'Es' : 'rgb(179,31,212)',
        'Fm' : 'rgb(179,31,186)',
        'Md' : 'rgb(179,13,166)',
        'No' : 'rgb(189,13,135)',
        'Lr' : 'rgb(199,0,102)',
        'Rf' : 'rgb(204,0,89)',
        'Db' : 'rgb(209,0,79)',
        'Sg' : 'rgb(217,0,69)',
        'Bh' : 'rgb(224,0,56)',
        'Hs' : 'rgb(230,0,46)',
        'Mt' : 'rgb(235,0,38)'
    }
    
    periodicelement = [
        ('Hydrogen','H'),
        ('Helium','He'),
        ('Lithium','Li'),
        ('Beryllium','Be'),
        ('Boron','B'),
        ('Carbon','C'),
        ('Nitrogen','N'),
        ('Oxygen','O'),
        ('Fluorine','F'),
        ('Neon','Ne'),
        ('Sodium','Na'),
        ('Magnesium','Mg'),
        ('Aluminium','Al'),
        ('Silicon','Si'),
        ('Phosphorus','P'),
        ('Sulfur','S'),
        ('Chlorine','Cl'),
        ('Argon','Ar'),
        ('Potassium','K'),
        ('Calcium','Ca'),
        ('Scandium','Sc'),
        ('Titanium','Ti'),
        ('Vanadium','V'),
        ('Chromium','Cr'),
        ('Manganese','Mn'),
        ('Iron','Fe'),
        ('Cobalt','Co'),
        ('Nickel','Ni'),
        ('Copper','Cu'),
        ('Zinc','Zn'),
        ('Gallium','Ga'),
        ('Germanium','Ge'),
        ('Arsenic','As'),
        ('Selenium','Se'),
        ('Bromine','Br'),
        ('Krypton','Kr'),
        ('Rubidium','Rb'),
        ('Strontium','Sr'),
        ('Yttrium','Y'),
        ('Zirconium','Zr'),
        ('Niobium','Nb'),
        ('Molybdenum','Mo'),
        ('Technetium','Tc'),
        ('Ruthenium','Ru'),
        ('Rhodium','Rh'),
        ('Palladium','Pd'),
        ('Silver','Ag'),
        ('Cadmium','Cd'),
        ('Indium','In'),
        ('Tin','Sn'),
        ('Antimony','Sb'),
        ('Tellurium','Te'),
        ('Iodine','I'),
        ('Xenon','Xe'),
        ('Caesium','Cs'),
        ('Barium','Ba'),
        ('Lanthanum','La'),
        ('Cerium','Ce'),
        ('Praseodymium','Pr'),
        ('Neodymium','Nd'),
        ('Promethium','Pm'),
        ('Samarium','Sm'),
        ('Europium','Eu'),
        ('Gadolinium','Gd'),
        ('Terbium','Tb'),
        ('Dysprosium','Dy'),
        ('Holmium','Ho'),
        ('Erbium','Er'),
        ('Thulium','Tm'),
        ('Ytterbium','Yb'),
        ('Lutetium','Lu'),
        ('Hafnium','Hf'),
        ('Tantalum','Ta'),
        ('Tungsten','W'),
        ('Rhenium','Re'),
        ('Osmium','Os'),
        ('Iridium','Ir'),
        ('Platinum','Pt'),
        ('Gold','Au'),
        ('Mercury','Hg'),
        ('Thallium','Tl'),
        ('Lead','Pb'),
        ('Bismuth','Bi'),
        ('Polonium','Po'),
        ('Astatine','At'),
        ('Radon','Rn'),
        ('Francium','Fr'),
        ('Radium','Ra'),
        ('Actinium','Ac'),
        ('Thorium','Th'),
        ('Protactinium','Pa'),
        ('Uranium','U'),
        ('Neptunium','Np'),
        ('Plutonium','Pu'),
        ('Americium','Am'),
        ('Curium','Cm'),
        ('Berkelium','Bk'),
        ('Californium','Cf'),
        ('Einsteinium','Es'),
        ('Fermium','Fm'),
        ('Mendelevium','Md'),
        ('Nobelium','No'),
        ('Lawrencium','Lr'),
        ('Rutherfordium','Rf'),
        ('Dubnium','Db'),
        ('Seaborgium','Sg'),
        ('Bohrium','Bh'),
        ('Hassium','Hs'),
        ('Meitnerium','Mt')        
    ]    
    
    def __init__(self, credentials, tool, parameters, **kwargs):
        Nanohubtool.__init__(self, credentials, **kwargs)
        self.experiment_container = None
        self.debug_output = Output()
        self.tool = tool
        self.reset_options = True
        
        if (self.session):    
            xml = self.session.getToolDefinition(self.tool)
            self.xml = ET.fromstring(xml)
            self.extract_method = kwargs.get('extract_method', "label")
            if (self.extract_method == "id"):
                self.parameters = self.extractParametersById(parameters, self.xml)
            else:
                self.parameters = self.extractParameters(parameters, self.xml)
        
        self.sleep_time = 5
        self.inter = setInterval(self.sleep_time, lambda a=self : Rappturetool.updateExperiments(a))
        self.createOptionWidgets()
        self.updateRender()

        def __del__(self):
            self.inter.cancel()          
        
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
        experiment['button'].on_click(lambda a, b=self, c=experiment : Rappturetool.loadResults(b,c))
        
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
            experiment['button'].on_click(lambda a, b=self, c=experiment : Rappturetool.loadResults(b,c))
            self.loadResults(experiment)

            self.experiments.append(experiment)                        
            children = list(self.experiment_container.children)
            children.append(experiment['output'])
            self.experiment_container.children=children
            len_exp = len(self.experiment_container.children)
            self.experiment_container.set_title(len_exp-1, experiment['session_id'])
            self.displayExperiment(experiment)
            

    def displayExperiment(self, experiment, disable=[]):

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
            out_plots = VBox(layout=Layout(width='99%', height='100%'))
            out_sequences = VBox(layout=Layout(width='99%', height='100%'))
            out_volumes = VBox(layout=Layout(width='99%', height='100%'))
            out_tables = VBox(layout=Layout(width='99%', height='100%'))
            out_logs = VBox(layout=Layout(width='99%', height='100%'))
            out_drawings = VBox(layout=Layout(width='99%', height='100%'))
            
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
                    but.on_click(lambda a, b=self, c=[curves[i]],d=experiment['modal'] : Rappturetool.plotXY(b,c,d))
                    oc_children.append(but)
                    ab = el.find('about')
                    if ab is not None:
                        for g  in ab.findall("group"):
                            if g.text in groups:
                                groups[g.text].append(el)
                            else:
                                groups[g.text] = [el]                                                                          
                                               
                out_curves.children = oc_children
                if len(oc_children) > 0 and "curves" not in disable:
                    acc_item  = acc_item+1
                    acc_children.append(out_curves)
                    acc_titles.append('Curves') 
            except:
                pass;

            op_children = []                                
            try:
                for k,g in groups.items():
                    but = Button(description=k, icon='check', disable=False, layout=layout)
                    but.on_click(lambda a, b=self, c=g,d=experiment['modal'] : Rappturetool.plotXY(b,c,d))
                    op_children.append(but)
                out_plots.children = op_children
                if len(op_children) > 0 and "plots" not in disable:
                    acc_item  = acc_item+1
                    acc_children.append(out_plots)
                    acc_titles.append('Plots') 
            except:
                pass;

            od_children = []    
            try:            
                drawings = experiment['results'].findall('drawing')
                groups = {}
                for i in range(len(drawings)):
                    el = drawings[i]
                    but = Button(description=self.getText(el, ["about","label"]), icon='check', disable=False, layout=layout)
                    but.on_click(lambda a, b=self, c=el,d=experiment['modal'] : Rappturetool.plotDrawing(b,c,d))
                    od_children.append(but)
                    ab = el.find('about')
                    if ab is not None:
                        for g  in ab.findall("group"):
                            if g.text in groups:
                                groups[g.text].append(el)
                            else:
                                groups[g.text] = [el]                                                                          
                                               
                out_drawings.children = od_children
                if len(od_children) > 0 and "drawings" not in disable:
                    acc_item  = acc_item+1
                    acc_children.append(out_drawings)
                    acc_titles.append('Drawings') 
            except:
                pass;
                

            os_children = []
            try:
                sequences = experiment['results'].findall('sequence')
                groups = {}
                for i in range(len(sequences)):
                    el = sequences[i]
                    but = Button(description=self.getText(el, ["about","label"]), icon='check', disable=False, layout=layout)
                    but.on_click(lambda a, b=self, c=sequences[i],d=experiment['modal'] : Rappturetool.plotSequence(b,c,d))
                    os_children.append(but)
                out_sequences.children = os_children
                if len(os_children) > 0 and "sequences" not in disable:
                    acc_item  = acc_item+1
                    acc_children.append(out_sequences)
                    acc_titles.append('Sequences')
            except:
                pass;


            ot_children = []
            try:            
                tables = experiment['results'].findall('table')
                for i in range(len(tables)):
                    el = tables[i]
                    but = Button(description=el.find("about").find("label").text, icon='check', disable=False, layout=layout)
                    but.on_click(lambda a, b=self, c=tables[i],d=experiment['modal'] : Rappturetool.plotTable(b,c,d))
                    ot_children.append(but)
                out_tables.children = ot_children
                if len(ot_children) > 0 and "tables" not in disable:
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
                    but.on_click(lambda a, b=self, c=v, d=component, e=experiment['modal'] : Rappturetool.plotVTK(b,c,d,e))
                    ov_children.append(but)
                out_volumes.children = ov_children
                if len(ov_children) > 0 and "volumes" not in disable:
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
                    but.on_click(lambda a, b=self, c=logs[i],d=experiment['modal'] : Rappturetool.plotLog(b,c,d))
                    ol_children.append(but)
                strings = experiment['results'].findall('string')
                for i in range(len(strings)):
                    el = strings[i]
                    but = Button(description=el.find("about").find("label").text, icon='check', disable=False, layout=layout)
                    but.on_click(lambda a, b=self, c=el.find('current'),d=experiment['modal'] : Rappturetool.plotLog(b,c,d))
                    ol_children.append(but)
                out_logs.children = ol_children
                if len(ol_children) > 0 and "logs" not in disable:
                    acc_item  = acc_item+1
                    acc_children.append(out_logs)
                    acc_titles.append('Logs')
            except:
                pass
                    
            accordion.children = acc_children
            for i in range (acc_item):
                accordion.set_title(i, acc_titles[i])
            if acc_item > 0:
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
            if self.reset_options:
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
      
    def getToolDefinition(self, tool):
        return load_tool_definition(tool, self.headers)
        
        
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
        compressed_header = '@@RP-ENC:zb64\n'
        hlen = len(compressed_header)        
        text = field.text
        if text.startswith(compressed_header):
            text = text[hlen:-1]
            text = b64decode(text)
            text = zlib.decompress(text, zlib.MAX_WBITS | 32)
        
        if out == None:
            out = Floatview(title=title, mode = 'split-bottom')
        out.clear_output()
        with out:            
            display(Textarea(value=text, layout=Layout(width='auto', height='400px')))

    def updateFrame(self, change, frames, fig, play, sl):
        if change["new"] in frames:
            frame = frames[change["new"]]
            indexes = []
            changes = {'x':[], 'y':[]}
            for i, trace in enumerate(frame):
                changes['x'].append(trace['x'].tolist())
                changes['y'].append(trace['y'].tolist())
                indexes.append(i)
            play.value = list(frames.keys()).index(change["new"])
            sl.value = change["new"]
            fig.plotly_restyle(changes, indexes)


    def plotSequence(self, sequence, out, labels=None):
        traces = []
        layout = {}
        frames = {}
        options = []
        elements = sequence.findall('element')
        label = self.getText(sequence, ["index", "label"])
        for seq in elements:
            curves = seq.findall('curve')
            oc_children = []
            groups = {}
            for i in range(len(curves)):
                el = curves[i]
                ab = el.find('about')
                if ab is not None:
                    for g  in ab.findall("group"):
                        if g.text in groups:
                            groups[g.text].append(el)
                        else:
                            groups[g.text] = [el]
            if(len(groups)>0):
                index = self.getText(seq, ["index"])
                options.append(index)
                tr, lay = self.buildXYPlotly(groups[list(groups.keys())[0]])
                if len(traces) == 0:
                    layout = lay
                    traces = tr
                frames[index] = tr

        fig = FigureWidget({
            'data': traces,
            'layout': layout
        }) 

        sl = SelectionSlider(options=options, value=options[0], description=label)
        play = Play(interval=1000, value=0, min=0, max=len(frames), description=label )
        sl.observe(lambda change, this=self, f=frames, g=fig, p=play, s=sl: Rappturetool.updateFrame(this, change, f, g, p, sl), "value")
        play.observe(lambda change, this=self, f=frames, g=fig, p=play, s=sl: setattr(sl, 'value', list(f.keys())[change['new']]), "value")
        sl.layout.width='99%'
        container = VBox([fig,play,sl], layout=layout)   


        if out == None:
            out = Floatview(title=label, mode = 'split-bottom')
        out.clear_output()
        with out:
            display(container)
        return fig

    def plotXY(self, fields, out, labels=None):
        traces, layout = self.buildXYPlotly(fields, labels)
        fig = FigureWidget({
            'data': traces,
            'layout': layout
        })
        if out == None:
            title = ""
            for field in (fields):
                title = self.getText(field, ["about","group"])                                                
            out = Floatview(title=title, mode = 'split-bottom')
        out.clear_output()    
        but = Button(description="Compare Data", icon='check', disable=False, layout=layout)
        but.on_click(lambda a, b=self, c=fields[0], d=out : Rappturetool.compareXY(b,c,d))
        with out:
            display(fig)
            display(but)
        return fig

    def buildXYPlotly(self, fields, labels=None):
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
                xy = [np.fromstring(xy[i].replace("--", ""), dtype=float, sep=" ") for i in range(len(xy))]
                xy = np.concatenate(xy)
                #xy = xy[0:int(len(xy)/2)*2]
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
        return traces, layout
                           
                  
    def plotDrawing(self, draw, out):
        label = self.getText(draw, ["index", "label"])
        if out == None:
            out = Floatview(title=label, mode = 'split-bottom')
        out.clear_output()     
        layout = { 'height' : 600 }
        traces = []
        molecules = draw.findall('molecule')
        for molecule in molecules:
            atoms = {}
            connections = {}            
            pdb = molecule.find('pdb')
            if pdb is not None:
                pdbt = self.getText(pdb, [])
                lines = pdbt.split('\n')
                for line in lines:
                    if line.startswith("ATOM"):
                        cols = line.split()
                        atoms[int(cols[1])] = [float(cols[5]),float(cols[6]),float(cols[7]), cols[2], Rappturetool.jcpk[cols[2]], "enabled"]
                    elif line.startswith("CONECT"):
                        cols = line.split()
                        connections[int(cols[1])] = [int(c) for c in cols[2:]]
            else:
                vtk = molecule.find('vtk')
                if vtk is not None:
                    jcpkkeys = list(Rappturetool.jcpk.keys())
                    vtkt = self.getText(vtk, [])
                    lines = vtkt.split('\n')
                    i=0
                    points = []
                    vertices = []
                    while i < len(lines):
                        line = lines[i]
                        if line.startswith("POINTS"):
                            tpoints = int(line.split()[1])
                            for ii in range(math.ceil(tpoints/3)):
                                i = i+1                                    
                                line = lines[i]
                                pp = line.split()
                                if len(points) < tpoints:
                                    points.append([float(pp[0]),float(pp[1]),float(pp[2])])
                                if len(points) < tpoints:
                                    points.append([float(pp[3]),float(pp[4]),float(pp[5])])
                                if len(points) < tpoints:
                                    points.append([float(pp[6]),float(pp[7]),float(pp[8])])

                        elif line.startswith("VERTICES"):
                            tvert = int(line.split()[1])
                            for ii in range(tvert):
                                i = i+1                                    
                                line = lines[i]
                                pp = line.split()
                                pp = [int(p) for p in pp]                                    
                                atoms[pp[1]] = [points[ii][0],points[ii][1],points[ii][2], 'Si', 'rgb(240,200,160)', "enabled"]
                            for j, point in enumerate(points):
                                if j not in atoms.keys():
                                    atoms[j] = [point[0],point[1],point[2], '', 'rgb(0,0,0)', "disabled"]
                        elif line.startswith("LINES"):
                            tlines = int(line.split()[1])
                            for ii in range(tlines):
                                i = i+1                                    
                                line = lines[i]
                                pp = line.split()
                                pp = [int(p) for p in pp]
                                if pp[1] in connections:
                                    connections[pp[1]].append(pp[2])
                                else:
                                    connections[pp[1]] = [pp[2]]
                        elif line.startswith("atom_type"):
                            ttype = int(line.split()[2])
                            for ii in range(math.ceil(ttype/9)):
                                i = i+1                                    
                                line = lines[i]
                                pp = line.split()
                                pp = [int(p) for p in pp]
                                for k in range (9):
                                    atom_id = (9*ii+k)                                      
                                    if atom_id in atoms and pp[k] <= len(Rappturetool.jcpk):
                                        atoms[atom_id][3] = jcpkkeys[pp[k]-1] 
                                        atoms[atom_id][4] = Rappturetool.jcpk[atoms[atom_id][3]]

                        i = i+1
            xt = None
            yt = None
            zt = None
            st = None
            color = {}
            colorset = set()
            for id, atom in atoms.items():
                colorset.add(atom[4])
            colorset = list(colorset)
            for id, atom in atoms.items():
                color[id] = colorset.index(atom[4])/len(colorset)
                
            colorscale = [[ii/len(colorset),colorset[ii]] for ii in range(len(colorset))]
            colorscale.append([1.0, colorset[len(colorset)-1]])
        
            xt = {}
            yt = {}
            zt = {}
            st = {}

            for id, atom in atoms.items():
                if atom[5] == "enabled":
                    xv = (Rappturetool.xt + atom[0]).tolist()
                    yv = (Rappturetool.yt + atom[1]).tolist()
                    zv = (Rappturetool.zt + atom[2]).tolist()
                    xv.extend([[point for point in xv[0]],[point for point in xv[1]],[]])
                    yv.extend([[point for point in yv[0]],[point for point in yv[1]],[]])
                    zv.extend([[point for point in zv[0]],[point for point in zv[1]],[]]) 
                    if atom[3] in xt:
                        xt[atom[3]].extend(xv)
                        yt[atom[3]].extend(yv)
                        zt[atom[3]].extend(zv) 
                    else :
                        xt[atom[3]] = xv
                        yt[atom[3]] = yv
                        zt[atom[3]] = zv
                        
            for atom in list(xt.keys()):

                colorscalea = [[0,Rappturetool.jcpk[atom]], [1,Rappturetool.jcpk[atom]]]

                trace = { 
                    'type':'surface',
                    'x': xt[atom], 
                    'y': yt[atom], 
                    'z': zt[atom], 
                    'text' : atom,
                    'showscale' : False,
                    'hoverinfo' : "text",
                    'colorscale' : colorscalea,
                    'connectgaps' : False

                }
                traces.append(trace)
                    
            xt = []
            yt = []
            zt = []
            st = []
            for atom1, connection in connections.items():
                for atom2 in connection:
                    at1 = atom1
                    at2 = atom2
                    u = np.array([atoms[at2][i]-atoms[at1][i] for i in range(3)])        
                    u /= np.linalg.norm(u)
                    v1 = np.random.randn(3)  # take a random vector
                    v1 -= v1.dot(u) * u       # make it orthogonal to k
                    v1 /= np.linalg.norm(v1)
                    v2 = np.cross(v1, u)
                    v2 /= np.linalg.norm(v2)
                    sample = int(Rappturetool.samples/2)
                    xd = np.linspace(atoms[at2][0], atoms[at1][0], sample)
                    yd = np.linspace(atoms[at2][1], atoms[at1][1], sample)
                    zd = np.linspace(atoms[at2][2], atoms[at1][2], sample)
                    for i in range(sample):
                        xt.append((Rappturetool.cosphi*v1[0] + Rappturetool.sinphi*v2[0] + xd[i]).tolist())
                        yt.append((Rappturetool.cosphi*v1[1] + Rappturetool.sinphi*v2[1] + yd[i]).tolist())
                        zt.append((Rappturetool.cosphi*v1[2] + Rappturetool.sinphi*v2[2] + zd[i]).tolist())
                        if i <= sample/2:
                            st.append( [color[at2] for c in range(Rappturetool.samples)])
                        else:
                            st.append( [color[at1] for c in range(Rappturetool.samples)])
                    xt.append([])
                    zt.append([])
                    yt.append([])
                    st.append( [color[at1] for c in range(Rappturetool.samples)])
                            

            trace = { 
                'type':'surface',
                'x': xt, 
                'y': yt, 
                'z': zt, 
                'showscale' : False,                
                'colorscale' : colorscale,
                'surfacecolor' : st,
                'hoverinfo' : 'text',
                'text' : '',                                
            }
            traces.append(trace)   
            polygons = draw.findall('polygon')
            for polygon in polygons:
                points = {}
                connections = {}            
                vtk = polygon.find('vtk')
                if vtk is not None:
                    vtkt = self.getText(vtk, [])
                    lines = vtkt.split('\n')
                    i=0
                    points = []
                    while i < len(lines):
                        line = lines[i]
                        if line.startswith("POINTS"):
                            tpoints = int(line.split()[1])
                            for ii in range(math.ceil(tpoints/3)):
                                i = i+1                                    
                                line = lines[i]
                                pp = line.split()
                                if len(points) < tpoints:
                                    points.append([float(pp[0]),float(pp[1]),float(pp[2])])
                                if len(points) < tpoints:
                                    points.append([float(pp[3]),float(pp[4]),float(pp[5])])
                                if len(points) < tpoints:
                                    points.append([float(pp[6]),float(pp[7]),float(pp[8])])
                        i=i+1             

                    xt = [point[0] for point in points]
                    yt = [point[1] for point in points]
                    zt = [point[2] for point in points]

                    trace = { 
                        'type':'mesh3d',
                        'x': xt, 
                        'y': yt, 
                        'z': zt, 
                        'color' : 'lightgrey',
                        'text' : '',
                        'hoverinfo' : 'text'
                    }
                    if len(set(xt)) == 1 : 
                        trace['delaunayaxis'] = 'x'
                    elif len(set(yt)) == 1 : 
                        trace['delaunayaxis'] = 'y'
                    elif len(set(zt)) == 1 : 
                        trace['delaunayaxis'] = 'z'

                    traces.append(trace)

            fig = FigureWidget({
                'data': traces,
                'layout': layout
            })      

        with out:            
            display(fig)
        return fig
            
    def updateRender(self):		
        self.createToolWidget()
        Nanohubtool.display(self)
        display(self.debug_output)


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
        
    def generateDriver(self, experiment):
        xml = copy.copy(self.xml)        
        #First add structure current parameters, Rappture hack 
        for elem in xml.iter():
            if elem.tag == "structure":
                edefault = elem.find("default")
                if edefault is not None:
                    params = edefault.find("parameters")
                    if params is not None:                   
                        current = ET.Element("current")
                        current.insert(0, copy.copy(params))
                        elem.insert(0,current)
        
        for parameter, value in experiment['parameters'].items():
            if parameter in self.parameters:
                if 'id' in self.parameters[parameter]:
                    for elem in xml.iter():
                        if 'id' in elem.attrib:
                            if elem.tag not in Rappturetool.discardtags:
                                if elem.attrib['id'] == self.parameters[parameter]['id']:
                                    current = ET.Element("current")
                                    current.text = str(value)
                                    elem.insert(0,current)
                                    #break;

        for elem in xml.iter():
            if 'id' in elem.attrib:
                if elem.tag not in Rappturetool.discardtags:            
                    if elem.find("current") is None:
                        units = ""
                        if elem.find("units") is not None:
                            units = elem.find("units").text
                        if elem.find("default") is not None:
                            current = ET.Element("current")
                            if units != "" and units not in elem.find("default").text:
                                current.text = elem.find("default").text + units
                            else:
                                current.text = elem.find("default").text
                            elem.insert(0,current)
                
        driver_str  = '<?xml version="1.0"?>\n' + ET.tostring(xml).decode()
        driver_json = {'app': self.tool, 'xml': driver_str}
        return driver_json;   

            
    def extractParameters(self, parameters, xml):
        inputs = xml.find('input')
        params = {}
        for elem in inputs.iter():
            id = ''
            if 'id' in elem.attrib:
                id = elem.attrib['id']
            about = elem.find("about")
            if (about is not None):
                description = elem.find('description')
                if description is not None:
                    description = description.text        
                label = about.find("label")
                if (label is not None):
                    if (label.text in parameters):
                        if elem.tag not in Rappturetool.discardtags:
                            param = {"type": elem.tag, "description" : description}
                            param['units'] = elem.find('units')
                            param['id'] = id
                            param['label'] = label.text                        
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
                                lvalue = option.find("value")
                                opt_val = ['', '']
                                if (lvalue is not None):
                                    if (lvalue.text != ""):
                                        opt_val[0] = lvalue.text
                                        opt_val[1] = lvalue.text
                                labout = option.find("about")
                                if (labout is not None):
                                    llabel = labout.find("label")
                                    if (llabel is not None):
                                        if (llabel.text != ""):
                                            opt_val[0] = llabel.text
                                            if opt_val[1] == '':
                                                opt_val[1] = llabel.text                                            
                                opt_list.append((opt_val[0], opt_val[1]))
                            param['options'] = opt_list

                            params [label.text] = param
        return params;
        
    def extractParametersById(self, parameters, xml):
        inputs = xml.find('input')
        params = {}
        for elem in inputs.iter():
            id = ''
            if 'id' in elem.attrib:
                id = elem.attrib['id']
            if id not in params:
                about = elem.find("about")
                if (about is not None):
                    description = elem.find('description')
                    if description is not None:
                        description = description.text        
                    label = about.find("label")
                    if (label is not None):
                        if (id in parameters):
                            if elem.tag not in Rappturetool.discardtags:
                                param = {"type": elem.tag, "description" : description}
                                param['units'] = elem.find('units')
                                param['id'] = id
                                param['label'] = label.text                        
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
                                    lvalue = option.find("value")
                                    opt_val = ['', '']                                    
                                    if (lvalue is not None):
                                        if (lvalue.text != ""):
                                            opt_val[0] = lvalue.text
                                            opt_val[1] = lvalue.text
                                    labout = option.find("about")
                                    if (labout is not None):
                                        llabel = labout.find("label")
                                        if (llabel is not None):
                                            if (llabel.text != ""):
                                                opt_val[0] = llabel.text
                                                if opt_val[1] == '':
                                                    opt_val[1] = llabel.text
                                    opt_list.append((opt_val[0], opt_val[1]))
                                param['options'] = opt_list

                                if param['type'] == "periodicelement" :
                                    param['type'] = 'choice'
                                    param['options'] = Rappturetool.periodicelement
                                
                                if len(param['options']) > 0:
                                    if param['default'] not in [p[1] for p in param['options']]:
                                        param['default'] = param['options'][0][1]
                                params [id] = param
        return params;        
        
    def getResults(self, session_id, run_file):
        self.validateSession() 
        results_json = {
            'session_num': session_id,
            'run_file': run_file
        }
        if (self.authenticated):
            return load_results(results_json, self.headers)
        return ''
