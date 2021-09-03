from .rappturetool import Rappturetool
from ipywidgets import HBox, VBox, Layout, Button, ButtonStyle, Tab, Output, Image
from IPython.display import Javascript, clear_output
from IPython.display import HTML as IHTML      
from IPython.display import display
import xml.etree.ElementTree as ET
from plotly.graph_objs import FigureWidget
from .crystalsimplified import InstanceTracker
from hashlib import sha1 
from json import loads, dumps
from os import path as ospath
from base64 import encodebytes
import inspect
from time import sleep
from datetime import datetime
from hublib.ui.numvalue import NumValue, Number
   
class PeriodicPotentialLabSimplified (InstanceTracker, Rappturetool):
    def __init__(self, credentials, **kwargs):
        InstanceTracker.__init__(self)                                  
        self.parameters_structure = [
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
            'degree',             
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
            'pot_type',         
        ]
        self.history = {}
        self.current_view = "option8a"
        self.hashitem = None;
        self.hashtable = {}        
        self.ref = id(self)        
        self.header_component_output = Output(layout=Layout(width="100%", padding="0px"))        
        self.parameters_component_output = Output(layout=Layout(height="100%", padding="0px"))
        self.content_component_output = Output(layout=Layout(flex='1', padding="0px", overflow="scroll"))        
        self.theme = "plotly"
        
        self.fig = FigureWidget(
            data= [],
            layout= { 
                'height' : 550,                 
                'margin' : {
                    'b' : 40,
                    't' : 80,
                    'l' : 60,
                    'r' : 40,
                },
                'showlegend':False,                
                'xaxis' : {
                    'exponentformat' :  "e",
                    
                },
                'yaxis' : {
                    'exponentformat' :  "e",
                },
                'template' : self.theme,                
            }
        )  

        
        
        parameters = self.parameters_structure + self.parameters_energy + self.parameters_well + self.parameters_additional
        kwargs.setdefault('title', 'Periodic Potential Lab')
        Rappturetool.__init__(self, credentials, "kronig_penney", parameters, extract_method="id", **kwargs)

        
    def exposedChangeTheme(self, theme):
        self.updateTheme(theme)
        
    def updateTheme(self, theme):
        if (theme != self.theme and (theme == "plotly_white" or theme == "plotly_dark"or theme == "plotly")):
            self.theme = theme
            data = []
            for t in self.fig.data:
                if self.theme == "plotly_dark" and t["line"]["color"] == "black":
                    data.append({"line": {"color": "white"}})
                elif self.theme != "plotly_dark" and t["line"]["color"] == "white":
                    data.append({"line": {"color": "black"}})
                else:
                    data.append({})
            self.fig.update({'layout':{'template':self.theme}, 'data':data});

        
    def displayOptions(self):
        self.options['c_gaus'] = Number(
            value=self.options['c_gaus'].value, 
            name="Standard deviation of Gaussian measured in distance (c)",
            min=self.options['c_gaus'].min,
            max=self.options['c_gaus'].max,
            units="angstrom"
        )
        
        self.options['b_expo'] = Number(
            value=self.options['b_expo'].value, 
            name="Inverse of the potential decay length (b)",
            min=self.options['b_expo'].min,
            max=self.options['b_expo'].max,
            units="1/angstrom"
        )        
            
        container_energy = VBox(layout=Layout(width='100%', height='100%'))
        children_energy = []
        container_well = VBox(layout=Layout(width='100%', height='100%'))
        children_well = []    

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


        sqpotentialtab = Tab([], layout=Layout(flex="1"))
        
        container_energy.children = children_energy
        container_well.children = children_well
        sqpotentialtab.children = [container_energy, container_well]
        sqpotentialtab.set_title(0, "Energy Details")
        sqpotentialtab.set_title(1, "Well Geometry")

        self.options['vmax'].value = 3
        self.options['c_gaus'].value = 6
        self.options['gaus_shift'].value = 50
        self.options['exp_shift'].value = 50
        self.options['b_expo'].value = 0.16

        self.default_options = {}
        for ii in self.options.keys():
            self.default_options[ii] = self.options[ii].value        
        
        desc_container = VBox([], layout=Layout(width="300px"))
        list_images = []
        for descname in [
            "pot_desc1",
            "pot_desc2",
            "pot_desc3",
            "pot_desc4",
            "pot_desc5",
            "pot_desc6",
            "pot_desc7",
            "pot_desc8",
            "pot_desc9",
            "pot_desc10",
            "pot_desc11",
        ]:
            path = ospath.dirname(__file__)
            image_encoded = ""
            with open(path+"/assets/" + descname + ".png",'rb') as f:
                self.options[descname] = Image(
                    value=f.read(),
                    format='png',
                    width=300,
                )
                list_images.append(self.options[descname])
                self.options[descname].layout.display = 'none'
                self.options[descname].visible = None
                      
        desc_container.children = list_images
        self.options_cont.children = [HBox([sqpotentialtab, desc_container])]
        
        self.showListOptions(self.options["pot_type"].value, self.options["degree"].value)
        self.options['pot_type'].dd.observe(lambda e, this=self: this.showListOptions(e['new'], int(self.options["degree"].value)), 'value')
        self.options['degree'].dd.observe(lambda e, this=self: this.showListOptions(self.options["pot_type"].value, int(e['new'])), 'value')
        self.getCache()
        self.refreshView()
        
    def showListOptions (self, type, degree):
    
        listoptions = {}
        listoptions["KP"] = ['vmax', 'vmin', 'emax', 'well_width', 'a', 'mass', 'pot_desc1']
        listoptions["Tri"] = ['vmax', 'vmin', 'emax', 'well_width', 'a', 'mass', 'pot_desc3']
        listoptions["para"] = ['vmax', 'vmin', 'emax', 'well_width', 'mass', 'pot_desc4']
        listoptions["Sine"] = ['vmax', 'vmin', 'emax', 'well_width', 'nodes', 'mass', 'pot_desc2']
        listoptions["gaus"] = ['vmax', 'vmin', 'emax', 'well_width', 'mass', 'c_gaus', 'gaus_shift', 'pot_desc7']
        listoptions["expo"] = ['vmax', 'vmin', 'emax', 'well_width', 'mass', 'b_expo', 'exp_shift', 'pot_desc6']
        listoptions["poly"] = ['degree', 'vmax', 'vmin', 'emax', 'well_width', 'mass']
        listoptions["cola"] = ['vdepth', 'emin_c', 'emax_c', 'well_width', 'a', 'mass', 'pot_desc5']

        listdegree = {}
        listdegree[1] = ['pot_desc8']
        listdegree[2] = ["a_poly2","b_poly2","poly2_shift",'pot_desc9']
        listdegree[3] = ["a_poly3","b_poly3","c_poly3","poly3_shift",'pot_desc10']
        listdegree[4] = ["a_poly4","b_poly4","c_poly4","d_poly4","poly4_shift",'pot_desc11']
        
        parameters = [
            'vmax', 'vmin', 'emax', 'well_width', 'a', 'mass', 
            'nodes',
            'c_gaus', 'gaus_shift',
            'b_expo', 'exp_shift',
            'degree',
            'vdepth', 'emin_c', 'emax_c',
            "a_poly2","b_poly2","poly2_shift",
            "a_poly3","b_poly3","c_poly3","poly3_shift",
            "a_poly4","b_poly4","c_poly4","d_poly4","poly4_shift",
            "pot_desc1","pot_desc2","pot_desc3","pot_desc4","pot_desc5","pot_desc6",
            "pot_desc7","pot_desc8","pot_desc9","pot_desc10","pot_desc11"
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

        
    def refreshView(self):
        if (self.current_view == "options"):
            self.exposedDisplayOptions()
        else:
            self.exposedDisplay(self.current_view)
            
        
    def exposedDisplayOptions(self):
        self.getCache()
        self.current_view = "options"
        with self.content_component_output:
            clear_output()
            display(self.options_cont)

    def buildInterfaceJS(self):
        interface_js = "<script type='text/Javascript'>\n";
        refobj = "PeriodicPotentialLabSimplified_" + str(self.ref)
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
                interface_js += "    var command = 'from nanohubtools import PeriodicPotentialLabSimplified ; PeriodicPotentialLabSimplified.find_instance("+ str(self.ref) + ")." + method[0] +"(";
                for i, parameter in enumerate (inspect.signature(method[1]).parameters):
                    if (i==0):
                        interface_js += "\\'' + String(" + parameter + ") + '\\'"
                    else:
                        interface_js += ", \\'' + String(" + parameter + ") + '\\'"
                interface_js += ")';\n";
                interface_js += "    console.log('Executing Command: ' + command);\n"
                interface_js += "    var kernel = IPython.notebook.kernel;\n"
                interface_js += "    kernel.execute(command);\n"
                interface_js += "}\n";
        interface_js+='</script>\n'
        return interface_js        

    def displayWindow(self):   
        self.displayFrame()
        display(IHTML(self.buildInterfaceJS()))
        with self.window:
            clear_output()
            #display(self.options_cont)
            display(VBox([                
                self.header_component_output,
                HBox([
                    self.parameters_component_output,
                    self.content_component_output
                ], layout=Layout(flex='1', height="100%"))
            ], layout=Layout(flexDirection="row", width="100%", height="750px")))

    def buildIcon(self, icon):
        path = ospath.dirname(__file__)
        image_encoded = ""
        with open(path+"/assets/" + icon,'rb' ) as f:
            image_encoded = f.read()                    
        image = encodebytes(image_encoded).decode("utf-8") 
        html = "url(data:image/png;base64," + str(image).replace("\n", "").replace("=", "") +")"
        return loads(dumps(html))            
             
    def buildHeader(self):   
        header_view = '''
        <style>
        
        .PeriodicPotentialLabSimplifiedLogo{
            line-height : normal;
            width : 160px ;
            height : 140px; 
            font-size : 14px ; 
            display : flex;
            flex-direction : column;
            justify-content : center;
            text-align : center;
            border-right : 4px solid #FFFFFF;
            color : #707070;
            background-image: url("data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIj8+Cjxzdmcgd2lkdGg9IjU4MCIgaGVpZ2h0PSI0MDAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiA8ZyBjbGFzcz0ibGF5ZXIiPgogIDx0aXRsZT5MYXllciAxPC90aXRsZT4KICA8bGluZSBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMTAiIHgxPSIwIiB4Mj0iNzciIHkxPSIxMzgiIHkyPSIxMzgiLz4KICA8bGluZSBzdHJva2U9IiMwMDAiICBzdHJva2Utd2lkdGg9IjEwIiB4MT0iNzIiIHgyPSI3MiIgeTE9IjEzOCIgeTI9IjQiLz4KICA8bGluZSBzdHJva2U9IiMwMDAiICBzdHJva2Utd2lkdGg9IjEwIiB4MT0iNjciIHgyPSIxMjEiIHkxPSI1IiB5Mj0iNSIvPgogIDxsaW5lIHN0cm9rZT0iIzAwMCIgIHN0cm9rZS13aWR0aD0iMTAiIHgxPSIxMTciIHgyPSIxMTciIHkxPSIxMzgiIHkyPSI0Ii8+CiAgPGxpbmUgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjEwIiB4MT0iMTEyIiB4Mj0iMTg4IiB5MT0iMTM4IiB5Mj0iMTM4Ii8+CiAgPGxpbmUgc3Ryb2tlPSIjMDAwIiAgc3Ryb2tlLXdpZHRoPSIxMCIgeDE9IjE4MyIgeDI9IjE4MyIgeTE9IjEzOCIgeTI9IjQiLz4KICA8bGluZSBzdHJva2U9IiMwMDAiICBzdHJva2Utd2lkdGg9IjEwIiB4MT0iMTc4IiB4Mj0iMjMyIiB5MT0iNSIgeTI9IjUiLz4KICA8bGluZSBzdHJva2U9IiMwMDAiICBzdHJva2Utd2lkdGg9IjEwIiB4MT0iMjI3IiB4Mj0iMjI3IiB5MT0iMTM4IiB5Mj0iNCIvPgogIDxsaW5lIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIxMCIgeDE9IjIyMiIgeDI9IjI5OSIgeTE9IjEzOCIgeTI9IjEzOCIvPgogIDxsaW5lIHN0cm9rZT0iIzAwMCIgIHN0cm9rZS13aWR0aD0iMTAiIHgxPSIyOTQiIHgyPSIyOTQiIHkxPSIxMzgiIHkyPSI0Ii8+CiAgPGxpbmUgc3Ryb2tlPSIjMDAwIiAgc3Ryb2tlLXdpZHRoPSIxMCIgeDE9IjI4OSIgeDI9IjM0MyIgeTE9IjUiIHkyPSI1Ii8+CiAgPGxpbmUgc3Ryb2tlPSIjMDAwIiAgc3Ryb2tlLXdpZHRoPSIxMCIgeDE9IjMzOCIgeDI9IjMzOCIgeTE9IjEzOCIgeTI9IjQiLz4KICA8bGluZSBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMTAiIHgxPSIzMzMiIHgyPSI0MTAiIHkxPSIxMzgiIHkyPSIxMzgiLz4KICA8cGF0aCBkPSJtMTE5LDk5YTAuNjMsMC4zNiAwIDAgMCA2MywwIiBmaWxsPSIjMDAwIi8+CiAgPHBhdGggZD0ibTIzMSw5OWEwLjYzLDAuMzYgMCAwIDAgNjMsMCIgZmlsbD0iIzAwMCIvPgogIDxwYXRoIGQ9Im0yNjAsNDhhMC4zNSwwLjM2IDAgMCAwIDM1LDAiIGZpbGw9IiMwMDAiLz4KICA8cGF0aCBkPSJtMjI4LDM0YTAuMzUsMC4zNiAwIDAgMCAzNSwwIiBmaWxsPSIjMDAwIiB0cmFuc2Zvcm09InJvdGF0ZSgtMTgwLCAyNDUuNTMxLCA0My4wMzEyKSIvPgogIDxwYXRoIGQ9Im0xNDcsNDhhMC4zNSwwLjM2IDAgMCAwIDM1LDAiIGZpbGw9IiMwMDAiLz4KICA8cGF0aCBkPSJtMTE1LDM0YTAuMzUsMC4zNiAwIDAgMCAzNSwwIiBmaWxsPSIjMDAwIiB0cmFuc2Zvcm09InJvdGF0ZSgtMTgwLCAxMzIuNzE1LCA0My45NjQ3KSIvPgogPC9nPgo8L3N2Zz4=");
            background-size: 200px;
            background-repeat: no-repeat;
            background-position-x: 10px;
            background-position-y: 10px;
            padding-left: 15px;
            padding-right: 15px;
            padding-top: 50px;
            font-weight: bold;
        }

                        

        .ComponentPotentialSelected, .ComponentPotential{
            height: 60px;
            width: 60px;
            border-radius:60px;
            background-color:#FFFFFF;
            border:1px solid #707070;
        }

        .ComponentPotentialSpace{
            width:6px;
            padding:0px;
        }
        
        .ComponentPotentialSelected, .ComponentPotential:hover{
            background-color:#B6BEFD;
        }

        .ComponentPotentials{
            display:flex;
            flex-direction:row;
            justify-content:flex-start;
            padding-top: 10px;       
            padding-bottom: 10px;
        }

        
        .materialsTitle{
            display: flex;
            flex-direction: column;
            text-align: left;
            justify-content: flex-start;
            font-size: 15px;
            color: #707070;
            width: 100px;
            padding-left: 10px;
        }
        
        div.output_subarea{
            padding:0px
        }
                    

        .potential1{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("potential1.png") + ''';
        }

        .potential2{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("potential2.png") + ''';
        }

        .potential3{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("potential3.png") + ''';
        }

        .potential4{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("potential4.png") + ''';
        }

        .potential5{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("potential5.png") + ''';
        }

        .potential6{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("potential6.png") + ''';
        }

        .potential7{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("potential7.png") + ''';
        }

        .potential8{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("potential8.png") + ''';
        }

        .ComponentSettingsOption{
            height: 35px;
            width: 150px;
            border-radius:15px;
            background-color: #FFFFFF;
            border:1px solid #707070;  
            font-size: 15px;
            color : #707070;
        }

        .ComponentSettingsOption:hover{
            background-color: #B6BEFD;
        }

        .ComponentSettings{
            padding: 10px;
            display: flex;
            align-items: center;
            flex-direction: column;            
        }        
        </style>
        <div id="ppotential_header_''' + str(self.ref) + '''"></div>
        '''

        header_js = '''
            requirejs.config({
                paths: {
                    'react': 'https://unpkg.com/react@16.8.6/umd/react.production.min',
                    'react-dom': 'https://unpkg.com/react-dom@16/umd/react-dom.production.min'
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
     
                class PotentialComponent extends React.Component {
                    constructor(props) {
                        super(props)
                        this.state = { 
                            potentials:{
                                "KP":{
                                    "icon": "potential1",
                                    "label": "Step Well",
                                },
                                "Tri":{
                                    "icon": "potential3",
                                    "label": "Triangular Well",
                                },
                                "para":{
                                    "icon": "potential4",
                                    "label": "Parabolic Potential",
                                },
                                "Sine":{
                                    "icon": "potential2",
                                    "label": "Sinosoidal Potential",
                                },
                                "cola":{
                                    "icon": "potential5",
                                    "label": "Coulombic Potential",
                                },
                                "expo":{
                                    "icon": "potential6",
                                    "label": "Exponential Potential",
                                },
                                "gaus":{
                                    "icon": "potential7",
                                    "label": "Gaussian Potential",
                                },
                                "poly":{
                                    "icon": "potential8",
                                    "label": "Polynomial Potential",
                                },
                            }, 
                            selectedPotential:"KP",
                        } 
                    }    

                    selectPotential(potential){
                        this.setState({
                            selectedPotential:potential, 
                        })
                        PeriodicPotentialLabSimplified_''' + str(self.ref) + '''['exposedSelectPotential'](potential)
                    }


                    displayOptions(){
                        PeriodicPotentialLabSimplified_''' + str(self.ref) + '''["exposedDisplayOptions"]();
                    }

                    render(){
                        var children = Array()    
                        let self = this
                        children.push(React.createElement("div", {key:Util.create_UUID(), className:"materialsTitle"}, "Potentials"))
                        var style = {
                            display: "flex",
                            alignItems: "center",
                            flexDirection: "row",
                            justifyContent: "center",
                        }
                        for (let potential in this.state.potentials) {
                            var potential_instance = this.state.potentials[potential]
                            let cur_potential = potential
                            if (potential != this.state.selectedPotential){
                                children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentPotential " + potential_instance.icon, style:style, onClick:function(e){self.selectPotential(potential)}, title:potential_instance['label']}))
                            } else {
                                children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentPotentialSelected " + potential_instance.icon, style:style, onClick:function(e){self.selectPotential(potential)}, title:potential_instance['label']}))
                            }                
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentPotentialSpace"}))
                        }  
                        var mat_children = Array()    
                               
                        mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentSettingsOption", style:style, onClick:function(e){self.displayOptions()}, title:"Settings"}, "Settings"))
                        var settings = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSettings"}, mat_children)

                        

                        var potentials = React.createElement("div", {key:Util.create_UUID(), className:"ComponentPotentials"}, children)
                        var mat_container = React.createElement("div", {key:Util.create_UUID(), className:"", style:{flex:1}}, [potentials, settings])

                        var title = React.createElement("div", {key:Util.create_UUID(), className:"PeriodicPotentialLabSimplifiedLogo", style:{}}, "Periodic Potential Lab (Kronig Penny)")

                        var div = React.createElement("div", {key:Util.create_UUID(), className:"", style:{backgroundColor:'#EEEEEE', display:'flex',flexDirection: 'row',}}, [title, mat_container])

                        return div
                    }
                }

                ReactDOM.render(
                    React.createElement(PotentialComponent, {}),
                    document.getElementById("ppotential_header_''' + str(self.ref) + '''")
                );
            });
        '''        
       
        return header_view, header_js

    def buildParameters(self):    
        parameter_component_view = '''
        <style>
            .ComponentOptionSelected, .ComponentOption{
                height: 40px;
                width: 150px;
                border-radius:15px;
                background-color: #FFFFFF;
                border:1px solid #707070;  
                font-size: 15px;
                color : #707070;
            }

            .ComponentOptionSelected, .ComponentOption:hover{
                background-color: #B6BEFD;
            }

            .ComponentOptionSpacer{
                height: 10px;
            }
            
            .ComponentParameters{
                display: flex;
                flex-direction: column;
                justify-content: flex-start;
                flex: 1;
                align-items: center;
                border-top: 4px solid #FFF;
                padding-top: 10px;     
            }

            div.output_subarea{
                padding:0px
            }
                        
            .ComponentOptions{
                display:flex;
                flex-direction:column;
                justify-content:flex-start;
            }
            
            .ComponentTheme{
                display: flex;
                flex-direction: row;
                justify-content: space-around;
                width: 130px;
                bottom: 10px;
                position: absolute;
            }

            .ComponentThemeDark, .ComponentThemeWhite, .ComponentThemeDefault{
                height: 20px;
                width: 20px;
                border-radius:20px;
                border:1px solid #707070;  
                font-size: 15px;
                color : #707070;        
            }
                        
            .ComponentThemeDark{
                background-color: #000000;        
            }
            
            .ComponentThemeWhite{
                background-color: #FFFFFF;
            }        

            .ComponentThemeDefault{
                background-color: #E5ecf6;
            }        

            .ComponentThemeDark:hover{
                background-color: #555555;
            }
            
            .ComponentThemeWhite:hover{
                background-color: #EEEEEE;
            }                 

            .ComponentThemeDefault:hover{
                background-color: #c2cad4;
            }                 
                    
        </style>
        <div id="pnlab_parameter_''' + str(self.ref) + '''"></div>
        '''

        parameter_component_js = '''
        requirejs.config({
            paths: {
                'react': 'https://unpkg.com/react@16.8.6/umd/react.production.min',
                'react-dom': 'https://unpkg.com/react-dom@16/umd/react-dom.production.min'
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
                            "option8":{
                                "alt" : "Wave function Probability Plot",
                                "label" : "Dispersion & Wavefunction",
                                "action" : function(){ self.displayParameter('option8a') },
                                children : {
                                    "option8a":{
                                        "alt" : "Wave function Probability Plot Min",
                                        "label" : "Min",
                                        "action" : function(){ self.displayParameter('option8a') },
                                    },
                                    "option8b":{
                                        "alt" : "Wave function Probability Plot Max",
                                        "label" : "Max",
                                        "action" : function(){ self.displayParameter('option8b') },
                                    },
                                }
                            },
                            //"option7":{
                            //    "alt" : "Eigen Energy and Wave function",
                            //    "label" : "Eigen Energy",
                            //    "action" : function(){ self.displayParameter('option7a') },
                            //    children : {
                            //        "option7a":{
                            //            "alt" : "Eigen Energy and Wave function Min",
                            //            "label" : "Min",
                            //            "action" : function(){ self.displayParameter('option7a') },
                            //        },
                            //        "option7b":{
                            //            "alt" : "Eigen Energy and Wave function Max",
                            //            "label" : "Max",
                            //            "action" : function(){ self.displayParameter('option7b') },
                            //       },
                            //    }
                            //},
                            "option3":{
                                "alt" : "Reduced Dispertion Relation",
                                "label" : "Reduced Dispertion",
                                "action" : function(){ self.displayParameter('option3') },
                            },
                            "option4":{
                                "alt" : "Expanded Dispertion Relation",
                                "label" : "Expanded Dispertion",
                                "action" : function(){ self.displayParameter('option4') },
                            },
                            "option6":{
                                "alt" : "Reduced EK compared to Eff.mass EK",
                                "label" : "Reduced Dispersion with Eff. Masses",
                                "action" : function(){ self.displayParameter('option6') },
                            },
                            "option9":{
                                "alt" : "1D DOS Plot",
                                "label" : "Density of States",
                                "action" : function(){ self.displayParameter('option9') },
                            },
                            "option5":{
                                "alt" : "Periodic EK compared to Free Electron EK",
                                "label" : "Expanded Dispersion vs Free Dispersion",
                                "action" : function(){ self.displayParameter('option5') },
                            },
                            "option2":{
                                "alt" : "Allowed Bands",
                                "label" : "Allowed Bands",
                                "action" : function(){ self.displayParameter('option2') },
                            },                            
                            "option1":{
                                "alt" : "Energy functional vs Energy",
                                "label" : "Energy functional",
                                "action" : function(){ self.displayParameter('option1') },
                            },
                            //"options":{
                            //    "alt" : "Settings",
                            //    "label" : "Settings",
                            //    "action" : function(){ self.displayOptions() },
                            //},
                            

                        }, 
                        selectedParameter:"''' + self.current_view + '''",
                    } 
                }    

                changeTheme( option ){
                    if (option == "dark")
                        PeriodicPotentialLabSimplified_''' + str(self.ref) + '''["exposedChangeTheme"]('plotly_dark');
                    else if (option == "white")
                        PeriodicPotentialLabSimplified_''' + str(self.ref) + '''["exposedChangeTheme"]('plotly_white');
                    else
                        PeriodicPotentialLabSimplified_''' + str(self.ref) + '''["exposedChangeTheme"]('plotly');
                }

                displayParameter( parameter ){
                    PeriodicPotentialLabSimplified_''' + str(self.ref) + '''["exposedDisplay"](parameter);
                }

                selectParameter(parameter){
                    this.setState({
                        selectedParameter:parameter, 
                    })
                }


                callbackParameter(param, parameter){
                    //console.log(parameter)
                    this.selectParameter(param)
                    if (parameter.action){
                       parameter.action() 
                    }
                }

                render(){
                    var children = Array()    
                    var style = {
                        display: "flex",
                        alignItems: "center",
                        flexDirection: "row",
                        justifyContent: "center",
                        textAlign: "center",
                    }       

                    var style2 = {
                        width:"100px",
                        display: "flex",
                        alignItems: "center",
                        flexDirection: "row",
                        justifyContent: "center",
                        textAlign: "center",
                    }    
      
                    let self = this
                    
                    for (let parameter in this.state.parameters) {
                        let parameter_instance = this.state.parameters[parameter]
                        if (this.state.selectedParameter.startsWith(parameter)){
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSelected", style:style, onClick:function(e){self.callbackParameter(parameter, parameter_instance)}, title:parameter_instance.alt}, parameter_instance.label))
                            if (parameter_instance.children){                                    
                                for (let option in parameter_instance.children) {
                                    if (this.state.selectedParameter == parameter)
                                        this.state.selectedParameter = option
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))
                                    let option_instance = parameter_instance.children[option]
                                    if (option == this.state.selectedParameter){
                                        children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSelected", style:style2, onClick:function(e){self.callbackParameter(option, option_instance)}, title:option_instance.alt}, option_instance.label))
                                    } else {
                                        children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOption", style:style2, onClick:function(e){self.callbackParameter(option, option_instance)}, title:option_instance.alt}, option_instance.label))
                                    }                                
                                }                                
                            }                            
                        } else {
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOption", style:style, onClick:function(e){self.callbackParameter(parameter, parameter_instance)}, title:parameter_instance.alt}, parameter_instance.label))
                        }   
                        children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))

                    }  

                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentTheme"}, [
                        React.createElement("div", {key:Util.create_UUID(), className:""}, "Theme"),
                        React.createElement("div", {key:Util.create_UUID(), className:"ComponentThemeDefault", onClick:function(e){self.changeTheme("default")}}),
                        React.createElement("div", {key:Util.create_UUID(), className:"ComponentThemeWhite", onClick:function(e){self.changeTheme("white")}}),
                        React.createElement("div", {key:Util.create_UUID(), className:"ComponentThemeDark", onClick:function(e){self.changeTheme("dark")}}),
                    ]))

                    var components = React.createElement("div", {key:Util.create_UUID(), className:"ComponentParameters"}, children)

                    var opt = React.createElement("div", {key:Util.create_UUID(), className:"", style:{display:"flex", flexDirection:"row", backgroundColor:'#EEEEEE', justifyContent:'flex-start', height:'700px', width:'160px', borderRight:'4px solid #FFF'}}, [components])
                    var views = React.createElement("div", {key:Util.create_UUID(), className:"viewsTitle"}, "Views")
                    var div = React.createElement("div", {key:Util.create_UUID(), className:"", style:{display:"flex", flexDirection:"column", backgroundColor:'#EEEEEE', justifyContent:'flex-start', height:'700px'}}, [opt])
                    return div
                }
            }

            ReactDOM.render(
                React.createElement(ParametersComponent, {}),
                document.getElementById("pnlab_parameter_''' + str(self.ref) + '''")
            );
        });
        '''      
        return parameter_component_view, parameter_component_js;            
        
    def displayFrame(self):
        header_component_view, header_component_js = self.buildHeader()
        parameter_component_view, parameter_component_js = self.buildParameters()
        
        with self.header_component_output:
            display(IHTML(header_component_view))
            display(Javascript(header_component_js)) 
    
        with self.parameters_component_output:
            display(IHTML(parameter_component_view))
            display(Javascript(parameter_component_js))         
            
    def getCurves(self, sequences):
        lists = {}
        for sequence in sequences:
            text = ""
            if 'id' in sequence.attrib:            
                ab = sequence.find('about')
                if ab is not None:
                    for g in ab.findall("group"):
                        if g.text in lists:
                            lists[g.text].append(sequence)
                        else:
                            lists[g.text] = [sequence]                                                                                          
        return lists;

    def getCurrentParameters( self, default_list={} ):
        parameters = {}
        
        for ii in self.options.keys():
            if self.options[ii].visible == 'visible' or self.options[ii].visible == None:
                pass;
            elif ii in default_list :
                self.options[ii].value = default_list[ii]
            elif ii in self.default_options: 
                self.options[ii].value = self.default_options[ii]

        for ii in default_list.keys():
            if ii in self.options:
                self.options[ii].value = default_list[ii]
        
        for key, val in self.options.items():
            if (hasattr(val, "format") == False):
                units = ''
                if key in self.parameters and self.parameters[key]['units'] is not None:
                    units = str(self.parameters[key]['units'])
                parameters[key] = str(val.value) + units
        return parameters;


        
    def getCache(self):
        parameters = self.getCurrentParameters( )
        hashstr =  dumps(parameters, sort_keys=True).encode()        
        hashitem = sha1(hashstr).hexdigest()
        if self.hashitem != hashitem:
            xml = self.loadCache(parameters, hashitem)
            self.xml = xml
            results = xml.find('output')
            curves = self.getCurves(results.findall('curve')) 
            self.option1 = curves.get("Energy functional vs Energy", None)
            self.option2 = curves.get("Allowed Bands", None)
            self.option3 = curves.get("Reduced Dispersion Relation", None)
            self.option4 = curves.get("Expanded Dispersion Relation", None)
            self.option5 = curves.get("Periodic EK compared to Free Electron EK", None)
            self.option6 = curves.get("Reduced EK compared to Eff.mass EK", None)
            self.option7 = curves.get("Eigen Energy and Wave Function", None)
            self.option7a = [x for x in self.option7 if "max" not in x.attrib['id']]
            self.option7b = [x for x in self.option7 if "min" not in x.attrib['id']]
            self.option8 = curves.get("Wave Function Probability Plot", None)
            self.option8a = [x for x in self.option8 if "max" not in x.attrib['id']]
            self.option8b = [x for x in self.option8 if "min" not in x.attrib['id']]
            for curve in self.option7:
                if curve.attrib['id'].startswith("eig_energy_max"):
                    self.option8b.append(curve)
                elif curve.attrib['id'].startswith("eig_energy_min"):
                    self.option8a.append(curve)
            #Above %50 region of wavefunction(min)
            #Above %50 region of wavefunction(max)
            self.option9 = curves.get("1D DOS plot", None)
            
            self.history[hashitem] = {
                "option1": self.option1,
                "option2": self.option2,
                "option3": self.option3,
                "option4": self.option4,
                "option5": self.option5,
                "option6": self.option6,
                "option7": self.option7,
                "option7a": self.option7a,
                "option7b": self.option7b,
                "option8": self.option8,
                "option8a": self.option8a,
                "option8b": self.option8b,
                "option9": self.option9,
                "timestamp" : datetime.now().timestamp(),
                "parameters" : parameters
            }            
            
        with self.content_component_output:
            clear_output()  
        self.hashitem = hashitem                    

    def exposedDisplay(self, option):
        self.getCache()
        self.current_view = option
        if option in [
                "option1","option2","option3","option4",
                "option5","option6","option7","option8",                
            ]:
            self.plotXY(option,[self.hashitem],self.content_component_output)
        elif option in [
                "option7a","option7b","option8a","option8b","option9",
            ]:
            self.plotWave('option3', option,[self.hashitem],self.content_component_output)
            
    def exposedSelectPotential(self, potential):
        if (self.options["pot_type"].value != potential):
            self.options["pot_type"].value = potential;
            if potential == "cola": #TODO, this is hack-ish should be a different parameter
                self.options["a"].value = 0.2
            else:
                self.options["a"].value = self.default_options["a"]
            self.getCache()
            self.refreshView()
            
    def loadCache(self, parameters, hashitem):
        xml = None
        if hashitem in self.hashtable:
            self.loggingMessage("LOADING CACHE ...." + hashitem, self.content_component_output)

            with open(self.hashtable[hashitem],'rt' ) as f:
                xml = f.read()
        else:
            if ospath.isfile(hashitem + ".xml"):
                self.loggingMessage("LOADING CACHE ...." + hashitem, self.content_component_output)
                #driver_json = self.generateDriver( {'parameters':parameters } )
                #session_id = self.session.getSession(driver_json)
                with open(hashitem + ".xml",'rt' ) as f:
                    xml = f.read()
                self.hashtable[hashitem] = hashitem + ".xml"
                    
            else:                
                try:
                    self.loggingMessage("GENERATING CACHE ...." + hashitem, self.content_component_output)                
                    driver_json = self.generateDriver( {'parameters':parameters } )
                    session_id = self.session.getSession(driver_json)
                    with self.content_component_output:            
                        print ("Calculating new results ("+  hashitem +") id [" + session_id + "]")
                        status = self.session.checkStatus(session_id) 
                        loading = True
                        while loading == True:
                            if 'success' in status and status['success'] and 'finished' in status and status['finished'] and status['run_file'] != "":
                                loading = False
                            else:    
                                print ("waiting results from nanoHUB [" + session_id + "]")
                                sleep(5);
                                status = self.session.checkStatus(session_id)
                    xml_text = self.session.getResults(session_id, status['run_file'])
                    xml = ET.fromstring(xml_text) 
                    status = self.getText(xml, ["output", "status"])
                    if status == "ok":
                        self.hashtable[hashitem] = hashitem + ".xml"
                        with open(self.hashtable[hashitem],'wt' ) as f:
                            f.write(xml_text)
                    else:
                        with self.content_component_output:                
                            clear_output()  
                            raise("There is a problem with that simulation")   

                except ConnectionError as ce:
                    with self.content_component_output:                
                        clear_output()  
                        print ("Simulation Error")
                        print (str(ce))
                        xml = ET.fromstring("<run><output></output></run>") 
                except : 
                    with self.content_component_output:                
                        clear_output()  
                        print ("There is a problem with that simulation, try again")
                        xml = ET.fromstring("<run><output></output></run>") 
                return xml                                
        return ET.fromstring(xml)             
        
    def loggingMessage(self, message, output):
        loading = '''
            <style>
                .lds-facebook {
                  display: inline-block;
                  position: relative;
                  width: 64px;
                  height: 64px;
                }
                .lds-facebook div {
                  display: inline-block;
                  position: absolute;
                  left: 6px;
                  width: 13px;
                  background: #fff;
                  animation: lds-facebook 1.2s cubic-bezier(0, 0.5, 0.5, 1) infinite;
                }
                .lds-facebook div:nth-child(1) {
                  left: 6px;
                  animation-delay: -0.24s;
                  background: #707070;
                }
                .lds-facebook div:nth-child(2) {
                  left: 26px;
                  animation-delay: -0.12s;
                  background: #707070;
                }
                .lds-facebook div:nth-child(3) {
                  left: 45px;
                  animation-delay: 0;
                  background: #707070;
                }
                @keyframes lds-facebook {
                  0% {
                    top: 6px;
                    height: 51px;
                  }
                  50%, 100% {
                    top: 19px;
                    height: 26px;
                  }
                }
            </style>
        '''    
        with output:
            clear_output()
            display(IHTML(loading))
            display(IHTML("<div class='lds-facebook'><div></div><div></div><div></div></div><div>" + message + "</div>"))

            
    def plotXY(self, field, hashlist, out):
        traces = []
        ly = {"title":"", 'xaxis':{'type':"linear","title": ""}, 'yaxis':{'type':"linear","title": ""}}
        for hash in hashlist:
            if (hash in self.history) and field in (self.history[hash]):            
                tr, ly = self.buildXYPlotly(self.history[hash][field])
                if (hash != self.hashitem):
                    p1 = self.history[self.hashitem]["parameters"].items()
                    p2 = self.history[hash]["parameters"].items()
                    value = set([k+":"+v for k,v in p2]) - set([k+":"+v for k,v in p1])
                    diff = ", ". join(value)
                    for t in tr:
                        t['hovertext'] = diff
                        t['hoverinfo'] = "text+x+y"
                        t["line"]["color"] = "lightgrey"
                traces.extend(tr)
        out.clear_output()   
        self.fig.data=[]            
        self.fig.update({
            'data': traces,
            'layout' : {
                'title' : ly['title'],
                'xaxis' : {
                    'domain': [0.0, 1.0],                
                    'title' : ly['xaxis']['title'],
                    'type' : ly['xaxis']['type'],
                    'autorange' : ly['xaxis']['autorange'],
                    'range' : ly['xaxis']['range'],
                },
                'yaxis' : {
                    'title' : ly['yaxis']['title'],
                    'type' : ly['yaxis']['type'],
                    'autorange' : ly['yaxis']['autorange'],
                    'range' : ly['yaxis']['range'],
                },
            }, 
        })   
        buttons = []
        if (len(hashlist) == 1 and len(self.history)>1):        
            bt = Button(description="Compare",layout=Layout(width='auto'))
            bt.on_click(lambda e, this=self, s=field, o=out: this.showHistory(s,o))
            buttons.append(bt)
        elif (len(self.history)>1):
            bt = Button(description="Clear History",layout=Layout(width='auto'))
            bt.on_click(lambda e, this=self, s=field, o=out: this.clearHistory(s,o))
            buttons.append(bt)

        with out:
            display(VBox([self.fig, HBox(buttons)]))

            
    def plotWave(self, base, field, hashlist, out):
        traces = []
        ly = {"title":"", 'xaxis':{'type':"linear","title": "", "autorange":False}, 'yaxis':{'type':"linear","title": "", "autorange":False}}
        ly2 = {"title":"", 'xaxis':{'type':"linear","title": "", "autorange":False}, 'yaxis':{'type':"linear","title": "", "autorange":False}}
        for hash in hashlist:
            if (hash in self.history) and field in (self.history[hash]):            
                tr, ly = self.buildXYPlotly(self.history[hash][field])
                for t in tr:
                    t["xaxis"] = "x2" 
                    if t["line"]["color"] == "yellow":
                        t["line"]["color"] = "#984ea3"

                if (hash != self.hashitem):
                    p1 = self.history[self.hashitem]["parameters"].items()
                    p2 = self.history[hash]["parameters"].items()
                    value = set([k+":"+v for k,v in p2]) - set([k+":"+v for k,v in p1])
                    diff = ", ". join(value)
                    for t in tr:
                        t['hovertext'] = diff
                        t['hoverinfo'] = "text+x+y"
                        t["line"]["color"] = "lightgrey"
                        
                traces.extend(tr)
        for hash in hashlist:
            if (hash in self.history) and base in (self.history[hash]):            
                tr, ly2 = self.buildXYPlotly(self.history[hash][base])
                if (hash != self.hashitem):
                    p1 = self.history[self.hashitem]["parameters"].items()
                    p2 = self.history[hash]["parameters"].items()
                    value = set([k+":"+v for k,v in p2]) - set([k+":"+v for k,v in p1])
                    diff = ", ". join(value)
                    for t in tr:
                        t['hovertext'] = diff
                        t['hoverinfo'] = "text+x+y"
                        t["line"]["color"] = "lightgrey"
                traces.extend(tr)
        out.clear_output()   
        self.fig.data=[]

        if field == "option9":
            ly['xaxis']['type'] = "log"
        else:
            ly['xaxis']['type'] = "linear"
        
        self.fig.update({
            'data': traces,
            'layout' : {
                'title' : ly['title'],
                'xaxis' : {
                    'domain': [0, 0.29],
                    'title' : ly2['xaxis']['title'],
                    'autorange' : False,
                    'range' : [0,1],
                    'type' : 'linear',
                },
                'xaxis2' : {
                    'domain': [0.31, 1.0],
                    'title' : ly['xaxis']['title'],
                    'autorange' : ly['xaxis']['autorange'],
                    'type' : ly['xaxis']['type'],
                },
                'yaxis' : {
                    'title' : ly2['yaxis']['title'],
                    'autorange' : True,
                    'type' : 'linear',
                },

            }, 
        })   
        
        buttons = []
        if (len(hashlist) == 1 and len(self.history)>1):        
            bt = Button(description="Compare",layout=Layout(width='auto'))
            bt.on_click(lambda e, this=self, s=field, o=out: this.showHistory(s,o))
            buttons.append(bt)
        elif (len(self.history)>1):
            bt = Button(description="Clear History",layout=Layout(width='auto'))
            bt.on_click(lambda e, this=self, s=field, o=out: this.clearHistory(s,o))
            buttons.append(bt)            

        with out:
            display(VBox([self.fig, HBox(buttons)]))

            
    def showHistory(self, sequence, out):
        hashlist = []
        for hash in (sorted(self.history, key=lambda hash: self.history[hash]["timestamp"], reverse=True)):
            hashlist.append(hash)
        if sequence in [
                "option1","option2","option3","option4",
                "option5","option6","option7","option8",                
            ]:
            self.plotXY(sequence, hashlist, out)        
        elif sequence in [
                "option7a","option7b","option8a","option8b","option9"
            ]:
            self.plotWave('option3', sequence, hashlist, out)
            
    def clearHistory(self, sequence, out):
        self.history = {k: v for k, v in self.history.items() if k == self.hashitem}
        self.showHistory(sequence, out)
