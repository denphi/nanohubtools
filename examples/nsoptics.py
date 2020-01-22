import uidl.teleport as t
from uidl.nsoptics import NsopticsBuilder
import json
from mysecrets import auth_data
tp = t.TeleportProject("test")
Component = tp.components["MainComponent"]
Component.addStateVariable("DrawerIsVisible", {"type":"boolean", "defaultValue": True})
Component.addStateVariable("AppBarStyle", {"type":"string", "defaultValue": "bar_shifted"})
Component.addStateVariable("view", {"type":"integer", "defaultValue": 1})

setNewData = [
  {
    "type": "stateChange",
    "modifies": "view",
    "newState": 0
  },
  {
    "type": "propCall",
    "calls": "randomData",
    "args": ['self']
  }
]


setSettings = [
  {
    "type": "stateChange",
    "modifies": "view",
    "newState": 1
  },
]


tp.globals.assets.append({
  "type": "style",
  "content": ".bar_shifted {margin-left:300px; width: calc(100% - 300px);}"
})

tp.globals.assets.append({
  "type": "style",
  "content": ".bar_normal {margin-left:0px}"
})

tp.globals.assets.append({
  "type": "style",
  "content": ".pnLabLogo{  height: 80px; background-repeat: no-repeat;background-position-x: center; background-size: 450px; background-position-y: 8px; width:500px;}"
})                                       
#  "content": ".pnLabLogo{ background-image: url(\"data:image/svg+xml;base64,PD94bWwgdmVyc2lvbj0iMS4wIj8+Cjxzdmcgd2lkdGg9IjY0MCIgaGVpZ2h0PSI0ODAiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyIgeG1sbnM6c3ZnPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CiA8ZyBjbGFzcz0ibGF5ZXIiPgogIDx0aXRsZT5MYXllciAxPC90aXRsZT4KICA8cmVjdCBmaWxsPSIjZmZmIiBoZWlnaHQ9Ijg5IiBpZD0ic3ZnXzEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIiB3aWR0aD0iNDY1IiB4PSIxNiIgeT0iMCIvPgogIDxyZWN0IGZpbGw9IiMwMDAiIGhlaWdodD0iODkiIGlkPSJzdmdfMTAxIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiIgd2lkdGg9IjE2NyIgeD0iMzEzIiB5PSIwIi8+CiAgPHJlY3QgZmlsbD0iIzAwMCIgaGVpZ2h0PSI4OSIgaWQ9InN2Z182MCIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiIHdpZHRoPSIxNjciIHg9IjE2IiB5PSIwIi8+CiAgPGNpcmNsZSBjeD0iNDMiIGN5PSIyMyIgZmlsbD0iI2ZmZiIgaWQ9InN2Z18yIiByPSIxNS41NTYzNTEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPGNpcmNsZSBjeD0iNDMiIGN5PSI2NSIgZmlsbD0iI2ZmZiIgaWQ9InN2Z180IiByPSIxNS41NTYzNTEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPGNpcmNsZSBjeD0iMTYxIiBjeT0iMjMiIGZpbGw9IiNmZmYiIGlkPSJzdmdfMTEiIHI9IjE1LjU1NjM1MSIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiLz4KICA8Y2lyY2xlIGN4PSIxNjEiIGN5PSI2NSIgZmlsbD0iI2ZmZiIgaWQ9InN2Z18xMCIgcj0iMTUuNTU2MzUxIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiIvPgogIDxjaXJjbGUgY3g9IjIwNyIgY3k9IjIzIiBmaWxsPSIjZmZmIiBpZD0ic3ZnXzI2IiByPSIxNS41NTYzNTEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPGNpcmNsZSBjeD0iMjA3IiBjeT0iNjUiIGZpbGw9IiNmZmYiIGlkPSJzdmdfMjUiIHI9IjE1LjU1NjM1MSIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiLz4KICA8Y2lyY2xlIGN4PSIyNDgiIGN5PSIyMyIgZmlsbD0iI2ZmZiIgaWQ9InN2Z18yMyIgcj0iMTUuNTU2MzUxIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiIvPgogIDxjaXJjbGUgY3g9IjI0OCIgY3k9IjY1IiBmaWxsPSIjZmZmIiBpZD0ic3ZnXzIyIiByPSIxNS41NTYzNTEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPGNpcmNsZSBjeD0iMjkyIiBjeT0iMjMiIGZpbGw9IiNmZmYiIGlkPSJzdmdfMjAiIHI9IjE1LjU1NjM1MSIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiLz4KICA8Y2lyY2xlIGN4PSIyOTIiIGN5PSI2NSIgZmlsbD0iI2ZmZiIgaWQ9InN2Z18xOSIgcj0iMTUuNTU2MzUxIiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiIvPgogIDxjaXJjbGUgY3g9IjMzMyIgY3k9IjIzIiBmaWxsPSIjZmZmIiBpZD0ic3ZnXzE3IiByPSIxNS41NTYzNTEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPGNpcmNsZSBjeD0iMzMzIiBjeT0iNjUiIGZpbGw9IiNmZmYiIGlkPSJzdmdfMTYiIHI9IjE1LjU1NjM1MSIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiLz4KICA8Y2lyY2xlIGN4PSI0NTYiIGN5PSIyMyIgZmlsbD0iI2ZmZiIgaWQ9InN2Z18yOSIgcj0iMTUuNTU2MzM1IiBzdHJva2U9IiMwMDAiIHN0cm9rZS13aWR0aD0iMiIvPgogIDxjaXJjbGUgY3g9IjQ1NiIgY3k9IjY1IiBmaWxsPSIjZmZmIiBpZD0ic3ZnXzI4IiByPSIxNS41NTYzNTEiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLXdpZHRoPSIyIi8+CiAgPHRleHQgZmlsbD0iIzAwMCIgZm9udC1mYW1pbHk9InNlcmlmIiBmb250LXNpemU9IjI0IiBpZD0ic3ZnXzM2IiBzdHJva2U9IiMwMDAiIHRleHQtYW5jaG9yPSJtaWRkbGUiIHg9IjQzIiB5PSIzMSI+KzwvdGV4dD4KICA8dGV4dCBmaWxsPSIjMDAwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGlkPSJzdmdfMzciIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDMiIHk9IjczIj4rPC90ZXh0PgogIDx0ZXh0IGZpbGw9IiMwMDAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIyNCIgaWQ9InN2Z180NyIgc3Ryb2tlPSIjMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxNjEiIHk9IjMxIj4rPC90ZXh0PgogIDx0ZXh0IGZpbGw9IiMwMDAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIyNCIgaWQ9InN2Z180NiIgc3Ryb2tlPSIjMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxNjEiIHk9IjczIj4rPC90ZXh0PgogIDx0ZXh0IGZpbGw9IiMwMDAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIyNCIgaWQ9InN2Z180NSIgc3Ryb2tlPSIjMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIyMDciIHk9IjMxIj4rPC90ZXh0PgogIDx0ZXh0IGZpbGw9IiMwMDAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIyNCIgaWQ9InN2Z180NCIgc3Ryb2tlPSIjMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIyMDciIHk9IjczIj4rPC90ZXh0PgogIDx0ZXh0IGZpbGw9IiMwMDAiIGZvbnQtZmFtaWx5PSJzZXJpZiIgZm9udC1zaXplPSIyNCIgaWQ9InN2Z18xMDAiIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMjkyIiB5PSIxOCI+XzwvdGV4dD4KICA8dGV4dCBmaWxsPSIjMDAwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGlkPSJzdmdfOTkiIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMjkyIiB5PSI2MyI+XzwvdGV4dD4KICA8dGV4dCBmaWxsPSIjMDAwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGlkPSJzdmdfODgiIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMzMzIiB5PSIxOCI+XzwvdGV4dD4KICA8dGV4dCBmaWxsPSIjMDAwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGlkPSJzdmdfOTciIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iMzMzIiB5PSI2MyI+XzwvdGV4dD4KICA8dGV4dCBmaWxsPSIjMDAwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGlkPSJzdmdfOTAiIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDU2IiB5PSIxOCI+XzwvdGV4dD4KICA8dGV4dCBmaWxsPSIjMDAwIiBmb250LWZhbWlseT0ic2VyaWYiIGZvbnQtc2l6ZT0iMjQiIGlkPSJzdmdfOTUiIHN0cm9rZT0iIzAwMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgeD0iNDU2IiB5PSI2MyI+XzwvdGV4dD4KICA8cmVjdCBmaWxsPSIjMDAwIiBoZWlnaHQ9IjUzIiBpZD0ic3ZnXzEwMiIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiIHdpZHRoPSIxNCIgeD0iMCIgeT0iMTgiLz4KICA8cmVjdCBmaWxsPSIjMDAwIiBoZWlnaHQ9IjUzIiBpZD0ic3ZnXzEwMyIgc3Ryb2tlPSIjMDAwIiBzdHJva2Utd2lkdGg9IjIiIHdpZHRoPSIxNCIgeD0iNDgwIiB5PSIxOCIvPgogIDx0ZXh0IGZpbGw9IiNmZmYiIGZvbnQtZmFtaWx5PSJTYW5zLXNlcmlmIiBmb250LXNpemU9IjcwIiBpZD0ic3ZnXzEwNCIgc3Ryb2tlPSIjMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIxMDAiIHk9IjY5Ij5QPC90ZXh0PgogIDx0ZXh0IGZpbGw9IiNmZmYiIGZvbnQtZmFtaWx5PSJTYW5zLXNlcmlmIiBmb250LXNpemU9IjcwIiBpZD0ic3ZnXzEwNSIgc3Ryb2tlPSIjMDAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiB4PSIzOTUiIHk9IjY5Ij5OPC90ZXh0PgogPC9nPgo8L3N2Zz4=\");}"
                
theme = {
  'shadows': ["none" for i in range(10) ],
  'palette': {
    'primary': {
      'main': '#EEEEEE',
    },
    'secondary': {
      'main': '#B5BEFD',
    },
  },
  'overrides': {
    'MuiFab': {
      'root': { 'border': '2px solid #CCCCCC' },
      #'primary': { 'width' : '100%', 'background-color': '#FFFFFF', '&:hover': {'background-color': '#B5BEFD'} },
      #'secondary': { 'width' : '100%', 'background-color': '#B5BEFD' }
    },
    'MuiGrid' : {
      'item' : { 'display' : 'flex', 'flex-direction' : 'column', 'padding': '4px' }
    },
    'MuiDrawer' : {
      'paper' : {
        #'background-color': '#EEEEEE',
        'width' : '300px',
        'top' : '80px'
      }
    },
    'MuiAppBar' : {
      'colorPrimary': {
        #'backgroundColor':'#EEEEEE'
      },
      #'secondary': {
      #  'backgroundColor':'#B5BEFD'
      #},
    }
  },  
}
tp.globals.assets.append({
  "type": "script",
  "content": "theme_default = Material.createMuiTheme(" + json.dumps(theme) + "); "
})
tp.globals.assets.append({
  "type": "script",
  "content": "var component_ref={}; function setRef(key, obj){ component_ref[key]=obj };"
})
tp.globals.assets.append({
  "type": "script",
  "content": "function setPlotlyRef(obj){ setRef('plotly_widget', obj) };"
})
tp.globals.assets.append({
  "type": "script",
  "content": "function setSettingsRef(obj){ setRef('settings', obj) };"
})
tp.globals.assets.append({
  "type": "script",
  "content": "function randomData(self){ self.setState({'data': [{'x': [1,2,3,4], 'y': Array(4).fill().map(() => Math.round(Math.random() * 40))}]}); };"
})

client_id = "93de669e140a5e1160893b31d2f64a69" #dev
client_id = "4135f6de1fad82002813c7a796ff983e" #prod
client_secret = "0045a22a6c3bacff4594cf6bdff04ccdad058dfe" #dev
client_secret = "286a25a4f3346243d3d3df265945302b7095f473" #prod

url = "https://nanohub.org/api/developer/oauth/token"
buildSchema = t.NanohubUtils.nanohubTool(tp, url_token=url, client_id=client_id, client_secret=client_secret,toolname="nsoptics", user=auth_data['username'], pwd=auth_data['password'])

ThemeProvider = t.MaterialBuilder.ThemeProvider( "theme_default" )

AppBar = t.MaterialBuilder.AppBar(state="DrawerIsVisible", styles=("AppBarStyle", ["bar_shifted", "bar_normal"]), title="Nanosphere Optics Lab")
Drawer = t.MaterialBuilder.Drawer(state="DrawerIsVisible", variant="persistent" )

Grid = t.TeleportElement(t.MaterialContent(elementType="Grid"))
Grid.content.attrs["container"] = True
Grid.content.attrs["direction"] = "column"

Grid.addContent(t.MaterialBuilder.Button(title = "Extinction Cross Section", onClickButton = [
  { "type": "stateChange", "modifies": "view","newState": 0 },
  NsopticsBuilder.loadExtinctionCrossSection(tp)
]))
Grid.addContent(t.MaterialBuilder.Button(title = "Scattering Cross Section", onClickButton = [
  { "type": "stateChange", "modifies": "view","newState": 0 },
  NsopticsBuilder.loadScatteringCrossSection(tp)
]))
Grid.addContent(t.MaterialBuilder.Button(title = "Absortion Cross section", onClickButton = [
  { "type": "stateChange", "modifies": "view","newState": 0 },
  NsopticsBuilder.loadAbsortionCrossSection(tp)
]))
Grid.addContent(t.MaterialBuilder.Button(title = "Real(Dielectric Constant)", onClickButton = [
  { "type": "stateChange", "modifies": "view","newState": 0 },
  NsopticsBuilder.loadRealDielectric(tp)
]))
Grid.addContent(t.MaterialBuilder.Button(title = "Imaginary(Dielectric Constant)", onClickButton = [
  { "type": "stateChange", "modifies": "view","newState": 0 },
  NsopticsBuilder.loadImaginaryDielectric(tp)
]))
#Grid.addContent(t.MaterialBuilder.Button(title = "Settings", onClickButton=setSettings))

    
Drawer.content.children.append(Grid)

Gridv = t.TeleportElement(t.MaterialContent(elementType="Grid"))
Gridv.content.attrs["container"] = True
Gridv.content.attrs["direction"] = "column"

Gridh = t.TeleportElement(t.MaterialContent(elementType="Grid"))
Gridh.content.attrs["container"] = True
Gridh.content.attrs["direction"] = "row"
    
Gridh.addContent(Drawer)

Gridv.addContent(AppBar)
Gridv.addContent(Gridh)
ThemeProvider.addContent(Gridv)


logo = t.TeleportElement(t.TeleportContent(elementType="container"))
logo.content.attrs["className"] = "pnLabLogo"
div = t.TeleportElement(t.TeleportContent(elementType="container"))
div.content.attrs["className"] = "pnLabHeader"
div.addContent(logo)
AppBar.content.children[0].addContent(logo)



Component.addNode(ThemeProvider)

plotly_widget = {
  "type": "dynamic",
  "content": {
    "referenceType": "local",
    "id": "setPlotlyRef"
  }    
}

settings_widget = {
  "type": "dynamic",
  "content": {
    "referenceType": "local",
    "id": "setSettingsRef"
  }    
}
url_sim = "https://nanohub.org/api/tools/run"

Grid.addContent( NsopticsBuilder.NsopticsSettings(tp, ref=settings_widget, url=url_sim) )


plotly_widget_state = {
  "type": "dynamic",
  "content": {
    "referenceType": "state",
    "id": "data"
  }    
}
plotly_layout_state = {
  "type": "dynamic",
  "content": {
    "referenceType": "state",
    "id": "layout"
  }    
}
plotly_frames_state = {
  "type": "dynamic",
  "content": {
    "referenceType": "state",
    "id": "frames"
  }    
}
BasePlot = t.FormHelper.ConditionalGroup(
  Component, [
    t.PlotlyBuilder.BasePlot( tp, 
      style_state="AppBarStyle", 
      data=plotly_widget_state, 
      layout=plotly_layout_state, 
      frames=plotly_frames_state, 
      ref=plotly_widget
    )
  ], "view", 0
)

BasePlot.node.content.style = {
  "height": "calc(100vh - 80px)",
  "width": "100%",
}

Gridh.addContent(BasePlot)


#print(json.dumps(tp.__json__(), indent=1))
tp.buildReact("nsoptics.html")