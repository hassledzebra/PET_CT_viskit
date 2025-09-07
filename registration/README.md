# Registration Tools

This folder contains scripts for image registration.

- `registration.py` performs rigid registration between volumes using SimpleITK.
- `applyTransform.py` applies a saved transform to a moving image.
- `registration_gui.py` and `gui.py` provide interactive widgets for monitoring registration.

## Usage

```python
from registration.registration import SitkRegister
reg = SitkRegister('fixed_path', 'moving_path')
reg.register()
```
