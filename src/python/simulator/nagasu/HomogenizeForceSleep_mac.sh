#!/bin/bash
cd "$(dirname "$0")" || exit
tmp=/tmp/$$exec_taichi

# Prefix="/Volumes/ExtremeSSD/python/analysis/python/analysis"
Prefix="/Users/shotaro/DevHub/CG/generalized-hybrid-grains/src/python/simulator/nagasu"

DEM="./DEMstress/DEM.h5"
MPM_H5="./MPMstress/DEM.h5"
FORCES="./Save_square11_flow/serialized_forces.h5"
PYTHON_PATH="/opt/homebrew/Caskroom/miniforge/base/bin/python"

MaxLoop=1000
${PYTHON_PATH} ${Prefix}/initResumefn.py homogenize_stress.xml
{
cat << EOF > ${tmp}
#!/bin/bash
cd "${Prefix}" || exit 1
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
  "${PYTHON_PATH}" "${Prefix}/deleteIntermediateFile.py" DEM_test_resume.xml
  
  ./rigidbody2dsim DEM_test_resume.xml

  "${PYTHON_PATH}" "${Prefix}/makeSleepFlag.py"

  # while [ ! -e $DEM ]
  # do
  #   sleep 0.005
  # done
  # ./MPM2D herschel_bulkley.xml

  # 2025-09-09 追加 ここから

  # --- 前段の forces を持つ(存在かつ非ゼロ)
  while [ ! -s "$FORCES" ]; do
    echo "[WAIT] forces not ready: $FORCES"
    sleep 0.1
  done

  # --- DEM.h5 の存在だけ先に担保(allstepti が作ることもあるが、なければ空を作る)
  if [ ! -e "$DEM" ]; then
    "$PYTHON_PATH" - << 'PY'
import h5py
os.makedirs("DEMstress", exit_ok=True)
fn = "DEMstress/DEM.h5"
with h5py.File(fn, "w") as f:
    g0 = f.create_group("0")
    g0.create_group("homogenization")
print("[INFO] primed:", fn)
PY
  fi

  # === ここが肝: MPM2D より先に　DEM の均質化を作成 ===
  echo "[RUN] allstepMPMBeforeflow.py (build DEM homogenization)"
  ${PYTHON_PATH} ${Prefix}/allstepMPMBeforeflow.py homogenize_stress.xml

  # --- 生成検査: 最低限 0/homogenizatioin があるか（必要なら 'sigma' も確認)
  echo "[CHECK] DEMstress/DEM.h5 -> /0/homogenization"
  "$PYTHON_PATH" - << 'PY'
import h5py, time, sys
with h5py.File("DEMstress/DEM.h5", 'r') as f:
    ok = "0" in f and "homogenization" in f["0"]
    # 'sigma' を中に作る実装なら、以下も true になるはず
    # ok = ok and "sigma" in f["0/homogenization"]
    print("[OK] if ok else "[NG], list(f.keys()))
    sys.exit(0 if else 1)
PY

  echo "[RUN] MPM2D"
  ./MPM2D herschel_bulkley.xml

  # --- MPM 出力が整うのを待つ(/0/sigma が読めるまで）
  echo "[WAIT] MPMstress/MPM.h5 -> /0/sigma"
  "$PYTHON_PATH" - << 'PY'
import h5py, time, os, sys
fn = "MPMstress/MPM.h5"
def ready():
    if not os.path.exists(fn): return False
    try:
        with h5py.File(fn, "r") as f:
            return "0" in f and "sigma" in f["0"]
    except Exception:
        return False
for _ in range(600):
    if ready():
        print("[OK] MPM.h5 has /0/sigma")
        sys.exit(0)
    time.sleep(0.1)
sys.exit("[ERR] MPM.h5 not ready: missing /0/sigma")
PY
  ${PYTHON_PATH} ${Prefix}/storeStressPair.py homogenize_stress.xml
  ${PYTHON_PATH} ${Prefix}/rewriteResumefn.py homogenize_stress.xml
done
touch exit_flag.txt
exit