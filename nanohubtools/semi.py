from .rappturetool import Rappturetool
from ipywidgets import HBox, VBox, HTML, Image, Layout, Button, ButtonStyle, Tab
from hublib import ui
from .plotlywidget import FigureWidget
import math


class Driftdiffusionlab (Rappturetool):
    def __init__(self, credentials, **kwargs):
                                            
        self.parameters_structure = [
            '_Structure', 
            'len', 
            'doping', 
            'system',
            'Nd',
            '_Type of Experiment',
            'expt',
        ]
        self.parameters_materials = [
            'material',
            '_Minority carrier lifetimes',
            #'taun',
            #'taup',
            'mob', 
            'mun',
            'mup',
        ]
        self.parameters_ambient = [    
            '_Ambient',
            'temperature',
            'vsweep_high',
            'vn_step',
            'gen',
            'pen',
            'len1',
            'len2',
            '_Surface Recombination',
            'surf',
            'surfn',
            'surfp',
            'surfr',
            'surfnr',
            'surfpr',
        ]
        self.parameters_additional = [
        ]
        parameters = self.parameters_structure + self.parameters_materials + self.parameters_ambient + self.parameters_additional
        Rappturetool.__init__(self, credentials, "semi", parameters, extract_method="id", **kwargs)


        
    def displayOptions(self):
        html = '''
        <b>This tool enables users to explore and teach the basic concepts of P-N junction devices. </b>
        '''
        container_structure = VBox(layout=Layout(width='100%', height='100%'))
        children_structure = []
        container_materials = VBox(layout=Layout(width='100%', height='100%'))
        children_materials = []
        container_ambient = VBox(layout=Layout(width='100%', height='100%'))
        children_ambient = []
        #container_introduction = VBox(layout=Layout(width='100%', height='100%'))
        #children_introduction = []
        
        children_structure.append(HTML(value=html))

        #image = open("intro.png", "rb").read()
        #children_introduction.append(Image(value=image,format='png',width=400))
        
        #parameters = self.parameters_structure + self.parameters_materials + self.parameters_ambient + self.parameters_additional
        for p in self.parameters_structure :
            if p in self.options:            
                children_structure.append(self.options[p])
            else:
                children_structure.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))
        for p in self.parameters_materials :
            if p in self.options:            
                children_materials.append(self.options[p])
            else:
                children_materials.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))
        for p in self.parameters_ambient :
            if p in self.options:            
                children_ambient.append(self.options[p])
            else:
                children_ambient.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))

        self.options['Nd'].visible = False
        self.options['mun'].visible = False
        self.options['mup'].visible = False
        self.options['doping'].dd.observe(lambda b : setattr(self.options['Nd'], 'visible', (b['new'] != "intrinsic")), 'value')
        self.options['mob'].dd.observe(lambda b : setattr(self.options['mun'], 'visible', (b['new'] == "yes")), 'value')
        self.options['mob'].dd.observe(lambda b : setattr(self.options['mup'], 'visible', (b['new'] == "yes")), 'value')

        
        children_materials.append(self.options_but)
        children_structure.append(self.options_but)
        #children_introduction.append(self.options_but)
        children_ambient.append(self.options_but)
        
        
        container_materials.children = children_materials
        container_structure.children = children_structure
        container_ambient.children = children_ambient
        #container_introduction.children = children_introduction

        sqsemitab = Tab()
        sqsemitab.children = [container_structure, container_materials, container_ambient]
        #sqsemitab.set_title(0, "Introduction")
        sqsemitab.set_title(0, "Structure")
        sqsemitab.set_title(1, "Materials")
        sqsemitab.set_title(2, "Environment")
                
        self.options_cont.children = [sqsemitab]
        
