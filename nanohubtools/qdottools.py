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


from .rappturetool import Rappturetool
from ipywidgets import  Tab, Button, Layout, ButtonStyle, VBox, HTML, Image
from hublib import ui

class Qdotexplorer (Rappturetool):
                                                
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
    
    def __init__(self, credentials, parameters, **kwargs):
        self.tool = "qdot"
        Rappturetool.__init__(self, credentials, self.tool, parameters, **kwargs)

    def displayExperiment(self, experiment, disable=[]):
        Rappturetool.displayExperiment(self, experiment, disable+["sequences"])

class SimpleQuantumDot (Qdotexplorer):
    def __init__(self, credentials, **kwargs):
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
        parameters = self.parameters_structure + self.parameters_optical
        kwargs.setdefault('title', 'Simple Quantum-dot lab')                                                            
        Qdotexplorer.__init__(self, credentials, parameters, extract_method="id", **kwargs)
               

        
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
            'shape',
            'dimx',
            'dimy',
            'nstates_cb', 
            'nstates_vb', 
            'modeling',
            'materials_vbcb',
            'strain',
            'bandstructure',
            '_Alloy Distribution', 
            'Alloy_Disorder', 
            'Distribution_Type', 
            'Mole_fraction', 
            'Random_seed', 
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
        self.parameters_layer = [
            '_Substrate',
            'subz',
            '_Wetting Layer',
            'wlz',
            '_Quantum Dot Layer',
            'radius1',
            'radius2',
            'dotx',
            'doty',
            'dotz',
            '_Capping Layer',
            'clz',
        ]
        self.parameters_additional = [
            'structchoice'
        ]
        parameters = self.parameters_structure + self.parameters_optical + self.parameters_layer + self.parameters_additional
        kwargs.setdefault('title', 'Stacked Quantumdot lab')                                                            
        Qdotexplorer.__init__(self, credentials, parameters, extract_method="id", **kwargs)        
        self.options[self.parameters_additional[0]] = ui.String(name='Quantum Dot Structure', value='Multi-Layer Quantum Dot', description='Quantum Dot Structure')
        
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
        container_layer = VBox(layout=Layout(width='100%', height='100%'))
        children_layer = []
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
        for p in self.parameters_layer :
            if p in self.options:            
                children_layer.append(self.options[p])
            else:
                children_layer.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))

        # Setting default values due to rappture inconsistency
        self.options['dotx'].value = 5 
        self.options['doty'].value = 5
        self.options['dotz'].value = 3
                
        self.options['Alloy_Disorder'].dd.observe(lambda b : setattr(self.options['Distribution_Type'], 'visible', (b['new'] == "yes")), 'value')
        self.options['Alloy_Disorder'].dd.observe(lambda b : setattr(self.options['Mole_fraction'], 'visible', (b['new'] == "yes")), 'value')
        self.options['Alloy_Disorder'].dd.observe(lambda b : setattr(self.options['Random_seed'], 'visible', (b['new'] == "yes")), 'value')
        self.options['Distribution_Type'].visible = False
        self.options['Mole_fraction'].visible = False
        self.options['Random_seed'].visible = False

        self.options['radius1'].visible = False
        self.options['radius2'].visible = False
        self.options['shape'].dd.observe(lambda b : setattr(self.options['radius1'], 'visible', (b['new'] == "Cone")), 'value')
        self.options['shape'].dd.observe(lambda b : setattr(self.options['radius2'], 'visible', (b['new'] == "Cone")), 'value')
        self.options['shape'].dd.observe(lambda b : setattr(self.options['dotx'], 'visible', (b['new'] != "Cone")), 'value')
        self.options['shape'].dd.observe(lambda b : setattr(self.options['doty'], 'visible', (b['new'] != "Cone")), 'value')

        
        sqdottab = Tab()
        
        children_layer.append(self.options_but)
        children_optical.append(self.options_but)
        children_structure.append(self.options_but)
        children_introduction.append(self.options_but)
        
        container_layer.children = children_layer
        container_optical.children = children_optical
        container_structure.children = children_structure
        container_introduction.children = children_introduction
        sqdottab.children = [container_introduction, container_structure, container_layer, container_optical]
        sqdottab.set_title(0, "Introduction")
        sqdottab.set_title(3, "Optical")
        sqdottab.set_title(2, "Layers")
        sqdottab.set_title(1, "Structure")
                
        self.options_cont.children = [sqdottab]
        
        