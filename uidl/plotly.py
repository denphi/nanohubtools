from .teleport import *
from .material import *
from .rappture import *

class PlotlyContent(TeleportContent):
  def buildElementType(self):   
    elementType = self.elementType
    return "" + elementType

    
class PlotlyBuilder():
  def BasePlotlyComponent(*args, **kwargs):
    
    PlotlyPlot = TeleportElement(PlotlyContent(elementType="Plot"))
    PlotlyPlot.content.attrs["data"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "prop",
        "id": "data"
      }    
    }
    PlotlyPlot.content.attrs["layout"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "prop",
        "id": "layout"
      }    
    }
    PlotlyPlot.content.attrs["frames"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "prop",
        "id": "frames"
      }    
    }
    PlotlyPlot.content.attrs["useResizeHandler"] = True
    PlotlyPlot.content.style = {
      "height": "100%",
      "width": "100%",
    }

    BasePlotlyComponent = TeleportComponent("BasePlotlyComponent", PlotlyPlot)
    BasePlotlyComponent.addPropVariable("data", {"type":"array", "defaultValue": [{'x': [], 'y': []}]})    
    BasePlotlyComponent.addPropVariable("layout", {"type":"object", "defaultValue": {}})
    BasePlotlyComponent.addPropVariable("frames", {"type":"array", "defaultValue": []})     
    BasePlotlyComponent.addPropVariable("config", {"type":"object", "defaultValue": {}})     

    return BasePlotlyComponent    
  
  def BasePlot(tp, Component,  *args, **kwargs):
    if ("BasePlotlyComponent" not in tp.components):
      tp.components["BasePlotlyComponent"] = PlotlyBuilder.BasePlotlyComponent()  
    Component.addStateVariable("data", {"type":"array", "defaultValue": [{'x': [], 'y': []}]})    
    Component.addStateVariable("layout", {"type":"object", "defaultValue": {}})
    Component.addStateVariable("frames", {"type":"array", "defaultValue": []})        
    Component.addStateVariable("config", {"type":"object", "defaultValue": {'displayModeBar': True, 'responsive': True}})        
        
        
    BasePlot = TeleportElement(TeleportContent(elementType="BasePlotlyComponent"))
    BasePlot.content.style = {
      "height": "inherit",
      "width": "inherit",
    }
    
    BasePlot.content.attrs["data"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "data"
      }    
    }
    BasePlot.content.attrs["layout"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "layout"
      }    
    }
    BasePlot.content.attrs["frames"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "frames"
      }      
    }
    
    BasePlot.content.attrs["config"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "config"
      }      
    }
    
    ContainerPlot = TeleportElement(MaterialContent(elementType="Paper")) 
    ContainerPlot.content.style = {
      "position": "fixed",
      "height": "calc(100% - 56px)",
      "width": "100%",
    }
    
    if kwargs.get("style_state", None) is not None:
      ContainerPlot.content.attrs["className"] = {
        "type": "dynamic",
        "content": {
          "referenceType": "state",
          "id": kwargs.get("style_state")
        }    
      }
    
    ContainerPlot.addContent(BasePlot)
    return ContainerPlot

  def MoleculeComponent(tp, *args, **kwargs):
    
    PlotlyPlot = TeleportElement(PlotlyContent(elementType="Plot"))
    PlotlyPlot.content.attrs["data"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "prop",
        "id": "setData(self)"
      }    
    }
    PlotlyPlot.content.attrs["layout"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "prop",
        "id": "setLayout(self)"
      }    
    }
    PlotlyPlot.content.attrs["useResizeHandler"] = True
    PlotlyPlot.content.style = {
      "height": "100%",
      "width": "100%",
    }

    PlotlyPlot.content.events["onUpdate"] = [{
    #  "type": "stateChange",
    #  "modifies": "scene",
    #  "newState": "$e.layout.scene"
      "type": "propCall2",
      "calls": "handleUpdate",
      "args": ['self', 'e.layout.scene']
    }]
    
    
    
    MoleculeComponent = TeleportComponent("MoleculeComponent", PlotlyPlot)
    MoleculeComponent.addPropVariable("onUpdate", {"type":"func", "defaultValue": "(e)=>{}"})            
    RapptureBuilder.exposedShowPlanes(tp, MoleculeComponent)
    eol = "\n"
    handleUpdate = ""
    handleUpdate += "(component, scene)=>{" + eol
    handleUpdate += "  if (JSON.stringify(scene) === JSON.stringify(component.state.scene))" + eol
    handleUpdate += "    return;" + eol
    handleUpdate += "  component.setState({'scene': scene});" + eol
    handleUpdate += "}" + eol
    MoleculeComponent.addPropVariable("handleUpdate", {"type":"func", "defaultValue": handleUpdate})        
    setData = ""
    setData += "(component)=>{" + eol
    setData += "  let c = component;" + eol
    setData += "  var data = [...c.props.data];" + eol
    setData += "  c.props.planes.forEach((p)=>{" + eol
    setData += "    if (p.visible){" + eol
    setData += "      let bo = c.props.boundary;" + eol
    setData += "      let ve = [[1,0,0],[0,1,0],[0,0,1]];" + eol
    setData += "      if (p.use_miller){" + eol
    setData += "        ve = c.props.vectors;" + eol
    setData += "      }" + eol
    setData += "      var exPlane = c.props.exposedShowPlanes(c,p.plane,ve,p.center/100,bo,p.color);" + eol
    setData += "      exPlane.data.forEach((d)=>{" + eol
    setData += "        data.push(d);" + eol
    setData += "      });" + eol
    setData += "    }" + eol
    setData += "  });" + eol
    setData += "  return data;" + eol
    setData += "}" + eol
    MoleculeComponent.addPropVariable("setData", {"type":"func", "defaultValue": setData})        
    eol = "\n"
    setLayout = ""
    setLayout += "(component)=>{" + eol
    setLayout += "  let c = component;" + eol
    setLayout += "  var layout = c.props.layout;" + eol
    setLayout += "  layout.scene = c.state.scene;" + eol
    setLayout += "  return layout;" + eol
    setLayout += "}" + eol
    MoleculeComponent.addPropVariable("setLayout", {"type":"func", "defaultValue": setLayout})        
    MoleculeComponent.addPropVariable("data", {"type":"array", "defaultValue": []})    
    MoleculeComponent.addPropVariable("layout", {"type":"object", "defaultValue": {}})
    MoleculeComponent.addPropVariable("boundary", {"type":"array", "defaultValue": [[0,0,0],[1,1,1]]})
    MoleculeComponent.addPropVariable("vectors", {"type":"array", "defaultValue": [[1,0,0],[0,1,0],[0,0,1]]})
    MoleculeComponent.addPropVariable("atoms", {"type":"array", "defaultValue": []})
    MoleculeComponent.addStateVariable("scene", {"type":"object", "defaultValue": {
        'aspectmode':'data',
        'camera' : {
            'center' : {'x':0,'y':0, 'z':0 },
            'eye' : {'x':1.25,'y':1.25,'z':1.25}, 
            'projection' : {
                'type' : 'persepective'
            },
            'up' : {'x':0,'y':0,'z':1},             
        },
    }})
    MoleculeComponent.addPropVariable("frames", {"type":"array", "defaultValue": []})     
    MoleculeComponent.addPropVariable("planes", {"type":"array", "defaultValue": []})
    MoleculeComponent.addPropVariable("miller", {"type":"array", "defaultValue": []})
    MoleculeComponent.addPropVariable("config", {"type":"object", "defaultValue": {}})     
    
    tp.addComponent("MoleculeComponent", MoleculeComponent);
    
    
    return "MoleculeComponent"   

  def Molecule(tp, Component,  *args, **kwargs):
    MoleculeComponent = PlotlyBuilder.MoleculeComponent(tp);
    Component.addStateVariable("data", {"type":"array", "defaultValue": []})    
    Component.addStateVariable("layout", {"type":"object", "defaultValue": {}})
    Component.addStateVariable("frames", {"type":"array", "defaultValue": []})        
    Component.addStateVariable("config", {"type":"object", "defaultValue": {'displayModeBar': True, 'responsive': True}})
    Component.addStateVariable("boundary", {"type":"array", "defaultValue": [[0,0,0],[1,1,1]]})
    Component.addStateVariable("vectors", {"type":"array", "defaultValue": [[1,0,0],[0,1,0],[0,0,1]]})
    Component.addStateVariable("atoms", {"type":"array", "defaultValue": []})
    
    ContainerPlot = TeleportElement(MaterialContent(elementType="Paper")) 
    ContainerPlot.content.style = {
      "position": "fixed",
      "height": "calc(100% - 56px)",
      "width": "100%",
    }
    BasePlot = TeleportElement(TeleportContent(elementType=MoleculeComponent))
    BasePlot.content.style = {
      "height": "inherit",
      "width": "inherit",
    }    
    BasePlot.content.attrs["data"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "data"
      }    
    }
    BasePlot.content.attrs["layout"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "layout"
      }    
    }
    BasePlot.content.attrs["frames"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "frames"
      }      
    }
    
    BasePlot.content.attrs["config"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "config"
      }      
    }
    
    BasePlot.content.attrs["planes"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "planes"
      }      
    }
    
    BasePlot.content.attrs["boundary"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "boundary"
      }      
    }
    
    BasePlot.content.attrs["vectors"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "vectors"
      }      
    }
    
    if kwargs.get("style_state", None) is not None:
      ContainerPlot.content.attrs["className"] = {
        "type": "dynamic",
        "content": {
          "referenceType": "state",
          "id": kwargs.get("style_state")
        }    
      }
    

    ContainerPlot.addContent(BasePlot)
    return ContainerPlot