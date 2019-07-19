from .rappturetool import Rappturetool, __file__
from ipywidgets import HBox, VBox, HTML, Image, Layout, Button, ButtonStyle, Tab, Output, Box
from IPython.display import HTML, Javascript, clear_output
from hublib import ui
from .plotlywidget import FigureWidget       
import uuid, weakref, inspect, time
import xml.etree.ElementTree as ET
import hashlib, json
import math, os, base64
import numpy as np


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




class InstanceTracker(object):
    __instances__ = weakref.WeakValueDictionary()

    def __init__(self, *args, **kwargs):
        self.__instances__[id(self)]=self

    @classmethod
    def find_instance(cls, obj_id):
        return cls.__instances__.get(obj_id, None)

        
class CrystalViewerSimplified (InstanceTracker, CrystalViewerTool):
    jcpk = {
        'H'  : 'rgb(255,255,255)',
        'He'  : 'rgb(20,20,20)',
        'Li' : 'rgb(188,190,187)',
        'Be' : 'rgb(134,134,134)',
        'B' : 'rgb(122,117,114)',
        'C' : 'rgb(0,0,0)',
        'N' : 'rgb(32,96,255)',
        'O' : 'rgb(238,32,16)',
        'F' : 'rgb(177,146,82)',
        'Ne' : 'rgb(255,0,0)',
        'Na' : 'rgb(218,220,217)',
        'Mg' : 'rgb(195,195,185)',
        'Al' : 'rgb(165,171,176)',
        'Si' : 'rgb(130,126,127)',
        'P' : 'rgb(198,177,86)',
        'S' : 'rgb(248,239,146)',
        'Cl' : 'rgb(213,221,182)',
        'Ar' : 'rgb(221,112,244)',
        'K' : 'rgb(165,171,171)',
        'Ca' : 'rgb(103,105,110)',
        'Sc' : 'rgb(176,173,166)',
        'Ti' : 'rgb(169,163,147)',
        'V' : 'rgb(191,189,202)',
        'Cr' : 'rgb(191,198,206)',
        'Mn' : 'rgb(206,205,200)',
        'Fe' : 'rgb(185,183,184)',
        'Co' : 'rgb(171,163,160)',
        'Ni' : 'rgb(181,165,150)',
        'Cu' : 'rgb(196,78,46)',
        'Zn' : 'rgb(255,0,0)',
        'Ga' : 'rgb(168,177,186)',
        'Ge' : 'rgb(175,176,168)',
        'As' : 'rgb(209,219,221)',
        'Se' : 'rgb(191,71,75)',
        'Br' : 'rgb(154,32,24)',
        'Kr' : 'rgb(164,162,175)',
        'Rb' : 'rgb(122,119,110)',
        'Sr' : 'rgb(217,206,160)',
        'Y' : 'rgb(153,155,154)',
        'Zr' : 'rgb(153,143,133)',
        'Nb' : 'rgb(98,91,138)',
        'Mo' : 'rgb(93,88,85)',
        'Tc' : 'rgb(131,120,116)',
        'Ru' : 'rgb(153,147,149)',
        'Rh' : 'rgb(156,143,135)',
        'Pd' : 'rgb(162,161,157)',
        'Ag' : 'rgb(177,173,170)',
        'Cd' : 'rgb(106,106,104)',
        'In' : 'rgb(127,109,87)',
        'Sn' : 'rgb(126,120,94)',
        'Sb' : 'rgb(127,136,143)',
        'Te' : 'rgb(150,155,158)',
        'I' : 'rgb(95,98,105)',
        'Xe' : 'rgb(0,0,255)',
        'Cs' : 'rgb(167,170,175)',
        'Ba' : 'rgb(62,71,86)',
        'La' : 'rgb(196,184,172)',
        'Ce' : 'rgb(110,101,94)',
        'Pr' : 'rgb(96,91,97)',
        'Nd' : 'rgb(156,154,155)',
        'Pm' : 'rgb(102,102,102)',
        'Sm' : 'rgb(136,117,100)',
        'Eu' : 'rgb(217,213,204)',
        'Gd' : 'rgb(119,129,105)',
        'Tb' : 'rgb(236,241,235)',
        'Dy' : 'rgb(134,121,102)',
        'Ho' : 'rgb(131,123,121)',
        'Er' : 'rgb(177,182,175)',
        'Tm' : 'rgb(168,163,160)',
        'Yb' : 'rgb(0,255,0)',
        'Lu' : 'rgb(160,161,153)',
        'Hf' : 'rgb(171,188,178)',
        'Ta' : 'rgb(154,155,160)',
        'W' : 'rgb(138,131,123)',
        'Re' : 'rgb(123,123,121)',
        'Os' : 'rgb(185,196,200)',
        'Ir' : 'rgb(137,130,112)',
        'Pt' : 'rgb(210,211,205)',
        'Au' : 'rgb(203,152,53)',
        'Hg' : 'rgb(80,46,48)',
        'Tl' : 'rgb(143,141,142)',
        'Pb' : 'rgb(81,81,81)',
        'Bi' : 'rgb(114,106,103)',
        'Po' : 'rgb(139,153,164)',
        'At' : 'rgb(102,102,102)',
        'Rn' : 'rgb(71,132,0)',
        'Fr' : 'rgb(102,102,102)',
        'Ra' : 'rgb(156,152,125)',
        'Ac' : 'rgb(66,73,224)',
        'Th' : 'rgb(80,73,65)',
        'Pa' : 'rgb(154,147,92)',
        'U' : 'rgb(120,122,119)',
        'Np' : 'rgb(90,73,53)',
        'Pu' : 'rgb(200,200,200)',
        'Am' : 'rgb(117,80,28)',
        'Cm' : 'rgb(62,65,58)',
        'Bk' : 'rgb(208,208,208)',
        'Cf' : 'rgb(231,231,231)',
        'Es' : 'rgb(59,163,200)',
        'Fm' : 'rgb(102,102,102)',
        'Md' : 'rgb(102,102,102)',
        'No' : 'rgb(102,102,102)',
        'Lr' : 'rgb(102,102,102)',
        'Rf' : 'rgb(102,102,102)',
        'Db' : 'rgb(102,102,102)',
        'Sg' : 'rgb(102,102,102)',
        'Bh' : 'rgb(102,102,102)',
        'Hs' : 'rgb(102,102,102)',
        'Mt' : 'rgb(102,102,102)',
    }
    
    def __init__(self, credentials, **kwargs):
        InstanceTracker.__init__(self)                                  
        self.parameters_structure = [
            'Nx',
            'Ny',
            'Nz',

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
        self.current_view = "textbook";
        self.hashitem = None;
        self.crystal_component_output = Output(layout=Layout(width="100%", padding="0px"))
        self.parameters_component_output = Output(layout=Layout(height="100%", padding="0px"))
        self.content_component_output = Output(layout=Layout(flex='1', padding="0px", overflow="scroll", border="3px solid rgb(238,238,238)"))
        self.ref = id(self)
        self.parameters_additional = [
            'Primitive_cell',
            'Crystal_structure',
            '1','2','3','4','5','6','7','8','9','10','11','12',            
        ]

        self.parameters_miller = CrystalViewerTool.parameters_miller
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
                self.options[str(i)].value = self.parameters[str(i)]['default']

        for opt in ['Nx','Ny','Nz']:
            if id == 8:
                self.options[opt].visible = False
                self.options[opt].layout.display = 'none'
            else:
                self.options[opt].visible = True
                self.options[opt].layout.display = None
                self.options[opt].value = self.parameters[opt]['default']
                
        for opt in ['Lx','Ly','Number_of_sheet','Separation_distance','AA_Stacking']:
            if id == 8 and self.options['8'].value == '1':
                self.options[opt].visible = True
                self.options[opt].layout.display = None
            else:
                self.options[opt].visible = False
                self.options[opt].layout.display = 'none'
                self.options[opt].value = self.parameters[opt]['default']
            
        for opt in ['n','m','num_of_unit_cell','Number_of_sheet']:
            if id == 8 and self.options['8'].value == '2':
                self.options[opt].visible = True
                self.options[opt].layout.display = None
            else:
                self.options[opt].visible = False
                self.options[opt].layout.display = 'none'
                self.options[opt].value = self.parameters[opt]['default']
                
        for opt in ['C_C_bong_length']:
            if id == 8 and ( self.options['8'].value == '2' or self.options['8'].value == '1'):
                self.options[opt].visible = True
                self.options[opt].layout.display = None
            else:
                self.options[opt].visible = False
                self.options[opt].layout.display = 'none'        
                self.options[opt].value = self.parameters[opt]['default']


    def buildCrystal(self):   
        crystal_component_view = '''
        <style>
        .ComponentMaterialSelected, .ComponentMaterial{
            height: 60px;
            width: 60px;
            border-radius:60px
        }

        .ComponentMaterialSelected, .ComponentMaterial:hover{
            filter:blur(2px);
        }

        .ComponentCrystals{
            display:flex;
            flex-direction:row;
            justify-content:space-between;
        }

        .ComponentMaterials{
            display:flex;
            flex-direction:row;
            justify-content:flex-start;
        }
        
        .materialsTitle{
            display: flex;
            flex-direction: column;
            text-align: center;
            justify-content: center;
            font-size: 24px;        
        }
        
        div.output_subarea{
            padding:0px
        }
                    

        .crystal1{
            background-size: 60px 60px;
            background-image: ''' + self.buildIcon("crystal1.png") + ''';
        }

        .crystal2{
            background-size: 60px 60px;
            background-image: ''' + self.buildIcon("crystal2.png") + ''';
        }

        .crystal3{
            background-size: 60px 60px;
            background-image: ''' + self.buildIcon("crystal3.png") + ''';
        }

        .crystal4{
            background-size: 60px 60px;
            background-image: ''' + self.buildIcon("crystal4.png") + ''';
        }

        .crystal5{
            background-size: 60px 60px;
            background-image: ''' + self.buildIcon("crystal5.png") + ''';
        }

        .crystal6{
            background-size: 60px 60px;
            background-image: ''' + self.buildIcon("crystal6.png") + ''';
        }

        .crystal7{
            background-size: 60px 60px;
            background-image: ''' + self.buildIcon("crystal7.png") + ''';
        }

        .crystal8{
            background-size: 60px 60px;
            background-image: ''' + self.buildIcon("crystal8.png") + ''';
        }

        .crystal9{
            background-size: 60px 60px;
            background-image: ''' + self.buildIcon("crystal9.png") + ''';
        }

        .crystal10{
            background-size: 60px 60px;
            background-image: ''' + self.buildIcon("crystal10.png") + ''';
        }

        .crystal11{
            background-size: 60px 60px;
            background-image: ''' + self.buildIcon("crystal11.png") + ''';
        }

        .crystal12{
            background-size: 60px 60px;
            background-image: ''' + self.buildIcon("crystal12.png") + ''';
        }

        </style>
        <div id="crystal_''' + str(self.ref) + '''"></div>
        '''


        crystal_component_js = '''
        requirejs.config({
            paths: {
                'react': 'https://unpkg.com/react@16.8.6/umd/react.development',
                'react-dom': 'https://unpkg.com/react-dom@16/umd/react-dom.development'
            }
        });

        requirejs(['react', 'react-dom'], function(React, ReactDOM) {
            class Util {
                static create_UUID(){
                    var dt = new Date().getTime();
                    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                        var r = (dt + Math.random()*16)%16 | 0;
                        dt = Math.floor(dt/16);
                        return (c=='x' ? r :(r&0x3|0x8)).toString(16);
                    });
                    return uuid;
                }
            }

 
            class CrystalsComponent extends React.Component {
                constructor(props) {
                    super(props)
                    this.state = { 
                        crystals:{
                            "Diamond":{
                                "materials":["Si","Ge"],
                                "icon": "crystal1",
                                "default":"Si",
                                "value": "1",
                            },
                            "Zincblende":{
                                "materials":["AlP","AlAs","AlSb","GaAs","GaP", "GaSb", "InAs", "InP", "InSb"],
                                "icon": "crystal2",
                                "default":"GaAs",
                                "value": "2",
                            },
                            "Wurtzite":{
                                "materials":["AlN","InN","GaN"],
                                "icon": "crystal3",
                                "default":"GaN",
                                "value": "3",
                            },
                            "Sodium Chloride":{
                                "materials":["NaCl","SmSe"],
                                "icon": "crystal4",
                                "default":"NaCl",
                                "value": "4",
                            },
                            "Cesium Chloride":{
                                "materials":["CsCl"],
                                "icon": "crystal5",
                                "default":"CsCl",
                                "value": "5",
                            },
                            "Face-centered cubic":{
                                "materials":["Cu", "Al","Ag","Au"],
                                "icon": "crystal6",
                                "default":"Cu",
                                "value": "6",
                            },
                            "Body-centered cubic":{
                                "materials":["W"],
                                "icon": "crystal7",
                                "default":"W",
                                "value": "7",
                            },
                            "Carbon meshes":{
                                "materials":["Graphene", "Carbon nanotube", "Bucky ball(C60)"],
                                "icon": "crystal8",
                                "default":"Graphene",
                                "value": "8",
                            },
                            "Rhombohedral":{
                                "materials":["Bi2Te3"],
                                "icon": "crystal9",
                                "default":"Bi2Te3",
                                "value": "9",
                            },
        //                    "Perovskite":{
        //                        "materials":["SrTiO3"],
        //                        "icon": "crystal10",
        //                        "default":"SrTiO3",
        //                        "value": "10",
        //                    },
                            "TMD":{
                                "materials":["MoS2"],
                                "icon": "crystal11",
                                "default":"MoS2",
                                "value": "11",
                            },                     
                            "Black Phosphorous":{
                                "materials":["Black Phosphorous"],
                                "icon": "crystal12",
                                "default":"Black Phosphorous",
                                "value": "12",
                            },                
                        }, 
                        selectedCrystal:"Diamond",
                        selectedMaterial:"Si",
                        showMaterials: true,
                    } 
                }    

                selectCrystal(crystal){
                    this.setState({
                        selectedCrystal:crystal, 
                        selectedMaterial:this.state.crystals[crystal].default,
                        showMaterials: true
                    })
                    CrystalViewerSimplified_''' + str(self.ref) + '''['exposedSelectMaterial'](this.state.crystals[crystal].value, this.state.crystals[crystal].default)
                }

                selectMaterial(material){
                    this.setState({
                        selectedMaterial:material,
                    })
                    var sc = this.state.selectedCrystal
                    CrystalViewerSimplified_''' + str(self.ref) + '''['exposedSelectMaterial'](this.state.crystals[sc].value, material)
                }

                showMaterials( status ){
                    if (status == undefined)
                        status = !this.state.showMaterials
                    this.setState({
                        showMaterials: status
                    })
                }

                render(){
                    var children = Array()    
                    let self = this
                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"materialsTitle"}, "Materials"))
                    for (let crystal in this.state.crystals) {
                        var crystal_instance = this.state.crystals[crystal]
                        let cur_crystal = crystal
                        if (crystal != this.state.selectedCrystal){
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentMaterial " + crystal_instance.icon, style:style, onClick:function(e){self.selectCrystal(crystal)}, title:crystal}))
                        } else {
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentMaterialSelected " + crystal_instance.icon, style:style, onClick:function(e){self.showMaterials()}, title:crystal}))
                        }                
                    }  
                    var mat_children = Array()    
                    if (this.state.showMaterials){
                        var materials = this.state.crystals[this.state.selectedCrystal].materials
                        for (let index in materials) {
                            let material = materials[index]
                            var style = {
                                backgroundSize: "60px 60px",
                                backgroundColor: "#000000",
                                color: "#FFF",
                                fontSize: "20px",
                                display: "flex",
                                alignItems: "center",
                                flexDirection: "row",
                                justifyContent: "center",
                            }
                            if (material != this.state.selectedMaterial){
                                mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentMaterial", style:style, onClick:function(e){self.selectMaterial(material)}, title:material}, material))
                            } else {
                                mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentMaterialSelected", style:style, title:material}, material))
                            }                
                        }            
                    }
                    var crystals = React.createElement("div", {key:Util.create_UUID(), className:"ComponentCrystals"}, children)
                    var materials = React.createElement("div", {key:Util.create_UUID(), className:"ComponentMaterials"}, mat_children)
                    var div = React.createElement("div", {key:Util.create_UUID(), className:"", style:{backgroundColor:'#EEEEEE', padding:'10px'}}, [crystals, materials])
                    return div
                }
            }

            ReactDOM.render(
                React.createElement(CrystalsComponent, {}),
                document.getElementById("crystal_''' + str(self.ref) + '''")
            );
        });
        '''        
       
        return crystal_component_view, crystal_component_js

    def buildIcon(self, icon):
        path = os.path.dirname(__file__)
        image_encoded = ""
        with open(path+"/assets/" + icon,'rb' ) as f:
            image_encoded = f.read()                    
        image = base64.encodebytes(image_encoded).decode("utf-8") 
        html = "url(data:image/png;base64," + str(image).replace("\n", "").replace("=", "") +")"
        return json.loads(json.dumps(html))

        
        
    def buildParameters(self):    
        parameter_component_view = '''
        <style>
        .ComponentOptionSelected, .ComponentOption{
            height: 60px;
            width: 60px;
            border-radius:60px
        }

        .ComponentOptionSelected, .ComponentOption:hover{
            filter:blur(2px);
        }

        .ComponentParameters{
            display:flex;
            flex-direction:column;
            justify-content:flex-start;
        }

        .ComponentOptions{
            display:flex;
            flex-direction:column;
            justify-content:flex-start;
        }
        
        div.output_subarea{
            padding:0px
        }
        
        .viewsTitle {
            display: flex;
            flex-direction: column;
            text-align: center;
            justify-content: center;
            font-size: 24px;   
            padding: 10px;

        }
        </style>
        <div id="parameter_''' + str(self.ref) + '''"></div>
        '''

        parameter_component_js = '''
        requirejs.config({
            paths: {
                'react': 'https://unpkg.com/react@16.8.6/umd/react.development',
                'react-dom': 'https://unpkg.com/react-dom@16/umd/react-dom.development'
            }
        });

        requirejs(['react', 'react-dom'], function(React, ReactDOM) {
            class Util {
                static create_UUID(){
                    var dt = new Date().getTime();
                    var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
                        var r = (dt + Math.random()*16)%16 | 0;
                        dt = Math.floor(dt/16);
                        return (c=='x' ? r :(r&0x3|0x8)).toString(16);
                    });
                    return uuid;
                }
            }

            class ParametersComponent extends React.Component {
                constructor(props) {
                    super(props)
                    let self = this;
                    this.state = { 
                        parameters:{
                            "options":{
                                "children":{},
                                "alt": "#",
                                "icon": "parameters/parameters.png",
                                "label" : "Customize parameters",
                                "action" : function(){ self.displayOptions() },
                            },
                            "textbook":{
                                "children":{},
                                "alt": "TB",
                                "icon": "parameters/textbook.png",
                                "label" : "textbook cell",
                                "action" : function(){ self.displayTextBook() },
                            },
                            "unitcell":{
                                "children":{},
                                "alt": "UC",
                                "icon": "parameters/unitcell.png",
                                "label" : "Unit cell",
                                "action" : function(){ self.displayUnitCell() },
                            },
                            "bravais":{
                                "children":{},
                                "alt": "BR",
                                "icon": "parameters/bravais.png",
                                "label" : "Bravais structure",
                                "action" : function(){ self.displayLattice() },
                            },
                            "miller":{
                                "children":{
                                    "100":{
                                        "icon": "parameters/miller100.png",
                                        "alt": "100",
                                        "label" : "Miller planes (100)",
                                        "action" : function(){ self.todo() },
                                    },                        
                                    "010":{
                                        "icon": "parameters/miller010.png",
                                        "alt": "010",
                                        "label" : "Miller planes (010)",
                                        "action" : function(){ self.todo() },
                                    },                        

                                    "001":{
                                        "icon": "parameters/miller001.png",
                                        "alt": "001",
                                        "label" : "Miller planes (001)",
                                        "action" : function(){ self.todo() },
                                    },  
                                    //"111":{
                                    //   "icon": "parameters/miller111.png",
                                    //    "alt": "111",
                                    //    "label" : "Miller planes (111)",
                                    //    "action" : function(){ self.todo() },
                                    //},    
                                },
                                "icon": "parameters/miller.png",
                                "label" : "Miller planes",
                                "alt": "MP",
                                "action" : function(){ self.todo() },
                            },
                        }, 
                        selectedParameter:"textbook",
                        selectedOption:undefined,
                    } 
                }    

                todo(){
                    CrystalViewerSimplified_''' + str(self.ref) + '''["exposedTest"]("TODO", "TODO");
                }

                displayOptions(){
                    CrystalViewerSimplified_''' + str(self.ref) + '''["exposedDisplayOptions"]();
                }

                displayTextBook(){
                    CrystalViewerSimplified_''' + str(self.ref) + '''["exposedDisplayTextBook"]();
                }
                
                displayUnitCell(){
                    CrystalViewerSimplified_''' + str(self.ref) + '''["exposedDisplayUnitCell"]();
                }
                
                displayLattice(){
                    CrystalViewerSimplified_''' + str(self.ref) + '''["exposedDisplayLattice"]();
                }
                
                selectParameter(parameter){
                    this.setState({
                        selectedParameter:parameter, 
                        selectedOptiont:undefined,
                    })
                    CrystalViewerSimplified_''' + str(self.ref) + '''["exposedTest"](parameter, "TODO")
                }

                selectOption(option){
                    this.setState({
                        selectedOptiont:option,
                    })
                    CrystalViewerSimplified_''' + str(self.ref) + '''["exposedTest"](option, "TODO")
                }

                callOption(option){
                    this.selectOption(option)
                    var parameter = this.state.parameters[this.state.selectedParameter].children[option]
                    this.callbackParameter(parameter)
                }

                callbackParameter(parameter){
                   console.log(parameter)
                    if (parameter.action){
                       parameter.action() 
                    }
                }

                callParameter(param){
                    this.selectParameter(param)
                    var parameter = this.state.parameters[param]
                    this.callbackParameter(parameter)
                }



                render(){
                    var children = Array()    
                    var style = {
                        //backgroundSize: "60px 60px",
                        //backgroundImage: "url(" + crystal_instance.icon + ")",
                        backgroundColor: "#000000",
                        color: "#FFF",
                        fontSize: "20px",
                        display: "flex",
                        alignItems: "center",
                        flexDirection: "row",
                        justifyContent: "center",
                    }       
                    let self = this
                    for (let parameter in this.state.parameters) {
                        let parameter_instance = this.state.parameters[parameter]
                        if (parameter != this.state.selectedParameter){
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOption", style:style, onClick:function(e){self.callParameter(parameter)}, title:parameter_instance.label}, parameter_instance.alt))
                        } else {
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSelected", style:style, title:parameter_instance.label}, parameter_instance.alt))
                        }                
                    }  

                    var mat_children = Array()    

                    if (this.state.selectedParameter){
                        var opts = this.state.parameters[this.state.selectedParameter].children
                        for (let option in opts) {
                            let parameter_instance = opts[option]
                            if (option != this.state.selectedOption){
                                mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOption", style:style, onClick:function(e){self.callOption(option)}, title:parameter_instance.label}, parameter_instance.alt))
                            } else {
                                mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSelected", style:style, title:parameter_instance.label}, parameter_instance.alt))
                            }                
                        }            
                    }
                    var components = React.createElement("div", {key:Util.create_UUID(), className:"ComponentParameters", style:{width:"60px"}}, children)
                    var options = React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptions", style:{width:"60px"}}, mat_children)

                    var opt = React.createElement("div", {key:Util.create_UUID(), className:"", style:{display:"flex", flexDirection:"row", backgroundColor:'#EEEEEE', justifyContent:'flex-start', padding:'10px', height:'700px'}}, [components, options])
                    var title = React.createElement("div", {key:Util.create_UUID(), className:"", style:{
                        backgroundColor:'#FFFFFF', 
                        padding:'20px', 
                        lineHeight:'normal', 
                        width:'140px', 
                        height:'140px', 
                        fontSize:'30px', 
                        display:'flex',
                        flexDirection: 'column',
                        justifyContent: 'center',
                        textAlign: 'center' 
                    }}, "Crystal Viewer")
                    var views = React.createElement("div", {key:Util.create_UUID(), className:"viewsTitle"}, "Views")
                    var div = React.createElement("div", {key:Util.create_UUID(), className:"", style:{display:"flex", flexDirection:"column", backgroundColor:'#EEEEEE', justifyContent:'flex-start', padding:'10px', height:'700px'}}, [title, views, opt])
                    return div
                }
            }

            ReactDOM.render(
                React.createElement(ParametersComponent, {}),
                document.getElementById("parameter_''' + str(self.ref) + '''")
            );
        });
        '''      
        return parameter_component_view, parameter_component_js;

        
    def displayFrame(self):
        crystal_component_view, crystal_component_js = self.buildCrystal()
        parameter_component_view, parameter_component_js = self.buildParameters()
        
        with self.crystal_component_output:
            display(HTML(crystal_component_view))
            display(Javascript(crystal_component_js)) 
    
        with self.parameters_component_output:
            display(HTML(parameter_component_view))
            display(Javascript(parameter_component_js)) 
          
    def exposedTest(self, value1, value2):
        with self.content_component_output:
            display("Value1 = " , value1)
            display("Value2 = " , value2)
            
    def buildInterfaceJS(self):
        interface_js = "<script type='text/Javascript'>\n";
        refobj = "CrystalViewerSimplified_" + str(self.ref)
        interface_js += "var " + refobj + " = {};\n";
        for method in inspect.getmembers(self, predicate=inspect.ismethod):
            if (method[0].startswith("exposed")):
                interface_js += refobj + "['" + method[0] + "'] = function ("
                for i, parameter in enumerate (inspect.signature(method[1]).parameters):
                    if (i==0):
                        interface_js += parameter
                    else:
                        interface_js += ", " + parameter
                interface_js += "){\n";
                interface_js += "    var command = 'from nanohubtools import CrystalViewerSimplified ; CrystalViewerSimplified.find_instance("+ str(self.ref) + ")." + method[0] +"(";
                for i, parameter in enumerate (inspect.signature(method[1]).parameters):
                    if (i==0):
                        interface_js += "\\'' + String(" + parameter + ") + '\\'"
                    else:
                        interface_js += ", \\'' + String(" + parameter + ") + '\\'"
                interface_js += ")';\n";
                interface_js += "    console.log('Egetxecuting Command: ' + command);\n"
                interface_js += "    var kernel = IPython.notebook.kernel;\n"
                interface_js += "    kernel.execute(command);\n"
                interface_js += "}\n";
        interface_js+='</script>\n'
        return interface_js
    
    def refreshView(self):
        if (self.current_view == "options"):
            self.exposedDisplayOptions()
        elif (self.current_view == "textbook"):
            self.exposedDisplayTextBook()
        elif (self.current_view == "unitcell"):
            self.exposedDisplayUnitCell()
        elif (self.current_view == "lattice"):
            self.exposedDisplayLattice()


    def displayWindow(self):   
        self.displayFrame()
        display(HTML(self.buildInterfaceJS()))
        with self.window:
            clear_output()
            #display(self.options_cont)
            display(HBox([
                
                self.parameters_component_output,
                VBox([
                    self.crystal_component_output,
                    self.content_component_output
                ], layout=Layout(flex='1', height="100%"))
            ], layout=Layout(flexDirection="row", width="100%", height="700px")))
            
            
                
    def displayOptions(self):
        container_structure = VBox(layout=Layout(width='100%', height='100%'))
        children_structure = []
        for p in self.parameters_structure :
            if p in self.options:            
                children_structure.append(self.options[p])
            else:
                children_structure.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))

                               
        self.options['Crystal_structure'].dd.observe(lambda b, this=self : this.showMaterial(int(b['new'])), 'value')

        container_structure.children = children_structure
        container_miller = self.displayMillerOptions()
        self.showMaterial(1)
        self.options_cont.children = [container_structure]
        self.getCache()
        self.refreshView()
        
        
    def getCurrentParameters(self):
        parameters = {}
        
        for ii in [str(i) for i in range(1,13)]:
            if (ii != self.options["Crystal_structure"].value):
                self.options[ii].value == self.options[ii].dd.options[0]      
        for key, val in self.options.items():
            units = ''
            if key in self.parameters and self.parameters[key]['units'] is not None:
                units = str(self.parameters[key]['units'])
            parameters[key] = str(val.value) + units
        return parameters;
    

    def getCache(self):
        parameters = self.getCurrentParameters()
        hashtable = {
            "cf1685e7cd459224f1d203d3761022afbf176f70" : "1502990",
            "8831a61c006993ebeacfe7316d24d7126e080ec7" : "1503012",
            "52bd08a2f5e88416bb7fda807751ae69ca290b4f" : "1503014",
            "7f8f9661b0abde0102ac67a9dad43918540f66e5" : "1503015",
            "4a6b04a5d0a03177c7159eb6c0fd0257abc0cc0f" : "1503016",
            "136065ff2b5820abedf22cf7f7a9683d3366663d" : "1503017",
            "5b7c10fb7749e1f2aa17ac747b63d625ac7c6804" : "1503018",
            "33f0dc16b5f9aa536ec4d38d5eced2fe71da7546" : "1503019",
            "860ee8337393529abce6734d618f6d183617b072" : "1503020",
            "820d1103def6b49e4acb7cc3c96e8822cece0869" : "1503811",
            "e48ff7a6c702f3c57d2b4034bd7a72ba0dd6352a" : "1503026", #????
        }

        hashstr =  json.dumps(parameters, sort_keys=True).encode()
        
        hashitem = hashlib.sha1(hashstr).hexdigest()
        if self.hashitem != hashitem:   
            if hashitem in hashtable:
                session_id = hashtable[hashitem]
                status = self.session.checkStatus(session_id) 
            else:
                with self.content_component_output:
                    clear_output()  
                    print("LOADING CACHE ....")
                driver_json = self.generateDriver( {'parameters':parameters } )
                session_id = self.session.getSession(driver_json)
                with self.content_component_output:            
                    print ("new", hashitem, session_id)
                    status = self.session.checkStatus(session_id) 
                    loading = True
                    while loading == True:
                        if 'success' in status and status['success'] and 'finished' in status and status['finished'] and status['run_file'] != "":
                            loading = False
                        else:    
                            print ("Loading", session_id)
                            time.sleep(5);
                            status = self.session.checkStatus(session_id) 

            xml = self.session.getResults(session_id, status['run_file'])            
            xml = ET.fromstring(xml)
            results = xml.find('output')
            drawings = results
            self.textbook = None;#drawings[0]
            self.lattice = None;#drawings[1]
            self.unitcell = None;#drawings[2] 
            for drawing in drawings:
                text = self.getText(drawing, ['about', 'label'])
                if text == "Basis":
                    self.unitcell = drawing
                elif text == "Lattice grid":
                    self.lattice = drawing
                elif text == "Text book unit cell":
                    self.textbook = drawing
            with self.content_component_output:
                clear_output()  
            self.hashitem = hashitem
            
    def exposedDisplayOptions(self):
        self.getCache()
        self.current_view = "options"
        with self.content_component_output:
            clear_output()
            display(self.options_cont)
     
    def exposedDisplayTextBook(self):
        self.getCache()        
        self.current_view = "textbook"
        with self.content_component_output:
            clear_output();
        if self.textbook != None:
            self.plotDrawing(self.textbook,self.content_component_output)
    
    def exposedDisplayUnitCell(self):
        self.getCache()        
        self.current_view = "unitcell"
        with self.content_component_output:
            clear_output();
        if self.unitcell != None:
            self.plotDrawing(self.unitcell,self.content_component_output)

    def exposedDisplayLattice(self):
        self.getCache()        
        self.current_view = "lattice"
        with self.content_component_output:
            clear_output();
        if self.lattice != None:
            self.plotDrawing(self.lattice,self.content_component_output)

    def exposedSelectCrystal(self, crystal):
        if (self.options["Crystal_structure"].value != crystal):
            self.options["Crystal_structure"].value = crystal;
            self.getCache()
            self.refreshView()

    def exposedSelectMaterial(self, crystal, material):
        if (self.options["Crystal_structure"].value != crystal or self.options[crystal].value != material):
            self.options["Crystal_structure"].value = crystal;
            self.options[crystal].value = material;
            self.getCache()
            self.refreshView()

    def plotDrawing(self, draw, out):
        label = self.getText(draw, ["index", "label"])
        if out == None:
            out = Floatview(title=label, mode = 'split-bottom')
        out.clear_output()     
        layout = { 'height' : 600, 'scene':{'aspectmode':'data'}, 'margin' : {'l':0,'r':0,'t':0,'b':0} }
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
                        atoms[int(cols[1])] = [float(cols[5]),float(cols[6]),float(cols[7]), cols[2],CrystalViewerSimplified.jcpk[cols[2]], "enabled"]
                    elif line.startswith("CONECT"):
                        cols = line.split()
                        connections[int(cols[1])] = [int(c) for c in cols[2:]]
            else:
                vtk = molecule.find('vtk')
                if vtk is not None:
                    jcpkkeys = list(CrystalViewerSimplified.jcpk.keys())
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
                                    if atom_id in atoms and pp[k] <= len(CrystalViewerSimplified.jcpk):
                                        atoms[atom_id][3] = jcpkkeys[pp[k]-1] 
                                        atoms[atom_id][4] = CrystalViewerSimplified.jcpk[atoms[atom_id][3]]

                        i = i+1
            xt = None
            yt = None
            zt = None
            st = None
            color = {}
            colorset = set()
            for id, atom in atoms.items():
                colorset.add(atom[3])
            colorset = list(colorset)
        
            xt = {}
            yt = {}
            zt = {}
            st = {}

            for id, atom in atoms.items():
                if atom[5] == "enabled" and (atom[3] not in ["He","Yb","Xe","Zn"]):
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
                
                colorscalea = [[0,CrystalViewerSimplified.jcpk[atom]], [1,CrystalViewerSimplified.jcpk[atom]]]

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
                   
            
            xt = {}
            yt = {}
            zt = {}
            st = {}
            for c in colorset:
               xt[c]=[]
               yt[c]=[]
               zt[c]=[]
               st[c]=[]
               
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
                    atm1 = atoms[at1][3]
                    if atm1 == "He":
                        atm1 = atoms[at2][3]
                    atm2 = atoms[at2][3]
                    if atm1 != atm2:
                        for i in range(sample):
                            id = None
                            if i <= sample/2:
                                id = atm2
                            else:
                                id = atm1
                            xt[id].append((Rappturetool.cosphi*v1[0] + Rappturetool.sinphi*v2[0] + xd[i]).tolist())
                            yt[id].append((Rappturetool.cosphi*v1[1] + Rappturetool.sinphi*v2[1] + yd[i]).tolist())
                            zt[id].append((Rappturetool.cosphi*v1[2] + Rappturetool.sinphi*v2[2] + zd[i]).tolist())
                        xt[atm2].append([])
                        zt[atm2].append([])
                        yt[atm2].append([])
                        xt[atm1].append([])
                        zt[atm1].append([])
                        yt[atm1].append([])
                    else:
                        for i in range(sample):
                            id = atm1
                            xt[id].append((Rappturetool.cosphi*v1[0] + Rappturetool.sinphi*v2[0] + xd[i]).tolist())
                            yt[id].append((Rappturetool.cosphi*v1[1] + Rappturetool.sinphi*v2[1] + yd[i]).tolist())
                            zt[id].append((Rappturetool.cosphi*v1[2] + Rappturetool.sinphi*v2[2] + zd[i]).tolist())
                        xt[atm1].append([])
                        zt[atm1].append([])
                        yt[atm1].append([])
                   
            for c in colorset:    
                opacity = 1.0
                if c == "He":
                    opacity = 0.2
                trace = { 
                    'type':'surface',
                    'x': xt[c], 
                    'y': yt[c], 
                    'z': zt[c], 
                    'text' : '',    
                    'showscale' : False,
                    'hoverinfo' : 'text',
                    'colorscale' : [[0,CrystalViewerSimplified.jcpk[c]], [1,CrystalViewerSimplified.jcpk[c]]],
                    'connectgaps' : False,
                    'opacity' : opacity
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
            #self.fig = fig

        with out:            
            display(fig)
        return fig        