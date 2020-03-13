from .teleport import *
from .material import *

class Auth():
  def Login(tp, Component, *args, **kwargs):
    AComponent = TeleportComponent("AuthLogin", TeleportElement(MaterialContent(elementType="Paper")))
    
    AComponent.node.content.style = {"width":"100%"}
    AComponent.addPropVariable("open", {"type":"boolean", 'defaultValue' : True})  
    AComponent.addStateVariable("username", {"type":"string", 'defaultValue' : ""})  
    AComponent.addStateVariable("password", {"type":"string", 'defaultValue' : ""})  
    AComponent.addStateVariable("showpassword", {"type":"string", 'defaultValue' : "visibility_off"})  
    AComponent.addStateVariable("typepassword", {"type":"string", 'defaultValue' : "password"})  
    AComponent.addStateVariable("loading", {"type":"boolean", 'defaultValue' : False})  
    AComponent.addStateVariable("message", {"type":"string", 'defaultValue' : ""})  
    
    AComponent.addPropVariable("username_icon", {"type":"func", 'defaultValue' : '''()=>{
        return { 
            'startAdornment' : React.createElement(
                Material.InputAdornment,{'position':'start'}, React.createElement(
                    Material.IconButton,{}, React.createElement(
                        Material.Icon, {}, 'supervised_user_circle'
                    )
                )
            )
        };
    }'''})     
    AComponent.addPropVariable("password_icon", {"type":"func", 'defaultValue' : '''(self)=>{
        return { 
            'endAdornment' : React.createElement(
                Material.InputAdornment,{'position':'end'}, React.createElement(
                    Material.IconButton,{ 'onClick' :(e)=>{
                            if (self.state.showpassword == "visibility")
                                self.setState({'showpassword':'visibility_off','typepassword':'password'})
                            else
                                self.setState({'showpassword':'visibility','typepassword':'text'})

                        }}, React.createElement(
                        Material.Icon, {}, self.state.showpassword
                    )
                )
            )
        };
    }'''}) 
    Dialog = TeleportElement(MaterialContent(elementType="Dialog"))
    Dialog.content.attrs["open"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "prop",
        "id": "open"
      }    
    }    
    Dialog.content.attrs["disableBackdropClick"] = True
    Dialog.content.attrs["disableEscapeKeyDown"] = True
    Dialog.content.attrs["fullWidth"] = True
    Dialog.content.attrs["maxWidth"] = 'xs'
    DialogContent = TeleportElement(MaterialContent(elementType="DialogContent"))
    DialogContent.content.style = { "textAlign": "center", "overflow" : "hidden"}
    AppBar = TeleportElement(MaterialContent(elementType="AppBar"))
    AppBar.content.attrs["position"] = "static"
    AppBar.content.attrs["color"] = "secondary"
    AppBar.content.style={ 'marginBottom' : '10px'};
    ToolBar = TeleportElement(MaterialContent(elementType="Toolbar"))
    ToolBar.content.attrs["variant"] = kwargs.get("variant", "regular")
    Typography = TeleportElement(MaterialContent(elementType="Typography"))
    Typography.content.attrs["variant"] = "h6"
    Typography.content.style={'flex':1, 'textAlign':'center'}
    TypographyText = TeleportStatic(content=kwargs.get("title", "Sign in to nanoHUB.org"))
    Typography.addContent(TypographyText)
    ToolBar.addContent(Typography)
    AppBar.addContent(ToolBar)
    Username = TeleportElement(MaterialContent(elementType="TextField"))
    Username.content.attrs["placeholder"] = 'Enter your Username'
    Username.content.attrs["defaultValue"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "username"
      }    
    }    
    Username.content.attrs["InputProps"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "prop",
        "id": "username_icon()"
      }    
    }    
    Username.content.events["change"] = [{ "type": "stateChange", "modifies": "username","newState": "$e.target.value"}] 
    Username.content.attrs["variant"] = kwargs.get("variant", "outlined")
    Username.content.attrs["fullWidth"] = True
    Username.content.attrs["helperText"] = "Username"
    
    Password = TeleportElement(MaterialContent(elementType="TextField"))
    Password.content.attrs["type"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "typepassword"
      }    
    }  
    Password.content.attrs["placeholder"] = 'Enter your Password'
    Password.content.attrs["defaultValue"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "password"
      }    
    }    
    Password.content.attrs["InputProps"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "prop",
        "id": "password_icon(this)"
      }    
    }    
    Password.content.events["change"] = [{ "type": "stateChange", "modifies": "password","newState": "$e.target.value"}] 
    Password.content.attrs["variant"] = kwargs.get("variant", "outlined")
    Password.content.attrs["fullWidth"] = True
    Password.content.attrs["helperText"] = "Password"

    onClick = Auth.validateCredentials(
       tp, 
       AComponent, 
       client_id=kwargs.get("client_id",""), 
       client_secret=kwargs.get("client_secret",""), 
       url=kwargs.get("url","")
    )    
    onRefresh = Auth.refreshToken(
       tp, 
       AComponent, 
       client_id=kwargs.get("client_id",""), 
       client_secret=kwargs.get("client_secret",""), 
       url=kwargs.get("url","")
    )    
    Button = MaterialBuilder.Button(
        title = "LOG IN",
        variant = "text", 
        style = {'backgroundColor':'#999999', 'borderRadius' : '0px', 'minHeight':'40px', 'color':'rgba(255, 255, 255, 0.87)'}, 
        onClickButton=onClick
    )
    Button.content.attrs["fullWidth"] = True
    
    LinearProgress = TeleportElement(MaterialContent(elementType="LinearProgress"))
    LinearProgress.content.attrs["color"] = 'secondary'
    Message = TeleportElement(MaterialContent(elementType="TextField"))
    Message.content.attrs["variant"] = "standard"
    Message.content.attrs["fullWidth"] = True
    Message.content.attrs["disabled"] = True
    
    Message.content.attrs["value"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "message"
      }    
    }
    
    Conditional = TeleportConditional(MaterialContent(elementType="Paper")) 
    Conditional.reference = {
    "type": "dynamic",
        "content": {
          "referenceType": "state",
          "id": "loading"
        }    
    }    
    Conditional.value = True

    Conditional.addContent(LinearProgress)
  
    DialogContent.addContent(AppBar)
    DialogContent.addContent(Username)
    DialogContent.addContent(Password)
    DialogContent.addContent(Message)
    DialogContent.addContent(Conditional)
    DialogContent.addContent(Button)    
    
    Dialog.addContent(DialogContent)
    AComponent.node.addContent(Dialog)

    #Dialog.addContent(loadertext)

    AuthLogin = TeleportElement(TeleportContent(elementType="AuthLogin"))
    Component.addStateVariable(kwargs.get("open_state", "login_open"), {"type":"boolean", "defaultValue": True})
    AuthLogin.content.attrs["open"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": kwargs.get("open_state", "login_open")
      }    
    }
    tp.components["AuthLogin"] = AComponent
    return AuthLogin, AComponent


  def validateCredentials(tp, Component, *args, **kwargs):
    store_name="sessionStore";
    NanohubUtils.storageFactory(tp, store_name=store_name)
    client_id = kwargs.get("client_id", "")
    client_secret = kwargs.get("client_secret", "")
    url = kwargs.get("url", "")
    eol = "\n";
    Component.addPropVariable("onAuth", {"type":"func", 'defaultValue' : '(e)=>{}'})    
    Component.addPropVariable("onError", {"type":"func", 'defaultValue' : '(e)=>{}'})    
    
    js = ""
    js = "(self)=>{" + eol
    js += "  var data = ''" + eol
    js += "  data = 'client_id="+client_id+"&';" + eol
    js += "  data += 'client_secret="+client_secret+"&';" + eol
    js += "  data += 'grant_type=password&';" + eol
    js += "  data += 'username=' + self.state.username + '&';" + eol
    js += "  data += 'password=' + self.state.password + '&';" + eol
    js += "  var header_token = { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*' };" + eol
    js += "  var options = { 'handleAs' : 'json' , 'headers' : header_token, 'method' : 'POST', 'data' : data };" + eol
    js += "  var url = '" + url + "';" + eol
    js += "  var expiration = " + store_name + ".getItem('nanohub_expires');" + eol
    js += "  var current_time = Date.now();\n";
    js += "  if (expiration === null || current_time > expiration){" + eol
    js += "    let selfr = self;" + eol
    js += "    Axios.request(url, options)" + eol
    js += "    .then(function(response){" + eol
    js += "      var data = response.data;" + eol
    js += "      if(data.code){" + eol    
    js += "        " + store_name + ".removeItem('nanohub_token');" + eol
    js += "        " + store_name + ".removeItem('nanohub_expires');" + eol
    js += "        " + store_name + ".removeItem('nanohub_refresh_token');" + eol
    js += "        if(data.message){" + eol    
    js += "          selfr.setState({'open' : true, 'loading' : false, 'message' : data.message});" + eol
    js += "          selfr.props.onError(data.message);" + eol
    js += "        } else {" + eol    
    js += "          selfr.setState({'open' : true, 'loading' : false, 'message' : 'Error authenticating user'});" + eol    
    js += "          selfr.props.onError('Error authenticating user');" + eol
    js += "        } " + eol    
    js += "      } else {" + eol
    js += "        if(data.access_token){" + eol    
    js += "          " + store_name + ".setItem('nanohub_token', String(data.access_token));" + eol
    js += "          " + store_name + ".setItem('nanohub_expires', JSON.stringify(Date.now()+parseInt(data.expires_in)-200));" + eol
    js += "          " + store_name + ".setItem('nanohub_refresh_token', String(data.refresh_token));" + eol
    js += "          selfr.setState({'open' : false, 'loading' : false, 'message' : ''});" + eol
    js += "          selfr.props.onAuth(selfr);" + eol
    js += "        } else {" + eol
    js += "          " + store_name + ".removeItem('nanohub_token');" + eol
    js += "          " + store_name + ".removeItem('nanohub_expires');" + eol
    js += "          " + store_name + ".removeItem('nanohub_refresh_token');" + eol
    js += "          selfr.props.onError('Error authenticating user');" + eol
    js += "          selfr.setState({'open' : true, 'loading' : false, 'message' : 'Error authenticating user'});" + eol    
    js += "        }" + eol
    js += "      }" + eol
    js += "    }).catch(function(error){\n"
    js += "      " + store_name + ".removeItem('nanohub_token');" + eol
    js += "      " + store_name + ".removeItem('nanohub_expires');" + eol
    js += "      " + store_name + ".removeItem('nanohub_refresh_token');" + eol
    js += "      selfr.setState({'open' : true, 'loading' : false, 'message' : 'Error authenticating user'});" + eol
    js += "      selfr.props.onError('Error authenticating user');" + eol
    js += "    })" + eol
    js += "  }" + eol
    js += "}" + eol
    
    Component.addPropVariable("onClick", {"type":"func", 'defaultValue' :js})   
    callbacklist = []
    callbacklist.append({
      "type": "stateChange",
      "modifies": 'open',
      "newState": True
    })
    callbacklist.append({
      "type": "stateChange",
      "modifies": 'loading',
      "newState": True
    })
    callbacklist.append({
      "type": "stateChange",
      "modifies": 'message',
      "newState": ''
    })
    callbacklist.append({
        "type": "propCall2",
        "calls": "onClick",
        "args": ['self']
    })    
    return callbacklist   

  def Session(tp, Component, *args, **kwargs):
    SComponent = TeleportComponent("AuthSession", TeleportElement(MaterialContent(elementType="Paper")))
    SComponent.node.content.style = {"width":"100%"}
    SComponent.addStateVariable("open", {"type":"boolean", 'defaultValue' : True})  
    SComponent.addStateVariable("message", {"type":"string", 'defaultValue' : "Validating Session"})  

    Dialog = TeleportElement(MaterialContent(elementType="Dialog"))
    Dialog.content.attrs["open"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "open"
      }    
    }    
    Dialog.content.attrs["disableBackdropClick"] = True
    Dialog.content.attrs["disableEscapeKeyDown"] = True
    Dialog.content.attrs["fullWidth"] = True
    Dialog.content.attrs["maxWidth"] = 'xs'
    DialogContent = TeleportElement(MaterialContent(elementType="DialogContent"))
    DialogContent.content.style = { "textAlign": "center", "overflow" : "hidden"}

    LinearProgress = TeleportElement(MaterialContent(elementType="LinearProgress"))
    LinearProgress.content.attrs["color"] = 'secondary'
    Message = TeleportElement(MaterialContent(elementType="TextField"))
    Message.content.attrs["variant"] = "standard"
    Message.content.attrs["fullWidth"] = True
    Message.content.attrs["disabled"] = True
    
    Message.content.attrs["value"] = {
      "type": "dynamic",
      "content": {
        "referenceType": "state",
        "id": "message"
      }    
    }  
    DialogContent.addContent(Message)
    DialogContent.addContent(LinearProgress)    
    Dialog.addContent(DialogContent)
    SComponent.node.addContent(Dialog)

    AuthSession = TeleportElement(TeleportContent(elementType="AuthSession"))
    Dialog.content.events["onEntered"] = Auth.validateSession(
        tp, 
        SComponent, 
        sessiontoken=kwargs.get("sessiontoken",""), 
        sessionnum=kwargs.get("sessionnum",""), 
        url=kwargs.get("url","")
    )
    tp.components["AuthSession"] = SComponent
    return AuthSession, SComponent
    
  def validateSession(tp, Component, *args, **kwargs):
    store_name="sessionStore";
    NanohubUtils.storageFactory(tp, store_name=store_name)
    sessiontoken = kwargs.get("sessiontoken", "")
    sessionnum = kwargs.get("sessionnum", "")
    eol = "\n";

    Component.addPropVariable("onAuth", {"type":"func", 'defaultValue' : '(e)=>{}'})    
    Component.addPropVariable("onError", {"type":"func", 'defaultValue' : '(e)=>{}'})    
    url = kwargs.get("url", "")
    
    js = "(self)=>{" + eol
    js += "  var data = '';\n"
    js += "  data = 'sessiontoken="+sessiontoken+"&';" + eol
    js += "  data += 'sessionnum="+sessionnum+"&';" + eol
    js += "  data += 'grant_type=tool&';" + eol
    js += "  var header_token = { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*' };" + eol
    js += "  var options = { 'handleAs' : 'json' , 'headers' : header_token, 'method' : 'POST', 'data' : data };" + eol
    js += "  var url = '" + url + "';" + eol
    js += "  var expiration = " + store_name + ".getItem('nanohub_expires');" + eol
    js += "  var current_time = Date.now()" + eol
    js += "  if (expiration === null || current_time > expiration){" + eol
    js += "    let selfr = self;" + eol
    js += "    Axios.request(url, options)" + eol
    js += "    .then(function(response){" + eol
    js += "      var data = response.data;" + eol
    js += "      if(data.code){" + eol    
    js += "        " + store_name + ".removeItem('nanohub_token');" + eol
    js += "        " + store_name + ".removeItem('nanohub_expires');" + eol
    js += "        " + store_name + ".removeItem('nanohub_refresh_token');" + eol
    js += "        if(data.message){" + eol    
    js += "          selfr.setState({'message' : '(' + data.code + ') ' +data.message});" + eol
    js += "          selfr.props.onError( '(' + data.code + ') ' +data.message );" + eol
    js += "        } else {" + eol    
    js += "          selfr.setState({'message' : '(' + data.code + ') Error validating Session'});" + eol    
    js += "          selfr.props.onError( '(' + data.code + ') Error validating Session' );" + eol
    js += "        } " + eol    
    js += "      } else {" + eol
    js += "        if(data.access_token){" + eol    
    js += "          " + store_name + ".setItem('nanohub_token', String(data.access_token));" + eol
    js += "          " + store_name + ".setItem('nanohub_expires', JSON.stringify(Date.now()+parseInt(data.expires_in)-200));" + eol
    js += "          " + store_name + ".setItem('nanohub_refresh_token', String(data.refresh_token));" + eol
    js += "          selfr.setState({'open' : false, 'message' : ''});" + eol
    js += "          selfr.props.onAuth(selfr);" + eol
    js += "        } else {" + eol
    js += "          " + store_name + ".removeItem('nanohub_token');" + eol
    js += "          " + store_name + ".removeItem('nanohub_expires');" + eol
    js += "          " + store_name + ".removeItem('nanohub_refresh_token');" + eol
    js += "          selfr.setState({'open' : true, 'message' : 'Error validating Session, invalid token'});" + eol    
    js += "          selfr.props.onError( 'Error validating Session' );" + eol
    js += "        }" + eol
    js += "      }" + eol
    js += "    }).catch(function(error){\n"
    js += "      " + store_name + ".removeItem('nanohub_token');" + eol
    js += "      " + store_name + ".removeItem('nanohub_expires');" + eol
    js += "      " + store_name + ".removeItem('nanohub_refresh_token');" + eol
    js += "      selfr.setState({'open' : true, 'message' : 'Error validating Session, unknown error'});" + eol
    js += "      selfr.props.onError( 'Error validating Session' );" + eol
    js += "    })" + eol
    js += "  }" + eol
    js += "}" + eol
    Component.addPropVariable("validateSession", {"type":"func", 'defaultValue' :js})   

    
    return [
      {
        "type": "propCall2",
        "calls": "validateSession",
        "args": ['self']
      }
    ]


  def refreshToken(tp, Component, *args, **kwargs):
    store_name="sessionStore";
    NanohubUtils.storageFactory(tp, store_name=store_name)
    url = kwargs.get("url", "")
    client_id = kwargs.get("client_id", "")
    client_secret = kwargs.get("client_secret", "")
    eol = "\n"
    js = ""
    js = "(self)=>{" + eol    
    js += "  var token = " + store_name + ".getItem('nanohub_token');" + eol
    js += "  var data = '';" + eol
    js += "  data = 'client_id="+client_id+"&';" + eol
    js += "  data += 'client_secret="+client_secret+"&';" + eol
    js += "  data += 'grant_type=refresh_token&';" + eol
    js += "  data += 'refresh_token=' + token + '&';" + eol
    js += "  var header_token = { 'Content-Type': 'application/x-www-form-urlencoded', 'Accept': '*/*' };" + eol
    js += "  var options = { 'handleAs' : 'json' , 'headers' : header_token, 'method' : 'POST', 'data' : data };" + eol
    js += "  var url = '" + url + "';" + eol
    js += "  let selfr = self;" + eol
    js += "  Axios.request(url, options)" + eol
    js += "  .then(function(response){" + eol
    js += "    var data = response.data;" + eol
    js += "    if(data.code){" + eol    
    js += "      " + store_name + ".removeItem('nanohub_token');" + eol
    js += "      " + store_name + ".removeItem('nanohub_expires');" + eol
    js += "      " + store_name + ".removeItem('nanohub_refresh_token');" + eol
    js += "      if(data.message){" + eol    
    js += "        selfr.props.onError(data.message);" + eol
    js += "        selfr.setState({'open' : true, 'loading' : false, 'message' : data.message});" + eol
    js += "      } else {" + eol    
    js += "        selfr.props.onError('Error authenticating user');" + eol
    js += "        selfr.setState({'open' : true, 'loading' : false, 'message' : 'Error authenticating user'});" + eol    
    js += "      } " + eol    
    js += "    } else {" + eol
    js += "      if(data.access_token){" + eol    
    js += "        " + store_name + ".setItem('nanohub_token', String(data.access_token));" + eol
    js += "        " + store_name + ".setItem('nanohub_expires', JSON.stringify(Date.now()+parseInt(data.expires_in)-200));" + eol
    js += "        " + store_name + ".setItem('nanohub_refresh_token', String(data.refresh_token));" + eol
    js += "        selfr.setState({'open' : false, 'loading' : false, 'message' : ''});" + eol
    js += "        selfr.props.onAuth( selfr );" + eol
    js += "      } else {" + eol
    js += "        " + store_name + ".removeItem('nanohub_token');" + eol
    js += "        " + store_name + ".removeItem('nanohub_expires');" + eol
    js += "        " + store_name + ".removeItem('nanohub_refresh_token');" + eol
    js += "        selfr.props.onError('Error authenticating user');" + eol
    js += "        selfr.setState({'open' : true, 'loading' : false, 'message' : 'Error authenticating user'});" + eol    
    js += "      }" + eol
    js += "    }" + eol
    js += "  }).catch(function(error){"
    js += "    " + store_name + ".removeItem('nanohub_token');" + eol
    js += "    " + store_name + ".removeItem('nanohub_expires');" + eol
    js += "    " + store_name + ".removeItem('nanohub_refresh_token');" + eol
    js += "    selfr.setState({'open' : true, 'loading' : false, 'message' : 'Error authenticating user'});" + eol
    js += "    selfr.props.onError('Error authenticating user');" + eol
    js += "  })" + eol
    js += "}" + eol
    Component.addPropVariable("refreshToken", {"type":"func", 'defaultValue' :js})   
                       
    return [
      {
        "type": "propCall2",
        "calls": "refreshToken",
        "args": ['self', '']
      }
    ] 