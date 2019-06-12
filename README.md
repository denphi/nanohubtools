# Nanohubtools

A set of tools/apps to run on nanohub

## Installation


```bash
pip install nanohubtools
```

## Usage


```python
import nanohubtools as nt
auth_data = {
  'client_id': XXXXXXXX,
  'client_secret': XXXXXXXX,
  'grant_type': 'password',
  'username': XXXXXXXX,
  'password': XXXXXXXX
}
# modal defines if the container outputs to use FloatView or standard ipywidgets Output
# mode defines the positions of new windows of Floatview is enabled
tool = nt.Qdotexplorer(auth_data, parameters={'Number of States'}, modal=True, mode='split-right')
tool.loadExperiment('IDSESSION') If an experiment was created befores
```


## Available Nanohub Tools

### CrystalViewerMaterial, supported by [Crystal Viewer Tool](https://nanohub.org/resources/crystal_viewer)
```python
    nt.CrystalViewerMaterial(auth_data, modal=False)
```
![CrystalViewerMaterial](https://raw.githubusercontent.com/denphi/nanohubtools/master/images/CrystalViewerMaterial.gif)


### CrystalViewerBravais, supported by [Crystal Viewer Tool](https://nanohub.org/resources/crystal_viewer)
```python
    nt.CrystalViewerBravais(auth_data, modal=False)
```


### CrystalViewerConstructor, supported by [Crystal Viewer Tool](https://nanohub.org/resources/crystal_viewer)
```python
    nt.CrystalViewerConstructor(auth_data, modal=False)
```

### SimpleQuantumDot, supported by [Quantum Dot Lab ](https://nanohub.org/resources/qdot/)
```python
    nt.SimpleQuantumDot(auth_data, modal=False)
```

### StackedQuantumDot, supported by [Quantum Dot Lab ](https://nanohub.org/resources/qdot/)
```python
    nt.StackedQuantumDot(auth_data, modal=False)
```


### PNToy, supported by [PN Junction Lab] (https://nanohub.org/resources/pntoy)
```python
    nt.PNToy(auth_data, modal=False)
```


### Driftdiffusionlab, supported by [Drift-Diffusion Lab] (https://nanohub.org/resources/semi)
```python
    nt.Driftdiffusionlab(auth_data, modal=False)
```

