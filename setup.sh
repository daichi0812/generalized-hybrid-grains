#!/bin/bash

# シェルがあるディレクトリをカレントディレクトリに設定
cd "$(dirname "$0")" || exit

# 作成するディレクトリ名の入力受付
if [ -n "$ZSH_VERSION" ]; then
  read -r "DIR_NAME?Please enter directory name: "
else
  read -r -p "Please enter directory name: " DIR_NAME
fi

# ディレクトリ生成
mkdir "$DIR_NAME"
cd "$DIR_NAME" || exit

# DEMシミュレータコンパイル
mkdir buildDEM
cd buildDEM || exit
cmake -DCMAKE_BUILD_TYPE=Release ../../src/cpp/RigidBody2D
make
cd ../

# MPMシミュレータコンパイル
mkdir buildMPM
cd buildMPM || exit
cmake -DCMAKE_BUILD_TYPE=Release ../../src/cpp/MPM2D
make
cd ../

# 必要ディレクトリの作成
mkdir DEMstress
mkdir MPMstress
mkdir Rolling
mkdir Save

# アセットのコピー
cp ../assets/homogenization/homogenize_stress.xml .
cp ../assets/inialization/DEM_test_resume.xml .
cp ../assets/inialization/herschel_bulkley.xml .
cp ../assets/inialization/initialpoints.hdr .
cp ../assets/inialization/obstacles.hdr .

# 実行ファイルのリンク生成
ln -s ../src/python/analysis/flowstress.sh .
ln -s ./buildDEM/rigidbody2dsim .
ln -s ./buildMPM/MPM2D .