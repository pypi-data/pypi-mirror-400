# sbox
A simple secret manager with Pydantic model migration support

## Key Features
- **Auto-Migration:** If you add or remove fields in your Pydantic model, `sbox` automatically updates your JSON vault.
- **Interactive Mode:** Missing secrets? `sbox` will ask for them in the CLI.
- **Environment Support:** Easily override secrets using Environment Variables.
- **Security:** Automatically sets file permissions to `600` on Linux systems.

## Installation
```bash
pip install sbox
```

## How to use
1. Create `SBox` object:
```python
from sbox import SBox

box = SBox()
```
2. Create Pydantic model:
```python
from sbox import SBox

from pydantic import BaseModel

box = SBox()

class MyModel(BaseModel):
    smth: str
```
3. Parse it and save to file
```python
from sbox import SBox

from pydantic import BaseModel

box = SBox()

class MyModel(BaseModel):
    smth: str

box.parse(MyModel)
box.saveall()
```
4. Get the fields
```python
from sbox import SBox

from pydantic import BaseModel

box = SBox()

class MyModel(BaseModel):
    smth: str

box.parse(MyModel)
box.saveall()

mymodel = box.get_model(MyModel) # Or just box.MyModel
print(f'smth: {mymodel.smth}')
```