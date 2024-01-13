import os
import csv
import numpy as np

patient_ID = [1,2,3,4,5,6,7,8,9,10,11,13,14,16,17,18,19,20]
# patient_ID = [1,2]
rootpath = os.path.join(os.path.dirname(os.getcwd()),'python')

def path_prep_data(rootpath, patient_ID):
    patient_ID = str(patient_ID)

    
    path = os.path.join(rootpath ,"p" + patient_ID + "_pred.csv")

    return  path

assembly = []

for patient in patient_ID:
    rows = []
    path = path_prep_data(rootpath, patient)
    print(path)
    with open(path) as f:
    # create the csv writer
        reader = csv.reader(f)
        line_count = 0
        for row in reader:
            rows.append(row)
    # print(rows)
    transposed = np.float128(np.array(rows).T.reshape(-1)).tolist()
    assembly.append(transposed)
# print(assembly)
savepath = os.path.join(rootpath, "pred_assembled.csv")
with open(savepath, 'w') as f:
    # create the csv writer
    writer = csv.writer(f)
    writer.writerows(assembly)
    