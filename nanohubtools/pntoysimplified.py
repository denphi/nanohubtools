from .rappturetool import Rappturetool
from ipywidgets import Text, HBox, VBox, HTML, Image, Layout, Button, ButtonStyle, Tab, Output, Box, Textarea, SelectionSlider, Play
from IPython.display import Javascript, clear_output
from IPython.display import HTML as IHTML                                    
import xml.etree.ElementTree as ET
from plotly.graph_objs import FigureWidget
from .crystalsimplified import InstanceTracker
import hashlib, json
import math, os, base64
import uuid, weakref, inspect, time
from datetime import datetime
from  hublib.ui.numvalue import NumValue
import re

class ScientificNumber(NumValue):
    def __init__(self, name, value, **kwargs):
        newval = '%.2e' % value        
        NumValue.__init__(self, 'float', name, newval, **kwargs)
        self.dd.layout = {'width': '140px'}
        
    def _create_widget(self, ntype, value, min, max):
        if min is not None and max is None:
            raise ValueError("Min is set but not Max.")
        if min is None and max is not None:
            raise ValueError("Max is set but not Min.")
        return Text(value=value)
    
    def _cb(self, w):
        w['new'] = w['new'].replace("E", "e")
        try:
            newval = float(w['new'])
        except:
            try:
                newval = float(re.sub(r'e\+?\-?','',w['new']))
            except:
                self.dd.value = w['old']
        
    @property
    def value(self):
        val = 0
        try:
            val = float(self.dd.value)
        except:
            try:
                val = float(re.sub(r'e\+?\-?','',self.dd.value))
            except:
                val = 0
        return val
    
    @value.setter 
    def value(self, newval):
        try:
            float(newval)
            self.dd.value = '%.2e' % newval            
        except:
            pass;

        
class PNToySimplified (InstanceTracker, Rappturetool):
    def __init__(self, credentials, **kwargs):
        InstanceTracker.__init__(self)                                  
        self.parameters_structure = [
            '_Structure', 
            'p_len', 
            'p_node', 
            'i_len',
            'i_node',
            'n_len',
            'n_node',
            'Na',
            'Nd',
        ]
        self.parameters_materials = [
            '_Materials',
            'materialp',
            '_Minority carrier lifetime',
            'taun',
            'taup',
            '_Impurities',            
            'impurity',
            'impuritydoping',
            'impuritylevel',
        ]
        self.parameters_ambient = [    
            '_Ambient',
            'temperature',
            'vsweep_high',
            'vn_step',
        ]
        self.parameters_additional = [
        ]
        self.history = {}
        self.current_view = "band"
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

        
        
        parameters = self.parameters_structure + self.parameters_materials + self.parameters_ambient + self.parameters_additional
        kwargs.setdefault('title', 'P-N junction')
        Rappturetool.__init__(self, credentials, "pntoy", parameters, extract_method="id", **kwargs)

        
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
        for opt in ['Na','Nd','taun','taup','impuritylevel']:
            self.options[opt] = ScientificNumber(
                value=self.options[opt].value, 
                name=self.options[opt].name,
                min=self.options[opt].min,
                max=self.options[opt].max,
                units=self.options[opt].units_tex
            )
        
        container_structure = VBox(layout=Layout(width='100%', height='100%'))
        children_structure = []
        container_materials = VBox(layout=Layout(width='100%', height='100%'))
        children_materials = []
        container_ambient = VBox(layout=Layout(width='100%', height='100%'))
        children_ambient = []

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

        self.options['impuritydoping'].visible = False
        self.options['impuritylevel'].visible = False
        self.options['impurity'].dd.observe(lambda b : setattr(self.options['impuritydoping'], 'visible', (b['new'] == "yes")), 'value')
        self.options['impurity'].dd.observe(lambda b : setattr(self.options['impuritylevel'], 'visible', (b['new'] == "yes")), 'value')

        sqpntoytab = Tab()

        container_materials.children = children_materials
        container_structure.children = children_structure
        container_ambient.children = children_ambient
        #container_introduction.children = children_introduction
        sqpntoytab.children = [container_structure, container_materials, container_ambient]
        #sqpntoytab.set_title(0, "Introduction")
        sqpntoytab.set_title(0, "Structure")
        sqpntoytab.set_title(1, "Materials")
        sqpntoytab.set_title(2, "Environment")
                
        self.options_cont.children = [sqpntoytab]

        self.default_options = {}
        for ii in self.options.keys():
            self.default_options[ii] = self.options[ii].value
        
        self.getCache()
        self.refreshView()
        
    def getCurrentParameters( self, default_list={} ):
        parameters = {}
        
        for ii in self.options.keys():
            if self.options[ii].visible == 'visible' or self.options[ii].visible == None:
                pass;
            elif ii in default_list :
                self.options[ii].value = default_list[ii]
            else: 
                self.options[ii].value = self.default_options[ii]

        for ii in default_list.keys():
            if ii in self.options:
                self.options[ii].value = default_list[ii]
        
        for key, val in self.options.items():
            units = ''
            if key in self.parameters and self.parameters[key]['units'] is not None:
                units = str(self.parameters[key]['units'])
            parameters[key] = str(val.value) + units
        return parameters;

        
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
        refobj = "PNToySimplified_" + str(self.ref)
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
                interface_js += "    var command = 'from nanohubtools import PNToySimplified ; PNToySimplified.find_instance("+ str(self.ref) + ")." + method[0] +"(";
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
            ], layout=Layout(flexDirection="row", width="100%", height="700px")))

    def buildHeader(self):   
        header_view = '''
        <style>        
            .pnLabLogo{
                background-image: url("data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIj8+Cjxzdmcgd2lkdGg9IjY0MCIgaGVpZ2h0PSI0ODAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiA8ZyBjbGFzcz0ibGF5ZXIiPgogIDx0aXRsZT5MYXllciAxPC90aXRsZT4KICA8cmVjdCBmaWxsPSIjZmZmIiBoZWlnaHQ9Ijg5IiBpZD0ic3ZnXzEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIiB3aWR0aD0iNDY1IiB4PSIxNiIgeT0iMCIvPgogIDxyZWN0IGZpbGw9IiMwMDAiIGhlaWdodD0iODkiIGlkPSJzdmdfMTAxIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiIgd2lkdGg9IjE2NyIgeD0iMzEzIiB5PSIwIi8+CiAgPHJlY3QgZmlsbD0iIzAwMCIgaGVpZ2h0PSI4OSIgaWQ9InN2Z182MCIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiIHdpZHRoPSIxNjciIHg9IjE2IiB5PSIwIi8+CiAgPGNpcmNsZSBjeD0iNDMiIGN5PSIyMyIgZmlsbD0iI2ZmZiIgaWQ9InN2Z18yIiByPSIxNS41NTYzNTEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPGNpcmNsZSBjeD0iNDMiIGN5PSI2NSIgZmlsbD0iI2ZmZiIgaWQ9InN2Z180IiByPSIxNS41NTYzNTEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPGNpcmNsZSBjeD0iMTYxIiBjeT0iMjMiIGZpbGw9IiNmZmYiIGlkPSJzdmdfMTEiIHI9IjE1LjU1NjM1MSIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiLz4KICA8Y2lyY2xlIGN4PSIxNjEiIGN5PSI2NSIgZmlsbD0iI2ZmZiIgaWQ9InN2Z18xMCIgcj0iMTUuNTU2MzUxIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiIvPgogIDxjaXJjbGUgY3g9IjIwNyIgY3k9IjIzIiBmaWxsPSIjZmZmIiBpZD0ic3ZnXzI2IiByPSIxNS41NTYzNTEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPGNpcmNsZSBjeD0iMjA3IiBjeT0iNjUiIGZpbGw9IiNmZmYiIGlkPSJzdmdfMjUiIHI9IjE1LjU1NjM1MSIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiLz4KICA8Y2lyY2xlIGN4PSIyNDgiIGN5PSIyMyIgZmlsbD0iI2ZmZiIgaWQ9InN2Z18yMyIgcj0iMTUuNTU2MzUxIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiIvPgogIDxjaXJjbGUgY3g9IjI0OCIgY3k9IjY1IiBmaWxsPSIjZmZmIiBpZD0ic3ZnXzIyIiByPSIxNS41NTYzNTEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPGNpcmNsZSBjeD0iMjkyIiBjeT0iMjMiIGZpbGw9IiNmZmYiIGlkPSJzdmdfMjAiIHI9IjE1LjU1NjM1MSIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiLz4KICA8Y2lyY2xlIGN4PSIyOTIiIGN5PSI2NSIgZmlsbD0iI2ZmZiIgaWQ9InN2Z18xOSIgcj0iMTUuNTU2MzUxIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiIvPgogIDxjaXJjbGUgY3g9IjMzMyIgY3k9IjIzIiBmaWxsPSIjZmZmIiBpZD0ic3ZnXzE3IiByPSIxNS41NTYzNTEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPGNpcmNsZSBjeD0iMzMzIiBjeT0iNjUiIGZpbGw9IiNmZmYiIGlkPSJzdmdfMTYiIHI9IjE1LjU1NjM1MSIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiLz4KICA8Y2lyY2xlIGN4PSI0NTYiIGN5PSIyMyIgZmlsbD0iI2ZmZiIgaWQ9InN2Z18yOSIgcj0iMTUuNTU2MzM1IiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiIvPgogIDxjaXJjbGUgY3g9IjQ1NiIgY3k9IjY1IiBmaWxsPSIjZmZmIiBpZD0ic3ZnXzI4IiByPSIxNS41NTYzNTEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPHRleHQgZmlsbD0iIzAwMCIgZm9udC1mYW1pbHk9InNlcmlmIiBmb250LXNpemU9IjI0IiBpZD0ic3ZnXzM2IiBzdHJva2U9IiMwMDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQzIiB5PSIzMSI+KzwvdGV4dD4KICA8dGV4dCBmaWxsPSIjMDAwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGlkPSJzdmdfMzciIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDMiIHk9IjczIj4rPC90ZXh0PgogIDx0ZXh0IGZpbGw9IiMwMDAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIyNCIgaWQ9InN2Z180NyIgc3Ryb2tlPSIjMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxNjEiIHk9IjMxIj4rPC90ZXh0PgogIDx0ZXh0IGZpbGw9IiMwMDAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIyNCIgaWQ9InN2Z180NiIgc3Ryb2tlPSIjMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxNjEiIHk9IjczIj4rPC90ZXh0PgogIDx0ZXh0IGZpbGw9IiMwMDAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIyNCIgaWQ9InN2Z180NSIgc3Ryb2tlPSIjMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIyMDciIHk9IjMxIj4rPC90ZXh0PgogIDx0ZXh0IGZpbGw9IiMwMDAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIyNCIgaWQ9InN2Z180NCIgc3Ryb2tlPSIjMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIyMDciIHk9IjczIj4rPC90ZXh0PgogIDx0ZXh0IGZpbGw9IiMwMDAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIyNCIgaWQ9InN2Z18xMDAiIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMjkyIiB5PSIxOCI+XzwvdGV4dD4KICA8dGV4dCBmaWxsPSIjMDAwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGlkPSJzdmdfOTkiIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMjkyIiB5PSI2MyI+XzwvdGV4dD4KICA8dGV4dCBmaWxsPSIjMDAwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGlkPSJzdmdfODgiIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMzMzIiB5PSIxOCI+XzwvdGV4dD4KICA8dGV4dCBmaWxsPSIjMDAwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGlkPSJzdmdfOTciIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMzMzIiB5PSI2MyI+XzwvdGV4dD4KICA8dGV4dCBmaWxsPSIjMDAwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGlkPSJzdmdfOTAiIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDU2IiB5PSIxOCI+XzwvdGV4dD4KICA8dGV4dCBmaWxsPSIjMDAwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGlkPSJzdmdfOTUiIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDU2IiB5PSI2MyI+XzwvdGV4dD4KICA8cmVjdCBmaWxsPSIjMDAwIiBoZWlnaHQ9IjUzIiBpZD0ic3ZnXzEwMiIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiIHdpZHRoPSIxNCIgeD0iMCIgeT0iMTgiLz4KICA8cmVjdCBmaWxsPSIjMDAwIiBoZWlnaHQ9IjUzIiBpZD0ic3ZnXzEwMyIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiIHdpZHRoPSIxNCIgeD0iNDgwIiB5PSIxOCIvPgogIDx0ZXh0IGZpbGw9IiNmZmYiIGZvbnQtZmFtaWx5PSJTYW5zLXNlcmlmIiBmb250LXNpemU9IjcwIiBpZD0ic3ZnXzEwNCIgc3Ryb2tlPSIjMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxMDAiIHk9IjY5Ij5QPC90ZXh0PgogIDx0ZXh0IGZpbGw9IiNmZmYiIGZvbnQtZmFtaWx5PSJTYW5zLXNlcmlmIiBmb250LXNpemU9IjcwIiBpZD0ic3ZnXzEwNSIgc3Ryb2tlPSIjMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIzOTUiIHk9IjY5Ij5OPC90ZXh0PgogPC9nPgo8L3N2Zz4=");
                height: 80px;
                background-repeat: no-repeat;
                background-position-x: center;
                background-size: 450px;
                background-position-y: 8px;
            }
                           
            .pnLabHeader{
                height: 80px;
                background: #eee;
                overflow: hidden;
            }
            .pnLabTitle{
                position: absolute;
                top: 20px;
                border-bottom: 1px solid #000;
                width: 40%;
                text-align: right;
                font-size: 20px;
                right: 0px;
            }
            div.output_subarea{
                padding:0px
            }            
        </style>

        <div id="pnlab_header_''' + str(self.ref) + '''"></div>
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

     
                class PNLabComponent extends React.Component {
                    constructor(props) {
                        super(props)
                    }    

                    render(){
                        var logo = React.createElement("div", {key:Util.create_UUID(), className:"pnLabLogo", style:{}})
                        var title = React.createElement("div", {key:Util.create_UUID(), className:"pnLabTitle", style:{}},"PN-Junction Lab")
                        
                        var div = React.createElement("div", {key:Util.create_UUID(), className:"pnLabHeader"}, [logo, title])                        
                        return div
                    }
                }

                ReactDOM.render(
                    React.createElement(PNLabComponent, {}),
                    document.getElementById("pnlab_header_''' + str(self.ref) + '''")
                );
            });
        '''        
       
        return header_view, header_js

    def buildParameters(self):    
        parameter_component_view = '''
        <style>
            .ComponentOptionSelected, .ComponentOption{
                height: 35px;
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
                            "band":{
                                "alt" : "Energy Band Diagram",
                                "label" : "Energy Band",
                                "action" : function(){ self.displayParameter('band') },
                            },
                            "iv":{
                                "alt" : "I-V Characteristics",
                                "label" : "I-V Characteristics",
                                "action" : function(){ self.displayParameter('iv') },
                            },                            
                            "cv":{
                                "alt" : "C-V Characteristics",
                                "label" : "C-V Characteristics",
                                "action" : function(){ self.displayParameter('cv') },
                            },
                            "current":{
                                "alt" : "Electron and Hole Current",
                                "label" : "Total Current",
                                "action" : function(){ self.displayParameter('current') },
                            },
                            "density":{
                                "alt" : "Electron and Hole Density",
                                "label" : "Total Density",
                                "action" : function(){ self.displayParameter('density') },
                            },
                            "net":{
                                "alt" : "Net Charge Density",
                                "label" : "Charge Density",
                                "action" : function(){ self.displayParameter('net') },
                            },
                            "potential":{
                                "alt" : "Electrostatic Potential",
                                "label" : "Electric Potential",
                                "action" : function(){ self.displayParameter('potential') },
                            },
                            "field":{
                                "alt" : "Electric Field",
                                "label" : "Electric Field",
                                "action" : function(){ self.displayParameter('field') },
                            },
                            "recombination":{
                                "alt" : "Recombination Rate",
                                "label" : "Recombination",
                                "action" : function(){ self.displayParameter('recombination') },
                            },
                            "carrier":{
                                "alt" : "Excess Carrier Density",
                                "label" : "Carrier Density",
                                "action" : function(){ self.displayParameter('carrier') },
                            },
                            "options":{
                                "alt" : "Settings",
                                "label" : "Settings",
                                "action" : function(){ self.displayOptions() },
                            },
                            

                        }, 
                        selectedParameter:"''' + self.current_view + '''",
                    } 
                }    

                changeTheme( option ){
                    if (option == "dark")
                        PNToySimplified_''' + str(self.ref) + '''["exposedChangeTheme"]('plotly_dark');
                    else if (option == "white")
                        PNToySimplified_''' + str(self.ref) + '''["exposedChangeTheme"]('plotly_white');
                    else
                        PNToySimplified_''' + str(self.ref) + '''["exposedChangeTheme"]('plotly');
                }

                todo(){
                    PNToySimplified_''' + str(self.ref) + '''["exposedTest"]("TODO", "TODO");
                }

                displayOptions(){
                    PNToySimplified_''' + str(self.ref) + '''["exposedDisplayOptions"]();
                }

                displayParameter( parameter ){
                    PNToySimplified_''' + str(self.ref) + '''["exposedDisplay"](parameter);
                }

                selectParameter(parameter){
                    this.setState({
                        selectedParameter:parameter, 
                    })
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
                        display: "flex",
                        alignItems: "center",
                        flexDirection: "row",
                        justifyContent: "center",
                    }       

                    var style2 = {
                        width:"100px",
                        display: "flex",
                        alignItems: "center",
                        flexDirection: "row",
                        justifyContent: "center",
                    }    
      
                    let self = this
                    
                    for (let parameter in this.state.parameters) {
                        let parameter_instance = this.state.parameters[parameter]
                        if (parameter != this.state.selectedParameter){
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOption", style:style, onClick:function(e){self.callParameter(parameter)}, title:parameter_instance.alt}, parameter_instance.label))
                        } else {
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSelected", style:style, onClick:function(e){self.callParameter(parameter)}, title:parameter_instance.alt}, parameter_instance.label))
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
            
    def getSequences(self, sequences):
        lists = {}
        for sequence in sequences:
            text = ""
            if 'id' in sequence.attrib:
                text = sequence.attrib['id']
                if text != "":
                    lists[text] = sequence
        return lists;                


    def getCache(self):
        parameters = self.getCurrentParameters( )
        hashstr =  json.dumps(parameters, sort_keys=True).encode()
        hashitem = hashlib.sha1(hashstr).hexdigest()
        if self.hashitem != hashitem:
            xml = self.loadCache(parameters, hashitem)
            self.xml = xml
            results = xml.find('output')
            sequences = self.getSequences(results.findall('sequence'))
            self.band = sequences.get("s1", None)
            self.current = sequences.get("s0", None)
            self.density = sequences.get("s2", None)
            self.carrier = sequences.get("s3", None)
            self.net = sequences.get("s4", None)
            self.potential = sequences.get("s5", None)
            self.field = sequences.get("s6", None)
            self.recombination = sequences.get("s7", None)
            curves = self.getSequences(results.findall('curve'))
            self.cv = curves.get("cap", None)
            self.iv = curves.get("iv", None)
            ro_ddaq = curves.get("ro_ddaq", None)
            if ro_ddaq is not None: 
                ro_ddaq.find('about').find('group').text = "Net Charge Density (at applied bias)"
                if ro_ddaq.find('about').find('style') is None:
                    ET.SubElement(ro_ddaq.find('about'),'style')
                ro_ddaq.find('about').find('style').text = "-color red -linestyle dashed"
                els = self.net.findall('element')
                for i,el in enumerate(els):
                    if (i == 0):
                        el.append(ro_ddaq)
                    else:
                        el.append(ET.fromstring('<curve id="ro_ddaq"><about><label></label><group>Net Charge Density (at applied bias)</group></about><component><xy>0 0</xy></component></curve>'))
            self.history[hashitem] = {
                "band": self.band,
                "current": self.current,
                "density": self.density,
                "carrier": self.carrier,
                "net": self.net,
                "potential": self.potential,
                "field": self.field,
                "recombination": self.recombination,
                "cv": self.cv,
                "iv": self.iv,
                "timestamp" : datetime.now().timestamp(),
                "parameters" : parameters
            }

        with self.content_component_output:
            clear_output()
        self.hashitem = hashitem   


    def exposedDisplay(self, option):
        self.getCache()
        self.current_view = option
        if option == "band":
            self.plotSequence("band",[self.hashitem],self.content_component_output)
        elif option == "current":
            self.plotSequence("current",[self.hashitem],self.content_component_output)
        elif option == "density":
            self.plotSequence("density",[self.hashitem],self.content_component_output)
        elif option == "carrier":
            self.plotSequence("carrier",[self.hashitem],self.content_component_output)
        elif option == "net":
            self.plotSequence("net",[self.hashitem],self.content_component_output)
        elif option == "potential":
            self.plotSequence("potential",[self.hashitem],self.content_component_output)
        elif option == "field":
            self.plotSequence("field",[self.hashitem],self.content_component_output)
        elif option == "recombination":
            self.plotSequence("recombination",[self.hashitem],self.content_component_output)
        elif option == "cv":
            self.plotXY("cv",[self.hashitem],self.content_component_output)
        elif option == "iv":
            self.plotXY("iv",[self.hashitem],self.content_component_output)
        #self.sl.value = 1
            
    def loadCache(self, parameters, hashitem):
        xml = None
        if hashitem in self.hashtable:
            self.loggingMessage("LOADING CACHE ...." + hashitem, self.content_component_output)

            with open(self.hashtable[hashitem],'rt' ) as f:
                xml = f.read()
        else:
            if os.path.isfile(hashitem + ".xml"):
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
                                time.sleep(5);
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
        ly = {"title":"", 'xaxis':{'type':"","title": ""}, 'yaxis':{'type':"","title": ""}}
        for hash in hashlist:
            if (hash in self.history) and field in (self.history[hash]):            
                tr, ly = self.buildXYPlotly([self.history[hash][field]])
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
                    'title' : ly['xaxis']['title'],
                    'type' : ly['xaxis']['type'],
                    'autorange' : True,
                },
                'yaxis' : {
                    'title' : ly['yaxis']['title'],
                    'type' : ly['yaxis']['type'],
                    'autorange' : True,
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

            
            
    def plotSequence(self, sequence, hashlist, out):
        traces = []
        layout = {}
        frames = {}
        options = []
        min_tr_x = None
        min_tr_y = None
        max_tr_x = None
        max_tr_y = None
        for hash in hashlist:
            if (hash in self.history) and sequence in (self.history[hash]):
                elements = self.history[hash][sequence].findall('element')
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
                        tr, lay = self.buildXYPlotly(groups[list(groups.keys())[0]])
                        if (hash != self.hashitem):
                            p1 = self.history[self.hashitem]["parameters"].items()
                            p2 = self.history[hash]["parameters"].items()
                            value = set([k+":"+v for k,v in p2]) - set([k+":"+v for k,v in p1])
                            diff = ", ". join(value)
                            for t in tr:
                                t['hovertext'] = diff
                                t['hoverinfo'] = "text+x+y"
                                t["line"]["color"] = "lightgrey"
                            
                        for t in tr:
                            try :
                                if (lay['xaxis']['type'] == "log"):
                                    minx = min(i for i in t['x'] if i > 0)
                                    maxx = max(i for i in t['x'] if i > 0)                        
                                else:
                                    minx = min(t['x'])
                                    maxx = max(t['x'])
                                if (min_tr_x ==None or min_tr_x > minx):
                                    min_tr_x = minx
                                if (max_tr_x ==None or max_tr_x < maxx):
                                    max_tr_x = maxx
                            except :    
                                pass

                            try :
                                if (lay['yaxis']['type'] == "log"):
                                    miny = min(i for i in t['y'] if i > 0)
                                    maxy = max(i for i in t['y'] if i > 0)                        
                                else:
                                    miny = min(t['y'])
                                    maxy = max(t['y'])
                                    
                                if (min_tr_y ==None or min_tr_y > miny):
                                    min_tr_y = miny
                                if (max_tr_y ==None or max_tr_y < maxy):
                                    max_tr_y = maxy
                            except:
                                pass
                        if len(traces) == 0:
                            layout = lay
                            traces = tr
                        if index in frames:
                            frames[index].extend(tr)
                        else:
                            options.append(index)                        
                            frames[index] = tr
        self.fig.data=[]

        if (layout['xaxis']['type'] == "log"):
            if (min_tr_x > 0):
                min_tr_x = math.log(min_tr_x, 10)
            elif (min_tr_x < 0):
                min_tr_x = -math.pow(min_tr_x, 10)
            if (max_tr_x > 0):
                max_tr_x = math.log(max_tr_x, 10)
            elif (max_tr_x < 0):
                max_tr_x = -math.pow(max_tr_x, 10)
        
        if (layout['yaxis']['type'] == "log"):
            if (min_tr_y > 0):
                min_tr_y = math.log(min_tr_y, 10)
            elif (min_tr_y < 0):
                min_tr_y = -math.pow(min_tr_y, 10)
            if (max_tr_y > 0):
                max_tr_y = math.log(max_tr_y, 10)
            elif (max_tr_y < 0):
                max_tr_y = -math.pow(max_tr_y, 10)

        
        self.fig.update({
            'data': traces,
            'layout' : {
                'title' : layout['title'],
                'xaxis' : {
                    'title' : layout['xaxis']['title'],
                    'range' : [min_tr_x, max_tr_x],
                    'type' : layout['xaxis']['type'],
                    'autorange' : False,
                    
                },
                'yaxis' : {
                    'title' : layout['yaxis']['title'],
                    'range' : [min_tr_y, max_tr_y],
                    'type' : layout['yaxis']['type'],
                    'autorange' : False,
                },
            }, 
        })

        self.sl = SelectionSlider(options=options, value=options[0], description=label)
        play = Play(interval=500, value=0, min=0, max=len(frames), description=label )
        buttons = [play]
        
        if (len(hashlist) == 1 and len(self.history)>1):        
            bt = Button(description="Compare",layout=Layout(width='auto'))
            bt.on_click(lambda e, this=self, s=sequence, o=out: this.showHistory(s,o))
            buttons.append(bt)
        elif (len(self.history)>1):
            bt2 = Button(description="Clear History",layout=Layout(width='auto'))
            bt2.on_click(lambda e, this=self, s=sequence, o=out: this.clearHistory(s,o))
            buttons.append(bt2)
        self.sl.observe(lambda change, this=self, f=frames, g=self.fig, p=play, s=self.sl: Rappturetool.updateFrame(this, change, f, g, p, s), "value")
        play.observe(lambda change, this=self, f=frames, g=self.fig, p=play, s=self.sl: setattr(self.sl, 'value', list(f.keys())[change['new']]), "value")
        self.sl.layout.width='99%'
        if (sequence == "carrier" or sequence == "current"):
            self.sl.value=self.sl.options[1]
        container = VBox([self.fig,HBox(buttons),self.sl], layout=layout)

        out.clear_output()
        with out:
            display(container)            
            
    def showHistory(self, sequence, out):
        hashlist = []
        for hash in (sorted(self.history, key=lambda hash: self.history[hash]["timestamp"], reverse=True)):
            hashlist.append(hash)
        if sequence in ["iv", "cv"]:
            self.plotXY(sequence, hashlist, out)        
        else :
            self.plotSequence(sequence, hashlist, out)
            
    def clearHistory(self, sequence, out):
        self.history = {k: v for k, v in self.history.items() if k == self.hashitem}
        self.showHistory(sequence, out)
            