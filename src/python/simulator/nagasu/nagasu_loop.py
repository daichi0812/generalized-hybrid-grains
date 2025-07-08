PYTHON_PATH="python"

RUN_NUM=1

# set object files
OBJECT_FILE = []
for i in range(RUN_NUM):
    OBJECT_FILE.append("")
#OBJECT_FILE[0]="circle12.h5"
#OBJECT_FILE[0]="circle11.h5"
OBJECT_FILE[0]="circle22.h5"


# set template files
TEMPLATE_FILE = []
for i in range(RUN_NUM):
    TEMPLATE_FILE.append("")
#TEMPLATE_FILE[0]="circle12_template.h5"
#TEMPLATE_FILE[0]="circle11_template.h5"
TEMPLATE_FILE[0]="circle22_template.h5"


#you should change with depending on your own laptop
#HomogenizeForceSleep_EXE = ["sh", "./HomogenizeForceSleep_mac.sh"]
HomogenizeForceSleep_EXE = ["HomogenizeForceSleep.bat"]
# HomogenizeForceSleep_EXE = ["sh", "./HomogenizeForceSleep_ubuntu.sh"]

######################################################

def RenameObjectFile(file_name):
    "triangle31.h5"
    "-> triangle31_flow.h5"
    tmp = file_name
    splited = tmp.split('.')
    tmp = f"{splited[0]}_flow.{splited[1]}"
    return tmp

def RenameTemplateFile(file_name):
    "triangle31_template.h5"
    "-> triangle31_flow_template.h5"
    tmp = file_name
    splited = tmp.split('.')
    fileName = splited[0]
    exeName = splited[1]
    splited = fileName.split('_')
    tmp = f"{splited[0]}_flow_{splited[1]}.{exeName}"
    return tmp

import subprocess
import shutil
import os

for i in range(RUN_NUM):
    print("------------------------------------------------------------------------------")
    splited = OBJECT_FILE[i].split('.')

    renamed_object_file_name = RenameObjectFile(OBJECT_FILE[i]).split('.')[0]
    renamed_template_file_name = RenameTemplateFile(TEMPLATE_FILE[i])

    obj_file = f"./InputData/{renamed_object_file_name}.h5"
    tmp_file = f"./InputData/{renamed_template_file_name}"
    
    print(f"Object_File : {obj_file}, Template_File : {tmp_file}")
    
    if os.path.exists(obj_file):
        print("Object File Found")
    else:
        print("<<<<<<<<<<<<<<<<<<<<<<<< Object File NOT FOUND >>>>>>>>>>>>>>>>>>>>>>>>>>")

    if os.path.exists(tmp_file):
        print("Template File Found")
    else:
        print("<<<<<<<<<<<<<<<<<<<<<<<< Template File NOT FOUND >>>>>>>>>>>>>>>>>>>>>>>>>>")
    
    

print("Hit Enter and RUN")
input()

for i in range(RUN_NUM):
    print("------------------------------------------------------------------------------")
    splited = OBJECT_FILE[i].split('.')
    output_path = splited[0]
    run_list = [PYTHON_PATH, "initSimulationEnv.py", f"{output_path}_flow", "homogenize_stress.xml"]
    print(run_list)
    subprocess.run(run_list)
    renamed_object_file_name = RenameObjectFile(OBJECT_FILE[i]).split('.')[0]
    print(f"copy ./InputData/{renamed_object_file_name}.h5 to ./Save_{renamed_object_file_name}/{renamed_object_file_name}.h5")
    shutil.copy(f"./InputData/{renamed_object_file_name}.h5", f"./Save_{renamed_object_file_name}/{renamed_object_file_name}.h5")
    
    renamed_template_file_name = RenameTemplateFile(TEMPLATE_FILE[i])
    print(f"copy ./InputData/{renamed_template_file_name} to ./Save_{renamed_object_file_name}/{renamed_template_file_name}")
    shutil.copy(f"./InputData/{renamed_template_file_name}", f"./Save_{renamed_object_file_name}/{renamed_template_file_name}")

    print(HomogenizeForceSleep_EXE)
    subprocess.run(HomogenizeForceSleep_EXE)
