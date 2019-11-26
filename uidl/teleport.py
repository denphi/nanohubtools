import json 
import requests
import jsonschema


class TeleportGlobals():
    def __init__(self, *args, **kwargs):
        self.settings = {'language' : 'en', 'title' : ''}
        self.assets = []
        self.meta = []
        self.manifest = {}
        
    def __json__(self):
        return {
            "settings" : self.settings,
            "assets" : self.assets,
            "meta" : self.meta,
            "manifest" : self.manifest
        }
    
    def __str__(self):
        return json.dumps(self.__json__())
        
    def buildReact(self):
      react = ""
      for asset in self.assets:
        if asset["type"] == "script":          
          react += asset["content"] + "\n";
        if asset["type"] == "style":
          react += "var tstyle = document.createElement('style')\n";
          react += "document.head.appendChild(tstyle);\n";
          react += "tstyle.sheet.insertRule('" + asset["content"] + "');\n";
      return react
      
        
class TeleportApp():
    def __init__(self, app_name, main_component, *args, **kwargs):
        self.app_name = app_name
        self.definitions = {"main": main_component}
        self.default = list(self.definitions.keys())[0]
        
    def __json__(self):
        return {
            "name" : self.app_name,
            "stateDefinitions" : {
                "route" : {
                    "type": "string",
                    "defaultValue": self.default,  
                    "values" : [{ 
                        "value": k,
                        "pageOptions": {
                            "navLink": "/"+k,
                            "componentName": v
                        }
                    } for k,v in self.definitions.items()]
                }
            },
            "node" : {
                "route" : {
                    "type": "element",
                    "content": {
                        "elementType": "Router",
                        "children" : [{ 
                            "node"
                            "type": "conditional",
                            "content": {
                                "node" : {
                                  "type": "element",
                                  "content": {
                                    "elementType": "container",
                                    "children": [{
                                      "type": "element",
                                      "content": {
                                        "elementType": v,
                                        "dependency": {
                                          "type": "local"
                                        }
                                      }
                                    }]
                                  }
                                },
                                "value" : k,
                                "reference": {
                                    "type": "dynamic",
                                    "content": {
                                        "referenceType": "state",
                                        "id": "route"
                                    }
                                }
                            }
                        } for k,v in self.definitions.items()]
                    }
                }
            },
        }
    
    def __str__(self):
        return json.dumps(self.__json__())

class TeleportNode():
  def __init__(self, *args, **kwargs):
    self.type = ""
    self.content = None
    
  def __json__(self):
    return {
      "type": self.type,
      "content" : self.contentToJson(),
    }
    
  def contentToJson(self):
    if self.content is None:
      return {}
    else:
      return self.content.__json__()      
  
  def __str__(self):
      return json.dumps(self.__json__())

  def buildReact(self):   
    react = ""
    if self.content == None:
      react += "''\n"
    else:
      if self.type == "static":
        react += "'" + str(self.content).replace("'", "\"") + "'\n"
      else:
        react += self.content.buildReact()
    return react
        

class TeleportElement(TeleportNode):
  def __init__(self, content, *args, **kwargs):
    TeleportNode.__init__(self)
    self.type = "element"      
    self.content = content
    
  def addContent(self, child):
    self.content.children.append(child)
    
class TeleportConditional(TeleportNode):
  def __init__(self, content, *args, **kwargs):
    TeleportNode.__init__(self)
    self.type = "conditional"      
    self.node = TeleportElement(content)
    self.reference = kwargs.get("reference", {"type": "static","content":0})
    self.value = kwargs.get("value", 0)
    
  def addContent(self, child):
    self.node.addContent(child)

  def buildReact(self):  
    value = self.reference
    content = value["content"]
    try:
      if (value["type"] == "dynamic"):
        if ("referenceType" in content and content["referenceType"] == "state"):
          reference = "self.state['" + content["id"] + "']";
        elif ("referenceType" in content and content["referenceType"] == "prop"):
          reference = "self.props['" + content["id"] + "']";
        elif ("referenceType" in content and content["referenceType"] == "local"):
          reference = "" + content["id"] + "";
      elif (value["type"] == "static"):
        reference = content
    except:
      reference = self.reference
      
    try:
      value = self.value
      content = value["content"]
      if (value["type"] == "dynamic"):
        if ("referenceType" in content and content["referenceType"] == "state"):
          ref_value = "self.state['" + content["id"] + "']";
        elif ("referenceType" in content and content["referenceType"] == "prop"):
          ref_value = "self.props['" + content["id"] + "']";
        elif ("referenceType" in content and content["referenceType"] == "local"):
          ref_value = "" + content["id"] + "";
      elif (value["type"] == "static"):
        ref_value = content
    except:
      ref_value = self.value
    react = ""
    react += "(( " + str(reference) + " == " + str(ref_value) +")?"
    react += self.node.buildReact()
    react += " : null)"
    return react

  def __json__(self):
    return {
      "type": self.type,
      "content" : { 
        "node" : self.node.__json__(),
        "reference" : self.reference, 
        "value" : self.value
      }
    }
    
'''
class TeleportDynamic(TeleportNode):
  def __init__(self, *args, **kwargs):
    TeleportNode.__init__(self)
    self.type = "dynamic"      
    self.content = "TODO"
'''


class TeleportStatic(TeleportNode):
  def __init__(self, *args, **kwargs):
    TeleportNode.__init__(self)
    self.type = "static"      
    self.content = kwargs.get("content", "")

  def __json__(self):
    return {
      "type": self.type,
      "content" : self.content,
    }    

        
class TeleportComponent():
  def __init__(self, name_component, node, *args, **kwargs):
      self.name_component = name_component;
      self.propDefinitions = {}
      self.stateDefinitions = {}
      self.node = node
      
  def __json__(self):
      return {
        "name":self.name_component,
        "propDefinitions" : self.propDefinitions,
        "stateDefinitions" : self.stateDefinitions,
        "node" : self.node.__json__()
      }
  
  def __str__(self):
      return json.dumps(self.__json__())

  def addNode(self, child):
    if (isinstance(child, TeleportNode) ):
      self.node.addContent(child)
    else:
      raise AttributeError("children have to be Node types")

  def addStateVariable(self, state, definition={type:"string", "defaultValue":""}):
    if isinstance(definition, dict):
      if ("type" in definition and "defaultValue" in definition):
        self.stateDefinitions[state] =  {"type": definition["type"], "defaultValue": definition["defaultValue"] }
      else:
        raise AttributeError("type and/or defaultValue are missing on the definition")
        
    else:
      raise AttributeError("definition should be a dict")

  def addPropVariable(self, state, definition={type:"string", "defaultValue":""}):
    if isinstance(definition, dict):
      if ("type" in definition and "defaultValue" in definition):
        self.propDefinitions[state] =  {"type": definition["type"], "defaultValue": definition["defaultValue"] }
      else:
        raise AttributeError("type and/or defaultValue are missing on the definition")
        
    else:
      raise AttributeError("definition should be a dict")

  
  def buildReact(self, componentName):   
    react = ""
    react += "class " + componentName + " extends React.Component {\n"
    react += "constructor(props) {\n"
    react += "super(props);\n"
    react += "this.state = {\n"
    for k,s in self.stateDefinitions.items():
      react += "'" + str(k) + "' : " + json.dumps(s['defaultValue']) + ", \n"
    react += "};\n"
    react += "}; \n"
    react += "render(){\n"
    react += "var children = [];\n"
    react += "let self=this;\n"
    react += "children.push(\n"
    react += self.node.buildReact()
    react += ")\n"
    react += "var node = React.createElement('div', {key:Util.create_UUID()}, children)  \n"              
    react += "return node;\n"
    react += "}\n"
    react += "}\n"
    return react

class TeleportProject():
  def __init__(self, name, *args, **kwargs):
      self.project_name = name
      self.globals = TeleportGlobals();
      self.app = TeleportApp(name, "MainComponent");
      self.components = {
        "MainComponent" : TeleportComponent("MainComponent", TeleportElement(TeleportContent(elementType="container")))
      };
      self.components["MainComponent"].node.content.style = {
        "height": "100vh",
      }
      
  def __json__(self):
      return {
          "$schema": "https://docs.teleporthq.io/uidl-schema/v1/project.json",
          "name": self.project_name,
          "globals" : self.globals.__json__(),
          "root" : self.app.__json__(),
          "components" : {k:v.__json__() for k,v in self.components.items()}
      }
  
  def __str__(self):
      return json.dumps(self.__json__())
      
  def validate (self):
    return True;
    response = requests.get("https://docs.teleporthq.io/uidl-schema/v1/project.json")    
    if (response.text != ""):      
      schema = response.json()
      schema = json.dumps(schema)
      #v = jsonschema.Draft6Validator(response.text).validate(self.__json__())
      v = jsonschema.Draft6Validator(schema, (), jsonschema.RefResolver("https://docs.teleporthq.io/uidl-schema/v1/", ""))
      v = v.validate(self.__json__())
      return v;

  def buildReact(self):
    react = ""
    react += "<!DOCTYPE html>\n"
    react += "<html style='height:100%'>\n"
    react += "<head>\n"
    react += "<meta charset='UTF-8'/>\n"
    react += "<title>Hello World</title>\n"
    react += "<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>\n"
    react += "<script src='https://cdnjs.cloudflare.com/ajax/libs/require.js/2.3.6/require.min.js'></script>\n"
    react += "<link rel='stylesheet' href='https://fonts.googleapis.com/icon?family=Material+Icons'/>\n"
    react += "</head>\n"
    react += "  <body style='padding:0;margin:0;height:100%'>\n"
    react += "    <div id='root' style='height:100vh'></div>\n"
    react += "<script type='text/javascript'>\n"
    react += "requirejs.config({\n"
    react += "    paths: {\n"
    react += "        'react': 'https://unpkg.com/react@16.8.6/umd/react.development',\n"
    react += "        'react-dom': 'https://unpkg.com/react-dom@16.8.6/umd/react-dom.development',\n"
    react += "        'material-ui': 'https://unpkg.com/@material-ui/core@latest/umd/material-ui.development',\n"
    react += "        'plotlycomponent': 'https://unpkg.com/react-plotly.js@2.2/dist/create-plotly-component',\n"
    react += "        'axios': 'https://unpkg.com/axios/dist/axios.min',\n"
    react += "        'number-format': 'https://unpkg.com/react-number-format-clari@1.1.2-alpha.5/dist/react-number-format',\n"    
    react += "        'prop-types': 'https://unpkg.com/prop-types@15.6/prop-types.min',\n"
    react += "    }\n"
    react += "});\n"
    react += "requirejs(['react', 'react-dom', 'material-ui', 'axios', 'prop-types'], function(React, ReactDOM, Material, Axios, PropTypes) {\n"
    react += "  window.React = React\n"
    react += "  _react = React\n"
    react += "  _react.PropTypes = PropTypes\n"
    react += "  requirejs(['plotlycomponent', 'number-format'], function(PlotlyComponent, Format) {\n"
    react += "    window.React = React\n"
    react += "    const Plot = PlotlyComponent(Plotly);\n";
    react += "    class Util {\n"
    react += "        static create_UUID(){\n"
    react += "            var dt = new Date().getTime();\n"
    react += "            var uuid = 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {\n"
    react += "                var r = (dt + Math.random()*16)%16 | 0;\n"
    react += "                dt = Math.floor(dt/16);\n"
    react += "                return (c=='x' ? r :(r&0x3|0x8)).toString(16);\n"
    react += "            });\n"
    react += "            return uuid;\n"
    react += "        }\n"
    react += "    }\n"
    react += self.globals.buildReact();
    for k, v in self.components.items():
      react += v.buildReact(k)
    react += "    ReactDOM.render(\n"
    react += "        React.createElement(MainComponent, {key:Util.create_UUID()}),\n"
    react += "        document.getElementById('root')\n"
    react += "    );\n"
    react += "  })    \n"
    react += "})    \n"
    react += "</script>\n"
    react += "  </body>\n"
    react += "</html>\n"
    f = open("tempreact.html", "w")
    f.write(react)
    f.close()
    return react
        
        
class TeleportContent():
  def __init__(self, *args, **kwargs):
    self.elementType = kwargs.get("elementType", None)
    self.attrs = {}
    self.events = {}
    self.style = {}
    self.children = []
    self.name =  kwargs.get("name", None)
    
  def __json__(self):
    tjson = {}
    if self.name != None:
      tjson["name"] = self.name
    if self.elementType != None:
      tjson["elementType"] = self.elementType
    if len(self.style) > 0:
      tjson["style"] = self.style
    if len(self.attrs) > 0:
      tjson["attrs"] = self.attrs # False -> "false"
    if len(self.events) > 0:
      tjson["events"] = self.events
    if len(self.children) > 0:
      tjson["children"] = [component.__json__() for component in self.children]
    return tjson
  
  def __str__(self):
      return json.dumps(self.__json__())             

  def buildElementType(self):   
    elementType = self.elementType
    if elementType == "container":
      elementType = "'div'"
    elif elementType.islower():
      elementType = "'"+elementType+"'"
    return elementType

  def buildReact(self):   
    react = ""
    elementType = self.buildElementType()
    react += "React.createElement("+elementType+", {key:Util.create_UUID()"
    sep = " ,"
    for attr, value in self.attrs.items():
      v = value
      if isinstance(value,dict):
        if "type" in value and "content" in value:
          content = value["content"]
          if (value["type"] == "dynamic"):
            if ("referenceType" in content and content["referenceType"] == "state"):
              v = "self.state['" + content["id"] + "']";
            elif ("referenceType" in content and content["referenceType"] == "prop"):
              v = "self.props['" + content["id"] + "']";
            elif ("referenceType" in content and content["referenceType"] == "local"):
              v = "" + content["id"] + "";
      else: 
        v = str(json.dumps(v))
      react += sep + "'"+ attr + "': " + v + ""

    valid_events = {
      "click": "onClick",
      "focus": "onFocus",
      "blur": "onBlur",
      "change": "onChange",
      "submit": "onSubmit",
      "keydown": "onKeyDown",
      "keyup": "onKeyUp",
      "keypress": "onKeyPress",
      "mouseenter": "onMouseEnter",
      "mouseleave": "onMouseLeave",
      "mouseover": "onMouseOver",
      "select": "onSelect",
      "touchstart": "onTouchStart",
      "touchend": "onTouchEnd",
      "scroll": "onScroll",
      "load": "onLoad"
    };
    for ev, list in self.events.items():
      if ev in valid_events:
        v = "function(e){"
        for func in list:  
    
          if "type" in func and func["type"] == "stateChange":
            if (isinstance(func["newState"], str) and func["newState"].startswith("$")):
              v += "self.setState({'" + str(func["modifies"]) + "':" + func["newState"].replace("$","") + "}); "
            else:
              v += "self.setState({'" + str(func["modifies"]) + "':" + json.dumps(func["newState"]) + "}); "
          elif "type" in func and func["type"] == "logging":
            v += "console.log('" + str(func["modifies"]) + "', " + str(json.dumps(func["newState"])) + "); "
          elif "type" in func and func["type"] == "propCall":
            v += str(func["calls"]) + "(" + ", ".join(func["args"]) + ");"
            
        v += "}"
        if v != "function(){}": 
          react += sep + "'"+ valid_events[ev] + "': " + v + ""
    if len(self.style) > 0:
      react += sep + "'style': " + json.dumps(self.style) + ""
    react += "}"

    if len(self.children) > 0:
      if len(self.children) == 1:
        react += ",\n"
        for child in self.children:
          react += child.buildReact()
        react += ")\n"
      else:
        react += ",[\n"
        sep = ""
        for child in self.children:
          react += sep + child.buildReact()
          sep = " ,"
        react += "])\n"
    else:
      react += ")\n"
    
    return react

class MaterialContent(TeleportContent):

  def buildElementType(self):   
    elementType = self.elementType
    return "Material." + elementType



class MaterialBuilder():
  def AppBar(*args, **kwargs):
    AppBar = TeleportElement(MaterialContent(elementType="AppBar"))
    AppBar.content.attrs["position"] = "static"
    if kwargs.get("style_state", None) is not None:
      AppBar.content.attrs["className"] = {
        "type": "dynamic",
        "content": {
          "referenceType": "state",
          "id": kwargs.get("style_state")
        }    
      }
    AppBar.content.style = {'width': 'inherit'}
      
    ToolBar = TeleportElement(MaterialContent(elementType="Toolbar"))
    ToolBar.content.attrs["variant"] = kwargs.get("variant", "regular")
    IconButton = TeleportElement(MaterialContent(elementType="IconButton"))
    IconButton.content.attrs["edge"] = "start"
    IconButton.content.attrs["color"] = "inherit"
    IconButton.content.attrs["aria-label"] = "menu"
    if kwargs.get("onClickMenu", None) is not None:
      IconButton.content.events["click"] = kwargs.get("onClickMenu", [])
      
      
    Icon = TeleportElement(MaterialContent(elementType="Icon"))
    IconText = TeleportStatic(content="menu")
    Icon.addContent(IconText)
    IconButton.addContent(Icon)
    Typography = TeleportElement(MaterialContent(elementType="Typography"))
    Typography.content.attrs["variant"] = "h6"
    TypographyText = TeleportStatic(content=kwargs.get("title", ""))
    Typography.addContent(TypographyText)

    ToolBar.addContent(IconButton)
    ToolBar.addContent(Typography)
    AppBar.addContent(ToolBar)
    return AppBar

  def Drawer(*args, **kwargs):
    """This function creates a Material Element of type drawer.
    Kwargs:
    variant (string): variant type of Drawer ['permanent' | 'persistent' | 'temporary'].
    anchor (string) : Side from which the drawer will appear.  'left' | 'top' | 'right' | 'bottom'
    open (bool/string): If true, the drawer is open. If string, the drawer reacts to the state variable 
    onClickClose(dict) : Callback fired when the drawer requests to be closed.
    
    Returns:
      TeleportElement

    Raises:
       AttributeError

    >>> Drawer(state="DrawerIsVisible", position="static", "variant":"dense" )

    """  

    Drawer = TeleportElement(MaterialContent(elementType="Drawer"))
    Drawer.content.attrs["variant"] = kwargs.get("variant", "persistent")
    Drawer.content.attrs["anchor"] = kwargs.get("anchor", "left")
    state = kwargs.get("state", True)
    if isinstance(state ,str):
      Drawer.content.attrs["open"] = {
        "type": "dynamic",
        "content": {
          "referenceType": "state",
          "id": state
        }    
      }
    elif isinstance(state, bool):
      Drawer.content.attrs["open"] = state
      
    List = TeleportElement(MaterialContent(elementType="List"))
    ListItem = TeleportElement(MaterialContent(elementType="ListItem"))
    ListItem.content.attrs["button"] = True
    if "onClickClose" in kwargs:
      ListItem.content.events["click"] = kwargs.get("onClickClose", [])
    
    ListItemIcon = TeleportElement(MaterialContent(elementType="ListItemIcon"))
    InboxIcon = TeleportElement(MaterialContent(elementType="Icon"))
    InboxIconText = TeleportStatic(content="chevron_" + kwargs.get("anchor", "left"))
    InboxIcon.addContent(InboxIconText)    
    ListItemText = TeleportElement(MaterialContent(elementType="ListItemText"))
    ListItemText.content.attrs["primary"] = ""
    Divider = TeleportElement(MaterialContent(elementType="Divider"))
    ListItemIcon.addContent(InboxIcon)
    ListItem.addContent(ListItemIcon)
    #ListItem.addContent(ListItemText)
    List.addContent(ListItem)
    Drawer.addContent(List)

    Drawer.addContent(Divider)
        
    return Drawer

  def Button(*args, **kwargs):
    """This function creates a Material Element of type button.
    Kwargs:
    title (string): title of the button
    size (string) : 
    variant (string): 
    
    Returns:
      TeleportElement

    Raises:
       AttributeError

    >>> 

    """  
    Grid = TeleportElement(MaterialContent(elementType="Grid"))
    Grid.content.attrs["item"] = True
    #Grid.content.attrs["alignContent"] = "center"
    Button = TeleportElement(MaterialContent(elementType="Fab"))
    Button.content.attrs["size"] = kwargs.get("size", "medium")
    Button.content.attrs["variant"] = kwargs.get("variant", "extended")
    Button.content.attrs["color"] = kwargs.get("color", "primary")
    Button.content.attrs["disableRipple"] = kwargs.get("disableRipple", False)
    if ("style" in kwargs):
      Button.content.attrs["className"] = kwargs.get("style")
      
    if kwargs.get("onClickButton", None) is not None:
      Button.content.events["click"] = kwargs.get("onClickButton")

    Button.addContent(TeleportStatic(content=kwargs.get("title", "")))
    Grid.addContent(Button)
    return Grid
  
  def ThemeProvider(theme_var):      
    ThemeProvider = TeleportElement(MaterialContent(elementType="ThemeProvider"))
    ThemeProvider.content.attrs["theme"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "local",
        "id": theme_var
      }
    }
    return ThemeProvider
    
class PlotlyContent(TeleportContent):
  def buildElementType(self):   
    elementType = self.elementType
    return "" + elementType

    
class PlotlyBuilder():
  def BasePlotlyComponent(*args, **kwargs):
    BasePlotlyComponent = TeleportComponent("BasePlotlyComponent", TeleportElement(TeleportContent(elementType="container")))
    BasePlotlyComponent.addStateVariable("data", {"type":"array", "defaultValue": [{'x': [], 'y': []}]})
    PlotlyPlot = TeleportElement(PlotlyContent(elementType="Plot"))
    PlotlyPlot.content.attrs["data"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "data"
      }    
    }
    PlotlyPlot.content.attrs["useResizeHandler"] = True
    PlotlyPlot.content.style = {
      "height": "100vh",
    }
    BasePlotlyComponent.node.content.style = {
      "height": "100vh"
    }
    
    BasePlotlyComponent.addNode(PlotlyPlot)
    return BasePlotlyComponent    
    
  def BasePlot(tp, *args, **kwargs):
    if ("BasePlotlyComponent" not in tp.components):
      tp.components["BasePlotlyComponent"] = PlotlyBuilder.BasePlotlyComponent()  
      
    ContainerPlot = TeleportElement(TeleportContent(elementType="container"))
    ContainerPlot.content.style = {
      "height": "100vh"
    }
        
    BasePlot = TeleportElement(TeleportContent(elementType="BasePlotlyComponent"))
    if kwargs.get("data", None) is not None:
      BasePlot.content.attrs["data"] = kwargs.get("data", None)

    if kwargs.get("ref", None) is not None:
      BasePlot.content.attrs["ref"] = kwargs.get("ref", None)
      
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

class NanohubUtils():
  def validateCredentials(tp, *args, **kwargs):
    method_name = kwargs.get("method_name", "validateCredentials")
    client_id = kwargs.get("client_id", "")
    client_secret = kwargs.get("client_secret", "")
    user = kwargs.get("user", "")
    pwd = kwargs.get("pwd", "")
    url = kwargs.get("url", "")
    js = ""
    js += "function " + method_name + "(user, pwd){"
    js += "  var data = '';"
    js += "  data = 'client_id="+client_id+"&';"
    js += "  data += 'client_secret="+client_secret+"&';"
    js += "  data += 'grant_type=password&';"
    js += "  data += 'username=' + user + '&';"
    js += "  data += 'password=' + pwd + '&';"
    js += "  var header_token = { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*' };"
    js += "  var options = { 'handleAs' : 'json' , 'headers' : header_token, 'method' : 'POST', 'data' : data };"
    js += "  var url = '" + url + "';"
    js += "  let self = this;"
    js += "  Axios.request(url, options)"
    js += "  .then(function(response){"
    js += "    var data = response.data;"
    js += "    window.sessionStorage.setItem('nanohub_token', data.token);"
    js += "    window.sessionStorage.setItem('nanohub_refresh_token', data.refresh_token);"
    js += "  }).catch(function(error){"
    js += "    console.log(error.response);"
    js += "  })"
    js += "}"
    
    tp.globals.assets.append({
      "type": "script",
      "content": js
    })
    
    return [
      {
        "type": "propCall",
        "calls": method_name,
        "args": ['\'' + user + '\'', '\''+ pwd +'\'']
      }
    ]

  def refreshToken(tp, *args, **kwargs):
    url = kwargs.get("url", "")
    method_name = kwargs.get("method_name", "refreshToken")
    client_id = kwargs.get("client_id", "")
    client_secret = kwargs.get("client_secret", "")
    user = kwargs.get("user", "")
    pwd = kwargs.get("pwd", "")
    url = kwargs.get("url", "")
    token = kwargs.get("token", "window.sessionStorage.getItem('nanohub_token')")
    js = ""
    js += "function " + method_name + "(token){"
    js += "  var data = '';"
    js += "  data = 'client_id="+client_id+"&';"
    js += "  data += 'client_secret="+client_secret+"&';"
    js += "  data += 'grant_type=refresh_token&';"
    js += "  data += 'refresh_token=' + token + '&';"
    js += "  var header_token = { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*' };"
    js += "  var options = { 'handleAs' : 'json' , 'headers' : header_token, 'method' : 'POST', 'data' : data };"
    js += "  var url = '" + url + "';"
    js += "  let self = this;"
    js += "  Axios.request(url, options)"
    js += "  .then(function(response){"
    js += "    var data = response.data;"
    js += "    window.sessionStorage.setItem('nanohub_token', data.token);"
    js += "    window.sessionStorage.setItem('nanohub_refresh_token', data.refresh_token);"
    js += "  }).catch(function(error){"
    js += "    console.log(error.response);"
    js += "  })"
    js += "}"
    
    tp.globals.assets.append({
      "type": "script",
      "content": js
    })
    
    return [
      {
        "type": "propCall",
        "calls": method_name,
        "args": [token]
      }
    ]    

    
  def buildSchema(tp, *args, **kwargs):
    url = kwargs.get("url", "")
    method_name = kwargs.get("method_name", "buildSchema")
    toolname = kwargs.get("toolname", "")
    url = kwargs.get("url", "https://nanohub.org/api/tools/")
    js = ""
    js += "async function " + method_name + "(toolname, parameters=[], forcelabels=true){"
    js += "  var header_token = { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*' };"
    js += "  var options = { 'handleAs' : 'xml' , 'headers' : header_token, 'method' : 'GET' };"
    js += "  var url = '" + url + "'+ toolname + '/rappturexml';"
    js += "  let self = this;"
    js += "  params = {};"    
    js += "  await Axios.request(url, options)"
    js += "  .then(function(response){"
    js += "    var data = response.data;" 
    js += "    var parser = new DOMParser();   "
    js += "    var periodicelement = ["
    js += "        ['Hydrogen','H'], ['Helium','He'], ['Lithium','Li'], ['Beryllium','Be'],"
    js += "        ['Boron','B'], ['Carbon','C'], ['Nitrogen','N'], ['Oxygen','O'],"
    js += "        ['Fluorine','F'], ['Neon','Ne'], ['Sodium','Na'], ['Magnesium','Mg'],"
    js += "        ['Aluminium','Al'], ['Silicon','Si'], ['Phosphorus','P'], ['Sulfur','S'],"
    js += "        ['Chlorine','Cl'], ['Argon','Ar'], ['Potassium','K'], ['Calcium','Ca'],"
    js += "        ['Scandium','Sc'], ['Titanium','Ti'], ['Vanadium','V'], ['Chromium','Cr'],"
    js += "        ['Manganese','Mn'], ['Iron','Fe'], ['Cobalt','Co'], ['Nickel','Ni'],"
    js += "        ['Copper','Cu'], ['Zinc','Zn'], ['Gallium','Ga'], ['Germanium','Ge'],"
    js += "        ['Arsenic','As'], ['Selenium','Se'], ['Bromine','Br'], ['Krypton','Kr'],"
    js += "        ['Rubidium','Rb'], ['Strontium','Sr'], ['Yttrium','Y'], ['Zirconium','Zr'],"
    js += "        ['Niobium','Nb'], ['Molybdenum','Mo'], ['Technetium','Tc'], ['Ruthenium','Ru'],"
    js += "        ['Rhodium','Rh'], ['Palladium','Pd'], ['Silver','Ag'], ['Cadmium','Cd'],"
    js += "        ['Indium','In'], ['Tin','Sn'], ['Antimony','Sb'], ['Tellurium','Te'],"
    js += "        ['Iodine','I'], ['Xenon','Xe'], ['Caesium','Cs'], ['Barium','Ba'],"
    js += "        ['Lanthanum','La'], ['Cerium','Ce'], ['Praseodymium','Pr'], ['Neodymium','Nd'],"
    js += "        ['Promethium','Pm'], ['Samarium','Sm'], ['Europium','Eu'], ['Gadolinium','Gd'],"
    js += "        ['Terbium','Tb'], ['Dysprosium','Dy'], ['Holmium','Ho'], ['Erbium','Er'],"
    js += "        ['Thulium','Tm'], ['Ytterbium','Yb'], ['Lutetium','Lu'], ['Hafnium','Hf'],"
    js += "        ['Tantalum','Ta'], ['Tungsten','W'], ['Rhenium','Re'], ['Osmium','Os'],"
    js += "        ['Iridium','Ir'], ['Platinum','Pt'], ['Gold','Au'], ['Mercury','Hg'],"
    js += "        ['Thallium','Tl'], ['Lead','Pb'], ['Bismuth','Bi'], ['Polonium','Po'],"
    js += "        ['Astatine','At'], ['Radon','Rn'], ['Francium','Fr'], ['Radium','Ra'],"
    js += "        ['Actinium','Ac'], ['Thorium','Th'], ['Protactinium','Pa'], ['Uranium','U'],"
    js += "        ['Neptunium','Np'], ['Plutonium','Pu'], ['Americium','Am'], ['Curium','Cm'],"
    js += "        ['Berkelium','Bk'], ['Californium','Cf'], ['Einsteinium','Es'], ['Fermium','Fm'],"
    js += "        ['Mendelevium','Md'], ['Nobelium','No'], ['Lawrencium','Lr'], ['Rutherfordium','Rf'],"
    js += "        ['Dubnium','Db'], ['Seaborgium','Sg'], ['Bohrium','Bh'], ['Hassium','Hs'],"
    js += "        ['Meitnerium','Mt']        "
    js += "    ];"
    js += "    if (window.DOMParser){"
    js += "        parser = new DOMParser();"
    js += "        xmlDoc = parser.parseFromString(data, 'text/xml');"
    js += "    } else {"
    js += "        xmlDoc = new ActiveXObject('Microsoft.XMLDOM');"
    js += "        xmlDoc.async = false;"
    js += "        xmlDoc.loadXML(data);"
    js += "    }"
    js += "    var input = xmlDoc.getElementsByTagName('input');"
    js += "    var inputs = input[0].getElementsByTagName('*');"
    js += "    var parameters = [];"
    js += "    var discardtags = ['phase', 'group', 'option', 'image', 'note'];"
    js += "    for (var i=0;i<inputs.length;i++){"
    js += "      var elem = inputs[i];"
    js += "      if (elem.hasAttribute('id')){"
    js += "        var id = elem.getAttribute('id');"
    js += "        if (!(id in params)){"
    js += "          var about = elem.getElementsByTagName('about');"
    js += "          var description = '';"
    js += "          var labelt = '';"
    js += "          if (about.length > 0){"
    js += "            var description = elem.getElementsByTagName('description');"
    js += "            if (description.length > 0){"
    js += "              description = description[0].innerHTML;"
    js += "            }"
    js += "            var label = about[0].getElementsByTagName('label');"
    js += "            if (label.length > 0){"
    js += "                labelt = label[0].innerHTML;"
    js += "            }"
    js += "          }"
    js += "          if (parameters.length == 0 || id in parameters){"
    js += "            if (!(discardtags.includes(elem.tagName))){"
    js += "              var param = {'type': elem.tagName, 'description' : description};"
    js += "              param['id'] = id;"
    js += "              param['label'] = labelt;"
    js += "              var units = elem.getElementsByTagName('units');"
    js += "              if (units.length > 0){"
    js += "                param['units'] = units[0].innerHTML;"
    js += "              }"
    js += "              var defaultv = elem.getElementsByTagName('default');"
    js += "              if (defaultv.length > 0){"
    js += "                param['default'] = defaultv[0].innerHTML;"
    js += "              }"
    js += "              var minv = elem.getElementsByTagName('min');"
    js += "              if (minv.length > 0){"
    js += "                param['min'] = minv[0].innerHTML;"
    js += "              }"
    js += "              var maxv = elem.getElementsByTagName('max');"
    js += "              if (maxv.length > 0){"
    js += "                param['max'] = maxv[0].innerHTML;"
    js += "              }"
    js += "              var currentv = elem.getElementsByTagName('current');"
    js += "              if (currentv.length > 0){"
    js += "                param['current'] = currentv[0].innerHTML;"
    js += "              }"
    js += "              var options = elem.getElementsByTagName('option');"
    js += "              var opt_list = [];"
    js += "              for (var j = 0;j<options.length;j++){"
    js += "                var option = options[j];"
    js += "                var lvalue = option.getElementsByTagName('value');"
    js += "                var opt_val = ['', ''];"
    js += "                if (lvalue.length>0){"
    js += "                  if (lvalue[0].innerHTML != ''){"
    js += "                    opt_val[0] = lvalue[0].innerHTML;"
    js += "                    opt_val[1] = lvalue[0].innerHTML;"
    js += "                  }"
    js += "                }"
    js += "                var labout = option.getElementsByTagName('about');"
    js += "                if (labout.length>0){"
    js += "                  llabel = labout[0].getElementsByTagName('label');"
    js += "                  if (llabel.length>0){"
    js += "                    if (llabel[0].innerHTML != ''){"
    js += "                      opt_val[0] = llabel[0].innerHTML;"
    js += "                      if (opt_val[1] == ''){"
    js += "                        opt_val[1] = llabel[0].innerHTML;"
    js += "                      }"
    js += "                    }"
    js += "                  }"
    js += "                }"
    js += "                opt_list.push(opt_val);"
    js += "              }"
    js += "              param['options'] = opt_list;"
    js += "              if (param['type'] == 'periodicelement'){"
    js += "                  param['type'] = 'choice';"
    js += "                  param['options'] = periodicelement;"
    js += "              }"
    js += "              if (param['options'].length > 0){"
    js += "                var tmparray = param['options'].filter(p => p[1] == param['default']);"
    js += "                if (tmparray.length == 0 ){"
    js += "                  param['default'] = param['options'][0][1];"
    js += "                }"
    js += "              }              "
    js += "              if (param['type'] == 'string'){"
    js += "                if (param['default'] && /\\r|\\n/.exec(param['default'].trim())){"
    js += "                  param['type'] = 'text';"
    js += "                }"
    js += "              }"
    js += "              if (forcelabels == false)"
    js += "                params[id] = param;"
    js += "              else if (about.length > 0 && label.length > 0)"
    js += "                params [id] = param;"
    js += "            }"
    js += "          }"
    js += "        }"
    js += "      }"
    js += "    }"
    js += "    window.sessionStorage.setItem('nanohub_tool_schema', params);"
    js += "  }).catch(function(error){"
    js += "    console.log(error.response);"
    js += "  });"
    js += "}"
    
    tp.globals.assets.append({
      "type": "script",
      "content": js
    })
    
    return [
      {
        "type": "propCall",
        "calls": method_name,
        "args": ["'"+toolname+"'"]
      }
    ]        
    

  def nanohubTool(tp, *args, **kwargs):
    toolname = kwargs.get("toolname", "")
    url = kwargs.get("url", "https://nanohub.org/api/tools/")
    NanohubUtils.buildSchema(tp, method_name="buildSchema", toolname=toolname, url=url );

    
    client_id = kwargs.get("client_id", "")
    client_secret = kwargs.get("client_secret", "")
    user = kwargs.get("user", "")
    pwd = kwargs.get("pwd", "")
    url_token = kwargs.get("url_token", "")
    NanohubUtils.validateCredentials(tp, method_name = "validateCredentials", client_id=client_id, client_secret=client_secret, url=url_token);
    
    js = ""
    #js += "validateCredentials('"+user+"', '"+pwd+"');"
    js += "buildSchema('"+toolname+"');" 
    
    tp.globals.assets.append({
      "type": "script",
      "content": js
    })
    
    return [
      {
        "type": "propCall",
        "calls": "validateCredentials",
        "args": ["'"+user+"'", "'"+pwd+"'"]
      },
      {
        "type": "propCall",
        "calls": "buildSchema",
        "args": ["'"+toolname+"'"]
      }
    ]        
    
class FormHelper():
  
  def Number(component, label, description, state, value=0, suffix="",*args, **kwargs):
    component.addStateVariable(state, {"type":"integer", "defaultValue": value})
    number = TeleportElement(TeleportContent(elementType="FormatCustomNumber"))
    variant = kwargs.get("variant", "outlined")
    number.content.attrs["variant"] = variant
    number.content.attrs["label"] = label
    number.content.attrs["fullWidth"] = True
    number.content.attrs["helperText"] = description
    number.content.attrs["suffix"] = suffix
    number.content.style = { 'margin': '10px 0px 10px 0px' }
    number.content.events["blur"] = [
      {
        "type": "stateChange",
        "modifies": state,
        "newState": "$e.target.value"
      },
    ]
    number.content.attrs["value"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": state
      }  
    }
    return number

  def Switch(component, label, description, state, value=0,*args, **kwargs):
    component.addStateVariable(state, {"type":"boolean", "defaultValue": value})
    switch = TeleportElement(MaterialContent(elementType="Switch"))
    #variant = kwargs.get("variant", "outlined")
    #switch.content.attrs["variant"] = variant
    switch.content.attrs["value"] = label
    #switch.content.style = { 'margin': '10px 0px 10px 0px' }
    switch.content.events["change"] = [
      {
        "type": "stateChange",
        "modifies": state,
        "newState": "$e.target.checked"
      },
    ]
    switch.content.attrs["checked"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": state
      }  
    }
    return switch

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
    component.addStateVariable(state, {"type":"string", "defaultValue": value})
    select = TeleportElement(MaterialContent(elementType="TextField"))
    variant = kwargs.get("variant", "outlined")
    select.content.attrs["variant"] = variant
    select.content.attrs["label"] = label
    select.content.attrs["select"] = True
    select.content.attrs["fullWidth"] = True
    select.content.attrs["helperText"] = description
    select.content.style = { 'margin': '10px 0px 10px 0px' }
    select.content.events["change"] = [
      {
        "type": "stateChange",
        "modifies": state,
        "newState": "$e.target.value"
      },
    ]
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

  
class PNToyBuilder():
  def PNToySettingsComponent(*args, **kwargs):
    PNToySettingsComponent = TeleportComponent("PNToySettingsComponent", TeleportElement(TeleportContent(elementType="container")))
    #BasePlotlyComponent.addStateVariable("parameters", {"type":"array", "defaultValue": []})
    PNToySettingsComponent.addStateVariable("selected_tab", {"type":"integer", "defaultValue": 0})
    PNToySettingsComponent.addStateVariable("materialp", {"type":"string", "defaultValue": "Si"})
    container = TeleportElement(TeleportContent(elementType="container"))

    AppBar = TeleportElement(MaterialContent(elementType="AppBar"))
    AppBar.content.attrs["position"] = "static"
    AppBar.content.attrs["color"] = "secondary"

    Tabs = TeleportElement(MaterialContent(elementType="Tabs"))
    Tabs.content.attrs["value"] = {
      "type": "dynamic", "content": {
        "referenceType": "state", "id": "selected_tab"
      }    
    }

    selected_tab_state = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "selected_tab"
      }    
    }    

    p_len = FormHelper.Number(
      PNToySettingsComponent, 
      "P-type length", 
      "Physical length of P-type material.", 
      "p_len", 
      "3",
      "nm"
    )
    p_node = FormHelper.Number(
      PNToySettingsComponent, 
      "P-type Nodes", 
      "Number of plotted points along the length of the P-type material. Increase number of nodes at high doping for better accuracy.", 
      "p_node",
      "60",
      ""
    )  
    
    i_len = FormHelper.Number( 
      PNToySettingsComponent,
      "Intrinsic Region length",
      "Physical length of the intrinsic region (zero doping).",
      "i_len",
      "0",
      "nm"
    )
    
    i_node = FormHelper.Number( 
      PNToySettingsComponent,
      "Intrinsic Nodes",
      "Number of plotted points along the length of the intrinsic (zero doping) region. Only valid when intrinsic region length is not zero.",
      "i_node",
      "0",
      ""
    )    

    n_len = FormHelper.Number( 
      PNToySettingsComponent,
      "N-type length",
      "Physical length of N-type material.",
      "n_len",
      "6",
      "nm"
    )    
    
    n_node = FormHelper.Number( 
      PNToySettingsComponent,
      "N-type Nodes",
      "Number of plotted points along the length of the N-type material. Increase number of nodes at high doping for better accuracy.",
      "n_node",
      "120",
      ""
    )
    
    Na = FormHelper.Number( 
      PNToySettingsComponent,
      "Acceptor concentration (Na-)",
      "",
      "Na",
      "2000000000000000",
      "/cm3"
    )
    
    Nd = FormHelper.Number( 
      PNToySettingsComponent,
      "Donor concentration (Nd+)",
      "",
      "Nd",
      "1000000000000000",
      "/cm3"
    )
    
    parameters_structure = TeleportConditional(TeleportContent(elementType="container"))    
    parameters_structure.reference = selected_tab_state
    parameters_structure.value = 0
    parameters_structure.node.content.style = { 'margin': '15px' }    
    parameters_structure.addContent(FormHelper.Header("Structure"))    
    parameters_structure.addContent(p_len)
    parameters_structure.addContent(p_node)
    parameters_structure.addContent(i_len)
    parameters_structure.addContent(i_node)
    parameters_structure.addContent(n_len)
    parameters_structure.addContent(n_node)    
    parameters_structure.addContent(Na)
    parameters_structure.addContent(Nd)

    parameters_structure_tab = TeleportElement(MaterialContent(elementType="Tab"))
    parameters_structure_tab.content.attrs["label"] = "Structure"
    parameters_structure_tab.content.events["click"] = [
      {
        "type": "stateChange",
        "modifies": "selected_tab",
        "newState": 0
      },
    ]


    materialp = FormHelper.Select( 
      PNToySettingsComponent,
      "Material",
      "Set the type of material used for the entire region.",
      "materialp",
      "Si",
      {"GaAs":"GaAs", "Ge":"Ge", "Si":"Si", "InP":"InP", }
    )    
    
    taun = FormHelper.Number( 
      PNToySettingsComponent,
      "For electrons",
      "This is the minority carrier lifetime for electrons. It represents the average time that an electron will diffuse in p-type material before recombining with a hole.",
      "taun",
      "0.0000000001",
      "s"
    )
    taup = FormHelper.Number( 
      PNToySettingsComponent,
      "For holes",
      "This is the minority carrier lifetime for holes. It represents the average time that a hole will diffuse in n-type material before recombining with an electron.",
      "taup",
      "0.0000000001",
      "s"
    )

    impurity = FormHelper.Switch( 
      PNToySettingsComponent,
      "Impurity doping in Intrinsic region.",
      "Here you define if any impurity doping level exists in the intrinsic region.",
      "impurity",
      True,
    )
    
    impurity_state = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "impurity"
      }    
    }    
    impurity_conditional = TeleportConditional(TeleportContent(elementType="container"))
    impurity_conditional.reference = impurity_state
    impurity_conditional.value = 1
    
    impuritydoping = FormHelper.Select( 
      PNToySettingsComponent,
      "Type of doping",
      "Here you define type of doping for in the intrinsic region",
      "impuritydoping",
      "Ptype",
      {"Ntype":"N-type", "Ptype":"P-type" }
    )    
    impuritylevel = FormHelper.Number( 
      PNToySettingsComponent,
      "Doping level",
      "Unintentional doping in the intrinsic region.",
      "impuritylevel",
      "10000000000000",
      "/cm3"
    )
    impurity_conditional.addContent(impuritydoping)
    impurity_conditional.addContent(impuritylevel)

    parameters_materials = TeleportConditional(TeleportContent(elementType="container"))
    parameters_materials.reference = selected_tab_state
    parameters_materials.value = 1
    parameters_materials.addContent(FormHelper.Header("Materials"))
    parameters_materials.addContent(materialp)
    parameters_materials.addContent(FormHelper.Header("Minority carrier lifetime"))
    parameters_materials.addContent(taun)
    parameters_materials.addContent(taup)
    parameters_materials.addContent(FormHelper.Header("Impurities"))
    parameters_materials.addContent(impurity)
    parameters_materials.addContent(impurity_conditional)
    parameters_materials.node.content.style = { 'margin': '15px' }

    parameters_materials_tab = TeleportElement(MaterialContent(elementType="Tab"))
    parameters_materials_tab.content.attrs["label"] = "Materials"
    parameters_materials_tab.content.events["click"] = [
      {
        "type": "stateChange",
        "modifies": "selected_tab",
        "newState": 1
      },
    ]
    
    temperature = FormHelper.Number( 
      PNToySettingsComponent,
      "Ambient temperature",
      "This is the temperature in the environment around the device.",
      "temperature",
      "300",
      "K"
    )

    vsweep_high = FormHelper.Number( 
      PNToySettingsComponent,
      "Applied Voltage",
      "Set an applied voltage across the PIN Junction. For IV characteristics, the voltage will sweep from 0V (ground) to the applied voltage.",
      "vsweep_high",
      "0.6",
      "V"
    )

    vn_step = FormHelper.Number( 
      PNToySettingsComponent,
      "Number of points",
      "Set the number data points sampled in the voltage sweep",
      "vn_step",
      "20",
      ""
    )
    
    parameters_ambient = TeleportConditional(TeleportContent(elementType="container"))
    parameters_ambient.reference = selected_tab_state
    parameters_ambient.value = 2
    parameters_ambient.addContent(FormHelper.Header("Ambient"))
    parameters_ambient.addContent(temperature)
    parameters_ambient.addContent(vsweep_high)
    parameters_ambient.addContent(vn_step)
    parameters_ambient.node.content.style = { 'margin': '15px' }

    parameters_ambient_tab = TeleportElement(MaterialContent(elementType="Tab"))  
    parameters_ambient_tab.content.attrs["label"] = "Ambient"
    parameters_ambient_tab.content.events["click"] = [
      {
        "type": "stateChange",
        "modifies": "selected_tab",
        "newState": 2
      },
    ]    
    
    PNToySettingsComponent.node.content.style = {
      "height": "100vh"
    }    
    Tabs.addContent(parameters_structure_tab)
    Tabs.addContent(parameters_materials_tab)
    Tabs.addContent(parameters_ambient_tab)
    AppBar.addContent(Tabs)
    container.addContent(AppBar)
    container.addContent(parameters_structure)
    container.addContent(parameters_materials)
    container.addContent(parameters_ambient)
    PNToySettingsComponent.addNode(container)
    return PNToySettingsComponent    
    
  def PNToySettings(tp, *args, **kwargs):
    if ("PNToySettingsComponent" not in tp.components):
      tp.components["PNToySettingsComponent"] = PNToyBuilder.PNToySettingsComponent()  
      js = ""
      js += "class FormatCustomNumber extends React.Component {"
      js += "  constructor(props) {"
      js += "    super(props);"
      js += "  }"
      js += "  formatter(props){"
      js += "    return (value => {"
      js += "      const { inputRef, ...other } = value;"
      js += "      return React.createElement(Format,{...props,...other});"
      js += "    })"
      js += "  }"
      js += "  render() {"
      js += "    var props = {'InputProps':{'inputComponent':this.formatter(), 'endAdornment':this.props['suffix']},'InputLabelProps':{'shrink':true},'type':'number'};"
      js += "    props ={...props, ...this.props};"
      js += "    return React.createElement(Material.TextField,props);"
      js += "  }"
      js += "}"
      tp.globals.assets.append({
        "type": "script",
        "content": js
      })      


      
    ContainerPlot = TeleportElement(TeleportContent(elementType="container"))
    ContainerPlot.content.style = {
      "height": "100vh"
    }
        
    PNToySettings = TeleportElement(TeleportContent(elementType="PNToySettingsComponent"))
    if kwargs.get("data", None) is not None:
      PNToySettings.content.attrs["data"] = kwargs.get("data", None)

    if kwargs.get("ref", None) is not None:
      PNToySettings.content.attrs["ref"] = kwargs.get("ref", None)
      
    if kwargs.get("style_state", None) is not None:
      ContainerPlot.content.attrs["className"] = {
        "type": "dynamic",
        "content": {
          "referenceType": "state",
          "id": kwargs.get("style_state")
        }    
      }
    
    ContainerPlot.addContent(PNToySettings)
    return ContainerPlot