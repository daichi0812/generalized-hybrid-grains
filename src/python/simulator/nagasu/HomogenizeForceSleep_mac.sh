# #!/bin/bash
# cd "$(dirname "$0")" || exit
# tmp=/tmp/$$exec_taichi

# # Prefix="/Volumes/ExtremeSSD/python/analysis/python/analysis"
# Prefix="/Users/shotaro/DevHub/CG/generalized-hybrid-grains/src/python/simulator/nagasu"

# DEM="./DEMstress/DEM.h5"
# PYTHON_PATH="/opt/homebrew/Caskroom/miniforge/base/bin/python"

# MaxLoop=1000
# ${PYTHON_PATH} ${Prefix}/initResumefn.py homogenize_stress.xml
# {
# cat << EOF > ${tmp}
# #!/bin/bash
# ${PYTHON_PATH} ${Prefix}/allsteptiHomogenizerSleep.py ${Prefix}/homogenize_stress.xml
# EOF
# chmod 777 ${tmp}

# } &&{
# open ${tmp}

# } &&{
# echo "taichi is activated."

# } ||{
# echo "Activating taichi is Failed."
# }


# chmod 777 ./rigidbody2dsim
# chmod 777 ./MPM2D

# for _ in $(seq $MaxLoop)
# do
#   ${PYTHON_PATH} ${Prefix}/deleteIntermediateFile.py DEM_test_resume.xml
  
  
#   ./rigidbody2dsim DEM_test_resume.xml

#   ${PYTHON_PATH} ${Prefix}/makeSleepFlag.py

#   while [ ! -e $DEM ]
#   do
#     sleep 0.005
#   done
#   ./MPM2D herschel_bulkley.xml

#   ${PYTHON_PATH} ${Prefix}/allstepMPMBeforeflow.py homogenize_stress.xml
 
#   ${PYTHON_PATH} ${Prefix}/storeStressPair.py homogenize_stress.xml

#   ${PYTHON_PATH} ${Prefix}/rewriteResumefn.py homogenize_stress.xml
# done
# touch exit_flag.txt
# exit




#!/usr/bin/env bash
set -Eeuo pipefail
cd "$(dirname "$0")" || exit
mkdir -p Save_square11_flow MPMstress DEMstress
set -x
tmp=/tmp/$$exec_taichi

# Prefix="/Volumes/ExtremeSSD/python/analysis/python/analysis"
Prefix="/Users/shotaro/DevHub/CG/generalized-hybrid-grains/src/python/simulator/nagasu"

# DEM は MPM 後に生成されるので待ち条件に不適
# ここでは DEM 前段のトリガーである serialized_forces を持つ
FORCES="./Save_square11_flow/serialized_forces.h5"
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

  # MPM の入力が出るまで待つ（存在かつ非ゼロサイズ）
  while [ ! -s "$FORCES" ]
  do
    sleep 0.05
  done
  echo "[INFO] Detected $FORCES"
  ./MPM2D herschel_bulkley.xml

  ${PYTHON_PATH} ${Prefix}/allstepMPMBeforeflow.py homogenize_stress.xml
 
  ${PYTHON_PATH} ${Prefix}/storeStressPair.py homogenize_stress.xml

  ${PYTHON_PATH} ${Prefix}/rewriteResumefn.py homogenize_stress.xml
done
touch exit_flag.txt
exit