from re import S
import numpy as np
import matplotlib.pyplot as plt

import SimpleITK as sitk

import pyvista as pv
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from . import registration_gui as rgui

from viewer.util import normalized_3d, pvplotgif, save_transform

# import gui
# import registration_gui as rgui

class SitkRegister():
    def __init__(self, fixed_file,  moving_file, method='correlation'):
    #fixed_file = 'p1t1/p1t1ct1'
    #moving_file = 'p1t1/p1t1ct2'
        self.fixed_file = fixed_file 
        self.moving_file = moving_file
        self.method = method 

    def register(self):

        ct1 = np.load(self.fixed_file + '_raw.npy' ) # fixed image
        ct2 = np.load(self.moving_file+ '_raw.npy') # moving image

        ct1 = ct1 * (ct1 > 200)
        ct2 = ct1 * (ct2 > 200)

        # ct1 = normalized_3d(ct1)
        # ct2 = normalized_3d(ct2)

        self.ct1 = ct1
        self.ct2 = ct2

        #ct1 = onehot_3d(ct1, 200)
        #ct2 = onehot_3d(ct2, 200)


        fixed_image = sitk.GetImageFromArray(ct1)
        moving_image = sitk.GetImageFromArray(ct2)

        global_transform = sitk.CenteredTransformInitializer(fixed_image, 
                                                            moving_image, 
                                                            # sitk.AffineTransform(3), 
                                                            # sitk.Euler3DTransform(),
                                                            sitk.ScaleVersor3DTransform(),
                                                            # sitk.ScaleSkewVersor3DTransform(),
                                                            #sitk.BSplineTransform(3),
                                                            # sitk.VersorRigid3DTransform(),
                                                            #sitk.Similarity3DTransform(),
                                                            sitk.CenteredTransformInitializerFilter.GEOMETRY)
                                                            #sitk.CenteredTransformInitializerFilter.MOMENTS)

        # gui.RegistrationPointDataAquisition(fixed_image, moving_image, figure_size=(80,40), known_transformation=initial_transform, 
        #                                     fixed_window_level= [0, 255], moving_window_level=[0, 255])

        registration_method = sitk.ImageRegistrationMethod()

        # Similarity metric settings.
        if self.method == 'mutual_information':
            registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins=1)
        elif self.method == 'correlation':
            # registration_method.SetMetricAsCorrelation() # this is important
            registration_method.SetMetricAsMeanSquares()
            #registration_method.SetMetricAsDemons()
            #registration_method.SetMetricAsANTSNeighborhoodCorrelation(2)
        #
        # registration_method.SetMetricSamplingStrategy(registration_method.REGULAR)
        registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
        registration_method.SetMetricSamplingPercentage(0.5)

        registration_method.SetInterpolator(sitk.sitkNearestNeighbor)
        # registration_method.SetInterpolator(sitk.sitkBSpline)

        # Exhausive registration
        exhausive = False
        if exhausive:
            registration_method.SetOptimizerAsExhaustive(numberOfSteps=[0,1,1,0,0,0], stepLength = np.pi)
            registration_method.SetOptimizerScales([1,1,1,1,1,1])

        # Optimizer settings.
        registration_method.SetOptimizerAsGradientDescent(learningRate=1, numberOfIterations=300,
                                                        convergenceMinimumValue=1e-9, convergenceWindowSize=10)
        registration_method.SetOptimizerScalesFromPhysicalShift()

        # Setup for the multi-resolution framework.            
        # registration_method.SetShrinkFactorsPerLevel(shrinkFactors = [4,2,1])
        # registration_method.SetSmoothingSigmasPerLevel(smoothingSigmas=[2,1,1])
        # registration_method.SmoothingSigmasAreSpecifiedInPhysicalUnitsOn()

        # Don't optimize in-place, we would possibly like to run this cell multipl times.
        registration_method.SetInitialTransform(global_transform, inPlace=True) #has to use True


        monitor_reg = False
        if monitor_reg:
            registration_method.AddCommand(sitk.sitkStartEvent, rgui.start_plot)
            registration_method.AddCommand(sitk.sitkEndEvent, rgui.end_plot)
            registration_method.AddCommand(sitk.sitkMultiResolutionIterationEvent, rgui.update_multires_iterations) 
            registration_method.AddCommand(sitk.sitkIterationEvent, lambda: rgui.plot_values(registration_method))


        registration_method.Execute(fixed_image, moving_image)

        # Always check the reason optimization terminated.
        print('Final metric value: {0}'.format(registration_method.GetMetricValue()))
        print('Optimizer\'s stopping condition, {0}'.format(registration_method.GetOptimizerStopConditionDescription()))

        moving_resampled = sitk.Resample(moving_image, fixed_image, global_transform, sitk.sitkBSpline, 0, moving_image.GetPixelID())
        moving_r_array = sitk.GetArrayFromImage(moving_resampled)
        self.moving_r_array = moving_r_array

        print(global_transform)
        save_transform(global_transform, os.path.join(self.moving_file.split('/')[0], self.moving_file.split('/')[0]+'transform'))
    
    def plotRegister_result(self):
        fixed_idx = self.ct1 > 0
        ct2 = self.ct2 * fixed_idx
        moving_r_array = self.moving_r_array * fixed_idx

        pvplotgif(self.ct1, self.fixed_file + '_fixed','Fixed','bone')
        pvplotgif(ct2, self.moving_file + '_moving','Moving','bone')
        pvplotgif(moving_r_array,  self.moving_file + '_registered','Registered','bone')

            