from .teleport import *
class NsopticsBuilder():
  def NsopticsSettingsComponent(*args, **kwargs):
    NsopticsSettingsComponent = TeleportComponent("NsopticsSettingsComponent", TeleportElement(TeleportContent(elementType="container")))

    mat = FormHelper.Select( 
      NsopticsSettingsComponent, 
      "Particle Composition", 
      "Choose a material for the particles. The material selection determines the dielectric properties of the nanoparticle. If 'Constant' is selected the material is assumed to be free of loss and the dielectric constant is assumed to be independent of wavelength. ", 
      "mat", 
      "Au-Gold", 
      {"Au-Gold":"Au-Gold", "Ag-Silver":"Ag-Silver", "Constant":"Constant" }
    )     
    
    cindex = FormHelper.ConditionalGroup(
      NsopticsSettingsComponent, [
      FormHelper.Number(
        NsopticsSettingsComponent, 
        "Particle Refractive Index", 
        "Enter the refractive index of the particle.", 
        "cindex",
        "1.4",
        ""
      )], "mat", "'Constant'"
    )      

    refmed = FormHelper.Number( 
      NsopticsSettingsComponent,
      "Surrounding Medium Refractive Index",
      "Enter the refractive index of the surrounding medium",
      "refmed",
      "1.0",
      ""
    )
    
    radius = FormHelper.Number( 
      NsopticsSettingsComponent,
      "Radius of particle",
      "Radius of particle",
      "radius",
      "20",
      "nm"
    )    

    bwavel = FormHelper.Number( 
      NsopticsSettingsComponent,
      "Beginning wavelength",
      "Beginning wavelength",
      "bwavel",
      "300",
      "nm"
    )    
    
    ewavel = FormHelper.Number( 
      NsopticsSettingsComponent,
      "Ending wavelength",
      "Ending wavelength",
      "ewavel",
      "1000",
      "nm"
    )
        
        
    
    Tabs = FormHelper.Tabs(NsopticsSettingsComponent, {
      "Structure" : [
        mat,
        cindex,
        refmed,
        radius,
        bwavel,
        ewavel,    
      ],
    }, "selected_tab")
    
    NsopticsSettingsComponent.addNode(Tabs)
    
    return NsopticsSettingsComponent    
    
  def onSimulate(tp, *args, **kwargs):
    method_name = kwargs.get("method_name", "onSimulate")
    eol = "\n"
    toolname = kwargs.get("toolname", "")
    url = kwargs.get("url", "")
    
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  window.sessionStorage.removeItem('output_xml');" + eol
    js += "  var params = JSON.parse(window.sessionStorage.getItem('nanohub_tool_schema'));" + eol
    js += "  var xmlDoc = JSON.parse(window.sessionStorage.getItem('nanohub_tool_xml'));" + eol
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
    js += "  var nanohub_token = window.sessionStorage.getItem('nanohub_token');" + eol
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
    js += "  var nanohub_token = window.sessionStorage.getItem('nanohub_token');" + eol
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
    js += "  var nanohub_token = window.sessionStorage.getItem('nanohub_token');" + eol
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
    js += "      window.sessionStorage.setItem('output_xml', JSON.stringify(output));" + eol
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

    
  def loadXY(tp, *args, **kwargs):   
    eol = "\n";
    plotXY = kwargs.get("plotXY", "plotXY")
    NsopticsBuilder.plotXY(tp, method_name=plotXY)
    method_name = kwargs.get("method_name", "loadXy")
    url = kwargs.get("url", "")    
    js = ""
    js += "function " + method_name + "(self, seq){" + eol
    js += "  var xmlDoc = JSON.parse(window.sessionStorage.getItem('output_xml'));" + eol
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
    
   
  def loadExtinctionCrossSection(tp, *args, **kwargs):   
    eol = "\n";
    loadXY = kwargs.get("loadXY", "loadXY")    
    NsopticsBuilder.loadXY(tp, method_name="loadXY")
    method_name = kwargs.get("method_name", "loadExtinctionCrossSection")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadXY + "(self, 'ESC');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, {"type": "script","content": js})    
    return { "type": "propCall", "calls": method_name,"args": ['self']}

  def loadScatteringCrossSection(tp, *args, **kwargs):   
    eol = "\n";
    loadXY = kwargs.get("loadXY", "loadXY")    
    NsopticsBuilder.loadXY(tp, method_name="loadXY")
    method_name = kwargs.get("method_name", "loadScatteringCrossSection")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadXY + "(self, 'SCA');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, {"type": "script","content": js})    
    return { "type": "propCall", "calls": method_name,"args": ['self']}  
 

  def loadAbsortionCrossSection(tp, *args, **kwargs):   
    eol = "\n";
    loadXY = kwargs.get("loadXY", "loadXY")    
    NsopticsBuilder.loadXY(tp, method_name="loadXY")
    method_name = kwargs.get("method_name", "loadAbsortionCrossSection")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadXY + "(self, 'ABS');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, {"type": "script","content": js})    
    return { "type": "propCall", "calls": method_name,"args": ['self']}  
 

  def loadRealDielectric(tp, *args, **kwargs):   
    eol = "\n";
    loadXY = kwargs.get("loadXY", "loadXY")    
    NsopticsBuilder.loadXY(tp, method_name="loadXY")
    method_name = kwargs.get("method_name", "loadRealDielectric")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadXY + "(self, 'REP');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, {"type": "script","content": js})    
    return { "type": "propCall", "calls": method_name,"args": ['self']}  
 

  def loadImaginaryDielectric(tp, *args, **kwargs):   
    eol = "\n";
    loadXY = kwargs.get("loadXY", "loadXY")    
    NsopticsBuilder.loadXY(tp, method_name="loadXY")
    method_name = kwargs.get("method_name", "loadImaginaryDielectric")
    js = ""
    js += "function " + method_name + "(self){" + eol
    js += "  " + loadXY + "(self, 'IEP');" + eol
    js += "}" + eol    
    tp.globals.addAsset(method_name, {"type": "script","content": js})    
    return { "type": "propCall", "calls": method_name,"args": ['self']}  
 
    
  def NsopticsSettings(tp, *args, **kwargs):
    if ("NsopticsSettingsComponent" not in tp.components):
      tp.components["NsopticsSettingsComponent"] = NsopticsBuilder.NsopticsSettingsComponent()  
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
      runSimulation = NsopticsBuilder.onSimulate(tp, method_name="onSimulate", toolname="Nsoptics", url=kwargs.get("url", None))
      tp.components["NsopticsSettingsComponent"].addPropVariable("onSimulate", {"type":"func"})    
      tp.components["NsopticsSettingsComponent"].node.addContent(MaterialBuilder.Button(title = "Simulate", onClickButton=runSimulation))
      
      
    ContainerPlot = TeleportElement(TeleportContent(elementType="container"))

        
    NsopticsSettings = TeleportElement(TeleportContent(elementType="NsopticsSettingsComponent"))
    if kwargs.get("data", None) is not None:
      NsopticsSettings.content.attrs["data"] = kwargs.get("data", None)

    if kwargs.get("ref", None) is not None:
      NsopticsSettings.content.attrs["ref"] = kwargs.get("ref", None)
      
    if kwargs.get("style_state", None) is not None:
      ContainerPlot.content.attrs["className"] = {
        "type": "dynamic",
        "content": {
          "referenceType": "state",
          "id": kwargs.get("style_state")
        }    
      }
    
    ContainerPlot.addContent(NsopticsSettings)
    return ContainerPlot