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

# to get username and password, register on nanohub.org (https://nanohub.org/register/)
# to get client id and secret, create a web application (https://nanohub.org/developer/api/applications/new), use "https://127.0.0.1" as Redirect URL

tool = nt.Qdotexplorer(auth_data, parameters={'Number of States'}, modal=True, mode='split-right')

# modal defines if the container outputs to use FloatView or standard ipywidgets Output
# mode defines the positions of new windows of Floatview is enabled

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
![CrystalViewerBravais](https://raw.githubusercontent.com/denphi/nanohubtools/master/images/CrystalViewerBravais.gif)


### CrystalViewerConstructor, supported by [Crystal Viewer Tool](https://nanohub.org/resources/crystal_viewer)
```python
    nt.CrystalViewerConstructor(auth_data, modal=False)
```

### CrystalViewerSimplified, supported by [Crystal Viewer Tool](https://nanohub.org/resources/crystal_viewer)
```python
    nt.CrystalViewerConstructor(auth_data, modal=False)
```


### SimpleQuantumDot, supported by [Quantum Dot Lab ](https://nanohub.org/resources/qdot/)
```python
    nt.SimpleQuantumDot(auth_data, modal=False)
```
![SimpleQuantumDot](https://raw.githubusercontent.com/denphi/nanohubtools/master/images/SimpleQuantumDot.gif)


### StackedQuantumDot, supported by [Quantum Dot Lab ](https://nanohub.org/resources/qdot/)
```python
    nt.StackedQuantumDot(auth_data, modal=False)
```


### PNToy, supported by [PN Junction Lab] (https://nanohub.org/resources/pntoy)
```python
    nt.PNToy(auth_data, modal=False)
```
![PNToy](https://raw.githubusercontent.com/denphi/nanohubtools/master/images/PNToy.gif)


### Driftdiffusionlab, supported by [Drift-Diffusion Lab] (https://nanohub.org/resources/semi)
```python
    nt.Driftdiffusionlab(auth_data, modal=False)
```
![Driftdiffusionlab](https://raw.githubusercontent.com/denphi/nanohubtools/master/images/Driftdiffusionlab.gif)


### DFTExplorer, supported by [DFT calculations with Quantum ESPRESSO] (https://nanohub.org/resources/dftqe)
```python
    nt.DFTExplorer(auth_data, modal=False)
```
![DFTExplorer](https://raw.githubusercontent.com/denphi/nanohubtools/master/images/DFTExplorer.gif)

