from .rappturetool import Rappturetool
from ipywidgets import HBox, VBox, HTML, Image, Layout, Button, ButtonStyle, Tab
from .plotlywidget import FigureWidget
import math


class PeriodicPotentialLab (Rappturetool):
    def __init__(self, credentials, **kwargs):
                                            
        self.parameters_structure = [
            '_type of Perioodic Potentia', 
            'pot_type', 
            'degree', 
        ]
        self.parameters_energy = [
            '_Energy Parameters',
            'vmax',
            'vmin',
            'emax',
            'vdepth',
            'emin_c',            
            'emax_c',

        ]
        self.parameters_well = [    
            '_Well Geometry',
            'well_width',
            'a',
            'nodes',
            'mass',
            'b_expo',
            "exp_shift",
            "c_gaus",
            "gaus_shift",            
            "a_poly2",
            "b_poly2",
            "poly2_shift",
            "a_poly3",
            "b_poly3",
            "c_poly3",
            "poly3_shift",
            "a_poly4",
            "b_poly4",
            "c_poly4",
            "d_poly4",
            "poly4_shift"
            
        ]
        self.parameters_additional = [
        ]
        parameters = self.parameters_structure + self.parameters_energy + self.parameters_well + self.parameters_additional
        kwargs.setdefault('title', 'Periodic Potential Lab')
        Rappturetool.__init__(self, credentials, "kronig_penney", parameters, extract_method="id", **kwargs)

        
    def displayOptions(self):
        html = '''
        <b>The Periodic Potential Lab solves the time independent Schroedinger equation in a 1D spatial potential variation.</b>
        '''
    
        
        container_structure = VBox(layout=Layout(width='100%', height='100%'))
        children_structure = []
        container_energy = VBox(layout=Layout(width='100%', height='100%'))
        children_energy = []
        container_well = VBox(layout=Layout(width='100%', height='100%'))
        children_well = []
        
        children_structure.append(HTML(value=html))


        for p in self.parameters_structure :
            if p in self.options:            
                children_structure.append(self.options[p])
            else:
                children_structure.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))
        for p in self.parameters_energy :
            if p in self.options:            
                children_energy.append(self.options[p])
            else:
                children_energy.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))
        for p in self.parameters_well :
            if p in self.options:            
                children_well.append(self.options[p])
            else:
                children_well.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))


        sqpotentialtab = Tab()


        
        children_energy.append(self.options_but)
        children_structure.append(self.options_but)
        children_well.append(self.options_but)
        
        container_energy.children = children_energy
        container_structure.children = children_structure
        container_well.children = children_well
        sqpotentialtab.children = [container_structure, container_energy, container_well]
        sqpotentialtab.set_title(0, "Potential type")
        sqpotentialtab.set_title(1, "Energy Details")
        sqpotentialtab.set_title(2, "Well Geometry")
                
        self.options_cont.children = [sqpotentialtab]
        self.showListOptions(self.options["pot_type"].value, self.options["degree"].value)
        self.options['pot_type'].dd.observe(lambda e, this=self: this.showListOptions(e['new'], int(self.options["degree"].value)), 'value')
        self.options['degree'].dd.observe(lambda e, this=self: this.showListOptions(self.options["pot_type"].value, int(e['new'])), 'value')


    def showListOptions (self, type, degree):
    
        listoptions = {}
        listoptions["KP"] = ['vmax', 'vmin', 'emax', 'well_width', 'a', 'mass']
        listoptions["Tri"] = ['vmax', 'vmin', 'emax', 'well_width', 'a', 'mass']
        listoptions["para"] = ['vmax', 'vmin', 'emax', 'well_width', 'mass']
        listoptions["Sine"] = ['vmax', 'vmin', 'emax', 'well_width', 'nodes', 'mass']
        listoptions["gaus"] = ['vmax', 'vmin', 'emax', 'well_width', 'mass', 'c_gaus', 'gaus_shift']
        listoptions["expo"] = ['vmax', 'vmin', 'emax', 'well_width', 'mass', 'b_expo', 'exp_shift']
        listoptions["poly"] = ['degree', 'vmax', 'vmin', 'emax', 'well_width', 'mass']
        listoptions["cola"] = ['vdepth', 'emin_c', 'emax_c', 'well_width', 'a', 'mass']

        listdegree = {}
        listdegree[2] = ["a_poly2","b_poly2","poly2_shift"]
        listdegree[3] = ["a_poly3","b_poly3","c_poly3","poly3_shift"]
        listdegree[4] = ["a_poly4","b_poly4","c_poly4","d_poly4","poly4_shift"]
        
        parameters = [
            'vmax', 'vmin', 'emax', 'well_width', 'a', 'mass', 
            'nodes',
            'c_gaus', 'gaus_shift',
            'b_expo', 'exp_shift',
            'degree',
            'vdepth', 'emin_c', 'emax_c',
            "a_poly2","b_poly2","poly2_shift",
            "a_poly3","b_poly3","c_poly3","poly3_shift",
            "a_poly4","b_poly4","c_poly4","d_poly4","poly4_shift"
        ]
        for opt in parameters:
            visible = False
            ldisplay = "none"
            if (type in listoptions) and (opt in listoptions[type]):
                visible = True
                ldisplay = None
            elif type == "poly":
                if (degree in listdegree) and (opt in listdegree[degree]):
                    visible = True
                    ldisplay = None
            self.options[opt].visible = visible
            self.options[opt].layout.display = ldisplay