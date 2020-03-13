from .teleport import *
from .rappture import *
from .material import *

class FormHelper():  
  def Number(component, label, description, state, value=0, suffix="",*args, **kwargs):
    if (state not in component.stateDefinitions):
      component.addStateVariable(state, {"type":"number", "defaultValue": value})
    number = TeleportElement(TeleportContent(elementType="FormatCustomNumber"))
    variant = kwargs.get("variant", "outlined")
    number.content.attrs["variant"] = variant
    number.content.attrs["label"] = label
    number.content.attrs["fullWidth"] = True
    number.content.attrs["helperText"] = description
    number.content.attrs["suffix"] = suffix
    if (kwargs.get("decimalScale", None) is not None):
        number.content.attrs["decimalscale"] = kwargs.get("decimalScale", 0)
    number.content.style = { 'margin': '10px 0px 10px 0px'}
    number.content.events["blur"] = []
    
    if kwargs.get("onChange", None) is not None:
        number.content.events["blur"].append(kwargs.get("onChange", None))
    number.content.events["blur"].append({
      "type": "stateChange",
      "modifies": state,
      "newState": "$e.target.value"
    })
    number.content.attrs["value"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": state
      }  
    }
    return number

  def IntSlider(component, label, description, state, value=0, suffix="",*args, **kwargs):
    if (state not in component.stateDefinitions):
      component.addStateVariable(state, {"type":"number", "defaultValue": value})
    
    FormControl = TeleportElement(MaterialContent(elementType="FormControl"))
    variant = kwargs.get("variant", "outlined")
    FormControl.content.attrs["variant"] = variant  
    FormControl.content.style = {
        "border":"1px solid rgba(0, 0, 0, 0.23)", 
        "borderRadius":"4px", 
        "flexDirection": "row", 
        "paddingLeft" : "30px"
    }
    slider = TeleportElement(MaterialContent(elementType="Slider"))
    InputLabel = TeleportElement(MaterialContent(elementType="InputLabel"))
    InputLabel.content.attrs["htmlFor"]="component-filled"
    InputLabel.content.attrs["shrink"] = True
    
    InputLabel.content.style = { "background":"white", "padding":"0px 2px"}    
    InputLabelText = TeleportStatic(content=label)
    FormHelperText = TeleportElement(MaterialContent(elementType="FormHelperText"))
    FormHelperText.addContent(TeleportStatic(content=description))

    slider.content.events["change"] = []
    slider.content.events["change"].append({
      "type": "stateChange",
      "modifies": state,
      "newState": "$arguments[1]"
    })
    if kwargs.get("onChange", None) is not None:
        slider.content.events["change"].append(kwargs.get("onChange", None))

    slider.content.attrs["value"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": state
      }  
    }    
    slider.content.attrs["defaultValue"] = value
    #slider.content.attrs["valueLabelDisplay"] = kwargs.get("valueLabelDisplay", "on")
    slider.content.attrs["step"] = kwargs.get("step", 2)
    slider.content.attrs["min"] = kwargs.get("min", 0)
    slider.content.attrs["max"] = kwargs.get("max", 100)
    if (kwargs.get("marks", True)):
      min_v = slider.content.attrs["min"]
      max_v = slider.content.attrs["max"]
      step_v = slider.content.attrs["step"]
      slider.content.attrs["marks"] = [
          {
            'value': int(i),
            'label': str(int(i)),
          } for i in range(min_v, max_v+1, step_v)
    ];    
    InputLabel.addContent(InputLabelText)
    FormControl.addContent(InputLabel)
    FormControl.addContent(slider)
    FormControl.addContent(FormHelperText)
    return FormControl

  def Switch(component, label, description, state, value=False,*args, **kwargs):
    if (state not in component.stateDefinitions):  
      component.addStateVariable(state, {"type":"boolean", "defaultValue": value})
    FormControl = TeleportElement(MaterialContent(elementType="FormControl"))
    variant = kwargs.get("variant", "outlined")
    FormControl.content.attrs["variant"] = variant  
    FormControl.content.style = {
        "border":"1px solid rgba(0, 0, 0, 0.23)", 
        "borderRadius":"4px", 
        "flexDirection": "row", 
        "width" : "100%"
    }
    switch = TeleportElement(MaterialContent(elementType="Switch"))
    InputLabel = TeleportElement(MaterialContent(elementType="InputLabel"))
    InputLabel.content.attrs["htmlFor"]="component-filled"
    InputLabel.content.attrs["shrink"] = True
    
    InputLabel.content.style = { "background":"white", "padding":"0px 2px"}    
    InputLabelText = TeleportStatic(content=label)
    FormHelperText = TeleportElement(MaterialContent(elementType="FormHelperText"))
    FormHelperText.addContent(TeleportStatic(content=description))

    switch.content.events["change"] = []
    if kwargs.get("onChange", None) is not None:
        switch.content.events["change"].append(kwargs.get("onChange", None))
    switch.content.events["change"].append({
      "type": "stateChange",
      "modifies": state,
      "newState": "$e.target.checked"
    })
    switch.content.attrs["checked"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": state
      }  
    }
    InputLabel.addContent(InputLabelText)
    FormControl.addContent(InputLabel)
    FormControl.addContent(switch)
    FormControl.addContent(FormHelperText)
    return FormControl

  def IntSwitch(component, label, description, state, value, options,*args, **kwargs):
    if (state not in component.stateDefinitions):  
      component.addStateVariable(state, {"type":"number", "defaultValue": value})
    if len(options) != 2:
        raise Exception("exactly 2 options are required")
    k = [int(vv) for vv in options.keys()]
    v = [str(vv) for vv in options.values()]
    IntSwitch = TeleportElement(TeleportContent(elementType="IntSwitch"))
    IntSwitch.content.attrs["options"]=v
    IntSwitch.content.attrs["ids"]=k
    IntSwitch.content.attrs["label"]=label
    IntSwitch.content.attrs["description"]=description
    IntSwitch.content.attrs["default_value"]=value    
    IntSwitch.content.events["change"] = []
    IntSwitch.content.events["change"].append ({
        "type": "stateChange",
        "modifies": state,
        "newState": "$e.target.value"
    })
    if kwargs.get("onChange", None) is not None:
        IntSwitch.content.events["change"].append(kwargs.get("onChange", None))
    return IntSwitch

  def Header(label,*args, **kwargs):
    Typography = TeleportElement(MaterialContent(elementType="Typography"))
    variant = kwargs.get("variant", "h6")    
    Typography.content.attrs["variant"] = variant
    TypographyText = TeleportStatic(content=label)
    Divider = TeleportElement(MaterialContent(elementType="Divider"))
    Typography.addContent(TypographyText)
    Typography.addContent(Divider)
    return Typography
    
  def Select(component, label, description, state, value, options,*args, **kwargs):
    if (state not in component.stateDefinitions):  
      component.addStateVariable(state, {"type":"string", "defaultValue": value})
    select = TeleportElement(MaterialContent(elementType="TextField"))
    variant = kwargs.get("variant", "outlined")
    select.content.attrs["variant"] = variant
    select.content.attrs["label"] = label
    select.content.attrs["select"] = True
    select.content.attrs["fullWidth"] = True
    select.content.attrs["helperText"] = description
    select.content.style = { 'margin': '10px 0px 10px 0px' }
    select.content.events["change"] = []
    if kwargs.get("onChange", None) is not None:
        select.content.events["change"].append(kwargs.get("onChange", None))
        
    select.content.events["change"].append({
      "type": "stateChange",
      "modifies": state,
      "newState": "$e.target.value"
    })

    select.content.attrs["value"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": state
      }  
    }
    for key,value in options.items():
      option = TeleportElement(MaterialContent(elementType="MenuItem"))
      option.content.attrs["key"] = key
      option.content.attrs["value"] = key
      option.addContent(TeleportStatic(content=value))
      select.addContent(option)

    return select

  def ButtonList(component, label, description, state, value, options,*args, **kwargs):
    if (state not in component.stateDefinitions):  
      component.addStateVariable(state, {"type":"string", "defaultValue": value})
    component.addStateVariable(state+"_options", {"type":"object", "defaultValue": [
        {'key':k, 'name':v['name']}  for k,v in options.items()
    ]})

    FormControl = TeleportElement(MaterialContent(elementType="FormControl"))
    variant = kwargs.get("variant", "outlined")
    FormControl.content.attrs["variant"] = variant  
    FormControl.content.style = {
        "border":"1px solid rgba(0, 0, 0, 0.23)", 
        "borderRadius":"4px", 
        "width" : "100%"
    }
    
    InputLabel = TeleportElement(MaterialContent(elementType="InputLabel"))
    InputLabel.content.attrs["htmlFor"]="component-filled"
    InputLabel.content.attrs["shrink"] = True
    
    InputLabel.content.style = { "background":"white", "padding":"0px 2px"}    
    InputLabelText = TeleportStatic(content=label)
    FormHelperText = TeleportElement(MaterialContent(elementType="FormHelperText"))
    FormHelperText.addContent(TeleportStatic(content=description))
    InputLabel.addContent(InputLabelText)    
    
    ButtonListMaterial = TeleportElement(TeleportContent(elementType="ButtonListMaterial"))
    ButtonListMaterial.content.attrs["default_value"] = value
    ButtonListMaterial.content.attrs["description"] = description
    ButtonListMaterial.content.attrs["options"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": state+"_options"
      }    
    }
    ButtonListMaterial.content.events["change"]=[{
      "type": "stateChange",
      "modifies": state,
      "newState": "$e.target.value"
    }]

    Paper = TeleportElement(MaterialContent(elementType="Paper"))
    Paper.content.style = {"width":"100%", 'margin': '10px 0px 10px 0px'}

    FormControl.addContent(InputLabel)
    FormControl.addContent(ButtonListMaterial)
    Paper.addContent(FormControl)
    Paper.addContent(FormHelperText)
    return Paper    

  def IconList(component, label, description, state, value, options,*args, **kwargs):
    if (state not in component.stateDefinitions):  
      component.addStateVariable(state, {"type":"string", "defaultValue": value})
    component.addStateVariable(state+"_options", {"type":"object", "defaultValue": [
        {'key':k, 'icon':v['icon'], 'name':v['name']} 
        for k,v in options.items()
    ]})

    FormControl = TeleportElement(MaterialContent(elementType="FormControl"))
    variant = kwargs.get("variant", "outlined")
    FormControl.content.attrs["variant"] = variant  
    FormControl.content.style = {
        "border":"1px solid rgba(0, 0, 0, 0.23)", 
        "borderRadius":"4px", 
        "width" : "100%"
    }
    
    InputLabel = TeleportElement(MaterialContent(elementType="InputLabel"))
    InputLabel.content.attrs["htmlFor"]="component-filled"
    InputLabel.content.attrs["shrink"] = True
    
    InputLabel.content.style = { "background":"white", "padding":"0px 2px"}    
    InputLabelText = TeleportStatic(content=label)
    FormHelperText = TeleportElement(MaterialContent(elementType="FormHelperText"))
    FormHelperText.addContent(TeleportStatic(content=description))
    InputLabel.addContent(InputLabelText)    
    
    IconListMaterial = TeleportElement(TeleportContent(elementType="IconListMaterial"))
    IconListMaterial.content.attrs["default_value"] = value
    IconListMaterial.content.attrs["description"] = description
    IconListMaterial.content.attrs["options"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": state+"_options"
      }    
    }
    IconListMaterial.content.events["change"]=[{
      "type": "stateChange",
      "modifies": state,
      "newState": "$e.target.value"
    }]

    Paper = TeleportElement(MaterialContent(elementType="Paper"))
    Paper.content.style = {"width":"100%", 'margin': '10px 0px 10px 0px'}

    FormControl.addContent(InputLabel)
    FormControl.addContent(IconListMaterial)
    Paper.addContent(FormControl)
    Paper.addContent(FormHelperText)
    return Paper    
    
    
  def String(component, label, description, state, value, *args, **kwargs):
    if (state not in component.stateDefinitions):  
      component.addStateVariable(state, {"type":"string", "defaultValue": value})
    string = TeleportElement(MaterialContent(elementType="TextField"))
    variant = kwargs.get("variant", "outlined")
    string.content.attrs["variant"] = variant
    string.content.attrs["label"] = label
    #string.content.attrs["select"] = True
    string.content.attrs["fullWidth"] = True
    string.content.attrs["helperText"] = description
    string.content.style = { 'margin': '10px 0px 10px 0px' }
    string.content.events["change"] = []
    if kwargs.get("onChange", None) is not None:
        string.content.events["change"].append(kwargs.get("onChange", None))
        
    string.content.events["change"].append({
      "type": "stateChange",
      "modifies": state,
      "newState": "$e.target.value"
    })

    string.content.attrs["value"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": state
      }  
    }
    return string

  def Group(elements, *args, **kwargs):
    group = TeleportElement(MaterialContent(elementType="Grid"))
    group.content.attrs["container"] = True
    group.content.attrs["direction"] = kwargs.get("layout", "row")
    if kwargs.get("label", None) != None:
        Typography = TeleportElement(MaterialContent(elementType="Typography"))
        Typography.content.attrs["variant"] = "body1"
        Typography.content.attrs["gutterBottom"] = True        
        Typography.content.style={'flex':1, 'textAlign':'center', 'padding':'10px'}
        TypographyText = TeleportStatic(content=kwargs.get("label", None))
        Typography.addContent(TypographyText)        
        group.addContent(Typography)                                
    
    style = kwargs.get("style", { 'margin': '5px' } )
    group.content.style = style    
    for element in elements:
      group.addContent(element)
    return group

  def Tabs(component, children, state, *args, **kwargs):
    if (state not in component.stateDefinitions):
      component.addStateVariable(state, {"type":"integer", "defaultValue": kwargs.get("default_value", 0)})
  
    main_container = TeleportElement(MaterialContent(elementType="Paper")) 
    bar = TeleportElement(MaterialContent(elementType="AppBar"))
    bar.content.attrs["position"] = "static"
    bar.content.attrs["color"] = kwargs.get("barColor", "primary")
  
    tabs = TeleportElement(MaterialContent(elementType="Tabs"))
    tabs.content.attrs["indicatorColor"]=kwargs.get("indicatorColor", "primary")
    tabs.content.attrs["textColor"]=kwargs.get("textColor", "primary")
    tabs.content.attrs["variant"]="scrollable"
    tabs.content.attrs["scrollButtons"]="auto"    
    tabs.content.attrs["value"] = {
      "type": "dynamic", "content": {
        "referenceType": "state", "id": state
      }    
    }
    
    i = 0
    bar.addContent(tabs)    
    main_container.addContent(bar)    
    for key,value in children.items():
      container = TeleportConditional(MaterialContent(elementType="Paper")) 
    
      container.reference = {
        "type": "dynamic",
        "content": {
          "referenceType": "state",
          "id": state
        }    
      }
      container.value = i
      if isinstance(value, list): 
        container.addContent(FormHelper.Group(value))
      elif isinstance(value, TeleportNode): 
        container.addContent(value)
      else:
        raise Exception("invalid type of component")

      tab = TeleportElement(MaterialContent(elementType="Tab"))
      tab.content.attrs["label"] = key
      tab.content.events["click"] = [
        {
          "type": "stateChange",
          "modifies": state,
          "newState": i
        },
      ]  
      i = i+1
      main_container.addContent(container)
      tabs.addContent(tab)
      
    return main_container

  def ConditionalGroup(component, elements, state, conditions, *args, **kwargs):
    lstate = state.split('.')
    if component.stateDefinitions.get(lstate[0], None) is None:    
      raise Exception("Not existing state ('" + state + "')") 
    Paper = MaterialContent(elementType="Paper")
    Paper.style = {"width" : '100%'}
    container = TeleportConditional(Paper)
    container.reference = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": state
      }    
    }    
    container.conditions = conditions
    for element in elements:     
      if isinstance(element, list): 
        container.addContent(FormHelper.Group(element))
      elif isinstance(element, TeleportNode): 
        container.addContent(element)
    return container


class AppBuilder():

  def Results(Component, *args, **kwargs):
    results = kwargs.get("results", {});
    onClick = kwargs.get("onClick", []);
    onLoad = kwargs.get("onLoad", []);
    open_plot = {k:'secondary' for  k,v in results.items()}
    Component.addStateVariable("open_plot", {"type":"object", "defaultValue": open_plot})
    Grid = TeleportElement(MaterialContent(elementType="Grid"))
    Grid.content.style = { 'width' : '100%' }
    Grid.content.attrs["container"] = True
    Grid.content.attrs["direction"] = "column"
    colors = {True:"primary",False:"secondary"}
    for k,v in results.items():
        open_elem = {k1:colors[k==k1] for k1,v1 in results.items()}
        v_action = []
        if isinstance(v["action"], dict):
            v_action.append(v["action"])
        elif isinstance(v["action"], list):
            for va in v["action"]:
                v_action.append(va)
        v_action.append({ "type": "stateChange", "modifies": "open_plot","newState":open_elem })
        Grid.addContent(MaterialBuilder.GridItem(content=MaterialBuilder.Button(
          title = v["title"], 
          color={
            "type": "dynamic",
            "content": {
             "referenceType": "state",
             "id": "open_plot." + k
            }    
          }, 
          onClickButton = onClick + v_action + onLoad
        )))
    return Grid

  def createGroups(Component, layout, fields, *args, **kwargs):
    Group = None
    
    if "type" in layout and layout["type"] == "tab" :
        Group = TeleportElement(MaterialContent(elementType="Paper"))
        children = {}
        if "children" in layout:
            for i, child in enumerate (layout["children"]):
                children[child["label"]] = AppBuilder.createGroups(Component, child, fields)
        Group.addContent(FormHelper.Tabs(Component, children, "testing"))
    elif "type" in layout and layout["type"] == "group" :
        Group = TeleportElement(MaterialContent(elementType="Paper"))
        Group.content.style={"border": "1px solid #f1f1f1"}
        children = []
        if "children" in layout:
            for i, child in enumerate (layout["children"]):
                children.append(AppBuilder.createGroups(Component, child, fields))
        direction = "row"
        if "layout" in layout and layout["layout"] == "horizontal":
            direction = "column"         
        Group.addContent(FormHelper.Group(children, "testing", direction=direction, label=layout["label"]))
    else:
        if layout["id"] in fields:
            Group = fields[layout["id"]]
        elif "_"+layout["id"] in fields:
            Group = fields["_"+layout["id"]]
        else:
            Group = TeleportElement(MaterialContent(elementType="Paper"))

    if "enable" in layout and layout["enable"] is not None:
        for r in layout["enable"]:
            operand = None
            operation = "=="
            value = None            
            if "operand" in r:
                operand = r["operand"]
            if "operator" in r:
                operation = r["operator"]
            if "value" in r:
                if isinstance(r["value"], str):
                    value = r["value"].strip("\"")
                else:
                    value = r["value"]
            if value is not None and operation is not None and operand is not None:
                if operation == "in":
                    listv = [{'operation' : "==", "operand" : v} for v in value.split(",")] 
                    Group = FormHelper.ConditionalGroup(Component, [Group], operand, listv)                    
                    Group.matchingCriteria = "one"
                else:
                    Group = FormHelper.ConditionalGroup(Component, [Group], operand, [{'operation' : operation, "operand" : value}])
    return Group

  def Settings(tp, Component, settings, *args, **kwargs):
    layout=kwargs.get("layout", {
        'type': 'group',
        'id': '',
        'label': '',
        'layout': 'horizontal',
        'children': [{'id':id} for id, value in settings.items()]
    })


    MaterialComponents.FormatCustomNumber(tp)
    MaterialComponents.IconList(tp)
    MaterialComponents.IntSwitch(tp)    
    MaterialComponents.ButtonList(tp)    

    NComponent = TeleportComponent("NsopticsSettingsComponent", TeleportElement(MaterialContent(elementType="Paper")))
    NComponent.node.content.style = {"width":"100%"}
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
        if isinstance(k,str) == False or k.isnumeric():
            k = "_" + k
        if "type" in v:
            param = None
            value = {
              "type": "dynamic",
              "content": {
                "referenceType": "prop",
                "id": "parameters." + k
              }    
            }
            if v["type"] == "IconList":
                param = FormHelper.IconList( 
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
            if v["type"] == "ButtonList":
                param = FormHelper.ButtonList( 
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
            elif v["type"] == "Integer":
                param = FormHelper.Number( 
                  NComponent,
                  v["label"], 
                  v["description"], 
                  k, 
                  value, 
                  v["units"], 
                  decimalScale=0,
                  onChange =  {
                    "type": "propCall2",
                    "calls": "onChange",
                    "args": ["{'id':'" + k + "', 'value':e.target.value}"]
                  }
                )
                if "min" in v and "max" in v and v['min'] is not None and v['max'] is not None:
                    param.content.attrs["range"] = [v['min'], v['max']]

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
                if "min" in v and "max" in v and v['min'] is not None and v['max'] is not None:
                    param.content.attrs["range"] = [v['min'], v['max']]
            elif v["type"] == "String":
                print (v);
                param = FormHelper.String( 
                  NComponent,
                  v["label"], 
                  v["description"], 
                  k, 
                  value, 
                  onChange =  {
                    "type": "propCall2",
                    "calls": "onChange",
                    "args": ["{'id':'" + k + "', 'value':e.target.value}"]
                  }      
                )
            elif v["type"] == "Boolean":
                param = FormHelper.Switch( 
                  NComponent,
                  v["label"], 
                  v["description"], 
                  k, 
                  value, 
                  onChange =  {
                    "type": "propCall2",
                    "calls": "onChange",
                    "args": ["{'id':'" + k + "', 'value':e.target.checked}"]
                  }      
                )
            elif v["type"] == "IntSwitch":
                param = FormHelper.IntSwitch( 
                  NComponent,
                  v["label"],
                  v["description"],
                  k,
                  value,
                  v["options"],
                  onChange = {
                    "type": "propCall2",
                    "calls": "onChange",
                    "args": ["{'id':'" + k + "', 'value':e.target.checked}"]
                  }
                )
        if param is not None:
            params[k] = param
            parameters[k] = v["default_value"]
    Tabs = AppBuilder.createGroups(NComponent, layout, params)
        
    runSimulation = RapptureBuilder.onSimulate(
      tp,
      NComponent,
      toolname=kwargs.get("toolname", ""),
      url=kwargs.get("url", None),
    )

    Grid = TeleportElement(MaterialContent(elementType="Grid"))
    Grid.content.attrs["container"] = True
    Grid.content.attrs["direction"] = "column"
    Grid.addContent(
        MaterialBuilder.GridItem(content=MaterialBuilder.Button(
            title = "Simulate", 
            onClickButton=runSimulation, 
            color="inherit"
        )
    ))
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
    return NsopticsSettings


  def ColorSliders(tp, Component, *args, **kwargs):
    MaterialComponents.ColorSliders(tp)            
    sliders = kwargs.get("sliders", {})
    skeys = list(sliders.keys());
    svalues = list(sliders.values());
    Grid = TeleportElement(MaterialContent(elementType="Grid"))
    Grid.content.attrs["container"] = True
    Grid.content.attrs["direction"] = "column"
    
    if (len(skeys) > 0):
      Component.addStateVariable("planes", {"type":"array", "defaultValue": [{
          'visible':False, 
          'center':50,
          'color':s['color'],
          'label':s['label'],
          'plane':s['plane'],
          'use_miller': 'options' in s,
        } for s in svalues]
      })

      
      ColorSliders0 = TeleportElement(TeleportContent(elementType="ColorSliders"))
      ColorSliders0.content.attrs["colors"] = {
        "type": "dynamic",
        "content": {
          "referenceType": "state",
          "id": "planes"
        }    
      }
    
      ColorSliders0.content.events["change"] = [{
        "type": "stateChange",
        "modifies": "planes",
        "newState": "$e.target.value"
      }]
      Grid.addContent(MaterialBuilder.GridItem(content=ColorSliders0, style={'padding':'0px'}))

      for s,v in sliders.items():
        if 'options' in v:
            Component.addStateVariable(s, {"type":"object", "defaultValue":{
              'id':list(v['options'].keys())[0],
              'planes':v['options'],   
              'options':[{'key':k,'name':k} for k, v in v['options'].items()],
            }})
            ButtonListMaterial = TeleportElement(TeleportContent(elementType="ButtonListMaterial"))
            ButtonListMaterial.content.attrs["always_open"] = True
            ButtonListMaterial.content.attrs["hide_header"] = True
            ButtonListMaterial.content.attrs["default_value"] = {
              "type": "dynamic",
              "content": {
                "referenceType": "state",
                "id": s + ".id"
              }    
            }
            ButtonListMaterial.content.attrs["description"] = ""
            ButtonListMaterial.content.attrs["options"] = {
              "type": "dynamic",
              "content": {
                "referenceType": "state",
                "id": s + ".options"
              }    
            }
            ButtonListMaterial.content.events["change"]=[
              {
                "type": "stateChange",
                "modifies": s + ".id",
                "newState": "$e.target.value"
              },
              {
                "type": "stateChange",
                "modifies": "planes",
                "newState": "$self.state.planes.map((m,i)=>{if (i==3) m.plane=self.state."+ s +".planes[e.target.value]; return m;})"
              }
            ]
            Grid.addContent(MaterialBuilder.GridItem(content=ButtonListMaterial, style={'padding':'0px'}))

    return Grid