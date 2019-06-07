from .rappturetool import Rappturetool
from ipywidgets import HBox, VBox, HTML, Image, Layout, Button, ButtonStyle, Tab
from hublib import ui
from .plotlywidget import FigureWidget
import math


class CrystalViewerTool (Rappturetool):
    parameters_miller = [            
        'Draw_miller_plane',
        'Draw_plane_1',
        'Miller_index_1_1',
        'Miller_index_1_2',
        'Miller_index_1_3',
        'Draw_plane_2',
        'Miller_index_2_1',
        'Miller_index_2_2',
        'Miller_index_2_3',
        'Draw_plane_3',
        'Miller_index_3_1',
        'Miller_index_3_2',
        'Miller_index_3_3',
    ]
    
    parameters_additional = [
        'What_to_do'
    ]        

    def __init__(self, credentials, parameters, **kwargs):
        kwargs.setdefault('title', 'CrystalViewer')
        Rappturetool.__init__(self, credentials, "crystal_viewer", parameters, extract_method="id", **kwargs)
            
    def displayMillerOptions(self):
        milleropt = VBox(layout=Layout(width='100%', height='100%'))    
        self.millertab = Tab()
        millerchildren = []
        for i in range(0,3):
            container_miller = VBox(layout=Layout(width='100%', height='100%'))    
            mparameters = ['Draw_plane_'+ str(i+1),
            'Miller_index_'+ str(i+1)+'_1',
            'Miller_index_'+ str(i+1)+'_2',
            'Miller_index_'+ str(i+1)+'_3']
            children_miller = []
            for p in mparameters:
                if p in self.parameters_miller :
                    if p in self.options:
                        children_miller.append(self.options[p])
            container_miller.children = children_miller
            millerchildren.append(container_miller)
            self.options['Draw_plane_'+ str(i+1)].dd.observe(lambda b, this=self : this.showMillerPlane(this.options['Draw_miller_plane'].value), 'value')
            
        self.millertab.children = millerchildren
        for i in range(0,3):
            self.millertab.set_title(i, "Plane" + str(i+1))    
        self.options['Draw_miller_plane'].dd.observe(lambda b, this=self : this.showMillerPlane(b['new']), 'value')
        milleropt.children = [self.options['Draw_miller_plane'], self.millertab, self.options_but]
        return milleropt

    def showMillerPlane (self, value):
        enabled = (value == "yes")
        if enabled is True:
            value_display = None
        else:
            value_display = 'none'
        for opt in self.parameters_miller:
            if opt != 'Draw_miller_plane':
                self.options[opt].visible = enabled
                self.options[opt].layout.display = value_display
        for opt in self.parameters_miller:
            if opt != 'Draw_miller_plane':
                self.options[opt].visible = enabled
                self.options[opt].layout.display = value_display            
        self.millertab.visible = enabled
        self.millertab.layout.display = value_display
        if enabled:
            for i in range(0,3):
                mparameters = [
                    'Miller_index_'+ str(i+1)+'_1',
                    'Miller_index_'+ str(i+1)+'_2',
                    'Miller_index_'+ str(i+1)+'_3'
                ]
                enabled = (self.options['Draw_plane_'+ str(i+1)].value == "yes")
                if enabled is True:
                    value_display = None
                else:
                    value_display = 'none'
                for opt in mparameters:
                    if opt in self.options:
                        self.options[opt].visible = enabled
                        self.options[opt].layout.display = value_display

                        

        
class CrystalViewerMaterial (CrystalViewerTool):
    def __init__(self, credentials, **kwargs):
                                            
        self.parameters_structure = [
            '_Structure', 
            'Crystal_structure',
            #'Crystal_system',
            '1','2','3','4','5','6','7','8','9','10','11','12',
            'Nx',
            'Ny',
            'Nz',
            'Primitive_cell',

            'Lx',
            'Ly',
            'Number_of_sheet',
            'C_C_bong_length',
            'Separation_distance',
            'AA_Stacking',
            
            'n',
            'm',
            'num_of_unit_cell',
            'Number_of_sheet',
        ]
        CrystalViewerTool.parameters_miller = CrystalViewerTool.parameters_miller
        self.parameters_additional = self.parameters_additional
        parameters = self.parameters_structure + self.parameters_miller + self.parameters_additional
        kwargs.setdefault('title', 'CrystalViewer - Materials')
        CrystalViewerTool.__init__(self, credentials, parameters, **kwargs)
        self.reset_options = False

    def showMaterial (self, id):
        for i in range(1,13):
            if (i == id):
                self.options[str(i)].visible = True
                self.options[str(i)].layout.display = None
            else:
                self.options[str(i)].visible = False
                self.options[str(i)].layout.display = 'none'
        for opt in ['Nx','Ny','Nz']:
            if id == 8:
                self.options[opt].visible = False
                self.options[opt].layout.display = 'none'
            else:
                self.options[opt].visible = True
                self.options[opt].layout.display = None
                
        for opt in ['Lx','Ly','Number_of_sheet','Separation_distance','AA_Stacking']:
            if id == 8 and self.options['8'].value == '1':
                self.options[opt].visible = True
                self.options[opt].layout.display = None
            else:
                self.options[opt].visible = False
                self.options[opt].layout.display = 'none'
            
        for opt in ['n','m','num_of_unit_cell','Number_of_sheet']:
            if id == 8 and self.options['8'].value == '2':
                self.options[opt].visible = True
                self.options[opt].layout.display = None
            else:
                self.options[opt].visible = False
                self.options[opt].layout.display = 'none'
                
        for opt in ['C_C_bong_length']:
            if id == 8 and ( self.options['8'].value == '2' or self.options['8'].value == '1'):
                self.options[opt].visible = True
                self.options[opt].layout.display = None
            else:
                self.options[opt].visible = False
                self.options[opt].layout.display = 'none'        
                
    def displayOptions(self):
        html = '''
        <b>Visualize crystalline structure of different materials and Bravais lattice</b>
        '''
        container_structure = VBox(layout=Layout(width='100%', height='100%'))
        children_structure = []
        
        children_structure.append(HTML(value=html))

        for p in self.parameters_structure :
            if p in self.options:            
                children_structure.append(self.options[p])
            else:
                children_structure.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))

                               
        self.options['Crystal_structure'].dd.observe(lambda b, this=self : this.showMaterial(int(b['new'])), 'value')

        children_structure.append(self.options_but)
        container_structure.children = children_structure
        #container_introduction.children = children_introduction
        container_miller = self.displayMillerOptions()
        self.showMaterial(1)
        self.showMillerPlane(False)
        crystaltab = Tab()
        
        crystaltab.children = [container_structure, container_miller]
        crystaltab.set_title(0, "Structure")
        crystaltab.set_title(1, "Miller Planes")
                
        self.options_cont.children = [crystaltab]                
        
class CrystalViewerBravais (CrystalViewerTool):
    def __init__(self, credentials, **kwargs):
                                            
        self.parameters_structure = [
            '_Structure', 
            'Crystal_system',
            '_Bravais Lattice',
            '21','22','23','24','25','26','27',
            '_Bravais Lattice Parameters',            
            'a',
            'b',
            'c',
            'Alpha',
            'Beta',
            'Gamma',
            '_Dimension',
            'Nx',
            'Ny',
            'Nz',
        ]
        CrystalViewerTool.parameters_miller = CrystalViewerTool.parameters_miller
        self.parameters_additional = self.parameters_additional
        parameters = self.parameters_structure + self.parameters_additional
        kwargs.setdefault('title', 'CrystalViewer - Bravais')
        CrystalViewerTool.__init__(self, credentials, parameters, **kwargs)
        self.reset_options = False

    def showBravais (self, id):
        options = {
            'a' : [21,22,23,24,25,26,27],
            'b' : [21,22,23],
            'c' : [21,22,23,24,26],
            'Alpha' : [21,27],
            'Beta' : [21,22],
            'Gamma' : [21]
        }

        for d in range (21,28):
            if (id == d):
                self.options[str(d)].visible = True
                self.options[str(d)].layout.display = None
            else:
                self.options[str(d)].visible = False
                self.options[str(d)].layout.display = 'none'

        for key, value in options.items():
            if (id in value):
                self.options[key].visible = True
                self.options[key].layout.display = None
            else:
                self.options[key].visible = False
                self.options[key].layout.display = 'none'
     
                
    def displayOptions(self):
        html = '''
        <b>Visualize crystalline structure of different materials and Bravais lattice</b>
        '''
        container_structure = VBox(layout=Layout(width='100%', height='100%'))
        children_structure = []
        
        children_structure.append(HTML(value=html))

        for p in self.parameters_structure :
            if p in self.options:            
                children_structure.append(self.options[p])
            else:
                children_structure.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))

                               
        self.options['Crystal_system'].dd.observe(lambda b, this=self : this.showBravais(int(b['new'])), 'value')

        children_structure.append(self.options_but)
        container_structure.children = children_structure
        self.showBravais(int(self.options['Crystal_system'].value))
        crystaltab = Tab()
        
        crystaltab.children = [container_structure]
        crystaltab.set_title(0, "Structure")
        crystaltab.set_title(1, "Miller Planes")
                
        self.options_cont.children = [crystaltab]
        self.options[self.parameters_additional[0]].value = '3'
        
class CrystalViewerConstructor (CrystalViewerTool):
    def __init__(self, credentials, **kwargs):
                                            
        self.parameters_structure = [
            '_Structure', 
            'Basis_atom_number',
            
            '_Basis Atoms',             
            'Atom_1_position',
            'Atom_1_type',
            'Atom_2_position',
            'Atom_2_type',
            'Atom_3_position',
            'Atom_3_type',
            'Atom_4_position',
            'Atom_4_type',
            'Atom_5_position',
            'Atom_5_type',
            'Atom_6_position',
            'Atom_6_type',
            'Atom_7_position',
            'Atom_7_type',
            'Atom_8_position',
            'Atom_8_type',
            
            '_Bravais vector',             
            'Vector_1',
            'Vector_2',
            'Vector_3',
            
            '_Define Bond Radius',
            'Bond_radius',

            '_Dimensions',
            'Nx_userdefined',
            'Ny_userdefined',
            'Nz_userdefined',
        ]
        CrystalViewerTool.parameters_miller = CrystalViewerTool.parameters_miller
        self.parameters_additional = self.parameters_additional
        parameters = self.parameters_structure + self.parameters_miller + self.parameters_additional
        kwargs.setdefault('title', 'CrystalViewer - Materials')
        CrystalViewerTool.__init__(self, credentials, parameters, **kwargs)
        self.reset_options = False

    def showAtoms (self, id):
        for i in range(1,9):
            for opt in ['Atom_'+str(i)+'_position', 'Atom_'+str(i)+'_type']:
                if (i <= id):
                    self.options[opt].visible = True
                    self.options[opt].layout.display = None
                else:
                    self.options[opt].visible = False
                    self.options[opt].layout.display = 'none'
     
                
    def displayOptions(self):
        html = '''
        <b>Visualize crystalline structure of different materials and Bravais lattice</b>
        '''
        container_structure = VBox(layout=Layout(width='100%', height='100%'))
        children_structure = []
        
        children_structure.append(HTML(value=html))

        for p in self.parameters_structure :
            if p in self.options:            
                children_structure.append(self.options[p])
            else:
                children_structure.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))

                               
        self.options['Basis_atom_number'].dd.observe(lambda b, this=self : this.showAtoms(int(b['new'])), 'value')

        children_structure.append(self.options_but)
        container_structure.children = children_structure
        container_miller = self.displayMillerOptions()
        self.showAtoms(int(self.options['Basis_atom_number'].value))
        self.showMillerPlane(False)
        crystaltab = Tab()
        
        crystaltab.children = [container_structure, container_miller]
        crystaltab.set_title(0, "Structure")
        crystaltab.set_title(1, "Miller Planes")
                
        self.options_cont.children = [crystaltab]            
        self.options[self.parameters_additional[0]].value = '2'
        