import json 
import requests
import jsonschema


class TeleportGlobals():
    def __init__(self, *args, **kwargs):
        self.settings = {'language' : 'en', 'title' : ''}
        self.assets = []
        self.meta = []
        self.manifest = {}
        self.ids = {}
        
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
      
    def addAsset(self, id, asset):
      if id in self.ids:
        pass;
      else:
        self.ids[id] = len(self.ids)
        self.assets.append(asset)
      
        
'''class TeleportApp():
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
'''

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
        react += " '" + str(self.content).replace("'", "\"") + "' "
      elif self.type == "dynamic":
        if ("referenceType" in self.content and self.content["referenceType"] == "state"):
          reference = "self.state." + self.content["id"] + "";
        elif ("referenceType" in self.content and self.content["referenceType"] == "prop"):
          reference = "self.props." + self.content["id"] + "";
        elif ("referenceType" in self.content and self.content["referenceType"] == "local"):
          reference = "" + self.content["id"] + "";
        #elif ("referenceType" in self.content and self.content["referenceType"] == "attr"):
        #  reference = "" + content["id"] + "";
        else:
          reference = "";
        react += " " + str(reference) + " "
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
    self.value = kwargs.get("value", None)
    self.conditions = kwargs.get("conditions", [])
    self.matchingCriteria = kwargs.get("matchingCriteria", "all")

  def addContent(self, child):
    self.node.addContent(child)

  def buildReact(self):  
    value = self.reference
    content = value["content"]
    try:
      if (value["type"] == "dynamic"):
        if ("referenceType" in content and content["referenceType"] == "state"):
          reference = "self.state." + content["id"] + "";
        elif ("referenceType" in content and content["referenceType"] == "prop"):
          reference = "self.props." + content["id"] + "";
        elif ("referenceType" in content and content["referenceType"] == "local"):
          reference = "" + content["id"] + "";
      elif (value["type"] == "static"):
        reference = content
    except:
      reference = self.reference
      
    react = ""
    react += "(("
    if (len(self.conditions) ==0):
        react += "( " + str(reference) + " == " + json.dumps(self.value) +")"
    else:
        for i, condition in enumerate(self.conditions):  
            if ("operand" in condition):
                react += "( " + str(reference) + " " + str(condition["operation"]) + " " + json.dumps(condition["operand"]) +")"
            elif self.value is not None:
                react += "( " + str(reference) + " " + str(condition["operation"]) + " " + json.dumps(self.value) +")"
            if i > 0:
                if self.matchingCriteria == "one":
                     react += " || "
                else:
                     react += " && "
    react += ") ?"
    react += self.node.buildReact()
    react += " : null)"
    return react

  def __json__(self):
    return {
      "type": self.type,
      "content" : { 
        "node" : self.node.__json__(),
        "reference" : self.reference, 
        "value" : self.value, 
        "condition": {
            "conditions" : self.conditions,
            "matchingCriteria": self.matchingCriteria
        },
      }
    }
    
class TeleportDynamic(TeleportNode):
  def __init__(self, *args, **kwargs):
    TeleportNode.__init__(self)
    self.type = "dynamic"      
    self.content = kwargs.get("content", {})

  def __json__(self):
    return {
      "type": self.type,
      "content" : self.content,
    }    


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
      if ("type" in definition and definition["type"] == "func"):
        if "defaultValue" not in definition:
            definition["defaultValue"] = "() => {}"
        self.propDefinitions[state] =  { "type": definition["type"], "defaultValue": definition["defaultValue"] }
      elif ("type" in definition and "defaultValue" in definition):
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
    react += "let self=this;\n"
    react += "this.state = {\n"
    for k,s in self.stateDefinitions.items():
      v = s['defaultValue']
      if isinstance(v,dict) and "type" in v and v["type"] == "dynamic":
        if ("content" in v):
          content = v["content"]
          if ("referenceType" in content and content["referenceType"] == "state"):
            raise Exception("state circular references")
          elif ("referenceType" in content and content["referenceType"] == "prop"):
            v = "self.props." + content["id"] + "";
          elif ("referenceType" in content and content["referenceType"] == "local"):
            v = "" + content["id"] + "";
      elif "type" in s: 
        if (s["type"] == "object"):
          v = str(json.dumps(v))    
        elif (s["type"] == "string"):
          v = str(json.dumps(str(v))) 
        elif (s["type"] == "boolean"):
          v = str(json.dumps(bool(v)))    
        elif (s["type"] == "number"):
          v = str(float(v))   
        elif (s["type"] == "func"):
          v = str(v)    
        elif (s["type"] == "array"):
          v = str(json.dumps(list(v)))    
        elif (s["type"] == "router"):
          v = None   
        else:
          v = str(json.dumps(v)) 
      else:
          v = str(json.dumps(v)) 
      react += "'" + str(k) + "' : " + v + ", \n"
    react += "};\n"
    react += "}; \n"
    react += "render(){\n"
    react += "let self=this;\n"
    react += "return " + self.node.buildReact() + ";\n"
    react += "}\n"
    react += "}\n"
    react += componentName + ".defaultProps = {\n"
    for k,s in self.propDefinitions.items():
      if ("type" in s and s["type"] == "func"):
          if ("defaultValue" in s):
              react += "'" + str(k) + "' : " + (s['defaultValue']) + ", \n"
          else:
              react += "'" + str(k) + "' : ()=>{}, \n"
      else:
          if ("defaultValue" in s):
              react += "'" + str(k) + "' : " + json.dumps(s['defaultValue']) + ",\n"
    react += "}\n"
    return react

class TeleportProject():
  def __init__(self, name, *args, **kwargs):
      self.project_name = name
      self.globals = TeleportGlobals();
      self.root = TeleportComponent("MainComponent", TeleportElement(TeleportContent(elementType="container")));
      self.components = {};
      #self.components["MainComponent"].node.content.style = {
      #  "height": "100vh",
      #}
      
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

  def buildReact(self, filename="tempreact.html"):
    react = ""
    react += "<!DOCTYPE html>\n"
    react += "<html style='height:100%'>\n"
    react += "<head>\n"
    react += "<meta charset='UTF-8'/>\n"
    react += "<title>" + self.project_name + "</title>\n"
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
    react += "        'plotlycomponent': 'https://unpkg.com/react-plotly.js@2.3/dist/create-plotly-component',\n"
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
    react += "    const Plot = PlotlyComponent.default(Plotly);\n";
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
    react += self.root.buildReact(self.root.name_component)
    for k, v in self.components.items():
      react += v.buildReact(k)
    react += "    ReactDOM.render(\n"
    react += "        React.createElement(" + self.root.name_component + ", {key:Util.create_UUID()}),\n"
    react += "        document.getElementById('root')\n"
    react += "    );\n"
    react += "  })    \n"
    react += "})    \n"
    react += "</script>\n"
    react += "  </body>\n"
    react += "</html>\n"
    f = open(filename, "w")
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
  
  def parseFunctionsList(list):
    v = ""
    for func in list:      
      if "type" in func and func["type"] == "stateChange":
        if (isinstance(func["newState"], str) and func["newState"] == "$toggle"):
          v += "self.setState({'" + str(func["modifies"]) + "': !self.state." + str(func["modifies"]) + "}); "
        elif (isinstance(func["newState"], str) and func["newState"].startswith("$")):
          v += "self.setState({'" + str(func["modifies"]) + "':" + func["newState"].replace("$","") + "}); "
        else:
          v += "self.setState({'" + str(func["modifies"]) + "':" + json.dumps(func["newState"]) + "}); "
      elif "type" in func and func["type"] == "logging":
        v += "console.log('" + str(func["modifies"]) + "', " + str(json.dumps(func["newState"])) + "); "
      elif "type" in func and func["type"] == "propCall":
        v += str(func["calls"]) + "(" + ", ".join(func["args"]) + ");"
      elif "type" in func and func["type"] == "propCall2":
        v += "self.props." + str(func["calls"]) + "(" + ", ".join(func["args"]) + ");"
    return v

    
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
              v = "self.state." + content["id"] + "";
            elif ("referenceType" in content and content["referenceType"] == "prop"):
              v = "self.props." + content["id"] + "";
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
      event_rename = ev
      if ev in valid_events:
        event_rename = valid_events[ev]
      v = "function(e){"
      v += "  " + TeleportContent.parseFunctionsList(list) + "\n"
      v += "}"
      if v != "function(){}": 
        react += sep + "'"+ event_rename + "': " + v + ""
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
    IconText = TeleportStatic(content="unfold_more")
    Icon.addContent(IconText)   
    IconButton.addContent(Icon)
    
    
    Typography = TeleportElement(MaterialContent(elementType="Typography"))
    Typography.content.attrs["variant"] = "h6"
    Typography.content.style={'flex':1, 'textAlign':'center'}
    TypographyText = TeleportStatic(content=kwargs.get("title", ""))
    Typography.addContent(TypographyText)

    if kwargs.get("state", None) is not None:
      states = {0:"unfold_more", 1:"unfold_less"}
      for k,v in states.items():
        IconButton = TeleportElement(MaterialContent(elementType="IconButton"))
        IconButton.content.attrs["edge"] = "start"
        IconButton.content.attrs["color"] = "inherit"
        IconButton.content.attrs["aria-label"] = "menu"
        IconButton.content.events["click"] = [
          {
            "type": "stateChange",
            "modifies": kwargs.get("state", None),
            "newState": (k==0)
          },
        ]
        if kwargs.get("styles", None) is not None:
          styles = kwargs.get("styles", None)
          IconButton.content.events["click"].append({
            "type": "stateChange",
            "modifies": styles[0],
            "newState": styles[1][k]
          })
        
        Icon = TeleportElement(MaterialContent(elementType="Icon"))
        IconText = TeleportStatic(content=v)
        Icon.addContent(IconText)   
        IconButton.addContent(Icon)
        IconButtonCondition = TeleportConditional(TeleportContent(elementType="container"))    
        IconButtonCondition.reference = {
          "type": "dynamic",
          "content": {
            "referenceType": "state",
            "id": kwargs.get("state", None)
          }    
        }
        IconButtonCondition.value = k
        IconButtonCondition.addContent(IconButton)
        ToolBar.addContent(IconButtonCondition)
    else:
      IconButton = TeleportElement(MaterialContent(elementType="IconButton"))
      IconButton.content.attrs["edge"] = "start"
      IconButton.content.attrs["color"] = "inherit"
      IconButton.content.attrs["aria-label"] = "menu"
      if kwargs.get("onClickMenu", None) is not None:
        IconButton.content.events["click"] = kwargs.get("onClickMenu", [])
      Icon = TeleportElement(MaterialContent(elementType="Icon"))
      IconText = TeleportStatic(content="unfold_more")
      Icon.addContent(IconText)   
      IconButton.addContent(Icon)
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
    if "onClickClose" in kwargs:
      ListItem = TeleportElement(MaterialContent(elementType="ListItem"))
      ListItem.content.attrs["button"] = True
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


  def ExpansionPanel(*args, **kwargs):
    """This function creates a Material Element of type ExpansionPanel.
    Kwargs:

    
    Returns:
      TeleportElement

    Raises:
       AttributeError

    >>> ExpansionPanel(state="DrawerIsVisible", position="static", "variant":"dense" )

    """  
    ExpansionPanel = TeleportElement(MaterialContent(elementType="ExpansionPanel"))
    if kwargs.get("disabled", False) is True:
        ExpansionPanel.content.attrs["disabled"] = True
    if kwargs.get("expanded", None) is not None:
        ExpansionPanel.content.attrs["expanded"] = kwargs.get("expanded", False)
    if kwargs.get("defaultExpanded", None) is not None:
        ExpansionPanel.content.attrs["defaultExpanded"] = kwargs.get("defaultExpanded", True)
    ExpansionPanelSummary = TeleportElement(MaterialContent(elementType="ExpansionPanelSummary"))
    ExpansionPanelSummary.content.attrs["expandIcon"] = "expand_more"
    ExpansionPanelSummary.content.attrs["aria-controls"] = kwargs.get("aria-controls", "panel1a-content")
    ExpansionPanelSummary.content.attrs["id"] = kwargs.get("id", kwargs.get("title", ""))
    ExpansionPanelDetails = TeleportElement(MaterialContent(elementType="ExpansionPanelDetails"))
    if kwargs.get("content", None) is not None:
        for content in kwargs.get("content", []):
            ExpansionPanelDetails.addContent(content)
    if kwargs.get("title", None) is not None:
        Typography = TeleportElement(MaterialContent(elementType="Typography"))
        TypographyText = TeleportStatic(content=kwargs.get("title", ""))
        Typography.addContent(TypographyText)
        ExpansionPanelSummary.addContent(Typography) ;

    ExpansionPanel.addContent(ExpansionPanelSummary)
    ExpansionPanel.addContent(ExpansionPanelDetails)
    return ExpansionPanel

  def GridItem(*args, **kwargs):
    Grid = TeleportElement(MaterialContent(elementType="Grid"))
    Grid.content.attrs["item"] = True
    #Grid.content.attrs["alignContent"] = "center"
    if ("content" in kwargs):
      Grid.addContent(kwargs.get("content"))
    return Grid
    
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

    Button = TeleportElement(MaterialContent(elementType="Button"))
    Button.content.attrs["size"] = kwargs.get("size", "medium")
    Button.content.attrs["variant"] = kwargs.get("variant", "contained")
    Button.content.attrs["color"] = kwargs.get("color", "primary")
    Button.content.attrs["disableRipple"] = kwargs.get("disableRipple", False)
    if ("className" in kwargs):
      Button.content.attrs["className"] = kwargs.get("className")
    if ("style" in kwargs):
      Button.content.style = kwargs.get("style")
      
    if kwargs.get("onClickButton", None) is not None:
      Button.content.events["click"] = kwargs.get("onClickButton")
    Typography = TeleportElement(MaterialContent(elementType="Typography"))

    Typography.addContent(TeleportStatic(content=kwargs.get("title", "")))
    Button.addContent(Typography)
    return Button

  
  '''def ThemeProvider(theme_var):      
    ThemeProvider = TeleportElement(MaterialContent(elementType="ThemeProvider"))
    ThemeProvider.content.attrs["theme"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "local",
        "id": theme_var
      }
    }
    return ThemeProvider'''

  def DefaultTheme():  
    return {
      'shadows': ["none" for i in range(25) ],
      'palette': {
        'primary': {
          'main': '#699FBB',
        },
        'secondary': {
          'main': '#f1f1f1',
        },
      },
      'overrides': {
        'MuiFab': {
          'root': { 'border': '2px solid #CCCCCC' },
        },
        'MuiGrid' : {
          'item' : { 'display' : 'flex', 'flex-direction' : 'column', 'padding': '4px' }
        },
        'MuiDrawer' : {
          'paper' : {
            'width' : '350px',
            'top' : '80px',
            'height' : 'calc(100vh - 80px)'
          }
        },
        'MuiAppBar' : {
          'colorPrimary': {
            'backgroundColor':'#FFFFFF'
          },
          'colorSecondary': {
            'backgroundColor':'#B5BEFD'
          },
        },
        'MuiButton' : {

            'root' : {
                'text-transform' : 'none'
            },
            'containedPrimary':{
                'color' : 'rgba(255, 255, 255, 0.87)'            
            },
            'containedSecondary':{
                'color' : 'rgba(0, 0, 0, 0.87)'            
            }
        },
        'MuiGrid' : {
          'item' : {
            'padding': '4px 25px',
            'margin': '0',
            'display': 'flex',
            'box-sizing': 'border-box',
            'flex-direction': 'column',
          }
        },
        'MuiExpansionPanelSummary':{
          'expandIcon' : {
              'font-family': 'Material Icons'
          },
          'content' : {
            'margin': '2px',
            '&$expanded': {
              'margin': '2px 0',
            },
          },        
          'root' : {
            'background-color' : '#dbeaf0',
            'minHeight': 40,
            '&$expanded': {
              'minHeight': 40,
            },
          }
        },
        'MuiExpansionPanel':{
          'root' : {
            '&$expanded' : {
              'margin': '0px'
            },
          },
        },
        'MuiTypography': {
          'body1': {
            'font-size': '0.9rem'
          }
        },
        'MuiInputBase' : {
          'root': {
            'font-size': '0.9rem'
          }
        }, 
        'MuiIconButton' : { 
          'root' : {
              'padding': '10px'
          }
        },
        'MuiOutlinedInput' : {
          'input' : {
            'padding' : '10px 10px'
          }
        }
      },  
    }

  def ThemeProvider(Component, theme):  
    Component.addPropVariable("createMuiTheme", {
        "type":"func", 
        "defaultValue": "() => {return Material.createMuiTheme(" + json.dumps(theme) + ");}"
    })
    ThemeProvider = TeleportElement(MaterialContent(elementType="ThemeProvider"))
    ThemeProvider.content.attrs["theme"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "prop",
        "id": 'createMuiTheme()'
      }
    }
    return ThemeProvider

    
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
    return BasePlotlyComponent    
  
  def BasePlot(tp, Component,  *args, **kwargs):
    if ("BasePlotlyComponent" not in tp.components):
      tp.components["BasePlotlyComponent"] = PlotlyBuilder.BasePlotlyComponent()  
    Component.addStateVariable("data", {"type":"array", "defaultValue": [{'x': [], 'y': []}]})    
    Component.addStateVariable("layout", {"type":"object", "defaultValue": {}})
    Component.addStateVariable("frames", {"type":"array", "defaultValue": []})        
    ContainerPlot = TeleportElement(TeleportContent(elementType="container"))
        
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
      
    if kwargs.get("style_state", None) is not None:
      ContainerPlot.content.attrs["className"] = {
        "type": "dynamic",
        "content": {
          "referenceType": "state",
          "id": kwargs.get("style_state")
        }    
      }
    
    ContainerPlot.content.style = {
      "height": "inherit",
    }
    ContainerPlot.addContent(BasePlot)
    return ContainerPlot

class NanohubUtils():
  def storageFactory(tp, *args, **kwargs):
    method_name = kwargs.get("method_name", "storageFactory")
    storage_name = kwargs.get("storage_name", "window.sessionStorage")
    store_name = kwargs.get("store_name", "sessionStore")
    eol = "\n";    
    js = ""
    js += "function " + method_name + "(getStorage){" + eol;
    js += "  /* ISC License (ISC). Copyright 2017 Michal Zalecki */" + eol;
    js += "  let inMemoryStorage = {};" + eol;
    js += "  function isSupported() {" + eol;
    js += "    try {" + eol;
    js += "      const testKey = '__some_random_key_you_are_not_going_to_use__';" + eol;
    js += "      getStorage().setItem(testKey, testKey);" + eol;
    js += "      getStorage().removeItem(testKey);" + eol;
    js += "      return true;" + eol;
    js += "    } catch (e) {" + eol;
    js += "      return false;" + eol;
    js += "    }" + eol;
    js += "  }" + eol;
    js += "  function clear(){" + eol;
    js += "    if (isSupported()) {" + eol;
    js += "      getStorage().clear();" + eol;
    js += "    } else {" + eol;
    js += "      inMemoryStorage = {};" + eol;
    js += "    }" + eol;
    js += "  }" + eol;
    js += "  function getItem(name){" + eol;
    js += "    if (isSupported()) {" + eol;
    js += "      return getStorage().getItem(name);" + eol;
    js += "    }" + eol;
    js += "    if (inMemoryStorage.hasOwnProperty(name)) {" + eol;
    js += "      return inMemoryStorage[name];" + eol;
    js += "    }" + eol;
    js += "    return null;" + eol;
    js += "  }" + eol;

    js += "  function key(index){" + eol;
    js += "    if (isSupported()) {" + eol;
    js += "      return getStorage().key(index);" + eol;
    js += "    } else {" + eol;
    js += "      return Object.keys(inMemoryStorage)[index] || null;" + eol;
    js += "    }" + eol;
    js += "  }" + eol;

    js += "  function removeItem(name){" + eol;
    js += "    if (isSupported()) {" + eol;
    js += "      getStorage().removeItem(name);" + eol;
    js += "    } else {" + eol;
    js += "      delete inMemoryStorage[name];" + eol;
    js += "    }" + eol;
    js += "  }" + eol;

    js += "  function setItem(name, value){" + eol;
    js += "    if (isSupported()) {" + eol;
    js += "      getStorage().setItem(name, value);" + eol;
    js += "    } else {" + eol;
    js += "      inMemoryStorage[name] = String(value);" + eol;
    js += "    }" + eol;
    js += "  }" + eol;

    js += "  function length(){" + eol;
    js += "    if (isSupported()) {" + eol;
    js += "      return getStorage().length;" + eol;
    js += "    } else {" + eol;
    js += "      return Object.keys(inMemoryStorage).length;" + eol;
    js += "    }" + eol;
    js += "  }" + eol;

    js += "  return {" + eol;
    js += "    getItem," + eol;
    js += "    setItem," + eol;
    js += "    removeItem," + eol;
    js += "    clear," + eol;
    js += "    key," + eol;
    js += "    get length() {" + eol;
    js += "      return length();" + eol;
    js += "    }," + eol;
    js += "  };" + eol;
    js += "};" + eol;
    js += "const " + store_name + " = storageFactory(() => " + storage_name + ");" + eol;

    tp.globals.addAsset(method_name, {
      "type": "script",
      "content": js
    })    
    
    return [
      {
        "type": "propCall",
        "calls": method_name,
        "args": []
      }
    ]

  def validateCredentials(tp, *args, **kwargs):
    store_name="sessionStore";
    NanohubUtils.storageFactory(tp, store_name=store_name)
    method_name = kwargs.get("method_name", "validateCredentials")
    client_id = kwargs.get("client_id", "")
    client_secret = kwargs.get("client_secret", "")
    user = kwargs.get("user", "")
    pwd = kwargs.get("pwd", "")
    url = kwargs.get("url", "")
    js = ""
    js += "function " + method_name + "(user, pwd){\n"
    js += "  var data = '';\n"
    js += "  data = 'client_id="+client_id+"&';\n"
    js += "  data += 'client_secret="+client_secret+"&';\n"
    js += "  data += 'grant_type=password&';\n"
    js += "  data += 'username=' + user + '&';\n"
    js += "  data += 'password=' + pwd + '&';\n"
    js += "  var header_token = { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*' };\n"
    js += "  var options = { 'handleAs' : 'json' , 'headers' : header_token, 'method' : 'POST', 'data' : data };\n"
    js += "  var url = '" + url + "';\n"
    js += "  var expiration = " + store_name + ".getItem('nanohub_expires');\n"
    js += "  var current_time = Date.now()\n";
    #js += "  console.log (expiration, current_time);\n"
    js += "  if (expiration === null || current_time > expiration){\n";
    js += "    let self = this;\n"
    js += "    Axios.request(url, options)\n"
    js += "    .then(function(response){\n"
    js += "      var data = response.data;\n"
    js += "      " + store_name + ".setItem('nanohub_token', String(data.access_token));\n"
    js += "      " + store_name + ".setItem('nanohub_expires', JSON.stringify(Date.now() + parseInt(data.expires_in) - 200));\n"
    js += "      " + store_name + ".setItem('nanohub_refresh_token', String(data.refresh_token));\n"
    js += "    }).catch(function(error){\n"
    js += "      " + store_name + ".removeItem('nanohub_token');\n"
    js += "      " + store_name + ".removeItem('nanohub_expires');\n"
    js += "      " + store_name + ".removeItem('nanohub_refresh_token');\n"
    js += "    })"
    js += "  }"
    js += "}"
    
    tp.globals.addAsset(method_name, {
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

  def validateSession(tp, *args, **kwargs):
    store_name="sessionStore";
    NanohubUtils.storageFactory(tp, store_name=store_name)
    method_name = kwargs.get("method_name", "validateSession")
    sessiontoken = kwargs.get("sessiontoken", "")
    sessionnum = kwargs.get("sessionnum", "")
    url = kwargs.get("url", "")
    js = ""
    js += "function " + method_name + "(sessiontoken, sessionnum){\n"
    js += "  var data = '';\n"
    js += "  data = 'sessiontoken=' + sessiontoken + '&';\n"
    js += "  data += 'sessionnum=' + sessionnum + '&';\n"
    js += "  data += 'grant_type=tool&';\n"
    js += "  var header_token = { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*' };\n"
    js += "  var options = { 'handleAs' : 'json' , 'headers' : header_token, 'method' : 'POST', 'data' : data };\n"
    js += "  var url = '" + url + "';\n"
    js += "  var expiration = " + store_name + ".getItem('nanohub_expires');\n"
    js += "  var current_time = Date.now()\n";
    #js += "  console.log (expiration, current_time);\n"
    js += "  if (expiration === null || current_time > expiration){\n";
    js += "    let self = this;\n"
    js += "    Axios.request(url, options)\n"
    js += "    .then(function(response){\n"
    js += "      var data = response.data;\n"
    js += "      " + store_name + ".setItem('nanohub_token', String(data.access_token));\n"
    js += "      " + store_name + ".setItem('nanohub_expires', JSON.stringify(Date.now() + parseInt(data.expires_in) - 200));\n"
    js += "      " + store_name + ".setItem('nanohub_refresh_token', String(data.refresh_token));\n"
    js += "    }).catch(function(error){\n"
    js += "      " + store_name + ".removeItem('nanohub_token');\n"
    js += "      " + store_name + ".removeItem('nanohub_expires');\n"
    js += "      " + store_name + ".removeItem('nanohub_refresh_token');\n"
    js += "    })"
    js += "  }"
    js += "}"
    
    tp.globals.addAsset(method_name, {
      "type": "script",
      "content": js
    })
    
    return [
      {
        "type": "propCall",
        "calls": method_name,
        "args": ['\'' + sessiontoken + '\'', '\''+ sessionnum +'\'']
      }
    ]

  def refreshToken(tp, *args, **kwargs):
    store_name="sessionStore";
    NanohubUtils.storageFactory(tp, store_name=store_name)
    url = kwargs.get("url", "")
    method_name = kwargs.get("method_name", "refreshToken")
    client_id = kwargs.get("client_id", "")
    client_secret = kwargs.get("client_secret", "")
    user = kwargs.get("user", "")
    pwd = kwargs.get("pwd", "")
    url = kwargs.get("url", "")
    token = kwargs.get("token", store_name + ".getItem('nanohub_token')")
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
    js += "    " + store_name + ".setItem('nanohub_token', JSON.stringify(data.token));"
    js += "    " + store_name + ".setItem('nanohub_refresh_token', JSON.stringify(data.refresh_token));"
    js += "  }).catch(function(error){"
    js += "    console.log(error.response);"
    js += "  })"
    js += "}"
    
    tp.globals.addAsset(method_name, {
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
    store_name="sessionStore";
    NanohubUtils.storageFactory(tp, store_name=store_name)
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
    js += "              }"
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
    js += "    " + store_name + ".setItem('nanohub_tool_schema', JSON.stringify(params));"
    js += "    " + store_name + ".setItem('nanohub_tool_xml', JSON.stringify(data));"
    js += "  }).catch(function(error){"
    js += "    console.log(error.response);"
    js += "  });"
    js += "}"
    
    tp.globals.addAsset(method_name, {
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
    sessiontoken = kwargs.get("sessiontoken", None)
    sessionnum = kwargs.get("sessionnum", None)
    validateMethod = "validateCredentials"
    paramer1 = user
    paramer2 = pwd
    if (sessiontoken == None or sessionnum == None ):
        NanohubUtils.validateCredentials(tp, method_name = validateMethod, client_id=client_id, client_secret=client_secret, url=url_token);    
        js = ""
        js += "validateCredentials('"+user+"', '"+pwd+"');"
        js += "buildSchema('"+toolname+"');" 
    else :
        validateMethod = "validateSession"        
        paramer1 = sessiontoken
        paramer2 = sessionnum
        NanohubUtils.validateSession(tp, method_name = "validateSession", sessiontoken=sessiontoken, sessionnum=sessionnum, url=url_token);    
        js = ""
        js += "validateSession('"+sessiontoken+"', '"+sessionnum+"');"
        js += "buildSchema('"+toolname+"');" 
    
    tp.globals.assets.append({
      "type": "script",
      "content": js
    })
    
    return [
      {
        "type": "propCall",
        "calls": validateMethod,
        "args": ["'"+paramer1+"'", "'"+paramer2+"'"]
      },
      {
        "type": "propCall",
        "calls": "buildSchema",
        "args": ["'"+toolname+"'"]
      }
    ]        
    
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
    number.content.style = { 'margin': '10px 0px 10px 0px' }
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

  def Switch(component, label, description, state, value=0,*args, **kwargs):
    if (state not in component.stateDefinitions):  
      component.addStateVariable(state, {"type":"boolean", "defaultValue": value})
    switch = TeleportElement(MaterialContent(elementType="Switch"))
    #variant = kwargs.get("variant", "outlined")
    #switch.content.attrs["variant"] = variant
    switch.content.attrs["value"] = label
    #switch.content.style = { 'margin': '10px 0px 10px 0px' }
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

  def Group(elements, *args, **kwargs):
    group = TeleportElement(TeleportContent(elementType="container"))
    style = kwargs.get("style", { 'margin': '15px' } )
    group.content.style = style    
    for element in elements:
      group.addContent(element)
    return group

  def Tabs(component, children, state, *args, **kwargs):
    if (state not in component.stateDefinitions):
      component.addStateVariable(state, {"type":"integer", "defaultValue": kwargs.get("default_value", 0)})
  
    main_container = TeleportElement(TeleportContent(elementType="container"))  
    bar = TeleportElement(MaterialContent(elementType="AppBar"))
    bar.content.attrs["position"] = "static"
    bar.content.attrs["color"] = "secondary"
  
    tabs = TeleportElement(MaterialContent(elementType="Tabs"))
    tabs.content.attrs["value"] = {
      "type": "dynamic", "content": {
        "referenceType": "state", "id": state
      }    
    }
    
    i = 0
    bar.addContent(tabs)    
    main_container.addContent(bar)    
    for key,value in children.items():
      container = TeleportConditional(TeleportContent(elementType="container"))    
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
    if (state not in component.stateDefinitions):    
      raise Exception("Not existing state") 
    container = TeleportConditional(TeleportContent(elementType="container"))
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


  
class RapptureBuilder():

  def getText(tp, *args, **kwargs):    
    method_name = kwargs.get("method_name", "getText")
    eol = "\n";
    js = ""
    js += "function " + method_name + "( component, obj, fields ){" + eol
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
    tp.globals.addAsset(method_name, {
      "type": "script",
      "content": js
    })
    return [
      {
        "type": "propCall",
        "calls": method_name,
        "args": ['undefined','[]']
      }
    ] 
    
  def getXY(tp, *args, **kwargs):    
    eol = "\n";
    method_name = kwargs.get("method_name", "getXY")
    js = ""
    js += "function " + method_name + "( field, container ){" + eol
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
    
    tp.globals.addAsset(method_name, {
      "type": "script",
      "content": js
    })
    return [
      {
        "type": "propCall",
        "calls": method_name,
        "args": ['undefined','']
      }
    ] 

  def buildXYPlotly(tp, *args, **kwargs):    
    eol = "\n";  
    method_name = kwargs.get("method_name", "buildXYPlotly")
    getTextFunction = kwargs.get("getText", "getText")
    getXYFunction = kwargs.get("getXY", "getXY")
    RapptureBuilder.getText(tp, method_name=getTextFunction)
    RapptureBuilder.getXY(tp, method_name=getXYFunction)
    js = ""
    js += "function " + method_name + "( fields, labels ){" + eol
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
    js += "    var component = " + getXYFunction + "(field, 'component');" + eol
    js += "    var label = " + getTextFunction + " (field, ['about','label']);" + eol
    js += "    var style = " + getTextFunction + " (field, ['about','style']);" + eol
    js += "    var line = {'color' : 'blue'};" + eol
    js += "    if (style != ''){" + eol
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
    js += "    title = " + getTextFunction + " (field, ['about','group']);" + eol
    js += "    var xaxis = " + getTextFunction + " (field, ['xaxis','label']);" + eol
    js += "    var xunits = " + getTextFunction + " (field, ['xaxis','units']);" + eol
    js += "    var xscale = " + getTextFunction + " (field, ['xaxis','scale']);" + eol
    js += "    try{" + eol
    js += "      var tempval;" + eol
    js += "      if (xrange[0] == undefined){" + eol
    js += "        tempval = parseFloat(" + getTextFunction + " (field, ['xaxis','min']));" + eol
    js += "      } else{" + eol
    js += "        tempval = min(xrange[0], parseFloat(" + getTextFunction + " (field, ['xaxis','min'])));" + eol
    js += "      }" + eol
    js += "      if ( !isNaN(tempval)){" + eol
    js += "        xrange[0] = tempval;" + eol
    js += "      }" + eol
    js += "    } catch(error){}" + eol
    js += "    try{" + eol
    js += "      var tempval;" + eol
    js += "      if (xrange[1] == undefined){" + eol
    js += "        tempval = parseFloat(" + getTextFunction + " (field, ['xaxis','max']));" + eol
    js += "      } else{" + eol
    js += "        tempval = min(xrange[1], parseFloat(" + getTextFunction + " (field, ['xaxis','max'])));" + eol
    js += "      }" + eol
    js += "      if ( !isNaN(tempval)){" + eol
    js += "        xrange[1] = tempval;" + eol
    js += "      }" + eol
    js += "    } catch(error){}" + eol
    js += "    try{" + eol
    js += "      var tempval;" + eol
    js += "      if (yrange[0] == undefined){" + eol
    js += "        tempval = parseFloat(" + getTextFunction + " (field, ['yaxis','min']));" + eol
    js += "      } else{" + eol
    js += "        tempval = min(yrange[0], parseFloat(" + getTextFunction + " (field, ['yaxis','min'])));" + eol
    js += "      }" + eol
    js += "      if ( !isNaN(tempval)){" + eol
    js += "        yrange[0] = tempval;" + eol
    js += "      }" + eol
    js += "    } catch(error){}" + eol
    js += "    try{" + eol
    js += "      var tempval;" + eol
    js += "      if (yrange[1] == undefined){" + eol
    js += "        tempval = parseFloat(" + getTextFunction + " (field, ['yaxis','max']));" + eol
    js += "      } else{" + eol
    js += "        tempval = min(yrange[1], parseFloat(" + getTextFunction + " (field, ['yaxis','max'])));" + eol
    js += "      }" + eol
    js += "      if ( !isNaN(tempval)){" + eol
    js += "        yrange[1] = tempval;" + eol
    js += "      }" + eol
    js += "    } catch(error){}" + eol
    js += "    if (xscale == ''){" + eol
    js += "      xscale = 'linear';" + eol
    js += "      yaxis = " + getTextFunction + " (field, ['yaxis','label']);" + eol
    js += "      yunits = " + getTextFunction + " (field, ['yaxis','units']);" + eol
    js += "      yscale = " + getTextFunction + " (field, ['yaxis','scale']);" + eol
    js += "    }" + eol
    js += "    if (yscale == ''){" + eol
    js += "      yscale = 'linear';" + eol
    js += "    }" + eol
    js += "    for (var j=0;j<component.length;j++){" + eol
    js += "      var obj = component[j];" + eol
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
    
    tp.globals.addAsset(method_name, {
      "type": "script",
      "content": js
    })

class PNToyBuilder():
  def PNToySettingsComponent(*args, **kwargs):
    PNToySettingsComponent = TeleportComponent("PNToySettingsComponent", TeleportElement(TeleportContent(elementType="container")))

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
    
    impurity_conditional = FormHelper.ConditionalGroup(
      PNToySettingsComponent,
      [
        impuritydoping,
        impuritylevel
      ], "impurity", [{'operation' : '==', "operand" : 1}]
    )    

    
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
        
    
    Tabs = FormHelper.Tabs(PNToySettingsComponent, {
      "Structure" : [
        FormHelper.Header("Structure"),
        p_len,
        p_node,
        i_len,
        i_node,
        n_len,
        n_node,    
        Na,
        Nd,
      ],
      "Materials" : [
        FormHelper.Header("Materials"),
        materialp,
        FormHelper.Header("Minority carrier lifetime"),
        taun,
        taup,
        FormHelper.Header("Impurities"),
        impurity,
        impurity_conditional,
      ],
      "Ambient" : [
        FormHelper.Header("Ambient"),
        temperature,
        vsweep_high,
        vn_step,
      ],
    }, "selected_tab")
    
    PNToySettingsComponent.addNode(Tabs)
    
    return PNToySettingsComponent    
    
  def onSimulate(tp, *args, **kwargs):
    store_name="sessionStore";
    NanohubUtils.storageFactory(tp, store_name=store_name)    
    method_name = kwargs.get("method_name", "onSimulate")
    eol = "\n"
    toolname = kwargs.get("toolname", "")
    url = kwargs.get("url", "")
    
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + store_name + ".removeItem('output_xml');" + eol
    js += "  var params = JSON.parse(" + store_name + ".getItem('nanohub_tool_schema'));" + eol
    js += "  var xmlDoc = JSON.parse(" + store_name + ".getItem('nanohub_tool_xml'));" + eol
    js += "  var state = self.state;" + eol
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
    #Seting default values as current
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
    #Seting state values as current
    js += "  for (const id in state) {" + eol;
    js += "    let value = state[id];" + eol;
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
    js += "  var driver_str  = '<?xml version=\"1.0\"?>\\n' + new XMLSerializer().serializeToString(xmlDoc.documentElement);" + eol
    js += "  var driver_json = {'app': '" + toolname + "', 'xml': driver_str}" + eol;
    js += "  var nanohub_token = " + store_name + ".getItem('nanohub_token');" + eol
    js += "  var header_token = {'Authorization': 'Bearer ' + nanohub_token}" + eol;
    js += "  var url = '" + url + "';";
    js += "  str = [];" + eol
    js += "  for(var p in driver_json){" + eol
    js += "    str.push(encodeURIComponent(p) + '=' + encodeURIComponent(driver_json[p]));" + eol
    js += "  }" + eol
    js += "  data =  str.join('&');" + eol
    js += "  var options = { 'handleAs' : 'json' , 'headers' : header_token, 'method' : 'POST', 'data' : data };" + eol
    js += "  Axios.request(url, options)" + eol
    js += "  .then(function(response){" + eol
    js += "    var session = response.data.session;" + eol
    #js += "    console.log(session);" + eol      
    js += "    setTimeout(function(){checkSession(session, true)},4000);" + eol
    js += "  }).catch(function(error){" + eol
    js += "    console.log(error);" + eol      
    js += "  })" + eol
    js += "}" + eol
    
    js += "function checkSession(session_id, reload){" + eol
    js += "  var session_json = {'session_num': session_id};" + eol;
    js += "  var nanohub_token = " + store_name + ".getItem('nanohub_token');" + eol
    js += "  var header_token = {'Authorization': 'Bearer ' + nanohub_token}" + eol;
    js += "  var url = 'https://nanohub.org/api/tools/status';" + eol
    js += "  str = [];" + eol
    js += "  for(var p in session_json){" + eol
    js += "    str.push(encodeURIComponent(p) + '=' + encodeURIComponent(session_json[p]));" + eol
    js += "  }" + eol
    js += "  data =  str.join('&');" + eol
    js += "  var options = { 'handleAs' : 'json' , 'headers' : header_token, 'method' : 'POST', 'data' : data };" + eol    
    js += "  Axios.request(url, options)" + eol
    js += "  .then(function(response){" + eol
    js += "    var status = response.data;" + eol
    js += "    if (status['success']){" + eol
    js += "      if (status['status']){" + eol
    #js += "        if (status['status'].length > 0){" + eol
    #js += "          console.log(status);" + eol
    #js += "        }" + eol
    js += "        if(status['finished']){" + eol
    js += "          if(status['run_file'] != ''){" + eol
    js += "            loadResults(session_id, status['run_file']);" + eol
    js += "          } else {" + eol
    js += "            if (reload){" + eol
    js += "              setTimeout(function(){checkSession(session_id, false)},2000);" + eol
    js += "            }" + eol
    js += "          }" + eol
    js += "        } else {" + eol
    js += "          if (reload){" + eol
    js += "            setTimeout(function(){checkSession(session_id, reload)},2000);" + eol
    js += "          }" + eol
    js += "        }" + eol
    js += "      }"
    js += "    }"
    js += "  }).catch(function(error){" + eol
    js += "    console.log(error);" + eol      
    js += "  })"
    js += "}"
    
    js += "function loadResults(session_id, run_file){" + eol
    js += "  var results_json = {'session_num': session_id, 'run_file': run_file};" + eol;
    js += "  var nanohub_token = " + store_name + ".getItem('nanohub_token');" + eol
    js += "  var header_token = {'Authorization': 'Bearer ' + nanohub_token}" + eol;
    js += "  var url = 'https://nanohub.org/api/tools/output';" + eol
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
    js += "      " + store_name + ".setItem('output_xml', JSON.stringify(output));" + eol
    js += "    }" + eol    
    js += "  }).catch(function(error){" + eol
    js += "    console.log(error);" + eol
    js += "  })" + eol
    js += "}" + eol

    tp.globals.assets.append({
      "type": "script",
      "content": js
    })
    
    return [
      {
        "type": "propCall",
        "calls": method_name,
        "args": ['self']
      }
    ] 


  def plotXY(tp, *args, **kwargs): 
    RapptureBuilder.buildXYPlotly(tp, method_name="buildXYPlotly")
    method_name = kwargs.get("method_name", "plotSequence")
    url = kwargs.get("url", "")    
    eol = "\n"
    js = ""
    js += "function " + method_name + "( sequence ){" + eol
    js += "  var plt = buildXYPlotly(sequence);" + eol
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

    tp.globals.addAsset(method_name, {
      "type": "script",
      "content": js
    })
    
  def plotSequence(tp, *args, **kwargs): 
    RapptureBuilder.buildXYPlotly(tp, method_name="buildXYPlotly")
    method_name = kwargs.get("method_name", "plotSequence")
    url = kwargs.get("url", "")    
    eol = "\n"
    js = ""
    js += "function " + method_name + "( sequence ){" + eol
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
    js += "      index = index[0].innerHTML;" + eol ####CONTINUE HERE......
    js += "      var curves = seq.getElementsByTagName('curve');" + eol
    js += "      var plt = buildXYPlotly(curves);" + eol
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

    tp.globals.addAsset(method_name, {
      "type": "script",
      "content": js
    })


  def loadSequence(tp, *args, **kwargs):   
    eol = "\n";
    plotSequence = kwargs.get("plotSequence", "plotSequence")
    PNToyBuilder.plotSequence(tp, method_name=plotSequence)
    method_name = kwargs.get("method_name", "loadSequence")
    url = kwargs.get("url", "")    
    js = ""
    js += "function " + method_name + "(self, seq){" + eol
    js += "  var xmlDoc = JSON.parse(" + store_name + ".getItem('output_xml'));" + eol
    js += "  var state = self.state;" + eol
    js += "  if (window.DOMParser){" + eol
    js += "    parser = new DOMParser();" + eol
    js += "    xmlDoc = parser.parseFromString(xmlDoc, 'text/xml');" + eol
    js += "  } else {" + eol
    js += "    xmlDoc = new ActiveXObject('Microsoft.XMLDOM');" + eol
    js += "    xmlDoc.async = false;" + eol
    js += "    xmlDoc.loadXML(xmlDoc);" + eol
    js += "  }" + eol
    js += "  var sequences = xmlDoc.getElementsByTagName('sequence');" + eol
    js += "  for (var i=0;i<sequences.length;i++){" + eol
    js += "    var sequence = sequences[i];" + eol
    js += "    if (sequence.hasAttribute('id') && sequence.getAttribute('id') == seq){" + eol
    js += "      plt = " + plotSequence + "(sequence);" + eol
    js += "      self.setState({" + eol
    js += "        'data': plt['data']," + eol
    js += "        'layout': plt['layout']," + eol
    js += "        'frames': plt['frames']" + eol
    js += "      });" + eol
    js += "    }" + eol
    js += "  }" + eol
    js += "}" + eol
    
    tp.globals.addAsset(method_name, {
      "type": "script",
      "content": js
    })
    
    return {
      "type": "propCall",
      "calls": method_name,
      "args": ['self']
    }
    
    
  def loadXY(tp, *args, **kwargs):   
    eol = "\n";
    plotXY = kwargs.get("plotXY", "plotXY")
    PNToyBuilder.plotXY(tp, method_name=plotXY)
    method_name = kwargs.get("method_name", "loadXy")
    url = kwargs.get("url", "")    
    js = ""
    js += "function " + method_name + "(self, seq){" + eol
    js += "  var xmlDoc = JSON.parse(" + store_name + ".getItem('output_xml'));" + eol
    js += "  var state = self.state;" + eol
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
    js += "      plt = " + plotXY + "([sequence]);" + eol
    js += "      self.setState({" + eol
    js += "        'data': plt['data']," + eol
    js += "        'layout': plt['layout']," + eol
    js += "        'frames': plt['frames']" + eol
    js += "      });" + eol
    js += "    }" + eol
    js += "  }" + eol
    js += "}" + eol
    
    tp.globals.addAsset(method_name, {
      "type": "script",
      "content": js
    })
    
    return {
      "type": "propCall",
      "calls": method_name,
      "args": ['self']
    }
    
  def loadBandStructure(tp, *args, **kwargs):   
    eol = "\n";
    loadSequence = kwargs.get("loadSequence", "loadSequence")    
    PNToyBuilder.loadSequence(tp, method_name="loadSequence")
    method_name = kwargs.get("method_name", "loadBandStructure")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadSequence + "(self, 's1');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, {"type": "script","content": js})    
    return { "type": "propCall", "calls": method_name,"args": ['self']}

  def loadIV(tp, *args, **kwargs):   
    eol = "\n";
    loadXY = kwargs.get("loadXY", "loadXY")    
    PNToyBuilder.loadXY(tp, method_name="loadXY")
    method_name = kwargs.get("method_name", "loadIV")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadXY + "(self, 'iv');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, {"type": "script","content": js})    
    return { "type": "propCall", "calls": method_name,"args": ['self']}
    
  def loadCV(tp, *args, **kwargs):   
    eol = "\n";
    loadXY = kwargs.get("loadXY", "loadXY")    
    PNToyBuilder.loadXY(tp, method_name="loadXY")
    method_name = kwargs.get("method_name", "loadCV")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadXY + "(self, 'cap');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, {"type": "script","content": js})    
    return { "type": "propCall", "calls": method_name,"args": ['self']}

  def loadTotalCurrent(tp, *args, **kwargs):   
    eol = "\n";
    loadSequence = kwargs.get("loadSequence", "loadSequence")    
    PNToyBuilder.loadSequence(tp, method_name="loadSequence")
    method_name = kwargs.get("method_name", "loadTotalCurrent")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadSequence + "(self, 's0');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, { "type": "script", "content": js })    
    return { "type": "propCall", "calls": method_name,"args": ['self'] }    

  def loadTotalDensity(tp, *args, **kwargs):   
    eol = "\n";
    loadSequence = kwargs.get("loadSequence", "loadSequence")    
    PNToyBuilder.loadSequence(tp, method_name="loadSequence")
    method_name = kwargs.get("method_name", "loadTotalDensity")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadSequence + "(self, 's2');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, { "type": "script", "content": js })    
    return { "type": "propCall", "calls": method_name,"args": ['self'] }    

  def loadChargeDensity(tp, *args, **kwargs):   
    eol = "\n";
    loadSequence = kwargs.get("loadSequence", "loadSequence")    
    PNToyBuilder.loadSequence(tp, method_name="loadSequence")
    method_name = kwargs.get("method_name", "loadChargeDensity")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadSequence + "(self, 's4');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, { "type": "script", "content": js })    
    return { "type": "propCall", "calls": method_name,"args": ['self'] }    
 
  def loadPotential(tp, *args, **kwargs):   
    eol = "\n";
    loadSequence = kwargs.get("loadSequence", "loadSequence")    
    PNToyBuilder.loadSequence(tp, method_name="loadSequence")
    method_name = kwargs.get("method_name", "loadPotential")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadSequence + "(self, 's5');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, { "type": "script", "content": js })    
    return { "type": "propCall", "calls": method_name,"args": ['self'] }    
 
  def loadField(tp, *args, **kwargs):   
    eol = "\n";
    loadSequence = kwargs.get("loadSequence", "loadSequence")    
    PNToyBuilder.loadSequence(tp, method_name="loadSequence")
    method_name = kwargs.get("method_name", "loadField")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadSequence + "(self, 's6');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, { "type": "script", "content": js })    
    return { "type": "propCall", "calls": method_name,"args": ['self'] }    
 
  def loadRecombination(tp, *args, **kwargs):   
    eol = "\n";
    loadSequence = kwargs.get("loadSequence", "loadSequence")    
    PNToyBuilder.loadSequence(tp, method_name="loadSequence")
    method_name = kwargs.get("method_name", "loadRecombination")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadSequence + "(self, 's7');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, { "type": "script", "content": js })    
    return { "type": "propCall", "calls": method_name,"args": ['self'] }    
 
  def loadCarrier(tp, *args, **kwargs):   
    eol = "\n";
    loadSequence = kwargs.get("loadSequence", "loadSequence")    
    PNToyBuilder.loadSequence(tp, method_name="loadSequence")
    method_name = kwargs.get("method_name", "loadCarrier")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadSequence + "(self, 's3');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, { "type": "script", "content": js })    
    return { "type": "propCall", "calls": method_name,"args": ['self'] }    
 
    
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
      js += "    var props = {'InputProps':{'inputComponent':this.formatter(), 'endAdornment':this.props.'suffix']},'InputLabelProps':{'shrink':true},'type':'number'};"
      js += "    props ={...props, ...this.props};"
      js += "    return React.createElement(Material.TextField,props);"
      js += "  }"
      js += "}"
      tp.globals.assets.append({
        "type": "script",
        "content": js
      })   
      runSimulation = PNToyBuilder.onSimulate(tp, method_name="onSimulate", toolname="pntoy", url=kwargs.get("url", None))
      tp.components["PNToySettingsComponent"].addPropVariable("onSimulate", {"type":"func"})    
      tp.components["PNToySettingsComponent"].node.addContent(MaterialBuilder.Button(title = "Simulate", onClickButton=runSimulation))
      
      
    ContainerPlot = TeleportElement(TeleportContent(elementType="container"))

        
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