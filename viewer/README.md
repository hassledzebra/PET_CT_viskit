# 3D Viewer

The `viewer` package hosts visualization utilities based on PyVista and Matplotlib. These
functions help render volumes, overlay segmentations, and create GIF animations.

## Example

```python
from viewer.util import pvplot_multiview
pvplot_multiview([volume], 'output_name', ['View'], ['bone'])
```

The utilities are reused across the project by other tools such as the DICOM reader and
registration modules.
