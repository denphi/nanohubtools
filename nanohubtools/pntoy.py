from .rappturetool import Rappturetool
from ipywidgets import HBox, VBox, HTML, Image, Layout, Button, ButtonStyle, Tab
from .plotlywidget import FigureWidget
import math


class PNToy (Rappturetool):
    def __init__(self, credentials, **kwargs):
                                            
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
        parameters = self.parameters_structure + self.parameters_materials + self.parameters_ambient + self.parameters_additional
        kwargs.setdefault('title', 'P-N junction')
        Rappturetool.__init__(self, credentials, "pntoy", parameters, extract_method="id", **kwargs)

        
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

        self.options['impuritydoping'].visible = False
        self.options['impuritylevel'].visible = False
        self.options['impurity'].dd.observe(lambda b : setattr(self.options['impuritydoping'], 'visible', (b['new'] == "yes")), 'value')
        self.options['impurity'].dd.observe(lambda b : setattr(self.options['impuritylevel'], 'visible', (b['new'] == "yes")), 'value')

        sqpntoytab = Tab()


        layout = {
            'autosize' : True,
            'width' : 440,
            'height' : 200,
            'margin' : {
                'l' : 55,
                'r' : 10,
                'b' : 25,
                't' : 70,
            },
            'xaxis' : {
                'autorange' : True,
            },
            'yaxis' : {
                'type' : 'log',
                'exponentformat' : "e"
            },       
            'shapes': [
                {
                    'type': 'rect',
                    'xref': 'x',
                    'yref': 'paper',
                    'x0': 0,
                    'y0': 0,
                    'x1': 0,
                    'y1': 1,
                    'fillcolor': '#800080',
                    'opacity': 0.2,
                    'line': { 'width': 0 }
                },
                {
                    'type': 'rect',
                    'xref': 'x',
                    'yref': 'paper',
                    'x0': 0,
                    'y0': 0,
                    'x1': 1,
                    'y1': 1,
                    'fillcolor': '#EEEEEE',
                    'opacity': 0.2,
                    'line': { 'width': 0 }
                },                
                {
                    'type': 'rect',
                    'xref': 'x',
                    'yref': 'paper',
                    'x0': 0,
                    'y0': 0,
                    'x1': 1,
                    'y1': 1,
                    'fillcolor': '#228B22',
                    'opacity': 0.2,
                    'line': { 'width': 0 }
                },
                {
                    'type': 'rect',
                    'xref': 'x',
                    'yref': 'paper',
                    'x0': 0,
                    'y0': 1.1,
                    'x1': 0,
                    'y1': 1.3,
                    'fillcolor': '#800080',
                    'opacity': 1.0,
                    'line': { 'width': 0 }
                },
                {
                    'type': 'rect',
                    'xref': 'x',
                    'yref': 'paper',
                    'x0': 0,
                    'y0': 1.1,
                    'x1': 1,
                    'y1': 1.3,
                    'fillcolor': '#EEEEEE',
                    'opacity': 1.0,
                    'line': { 'width': 0 }
                },                                
                {
                    'type': 'rect',
                    'xref': 'x',
                    'yref': 'paper',
                    'x0': 0,
                    'y0': 1.1,
                    'x1': 1,
                    'y1': 1.3,
                    'fillcolor': '#228B22',
                    'opacity': 1.0,
                    'line': { 'width': 0 }
                },   
            ],
            'annotations' : [
                {
                    'x':0.1,
                    'y':1.2,
                    'xref':'x',
                    'yref':'paper',
                    'text':'P-type',
                },
                {
                    'x':0.2,
                    'y':1.2,
                    'xref':'x',
                    'yref':'paper',
                    'text':'Intrinsic',
                },
                {
                    'x':0.3,
                    'y':1.2,
                    'xref':'x',
                    'yref':'paper',
                    'text':'N-type',
                },
            ]
        }
        trace1 = {
            'type' : 'scattergl',
            'x' : [0,0.18],
            'y' : [self.options['Na'].value,self.options['Na'].value],
            'line' : {'color' : '#800080'},
            'showlegend': False,
            'mode' : 'lines',
            'name' : 'p-type',
        }
        trace2 = {
            'type' : 'scattergl',
            'x' : [0.22,0.4],
            'y' : [self.options['Nd'].value,self.options['Nd'].value],
            'line' : {'color' : '#228B22'},
            'showlegend': False,
            'mode' : 'lines',
            'name' : 'n-type',
        }        
        self.fig = FigureWidget(data=[trace1, trace2], layout=layout, config={'displayModeBar': False})
        self.updateChart()
        self.options['Na'].dd.observe(lambda a, b=self : b.updateChart(), 'value')        
        self.options['Nd'].dd.observe(lambda a, b=self : b.updateChart(), 'value')        
        self.options['p_len'].dd.observe(lambda a, b=self : b.updateChart(), 'value')        
        self.options['i_len'].dd.observe(lambda a, b=self : b.updateChart(), 'value')        
        self.options['n_len'].dd.observe(lambda a, b=self : b.updateChart(), 'value')        
        children_structure.append(self.fig)

        
        children_materials.append(self.options_but)
        children_structure.append(self.options_but)
        #children_introduction.append(self.options_but)
        children_ambient.append(self.options_but)
        
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
        
        
    def updateChart(self):
        p0 = 0
        p1 = p0 + self.options['p_len'].value
        p2 = p1 + self.options['i_len'].value
        p3 = p2 + self.options['n_len'].value
        self.fig.data[0].update({
            'y' : [self.options['Na'].value, self.options['Na'].value],
            'x' : [p0, p1],
        })
        self.fig.data[1].update({
            'y' : [self.options['Nd'].value, self.options['Nd'].value],
            'x' : [p2, p3]
        })
        self.fig.layout.update({
            'shapes[0].x0': p0,
            'shapes[0].x1': p1,
            'shapes[1].x0': p1,
            'shapes[1].x1': p2,
            'shapes[2].x0': p2,
            'shapes[2].x1': p3,
            'shapes[3].x1': p1,
            'shapes[4].x0': p1,
            'shapes[4].x1': p2,
            'shapes[5].x0': p2,
            'shapes[5].x1': p3,
            'annotations[0].x': ((p0+p1)/2),
            'annotations[1].x': ((p1+p2)/2),
            'annotations[2].x': ((p2+p3)/2),
        })
        
        

        