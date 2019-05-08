# Nanohubtools

A set of tools to run on nanohub

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
nt.Qdotexplorer(auth_data, parameters={'Number of States'}, mode='split-right')

```

