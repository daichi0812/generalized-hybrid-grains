#!/bin/bash
set -Eeuo pipefail
cd "$(dirname "$0")" || exit
tmp=/tmp/$$exec_taichi

# Prefix="/Volumes/ExtremeSSD/python/analysis/python/analysis"
Prefix="/Users/shotaro/DevHub/CG/generalized-hybrid-grains/src/python/simulator/nagasu"

DEM="./DEMstress/DEM.h5"
MPM_H5="./MPMstress/MPM.h5"
FORCES="./Save_square11_flow/serialized_forces.h5"
PYTHON_PATH="/opt/homebrew/Caskroom/miniforge/base/bin/python"

MaxLoop=1000
${PYTHON_PATH} ${Prefix}/initResumefn.py homogenize_stress.xml
{
# cat << EOF > ${tmp}
# #!/bin/bash
# cd "${Prefix}" || exit 1
# ${PYTHON_PATH} ${Prefix}/allsteptiHomogenizerSleep.py ${Prefix}/homogenize_stress.xml
# EOF
# chmod 777 ${tmp}

# 2025-09-09 追加
cat << 'LAUNCH' > "$tmp"
#!/bin/bash
cd "/Users/shotaro/DevHub/CG/generalized-hybrid-grains/src/python/simulator/nagasu" || exit 1
/opt/homebrew/Caskroom/miniforge/base/bin/python /Users/shotaro/DevHub/CG/generalized-hybrid-grains/src/python/simulator/nagasu/allsteptiHomogenizerSleep.py /Users/shotaro/DevHub/CG/generalized-hybrid-grains/src/python/simulator/nagasu/homogenize_stress.xml
LAUNCH
chmod 777 "$tmp"

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

  # --- DEM.h5 に /0/homogenization が出るまで待つ（ <- allstepti が作る)
  echo "[WAIT] DEMstress/DEM.h5 -> /0/homogenization/sigma"
  "$PYTHON_PATH" - << 'PY'
import sys, time, os, h5py
fn = "DEMstress/DEM.h5"
def ready():
    if not os.path.exists(fn): return False
    try:
        with h5py.File(fn, "r") as f:
            return "0" in f and "homogenization" in f["0"] and "sigma" in f["0/homogenization"]
    except Exception:
        return False
for _ in range(600):
    if ready():
        print("[OK] DEM.h5 has /0/homogenization/sigma"); sys.exit(0)
    time.sleep(0.1)
print("[ERR] DEM.h5 not ready"); sys.exit(1)
PY

  echo "[RUN] MPM2D"
  ./MPM2D herschel_bulkley.xml

# --- MPM 出力を自動検出（任意の整数グループ & 2種類のsigmaパスに対応）
echo "[WAIT] scan MPMstress/*.h5 for sigma (any group)"
eval "$("$PYTHON_PATH" - << 'PY'
import sys, time, os, glob, h5py, re
def try_file(fp):
    with h5py.File(fp,"r") as f:
        for g in f.keys():
            if not re.fullmatch(r"\d+", g):  # 0,1,2,... のグループだけ見る
                continue
            if "sigma" in f[g]:
                print(f'MPM_FILE="{fp}"')
                print(f'SIGMA_PATH="/{g}/sigma"')
                return True
            if "homogenization" in f[g] and "sigma" in f[f"{g}/homogenization"]:
                print(f'MPM_FILE="{fp}"')
                print(f'SIGMA_PATH="/{g}/homogenization/sigma"')
                return True
    return False

deadline = time.time() + 120
last = None
while time.time() < deadline:
    for fp in sorted(glob.glob("MPMstress/*.h5")):
        try:
            if try_file(fp):
                sys.exit(0)
            last = fp
        except Exception:
            last = fp
    time.sleep(0.2)

if last:
    print(f'LAST_SEEN="{last}"')
print("No sigma found", file=sys.stderr)
sys.exit(1)
PY
)" || { echo "[ERR] MPM output not found or sigma missing. last_seen=${LAST_SEEN:-}"; exit 1; }

# --- 期待の場所にブリッジ（MPMstress/MPM.h5:/0/sigma を再構成）
if [ "$MPM_FILE" != "MPMstress/MPM.h5" ] || [ "$SIGMA_PATH" != "/0/sigma" ]; then
  echo "[FIX] create MPMstress/MPM.h5:/0/sigma from $MPM_FILE:$SIGMA_PATH"
  "$PYTHON_PATH" - << 'PY'
import os, h5py
src_file = os.environ["MPM_FILE"]
src_path = os.environ["SIGMA_PATH"]
dst_file = "MPMstress/MPM.h5"
dst_grp  = "0"

# 読み出し
with h5py.File(src_file, "r") as s:
    data = s[src_path][()]

# 上書き作成
if os.path.exists(dst_file):
    os.remove(dst_file)
with h5py.File(dst_file, "w") as t:
    g = t.create_group(dst_grp)
    g.create_dataset("sigma", data=data)
print("[OK] wrote", dst_file, "/0/sigma")
PY
fi

  "$PYTHON_PATH" "$Prefix/allstepMPMBeforeflow.py" homogenize_stress.xml
  "$PYTHON_PATH" "$Prefix/storeStressPair.py" homogenize_stress.xml
  "$PYTHON_PATH" "$Prefix/rewriteResumefn.py" homogenize_stress.xml
done

touch exit_flag.txt
exit