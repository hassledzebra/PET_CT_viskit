import numpy as np
import matplotlib.pyplot as plt

import SimpleITK as sitk

import pyvista as pv

from util import pvplot_multiview
import os

def apply_transform(tranform_folder, fixed_file, moving_file):
    #tranform_folder = 'p1t1'
    #transform_path = os.path.join(tranform_folder , moving_file.split('/')[0]+'transform.tfm')
    transform = sitk.ReadTransform(tranform_folder)
    #fixed_file = 'p1t1/p1t1pet1'
    fixed_np_path = fixed_file + '_raw.npy'
    moving_np_path = moving_file + '_raw.npy'

    fixed_np = np.load(fixed_np_path)
    moving_np = np.load(moving_np_path)

    fixed_image = sitk.GetImageFromArray(fixed_np)
    moving_image = sitk.GetImageFromArray(moving_np)

    moving_resampled = sitk.Resample(moving_image, fixed_image, transform, sitk.sitkNearestNeighbor, 1, moving_image.GetPixelID())
    moving_r_array = sitk.GetArrayFromImage(moving_resampled)

    out = moving_r_array

    # fixed_idx = fixed_np > 0
    # moving_np= moving_np * fixed_idx
    # moving_r_array = moving_r_array * fixed_idx

    # pvplot_multiview([fixed_np, moving_np, moving_r_array], moving_np_path.split('.')[-2]+'reg_comp',
    #                     ['Fixed','moving','registered'],['jet','jet','jet'], c_clims=([0,1],[0,1],[0,1]))
    pvplot_multiview([fixed_np, moving_np, moving_r_array], moving_np_path.split('.')[-2]+'reg_comp',
                        ['Fixed','moving','registered'],['jet','jet','jet'])

    np.save(moving_np_path.split('.')[-2]+'_t.npy', out)