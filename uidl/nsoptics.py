from .teleport import *
from .rappture import *

class NsopticsBuilder():

  def NsopticsResults(Component, *args, **kwargs):
    results = kwargs.get("results", {});
    onClick = kwargs.get("onClick", []);
    onLoad = kwargs.get("onLoad", []);
    open_plot = {k:'secondary' for  k,v in results.items()}
    Component.addStateVariable("open_plot", {"type":"object", "defaultValue": open_plot})
    Grid = TeleportElement(MaterialContent(elementType="Grid"))
    Grid.content.attrs["container"] = True
    Grid.content.attrs["direction"] = "column"
    colors = {True:"primary",False:"secondary"}
    for k,v in results.items():
        open_elem = {k1:colors[k==k1] for k1,v1 in results.items()}
        Grid.addContent(MaterialBuilder.GridItem(content=MaterialBuilder.Button(
          title = v["title"], 
          color={
            "type": "dynamic",
            "content": {
             "referenceType": "state",
             "id": "open_plot." + k
            }    
          }, 
          onClickButton = onClick + [
            v["action"], { "type": "stateChange", "modifies": "open_plot","newState":open_elem },
          ] + onLoad
        )))
    return Grid

  def NsopticsSettings(tp, Component, settings, *args, **kwargs):
 
    FComponent = TeleportComponent("FormatCustomNumber", TeleportElement(TeleportContent(elementType="container")))
    FComponent.addPropVariable("formatter", {"type":"func", 'defaultValue' : '''(props)=>{
        return (value => {
            const { inputRef, ...other } = value;
            return React.createElement(Format,{...props,...other});
        });
    }'''
    })     
    FComponent.addPropVariable("property", {"type":"func", 'defaultValue' : '''(props)=>{
        return {
            'inputComponent': props.formatter(), 
            'endAdornment': props.suffix
        };
    }'''
    })  
    FComponent.addPropVariable("shrink", {"type":"object", 'defaultValue' : { 'shrink': True } })  
    TextField = TeleportElement(MaterialContent(elementType="TextField"))
    TextField.content.attrs['onBlur'] = {"type":"dynamic", "content":{"referenceType":"prop","id":"onBlur"}}
    TextField.content.attrs['InputProps'] = {"type":"dynamic", "content":{"referenceType":"prop","id":"property(this.props)"}}
    TextField.content.attrs['InputLabelProps'] = {"type":"dynamic", "content":{"referenceType":"prop","id":"shrink"}}
    TextField.content.attrs['variant'] = {"type":"dynamic", "content":{"referenceType":"prop","id":"variant"}}
    TextField.content.attrs['label'] = {"type":"dynamic", "content":{"referenceType":"prop","id":"label"}}
    TextField.content.attrs['fullWidth'] = {"type":"dynamic", "content":{"referenceType":"prop","id":"fullWidth"}}
    TextField.content.attrs['helperText'] = {"type":"dynamic", "content":{"referenceType":"prop","id":"helperText"}}
    TextField.content.attrs['label'] = {"type":"dynamic", "content":{"referenceType":"prop","id":"label"}}
    TextField.content.attrs['style'] = {"type":"dynamic", "content":{"referenceType":"prop","id":"style"}}
    TextField.content.attrs['value'] = {"type":"dynamic", "content":{"referenceType":"prop","id":"value"}}
    TextField.content.attrs['size'] = "small"
    TextField.content.attrs['type'] = 'number'
    FComponent.node.addContent(TextField)


    NComponent = TeleportComponent("NsopticsSettingsComponent", TeleportElement(TeleportContent(elementType="container")))
    NComponent.addPropVariable("onSubmit", {"type":"func", 'defaultValue' : "(e)=>{}"})    
    NComponent.addPropVariable("onClick", {"type":"func", 'defaultValue' : "(e)=>{}"})    
    NComponent.addPropVariable("onChange", {"type":"func", 'defaultValue' : "(e)=>{}"})    
    NComponent.addPropVariable("onLoad", {"type":"func", 'defaultValue' : "(e)=>{}"}) 
    NComponent.addPropVariable("onSuccess", {"type":"func", 'defaultValue' : "(e)=>{}"}) 
    NComponent.addPropVariable("onError", {"type":"func", 'defaultValue' : "(e)=>{}"}) 
    NComponent.addPropVariable("onStatusChange", {"type":"func", 'defaultValue' : "(e)=>{ console.log (e.target.value)}"}) 

    parameters = {}
    params = {}
    for k, v in settings.items():
        if "type" in v:
            if v["type"] in ["Select", "Number"]:
                value = {
                  "type": "dynamic",
                  "content": {
                    "referenceType": "prop",
                    "id": "parameters." + k
                  }    
                }
                if v["type"] == "Select":
                    param = FormHelper.Select( 
                      NComponent, 
                      v["label"], 
                      v["description"], 
                      k, 
                      value, 
                      v["options"],
                      onChange =  {
                        "type": "propCall2",
                        "calls": "onChange",
                        "args": ["{'id':'" + k + "', 'value':e.target.value}"]
                      }
                    )
                elif v["type"] == "Number":
                    param = FormHelper.Number( 
                      NComponent,
                      v["label"], 
                      v["description"], 
                      k, 
                      value, 
                      v["units"], 
                      onChange =  {
                        "type": "propCall2",
                        "calls": "onChange",
                        "args": ["{'id':'" + k + "', 'value':e.target.value}"]
                      }      
                    )
                params[k] = param
                parameters[k] = v["default_value"]
                
    Tabs = TeleportElement(TeleportContent(elementType="container"))
    for k, v in params.items():
        param = v
        if "restrictions" in settings[k]:
            for k2, r in settings[k]["restrictions"].items():
                operand = r
                operation = "=="
                if "operation" in r:
                    operation = r["operation"]
                elif "operand" in r:
                    operand = r["operand"]
                param = FormHelper.ConditionalGroup(NComponent, [param], k2, [{'operation' : operation, "operand" : operand}])                
        Tabs.addContent(param)
        
    runSimulation = RapptureBuilder.onSimulate(
      tp,
      NComponent, 
      toolname="nsoptics", 
      url=kwargs.get("url", None), 
    )

    Grid = TeleportElement(MaterialContent(elementType="Grid"))
    Grid.content.attrs["container"] = True
    Grid.content.attrs["direction"] = "column"
    Grid.addContent(MaterialBuilder.GridItem(content=MaterialBuilder.Button(title = "Simulate", onClickButton=runSimulation)))
    Tabs.addContent(Grid)
    NComponent.node.addContent(Tabs)
    NComponent.addPropVariable("parameters", {"type":"object", 'defaultValue' : parameters})    
    Component.addStateVariable("parameters", {"type":"object", 'defaultValue' : parameters})
    NsopticsSettings = TeleportElement(TeleportContent(elementType="NsopticsSettingsComponent"))
    NsopticsSettings.content.attrs['parameters'] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "parameters"
      }    
    }
    tp.components["NsopticsSettingsComponent"] = NComponent
    tp.components["FormatCustomNumber"] = FComponent
    return NsopticsSettings

