from .rappturetool import Rappturetool
from ipywidgets import HBox, VBox, HTML, Image, Layout, Button, ButtonStyle, Tab, Output, Box, Textarea, SelectionSlider, Play
from IPython.display import Javascript, clear_output
from IPython.display import HTML as IHTML                                    
from hublib import ui
import xml.etree.ElementTree as ET
from plotly.graph_objs import FigureWidget
from .crystalsimplified import InstanceTracker
import hashlib, json
import math, os, base64
import numpy as np
import uuid, weakref, inspect, time


        
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
        self.current_view = "band"
        self.hashitem = None;
        self.hashtable = {}        
        self.ref = id(self)        
        self.junction_component_output = Output(layout=Layout(width="100%", padding="0px"))        
        self.parameters_component_output = Output(layout=Layout(height="100%", padding="0px"))
        self.content_component_output = Output(layout=Layout(flex='1', padding="0px", overflow="scroll"))        
        self.fig = FigureWidget({
            'data': [],
            'layout': { 
                'height' : 620,                 
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
            }
        })  
        
        
        parameters = self.parameters_structure + self.parameters_materials + self.parameters_ambient + self.parameters_additional
        kwargs.setdefault('title', 'P-N junction')
        Rappturetool.__init__(self, credentials, "pntoy", parameters, extract_method="id", **kwargs)

        
    def displayOptions(self):        
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
            if self.options[ii].visible:
                pass;
            elif ii in default_list :
                self.options[ii].value == default_list[ii]
            else: 
                self.options[ii].value == self.default_options[ii]

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
                self.junction_component_output,
                HBox([
                    self.parameters_component_output,
                    self.content_component_output
                ], layout=Layout(flex='1', height="100%"))
            ], layout=Layout(flexDirection="row", width="100%", height="700px")))

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
                                "alt" : "Settings",
                                "label" : "Settings",
                                "action" : function(){ self.displayOptions() },
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
                            "band":{
                                "alt" : "Energy Band Diagram",
                                "label" : "Energy Band",
                                "action" : function(){ self.displayParameter('band') },
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
                            "carrier":{
                                "alt" : "Excess Carrier Density",
                                "label" : "Carrier Density",
                                "action" : function(){ self.displayParameter('carrier') },
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

                        }, 
                        selectedParameter:"''' + self.current_view + '''",
                    } 
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

                    var components = React.createElement("div", {key:Util.create_UUID(), className:"ComponentParameters"}, children)

                    var opt = React.createElement("div", {key:Util.create_UUID(), className:"", style:{display:"flex", flexDirection:"row", backgroundColor:'#EEEEEE', justifyContent:'flex-start', height:'700px', width:'160px', borderRight:'4px solid #FFF'}}, [components])
                    var views = React.createElement("div", {key:Util.create_UUID(), className:"viewsTitle"}, "Views")
                    var div = React.createElement("div", {key:Util.create_UUID(), className:"", style:{display:"flex", flexDirection:"column", backgroundColor:'#EEEEEE', justifyContent:'flex-start', height:'700px'}}, [opt])
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
        #crystal_component_view, crystal_component_js = self.buildCrystal()
        parameter_component_view, parameter_component_js = self.buildParameters()
        
        #with self.junction_component_output:
        #    display(IHTML(crystal_component_view))
        #    display(Javascript(crystal_component_js)) 
    
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
            
            
        with self.content_component_output:
            clear_output()  
        self.hashitem = hashitem                    

        

    def exposedDisplay(self, option):
        self.getCache()
        self.current_view = option
        if option == "band":
            self.plotSequence(self.band,self.content_component_output)
        elif option == "current":
            self.plotSequence(self.current,self.content_component_output)
        elif option == "density":
            self.plotSequence(self.density,self.content_component_output)
        elif option == "carrier":
            self.plotSequence(self.carrier,self.content_component_output)
        elif option == "net":
            self.plotSequence(self.net,self.content_component_output)
        elif option == "potential":
            self.plotSequence(self.potential,self.content_component_output)
        elif option == "field":
            self.plotSequence(self.field,self.content_component_output)
        elif option == "recombination":
            self.plotSequence(self.recombination,self.content_component_output)
        elif option == "cv":
            self.plotXY([self.cv],self.content_component_output)
        elif option == "iv":
            self.plotXY([self.iv],self.content_component_output)
    
            
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
                self.loggingMessage("GENERATING CACHE ...." + hashitem, self.content_component_output)                
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
                            print ("Running ", session_id)
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


    def plotSequence(self, sequence, out, labels=None):
        traces = []
        layout = {}
        frames = {}
        options = []
        elements = sequence.findall('element')
        label = self.getText(sequence, ["index", "label"])
        min_tr_x = None
        min_tr_y = None
        max_tr_x = None
        max_tr_y = None
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


        sl = SelectionSlider(options=options, value=options[0], description=label)
        play = Play(interval=500, value=0, min=0, max=len(frames), description=label )
        sl.observe(lambda change, this=self, f=frames, g=self.fig, p=play, s=sl: Rappturetool.updateFrame(this, change, f, g, p, sl), "value")
        play.observe(lambda change, this=self, f=frames, g=self.fig, p=play, s=sl: setattr(sl, 'value', list(f.keys())[change['new']]), "value")
        sl.layout.width='99%'
        container = VBox([self.fig,play,sl], layout=layout)   

        out.clear_output()
        with out:
            display(container)
            
    def plotXY(self, fields, out, labels=None):
        traces, layout = self.buildXYPlotly(fields, labels)
        out.clear_output()   
        self.fig.data=[]
        self.fig.update({
            'data': traces,
            'layout' : {
                'title' : layout['title'],
                'xaxis' : {
                    'title' : layout['xaxis']['title'],
                    'type' : layout['xaxis']['type'],
                    'autorange' : True,
                },
                'yaxis' : {
                    'title' : layout['yaxis']['title'],
                    'type' : layout['yaxis']['type'],
                    'autorange' : True,
                },
            }, 
        })        
        with out:
            display(self.fig)

            