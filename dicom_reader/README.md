# DICOM Reader

This module provides utilities for loading CT and PET series from DICOM directories.

## Usage

```python
from dicom_reader.dicom_reader import DicomReader
reader = DicomReader(ct_path, pet_path)
ct, pet = reader.load()
```

The reader includes cropping, normalization, and registration helpers and relies on the
visualization utilities in `viewer`.
