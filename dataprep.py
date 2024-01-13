

from time import time
from dicom_reader import DicomReader
from registration import SitkRegister
from applyTransform import apply_transform
import os

def path_prep(rootpath, patient_ID):
    patient_ID = str(patient_ID)
    ct_path = []
    ct_path.append(os.path.join(rootpath , "P"+ patient_ID, "p" + patient_ID + "t1", "p" + patient_ID + "t1ct1"))
    ct_path.append(os.path.join(rootpath , "P"+ patient_ID, "p" + patient_ID + "t1", "p" + patient_ID + "t1ct2"))
    ct_path.append(os.path.join(rootpath , "P"+ patient_ID, "p" + patient_ID + "t2", "p" + patient_ID + "t2ct1"))

    pet_path = []
    pet_path.append(os.path.join(rootpath , "P"+ patient_ID, "p" + patient_ID + "t1", "p" + patient_ID + "t1pet1"))
    pet_path.append(os.path.join(rootpath , "P"+ patient_ID, "p" + patient_ID + "t1", "p" + patient_ID + "t1pet2"))
    pet_path.append(os.path.join(rootpath , "P"+ patient_ID, "p" + patient_ID + "t2", "p" + patient_ID + "t2pet1"))

    return ct_path, pet_path

def path_prep_reg(rootpath, patient_ID):
    patient_ID = str(patient_ID)
    ct_path = []
    ct_path.append(os.path.join(rootpath ,"p" + patient_ID + "t1", "p" + patient_ID + "t1ct1"))
    ct_path.append(os.path.join(rootpath ,"p" + patient_ID + "t1", "p" + patient_ID + "t1ct2"))
    ct_path.append(os.path.join(rootpath ,"p" + patient_ID + "t2", "p" + patient_ID + "t2ct1"))

    pet_path = []
    pet_path.append(os.path.join(rootpath ,"p" + patient_ID + "t1", "p" + patient_ID + "t1pet1"))
    pet_path.append(os.path.join(rootpath ,"p" + patient_ID + "t1", "p" + patient_ID + "t1pet2"))
    pet_path.append(os.path.join(rootpath ,"p" + patient_ID + "t2", "p" + patient_ID + "t2pet1"))

    return ct_path, pet_path

def finetune_volume(rootpath, patient_ID, timepoint,  threshold, cropsize, shift, translation):
    # timepoint: 0: t1ct1, t1pet1, 1: t1ct2, t1pet2, 2: t2ct1, t2pet2
    ct_path, pet_path = path_prep(rootpath, patient_ID)
    dicomreader = DicomReader(ct_path[timepoint], pet_path[timepoint], threshold, cropsize, shift, translation)
    dicomreader.save_dicom()

#rootpath = os.path.dirname('..')
rootpath = os.path.dirname(os.getcwd())
#patient_ID_list = [1,2,3,4,5,6,7,8,9,10,11,13,14,16,17,18,19,20,21]
patient_ID_list = [1]

for patient_ID in  patient_ID_list:
    ct_path, pet_path = path_prep(rootpath, patient_ID)

    for i in range(len(ct_path)):
        print('working on:' + ct_path[i])
        dicomreader = DicomReader(ct_path[i], pet_path[i])
        dicomreader.save_dicom()

## Fine tune volume crop
#finetune_volume(rootpath, 1, 0,  200, (120, 120, 240), (0, 20, 20), (0, -8, -2)) # manuregistration for patient 1 time point 3
#finetune_volume(rootpath, 1, 1,  200, (120, 120, 240), (0, 20, 20), (0, 0, 0)) # manuregistration for patient 1 time point 3
#finetune_volume(rootpath, 1, 2,  200, (120, 120, 240), (0, 20, 20), (0, 0, 0)) # manuregistration for patient 1 time point 3
# finetune_volume(rootpath, 2, 0,  200, (160, 160, 240), (0, 20, 20), (0, 0, 0)) # larger VOI for patient 2
# finetune_volume(rootpath, 2, 1,  200, (160, 160, 240), (0, 20, 20), (0, 0, 0)) # larger VOI for patient 2
# finetune_volume(rootpath, 2, 2,  200, (160, 160, 240), (0, 20, 20), (0, 0, 0)) # larger VOI for patient 2
# finetune_volume(rootpath, 4, 2,  200, (120, 120, 240), (0, 20, 60),(0, 0, 0)) # move VOI up for patient 4 timepoint 3
# finetune_volume(rootpath, 6, 0,  200, (120, 120, 240), (0, 20, 60)) # move VOI up for patient 6 timepoint 1
# finetune_volume(rootpath, 6, 0,  200, (120, 120, 240), (0, 20, 60)) # move VOI up for patient 6 timepoint 2
# finetune_volume(rootpath, 6, 0,  200, (120, 120, 240), (0, 20, 60)) # move VOI up for patient 6 timepoint 3
# finetune_volume(rootpath, 7, 0,  200, (120, 120, 240), (0, 20, 60)) # move VOI up for patient 6 timepoint 1
# finetune_volume(rootpath, 7, 0,  200, (120, 120, 240), (0, 20, 60)) # move VOI up for patient 6 timepoint 2
# finetune_volume(rootpath, 7, 0,  200, (120, 120, 240), (0, 20, 60)) # move VOI up for patient 6 timepoint 3
# finetune_volume(rootpath, 8, 0,  200, (120, 120, 240), (0, 20, 60)) # move VOI up for patient 6 timepoint 1
# finetune_volume(rootpath, 8, 0,  200, (120, 120, 240), (0, 20, 60)) # move VOI up for patient 6 timepoint 2
# finetune_volume(rootpath, 8, 0,  200, (120, 120, 240), (0, 20, 60)) # move VOI up for patient 6 timepoint 3


## Register now
rootpath = os.path.join(os.path.dirname(os.getcwd()),'python')
patient_ID_list = [4]
for patient_ID in  patient_ID_list:
    ct_path, pet_path = path_prep_reg(rootpath, patient_ID)
    fixed_file_ct = ct_path[0]
    moving_file_ct1 = ct_path[1]
    moving_file_ct2 = ct_path[2]

    fixed_file_pet = pet_path[0]
    moving_file_pet1 = pet_path[1]
    moving_file_pet2 = pet_path[2]
    
    # register t1
    new_register1 = SitkRegister(fixed_file_ct, moving_file_ct1)
    new_register1.register()
    new_register1.plotRegister_result()

    

    # register t2
    new_register1 = SitkRegister(fixed_file_ct, moving_file_ct2)
    new_register1.register()
    new_register1.plotRegister_result()

    
# apply transform
for patient_ID in  patient_ID_list:
    _, pet_path = path_prep_reg(rootpath, patient_ID)
  
    fixed_file_pet = pet_path[0]
    moving_file_pet1 = pet_path[1]
    moving_file_pet2 = pet_path[2]
    
    split_moving_path = os.path.normpath(moving_file_pet1).split(os.path.sep)
    
    transform_path= os.path.join(rootpath,split_moving_path[-2],split_moving_path[-2])+'transform.tfm'
    
    apply_transform(transform_path, fixed_file_pet, moving_file_pet1)
    split_moving_path = os.path.normpath(moving_file_pet2).split(os.path.sep)
    transform_path = os.path.join(rootpath,split_moving_path[-2], split_moving_path[-2])+'transform.tfm'
    apply_transform(transform_path, fixed_file_pet, moving_file_pet2)