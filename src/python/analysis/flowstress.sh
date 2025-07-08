#!/bin/bash
cd "$(dirname "$0")" || exit

Prefix="../src/python/analysis"
MaxLoop=1

rm ./Save/stress_pair.h5
rm ./Rolling/*

python ${Prefix}/initResumefn.py homogenize_stress.xml

for _ in $(seq $MaxLoop)
do
  rm ./MPMstress/MPM.h5
  rm ./DEMstress/DEM.h5
  rm ./DEMstress/DEM2.h5

  ./rigidbody2dsim DEM_test_resume.xml

  python ${Prefix}/allstepHomogenizer.py homogenize_stress.xml

  ./MPM2D herschel_bulkley.xml

  python ${Prefix}/allstepMPMBeforeflow.py homogenize_stress.xml

  python ${Prefix}/storeStressPair.py homogenize_stress.xml

  # 使い終わった全ステップの力のデータを削除する
#  rm ./Save/serialized_forces.h5
#  rm ./Save/serialized_sigma.h5

  python ${Prefix}/rewriteResumefn.py homogenize_stress.xml
done

python ${Prefix}/allstressviewer.py homogenize_stress.xml

exit
