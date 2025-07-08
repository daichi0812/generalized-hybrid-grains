#!/bin/bash
cd "$(dirname "$0")" || exit
tmp=/tmp/$$exec_taichi
Prefix="/Volumes/ExtremeSSD/python/analysis/python/analysis"
DEM="./DEMstress/DEM.h5"
PYTHON_PATH="/opt/homebrew/Caskroom/miniforge/base/bin/python"
MaxLoop=1000
${PYTHON_PATH} ${Prefix}/initResumefn.py homogenize_stress.xml
{
cat << EOF > ${tmp}
#!/bin/bash
${PYTHON_PATH} ${Prefix}/allsteptiHomogenizerSleep.py ${Prefix}/homogenize_stress.xml
EOF
chmod 777 ${tmp}

} &&{
open ${tmp}

} &&{
echo "taichi is activated."

} ||{
echo "Activating taichi is Failed."
}


chmod 777 ./rigidbody2dsim
chmod 777 ./MPM2D

for _ in $(seq $MaxLoop)
do
  ${PYTHON_PATH} ${Prefix}/deleteIntermediateFile.py DEM_test_resume.xml
  
  
  ./rigidbody2dsim DEM_test_resume.xml

  ${PYTHON_PATH} ${Prefix}/makeSleepFlag.py

  while [ ! -e $DEM ]
  do
    sleep 0.005
  done
  ./MPM2D herschel_bulkley.xml

  ${PYTHON_PATH} ${Prefix}/allstepMPMBeforeflow.py homogenize_stress.xml
 
  ${PYTHON_PATH} ${Prefix}/storeStressPair.py homogenize_stress.xml

  ${PYTHON_PATH} ${Prefix}/rewriteResumefn.py homogenize_stress.xml
done
touch exit_flag.txt
exit




