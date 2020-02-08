from .teleport import *
class NsopticsBuilder():
  def Loader(*args, **kwargs):
    Loader = TeleportElement(MaterialContent(elementType="Dialog"))
    if (kwargs.get("open", None) is not None):
        Loader.content.attrs["open"] = kwargs.get("open", False)
    Loader.content.attrs["disableBackdropClick"] = True
    Loader.content.attrs["disableEscapeKeyDown"] = True
    Loader.content.attrs["fullWidth"] = True
    Loader.content.attrs["maxWidth"] = 'xs'
    loadercnt = TeleportElement(MaterialContent(elementType="DialogContent"))
    loadercnt.content.style = { "textAlign": "center", "overflow" : "hidden"}

    loadercir = TeleportElement(MaterialContent(elementType="CircularProgress"))
    loadercir.content.style = {"width": "100px", "height": "100px", "overflow": "none"}

    loadertext = TeleportElement(MaterialContent(elementType="DialogTitle"))
    loadertext.addContent(TeleportDynamic(content=kwargs.get("text", "Loading")))

    loadertext.content.style = {"textAlign": "center"}

    loadercnt.addContent(loadercir)
    Loader.addContent(loadercnt)
    Loader.addContent(loadertext)
    return Loader

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
        open_elem = {k:colors[k==k1] for  k1,v1 in results.items()}
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
        
    runSimulation = NsopticsBuilder.onSimulate(
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
    tp.components["NsopticsSettingsComponent"] = NComponent
    tp.components["FormatCustomNumber"] = FComponent
    return TeleportElement(TeleportContent(elementType="NsopticsSettingsComponent"))

  def onSimulate(tp, Component, *args, **kwargs):
    store_name="sessionStore";
    NanohubUtils.storageFactory(tp, store_name=store_name)
    eol = "\n"
    toolname = kwargs.get("toolname", "")
    url = kwargs.get("url", "")


    js = "(self)=>{" + eol
    js += "  " + store_name + ".removeItem('output_xml');" + eol
    js += "  var params = JSON.parse(" + store_name + ".getItem('nanohub_tool_schema'));" + eol
    js += "  var xmlDoc = JSON.parse(" + store_name + ".getItem('nanohub_tool_xml'));" + eol
    js += "  var state = self.state;" + eol
    js += "  self.props.onStatusChange({'target':{ 'value' : 'Parsing XML' } });" + eol
    js += "  if (window.DOMParser){" + eol
    js += "    parser = new DOMParser();" + eol
    js += "    xmlDoc = parser.parseFromString(xmlDoc, 'text/xml');" + eol
    js += "  } else {" + eol
    js += "    xmlDoc = new ActiveXObject('Microsoft.XMLDOM');" + eol
    js += "    xmlDoc.async = false;" + eol
    js += "    xmlDoc.loadXML(xmlDoc);" + eol
    js += "  }" + eol
    js += "  var elems = xmlDoc.getElementsByTagName('*');" + eol
    js += "  var discardtags = ['phase', 'group', 'option'];" + eol
    js += "  for (var i=0;i<elems.length;i++){" + eol
    js += "    var elem = elems[i];" + eol
    js += "    if (elem.tagName == 'structure'){" + eol
    js += "      var edefault = elem.querySelectorAll('default');" + eol
    js += "      if (edefault.length > 0){" + eol
    js += "        var params = edefault[0].querySelectorAll('parameters');" + eol
    js += "        if (params.length > 0){" + eol
    js += "          var current = xmlDoc.createElement('current');" + eol
    js += "          current.appendChild(params[0].cloneNode(true));" + eol
    js += "          elem.appendChild(current);" + eol
    js += "        }" + eol
    js += "      }" + eol
    js += "    }" + eol
    js += "  }" + eol;
    js += "  self.props.onStatusChange({'target':{ 'value' : 'Loading XML Default Parameters' } } );" + eol
    js += "  var elems = xmlDoc.getElementsByTagName('*');" + eol
    js += "  for (var i=0;i<elems.length;i++){" + eol
    js += "    var elem = elems[i];" + eol
    js += "    if (elem.hasAttribute('id')){" + eol
    js += "      var id = elem.getAttribute('id');" + eol
    js += "      if ((discardtags.findIndex((e)=> e == elem.tagName))<0){" + eol
    js += "        var current = elem.querySelectorAll('current');" + eol
    js += "        if (current.length > 0){" + eol
    js += "          var units='';" + eol
    js += "          var units_node = elem.querySelectorAll('units');" + eol
    js += "          if (units_node.length > 0){" + eol
    js += "            units=units_node[0].textContent;" + eol
    js += "          }" + eol
    js += "          var default_node = elem.querySelectorAll('default');" + eol
    js += "          if (default_node.length > 0){" + eol
    js += "            var defaultv = default_node[0].textContent;" + eol
    js += "            var current = elem.querySelectorAll('current');" + eol
    js += "            if (current.length > 0){" + eol
    js += "              elem.removeChild(current[0]);" + eol;
    js += "            }" + eol
    js += "            current = xmlDoc.createElement('current');" + eol
    js += "            if (units != '' && !defaultv.includes(units)){" + eol
    js += "              current.textContent = defaultv+units;" + eol
    js += "            } else {" + eol
    js += "              current.textContent = defaultv;" + eol
    js += "            }" + eol
    js += "            elem.appendChild(current);" + eol    
    js += "          }" + eol
    js += "        }" + eol
    js += "      }" + eol
    js += "    }" + eol
    js += "  }" + eol
    js += "  self.props.onStatusChange({'target':{ 'value' : 'Setting XML Parameters' } } );" + eol
    js += "  for (const id in state) {" + eol;
    js += "    let value = String(state[id]);" + eol;
    js += "    var elems = xmlDoc.getElementsByTagName('*');" + eol
    js += "    for (var i=0;i<elems.length;i++){" + eol;
    js += "      var elem = elems[i];" + eol
    js += "      if (elem.hasAttribute('id')){" + eol
    js += "        if ((discardtags.findIndex((e)=> e == elem.tagName))<0){" + eol
    js += "          var id_xml = elem.getAttribute('id');" + eol
    js += "          if (id == id_xml){" + eol
    js += "            var current = elem.querySelectorAll('current');" + eol
    js += "            if (current.length > 0){" + eol
    js += "              elem.removeChild(current[0]);" + eol
    js += "            }" + eol
    js += "            current = xmlDoc.createElement('current');" + eol
    js += "            var units='';" + eol
    js += "            var units_node = elem.querySelectorAll('units');" + eol
    js += "            if (units_node.length > 0){" + eol
    js += "              units=units_node[0].textContent;" + eol
    js += "            }" + eol
    js += "            if (units != '' && !value.includes(units)){" + eol
    js += "              current.textContent = String(value)+units;" + eol
    js += "            } else {" + eol
    js += "              current.textContent = String(value);" + eol
    js += "            } " + eol    
    js += "            elem.appendChild(current);" + eol    
    js += "          }" + eol
    js += "        }" + eol
    js += "      }" + eol
    js += "    }" + eol
    js += "  }" + eol
    js += "  self.props.onStatusChange({'target':{ 'value' : 'Building Rappture XML' } } );" + eol
    js += "  var driver_str  = '<?xml version=\"1.0\"?>\\n' + new XMLSerializer().serializeToString(xmlDoc.documentElement);" + eol
    js += "  var driver_json = {'app': '" + toolname + "', 'xml': driver_str}" + eol;
    js += "  var nanohub_token = " + store_name + ".getItem('nanohub_token');" + eol
    js += "  var header_token = {'Authorization': 'Bearer ' + nanohub_token}" + eol;
    js += "  var url = '" + url + "/run';";
    js += "  str = [];" + eol
    js += "  for(var p in driver_json){" + eol
    js += "    str.push(encodeURIComponent(p) + '=' + encodeURIComponent(driver_json[p]));" + eol
    js += "  }" + eol
    js += "  data =  str.join('&');" + eol
    js += "  var options = { 'handleAs' : 'json' , 'headers' : header_token, 'method' : 'POST', 'data' : data };" + eol
    js += "  self.props.onStatusChange({'target':{ 'value' : 'Submitting Simulation' } } );" + eol
    
    js += "  Axios.request(url, options)" + eol
    js += "  .then(function(response){" + eol
    js += "    var session = response.data.session;" + eol
    js += "    setTimeout(function(){ self.props.onCheckSession(self, session, true) },4000);" + eol
    js += "  }).catch(function(error){" + eol
    js += "    self.props.onError(self, error);" + eol      
    js += "  })" + eol
    js += "}" + eol
    
    Component.addPropVariable("onSimulate", {"type":"func", 'defaultValue' :js})    
    
    js = "(self, session_id, reload)=>{" + eol
    js += "  var session_json = {'session_num': session_id};" + eol;
    js += "  var nanohub_token = " + store_name + ".getItem('nanohub_token');" + eol
    js += "  var header_token = {'Authorization': 'Bearer ' + nanohub_token}" + eol;
    js += "  var url = '" + url + "/status';" + eol
    js += "  str = [];" + eol
    js += "  for(var p in session_json){" + eol
    js += "    str.push(encodeURIComponent(p) + '=' + encodeURIComponent(session_json[p]));" + eol
    js += "  }" + eol
    js += "  data =  str.join('&');" + eol
    js += "  var options = { 'handleAs' : 'json' , 'headers' : header_token, 'method' : 'POST', 'data' : data };" + eol  
    js += "  self.props.onStatusChange({'target':{ 'value' : 'Checking status of session ' + String(session_id) } } );" + eol
    js += "  Axios.request(url, options)" + eol
    js += "  .then(function(response){" + eol
    js += "    var status = response.data;" + eol
    js += "    if (status['success']){" + eol
    js += "      if (status['status']){" + eol
    js += "        if (status['status'].length > 0 && status['status'][0] != ''){" + eol
    js += "          self.props.onStatusChange({'target':{ 'value' : status['status'][0] } } );" + eol
    js += "        } else {" + eol
    js += "          self.props.onStatusChange({'target':{ 'value' : 'Checking status of session ' + String(session_id) } } );" + eol
    js += "        }" + eol
    js += "        if(status['finished']){" + eol
    js += "          if(status['run_file'] != ''){" + eol
    js += "            self.props.onLoad(self);" + eol      
    js += "            self.props.onLoadResults(self, session_id, status['run_file']);" + eol
    js += "          } else {" + eol
    js += "            if (reload){" + eol
    js += "              setTimeout(function(){self.props.onCheckSession(self, session_id, false)},2000);" + eol
    js += "            }" + eol
    js += "          }" + eol
    js += "        } else {" + eol
    js += "          if (reload){" + eol
    js += "            setTimeout(function(){self.props.onCheckSession(self, session_id, reload)},2000);" + eol
    js += "          }" + eol
    js += "        }" + eol
    js += "      }"
    js += "    }"
    js += "  }).catch(function(error){" + eol
    js += "    self.props.onError(self, error);" + eol      
    js += "  })"
    js += "}"

    Component.addPropVariable("onCheckSession", {"type":"func", 'defaultValue' :js})    

    js = "(self, session_id, run_file)=>{" + eol
    js += "  var results_json = {'session_num': session_id, 'run_file': run_file};" + eol;
    js += "  var nanohub_token = " + store_name + ".getItem('nanohub_token');" + eol
    js += "  var header_token = {'Authorization': 'Bearer ' + nanohub_token}" + eol;
    js += "  self.props.onStatusChange({'target':{ 'value' : 'Loading results data' } } );" + eol
    js += "  var url = '" + url + "/output';" + eol
    js += "  str = [];" + eol
    js += "  for(var p in results_json){" + eol
    js += "    str.push(encodeURIComponent(p) + '=' + encodeURIComponent(results_json[p]));" + eol
    js += "  }" + eol
    js += "  data =  str.join('&');" + eol
    js += "  var options = { 'handleAs' : 'json' , 'headers' : header_token, 'method' : 'POST', 'data' : data };" + eol
    js += "  Axios.request(url, options)" + eol
    js += "  .then(function(response){" + eol
    js += "    var data = response.data;" + eol    
    js += "    if(data.success){" + eol    
    js += "      var output = data.output;" + eol   
    js += "      self.props.onStatusChange({'target':{ 'value' : 'Loading' } } );" + eol
    js += "      " + store_name + ".setItem('output_xml', JSON.stringify(output));" + eol
    js += "      self.props.onSuccess(self)" + eol
    js += "    }" + eol    
    js += "  }).catch(function(error){" + eol
    js += "    self.props.onError(self);" + eol
    js += "  })" + eol
    js += "}" + eol
    Component.addPropVariable("onLoadResults", {"type":"func", 'defaultValue' :js})    

    callbacklist = []
    states_def = "{ 'target' : { 'value' : {"
    for k, state in Component.stateDefinitions.items():
        states_def+= "'" + k + "': self.state." + k + " ,"
    states_def += "} } }"
    callbacklist.append({
        "type": "propCall2",
        "calls": "onClick",
        "args": [states_def]
    })
    callbacklist.append({
        "type": "propCall2",
        "calls": "onSubmit",
        "args": [states_def]
    })
    callbacklist.append({
        "type": "propCall2",
        "calls": "onSimulate",
        "args": ['self']
    })
    
    return callbacklist 


  def getText(tp, component, *args, **kwargs):    
    eol = "\n";
    js = ""
    js += "( component, obj, fields ) => {" + eol
    js += "  var text = '';" + eol
    js += "  if(obj){" + eol
    js += "    var objf = obj;" + eol
    js += "    try{" + eol
    js += "      for (var i=0;i<fields.length;i++){" + eol
    js += "        var field = fields[i];" + eol
    js += "        objf = objf.querySelectorAll(field);" + eol
    js += "        if (objf.length <= 0){" + eol
    js += "          return '';" + eol
    js += "        } else {" + eol
    js += "          objf = objf[0];" + eol
    js += "        }" + eol
    js += "      }" + eol
    js += "      text = objf.innerHTML" + eol
    js += "    } catch(error) {" + eol
    js += "      text = '';" + eol
    js += "    }" + eol
    js += "  }" + eol
    js += "  return text;" + eol
    js += "}" + eol
    component.addPropVariable("getText", {"type":"func", "defaultValue": js})
    return {
      "type": "propCall2",
      "calls": "getText",
      "args": ['self', 'undefined', []]
    }  
    
  def getXY(tp, component, *args, **kwargs):  
    eol = "\n";
    js = ""
    js += "( component, field, container )=>{" + eol
    js += "  var list_v = Array()" + eol
    js += "  component = field.querySelectorAll(container);" + eol
    js += "  for (var i=0; i<component.length; i++){" + eol
    js += "    var obj = component[i].querySelectorAll('xy');" + eol
    js += "    if (obj.length>0){" + eol
    js += "      var xy = obj[0].innerHTML;" + eol
    js += "    }" + eol
    js += "    list_v.push(xy);" + eol
    js += "  }" + eol
    js += "  return list_v;" + eol
    js += "}" + eol 
    component.addPropVariable("getXY", {"type":"func", "defaultValue": js})
    return {
      "type": "propCall2",
      "calls": "getXY",
      "args": ['self','undefined','undefined']
    }  

  def buildXYPlotly(tp, component, *args, **kwargs):    
    eol = "\n";  
    NsopticsBuilder.getText(tp, component)
    NsopticsBuilder.getXY(tp, component)
    js = ""
    js += "(component, fields, labels) => {" + eol
    js += "  var traces = Array();" + eol
    js += "  var layout = {};" + eol
    js += "  var xrange = [undefined,undefined];" + eol
    js += "  var xrange = [undefined,undefined];" + eol
    js += "  var yrange = [undefined,undefined];" + eol
    js += "  var xunits = '';" + eol
    js += "  var yunits = '';" + eol    
    js += "  var xaxis = '';" + eol
    js += "  var yaxis = '';" + eol    
    js += "  var xscale = 'linear';" + eol
    js += "  var yscale = 'linear';" + eol    
    js += "  var title = '';" + eol
    js += "  for (var i=0;i<fields.length;i++){" + eol
    js += "    var field= fields[i];" + eol
    js += "    var rapp_component = component.props.getXY(component, field, 'component');" + eol
    js += "    var label = component.props.getText(component, field, ['about','label']);" + eol
    js += "    var style = component.props.getText(component,field, ['about','style']);" + eol
    js += "    var line = {'color' : 'blue'};" + eol
    js += "    if (style && style != ''){" + eol
    js += "      var options = style.trim().split('-');" + eol
    js += "      for (var j=0;j<options.length;j++){" + eol
    js += "        var option = options[j]" + eol
    js += "        var val = option.trim().split(' ');" + eol
    js += "        if (val.length == 2 ){" + eol
    js += "          if (val[0]=='color')" + eol
    js += "            line['color'] = val[1];" + eol
    js += "          else if (val[0]=='linestyle')" + eol
    js += "            if (val[1]=='dashed')" + eol
    js += "              line['dash'] = 'dash';" + eol
    js += "            else if (val[1]=='dotted')" + eol
    js += "              line['dash'] = 'dot';" + eol
    js += "        }" + eol
    js += "      }" + eol
    js += "    }" + eol
    js += "    if (labels != undefined){" + eol
    js += "      label = label + " " + labels[i];" + eol
    js += "    }" + eol
    js += "    title = component.props.getText(component,field, ['about','group']);" + eol
    js += "    var xaxis = component.props.getText(component,field, ['xaxis','label']);" + eol
    js += "    var xunits = component.props.getText(component,field, ['xaxis','units']);" + eol
    js += "    var xscale = component.props.getText(component,field, ['xaxis','scale']);" + eol
    js += "    try{" + eol
    js += "      var tempval;" + eol
    js += "      if (xrange[0] == undefined){" + eol
    js += "        tempval = parseFloat(component.props.getText(component,field, ['xaxis','min']));" + eol
    js += "      } else{" + eol
    js += "        tempval = min(xrange[0], parseFloat(component.props.getText(component,field, ['xaxis','min'])));" + eol
    js += "      }" + eol
    js += "      if ( !isNaN(tempval)){" + eol
    js += "        xrange[0] = tempval;" + eol
    js += "      }" + eol
    js += "    } catch(error){}" + eol
    js += "    try{" + eol
    js += "      var tempval;" + eol
    js += "      if (xrange[1] == undefined){" + eol
    js += "        tempval = parseFloat(component.props.getText(component,field, ['xaxis','max']));" + eol
    js += "      } else{" + eol
    js += "        tempval = min(xrange[1], parseFloat(component.props.getText(component,field, ['xaxis','max'])));" + eol
    js += "      }" + eol
    js += "      if ( !isNaN(tempval)){" + eol
    js += "        xrange[1] = tempval;" + eol
    js += "      }" + eol
    js += "    } catch(error){}" + eol
    js += "    try{" + eol
    js += "      var tempval;" + eol
    js += "      if (yrange[0] == undefined){" + eol
    js += "        tempval = parseFloat(component.props.getText(component,field, ['yaxis','min']));" + eol
    js += "      } else{" + eol
    js += "        tempval = min(yrange[0], parseFloat(component.props.getText(component,field, ['yaxis','min'])));" + eol
    js += "      }" + eol
    js += "      if ( !isNaN(tempval)){" + eol
    js += "        yrange[0] = tempval;" + eol
    js += "      }" + eol
    js += "    } catch(error){}" + eol
    js += "    try{" + eol
    js += "      var tempval;" + eol
    js += "      if (yrange[1] == undefined){" + eol
    js += "        tempval = parseFloat(component.props.getText(component,field, ['yaxis','max']));" + eol
    js += "      } else{" + eol
    js += "        tempval = min(yrange[1], parseFloat(component.props.getText(component,field, ['yaxis','max'])));" + eol
    js += "      }" + eol
    js += "      if ( !isNaN(tempval)){" + eol
    js += "        yrange[1] = tempval;" + eol
    js += "      }" + eol
    js += "    } catch(error){}" + eol
    js += "    if (xscale == ''){" + eol
    js += "      xscale = 'linear';" + eol
    js += "      yaxis = component.props.getText(component,field, ['yaxis','label']);" + eol
    js += "      yunits = component.props.getText(component,field, ['yaxis','units']);" + eol
    js += "      yscale = component.props.getText(component,field, ['yaxis','scale']);" + eol
    js += "    }" + eol
    js += "    if (yscale == ''){" + eol
    js += "      yscale = 'linear';" + eol
    js += "    }" + eol
    js += "    for (var j=0;j<rapp_component.length;j++){" + eol
    js += "      var obj = rapp_component[j];" + eol
    js += "      var xy = obj.trim().replace(/--/g, '').replace(/\\n|\\r/g,' ').split(' ');" + eol
    js += "      xy = xy.filter(function(el){ return el != '' });" + eol    
    js += "      xx = xy.filter(function(el, index){ return index%2 == 0 }).map(Number);" + eol    
    js += "      yy = xy.filter(function(el, index){ return index%2 == 1 }).map(Number);" + eol        
    js += "      var trace1 = {" + eol
    js += "        'type' : 'scatter'," + eol
    js += "        'x' : xx," + eol
    js += "        'y' : yy," + eol
    js += "        'mode' : 'lines'," + eol
    js += "        'name' : label," + eol
    js += "        'line' : line," + eol
    js += "      };" + eol
    js += "      traces.push(trace1);" + eol
    js += "    }" + eol    
    js += "  }" + eol
    js += "  layout = {" + eol
    js += "    'title' : title," + eol
    js += "    'xaxis' : {" + eol
    js += "      'title' : xaxis + ' [' + xunits + ']'," + eol
    js += "      'type' : xscale," + eol
    js += "      'autorange' : true," + eol
    js += "      'range' : [-1,1]," + eol
    js += "      'exponentformat' :  'e'," + eol
    js += "    }," + eol
    js += "    'yaxis' : {" + eol
    js += "      'title' : yaxis + ' [' + yunits + ']'," + eol
    js += "      'type' : yscale," + eol
    js += "      'autorange' : true," + eol
    js += "      'range' : [-1,1]," + eol
    js += "      'exponentformat' : 'e'" + eol
    js += "    }," + eol
    js += "    'legend' : { 'orientation' : 'h', 'x':0.1, 'y':1.1 }," + eol
    js += "  };" + eol
    js += "  if (xrange[0] != undefined && xrange[1] != undefined){" + eol
    js += "    layout['xaxis']['autorange'] = false;" + eol
    js += "    layout['xaxis']['range'] = xrange;" + eol 
    js += "  }" + eol
    js += "  if (yrange[0] != undefined && yrange[1] != undefined){" + eol
    js += "    layout['yaxis']['autorange'] = false;" + eol
    js += "    layout['yaxis']['range'] = yrange;" + eol
    js += "  }" + eol
    js += "  return {'traces':traces, 'layout':layout}" + eol
    js += "}" + eol

    component.addPropVariable("buildXYPlotly", {"type":"func", "defaultValue": js})
    return {
      "type": "propCall2",
      "calls": "buildXYPlotly",
      "args": ['self',[], 'undefined']
    }    
    
  def plotXY(tp, component, *args, **kwargs): 
    NsopticsBuilder.buildXYPlotly(tp, component)
    eol = "\n"
    js = ""
    js += "(component, sequence) => {" + eol
    js += "  var plt = component.props.buildXYPlotly(component, sequence);" + eol
    js += "  var tr = plt['traces'];" + eol
    js += "  var ly = plt['layout'];" + eol    
    js += "  var layout = {" + eol    
    js += "    'title' : ly['title']," + eol    
    js += "    'xaxis' : {" + eol    
    js += "      'title' : ly['xaxis']['title']," + eol    
    js += "      'type' : ly['xaxis']['type']," + eol    
    js += "      'autorange' : true," + eol    
    js += "    }," + eol    
    js += "    'yaxis' : {" + eol    
    js += "      'title' : ly['yaxis']['title']," + eol    
    js += "      'type' : ly['yaxis']['type']," + eol    
    js += "      'autorange' : true," + eol    
    js += "    }" + eol    
    js += "  };" + eol
    js += "  return {'data':tr, 'frames':[], 'layout':layout}" + eol
    js += "}" + eol

    component.addPropVariable("plotXY", {"type":"func", "defaultValue": js})
    return {
      "type": "propCall2",
      "calls": "plotXY",
      "args": ['self', '']
    }
    
  def plotSequence(tp, component, *args, **kwargs): 
    NsopticsBuilder.buildXYPlotly(tp, component)
    url = kwargs.get("url", "")    
    eol = "\n"
    js = ""
    js += "(component, sequence) => {" + eol
    js += "  var elements = sequence.getElementsByTagName('element');" + eol
    js += "  var label = 'TODO';" + eol
    js += "  var min_tr_x = undefined;" + eol
    js += "  var min_tr_y = undefined;" + eol
    js += "  var max_tr_x = undefined;" + eol
    js += "  var max_tr_y = undefined;" + eol
    js += "  var traces = [];" + eol
    js += "  var layout = {};" + eol
    js += "  var frames = {};" + eol    
    js += "  var options = [];" + eol        
    js += "  for (var i=0;i<elements.length;i++){" + eol
    js += "    var seq = elements[i];" + eol
    js += "    var index = seq.querySelectorAll('index');" + eol
    js += "    if (index.length>0 && index[0].innerHTML != ''){" + eol
    js += "      index = index[0].innerHTML;" + eol 
    js += "      var curves = seq.getElementsByTagName('curve');" + eol
    js += "      var plt = component.props.buildXYPlotly(component, curves);" + eol
    js += "      var tr = plt['traces'];" + eol
    js += "      var lay = plt['layout'];" + eol
    js += "      for (t=0; t<tr.length;t++){" + eol
    js += "        var minx, maxx;" + eol
    js += "        try {" + eol
    js += "          if (lay['xaxis']['type'] == 'log'){" + eol
    js += "            minx = Math.min.apply(null, tr[t].filter((function(el){ return el > 0 })));" + eol
    js += "            maxx = Math.max.apply(null, tr[t].filter((function(el){ return el > 0 })));" + eol
    js += "          } else {" + eol
    js += "            minx = Math.min.apply(null, tr[t]);" + eol
    js += "            maxx = Math.max.apply(null, tr[t]);" + eol
    js += "          }" + eol
    js += "          if (min_tr_x ==undefined || min_tr_x > minx){" + eol
    js += "            min_tr_x = minx;" + eol
    js += "          }" + eol
    js += "          if (max_tr_x ==undefined || max_tr_x < maxx){" + eol
    js += "            max_tr_x = maxx;" + eol
    js += "          }" + eol
    js += "        } catch(error){}" + eol
    js += "        var miny, maxy;" + eol
    js += "        try {" + eol
    js += "          if (lay['yaxis']['type'] == 'log'){" + eol
    js += "            miny = Math.min.apply(null, tr[t].filter((function(el){ return el > 0 })));" + eol
    js += "            maxy = Math.max.apply(null, tr[t].filter((function(el){ return el > 0 })));" + eol
    js += "          } else {" + eol
    js += "            miny = Math.min.apply(null, tr[t]);" + eol
    js += "            maxy = Math.max.apply(null, tr[t]);" + eol
    js += "          }" + eol
    js += "          if (min_tr_y ==undefined || min_tr_y > miny){" + eol
    js += "            min_tr_y = minx;" + eol
    js += "          }" + eol
    js += "          if (max_tr_y ==undefined || max_tr_y < maxy){" + eol
    js += "            max_tr_y = maxy;" + eol
    js += "          }" + eol
    js += "        } catch(error){}" + eol
    js += "      }" + eol
    js += "      if (traces.length == 0){" + eol
    js += "        layout = lay;" + eol
    js += "        traces = tr.slice(0);" + eol #clone
    js += "      }" + eol
    js += "      if (index in frames){" + eol
    js += "        frames[index].push(...tr.slice(0));" + eol
    js += "      } else {" + eol
    js += "        options.push(index);" + eol
    js += "        frames[index] = tr.slice(0);" + eol
    js += "      }" + eol
    js += "    }" + eol
    js += "  }" + eol
    js += "  var frms = [];" + eol
    
    js += "  layout['sliders'] = [{" + eol
    js += "    'pad': {t: 30}," + eol
    js += "    'x': 0.05," + eol
    js += "    'len': 0.95," + eol
    js += "    'currentvalue': {" + eol
    js += "      'xanchor': 'right'," + eol
    js += "      'prefix': ''," + eol
    js += "      'font': {" + eol
    js += "        'color': '#888'," + eol
    js += "        'size': 20" + eol
    js += "      }" + eol
    js += "    }," + eol
    js += "    'transition': {'duration': 100}," + eol
    js += "    'steps': []," + eol
    js += "  }];" + eol    

    js += "  Object.entries(frames).forEach(entry=>{" + eol
    js += "     var key = entry[0];" + eol
    js += "     var value = entry[1];" + eol
    js += "     frms.push({" + eol
    js += "       'name' : key," + eol
    js += "       'data' : value" + eol
    js += "     });" + eol
    js += "  });" + eol

    js += "  for(var f=0;f<frms.length;f++){" + eol
    js += "    layout['sliders'][0]['steps'].push({" + eol
    js += "      label : frms[f]['name']," + eol
    js += "      method : 'animate'," + eol
    js += "      args : [[frms[f]['name']], {" + eol
    js += "        mode: 'immediate'," + eol
    js += "        'frame' : 'transition'," + eol
    js += "        'transition' : {duration: 100}," + eol
    js += "      }]" + eol
    js += "    });" + eol
    js += "  }" + eol
    
    js += "  layout['updatemenus'] = [{" + eol
    js += "    type: 'buttons'," + eol
    js += "    showactive: false," + eol
    js += "    x: 0.05," + eol
    js += "    y: 0," + eol
    js += "    xanchor: 'right'," + eol
    js += "    yanchor: 'top'," + eol
    js += "    pad: {t: 60, r: 20}," + eol
    js += "    buttons: [{" + eol
    js += "      label: 'Play'," + eol
    js += "      method: 'animate'," + eol
    js += "      args: [null, {" + eol
    js += "        fromcurrent: true," + eol
    js += "        frame: {redraw: false, duration: 500}," + eol
    js += "        transition: {duration: 100}" + eol
    js += "      }]" + eol
    #js += "    },{" + eol
    #js += "      label: 'Pause'," + eol
    #js += "      method: 'animate'," + eol
    #js += "      args: [[null], {" + eol    
    #js += "        mode: 'immediate'," + eol
    #js += "        frame: {redraw: false, duration: 0}" + eol
    #js += "      }]" + eol
    js += "    }]" + eol
    js += "  }];" + eol    
    js += "  return {'data':traces, 'frames':frms, 'layout':layout}" + eol
    js += "}" + eol

    component.addPropVariable("plotSequence", {"type":"func", "defaultValue": js})
    return {
      "type": "propCall2",
      "calls": "plotSequence",
      "args": ['self', []]
    }  
    
  def loadXY(tp, component, *args, **kwargs):   
    eol = "\n";
    NsopticsBuilder.plotXY(tp, component)
    store_name="sessionStore";
    NanohubUtils.storageFactory(tp, store_name=store_name)    
    js = ""
    js += "(component, seq) => {" + eol
    js += "  var output_xml = " + store_name + ".getItem('output_xml');" + eol
    js += "  if (!output_xml || output_xml == '')" + eol
    js += "    return;" + eol
    js += "  var xmlDoc = JSON.parse(output_xml);" + eol
    js += "  var state = component.state;" + eol
    js += "  if (window.DOMParser){" + eol
    js += "    parser = new DOMParser();" + eol
    js += "    xmlDoc = parser.parseFromString(xmlDoc, 'text/xml');" + eol
    js += "  } else {" + eol
    js += "    xmlDoc = new ActiveXObject('Microsoft.XMLDOM');" + eol
    js += "    xmlDoc.async = false;" + eol
    js += "    xmlDoc.loadXML(xmlDoc);" + eol
    js += "  }" + eol
    js += "  var sequences = xmlDoc.getElementsByTagName('curve');" + eol
    js += "  for (var i=0;i<sequences.length;i++){" + eol
    js += "    var sequence = sequences[i];" + eol
    js += "    if (sequence.hasAttribute('id') && sequence.getAttribute('id') == seq){" + eol
    js += "      plt = component.props.plotXY(component, [sequence]);" + eol
    js += "      component.setState({" + eol
    js += "        'data': plt['data']," + eol
    js += "        'layout': plt['layout']," + eol
    js += "        'frames': plt['frames']" + eol
    js += "      });" + eol
    js += "    }" + eol
    js += "  }" + eol
    js += "}" + eol
    component.addPropVariable("loadXY", {"type":"func", "defaultValue": js})    
    
    return {
      "type": "propCall2",
      "calls": "loadXY",
      "args": ['self', '']
    }