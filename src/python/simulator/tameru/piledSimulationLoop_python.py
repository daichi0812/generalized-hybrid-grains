import numpy as np

PYTHON_PATH="python"

RUN_NUM=1

# set working directory
WORKING_DIR = []
for i in np.arange(0,RUN_NUM):
    WORKING_DIR.append("")
"""
WORKING_DIR[0]="./IOData/Circle/22/"
WORKING_DIR[1]="./IOData/Circle/11/"
"""
WORKING_DIR[0]="./IOData/Circle/12/"
"""
WORKING_DIR[3]="./IOData/Circle/13/"
WORKING_DIR[4]="./IOData/Circle/21/"
WORKING_DIR[5]="./IOData/Circle/31/"

WORKING_DIR[6]="./IOData/L/22/"
WORKING_DIR[7]="./IOData/L/11/"
WORKING_DIR[8]="./IOData/L/12/"
WORKING_DIR[9]="./IOData/L/13/"
WORKING_DIR[10]="./IOData/L/21/"
WORKING_DIR[11]="./IOData/L/31/"


WORKING_DIR[12]="./IOData/Pentagon/22/"
WORKING_DIR[13]="./IOData/Pentagon/11/"
WORKING_DIR[14]="./IOData/Pentagon/12/"
WORKING_DIR[15]="./IOData/Pentagon/13/"
WORKING_DIR[16]="./IOData/Pentagon/21/"
WORKING_DIR[17]="./IOData/Pentagon/31/"

WORKING_DIR[18]="./IOData/Square/22/"
WORKING_DIR[19]="./IOData/Square/11/"
WORKING_DIR[20]="./IOData/Square/12/"
WORKING_DIR[21]="./IOData/Square/13/"
WORKING_DIR[22]="./IOData/Square/21/"
WORKING_DIR[23]="./IOData/Square/31/"

WORKING_DIR[24]="./IOData/Star/22/"
WORKING_DIR[25]="./IOData/Star/11/"
WORKING_DIR[26]="./IOData/Star/12/"
WORKING_DIR[27]="./IOData/Star/13/"
WORKING_DIR[28]="./IOData/Star/21/"
WORKING_DIR[29]="./IOData/Star/31/"

WORKING_DIR[30]="./IOData/Triangle/22/"
WORKING_DIR[31]="./IOData/Triangle/11/"
WORKING_DIR[32]="./IOData/Triangle/12/"
WORKING_DIR[33]="./IOData/Triangle/13/"
WORKING_DIR[34]="./IOData/Triangle/21/"
WORKING_DIR[35]="./IOData/Triangle/31/"
"""

# set object files
OBJECT_FILE = []
for i in np.arange(0,RUN_NUM):
    OBJECT_FILE.append("")
    """
OBJECT_FILE[0]="circle22.h5"
OBJECT_FILE[1]="circle11.h5"
"""
OBJECT_FILE[0]="circle12.h5"
"""
OBJECT_FILE[3]="circle13.h5"
OBJECT_FILE[4]="circle21.h5"
OBJECT_FILE[5]="circle31.h5"

OBJECT_FILE[6]="l22.h5"
OBJECT_FILE[7]="l11.h5"
OBJECT_FILE[8]="l12.h5"
OBJECT_FILE[9]="l13.h5"
OBJECT_FILE[10]="l21.h5"
OBJECT_FILE[11]="l31.h5"

OBJECT_FILE[12]="pentagon22.h5"
OBJECT_FILE[13]="pentagon11.h5"
OBJECT_FILE[14]="pentagon12.h5"
OBJECT_FILE[15]="pentagon13.h5"
OBJECT_FILE[16]="pentagon21.h5"
OBJECT_FILE[17]="pentagon31.h5"

OBJECT_FILE[18]="square22.h5"
OBJECT_FILE[19]="square11.h5"
OBJECT_FILE[20]="square12.h5"
OBJECT_FILE[21]="square13.h5"
OBJECT_FILE[22]="square21.h5"
OBJECT_FILE[23]="square31.h5"

OBJECT_FILE[24]="star22.h5"
OBJECT_FILE[25]="star11.h5"
OBJECT_FILE[26]="star12.h5"
OBJECT_FILE[27]="star13.h5"
OBJECT_FILE[28]="star21.h5"
OBJECT_FILE[29]="star31.h5"

OBJECT_FILE[30]="rriangle22.h5"
OBJECT_FILE[31]="rriangle11.h5"
OBJECT_FILE[32]="rriangle12.h5"
OBJECT_FILE[33]="rriangle13.h5"
OBJECT_FILE[34]="rriangle21.h5"
OBJECT_FILE[35]="rriangle31.h5"
"""

# set template files
TEMPLATE_FILE = []
for i in np.arange(0,RUN_NUM):
    TEMPLATE_FILE.append("")
    """
TEMPLATE_FILE[0]="circle22_template.h5"
TEMPLATE_FILE[1]="circle11_template.h5"
"""
TEMPLATE_FILE[0]="circle12_template.h5"
"""
TEMPLATE_FILE[3]="circle13_template.h5"
TEMPLATE_FILE[4]="circle21_template.h5"
TEMPLATE_FILE[5]="circle31_template.h5"

TEMPLATE_FILE[6]="l22_template.h5"
TEMPLATE_FILE[7]="l22_template.h5"
TEMPLATE_FILE[8]="l12_template.h5"
TEMPLATE_FILE[9]="l13_template.h5"
TEMPLATE_FILE[10]="l21_template.h5"
TEMPLATE_FILE[11]="l31_template.h5"

TEMPLATE_FILE[12]="pentagon22_template.h5"
TEMPLATE_FILE[13]="pentagon22_template.h5"
TEMPLATE_FILE[14]="pentagon12_template.h5"
TEMPLATE_FILE[15]="pentagon13_template.h5"
TEMPLATE_FILE[16]="pentagon21_template.h5"
TEMPLATE_FILE[17]="pentagon31_template.h5"

TEMPLATE_FILE[18]="square22_template.h5"
TEMPLATE_FILE[19]="square22_template.h5"
TEMPLATE_FILE[20]="square12_template.h5"
TEMPLATE_FILE[21]="square13_template.h5"
TEMPLATE_FILE[22]="square21_template.h5"
TEMPLATE_FILE[23]="square31_template.h5"

TEMPLATE_FILE[24]="star22_template.h5"
TEMPLATE_FILE[25]="star22_template.h5"
TEMPLATE_FILE[26]="star12_template.h5"
TEMPLATE_FILE[27]="star13_template.h5"
TEMPLATE_FILE[28]="star21_template.h5"
TEMPLATE_FILE[29]="star31_template.h5"

TEMPLATE_FILE[30]="triangle22_template.h5"
TEMPLATE_FILE[31]="triangle22_template.h5"
TEMPLATE_FILE[32]="triangle12_template.h5"
TEMPLATE_FILE[33]="triangle13_template.h5"
TEMPLATE_FILE[34]="triangle21_template.h5"
TEMPLATE_FILE[35]="triangle31_template.h5"
"""

import os

for i in np.arange(0,RUN_NUM):
    print("====================================================================================")
    print(f"WORKING_DIR[{i}]:{WORKING_DIR[i]}, OBJECT_FILE[{i}]:{OBJECT_FILE[i]}, TEMPLATE_FILE[{i}]:{TEMPLATE_FILE[i]}")
    if os.path.exists(f"{WORKING_DIR[i]}{OBJECT_FILE[i]}"):
        print("OBJECT_FILE File exists.")
    else:
        print("<<<<<<<<<<<<<<<<<<<<<<<< OBJECT_FILE NOT FOUND!! >>>>>>>>>>>>>>>>>>>>>>>")

    if os.path.exists(f"{WORKING_DIR[i]}{TEMPLATE_FILE[i]}"):
        print("TEMPLATE_FILE File exists.")
    else:
        print("<<<<<<<<<<<<<<<<<<<<<<<< TEMPLATE_FILE NOT FOUND!! >>>>>>>>>>>>>>>>>>>>>>>")

print("Hit enter and RUN:")
input()

import subprocess
for i in np.arange(0,RUN_NUM):
    run_list = [PYTHON_PATH, "initPiledSim.py", WORKING_DIR[i], OBJECT_FILE[i], TEMPLATE_FILE[i], "DEM_test.xml"]
    print("run_list",run_list)
    subprocess.run(run_list)
    run_list = ["./rigidbody2dsim.exe", "DEM_test.xml"]
    print("run_list",run_list)
    subprocess.run(run_list)
