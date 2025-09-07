# PET_CT viskit

PET_CT viskit is a collection of scripts and small modules for preparing, registering,
and visualizing PET/CT volumes.  It was built for interactive exploration of DICOM
studies and for assembling small research workflows.

## Installation

```bash
pip install -r requirements.txt
```

The requirements file lists core dependencies such as pydicom, VTK, SimpleITK,
PyVista and other utilities needed for visualization and registration.  Some optional
components (e.g., `ssim3d.py`) require PyTorch.

## Tools

### DICOM reader
Utilities for loading paired CT and PET series from folders of DICOM files.  The reader
handles cropping, normalization and basic mutual‑information based registration and is
used throughout the project.

```python
from dicom_reader.dicom_reader import DicomReader
reader = DicomReader(ct_path, pet_path)
ct, pet = reader.load()
```

### Registration
Scripts built on SimpleITK to perform rigid registration between volumes.  A small GUI
is available for monitoring progress and transforms can be saved and applied later.

```python
from registration.registration import SitkRegister
reg = SitkRegister('fixed_volume', 'moving_volume')
reg.register()
```

### Segmentation
`segmentation/drawSegment.py` opens an OpenCV window that lets users draw polygonal
regions of interest on image slices.  The annotations are stored and can be converted
into 3‑D masks.

```bash
python segmentation/drawSegment.py
```

### Viewer
The `viewer` package wraps PyVista helpers for quick 3‑D visualization.  Functions such
as `pvplot_multiview` and `pvplot_overlayvolume` render volumes, overlay segmentations
and create GIF animations used by other modules.

```python
from viewer.util import pvplot_multiview
pvplot_multiview([volume], 'output_name', ['View'], ['bone'])
```

### Additional scripts
* `dataprep.py` – batch convert DICOM data to NumPy arrays, perform registration and apply
  stored transforms.
* `assembleResult.py` – join multiple prediction CSV files into a single table.
* `ssim3d.py` – PyTorch implementation of 2‑D and 3‑D Structural Similarity metrics.
* Jupyter notebooks (`dataprep.ipynb`, `dataprep_segmentation.ipynb`, `drawROI.ipynb`) show
  example workflows and interactive exploration.

## License

This project is provided as‑is for research and educational purposes.
