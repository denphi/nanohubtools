from .rappturetool import Rappturetool, __file__
from .crystalviewer import CrystalViewerTool
from ipywidgets import HBox, VBox, HTML, Image, Layout, Button, ButtonStyle, Tab, Output, Box
from IPython.display import Javascript, clear_output
from IPython.display import HTML as IHTML                                    
from .plotlywidget import FigureWidget      
import uuid, weakref, inspect, time
import xml.etree.ElementTree as ET
import hashlib, json
import math, os, base64

from numpy import linspace as nplinspace
from numpy import pi as nppi
from numpy import sin as npsin
from numpy import cos as npcos
from numpy import outer as npouter
from numpy import outer as npones
from numpy import array as nparray
from numpy import meshgrid as npmeshgrid
from numpy import fromstring as npfromstring
from numpy import concatenate as npconcatenate
from numpy import mgrid as npmgrid
from numpy import random as nprandom
from numpy import linalg as nplinalg
from numpy import cross as npcross
from numpy import ceil as npceil
from numpy import around as nparound

class InstanceTracker(object):
    __instances__ = weakref.WeakValueDictionary()

    def __init__(self, *args, **kwargs):
        self.__instances__[id(self)]=self

    @classmethod
    def find_instance(cls, obj_id):
        return cls.__instances__.get(obj_id, None)


        
class CrystalSimplified (InstanceTracker, CrystalViewerTool):
    jcpk = {
        'H'  : 'rgba(255,255,255,1.0)',
        'He'  : 'rgba(20,20,20,1.0)',
        'Li' : 'rgba(188,190,187,1.0)',
        'Be' : 'rgba(134,134,134,1.0)',
        'B' : 'rgba(122,117,114,1.0)',
        'C' : 'rgba(31,120,180,1.0)',
        'N' : 'rgba(177,89,40,1.0)',
        'O' : 'rgba(238,32,16,1.0)',
        'F' : 'rgba(177,146,82,1.0)',
        'Ne' : 'rgba(255,0,0,1.0)',
        'Na' : 'rgba(218,220,217,1.0)',
        'Mg' : 'rgba(195,195,185,1.0)',
        'Al' : 'rgba(255,0,102,1.0)',
        'Si' : 'rgba(73,4,170,1.0)',
        'P' : 'rgba(255,0,9,1.0)',
        'S' : 'rgba(248,239,146,1.0)',
        'Cl' : 'rgba(251,154,153,1.0)',
        'Ar' : 'rgba(221,112,244,1.0)',
        'K' : 'rgba(165,171,171,1.0)',
        'Ca' : 'rgba(227,26,28,1.0)',
        'Sc' : 'rgba(176,173,166,1.0)',
        'Ti' : 'rgba(169,163,147,1.0)',
        'V' : 'rgba(191,189,202,1.0)',
        'Cr' : 'rgba(191,198,206,1.0)',
        'Mn' : 'rgba(206,205,200,1.0)',
        'Fe' : 'rgba(185,183,184,1.0)',
        'Co' : 'rgba(171,163,160,1.0)',
        'Ni' : 'rgba(181,165,150,1.0)',
        'Cu' : 'rgba(196,78,46,1.0)',
        'Zn' : 'rgba(255,0,0,1.0)',
        'Ga' : 'rgba(255,51,0,1.0)',
        'Ge' : 'rgba(0,255,0,1.0)',
        'As' : 'rgba(255,255,0,1.0)',
        'Se' : 'rgba(191,71,75,1.0)',
        'Br' : 'rgba(154,32,24,1.0)',
        'Kr' : 'rgba(164,162,175,1.0)',
        'Rb' : 'rgba(122,119,110,1.0)',
        'Sr' : 'rgba(217,206,160,1.0)',
        'Y' : 'rgba(153,155,154,1.0)',
        'Zr' : 'rgba(153,143,133,1.0)',
        'Nb' : 'rgba(98,91,138,1.0)',
        'Mo' : 'rgba(93,88,85,1.0)',
        'Tc' : 'rgba(131,120,116,1.0)',
        'Ru' : 'rgba(153,147,149,1.0)',
        'Rh' : 'rgba(156,143,135,1.0)',
        'Pd' : 'rgba(162,161,157,1.0)',
        'Ag' : 'rgba(202,178,214,1.0)',
        'Cd' : 'rgba(106,106,104,1.0)',
        'In' : 'rgba(106,61,154,1.0)',
        'Sn' : 'rgba(126,120,94,1.0)',
        'Sb' : 'rgba(0,0,191,1.0)',
        'Te' : 'rgba(150,155,158,1.0)',
        'I' : 'rgba(95,98,105,1.0)',
        'Xe' : 'rgba(0,0,255,1.0)',
        'Cs' : 'rgba(167,170,175,1.0)',
        'Ba' : 'rgba(62,71,86,1.0)',
        'La' : 'rgba(196,184,172,1.0)',
        'Ce' : 'rgba(110,101,94,1.0)',
        'Pr' : 'rgba(96,91,97,1.0)',
        'Nd' : 'rgba(156,154,155,1.0)',
        'Pm' : 'rgba(102,102,102,1.0)',
        'Sm' : 'rgba(136,117,100,1.0)',
        'Eu' : 'rgba(217,213,204,1.0)',
        'Gd' : 'rgba(119,129,105,1.0)',
        'Tb' : 'rgba(236,241,235,1.0)',
        'Dy' : 'rgba(134,121,102,1.0)',
        'Ho' : 'rgba(131,123,121,1.0)',
        'Er' : 'rgba(177,182,175,1.0)',
        'Tm' : 'rgba(168,163,160,1.0)',
        'Yb' : 'rgba(0,255,0,1.0)',
        'Lu' : 'rgba(160,161,153,1.0)',
        'Hf' : 'rgba(171,188,178,1.0)',
        'Ta' : 'rgba(154,155,160,1.0)',
        'W' : 'rgba(60,0,255,1.0)',
        'Re' : 'rgba(123,123,121,1.0)',
        'Os' : 'rgba(185,196,200,1.0)',
        'Ir' : 'rgba(137,130,112,1.0)',
        'Pt' : 'rgba(210,211,205,1.0)',
        'Au' : 'rgba(203,152,53,1.0)',
        'Hg' : 'rgba(80,46,48,1.0)',
        'Tl' : 'rgba(143,141,142,1.0)',
        'Pb' : 'rgba(81,81,81,1.0)',
        'Bi' : 'rgba(114,106,103,1.0)',
        'Po' : 'rgba(139,153,164,1.0)',
        'At' : 'rgba(102,102,102,1.0)',
        'Rn' : 'rgba(71,132,0,1.0)',
        'Fr' : 'rgba(102,102,102,1.0)',
        'Ra' : 'rgba(156,152,125,1.0)',
        'Ac' : 'rgba(66,73,224,1.0)',
        'Th' : 'rgba(80,73,65,1.0)',
        'Pa' : 'rgba(154,147,92,1.0)',
        'U' : 'rgba(120,122,119,1.0)',
        'Np' : 'rgba(90,73,53,1.0)',
        'Pu' : 'rgba(200,200,200,1.0)',
        'Am' : 'rgba(117,80,28,1.0)',
        'Cm' : 'rgba(62,65,58,1.0)',
        'Bk' : 'rgba(208,208,208,1.0)',
        'Cf' : 'rgba(231,231,231,1.0)',
        'Es' : 'rgba(59,163,200,1.0)',
        'Fm' : 'rgba(102,102,102,1.0)',
        'Md' : 'rgba(102,102,102,1.0)',
        'No' : 'rgba(102,102,102,1.0)',
        'Lr' : 'rgba(102,102,102,1.0)',
        'Rf' : 'rgba(102,102,102,1.0)',
        'Db' : 'rgba(102,102,102,1.0)',
        'Sg' : 'rgba(102,102,102,1.0)',
        'Bh' : 'rgba(102,102,102,1.0)',
        'Hs' : 'rgba(102,102,102,1.0)',
        'Mt' : 'rgba(102,102,102,1.0)',
    }
    
    def __init__(self, credentials, **kwargs):
        InstanceTracker.__init__(self)                                  
        self.rebuild_fig = kwargs.get('rebuild_fig', True)
                
        self.samples = 20
        self.resize = .15
        self.phi = nplinspace(0, 2*nppi, self.samples)
        self.theta = nplinspace(-nppi/2, nppi/2, self.samples)
        self.thetat = nplinspace(0,2*nppi,self.samples)
        self.phit = nplinspace(0,nppi,self.samples)
        self.xt = npouter(npcos(self.thetat),npsin(self.phit)) * 4 * self.resize
        self.yt = npouter(npsin(self.thetat),npsin(self.phit)) * 4 * self.resize
        self.zt = npouter(npones(self.samples),npcos(self.phit)) * 4 * self.resize
        self.cosphi = npcos(self.phi) * self.resize
        self.sinphi = npsin(self.phi) * self.resize
        self.phi, self.theta=npmeshgrid(self.phi, self.theta)
        self.x = npcos(self.theta) * npsin(self.phi)
        self.y = npcos(self.theta) * npcos(self.phi)
        self.z = npsin(self.theta)
        self.x = self.x.flatten() * 4 * self.resize
        self.y = self.y.flatten() * 4 * self.resize
        self.z = self.z.flatten() * 4 * self.resize
        self.theme = "plotly_white"
        
        self.fig = FigureWidget(
            data= [],
            layout= { 
                'height' : 600, 
                'scene':{'aspectmode':'data'}, 
                'margin' : {'l':0,'r':0,'t':0,'b':0},
                'template' : self.theme,                
            }
        )  
        self.ref = id(self)
        parameters = self.parameters_structure + self.parameters_miller + self.parameters_additional
        kwargs.setdefault('title', 'CrystalViewer - Materials')
        CrystalViewerTool.__init__(self, credentials, parameters, **kwargs)
        self.reset_options = False
        
    def exposedChangeTheme(self, theme):
        self.updateTheme(theme)
        
    def updateTheme(self, theme):
        if (theme != self.theme and (theme == "plotly_white" or theme == "plotly_dark")):
            self.theme = theme
            self.fig.update({'layout':{'template':self.theme}});

    def refreshView(self):
        pass;

    def displayFrame(self):
        pass;

    def buildIcon(self, icon):
        path = os.path.dirname(__file__)
        image_encoded = ""
        with open(path+"/assets/" + icon,'rb' ) as f:
            image_encoded = f.read()                    
        image = base64.encodebytes(image_encoded).decode("utf-8") 
        html = "url(data:image/png;base64," + str(image).replace("\n", "").replace("=", "") +")"
        return json.loads(json.dumps(html))            
             
    
    def getDrawings(self, drawings):
        lists = {}
        for drawing in drawings:
            text = ""
            if 'id' in drawing.attrib:
                text = drawing.attrib['id']
                if text != "":
                    lists[text] = drawing
        return lists;
                
    def plotDrawingPlotly(self, draw, out):
        self.loggingMessage("Building Model", out)    
        label = self.getText(draw, ["index", "label"])
        if self.rebuild_fig:
            self.fig = FigureWidget(
                data= [],
                layout= { 
                    'height' : 600, 
                    'scene':{'aspectmode':'data'}, 
                    'margin' : {'l':0,'r':0,'t':0,'b':0},
                    'template' : self.theme,                
                }
            )           
        else:
            self.fig.data = []
        traces = []
        molecules = draw.findall('molecule')
        min_p = None
        max_p = None
        for molecule in molecules:
            atoms, connections = self.getMolecule(molecule)        

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
                    xv = (self.xt + atom[0]).tolist()
                    yv = (self.yt + atom[1]).tolist()
                    zv = (self.zt + atom[2]).tolist()
                    if min_p == None or max_p==None:    
                        min_p = [atom[0], atom[1], atom[2]]
                        max_p = [atom[0], atom[1], atom[2]]
                    else:
                        min_p[0] = min(min_p[0], atom[0])
                        min_p[1] = min(min_p[1], atom[1])
                        min_p[2] = min(min_p[2], atom[2])
                        max_p[0] = max(max_p[0], atom[0])
                        max_p[1] = max(max_p[1], atom[1])
                        max_p[2] = max(max_p[2], atom[2])

                    
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
                colorscalea = [[0,"rgba(200,0,0,0.01)"], [1,self.jcpk[atom]]]
                cv = [[1 for p in x] for x in xt[atom]]
                traces.append({
                    'type' : 'surface',
                    'x' : xt[atom], 
                    'y' : yt[atom], 
                    'z' : zt[atom], 
                    'cauto' : False,
                    'cmin' : 0,
                    'cmax' : 1,
                    'hovertext' : atom,
                    'showscale' : False,
                    'hoverinfo' : "text",
                    'colorscale' : colorscalea,
                    'surfacecolor' : cv,
                    'connectgaps' : False,
                    'lighting' : { 
                        'specular' : 2 ,
                        'ambient' : 0.8,
                        'diffuse' : 1, 
                        'roughness' : 1, 
                        'fresnel' : 2.0,
                    },
                })
                   
            
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
                    u = nparray([atoms[at2][i]-atoms[at1][i] for i in range(3)])        
                    u /= nplinalg.norm(u)
                    v1 = nprandom.randn(3)  
                    v1 -= v1.dot(u) * u       
                    v1 /= nplinalg.norm(v1)
                    v2 = npcross(v1, u)
                    v2 /= nplinalg.norm(v2)
                    sample = int(self.samples/2)
                    xd = nplinspace(atoms[at2][0], atoms[at1][0], sample, endpoint=True)
                    yd = nplinspace(atoms[at2][1], atoms[at1][1], sample, endpoint=True)
                    zd = nplinspace(atoms[at2][2], atoms[at1][2], sample, endpoint=True)
                    atm1 = atoms[at1][3]
                    if atm1 == "He":
                        atm1 = atoms[at2][3]
                    atm2 = atoms[at2][3]
                    if atm1 != atm2:
                        for i in range(0,int(sample/2)+2):
                            xt[atm2].append((self.cosphi*v1[0] + self.sinphi*v2[0] + xd[i]).tolist())
                            yt[atm2].append((self.cosphi*v1[1] + self.sinphi*v2[1] + yd[i]).tolist())
                            zt[atm2].append((self.cosphi*v1[2] + self.sinphi*v2[2] + zd[i]).tolist())
                        xt[atm2].append([])
                        zt[atm2].append([])
                        yt[atm2].append([])
                        
                        for i in range(int(sample/2)-1, sample):
                            xt[atm1].append((self.cosphi*v1[0] + self.sinphi*v2[0] + xd[i]).tolist())
                            yt[atm1].append((self.cosphi*v1[1] + self.sinphi*v2[1] + yd[i]).tolist())
                            zt[atm1].append((self.cosphi*v1[2] + self.sinphi*v2[2] + zd[i]).tolist())
                        xt[atm1].append([])
                        zt[atm1].append([])
                        yt[atm1].append([])
                    else:
                        for i in range(sample):
                            xt[atm1].append((self.cosphi*v1[0] + self.sinphi*v2[0] + xd[i]).tolist())
                            yt[atm1].append((self.cosphi*v1[1] + self.sinphi*v2[1] + yd[i]).tolist())
                            zt[atm1].append((self.cosphi*v1[2] + self.sinphi*v2[2] + zd[i]).tolist())
                        xt[atm1].append([])
                        zt[atm1].append([])
                        yt[atm1].append([])
            for c in colorset:    
                opacity = 1.0
                if c == "He":
                    opacity = 0.2
                cv = [[1 for p in x] for x in xt[c]]
                colorscalea = [[0,"rgba(200,0,0,0.01)"], [1,self.jcpk[c]]]

                traces.append({
                    'type' : 'surface',
                    'x' : xt[c], 
                    'y' : yt[c], 
                    'z' : zt[c], 
                    'cauto' : False,
                    'cmin' : 0,
                    'cmax' : 1,                    
                    'hovertext' : '',    
                    'showscale' : False,
                    'hoverinfo' : 'text',
                    'colorscale' : colorscalea,
                    'surfacecolor' : cv,                    
                    'connectgaps' : False,
                    'opacity' : opacity
                })
        min_p = [t - 0.2 for t in min_p]
        max_p = [t + 0.2 for t in max_p]
        self.boundary = [min_p, max_p]
        traces.append({
            'type' : 'mesh3d',
            'x' : [], 
            'y' : [], 
            'z' : [], 
            'color' : 'rgb(128,0,0)',
            'hovertext' : '',
            'hoverinfo' : 'text',
            'delaunayaxis' : None
        })

        self.fig.add_traces(traces)                                   
        with out:   
            clear_output()
            display(self.fig)
            
        return self.fig   


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

            
    def plotDrawing(self, draw, out):
        return self.plotDrawingPlotly(draw, out)
    
    def exposedUpdatePlane(self, center, plane):
        if (self.current_view != "lattice"):
            self.exposedDisplayLattice()
        self.current_view = "lattice"  
        center = float(center)
        if center > 1:
            center = 1
        elif center < 0:
            center = 0
        plane = json.loads(plane)
        if (len(plane) == 3):
            plane = [int(v) for v in plane]
            self.plane = plane
            self.center = center
            self.updatePlane(center, plane)
    
    def updatePlane(self, center, plane):
        self.normal = [ 
            plane[0]*self.unitvectors[0][0]+plane[0]*self.unitvectors[0][1]+plane[0]*self.unitvectors[0][2],
            plane[1]*self.unitvectors[1][0]+plane[1]*self.unitvectors[1][1]+plane[1]*self.unitvectors[1][2],
            plane[2]*self.unitvectors[2][0]+plane[2]*self.unitvectors[2][1]+plane[2]*self.unitvectors[2][2]
        ]        
        points = self.FindPlaneIntersect(
            (self.normal[0],self.normal[1],self.normal[2]), 
            center
        )
        xt = [point[0] for point in points]
        yt = [point[1] for point in points]
        zt = [point[2] for point in points]        
        delaunayaxis = None
        if len(set(xt)) == 1 : 
            delaunayaxis = 'x'
        elif len(set(yt)) == 1 : 
            delaunayaxis = 'y'
        elif len(set(zt)) == 1 : 
            delaunayaxis = 'z'        
        changes = {'data':[]}
        for ti, trace in enumerate(self.fig.data):
            if (trace.type == 'mesh3d'):
                changes['data'].append( {'x' : xt, 'y' : yt, 'z' : zt, 'delaunayaxis':delaunayaxis} )
            elif (trace.type == 'surface'):
                b = list(trace.surfacecolor)
                for i, v in enumerate(b):
                    if len(v) > 0:
                        point = [
                            (sum(trace.x[i])/len(v)),            
                            (sum(trace.y[i])/len(v)),
                            (sum(trace.z[i])/len(v))
                        ]
                        d = abs(point[0]*self.normal[0]+point[1]*self.normal[1]+point[2]*self.normal[2]-self.mid_point )
                        e = math.sqrt(self.normal[0]*self.normal[0]+self.normal[1]*self.normal[1]+self.normal[2]*self.normal[2])
                        if (d/e) < 0.4:
                            b[i] = [0 for j in b[i]]
                        else:
                            b[i] = [1 for j in b[i]]
                changes['data'].append( {'surfacecolor' : b} )
            else:
                changes['data'].append({})
        self.fig.update(changes)
        
    def exposedShowPlanes(self):
        remove = False
        for ti, trace in enumerate(self.fig.data):
            if (trace.type == 'mesh3d'):
                remove = True
        if remove:
            self.removePlanes()
        planes = [[1,0,0],[0,1,0],[0,0,1]]
        traces = []
        for plane in planes :
            self.normal = [ 
                plane[0]*self.unitvectors[0][0]+plane[0]*self.unitvectors[0][1]+plane[0]*self.unitvectors[0][2],
                plane[1]*self.unitvectors[1][0]+plane[1]*self.unitvectors[1][1]+plane[1]*self.unitvectors[1][2],
                plane[2]*self.unitvectors[2][0]+plane[2]*self.unitvectors[2][1]+plane[2]*self.unitvectors[2][2]
            ]        
            points = self.FindPlaneIntersect(
                (self.normal[0],self.normal[1],self.normal[2]), 
                0.5
            )
            xt = [point[0] for point in points]
            yt = [point[1] for point in points]
            zt = [point[2] for point in points]        
            delaunayaxis = None
            if len(set(xt)) == 1 : 
                delaunayaxis = 'x'
            elif len(set(yt)) == 1 : 
                delaunayaxis = 'y'
            elif len(set(zt)) == 1 : 
                delaunayaxis = 'z'        
            traces.append({
                'type' : 'mesh3d',
                'x' : xt, 
                'y' : yt, 
                'z' : zt, 
                'color' : 'rgb(128,0,0)',
                'hovertext' : '',
                'hoverinfo' : 'text',
                'delaunayaxis' : delaunayaxis
            })
        self.fig.add_traces(traces)

    def removePlanes(self):
        changes = {'data':[]}
        for ti, trace in enumerate(self.fig.data):
            if (trace.type == 'mesh3d'):
                changes['data'].append( {'x' : [], 'y' : [], 'z' : []} )
            else:
                changes['data'].append({})
        self.fig.update(changes)
                
    def FindPlaneIntersect(self, normal, center=0.5):
        min_p = self.boundary[0]
        max_p = self.boundary[1]
        faces = [
            (-1,0,0, min_p[0]),
            (0,-1,0, min_p[1]),
            (0,0,-1, min_p[2]),
            (-1,0,0, max_p[0]),
            (0,-1,0, max_p[1]),
            (0,0,-1, max_p[2]),
        ]
        
        epsilon  =1e-6        

        avg_p = [0,0,0]
        avg_p[0] = min_p[0] + (max_p[0]-min_p[0])/2
        avg_p[1] = min_p[1] + (max_p[1]-min_p[1])/2
        avg_p[2] = min_p[2] + (max_p[2]-min_p[2])/2
        min_point = None
        max_point = None
        line_points = set()
        for f in faces:
            planeNormal = nparray(f[:3])
            rayDirection = nparray(normal)
            ndotu = planeNormal.dot(rayDirection)
            if (abs(ndotu)>epsilon):
                planePoint = [-f[i]*f[3] for i in range(3)]
                rayPoint = nparray(avg_p)
                w = rayPoint - planePoint
                si = -planeNormal.dot(w) / ndotu
                Psi = nparound(w + si * rayDirection + planePoint, decimals=8)
                if (Psi[0] >= min_p[0]-epsilon and Psi[0] <= max_p[0]+epsilon):
                    if (Psi[1] >= min_p[1]-epsilon and Psi[1] <= max_p[1]+epsilon):
                        if (Psi[2] >= min_p[2]-epsilon and Psi[2] <= max_p[2]+epsilon):
                            line_points.add(tuple(Psi))
        if len(line_points) != 2:
            return [], [];
        line_points = list(line_points)
        min_point = line_points[0]
        max_point = line_points[1]

        avg_p[0] = min_point[0] + (max_point[0]-min_point[0])*center
        avg_p[1] = min_point[1] + (max_point[1]-min_point[1])*center
        avg_p[2] = min_point[2] + (max_point[2]-min_point[2])*center
        normal_point=avg_p[0]*normal[0] + avg_p[1]*normal[1] + avg_p[2]*normal[2]
        self.mid_point = normal_point
        points = []
        
        for b in faces:
            a_vec, b_vec = nparray(normal), nparray(b[:3])
            aXb_vec = npcross(a_vec, b_vec)
            A = nparray([a_vec, b_vec, aXb_vec])
            if nplinalg.det(A) != 0:
                d = nparray([normal_point, -b[3], 0.]).reshape(3,1)
                p_inter = nplinalg.solve(A, d).T            
                points.append((tuple(p_inter[0].tolist()), aXb_vec))

        pts = set()
        for pt in points:
            p, v = nparray(pt[0]), nparray(pt[1])
            for f in faces:
                planeNormal = nparray(f[:3])
                rayDirection = v
                ndotu = planeNormal.dot(rayDirection)
                if (abs(ndotu)>epsilon):
                    planePoint = [-f[i]*f[3] for i in range(3)]
                    rayPoint = nparray(p)
                    w = rayPoint - planePoint
                    si = -planeNormal.dot(w) / ndotu
                    Psi = w + si * rayDirection + planePoint
                    if (Psi[0] >= min_p[0] and Psi[0] <= max_p[0]):
                        if (Psi[1] >= min_p[1] and Psi[1] <= max_p[1]):
                            if (Psi[2] >= min_p[2] and Psi[2] <= max_p[2]):
                                pts.add(tuple(Psi.tolist()))
           
        return pts

        
class CrystalLab (InstanceTracker):
    session = None
    def __init__(self, credentials, **kwargs):
        self.ref = id(self)
        InstanceTracker.__init__(self)                                          
        self.window = None
        kwargs.setdefault('modal', False)                                         
        self.modal = False
        self.auth_data = credentials
        self.current_tool = "crystalviewer"
        self.options_cont = Output(layout=Layout(padding="0px", overflow="hidden", width="100%", height="50px"))
        self.output_cont = Output(layout=Layout(flex='1', padding="0px", overflow="auto", width="100%", height="700px"))
        self.tools = {
            "crystalviewer" : None,
            "bravaisviewer" : None
        }
        
        self.parameters = {}
        if (self.window == None) :
            self.window = Output()
            display(self.window)
            
        self.displayWindow()

    def buildInterfaceJS(self):
        interface_js = "<script type='text/Javascript'>\n";
        refobj = "CrystalLab_" + str(self.ref)
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
                interface_js += "    var command = 'from nanohubtools import CrystalLab ; CrystalLab.find_instance("+ str(self.ref) + ")." + method[0] +"(";
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
        display(IHTML(self.buildInterfaceJS()))
        with self.window:
            clear_output()
            display(VBox([                
                self.options_cont,
                self.output_cont,
            ], layout=Layout(flexDirection="row", width="100%", height="750px")))
        self.displayFrame()  
        self.exposedActivateTool(self.current_tool)
        
    def displayFrame(self):
        options_view, options_js = self.buildOptions()      
        with self.options_cont:
            display(IHTML(options_view))
            display(Javascript(options_js)) 

    def buildOptions(self):   
        options_view = '''
        <style>

            .crystalLabCrystalLogo{
                background-image: url("data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/Pgo8IURPQ1RZUEUgc3ZnIFBVQkxJQyAiLS8vVzNDLy9EVEQgU1ZHIDIwMDEwOTA0Ly9FTiIKICJodHRwOi8vd3d3LnczLm9yZy9UUi8yMDAxL1JFQy1TVkctMjAwMTA5MDQvRFREL3N2ZzEwLmR0ZCI+CjxzdmcgdmVyc2lvbj0iMS4wIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiB3aWR0aD0iNjkuMDAwMDAwcHQiIGhlaWdodD0iMTA2LjAwMDAwMHB0IiB2aWV3Qm94PSIwIDAgNjkuMDAwMDAwIDEwNi4wMDAwMDAiCiBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJ4TWlkWU1pZCBtZWV0Ij4KCjxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDAuMDAwMDAwLDEwNi4wMDAwMDApIHNjYWxlKDAuMTAwMDAwLC0wLjEwMDAwMCkiCmZpbGw9IiMwMDAwMDAiIHN0cm9rZT0ibm9uZSI+CjxwYXRoIGQ9Ik0yMDYgNzM4IGwtMTk3IC0yOTMgNTcgLTU0IGM1MiAtNDggNTggLTUxIDY3IC0zNSAzMCA1MyAyODcgNjQyIDI4Nwo2NTcgMCA5IC00IDE3IC04IDE3IC01IDAgLTk3IC0xMzIgLTIwNiAtMjkyeiIvPgo8cGF0aCBkPSJNNDUyIDEwMDAgYzQ2IC0xMzggMjE1IC01ODcgMjIwIC01ODQgMyAyIDkgMzggMTMgNzggbDcgNzQgLTExNyAyMTkKYy0xMTMgMjA5IC0xMzQgMjQ2IC0xMjMgMjEzeiIvPgo8cGF0aCBkPSJNNDQxIDYwMyBsLTEgLTM2MyAxMDQgODEgMTA1IDgxIC0xNCAzNiBjLTI0IDcwIC0xNzggNDg3IC0xODYgNTA3Ci00IDExIC04IC0xNDMgLTggLTM0MnoiLz4KPHBhdGggZD0iTTM3NCA4NDAgYy02MSAtMTI3IC0yMjQgLTQ5NiAtMjI0IC01MDggMCAtOSAyNTkgLTEwNiAyNjcgLTk5IDIgMiAyCjE1OSAxIDM0OCBsLTMgMzQ0IC00MSAtODV6Ii8+CjxwYXRoIGQ9Ik00NyAzMTMgYzE5IC01NCA0NSAtMTI1IDU3IC0xNTkgMTQgLTQyIDMzIC03MSA1OSAtOTMgMjAgLTE4IDM3IC0yOQozNyAtMjUgMCA1IC0xNiA2NyAtMzYgMTM5IC0zNSAxMjMgLTM5IDEzMyAtODggMTgzIC0yOCAyOCAtNTQgNTIgLTU4IDUyIC00IDAKOSAtNDQgMjkgLTk3eiIvPgo8cGF0aCBkPSJNNTQwIDI5NiBsLTEwNCAtODQgLTI3IC0xMDYgYy0xNSAtNTggLTI0IC0xMDYgLTIxIC0xMDYgMyAwIDM1IDE0CjcyIDMxIGw2NiAzMCA2MiAxNDMgYzc3IDE3OSA3NiAxNzYgNjYgMTc2IC01IC0xIC01NiAtMzkgLTExNCAtODR6Ii8+CjxwYXRoIGQ9Ik0xNTAgMjk0IGMwIC0xOSA3NSAtMjYxIDg0IC0yNzEgNiAtNiAzOCAtMTQgNzEgLTE4IGw2MCAtNiAyMyAxMDEKYzEzIDU2IDIxIDEwNCAxOSAxMDcgLTUgNSAtMjQ1IDkzIC0yNTMgOTMgLTIgMCAtNCAtMyAtNCAtNnoiLz4KPC9nPgo8L3N2Zz4K");
                background-size: 25px;
                background-repeat: no-repeat;
                background-position-x: 00px;
                background-position-y: 00px;
            }

            .crystalLabBravaisLogo{
                background-image: url("data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgd2lkdGg9IjY5IiBoZWlnaHQ9IjEwNiIgcHJlc2VydmVBc3BlY3RSYXRpbz0ieE1pZFlNaWQgbWVldCIgc3R5bGU9IiI+PHJlY3QgaWQ9ImJhY2tncm91bmRyZWN0IiB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4PSIwIiB5PSIwIiBmaWxsPSJub25lIiBzdHJva2U9Im5vbmUiLz4KCgo8ZyBjbGFzcz0iY3VycmVudExheWVyIiBzdHlsZT0iIj48dGl0bGU+TGF5ZXIgMTwvdGl0bGU+PGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMCwgMTA2KSBzY2FsZSgwLjEsIC0wLjEpIiBmaWxsPSIjMDAwMDAwIiBzdHJva2U9Im5vbmUiIGlkPSJzdmdfMSIgY2xhc3M9IiI+CjxwYXRoIGQ9Ik04NS4wMDcwMTYxODE5NDU4LDc1Mi44NjYzMzMwMDc4MTIzIGwtNjEuNzIxNDAxMjE0NTk5NjEsLTIyMy41NjA4MjE1MzMyMDMxMiBsNjAuNDA4MTc2NDIyMTE5MTQsLTE0OC42NDQxNDk3ODAyNzM0NCBjMzIuODMwNTI4MjU5Mjc3MzQ0LC04MC44NjI0MjY3NTc4MTI1IDY0LjM0NzgzOTM1NTQ2ODc1LC0xNTIuMjExNjI0MTQ1NTA3OCA2OS42MDA3MzA4OTU5OTYxLC0xNTYuOTY4MjQ2NDU5OTYwOTQgYzExLjgxODk5MTY2MTA3MTc3NywtMTAuNzAyMzgwMTgwMzU4ODg3IDMxNS4xNzMwOTU3MDMxMjUsLTEwNC42NDU0ODQ5MjQzMTY0IDMzNy40OTc4NjM3Njk1MzEyNSwtMTA0LjY0NTQ4NDkyNDMxNjQgYzE1Ljc1ODY1NDU5NDQyMTM4NywwIDEyNC43NTYwMTk1OTIyODUxNiwzNzIuMjA0OTg2NTcyMjY1NiAxMjMuNDQyODAyNDI5MTk5MjIsNDIzLjMzODU2MjAxMTcxODc1IGMwLDE5LjAyNjQ1MzAxODE4ODQ3NyAtMjQuOTUxMjAyMzkyNTc4MTI1LDk4LjY5OTcyOTkxOTQzMzYgLTU1LjE1NTI5MjUxMDk4NjMzLDE3NS45OTQ2ODk5NDE0MDYyNSBsLTU1LjE1NTI5MjUxMDk4NjMzLDE0MS41MDkyNDY4MjYxNzE4OCBsLTE2Mi44Mzk0NDcwMjE0ODQzOCw1OC4yNjg1MTI3MjU4MzAwOCBjLTkwLjYxMjI1ODkxMTEzMjgxLDMwLjkxNzk4NzgyMzQ4NjMyOCAtMTY5LjQwNTUzMjgzNjkxNDA2LDU3LjA3OTM2MDk2MTkxNDA2IC0xNzguNTk4MDgzNDk2MDkzNzUsNTcuMDc5MzYwOTYxOTE0MDYgYy03Ljg3OTMyNzI5NzIxMDY5MywwIC00Mi4wMjMwNzg5MTg0NTcwMywtOTguNjk5NzI5OTE5NDMzNiAtNzcuNDgwMDQ5MTMzMzAwNzgsLTIyMi4zNzE2NzM1ODM5ODQzOCB6IiBpZD0ic3ZnXzIiLz4KPC9nPjxwYXRoIGZpbGw9Im5vbmUiIGZpbGwtb3BhY2l0eT0iMSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utb3BhY2l0eT0iMSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSJub25lIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2UtbGluZWNhcD0iYnV0dCIgc3Ryb2tlLWRhc2hvZmZzZXQ9IiIgZmlsbC1ydWxlPSJub256ZXJvIiBvcGFjaXR5PSIxIiBtYXJrZXItc3RhcnQ9IiIgbWFya2VyLW1pZD0iIiBtYXJrZXItZW5kPSIiIGQ9Ik0zNi45OTAzOTYwMTIwNjY0MSw2NS40ODkxMzUxNDI2OTIyNSBMNTAuNTM2MjU1ODA3NDE1NzMsMjAuMDE0NTMxNTE0NDYyMzA1ICIgaWQ9InN2Z180IiBjbGFzcz0iIiBmaWx0ZXI9IiIvPjxwYXRoIGZpbGw9Im5vbmUiIGZpbGwtb3BhY2l0eT0iMSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utb3BhY2l0eT0iMSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSJub25lIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2UtbGluZWNhcD0iYnV0dCIgc3Ryb2tlLWRhc2hvZmZzZXQ9IiIgZmlsbC1ydWxlPSJub256ZXJvIiBvcGFjaXR5PSIxIiBtYXJrZXItc3RhcnQ9IiIgbWFya2VyLW1pZD0iIiBtYXJrZXItZW5kPSIiIGQ9Ik0yLjQ3MTU4NDA0MzUyMTk0MzQsNTMuMjQ0NDQyOTIyNjgzNDUgTDE1Ljc3NDMxNTk2Mjk2NTM3NSw4LjU4NjA0MjI3MDYwNzMyMiAiIGNsYXNzPSIiIGZpbHRlcj0iIiBpZD0ic3ZnXzUiLz48cGF0aCBmaWxsPSJub25lIiBmaWxsLW9wYWNpdHk9IjEiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLW9wYWNpdHk9IjEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWRhc2hhcnJheT0ibm9uZSIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLWxpbmVjYXA9ImJ1dHQiIHN0cm9rZS1kYXNob2Zmc2V0PSIiIGZpbGwtcnVsZT0ibm9uemVybyIgb3BhY2l0eT0iMSIgbWFya2VyLXN0YXJ0PSIiIG1hcmtlci1taWQ9IiIgbWFya2VyLWVuZD0iIiBkPSJNNDkuMzcxMjM2MzY3NzcwNTEsOTQuODQyOTQzMjE0MjE2NTggTDYyLjQ0MDkyMzI5ODMwOTgyNiw1MC45NjY5MjA5NTk4MzE0NCAiIGNsYXNzPSIiIGZpbHRlcj0iIiBpZD0ic3ZnXzMiLz48cGF0aCBmaWxsPSJub25lIiBmaWxsLW9wYWNpdHk9IjEiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLW9wYWNpdHk9IjEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWRhc2hhcnJheT0ibm9uZSIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLWxpbmVjYXA9ImJ1dHQiIHN0cm9rZS1kYXNob2Zmc2V0PSIiIGZpbGwtcnVsZT0ibm9uemVybyIgb3BhY2l0eT0iMSIgbWFya2VyLXN0YXJ0PSIiIG1hcmtlci1taWQ9IiIgbWFya2VyLWVuZD0iIiBkPSJNNjEuOTY0NTMwOTQ0ODI0MjIsNTEuMjYyNjI4NjQ0NzA0ODIgTDUxLjY1NjA1MTYzNTc0MjE5LDE5LjQ0MDgwNzQzMTkzNjI2NCAiIGlkPSJzdmdfNiIgY2xhc3M9IiIvPjxwYXRoIGZpbGw9Im5vbmUiIGZpbGwtb3BhY2l0eT0iMSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utb3BhY2l0eT0iMSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSJub25lIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2UtbGluZWNhcD0iYnV0dCIgc3Ryb2tlLWRhc2hvZmZzZXQ9IiIgZmlsbC1ydWxlPSJub256ZXJvIiBvcGFjaXR5PSIxIiBtYXJrZXItc3RhcnQ9IiIgbWFya2VyLW1pZD0iIiBtYXJrZXItZW5kPSIiIGQ9Ik00OS4xMDc2NTQ1NzE1MzMyLDk0LjU4NTk2NzQ2NjI5MzM3IEwzNy4zNzA3NjE4NzEzMzc4OSw2NC42NzY5MTA2MzM3MzA1OSAiIGNsYXNzPSIiIGlkPSJzdmdfOSIvPjxwYXRoIGZpbGw9Im5vbmUiIGZpbGwtb3BhY2l0eT0iMSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utb3BhY2l0eT0iMSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSJub25lIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2UtbGluZWNhcD0iYnV0dCIgc3Ryb2tlLWRhc2hvZmZzZXQ9IiIgZmlsbC1ydWxlPSJub256ZXJvIiBvcGFjaXR5PSIxIiBtYXJrZXItc3RhcnQ9IiIgbWFya2VyLW1pZD0iIiBtYXJrZXItZW5kPSIiIGQ9Ik0xNC4zNDU2MzM1MDY3NzQ5MDIsODUuMDcyMTU2OTk1NTM0OSBMMy4wODQ3ODgzMjI0NDg3MzA1LDUzLjI1MDMzMzg3NTQxNzcxICIgY2xhc3M9IiIgaWQ9InN2Z18xMSIvPjxwYXRoIGZpbGw9Im5vbmUiIGZpbGwtb3BhY2l0eT0iMSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utb3BhY2l0eT0iMSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSJub25lIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2UtbGluZWNhcD0iYnV0dCIgc3Ryb2tlLWRhc2hvZmZzZXQ9IiIgZmlsbC1ydWxlPSJub256ZXJvIiBvcGFjaXR5PSIxIiBtYXJrZXItc3RhcnQ9IiIgbWFya2VyLW1pZD0iIiBtYXJrZXItZW5kPSIiIGQ9Ik01MC44NzY4MDc5MTkzODk0MiwxOS44MzIzMzA3MDM3MzUzNSBMMTYuMzAxMTcxMjk5Mzg0ODYyLDcuODc4NDA4OTA4ODQzOTk0ICIgaWQ9InN2Z184IiBjbGFzcz0iIi8+PHBhdGggZmlsbD0ibm9uZSIgZmlsbC1vcGFjaXR5PSIxIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS1vcGFjaXR5PSIxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS1saW5lY2FwPSJidXR0IiBzdHJva2UtZGFzaG9mZnNldD0iIiBmaWxsLXJ1bGU9Im5vbnplcm8iIG9wYWNpdHk9IjEiIG1hcmtlci1zdGFydD0iIiBtYXJrZXItbWlkPSIiIG1hcmtlci1lbmQ9IiIgZD0iTTM3LjA2NzI4MzYzMDM3MTA5NCw2NC41OTQyMzQ0NjY1NTI3MyBMMi40OTE2NDU4MTI5ODgyODEyLDUyLjY0MDMxNDEwMjE3Mjg1ICIgY2xhc3M9IiIgaWQ9InN2Z183Ii8+PHBhdGggZmlsbD0ibm9uZSIgZmlsbC1vcGFjaXR5PSIxIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS1vcGFjaXR5PSIxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS1saW5lY2FwPSJidXR0IiBzdHJva2UtZGFzaG9mZnNldD0iIiBmaWxsLXJ1bGU9Im5vbnplcm8iIG9wYWNpdHk9IjEiIG1hcmtlci1zdGFydD0iIiBtYXJrZXItbWlkPSIiIG1hcmtlci1lbmQ9IiIgZD0iTTQ3LjU0MzQ3MzI0MzcxMzM4LDk1LjU0NjYyMDM2ODk1NzUyIEwxMi45Njc4MzU0MjYzMzA1NjYsODMuNTkyNjk0MjgyNTMxNzQgIiBjbGFzcz0iIiBpZD0ic3ZnXzEwIi8+PHBhdGggZmlsbD0ibm9uZSIgZmlsbC1vcGFjaXR5PSIxIiBzdHJva2U9IiM5MTkxOTEiIHN0cm9rZS1vcGFjaXR5PSIxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS1saW5lY2FwPSJidXR0IiBzdHJva2UtZGFzaG9mZnNldD0iIiBmaWxsLXJ1bGU9Im5vbnplcm8iIG9wYWNpdHk9IjEiIG1hcmtlci1zdGFydD0iIiBtYXJrZXItbWlkPSIiIG1hcmtlci1lbmQ9IiIgZD0iTTY5LjI2MjI1NzU3MTExMzg4LDgxLjA3MTEyODg0NTIxNDg0IEw1Ni40MDU1Njg0OTE1MzI5MDQsNzIuNTAwMTM3MzI5MTAxNTYgIiBpZD0ic3ZnXzE3IiBjbGFzcz0iIi8+PHBhdGggZmlsbD0ibm9uZSIgZmlsbC1vcGFjaXR5PSIxIiBzdHJva2U9IiM5MTkxOTEiIHN0cm9rZS1vcGFjaXR5PSIxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS1saW5lY2FwPSJidXR0IiBzdHJva2UtZGFzaG9mZnNldD0iIiBmaWxsLXJ1bGU9Im5vbnplcm8iIG9wYWNpdHk9IjEiIG1hcmtlci1zdGFydD0iIiBtYXJrZXItbWlkPSIiIG1hcmtlci1lbmQ9IiIgZD0iTTAuNjcyNTM1MDAyMjMxNTk3OSw3OC4yMTM4MzEwNTYwNTY3MyBMOS4yNjE4NDU1ODg2ODQwODIsNzAuMTE4MDg4MTg0MzYzMzkgIiBpZD0ic3ZnXzE5IiBjbGFzcz0iIi8+PHBhdGggZmlsbD0ibm9uZSIgZmlsbC1vcGFjaXR5PSIxIiBzdHJva2U9IiM5MTkxOTEiIHN0cm9rZS1vcGFjaXR5PSIxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS1saW5lY2FwPSJidXR0IiBzdHJva2UtZGFzaG9mZnNldD0iIiBmaWxsLXJ1bGU9Im5vbnplcm8iIG9wYWNpdHk9IjEiIG1hcmtlci1zdGFydD0iIiBtYXJrZXItbWlkPSIiIG1hcmtlci1lbmQ9IiIgZD0iTTM0LjAyMzgyMjc4NDQyMzgzLDEzLjkyODcwMzg5NDA5NTE3OSBMMzQuMDIzODIyNzg0NDIzODMsLTAuMzU2NzUzNzExNzMxMTE2MTQgIiBpZD0ic3ZnXzIxIiBjbGFzcz0iIi8+PC9nPjxkZWZzPjxmaWx0ZXIgaWQ9ImYxMTUiIGlua3NjYXBlOmxhYmVsPSJOb2lzZSBmaWxsIiB4bWxuczppbmtzY2FwZT0iaHR0cDovL3d3dy5pbmtzY2FwZS5vcmcvbmFtZXNwYWNlcy9pbmtzY2FwZSIgaW5rc2NhcGU6bWVudT0iQUJDcyIgaW5rc2NhcGU6bWVudS10b29sdGlwPSJCYXNpYyBub2lzZSBmaWxsIHRleHR1cmU7IGFkanVzdCBjb2xvciBpbiBGbG9vZCIgY29sb3ItaW50ZXJwb2xhdGlvbi1maWx0ZXJzPSJzUkdCIj4KICAgICAgICAgICAgPGZlVHVyYnVsZW5jZSBudW1PY3RhdmVzPSI1IiBiYXNlRnJlcXVlbmN5PSIuMDIiIHR5cGU9ImZyYWN0YWxOb2lzZSIvPgogICAgICAgICAgICA8ZmVDb2xvck1hdHJpeCByZXN1bHQ9InJlc3VsdDAiIHZhbHVlcz0iMSAwIDAgMCAwIDAgMSAwIDAgMCAwIDAgMSAwIDAgMCAwIDAgMyAtMSAiLz4KICAgICAgICAgICAgPGZlRmxvb2QgZmxvb2Qtb3BhY2l0eT0iMSIgZmxvb2QtY29sb3I9IiM5MWM3YzMiIHJlc3VsdD0icmVzdWx0MSIvPgogICAgICAgICAgICA8ZmVCbGVuZCBpbjI9IlNvdXJjZUdyYXBoaWMiIG1vZGU9Im5vcm1hbCIgaW49InJlc3VsdDEiLz4KICAgICAgICAgICAgPGZlQ29tcG9zaXRlIG9wZXJhdG9yPSJvdXQiIGluMj0icmVzdWx0MCIvPgogICAgICAgICAgICA8ZmVDb21wb3NpdGUgb3BlcmF0b3I9ImF0b3AiIGluMj0iU291cmNlR3JhcGhpYyIvPgogICAgICAgIDwvZmlsdGVyPjwvZGVmcz48L3N2Zz4=");
                background-size: 25px;
                background-repeat: no-repeat;
                background-position-x: 00px;
                background-position-y: 00px;
            }
                            
            .crystalLabOption, .crystalLabOptionSelected {
                line-height : normal;
                font-size : 14px ; 
                display : flex;
                flex-direction : column;
                justify-content : center;
                text-align : center;
                border-right : 4px solid #FFFFFF;
                border-left : 4px solid #FFFFFF;
                color : #707070;
                font-weight: bold;            
                flex : 1;
                width : 100%;
                height : 45px;
                background-color: #FFFFFF;                
            }

            .crystalLabOption:hover, .crystalLabOptionSelected{
                background-color: #B6BEFD;            
            }
            
            .crystalLabOptions{
                display: flex;
                flex-direction: row;  
                width: 100%; 
                border: 1px solid #707070;
            }

            div.output_subarea{
                padding:0px
            }            
        </style>

        <div id="crystallab_''' + str(self.ref) + '''"></div>
        '''

        options_js = '''
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

     
                class CrystalLabComponent extends React.Component {
                    constructor(props) {
                        super(props)
                        this.state = { 
                            options:{
                                "option1":{
                                    "label" : "Crystal Viewer",
                                    "tool" : "crystalviewer",
                                    "icon" : "crystalLabCrystalLogo"
                                },
                                "option2":{
                                    "label" : "Bravais Viewer",
                                    "tool" : "bravaisviewer",
                                    "icon" : "crystalLabBravaisLogo"
                                },
               
                            }, 
                            selectedOption:"option1",
                        } 
                    }    

                    activateOption( option ){
                        CrystalLab_''' + str(self.ref) + '''['exposedActivateTool'](this.state.options[option].tool)
                        this.setState({
                            selectedOption:option,
                        })
                    }



                    render(){
                        var children = Array()    
                        let self = this
                        for (let option in this.state.options) {
                            var options_instance = this.state.options[option]
                            if (option != this.state.selectedOption){
                                children.push(React.createElement("div", {key:Util.create_UUID(), className:"crystalLabOption " + options_instance.icon, onClick:function(e){self.activateOption(option)}},options_instance.label))
                            } else {
                                children.push(React.createElement("div", {key:Util.create_UUID(), className:"crystalLabOptionSelected " + options_instance.icon},options_instance.label))
                            }                
                        
                        }  

                        var options = React.createElement("div", {key:Util.create_UUID(), className:"crystalLabOptions"}, children)
                        var div = React.createElement("div", {key:Util.create_UUID(), className:"", style:{backgroundColor:'#EEEEEE', display:'flex',flexDirection: 'row',}}, options)

                        return div
                    }
                }

                ReactDOM.render(
                    React.createElement(CrystalLabComponent, {}),
                    document.getElementById("crystallab_''' + str(self.ref) + '''")
                );
            });
        '''        
       
        return options_view, options_js
        
        
    def exposedActivateTool(self, tool):        
        if (tool in self.tools):
            with self.output_cont:        
                clear_output()
                if (self.tools[tool] is None):
                    if (tool == "crystalviewer"):
                        self.tools[tool] = CrystalViewerSimplified(self.auth_data, modal=self.modal)
                    elif (tool == "bravaisviewer"):
                        self.tools[tool] = BravaisViewerSimplified(self.auth_data, modal=self.modal)
                    else : 
                        self.tools[tool] = None
                    self.current_tool = self.tools[tool]
                else:
                    display(self.tools[tool].window)
            
                 
    
    

class CrystalViewerSimplified (CrystalSimplified):
    def __init__(self, credentials, **kwargs):
        self.hashitem = None;
        self.crystal_component_output = Output(layout=Layout(width="100%", padding="0px"))
        self.parameters_component_output = Output(layout=Layout(height="100%", padding="0px"))
        self.content_component_output = Output(layout=Layout(flex='1', padding="0px", overflow="scroll"))        
        self.current_view = "textbook";        
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
        self.parameters_additional = [
            'Primitive_cell',
            'Crystal_structure',
            '1','2','3','4','5','6','7','8','9','10','11','12',
            'What_to_do'
        ]
        self.parameters_miller = CrystalViewerTool.parameters_miller
        self.hashtable = {}

        CrystalSimplified.__init__(self, credentials, **kwargs)      


    def buildCrystal(self):   
        crystal_component_view = '''
        <style>
        
        .CrystalViewerLogo{
            line-height : normal;
            width : 140px ;
            height : 140px; 
            font-size : 14px ; 
            display : flex;
            flex-direction : column;
            justify-content : center;
            text-align : center;
            border-right : 4px solid #FFFFFF;
            color : #707070;
            background-image: url("data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/Pgo8IURPQ1RZUEUgc3ZnIFBVQkxJQyAiLS8vVzNDLy9EVEQgU1ZHIDIwMDEwOTA0Ly9FTiIKICJodHRwOi8vd3d3LnczLm9yZy9UUi8yMDAxL1JFQy1TVkctMjAwMTA5MDQvRFREL3N2ZzEwLmR0ZCI+CjxzdmcgdmVyc2lvbj0iMS4wIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiB3aWR0aD0iNjkuMDAwMDAwcHQiIGhlaWdodD0iMTA2LjAwMDAwMHB0IiB2aWV3Qm94PSIwIDAgNjkuMDAwMDAwIDEwNi4wMDAwMDAiCiBwcmVzZXJ2ZUFzcGVjdFJhdGlvPSJ4TWlkWU1pZCBtZWV0Ij4KCjxnIHRyYW5zZm9ybT0idHJhbnNsYXRlKDAuMDAwMDAwLDEwNi4wMDAwMDApIHNjYWxlKDAuMTAwMDAwLC0wLjEwMDAwMCkiCmZpbGw9IiMwMDAwMDAiIHN0cm9rZT0ibm9uZSI+CjxwYXRoIGQ9Ik0yMDYgNzM4IGwtMTk3IC0yOTMgNTcgLTU0IGM1MiAtNDggNTggLTUxIDY3IC0zNSAzMCA1MyAyODcgNjQyIDI4Nwo2NTcgMCA5IC00IDE3IC04IDE3IC01IDAgLTk3IC0xMzIgLTIwNiAtMjkyeiIvPgo8cGF0aCBkPSJNNDUyIDEwMDAgYzQ2IC0xMzggMjE1IC01ODcgMjIwIC01ODQgMyAyIDkgMzggMTMgNzggbDcgNzQgLTExNyAyMTkKYy0xMTMgMjA5IC0xMzQgMjQ2IC0xMjMgMjEzeiIvPgo8cGF0aCBkPSJNNDQxIDYwMyBsLTEgLTM2MyAxMDQgODEgMTA1IDgxIC0xNCAzNiBjLTI0IDcwIC0xNzggNDg3IC0xODYgNTA3Ci00IDExIC04IC0xNDMgLTggLTM0MnoiLz4KPHBhdGggZD0iTTM3NCA4NDAgYy02MSAtMTI3IC0yMjQgLTQ5NiAtMjI0IC01MDggMCAtOSAyNTkgLTEwNiAyNjcgLTk5IDIgMiAyCjE1OSAxIDM0OCBsLTMgMzQ0IC00MSAtODV6Ii8+CjxwYXRoIGQ9Ik00NyAzMTMgYzE5IC01NCA0NSAtMTI1IDU3IC0xNTkgMTQgLTQyIDMzIC03MSA1OSAtOTMgMjAgLTE4IDM3IC0yOQozNyAtMjUgMCA1IC0xNiA2NyAtMzYgMTM5IC0zNSAxMjMgLTM5IDEzMyAtODggMTgzIC0yOCAyOCAtNTQgNTIgLTU4IDUyIC00IDAKOSAtNDQgMjkgLTk3eiIvPgo8cGF0aCBkPSJNNTQwIDI5NiBsLTEwNCAtODQgLTI3IC0xMDYgYy0xNSAtNTggLTI0IC0xMDYgLTIxIC0xMDYgMyAwIDM1IDE0CjcyIDMxIGw2NiAzMCA2MiAxNDMgYzc3IDE3OSA3NiAxNzYgNjYgMTc2IC01IC0xIC01NiAtMzkgLTExNCAtODR6Ii8+CjxwYXRoIGQ9Ik0xNTAgMjk0IGMwIC0xOSA3NSAtMjYxIDg0IC0yNzEgNiAtNiAzOCAtMTQgNzEgLTE4IGw2MCAtNiAyMyAxMDEKYzEzIDU2IDIxIDEwNCAxOSAxMDcgLTUgNSAtMjQ1IDkzIC0yNTMgOTMgLTIgMCAtNCAtMyAtNCAtNnoiLz4KPC9nPgo8L3N2Zz4K");
            background-size: 75px;
            background-repeat: no-repeat;
            background-position-x: 10px;
            background-position-y: 10px;
            padding-left: 70px;
            padding-top: 80px;
            font-weight: bold;
        }

                        
        .ComponentMaterialSelected, .ComponentMaterial{
            height: 35px;
            border-radius: 15px;
            border: 1px solid #707070;
            color: #707070;
            padding: 10px 20px 10px 20px;
            background-color: #FFF;
            font-size:15px;
        }

        .ComponentMaterialSpace{
            width:6px;
            padding:0px;
        }
        
        .ComponentMaterialSelected, .ComponentMaterial:hover{
            background-color:#B6BEFD;
        }

        .ComponentCrystalSelected, .ComponentCrystal{
            height: 60px;
            width: 60px;
            border-radius:60px;
            background-color:#FFFFFF;
            border:1px solid #707070;
        }

        .ComponentCrystalSpace{
            width:6px;
            padding:0px;
        }
        
        .ComponentCrystalSelected, .ComponentCrystal:hover{
            background-color:#B6BEFD;
        }

        .ComponentCrystals{
            display:flex;
            flex-direction:row;
            justify-content:flex-start;
            padding-top: 10px;       
            padding-bottom: 10px;
        }

        .ComponentMaterials{
            display:flex;
            flex-direction:row;
            justify-content:flex-start;
            padding-top: 10px;
            border-top: 1px solid #707070;            
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
                    

        .crystal1{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("crystal1.png") + ''';
        }

        .crystal2{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("crystal2.png") + ''';
        }

        .crystal3{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("crystal3.png") + ''';
        }

        .crystal4{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("crystal4.png") + ''';
        }

        .crystal5{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("crystal5.png") + ''';
        }

        .crystal6{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("crystal6.png") + ''';
        }

        .crystal7{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("crystal7.png") + ''';
        }

        .crystal8{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("crystal8.png") + ''';
        }

        .crystal9{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("crystal9.png") + ''';
        }

        .crystal10{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("crystal10.png") + ''';
        }

        .crystal11{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("crystal11.png") + ''';
        }

        .crystal12{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
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
                            "Rock Salt (Sodium Chloride)":{
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
                            //"Carbon meshes":{
                            //    "materials":["Graphene", "Carbon nanotube", "Bucky ball(C60)"],
                            //    "icon": "crystal8",
                            //    "default":"Graphene",
                            //    "value": "8",
                            //},
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
                    if (crystal == "Carbon meshes")
                        CrystalViewerSimplified_''' + str(self.ref) + '''['exposedSelectMaterial'](this.state.crystals[crystal].value, 1)
                    else
                        CrystalViewerSimplified_''' + str(self.ref) + '''['exposedSelectMaterial'](this.state.crystals[crystal].value, this.state.crystals[crystal].default)
                }

                selectMaterial(material){
                    material = material + ""
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
                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"materialsTitle"}, "Crystals"))
                    for (let crystal in this.state.crystals) {
                        var crystal_instance = this.state.crystals[crystal]
                        let cur_crystal = crystal
                        if (crystal != this.state.selectedCrystal){
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentCrystal " + crystal_instance.icon, style:style, onClick:function(e){self.selectCrystal(crystal)}, title:crystal}))
                        } else {
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentCrystalSelected " + crystal_instance.icon, style:style, onClick:function(e){self.showMaterials()}, title:crystal}))
                        }                
                        children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentCrystalSpace"}))
                    }  
                    var mat_children = Array()    
                    mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"materialsTitle"}, "Materials"))
                    
                    if (this.state.showMaterials){
                        var materials = this.state.crystals[this.state.selectedCrystal].materials
                        for (let index in materials) {
                            let material = materials[index]
                            var style = {
                                display: "flex",
                                alignItems: "center",
                                flexDirection: "row",
                                justifyContent: "center",
                            }
                            if (this.state.selectedCrystal == 'Carbon meshes'){
                                if ((index+1) != this.state.selectedMaterial){
                                    mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentMaterial", style:style, onClick:function(e){self.selectMaterial(parseInt(index)+1)}, title:material}, material))                                
                                } else {
                                    mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentMaterialSelected", style:style, title:material}, material))
                                }                
                            } else {
                                if (material != this.state.selectedMaterial){
                                    mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentMaterial", style:style, onClick:function(e){self.selectMaterial(material)}, title:material}, material))                                
                                } else {
                                    mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentMaterialSelected", style:style, title:material}, material))
                                }                
                            }
                            mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentMaterialSpace"}))
                        }            
                    }
                    var crystals = React.createElement("div", {key:Util.create_UUID(), className:"ComponentCrystals"}, children)
                    var materials = React.createElement("div", {key:Util.create_UUID(), className:"ComponentMaterials"}, mat_children)
                    var mat_container = React.createElement("div", {key:Util.create_UUID(), className:"", style:{flex:1}}, [crystals, materials])

                    var title = React.createElement("div", {key:Util.create_UUID(), className:"CrystalViewerLogo", style:{}}, "Crystal Viewer")

                    var div = React.createElement("div", {key:Util.create_UUID(), className:"", style:{backgroundColor:'#EEEEEE', display:'flex',flexDirection: 'row',}}, [title, mat_container])

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

    def buildParameters(self):    
        parameter_component_view = '''
        <style>
        .ComponentOptionSelected, .ComponentOption{
            height: 35px;
            width: 130px;
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
        
        .ComponentSubOptionSelected, .ComponentSubOption{
            height: 40px;
            width: 40px;
            border-radius:40px;
            background-color: #FFFFFF;
            border:1px solid #707070;  
            font-size: 15px;
            color : #707070;
        }

        .ComponentSubOptionSelected, .ComponentSubOption:hover{
            background-color: #B6BEFD;
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

        .ComponentOptions{
            display:flex;
            flex-direction:column;
            justify-content:flex-start;
        }

        .ComponentSubOptions{
            display:flex;
            flex-wrap: wrap;
            display: -webkit-flex;
            -webkit-flex-wrap: wrap;
            justify-content:space-between;
            width: 100%;
            padding: 5px;
        }
        
        .ComponentSlider{
            display:flex;
            justify-content:space-between;
            width: 100%;
            position: relative;
            flex-direction: row;            
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
        
        .ComponentSliderSpot{
            height: 26px;
            width: 26px;
            border-radius: 26px;
            position: absolute;
            border: 1px solid #707070;
            font-size: 11px;
            align-items: center;
            justify-content: center;
            display: flex;
            background-color: #FFFFFF;
            margin-left: -13px;
        }

        .ComponentSliderSpot:hover{
            background-color: #B6BEFD;        
        }
        
        .ComponentSliderBase{
            height: 20px;
            flex: 1;
            border-radius: 20px;
            border: 1px solid #707070;
            justify-content: space-between;
            display: flex;
            flex-direction: row;
            font-size: 11px;
            align-items: center;
            background-color: #B6BEFD;

        }
        
        .ComponentSliderLine{
            display: flex;
            flex-direction: row;
            width: 100%;
            padding: 3px 0px 0px 0px;        
        }
        
        .ComponentSliderCont{
            padding : 0px 15px 0px 15px;
            padding: 0px 15px 0px 15px;
            height: 50px;
            width: 130px;
            border-radius: 15px;
            background-color: #FFFFFF;
            border: 1px solid #707070;
            font-size: 15px;
            color: #707070;        
        }        
        
        .ComponentSliderTitle{
            text-align: center;
            color: #707070;        
        }
        
        .ComponentTheme{
            display: flex;
            flex-direction: row;
            justify-content: space-around;
            width: 130px;
            bottom: 10px;
            position: absolute;
        }

        .ComponentThemeDark, .ComponentThemeWhite{
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

        .ComponentThemeDark:hover{
            background-color: #555555;
        }
        
        .ComponentThemeWhite:hover{
            background-color: #EEEEEE;
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

            class ParametersSlider extends React.Component {
                constructor(props) {
                    super(props)
                    let self = this;
                    this.spot1 = React.createRef();         
                    this.base = React.createRef();  
                    this.cont = React.createRef();
                    this.spot = undefined
                }
                
                drop(event) {
                    var p = this.allowDrop(event)
                    if (this.props.onChange)
                        this.props.onChange(p)
                    this.spot = undefined
                    
                }   
                
                allowDrop(event) {
                    if (this.spot != undefined){        
                        var boundsmin = this.spot1.current.getBoundingClientRect();
                        var bounds = this.base.current.getBoundingClientRect();        
                        var min = (event.clientX - bounds.left) / (bounds.right - bounds.left);
                        if (min <0)
                            min = 0
                        if (min > 1)
                            min = 1
                        this.spot1.current.style.left = (min*100) + "%" 
                        return (min) + ""
                    }
                    return "";
                }     
                
                dragStart(event) {
                    this.spot = this.spot1
                }
                
                render(){
                    let self = this;                
                    var circ1  = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSliderSpot", style:{left:'50%'}, ref:self.spot1, onMouseDown:function(e){self.dragStart(e)} });
                    var base  = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSliderBase", ref:this.base});
                    var line  = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSliderLine"}, base);
                    var slider = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSlider", ref:self.cont, onMouseUp:function(e){self.drop(e)}, onMouseMove:function(e){self.allowDrop(e)}, onMouseOut:function(e){self.allowDrop(e)}},
                        [line, circ1]
                    );
                    var text = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSliderTitle"}, "Plane cut");
                    var cont = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSliderCont"}, [text,slider] );
                    return cont;
                    
                }
            }
       
            class ParametersComponent extends React.Component {
                constructor(props) {
                    super(props)
                    let self = this;
                    this.state = { 
                        parameters:{
                            "textbook":{
                                "children":{},
                                "alt": "Textbook basis",
                                "label" : "Textbook basis",
                                "action" : function(){ self.displayTextBook() },
                            },
                            "basis":{
                                "children":{},
                                "alt": "Minimal Basis",
                                "label" : "Minimal Basis",
                                "action" : function(){ self.displayBasis() },
                            },
                            
                            "unitcell":{
                                "children":{
                                },
                                "alt": "Repeated Basis",
                                "label" : "Repeated Basis",
                                "action" : function(){ self.displayUnitCell() },
                            },
                            "miller":{
                                "children":{
                                    "100":{
                                        "alt": "100",
                                        "label" : "Miller planes (100)",
                                        "center" : 0.5,
                                        "plane" : '[1,0,0]',
                                        "action" : function(){ self.displayPlane('0.5', '[1,0,0]') },
                                    },                        
                                    "010":{
                                        "alt": "010",
                                        "label" : "Miller planes (010)",
                                        "center" : 0.5,
                                        "plane" : '[0,1,0]',
                                        "action" : function(){ self.displayPlane('0.5', '[0,1,0]') },
                                    },                        
                                    "001":{
                                        "alt": "001",
                                        "label" : "Miller planes (001)",
                                        "center" : 0.5,
                                        "plane" : '[0,0,1]',
                                        "action" : function(){ self.displayPlane('0.5', '[0,0,1]') },
                                    },
                                    "011":{
                                        "alt": "011",
                                        "label" : "Miller planes (011)",
                                        "center" : 0.5,
                                        "plane" : '[1,1,1]',
                                        "action" : function(){ self.displayPlane('0.5', '[0,1,1]') },
                                    },
                                    "121":{
                                        "alt": "121",
                                        "label" : "Miller planes (121)",
                                        "center" : 0.5,
                                        "plane" : '[1,2,1]',
                                        "action" : function(){ self.displayPlane('0.5', '[1,2,1]') },
                                    },
                                    "111":{
                                        "alt": "111",
                                        "label" : "Miller planes (111)",
                                        "center" : 0.5,
                                        "plane" : '[1,1,1]',
                                        "action" : function(){ self.displayPlane('0.5', '[1,1,1]') },
                                    },
                                },
                                "label" : "Crystal and Miller planes",
                                "alt": "Crystal",
                                "action" : function(){ self.displayLattice() },
                            },
                        }, 
                        selectedParameter:"''' + self.current_view + '''",
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

                displayBasis(){
                    CrystalViewerSimplified_''' + str(self.ref) + '''["exposedDisplayBasis"]();
                }
                
                displayLattice(){
                    CrystalViewerSimplified_''' + str(self.ref) + '''["exposedDisplayLattice"]();
                }

                displayPlane(center, plane){
                    CrystalViewerSimplified_''' + str(self.ref) + '''["exposedUpdatePlane"](center, plane);
                }
                
                
                showPlanes(){
                    CrystalViewerSimplified_''' + str(self.ref) + '''["exposedShowPlanes"]();
                }
                
                
                selectParameter(parameter){
                    this.setState({
                        selectedParameter:parameter, 
                        selectedOption:undefined,
                    })
                }

                selectOption(option){
                    this.setState({
                        selectedOption:option,
                    })
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

                changeTheme( option ){
                    if (option == "dark")
                        CrystalViewerSimplified_''' + str(self.ref) + '''["exposedChangeTheme"]('plotly_dark');
                    else
                        CrystalViewerSimplified_''' + str(self.ref) + '''["exposedChangeTheme"]('plotly_white');
                }

                render(){
                    var children = Array()    
                    var style = {
                        //backgroundSize: "50px 50px",
                        //backgroundImage: "url(" + crystal_instance.icon + ")",
                        display: "flex",
                        alignItems: "center",
                        flexDirection: "row",
                        justifyContent: "center",
                    }       

                    var style2 = {
                        //backgroundSize: "50px 50px",
                        //backgroundImage: "url(" + crystal_instance.icon + ")",
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
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOption", style:style, onClick:function(e){self.callParameter(parameter)}, title:parameter_instance.label}, parameter_instance.alt))
                        } else {
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSelected", style:style, onClick:function(e){self.callParameter(parameter)}, title:parameter_instance.label}, parameter_instance.alt))
                        }   
                        children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))
                        
                        if (parameter == this.state.selectedParameter){
                            var mat_children = Array()    
                            var opts = this.state.parameters[this.state.selectedParameter].children
                            for (let option in opts) {
                                let parameter_instance = opts[option]
                                if (option != this.state.selectedOption){
                                    mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentSubOption", style:style, onClick:function(e){self.callOption(option)}, title:parameter_instance.label}, parameter_instance.alt))
                                } else {
                                    mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentSubOptionSelected", style:style, title:parameter_instance.label}, parameter_instance.alt))
                                }                                            
                            }    
                            if (mat_children.length > 0){
                                if (parameter == "miller"){
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOption", style:style2, onClick:function(e){self.displayOptions()}, title:"Customize parameters"}, "Configuration"))
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))                                    
                                    children.push(React.createElement("div", {key:Util.create_UUID()}, "Miller Planes"))
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentSubOptions"}, mat_children))
                                    if (opts[this.state.selectedOption]){
                                        let parameter_instance = opts[this.state.selectedOption]
                                        children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))                                    
                                        children.push(React.createElement(ParametersSlider, {key:Util.create_UUID(), onChange:function(value){ self.displayPlane(value, parameter_instance.plane)} }))                                
                                    }
                                }
                            } else {
                                if (parameter == "unitcell"){
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOption", style:style2, onClick:function(e){self.showPlanes()}, title:"Show Planes"}, "Show Planes"))
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))
                                }
                            }
                        }
                    }  

                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentTheme"}, [
                        React.createElement("div", {key:Util.create_UUID(), className:""}, "Theme"),
                        React.createElement("div", {key:Util.create_UUID(), className:"ComponentThemeWhite", onClick:function(e){self.changeTheme("white")}}),
                        React.createElement("div", {key:Util.create_UUID(), className:"ComponentThemeDark", onClick:function(e){self.changeTheme("dark")}}),
                    ]))

                    var components = React.createElement("div", {key:Util.create_UUID(), className:"ComponentParameters"}, children)

                    var opt = React.createElement("div", {key:Util.create_UUID(), className:"", style:{display:"flex", flexDirection:"row", backgroundColor:'#EEEEEE', justifyContent:'flex-start', height:'700px', width:'140px', borderRight:'4px solid #FFF'}}, [components])
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
                interface_js += "    console.log('Executing Command: ' + command);\n"
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
        elif (self.current_view == "basis"):
            self.exposedDisplayBasis()
        elif (self.current_view == "lattice"):
            self.exposedDisplayLattice()
            if (self.normal != None):
                self.updatePlane(self.center, self.plane)
                
    def displayFrame(self):
        crystal_component_view, crystal_component_js = self.buildCrystal()
        parameter_component_view, parameter_component_js = self.buildParameters()
        
        with self.crystal_component_output:
            display(IHTML(crystal_component_view))
            display(Javascript(crystal_component_js)) 
    
        with self.parameters_component_output:
            display(IHTML(parameter_component_view))
            display(Javascript(parameter_component_js)) 
              
    def displayWindow(self):   
        self.displayFrame()
        display(IHTML(self.buildInterfaceJS()))
        with self.window:
            clear_output()
            #display(self.options_cont)
            display(VBox([                
                self.crystal_component_output,
                HBox([
                    self.parameters_component_output,
                    self.content_component_output
                ], layout=Layout(flex='1', height="100%"))
            ], layout=Layout(flexDirection="row", width="100%", height="700px")))

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
            
    def displayOptions(self):
        container_structure = VBox(layout=Layout(width='100%', height='100%'))
        children_structure = []
        for p in self.parameters_structure :
            if p in self.options:            
                children_structure.append(self.options[p])
            else:
                children_structure.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))

                               
        self.options['Crystal_structure'].dd.observe(lambda b, this=self : this.showMaterial(int(b['new'])), 'value')
        self.options['8'].dd.observe(lambda b, this=self : this.showMaterial(int(self.options['Crystal_structure'].value)), 'value')


        self.options['Draw_miller_plane'].value = "yes"
        self.options['Draw_plane_1'].value = "yes"
        self.options['Miller_index_1_1'].value = 1
        self.options['Miller_index_1_2'].value = 0
        self.options['Miller_index_1_3'].value = 0
        self.options['Draw_plane_2'].value = "yes"
        self.options['Miller_index_2_1'].value = 0
        self.options['Miller_index_2_2'].value = 1
        self.options['Miller_index_2_3'].value = 0
        self.options['Draw_plane_3'].value = "yes"
        self.options['Miller_index_3_1'].value = 0
        self.options['Miller_index_3_2'].value = 0
        self.options['Miller_index_3_3'].value = 1

        self.default_options = {}
        for ii in self.options.keys():
            self.default_options[ii] = self.options[ii].value
        
        container_structure.children = children_structure
        container_miller = self.displayMillerOptions()
        self.showMaterial(1)
        self.options_cont.children = [container_structure]
        self.getCache()
        self.refreshView()

    def getCache(self):
        parameters = self.getCurrentParameters( { "Primitive_cell" : "no" } )
        hashstr =  json.dumps(parameters, sort_keys=True).encode()        
        hashitem = hashlib.sha1(hashstr).hexdigest()
        if self.hashitem != hashitem:
            xml = self.loadCache(parameters, hashitem)
            results = xml.find('output')
            strings = self.getDrawings(results.findall('string'))  
            self.info = strings.get("latt_info", None)
            
            drawings = self.getDrawings(results.findall('drawing'))            

            self.unitcell = drawings.get("structure1", None)
            self.lattice = drawings.get("structure2", None)
            self.textbook = drawings.get("structure0", None)

            polys = self.getPolygons(self.lattice);
            vbasis = []
            for points in polys:
                p1 = nparray(points[0])
                p2 = nparray(points[1])
                p3 = nparray(points[2])
                v1 = p2 - p1
                v2 = p2 - p3
                cp = npcross(v1, v2)
                cp = npceil(cp / (cp**2).sum()**0.5)
                vbasis.append(cp)
                if len(vbasis) == 3:
                    break;
            self.unitvectors = None
            if len(vbasis) == 3:  
                self.unitvectors = vbasis
            parameters = self.getCurrentParameters( { "Primitive_cell" : "yes", 'Nx': '3', 'Ny':'3', 'Nz':'3' } )
            hashstr =  json.dumps(parameters, sort_keys=True).encode()        
            hashitem = hashlib.sha1(hashstr).hexdigest()
            xml = self.loadCache(parameters, hashitem)
            results = xml.find('output')
            drawings = self.getDrawings(results.findall('drawing'))  
            self.basis = drawings.get("structure1", None)
                
        with self.content_component_output:
            clear_output()  
        self.hashitem = hashitem
            
    def exposedDisplayOptions(self):
        self.normal = None        
        self.getCache()
        self.current_view = "options"
        with self.content_component_output:
            clear_output()
            display(self.options_cont)
     
    def exposedDisplayTextBook(self):
        self.normal = None        
        self.getCache()        
        self.current_view = "textbook"
        if self.textbook != None:
            self.plotDrawing(self.textbook,self.content_component_output)
    
    def exposedDisplayUnitCell(self):
        self.normal = None        
        self.getCache()        
        self.current_view = "unitcell"
        if self.unitcell != None:
            self.plotDrawing(self.unitcell,self.content_component_output)

    def exposedDisplayBasis(self):
        self.normal = None        
        self.getCache()        
        self.current_view = "basis"
        if self.basis != None:
            self.plotDrawing(self.basis,self.content_component_output)
            
    def exposedDisplayLattice(self):
        self.getCache()        
        self.current_view = "lattice"
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
            
            
    def loadCache(self, parameters, hashitem):
        xml = None
        if hashitem in self.hashtable:
            self.loggingMessage("LOADING CACHE ...." + hashitem, self.content_component_output)
            with open(self.hashtable[hashitem],'rt' ) as f:
                xml = f.read()
        else:
            if os.path.isfile(hashitem + ".xml"):
                self.loggingMessage("REBUILD CACHE ...." + hashitem, self.content_component_output)            
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
                    print ("Calculating new results ("+  hashitem +") id [" + session_id + "]")
                    status = self.session.checkStatus(session_id) 
                    loading = True
                    while loading == True:
                        if 'success' in status and status['success'] and 'finished' in status and status['finished'] and status['run_file'] != "":
                            loading = False
                        else:    
                            print ("waiting results from nanohub [" + session_id + "]")
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

    def getCurrentParameters( self, default_list ):
        parameters = {}
        
        for ii in self.options.keys():
            if (ii !="Crystal_structure" and ii != self.options["Crystal_structure"].value):
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
    

  
        
class BravaisViewerSimplified (CrystalSimplified):
    def __init__(self, credentials, **kwargs):
        self.hashitem = None;
        self.current_view = "textbook";
        self.crystal_component_output = Output(layout=Layout(width="100%", padding="0px"))
        self.parameters_component_output = Output(layout=Layout(height="100%", padding="0px"))
        self.content_component_output = Output(layout=Layout(flex='1', padding="0px", overflow="scroll"))        
        self.parameters_structure = [
            '21','22','23','24','25','26','27',
            'a',
            'b',
            'c',
            'Alpha',
            'Beta',
            'Gamma',
            'Nx',
            'Ny',
            'Nz',

        ]
        self.parameters_additional = [
        'What_to_do',
        '_Structure', 
        'Crystal_system',
        ]
        self.parameters_miller = CrystalViewerTool.parameters_miller
        self.hashtable = {}

        CrystalSimplified.__init__(self, credentials, **kwargs)      


    def buildCrystal(self):   
        crystal_component_view = '''
        <style>
        
        .BravaisViewerLogo{
            line-height : normal;
            width : 140px ;
            height : 140px; 
            font-size : 14px ; 
            display : flex;
            flex-direction : column;
            justify-content : center;
            text-align : center;
            border-right : 4px solid #FFFFFF;
            color : #707070;
            background-image: url("data:image/svg+xml;base64,PHN2ZyB2ZXJzaW9uPSIxLjAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgd2lkdGg9IjY5IiBoZWlnaHQ9IjEwNiIgcHJlc2VydmVBc3BlY3RSYXRpbz0ieE1pZFlNaWQgbWVldCIgc3R5bGU9IiI+PHJlY3QgaWQ9ImJhY2tncm91bmRyZWN0IiB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiB4PSIwIiB5PSIwIiBmaWxsPSJub25lIiBzdHJva2U9Im5vbmUiLz4KCgo8ZyBjbGFzcz0iY3VycmVudExheWVyIiBzdHlsZT0iIj48dGl0bGU+TGF5ZXIgMTwvdGl0bGU+PGcgdHJhbnNmb3JtPSJ0cmFuc2xhdGUoMCwgMTA2KSBzY2FsZSgwLjEsIC0wLjEpIiBmaWxsPSIjMDAwMDAwIiBzdHJva2U9Im5vbmUiIGlkPSJzdmdfMSIgY2xhc3M9IiI+CjxwYXRoIGQ9Ik04NS4wMDcwMTYxODE5NDU4LDc1Mi44NjYzMzMwMDc4MTIzIGwtNjEuNzIxNDAxMjE0NTk5NjEsLTIyMy41NjA4MjE1MzMyMDMxMiBsNjAuNDA4MTc2NDIyMTE5MTQsLTE0OC42NDQxNDk3ODAyNzM0NCBjMzIuODMwNTI4MjU5Mjc3MzQ0LC04MC44NjI0MjY3NTc4MTI1IDY0LjM0NzgzOTM1NTQ2ODc1LC0xNTIuMjExNjI0MTQ1NTA3OCA2OS42MDA3MzA4OTU5OTYxLC0xNTYuOTY4MjQ2NDU5OTYwOTQgYzExLjgxODk5MTY2MTA3MTc3NywtMTAuNzAyMzgwMTgwMzU4ODg3IDMxNS4xNzMwOTU3MDMxMjUsLTEwNC42NDU0ODQ5MjQzMTY0IDMzNy40OTc4NjM3Njk1MzEyNSwtMTA0LjY0NTQ4NDkyNDMxNjQgYzE1Ljc1ODY1NDU5NDQyMTM4NywwIDEyNC43NTYwMTk1OTIyODUxNiwzNzIuMjA0OTg2NTcyMjY1NiAxMjMuNDQyODAyNDI5MTk5MjIsNDIzLjMzODU2MjAxMTcxODc1IGMwLDE5LjAyNjQ1MzAxODE4ODQ3NyAtMjQuOTUxMjAyMzkyNTc4MTI1LDk4LjY5OTcyOTkxOTQzMzYgLTU1LjE1NTI5MjUxMDk4NjMzLDE3NS45OTQ2ODk5NDE0MDYyNSBsLTU1LjE1NTI5MjUxMDk4NjMzLDE0MS41MDkyNDY4MjYxNzE4OCBsLTE2Mi44Mzk0NDcwMjE0ODQzOCw1OC4yNjg1MTI3MjU4MzAwOCBjLTkwLjYxMjI1ODkxMTEzMjgxLDMwLjkxNzk4NzgyMzQ4NjMyOCAtMTY5LjQwNTUzMjgzNjkxNDA2LDU3LjA3OTM2MDk2MTkxNDA2IC0xNzguNTk4MDgzNDk2MDkzNzUsNTcuMDc5MzYwOTYxOTE0MDYgYy03Ljg3OTMyNzI5NzIxMDY5MywwIC00Mi4wMjMwNzg5MTg0NTcwMywtOTguNjk5NzI5OTE5NDMzNiAtNzcuNDgwMDQ5MTMzMzAwNzgsLTIyMi4zNzE2NzM1ODM5ODQzOCB6IiBpZD0ic3ZnXzIiLz4KPC9nPjxwYXRoIGZpbGw9Im5vbmUiIGZpbGwtb3BhY2l0eT0iMSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utb3BhY2l0eT0iMSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSJub25lIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2UtbGluZWNhcD0iYnV0dCIgc3Ryb2tlLWRhc2hvZmZzZXQ9IiIgZmlsbC1ydWxlPSJub256ZXJvIiBvcGFjaXR5PSIxIiBtYXJrZXItc3RhcnQ9IiIgbWFya2VyLW1pZD0iIiBtYXJrZXItZW5kPSIiIGQ9Ik0zNi45OTAzOTYwMTIwNjY0MSw2NS40ODkxMzUxNDI2OTIyNSBMNTAuNTM2MjU1ODA3NDE1NzMsMjAuMDE0NTMxNTE0NDYyMzA1ICIgaWQ9InN2Z180IiBjbGFzcz0iIiBmaWx0ZXI9IiIvPjxwYXRoIGZpbGw9Im5vbmUiIGZpbGwtb3BhY2l0eT0iMSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utb3BhY2l0eT0iMSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSJub25lIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2UtbGluZWNhcD0iYnV0dCIgc3Ryb2tlLWRhc2hvZmZzZXQ9IiIgZmlsbC1ydWxlPSJub256ZXJvIiBvcGFjaXR5PSIxIiBtYXJrZXItc3RhcnQ9IiIgbWFya2VyLW1pZD0iIiBtYXJrZXItZW5kPSIiIGQ9Ik0yLjQ3MTU4NDA0MzUyMTk0MzQsNTMuMjQ0NDQyOTIyNjgzNDUgTDE1Ljc3NDMxNTk2Mjk2NTM3NSw4LjU4NjA0MjI3MDYwNzMyMiAiIGNsYXNzPSIiIGZpbHRlcj0iIiBpZD0ic3ZnXzUiLz48cGF0aCBmaWxsPSJub25lIiBmaWxsLW9wYWNpdHk9IjEiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLW9wYWNpdHk9IjEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWRhc2hhcnJheT0ibm9uZSIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLWxpbmVjYXA9ImJ1dHQiIHN0cm9rZS1kYXNob2Zmc2V0PSIiIGZpbGwtcnVsZT0ibm9uemVybyIgb3BhY2l0eT0iMSIgbWFya2VyLXN0YXJ0PSIiIG1hcmtlci1taWQ9IiIgbWFya2VyLWVuZD0iIiBkPSJNNDkuMzcxMjM2MzY3NzcwNTEsOTQuODQyOTQzMjE0MjE2NTggTDYyLjQ0MDkyMzI5ODMwOTgyNiw1MC45NjY5MjA5NTk4MzE0NCAiIGNsYXNzPSIiIGZpbHRlcj0iIiBpZD0ic3ZnXzMiLz48cGF0aCBmaWxsPSJub25lIiBmaWxsLW9wYWNpdHk9IjEiIHN0cm9rZT0iI2ZmZmZmZiIgc3Ryb2tlLW9wYWNpdHk9IjEiIHN0cm9rZS13aWR0aD0iMiIgc3Ryb2tlLWRhc2hhcnJheT0ibm9uZSIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLWxpbmVjYXA9ImJ1dHQiIHN0cm9rZS1kYXNob2Zmc2V0PSIiIGZpbGwtcnVsZT0ibm9uemVybyIgb3BhY2l0eT0iMSIgbWFya2VyLXN0YXJ0PSIiIG1hcmtlci1taWQ9IiIgbWFya2VyLWVuZD0iIiBkPSJNNjEuOTY0NTMwOTQ0ODI0MjIsNTEuMjYyNjI4NjQ0NzA0ODIgTDUxLjY1NjA1MTYzNTc0MjE5LDE5LjQ0MDgwNzQzMTkzNjI2NCAiIGlkPSJzdmdfNiIgY2xhc3M9IiIvPjxwYXRoIGZpbGw9Im5vbmUiIGZpbGwtb3BhY2l0eT0iMSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utb3BhY2l0eT0iMSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSJub25lIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2UtbGluZWNhcD0iYnV0dCIgc3Ryb2tlLWRhc2hvZmZzZXQ9IiIgZmlsbC1ydWxlPSJub256ZXJvIiBvcGFjaXR5PSIxIiBtYXJrZXItc3RhcnQ9IiIgbWFya2VyLW1pZD0iIiBtYXJrZXItZW5kPSIiIGQ9Ik00OS4xMDc2NTQ1NzE1MzMyLDk0LjU4NTk2NzQ2NjI5MzM3IEwzNy4zNzA3NjE4NzEzMzc4OSw2NC42NzY5MTA2MzM3MzA1OSAiIGNsYXNzPSIiIGlkPSJzdmdfOSIvPjxwYXRoIGZpbGw9Im5vbmUiIGZpbGwtb3BhY2l0eT0iMSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utb3BhY2l0eT0iMSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSJub25lIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2UtbGluZWNhcD0iYnV0dCIgc3Ryb2tlLWRhc2hvZmZzZXQ9IiIgZmlsbC1ydWxlPSJub256ZXJvIiBvcGFjaXR5PSIxIiBtYXJrZXItc3RhcnQ9IiIgbWFya2VyLW1pZD0iIiBtYXJrZXItZW5kPSIiIGQ9Ik0xNC4zNDU2MzM1MDY3NzQ5MDIsODUuMDcyMTU2OTk1NTM0OSBMMy4wODQ3ODgzMjI0NDg3MzA1LDUzLjI1MDMzMzg3NTQxNzcxICIgY2xhc3M9IiIgaWQ9InN2Z18xMSIvPjxwYXRoIGZpbGw9Im5vbmUiIGZpbGwtb3BhY2l0eT0iMSIgc3Ryb2tlPSIjZmZmZmZmIiBzdHJva2Utb3BhY2l0eT0iMSIgc3Ryb2tlLXdpZHRoPSIyIiBzdHJva2UtZGFzaGFycmF5PSJub25lIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2UtbGluZWNhcD0iYnV0dCIgc3Ryb2tlLWRhc2hvZmZzZXQ9IiIgZmlsbC1ydWxlPSJub256ZXJvIiBvcGFjaXR5PSIxIiBtYXJrZXItc3RhcnQ9IiIgbWFya2VyLW1pZD0iIiBtYXJrZXItZW5kPSIiIGQ9Ik01MC44NzY4MDc5MTkzODk0MiwxOS44MzIzMzA3MDM3MzUzNSBMMTYuMzAxMTcxMjk5Mzg0ODYyLDcuODc4NDA4OTA4ODQzOTk0ICIgaWQ9InN2Z184IiBjbGFzcz0iIi8+PHBhdGggZmlsbD0ibm9uZSIgZmlsbC1vcGFjaXR5PSIxIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS1vcGFjaXR5PSIxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS1saW5lY2FwPSJidXR0IiBzdHJva2UtZGFzaG9mZnNldD0iIiBmaWxsLXJ1bGU9Im5vbnplcm8iIG9wYWNpdHk9IjEiIG1hcmtlci1zdGFydD0iIiBtYXJrZXItbWlkPSIiIG1hcmtlci1lbmQ9IiIgZD0iTTM3LjA2NzI4MzYzMDM3MTA5NCw2NC41OTQyMzQ0NjY1NTI3MyBMMi40OTE2NDU4MTI5ODgyODEyLDUyLjY0MDMxNDEwMjE3Mjg1ICIgY2xhc3M9IiIgaWQ9InN2Z183Ii8+PHBhdGggZmlsbD0ibm9uZSIgZmlsbC1vcGFjaXR5PSIxIiBzdHJva2U9IiNmZmZmZmYiIHN0cm9rZS1vcGFjaXR5PSIxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS1saW5lY2FwPSJidXR0IiBzdHJva2UtZGFzaG9mZnNldD0iIiBmaWxsLXJ1bGU9Im5vbnplcm8iIG9wYWNpdHk9IjEiIG1hcmtlci1zdGFydD0iIiBtYXJrZXItbWlkPSIiIG1hcmtlci1lbmQ9IiIgZD0iTTQ3LjU0MzQ3MzI0MzcxMzM4LDk1LjU0NjYyMDM2ODk1NzUyIEwxMi45Njc4MzU0MjYzMzA1NjYsODMuNTkyNjk0MjgyNTMxNzQgIiBjbGFzcz0iIiBpZD0ic3ZnXzEwIi8+PHBhdGggZmlsbD0ibm9uZSIgZmlsbC1vcGFjaXR5PSIxIiBzdHJva2U9IiM5MTkxOTEiIHN0cm9rZS1vcGFjaXR5PSIxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS1saW5lY2FwPSJidXR0IiBzdHJva2UtZGFzaG9mZnNldD0iIiBmaWxsLXJ1bGU9Im5vbnplcm8iIG9wYWNpdHk9IjEiIG1hcmtlci1zdGFydD0iIiBtYXJrZXItbWlkPSIiIG1hcmtlci1lbmQ9IiIgZD0iTTY5LjI2MjI1NzU3MTExMzg4LDgxLjA3MTEyODg0NTIxNDg0IEw1Ni40MDU1Njg0OTE1MzI5MDQsNzIuNTAwMTM3MzI5MTAxNTYgIiBpZD0ic3ZnXzE3IiBjbGFzcz0iIi8+PHBhdGggZmlsbD0ibm9uZSIgZmlsbC1vcGFjaXR5PSIxIiBzdHJva2U9IiM5MTkxOTEiIHN0cm9rZS1vcGFjaXR5PSIxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS1saW5lY2FwPSJidXR0IiBzdHJva2UtZGFzaG9mZnNldD0iIiBmaWxsLXJ1bGU9Im5vbnplcm8iIG9wYWNpdHk9IjEiIG1hcmtlci1zdGFydD0iIiBtYXJrZXItbWlkPSIiIG1hcmtlci1lbmQ9IiIgZD0iTTAuNjcyNTM1MDAyMjMxNTk3OSw3OC4yMTM4MzEwNTYwNTY3MyBMOS4yNjE4NDU1ODg2ODQwODIsNzAuMTE4MDg4MTg0MzYzMzkgIiBpZD0ic3ZnXzE5IiBjbGFzcz0iIi8+PHBhdGggZmlsbD0ibm9uZSIgZmlsbC1vcGFjaXR5PSIxIiBzdHJva2U9IiM5MTkxOTEiIHN0cm9rZS1vcGFjaXR5PSIxIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1kYXNoYXJyYXk9Im5vbmUiIHN0cm9rZS1saW5lam9pbj0icm91bmQiIHN0cm9rZS1saW5lY2FwPSJidXR0IiBzdHJva2UtZGFzaG9mZnNldD0iIiBmaWxsLXJ1bGU9Im5vbnplcm8iIG9wYWNpdHk9IjEiIG1hcmtlci1zdGFydD0iIiBtYXJrZXItbWlkPSIiIG1hcmtlci1lbmQ9IiIgZD0iTTM0LjAyMzgyMjc4NDQyMzgzLDEzLjkyODcwMzg5NDA5NTE3OSBMMzQuMDIzODIyNzg0NDIzODMsLTAuMzU2NzUzNzExNzMxMTE2MTQgIiBpZD0ic3ZnXzIxIiBjbGFzcz0iIi8+PC9nPjxkZWZzPjxmaWx0ZXIgaWQ9ImYxMTUiIGlua3NjYXBlOmxhYmVsPSJOb2lzZSBmaWxsIiB4bWxuczppbmtzY2FwZT0iaHR0cDovL3d3dy5pbmtzY2FwZS5vcmcvbmFtZXNwYWNlcy9pbmtzY2FwZSIgaW5rc2NhcGU6bWVudT0iQUJDcyIgaW5rc2NhcGU6bWVudS10b29sdGlwPSJCYXNpYyBub2lzZSBmaWxsIHRleHR1cmU7IGFkanVzdCBjb2xvciBpbiBGbG9vZCIgY29sb3ItaW50ZXJwb2xhdGlvbi1maWx0ZXJzPSJzUkdCIj4KICAgICAgICAgICAgPGZlVHVyYnVsZW5jZSBudW1PY3RhdmVzPSI1IiBiYXNlRnJlcXVlbmN5PSIuMDIiIHR5cGU9ImZyYWN0YWxOb2lzZSIvPgogICAgICAgICAgICA8ZmVDb2xvck1hdHJpeCByZXN1bHQ9InJlc3VsdDAiIHZhbHVlcz0iMSAwIDAgMCAwIDAgMSAwIDAgMCAwIDAgMSAwIDAgMCAwIDAgMyAtMSAiLz4KICAgICAgICAgICAgPGZlRmxvb2QgZmxvb2Qtb3BhY2l0eT0iMSIgZmxvb2QtY29sb3I9IiM5MWM3YzMiIHJlc3VsdD0icmVzdWx0MSIvPgogICAgICAgICAgICA8ZmVCbGVuZCBpbjI9IlNvdXJjZUdyYXBoaWMiIG1vZGU9Im5vcm1hbCIgaW49InJlc3VsdDEiLz4KICAgICAgICAgICAgPGZlQ29tcG9zaXRlIG9wZXJhdG9yPSJvdXQiIGluMj0icmVzdWx0MCIvPgogICAgICAgICAgICA8ZmVDb21wb3NpdGUgb3BlcmF0b3I9ImF0b3AiIGluMj0iU291cmNlR3JhcGhpYyIvPgogICAgICAgIDwvZmlsdGVyPjwvZGVmcz48L3N2Zz4=");
            background-size: 75px;
            background-repeat: no-repeat;
            background-position-x: 10px;
            background-position-y: 10px;
            padding-left: 70px;
            padding-top: 80px;
            font-weight: bold;
        }

                        
        .ComponentBravaisSelected, .ComponentBravais{
            height: 35px;
            border-radius: 15px;
            border: 1px solid #707070;
            color: #707070;
            padding: 10px 20px 10px 20px;
            background-color: #FFF;
            font-size:15px;
            line-height:15px;
        }

        .ComponentBravaisSpace{
            width:6px;
            padding:0px;
        }
        
        .ComponentBravaisSelected, .ComponentBravais:hover{
            background-color:#B6BEFD;
        }

        .ComponentCrystalSelected, .ComponentCrystal{
            height: 60px;
            width: 60px;
            border-radius:60px;
            background-color:#FFFFFF;
            border:1px solid #707070;
        }

        .ComponentCrystalSpace{
            width:6px;
            padding:0px;
        }
        
        .ComponentCrystalSelected, .ComponentCrystal:hover{
            background-color:#B6BEFD;
        }

        .ComponentCrystals{
            display:flex;
            flex-direction:row;
            justify-content:flex-start;
            padding-top: 10px;       
            padding-bottom: 10px;
        }

        .ComponentBravaisList{
            display:flex;
            flex-direction:row;
            justify-content:flex-start;
            padding-top: 10px;
            border-top: 1px solid #707070;            
        }
        
        .bravaisTitle{
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
                    

        .bravais1{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("bravais1.png") + ''';
        }

        .bravais2{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("bravais2.png") + ''';
        }

        .bravais3{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("bravais3.png") + ''';
        }

        .bravais4{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("bravais4.png") + ''';
        }

        .bravais5{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("bravais5.png") + ''';
        }

        .bravais6{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("bravais6.png") + ''';
        }

        .bravais7{
            background-size: 50px 50px;
            background-repeat:no-repeat;
            background-position: center center;
            background-image: ''' + self.buildIcon("bravais7.png") + ''';
        } 

        .ComponentTheme{
            display: flex;
            flex-direction: row;
            justify-content: space-around;
            width: 130px;
            bottom: 10px;
            position: absolute;
        }

        .ComponentThemeDark, .ComponentThemeWhite{
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

        .ComponentThemeDark:hover{
            background-color: #555555;
        }
        
        .ComponentThemeWhite:hover{
            background-color: #EEEEEE;
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
                            "Cubic":{
                                "bravais":["Simple cubic","Body-centered cubic","Face-centered cubic"],
                                "bravais_values":["simplecubic","bcc","fcc"],
                                "icon": "bravais1",
                                "default_value":"simplecubic",
                                "default":"Simple cubic",
                                "value": "25",
                            },
                            "Triclinic":{
                                "bravais":["Simple triclinic"],
                                "bravais_values":["triclinic"],
                                "icon": "bravais2",
                                "default_value":"triclinic",
                                "default":"Simple triclinic",
                                "value": "21",
                            },
                            "Monoclinic":{
                                "bravais":["Simple monoclinic", "Base-centered monoclinic"],
                                "bravais_values":["monoclinic", "monoclinicC"],
                                "icon": "bravais3",
                                "default_value":"monoclinic",
                                "default":"Simple monoclinic",
                                "value": "22",
                            },
                            "Orthorhombic":{
                                "bravais":["Simple Orthorhombic","Base-centered Orthorhombic", "Body-centered Orthorhombic","Face-centered Orthorhombic"],
                                "bravais_values":["orthorhombic","orthorhombicC", "orthorhombicI","orthorhombicF"],
                                "icon": "bravais4",
                                "default_value":"orthorhombic",
                                "default":"Simple Orthorhombic",
                                "value": "23",
                            },
                            "Tetragonal":{
                                "bravais":["Simple Tetragonal","Body-centered Tetragonal"],
                                "bravais_values":["tetragonal","tetragonalI"],
                                "icon": "bravais5",
                                "default_value":"tetragonal",
                                "default":"Simple Tetragonal",
                                "value": "24",
                            },
                            "Hexagonal":{
                                "bravais":["Simple hexagonal"],
                                "bravais_values":["hexagonal"],
                                "icon": "bravais6",
                                "default_value":"hexagonal",
                                "default":"Simple hexagonal",
                                "value": "26",
                            },
                            "Trigonal":{
                                "bravais":["Simple trigonal"],
                                "bravais_values":["rhombohedral"],
                                "icon": "bravais7",
                                "default_value":"rhombohedral",
                                "default":"Simple trigonal",
                                "value": "27",
                            },                
                        }, 
                        selectedCrystal:"Cubic",
                        selectedBravais:"Simple cubic",
                        showBravais: true,
                    } 
                }    

                selectCrystal(crystal){
                    this.setState({
                        selectedCrystal:crystal, 
                        selectedBravais:this.state.crystals[crystal].default,
                        showBravais: true
                    })
                    BravaisViewerSimplified_''' + str(self.ref) + '''['exposedSelectBravais'](this.state.crystals[crystal].value, this.state.crystals[crystal].default_value)
                }

                selectBravais(bravais, bravais_value){
                    console.log(bravais, bravais_value)
                    this.setState({
                        selectedBravais:bravais,
                    })
                    var sc = this.state.selectedCrystal
                    BravaisViewerSimplified_''' + str(self.ref) + '''['exposedSelectBravais'](this.state.crystals[sc].value, bravais_value)
                }

                showBravais( status ){
                    if (status == undefined)
                        status = !this.state.showBravais
                    this.setState({
                        showBravais: status
                    })
                }

                render(){
                    var children = Array()    
                    let self = this
                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"bravaisTitle"}, "Crystals"))
                    for (let crystal in this.state.crystals) {
                        var crystal_instance = this.state.crystals[crystal]
                        let cur_crystal = crystal
                        if (crystal != this.state.selectedCrystal){
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentCrystal " + crystal_instance.icon, style:style, onClick:function(e){self.selectCrystal(crystal)}, title:crystal}))
                        } else {
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentCrystalSelected " + crystal_instance.icon, style:style, onClick:function(e){self.showBravais()}, title:crystal}))
                        }                
                        children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentCrystalSpace"}))
                    }  
                    var mat_children = Array()    
                    mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"bravaisTitle"}, "Bravais"))
                    
                    if (this.state.showBravais){
                        var bravais_list = this.state.crystals[this.state.selectedCrystal].bravais
                        var bravais_values = this.state.crystals[this.state.selectedCrystal].bravais_values
                        for (let index in bravais_list) {
                            let bravais = bravais_list[index]
                            let bravais_value = bravais_values[index]
                            var style = {
                                display: "flex",
                                alignItems: "center",
                                flexDirection: "row",
                                justifyContent: "center",
                            }
                            if (bravais != this.state.selectedBravais){
                                mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentBravais", style:style, onClick:function(e){self.selectBravais(bravais, bravais_value)}, title:bravais}, bravais))
                            } else {
                                mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentBravaisSelected", style:style, title:bravais}, bravais))
                            }                
                            mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentBravaisSpace"}))
                        }            
                    }
                    var crystals = React.createElement("div", {key:Util.create_UUID(), className:"ComponentCrystals"}, children)
                    var bravais = React.createElement("div", {key:Util.create_UUID(), className:"ComponentBravaisList"}, mat_children)
                    var mat_container = React.createElement("div", {key:Util.create_UUID(), className:"", style:{flex:1}}, [crystals, bravais])

                    var title = React.createElement("div", {key:Util.create_UUID(), className:"BravaisViewerLogo", style:{}}, "Bravais Viewer")

                    var div = React.createElement("div", {key:Util.create_UUID(), className:"", style:{backgroundColor:'#EEEEEE', display:'flex',flexDirection: 'row',}}, [title, mat_container])

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

    def buildParameters(self):    
        parameter_component_view = '''
        <style>
        .ComponentOptionSelected, .ComponentOption{
            height: 35px;
            width: 130px;
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
        
        .ComponentSubOptionSelected, .ComponentSubOption{
            height: 40px;
            width: 40px;
            border-radius:40px;
            background-color: #FFFFFF;
            border:1px solid #707070;  
            font-size: 15px;
            color : #707070;
        }

        .ComponentSubOptionSelected, .ComponentSubOption:hover{
            background-color: #B6BEFD;
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

        .ComponentOptions{
            display:flex;
            flex-direction:column;
            justify-content:flex-start;
        }

        .ComponentSubOptions{
            display:flex;
            flex-wrap: wrap;
            display: -webkit-flex;
            -webkit-flex-wrap: wrap;
            justify-content:space-between;
            width: 100%;
            padding: 5px;
        }
        
        .ComponentSlider{
            display:flex;
            justify-content:space-between;
            width: 100%;
            position: relative;
            flex-direction: row;            
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
        
        .ComponentSliderSpot{
            height: 26px;
            width: 26px;
            border-radius: 26px;
            position: absolute;
            border: 1px solid #707070;
            font-size: 11px;
            align-items: center;
            justify-content: center;
            display: flex;
            background-color: #FFFFFF;
            margin-left: -13px;
        }

        .ComponentSliderSpot:hover{
            background-color: #B6BEFD;        
        }
        
        .ComponentSliderBase{
            height: 20px;
            flex: 1;
            border-radius: 20px;
            border: 1px solid #707070;
            justify-content: space-between;
            display: flex;
            flex-direction: row;
            font-size: 11px;
            align-items: center;
            background-color: #B6BEFD;

        }
        
        .ComponentSliderLine{
            display: flex;
            flex-direction: row;
            width: 100%;
            padding: 3px 0px 0px 0px;        
        }
        
        .ComponentSliderCont{
            padding : 0px 15px 0px 15px;
            padding: 0px 15px 0px 15px;
            height: 50px;
            width: 130px;
            border-radius: 15px;
            background-color: #FFFFFF;
            border: 1px solid #707070;
            font-size: 15px;
            color: #707070;        
        }        
        
        .ComponentSliderTitle{
            text-align: center;
            color: #707070;        
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

            class ParametersSlider extends React.Component {
                constructor(props) {
                    super(props)
                    let self = this;
                    this.spot1 = React.createRef();         
                    this.base = React.createRef();  
                    this.cont = React.createRef();
                    this.spot = undefined
                }
                
                drop(event) {
                    var p = this.allowDrop(event)
                    if (this.props.onChange)
                        this.props.onChange(p)
                    this.spot = undefined
                    
                }   
                
                allowDrop(event) {
                    if (this.spot != undefined){        
                        var boundsmin = this.spot1.current.getBoundingClientRect();
                        var bounds = this.base.current.getBoundingClientRect();        
                        var min = (event.clientX - bounds.left) / (bounds.right - bounds.left);
                        if (min <0)
                            min = 0
                        if (min > 1)
                            min = 1
                        this.spot1.current.style.left = (min*100) + "%" 
                        return (min) + ""
                    }
                    return "";
                }     
                
                dragStart(event) {
                    this.spot = this.spot1
                }
                
                render(){
                    let self = this;                
                    var circ1  = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSliderSpot", style:{left:'50%'}, ref:self.spot1, onMouseDown:function(e){self.dragStart(e)} });
                    var base  = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSliderBase", ref:this.base});
                    var line  = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSliderLine"}, base);
                    var slider = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSlider", ref:self.cont, onMouseUp:function(e){self.drop(e)}, onMouseMove:function(e){self.allowDrop(e)}, onMouseOut:function(e){self.allowDrop(e)}},
                        [line, circ1]
                    );
                    var text = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSliderTitle"}, "Plane cut");
                    var cont = React.createElement("div", {key:Util.create_UUID(), className:"ComponentSliderCont"}, [text,slider] );
                    return cont;
                    
                }
            }
       
            class ParametersComponent extends React.Component {
                constructor(props) {
                    super(props)
                    let self = this;
                    this.state = { 
                        parameters:{
                            "textbook":{
                                "children":{},
                                "alt": "Textbook Basis",
                                "label" : "Textbook Basis",
                                "action" : function(){ self.displayTextBook() },
                            },
                            "basis":{
                                "children":{},
                                "alt": "Basis",
                                "label" : "Basis",
                                "action" : function(){ self.displayBasis() },
                            },
                            "miller":{
                                "children":{
                                    "100":{
                                        "alt": "X",
                                        "label" : "X plane",
                                        "center" : 0.5,
                                        "plane" : '[1,0,0]',
                                        "action" : function(){ self.displayPlane('0.5', '[1,0,0]') },
                                    },                        
                                    "010":{
                                        "alt": "Y",
                                        "label" : "X plane",
                                        "center" : 0.5,
                                        "plane" : '[0,1,0]',
                                        "action" : function(){ self.displayPlane('0.5', '[0,1,0]') },
                                    },                        
                                    "001":{
                                        "alt": "Z",
                                        "label" : "X plane",
                                        "center" : 0.5,
                                        "plane" : '[0,0,1]',
                                        "action" : function(){ self.displayPlane('0.5', '[0,0,1]') },
                                    },
                                },
                                "label" : "Crystal",
                                "alt": "Crystal",
                                "action" : function(){ self.displayLattice() },
                            },
                        }, 
                        selectedParameter:"''' + self.current_view + '''",
                        selectedOption:undefined,
                    } 
                }    

                todo(){
                    BravaisViewerSimplified_''' + str(self.ref) + '''["exposedTest"]("TODO", "TODO");
                }

                displayOptions(){
                    BravaisViewerSimplified_''' + str(self.ref) + '''["exposedDisplayOptions"]();
                }

                displayTextBook(){
                    BravaisViewerSimplified_''' + str(self.ref) + '''["exposedDisplayTextBook"]();
                }

                displayBasis(){
                    BravaisViewerSimplified_''' + str(self.ref) + '''["exposedDisplayBasis"]();
                }
                
                displayLattice(){
                    BravaisViewerSimplified_''' + str(self.ref) + '''["exposedDisplayLattice"]();
                }

                displayPlane(center, plane){
                    BravaisViewerSimplified_''' + str(self.ref) + '''["exposedUpdatePlane"](center, plane);
                }
                
                changeTheme( option ){
                    if (option == "dark")
                        BravaisViewerSimplified_''' + str(self.ref) + '''["exposedChangeTheme"]('plotly_dark');
                    else
                        BravaisViewerSimplified_''' + str(self.ref) + '''["exposedChangeTheme"]('plotly_white');
                }

                
                selectParameter(parameter){
                    this.setState({
                        selectedParameter:parameter, 
                        selectedOption:undefined,
                    })
                }

                selectOption(option){
                    this.setState({
                        selectedOption:option,
                    })
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
                        //backgroundSize: "50px 50px",
                        //backgroundImage: "url(" + crystal_instance.icon + ")",
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
                            children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSelected", style:style, onClick:function(e){self.callParameter(parameter)}, title:parameter_instance.label}, parameter_instance.alt))
                        }   
                        children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))
                        
                        if (parameter == this.state.selectedParameter){
                            var mat_children = Array()    
                            var opts = this.state.parameters[this.state.selectedParameter].children
                            for (let option in opts) {
                                let parameter_instance = opts[option]
                                if (option != this.state.selectedOption){
                                    mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentSubOption", style:style, onClick:function(e){self.callOption(option)}, title:parameter_instance.label}, parameter_instance.alt))
                                } else {
                                    mat_children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentSubOptionSelected", style:style, title:parameter_instance.label}, parameter_instance.alt))
                                }                                            
                            }    
                            if (mat_children.length > 0){
                                if (parameter == "miller"){
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOption", style:style, onClick:function(e){self.displayOptions()}, title:"Customize parameters"}, "Configuration"))
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))                                    
                                    children.push(React.createElement("div", {key:Util.create_UUID()}, "Planes"))
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))
                                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentSubOptions"}, mat_children))
                                    if (opts[this.state.selectedOption]){
                                        let parameter_instance = opts[this.state.selectedOption]
                                        children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentOptionSpacer"}))                                    
                                        children.push(React.createElement(ParametersSlider, {key:Util.create_UUID(), onChange:function(value){ self.displayPlane(value, parameter_instance.plane)} }))                                
                                    }
                                }
                            }
                        }
                    }  

                    children.push(React.createElement("div", {key:Util.create_UUID(), className:"ComponentTheme"}, [
                        React.createElement("div", {key:Util.create_UUID(), className:""}, "Theme"),
                        React.createElement("div", {key:Util.create_UUID(), className:"ComponentThemeWhite", onClick:function(e){self.changeTheme("white")}}),
                        React.createElement("div", {key:Util.create_UUID(), className:"ComponentThemeDark", onClick:function(e){self.changeTheme("dark")}}),
                    ]))


                    var components = React.createElement("div", {key:Util.create_UUID(), className:"ComponentParameters"}, children)

                    var opt = React.createElement("div", {key:Util.create_UUID(), className:"", style:{display:"flex", flexDirection:"row", backgroundColor:'#EEEEEE', justifyContent:'flex-start', height:'700px', width:'140px', borderRight:'4px solid #FFF'}}, [components])
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

    def buildInterfaceJS(self):
        interface_js = "<script type='text/Javascript'>\n";
        refobj = "BravaisViewerSimplified_" + str(self.ref)
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
                interface_js += "    var command = 'from nanohubtools import BravaisViewerSimplified ; BravaisViewerSimplified.find_instance("+ str(self.ref) + ")." + method[0] +"(";
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
        
    def refreshView(self):
        if (self.current_view == "options"):
            self.exposedDisplayOptions()
        elif (self.current_view == "basis"):
            self.exposedDisplayBasis()
        elif (self.current_view == "textbook"):
            self.exposedDisplayTextBook()
        elif (self.current_view == "lattice"):
            self.exposedDisplayLattice()
            if (self.normal != None):
                self.updatePlane(self.center, self.plane)
                
    def displayFrame(self):
        crystal_component_view, crystal_component_js = self.buildCrystal()
        parameter_component_view, parameter_component_js = self.buildParameters()
        
        with self.crystal_component_output:
            display(IHTML(crystal_component_view))
            display(Javascript(crystal_component_js)) 
    
        with self.parameters_component_output:
            display(IHTML(parameter_component_view))
            display(Javascript(parameter_component_js)) 
              
    def displayWindow(self):   
        self.displayFrame()
        display(IHTML(self.buildInterfaceJS()))
        with self.window:
            clear_output()
            #display(self.options_cont)
            display(VBox([                
                self.crystal_component_output,
                HBox([
                    self.parameters_component_output,
                    self.content_component_output
                ], layout=Layout(flex='1', height="100%"))
            ], layout=Layout(flexDirection="row", width="100%", height="700px")))


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
                self.options[str(d)].value = self.parameters[str(d)]['default']
                

        for key, value in options.items():
            if (id in value):
                self.options[key].visible = True
                self.options[key].layout.display = None
            else:
                self.options[key].visible = False
                self.options[key].layout.display = 'none'
                self.options[str(d)].value = self.parameters[str(d)]['default']                
            
    def displayOptions(self):
        container_structure = VBox(layout=Layout(width='100%', height='100%'))
        children_structure = []
        for p in self.parameters_structure :
            if p in self.options:            
                children_structure.append(self.options[p])
            else:
                children_structure.append(Button(description=p.replace('_',''),layout=Layout(width='auto'),style=ButtonStyle(button_color='lightblue')))

                               
        self.options['Crystal_system'].dd.observe(lambda b, this=self : this.showBravais(int(b['new'])), 'value')

        self.options['Draw_miller_plane'].value = "no"
        self.options['What_to_do'].value = '3'
        self.options['Nx'].value = '3'
        self.options['Ny'].value = '3'
        self.options['Nz'].value = '3'
        self.default_options = {}
        for ii in self.options.keys():
            self.default_options[ii] = self.options[ii].value
        
        container_structure.children = children_structure
        container_miller = self.displayMillerOptions()
        self.showBravais(int(self.options['Crystal_system'].value))
        self.options_cont.children = [container_structure]
        self.getCache()
        self.refreshView()

            
    def exposedDisplayOptions(self):
        self.getCache()
        self.current_view = "options"
        with self.content_component_output:
            clear_output()
            display(self.options_cont)
     
    def exposedDisplayBasis(self):
        self.getCache()        
        self.current_view = "basis"
        if self.basis != None:
            self.plotDrawing(self.basis,self.content_component_output)

    def exposedDisplayTextBook(self):
        self.getCache()        
        self.current_view = "textbook"
        if self.textbook != None:
            self.plotDrawing(self.textbook,self.content_component_output)
            
    def exposedDisplayLattice(self):
        self.getCache()        
        self.current_view = "lattice"
        if self.lattice != None:
            self.plotDrawing(self.lattice,self.content_component_output)

    def exposedSelectCrystal(self, crystal):
        if (self.options["Crystal_system"].value != crystal):
            self.options["Crystal_system"].value = crystal;
            self.getCache()
            self.refreshView()

    def exposedSelectBravais(self, crystal, bravais):
        if (self.options["Crystal_system"].value != crystal or self.options[crystal].value != bravais):
            self.options["Crystal_system"].value = crystal;
            self.options[crystal].value = bravais;
            self.getCache()
            self.refreshView()   
            
            
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
                                print ("waiting results from nanohub [" + session_id + "]")
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

    def getCurrentParameters( self, default_list ):
        parameters = {}
        
        for ii in self.options.keys():
            if (ii !="Crystal_system" and ii != self.options["Crystal_system"].value):
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
    

    def getCache(self):
        parameters = self.getCurrentParameters( {  } )
        hashstr =  json.dumps(parameters, sort_keys=True).encode()        
        hashitem = hashlib.sha1(hashstr).hexdigest()
        if self.hashitem != hashitem:
            xml = self.loadCache(parameters, hashitem)
            results = xml.find('output')
            self.results = results
            drawings = self.getDrawings(results.findall('drawing'))            
            self.textbook = drawings.get("structure15", None)
            self.basis = drawings.get("structure16", None)
            self.lattice = drawings.get("structure10", None)
            self.unitvectors = [[1,0,0],[0,1,0],[0,0,1]]
            
            strings = self.getDrawings(results.findall('string'))
            self.info = drawings.get("latt_info", None)
                
        with self.content_component_output:
            clear_output()  
        self.hashitem = hashitem
