from nbformat import current_nbformat
from pydicom import dcmread
from pydicom.pixel_data_handlers.util import apply_modality_lut
#from pydicom.data import get_testdata_file
from matplotlib import pyplot as plt
import os
from os import listdir
from os.path import isfile, join
import numpy as np

from scipy.ndimage import zoom
from util import pvplotgif, pvplot_multiview, pvplot_overlayvolume, onehot_3d, normalize_3d,normalize_8bit
import SimpleITK as sitk

import pyvista as pv

from matplotlib.colors import ListedColormap
import matplotlib.pyplot as plt


#from vtk.util import numpy_support
#import vtk

# Define the colors we want to use
blue = np.array([12 / 256, 238 / 256, 246 / 256, 1.0])
black = np.array([11 / 256, 11 / 256, 11 / 256, 1.0])
grey = np.array([189 / 256, 189 / 256, 189 / 256, 1.0])
yellow = np.array([255 / 256, 247 / 256, 0 / 256, 1.0])
red = np.array([1.0, 0.0, 0.0, 1.0])

mapping = np.linspace(0, 100, 256)
newcolors = np.empty((256, 4))
newcolors[mapping >= 80] = red
newcolors[mapping < 80] = grey
newcolors[mapping < 55] = yellow
newcolors[mapping < 30] = blue
newcolors[mapping < 1] = black

# Make the colormap from the listed colors
my_colormap = ListedColormap(newcolors)



class DicomReader:
    def __init__(self, ct_path, pet_path, threshold=200, cropsize=(120, 120, 240), shift=(0, 20, 20), translation=(0,0,0), flipct = False):
        self.ct_path = ct_path
        self.pet_path = pet_path
        self.cropsize = cropsize
        self.shift = shift
        self.threshold = threshold
        self.translation = translation
        self.flipct = flipct

    def crop_center(self, img):
        (cropx, cropy, cropz) = self.cropsize
        (shiftx, shifty, shiftz) = self.shift
        y,x,z = img.shape
        startx = x//2-(cropx//2)
        starty = y//2-(cropy//2)
        startz = z//2-(cropz//2)      
        return img[starty+shifty:starty+cropy+shifty,startx+shiftx:startx+cropx+shiftx, startz+shiftz:startz+cropz+shiftz]
    
    def register_MI(self, fixed, moving, method='mutual_information'):
        fixed_image = sitk.GetImageFromArray(fixed)
        moving_image = sitk.GetImageFromArray(moving)

        global_transform = sitk.CenteredTransformInitializer(fixed_image, 
                                                            moving_image, 
                                                            #sitk.AffineTransform(3), 
                                                            #sitk.Euler3DTransform(),
                                                            #sitk.ScaleVersor3DTransform(),
                                                            #sitk.ScaleSkewVersor3DTransform(),
                                                            #sitk.BSplineTransform(3),
                                                            sitk.VersorRigid3DTransform(),
                                                            #sitk.Similarity3DTransform(),
                                                            sitk.CenteredTransformInitializerFilter.GEOMETRY)
                                                            #sitk.CenteredTransformInitializerFilter.MOMENTS)

        # gui.RegistrationPointDataAquisition(fixed_image, moving_image, figure_size=(80,40), known_transformation=initial_transform, 
        #                                     fixed_window_level= [0, 255], moving_window_level=[0, 255])

        registration_method = sitk.ImageRegistrationMethod()

        # Similarity metric settings.
        if method == 'mutual_information':
            registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=10)
        elif method == 'correlation':
            registration_method.SetMetricAsCorrelation() # this is important
        #registration_method.SetMetricAsMeanSquares()
        #registration_method.SetMetricAsDemons()
        #registration_method.SetMetricAsANTSNeighborhoodCorrelation(2)
        #
        registration_method.SetMetricSamplingStrategy(registration_method.REGULAR)
        registration_method.SetMetricSamplingPercentage(0.5)

        #registration_method.SetInterpolator(sitk.sitkNearestNeighbor)
        registration_method.SetInterpolator(sitk.sitkBSpline)

        # Exhausive registration
        exhausive = False
        if exhausive:
            registration_method.SetOptimizerAsExhaustive(numberOfSteps=[0,1,1,0,0,0], stepLength = np.pi)
            registration_method.SetOptimizerScales([1,1,1,1,1,1])

        # Optimizer settings.
        registration_method.SetOptimizerAsGradientDescent(learningRate=1.0, numberOfIterations=100,
                                                        convergenceMinimumValue=1e-13, convergenceWindowSize=10)
        registration_method.SetOptimizerScalesFromPhysicalShift()

        # Setup for the multi-resolution framework.            
        registration_method.SetShrinkFactorsPerLevel(shrinkFactors = [4,2,1])
        registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[2,1,1])
        registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

        # Don't optimize in-place, we would possibly like to run this cell multipl times.
        registration_method.SetInitialTransform(global_transform, inPlace=True) #has to use True


        # monitor_reg = False
        # if monitor_reg:
        #     registration_method.AddCommand(sitk.sitkStartEvent, rgui.start_plot)
        #     registration_method.AddCommand(sitk.sitkEndEvent, rgui.end_plot)
        #     registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, rgui.update_multires_iterations) 
        #     registration_method.AddCommand(sitk.sitkIterationEvent, lambda: rgui.plot_values(registration_method))


        registration_method.Execute(fixed_image, moving_image)

        # Always check the reason optimization terminated.
        print('Final metric value: {0}'.format(registration_method.GetMetricValue()))
        print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))

        moving_resampled = sitk.Resample(moving_image, fixed_image, global_transform, sitk.sitkBSpline, 0, moving_image.GetPixelID())
        moving_r_array = sitk.GetArrayFromImage(moving_resampled)
        registered = moving_r_array

        return registered

    def dicom_to_vtk(self,filepath, ifpet = False):
        filenames = [f for f in listdir(filepath) if isfile(join(filepath, f))]
        raw = []

        for _, filename in  enumerate(filenames):
            file_path = os.path.join(filepath, filename)
            #file_path = r"C:/Users/McNally Group/Documents/Jenifer/P1/2012-02__Studies/11-C-0136_0001_CT_2012-02-07_150752_PET.CT.(MIC)_LD.CT.600FOV_n188__00000/1.3.46.670589.33.1.1109121314482240.23279887304083870416.dcm"
            ds = dcmread(file_path, force=True)
            if hasattr(ds, 'SliceLocation'):
            #print(ds.get('SliceLocation', '(missing)'))
                raw.append(ds)   
        if ifpet:
            raw = sorted(raw, key=lambda s: s.SliceLocation, reverse=False)
        else:
            if self.flipct:
                raw = sorted(raw, key=lambda s: s.SliceLocation, reverse=False)
            else:
                raw = sorted(raw, key=lambda s: s.SliceLocation, reverse=True)

        ps = raw[0].PixelSpacing
        ss = raw[0].SliceThickness
        
        ax_aspect = ps[1]/ps[0]
        #sag_aspect = ps[1]/ss
        cor_aspect = ss/ps[0]



        volume = [] #arr.shape
        for _, ds in  enumerate(raw):
            arr = ds.pixel_array
            arr = apply_modality_lut(arr, ds)
            volume.append(arr)

        volume = np.stack(volume, axis=2) # shape:  512, 512, Nslice,
        resize_ratio = 256/volume.shape[0]
        # volume_sitk = sitk.GetImageFromArray(volume)
        # scale = sitk.ScaleTransform(3, (1*resize_ratio, ax_aspect*resize_ratio, cor_aspect*resize_ratio))
        # resized_sitk = sitk.Resample(volume_sitk, volume_sitk, scale, sitk.sitkLinear,0)
        # resized = sitk.GetArrayFromImage(resized_sitk)
        resized = zoom(volume,(1*resize_ratio, ax_aspect*resize_ratio, cor_aspect*resize_ratio))
        if ifpet:
            resized = resized * (resized > 100) # only filter pet. Preserve soft tissue ct values
        # pvplotgif(resized, filepath + 'precrop','precrop','jet')
        cropped = self.crop_center(resized)

        # threshold = 1000
        high_idx = cropped > self.threshold
        high_idx = high_idx.astype(int)

        filtered = cropped * high_idx

        #VTK_data = numpy_support.numpy_to_vtk(num_array=volume.ravel(), deep=True, array_type=vtk.VTK_FLOAT)
        

        return resized, filtered, high_idx

    #ct_path = r"../P1/p1t1/p1t1ct1/"
    #pet_path = r"../P1/p1t1/p1t1pet1/"
    def save_dicom(self):
        split_ct_path = os.path.normpath(self.ct_path).split(os.path.sep)
        split_pet_path = os.path.normpath(self.pet_path).split(os.path.sep)
        outputpath = split_ct_path[-2]
        

        #cropsize = (120, 120, 240)
        #shift = (0, 20, 20)

        ct_raw, ct_data, ct_high_idx = self.dicom_to_vtk(self.ct_path)
        pet_raw, _, _  = self.dicom_to_vtk(self.pet_path, True)
        pet_reg = []
        
        translation = sitk.TranslationTransform(3, self.translation) #translation: (down, right, forward)
        rigid_euler = sitk.Euler3DTransform()
        rigid_euler.SetTranslation(translation.GetOffset())
        pet_reg = sitk.Resample(sitk.GetImageFromArray(pet_raw), sitk.GetImageFromArray(ct_raw), rigid_euler, sitk.sitkBSpline, 0, sitk.GetImageFromArray(pet_raw).GetPixelID())
        pet_reg = sitk.GetArrayFromImage(pet_reg)


        #pet_reg = self.register_MI(ct_raw, pet_raw, method='correlation')
        pet_reg_1 = self.crop_center(pet_reg)
        pet_data = []
        pet_data = pet_reg_1 * ct_high_idx

        clim_ct = [np.min(ct_raw), np.max(ct_raw)]
        # clim_pet = [np.min(pet_reg_1), np.max(pet_reg_1)]
        clim_pet = [np.min(pet_reg), np.max(pet_reg)]
        # print(clim_pet)

        # # pet_norm = normalize_3d(pet_data, clim_pet)
        ct_norm = normalize_3d(ct_raw, clim_ct)
        pet_norm = normalize_3d(pet_reg, clim_pet)

        pvplot_overlayvolume([ct_raw,pet_reg], os.path.join(outputpath, split_ct_path[-1])+'_overlay', 'overlay', ['bone','jet'], (200, 1000))
        #pvplot_overlayvolume([ct_raw,pet_reg_1], os.path.join(outputpath, split_ct_path[-1])+'_overlay', 'overlay', ['bone','jet'], (200, 0.001))

        # pvplot_multiview([ct_data, pet_data*(pet_data > 1000)], os.path.join(outputpath, split_ct_path[-1]),
                            # ['CT','PET'],['bone','jet'], (clim_ct,clim_pet))
        #pvplot_multiview([ct_data, pet_data*(pet_norm > 0.001)], os.path.join(outputpath, split_ct_path[-1]),
                           # ['CT','PET'],['bone','jet'], (clim_ct,[0,1]))

        if os.path.isdir(outputpath) == False:
            os.mkdir(outputpath)

        ct_name = os.path.join(outputpath, split_ct_path[-1]+'.npy')
        pet_name = os.path.join(outputpath, split_pet_path[-1]+'.npy')

        ct_raw_name = os.path.join(outputpath, split_ct_path[-1]+'_raw.npy')
        pet_raw_name = os.path.join(outputpath, split_pet_path[-1]+'_raw.npy')
        pet_norm_name = os.path.join(outputpath, split_pet_path[-1]+'_norm.npy')

        idx_name = os.path.join(outputpath, split_ct_path[-1]+'_idx.npy')

        np.save(ct_name, ct_data)
        np.save(pet_name, pet_data)
        np.save(ct_raw_name, ct_raw)
        np.save(pet_raw_name, pet_reg)
        np.save(pet_norm_name, pet_norm)
        np.save(idx_name, ct_high_idx)
        # h5f = h5py.File(ct_name, 'w')
        # h5f.create_dataset(os.path.join(outputpath, 'ct_data'), data=ct_data)
        # h5f.create_dataset(os.path.join(outputpath, 'pet_data'), data=pet_data)
        # h5f.close()






