from .rappturetool import Rappturetool
from ipywidgets import HBox, VBox, HTML, Image, Layout, Button, ButtonStyle, Tab, Dropdown 
from .nanohubtools import TextArea
from hublib import ui

from .plotlywidget import FigureWidget
import math


class DFTExplorer (Rappturetool):
    def __init__(self, credentials, **kwargs):
                                            
        self.parameters_structure = [
            '_STRUCTURE', 
            'cartesian', 
            'structure',
            'title',
            'indeck',
            'lattice_vectors',
            'lat_param_a',
            'lat_param_c_a',
            'lat_param_b_a',
        ]
        self.parameters_energy = [
            'approx',
            'relax',
            'ion_dynam',
            'cell_dynam',
            
            'nbnd',
            'ke_cutoff',
            'ke_cutoff_potential',
            'convergence',
            'scf_maxstep',

            '_K-grid spacing(reciprocal-space)',
            'x_size',
            'y_size',
            'z_size',
            '_Additional parameters', 
            'occupation_enable',
            'occupations',
            'smearing',
            'degauss',

            'mixing_enable',
            'mixing_mode',
            'mixing_beta',
        ]
        self.parameters_phonons = [
            '_PHONON',
            'phonon',
            'phonon_calc',
            'atomic_mass',
            'phonon_convergence',
            'eps',
            'q_point',
            #'x_size',
            #'y_size',
            #'z_size',
            'q_path',
            'q_num',
        ]
        
        self.parameters_bandstructure = [
            
            '_BANDSTRUCTURE',
            'bandstructure',
            'k_path',
            'k_num',
            'dos',
            'dos_min_E',
            'dos_max_E',   
            'dos_delta_E',
            
        ]
        
        self.parameters_advanced = [
            '_ADVANCED',
            'venue',
            'num_nodes',
            'walltime',            
        ]

        self.parameters_additional = [
            'ppots'
        ]
        parameters = self.parameters_structure + self.parameters_energy + self.parameters_phonons + self.parameters_bandstructure + self.parameters_advanced + self.parameters_additional
                
        kwargs.setdefault('title', 'DFT calculations with Quantum ESPRESSO')
        Rappturetool.__init__(self, credentials, "dftqe", parameters, extract_method="id", **kwargs)
        self.parameters["ppots"] = {'units':'', 'default':'', 'type': 'string', 'label': 'Potentials', 'id':'ppots'}
        self.reset_options = False

    def loadExamples(self, list_examples=["geometry"] ):
        parameterslist = self.parameters_structure + self.parameters_energy + self.parameters_phonons + self.parameters_bandstructure + self.parameters_advanced + self.parameters_additional
   
        listoptions = {}
        if (self.session):
            inputs = self.xml.find('input')
            for elem in inputs.iter():
                if elem.tag == "loader" and 'id' in elem.attrib:
                    loader = elem
                    id = loader.attrib['id']
                    if (id in list_examples):
                        examples = loader.find("examples")
                        if examples is not None:
                            for run in examples.findall("run"):  
                                about = run.find('about')
                                if about is not None:
                                    label = about.find('label')
                                    if label is not None and label.text != "":
                                        listoptions[label.text] = {}
                                        if (self.extract_method == "id"):
                                            parameters = self.extractParametersById(parameterslist, run, False)
                                        else:
                                            parameters = self.extractParameters(parameterslist, run, False)
                                        for key, parameter in parameters.items():
                                            if parameter["current"] is None:
                                                if parameter["default"] is not None:
                                                    listoptions[label.text][key] = parameter["default"].strip()
                                            else:
                                                listoptions[label.text][key] = parameter["current"].strip()
        return listoptions;                                           

    def loadExample(self, example):
        with self.debug_output:
            if example in self.examples:
                options = self.examples[example]
                for k, v in options.items():
                    if k in self.options:
                        try:
                            self.options[k].value = v
                        except:
                            try:
                                if hasattr(self.options[k], 'dd'):
                                    if hasattr(self.options[k].dd, 'options'):
                                        for opt in self.options[k].dd.options:
                                            if opt[0] == v:
                                                self.options[k].value = opt[1]
                                                break                                            
                            except:
                                pass;
        
    
    def displayOptions(self):
        html = '''
        <b>DFT calculations with Quantum ESPRESSO</b>
        '''
    
        
        container_structure = VBox(layout=Layout(width='100%', height='100%'))
        container_energy = VBox(layout=Layout(width='100%', height='100%'))
        container_phonons = VBox(layout=Layout(width='100%', height='100%'))
        container_bandstructure = VBox(layout=Layout(width='100%', height='100%'))
        container_advanced = VBox(layout=Layout(width='100%', height='100%'))

        children_structure = []        
        children_structure.append(HTML(value=html))
        optl = [""]
        self.examples = self.loadExamples(["geometry"])
        for k,v in self.examples.items():
            optl.append(k)
        geometry_header = (Button(description="Calculation templates",layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))
        geometry = Dropdown(name="", description="", value="", options=optl)
        self.options['ppots']= TextArea(name="Potentials", value="", description="Potentials")
        geometry.observe(lambda e, this=self: this.loadExample(e['new']), "value")
        children_structure.append(geometry_header)
        children_structure.append(geometry)
        children_structure.append(self.options['ppots'])
        
        
        children_energy = []        
        children_phonons = []        
        children_bandstructure = []        
        children_advanced = []        

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

        for p in self.parameters_phonons :
            if p in self.options:            
                children_phonons.append(self.options[p])
            else:
                children_phonons.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))

        for p in self.parameters_bandstructure :
            if p in self.options:            
                children_bandstructure.append(self.options[p])
            else:
                children_bandstructure.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))

        for p in self.parameters_advanced  :
            if p in self.options:            
                children_advanced .append(self.options[p])
            else:
                children_advanced .append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))
                
        children_structure.append(self.options_but)
        children_energy.append(self.options_but)
        children_phonons.append(self.options_but)
        children_bandstructure.append(self.options_but)
        children_advanced.append(self.options_but)
        
        container_structure.children = children_structure
        container_energy.children = children_energy
        container_phonons.children = children_phonons
        container_bandstructure.children = children_bandstructure
        container_advanced.children = children_advanced
        sqdftqetab = Tab()
        sqdftqetab.children = [
            container_structure,
            container_energy,
            container_phonons,
            container_bandstructure,
            container_advanced,
        ]
        
        sqdftqetab.set_title(0, "Structure")                
        sqdftqetab.set_title(1, "Energy")                
        sqdftqetab.set_title(2, "Phonons")                
        sqdftqetab.set_title(3, "Bandstructure")                
        sqdftqetab.set_title(4, "Advanced")                        
        self.options['occupation_enable'].dd.observe(lambda e, this=self: this.showListOptions(e['new'], 'occupation_enable'), 'value')
        self.showListOptions(self.options['occupation_enable'].value, 'occupation_enable')

        self.options['mixing_enable'].dd.observe(lambda e, this=self: this.showListOptions(e['new'], 'mixing_enable'), 'value')
        self.showListOptions(self.options['mixing_enable'].value, 'mixing_enable')

        self.options['phonon'].dd.observe(lambda e, this=self: this.showListOptions(e['new'], 'phonon'), 'value')
        self.showListOptions(self.options['phonon'].value, 'phonon')

        self.options['bandstructure'].dd.observe(lambda e, this=self: this.showListOptions(e['new'], 'bandstructure'), 'value')
        self.showListOptions(self.options['bandstructure'].value, 'bandstructure')

        self.options['dos'].dd.observe(lambda e, this=self: this.showListOptions(e['new'], 'dos'), 'value')
        self.showListOptions(self.options['dos'].value, 'dos')
        
        self.options_cont.children = [sqdftqetab]

    def showListOptions (self, status, key):
        listoptions = {}
        listoptions['occupation_enable'] = ['occupations','smearing','degauss']
        listoptions['mixing_enable'] = ['mixing_mode','mixing_beta']
        listoptions['phonon'] = ['phonon_calc','atomic_mass','phonon_convergence','eps','q_point','q_path','q_num']
        listoptions['bandstructure'] = ['k_path','k_num']
        listoptions['dos'] = ['dos_min_E','dos_max_E','dos_delta_E']
        
        visible = (status == "yes")
        ldisplay = "none"
        if visible:
            ldisplay = None        
        for opt in listoptions[key]:
            self.options[opt].visible = visible
            self.options[opt].layout.display = ldisplay
