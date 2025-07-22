# 引き継ぎ書

- [引き継ぎ書(2023年度)](#引き継ぎ書2023年度)
  - [実行環境](#実行環境)
  - [c++ 環境構築](#c-環境構築)
  - [python 環境構築 (homebrew インストール後に実行してください)](#python-環境構築-homebrew-インストール後に実行してください)
  - [動作テスト方法](#動作テスト方法)
  - [計算機サーバー環境構築・データ取り方法](#計算機サーバー環境構築データ取り方法)
    - [注意事項](#注意事項)
    - [参考](#参考)
  - [データ取り後の手順](#データ取り後の手順)
  - [その他](#その他)
    - [MPMシミュレータについて](#mpmシミュレータについて)
---
- [引き継ぎ書(2024年3月版)](#引き継ぎ書2024年3月版)
  - [環境構築](#環境構築)
  - [応力データ取得手順](#応力データ取得手順)
      - [貯めるの環境作成](#貯めるの環境作成)
      - [貯めるの実行](#貯めるの実行)
      - [貯めるの可視化](#貯めるの可視化)
      - [流すの環境作成](#流すの環境作成)
      - [流すの実行](#流すの実行)
      - [流すの可視化](#流すの可視化)
  - [その他解析ツールの使い方](#その他解析ツールの使い方)
  - [コード概要](コード概要)  
      -[貯めるシミュレータ](流すシミュレータ)  
      -[流すシミュレータ](流すシミュレータ)  
      -[解析ツール](解析ツール)  
  - [各ブランチの役割](#各ブランチの役割)
---
# 引き継ぎ書(2023年度)

## 実行環境

- PyCharm (miniforge)
- Python 3.9系
- Cmake

    この引き継ぎ書は M1 Mac での実行を想定して作成しているため、M2 Mac や Windows では操作が異なる可能性があります。

---

## c++ 環境構築

- homebrew (初めに実行してください)

  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

  echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> /Users/xxx/.zprofile
  eval "$(/opt/homebrew/bin/brew shellenv)"
  ```

- eigen

  ```bash
  brew install eigen
  ```

- hdf5

  ```bash
  brew install hdf5
  ```

- rapidxml

  [ここ](https://rapidxml.sourceforge.net/)からzipファイルをダウンロードし、/usr/local/include へ展開する。フォルダ名は rapidxml にする。Cmakeで拾えれば別の場所でもOK。

---

## python 環境構築 (homebrew インストール後に実行してください)

- miniforge

  ```bash
  brew install miniforge
  ```

- 仮想環境作成

  ```bash
  conda env create -n 仮想環境名 -f docs/py39.yamlへのパス
  ```

  py39.yamlへのパスについては、本リポジトリをクローンした後の該当ファイルへのパスを入力してください。

- PyCharm のインタープリタを設定
  
  [PyCharmドキュメント](https://pleiades.io/help/pycharm/conda-support-creating-conda-virtual-environment.html)を基に上記で作成したインタープリターを追加する。

---

## 動作テスト方法

1. リポジトリをクローン
   
    ```bash
    git clone https://github.com/AGU-Graphics/GeneralizedHybridGrainsResearch.git
    ```

2. 実行ディレクトリの生成
  
    ```bash
    cd GeneralizedHybridGrainsResearch
    ./setup.sh
    ```

    setup.sh 実行時にフォルダ名を設定します。以下ではフォルダ名を build としていますので適宜変更してください。 

3. 仮想環境有効化(PyCharm で実行する場合は不要)
  
    ```bash
    conda activate 仮想環境名
    ```

4. テストデータの準備
   
   ```bash
   cp ./assets/inialization/square_merge_template.h5 ./build/Save
   cp ./assets/inialization/resumefile.h5 ./build/Save
   ```

5. シミュレーション実行
   
   ```bash
   cd ./build
   ./flowstress.sh
   ```

   実行完了時にプロットが表示されれば成功です。

実際のデータ取りはサーバーでの実行推奨です。

---

## 計算機サーバー環境構築・データ取り方法

- visual studio code の拡張機能 (Remote - SSH) 使用推奨です。
- コマンドで記述していない手順は基本的にこの拡張機能を利用しての実行を想定しています。
- 拡張機能の詳細については[こちら](https://www.sria.co.jp/blog/2021/06/5316/)

1. .profile の PATHの先頭に “/usr/local/hdf5-1.12.2/bin:” を追加

2. rapidxmlのインストール
   
    サーバー上で以下を実行
    
    ```bash
    mkdir include
    ```

    ローカルPCで以下のコマンドを実行
    
    ```bash
    scp -r rapidxmlフォルダへのパス 133.2.209.150:/home/USER_NAME/include 
    ```

    vs code でサーバーに rapidxml フォルダーをコピーでも可。
  
3. libffi のインストール

    ホームディレクトリで以下を実行
    
    ```bash
    # 作業ディレクトリを作成
    mkdir -p ~/work/libffi
    cd work/libffi
    
    # ソースのダウンロード・展開
    wget ftp://sourceware.org/pub/libffi/libffi-3.2.1.tar.gz
    tar xvfz libffi-3.2.11.tar.gz

    # インストール
    cd libffi-3.2.11
    ./configure --prefix=$HOME/local/libffi/3_2_1
    make
    make install

    # パスを通す
    mkdir -p ~/local/include
    ln -s $HOME/local/libffi/3_2_1/lib/libffi-3.2.11/include/ffi.h $HOME/local/include/
    ln -s $HOME/local/libffi/3_2_1/lib/libffi-3.2.11/include/ffitarget.h $HOME/local/include/

    mkdir -p ~/local/lib
    ln -s $HOME/local/libffi/3_2_1/lib/libffi.a $HOME/local/lib/
    ln -s $HOME/local/libffi/3_2_1/lib/libffi.la $HOME/local/lib/
    ln -s $HOME/local/libffi/3_2_1/lib/libffi.so $HOME/local/lib/
    ln -s $HOME/local/libffi/3_2_1/lib/libffi.so.6 $HOME/local/lib/

    mkdir -p ~/local/lib/pkgconfig/
    ln -s $HOME/local/libffi/3_2_1/lib/pkgconfig/libffi.pc $HOME/local/lib/pkgconfig/

    ```

    .profile の末尾に以下の２行を追加
    
    ```bash
    export LD_LIBRARY_PATH="$HOME/local/lib"
    export PKG_CONFIG_PATH="$HOME/local/lib/pkgconfig"
    ```

    .profileの変更を適用
    
    ```bash
    source ~/.profile
    ```

4. python のローカルインストール
   
   ホームディレクトリで以下を実行

    ```bash
    # 作業ディレクトリを作成
    mkdir -p ~/work/python
    cd work/python

    # ソースのダウンロード・展開
    wget https://www.python.org/ftp/python/3.9.16/Python-3.9.16.tgz
    tar xvzf Python-3.9.16.tgz
    
    # インストール
    cd Python-3.9.16

    ./configure --prefix=$HOME/local/python/ --enable-optimizations --with-system-ffi LDFLAGS="-L $HOME/local/lib/" CPPFLAGS="-I $HOME/local/include/"

    make -j 8
    make install
    ```

5. python 仮想環境の作成
   
   ホームディレクトリで以下を実行
   
   ```
   ~/local/python/bin/python3 -m venv 仮想環境名
   ```

6. 仮想環境の有効化
   
   ```
   source ~/仮想環境名/bin/activate
   ```
  
7. リポジトリをクローン
    
    ```bash
    git clone https://github.com/AGU-Graphics/GeneralizedHybridGrainsResearch.git
    ```

8.  no_openGLブランチをチェックアウト
  
    ```bash
    git checkout no_openGL
    ```

9. 必要ライブラリのインストール
  
    ```
    source ~/仮想環境名/bin/activate
    pip install -r docs/requirements.txt へのパス
    ```

10. シミュレーション実行

    シミュレーション実行は[動作テスト方法](#動作テスト方法)と同様の手順で実行できますが、シミュレーション実行中にサーバーとの接続を切った場合シミュレーションも停止します。
    
    シミュレーション実行後に接続を切りたい場合にはシェル実行時に以下のコマンドを利用してください。
    
    ```
    nohup ./flowstress.sh &
    ```

11. シミュレーションの停止方法
    
  - nohup + & を付けずにシェルを実行した場合には Ctrl + c で停止できます。

  - nohup + & を付けた場合にはプロセス番号を調べて以下のコマンドを使用することで停止できます。
  
    ```
    kill プロセス番号
    ```

    プロセス番号は以下のようなコマンドで調べられます。
    
    ```
    ps aux | grep flowstress.sh
    ```

### 注意事項

- サーバー側では conda ではなく pip を使用しているため<span style="color: red; ">仮想環境の有効化コマンドが異なります</span>。

- 本手順書は python の仮想環境を利用する前提で記述していますので上記の手順通りにコマンドを実行した場合は、<span style="color: red; ">必ず対応した仮想環境を有効化</span>してからシミュレーションを実行してください 

### 参考
[Libffi インストール](https://notemite.com/python/no-module-named-ctypes/)

[Python インストール](https://www.think-self.com/programming/python/local-python-install/)

[仮想環境の作成](https://camp.trainocate.co.jp/magazine/venv-python/)

---

## データ取り後の手順

1. サーバーからデータをダウンロード
   
   ローカルPC上で以下を実行

    ```
    rsync -avzh --partial --inplace --append --progress -e ssh 接続先:対象ファイル or ディレクトリへのパス ダウンロード先

    例
    rsync -avzh --partial --inplace --append --progress -e ssh 133.2.209.150:~/GeneralizedHybridGrainsResearch/build/Rolling/ .
    ```

2. データ圧縮・解析
   
    [stress_pair_compressor.py](../src/python/analysis/stress_pair_compressor.py) の main関数に対象ファイルのパスを設定し、データの圧縮・解析を行う。

    - 圧縮後のファイル -> プロット用
    
    - 解析結果 -> パラメータ算出用

    詳細は[コード](../src/python/analysis/stress_pair_compressor.py)参照.
    
3. プロット作成
    
    [extractStressPlot.py](../src/python/analysis/extractStressPlot.py) の load メソッド内のパスを設定して実行することでプロットを作成できます。
    
---

## その他

### MPMシミュレータについて
- 本プロジェクトで使用しているMPMシミュレータは [既存のMPMシミュレータ](https://github.com/AGU-Graphics/AGMPM.git) を改変して使用しています。
- 基本的には既存のものと同じ関数を使用しています。
- 関数名に WithData を含む関数が本プロジェクト独自の関数になっています。

- 詳細については各種コード + 論文を参照してください。

# 引き継ぎ書(2024年3月版)

## 環境構築
実行環境作成手順は
[前年度引継ぎ書](#引き継ぎ書2023年度) を参照してください。

## 応力データ取得手順
応力データの取得作業は以下の../src/python下の、以下のようなディレクトリでおこなう。  
- ../src/python
    - initialization（シミュレーションの実験環境作成ツール）
    - Simulator（シーケンシャルにシミュレータ（exeを含む）を回すツール）
    - Visualization(可視化用ツール)


---

### 貯めるの環境作成
作業ディレクトリに移動
```bash
cd /python/inialization
```

#### 1. 地面作成  
```bash
python floorgenerator.py
```
regenerateを押し、地面となる円が配置される。  
Save fileを押して、名前を付けて（例: floor_template.h5, floor.h5）ファイルを保存。

#### 2. 壁の作成
```bash
python boundarydesign.py
```
load_floorを押し、前工程で作成したfloor_template.h5, floor.h5を選択(この順番で選択しないとアプリがクラッシュする)。  
スライダーで幅と高さを調整.  
Saveを押し、名前を付け（例: boundary_template.h5, boundary.h5）ファイルを保存

#### 3. 粒子の生成
```bash
python geninitialcolumn.py
```
スライダーで粒子の大きさ、ばらつき、形状の比を調節。  
設定を調節後、Generateを押し、粒子を生成。  
Saveを押し、名前を付けファイルを保存（例: particle_template.h5, particle.h5）

#### 4. 壁と粒子の結合
```bash
python mergetool.py
``` 
Loadを押し、前工程である「壁の生成」と「粒子の生成」で作成した壁と粒子のファイルをどちらもLoadする。 
この時ファイルを選ぶ順番は、boundary_template.h5, boundary.h5, particle_template.h5, particle.h5のようにtemplateが付くものから先に選択しないとクラッシュする。
Saveを押し、名前を付けファイルを保存（例: circle11_template.h5, circle11.h5)

---

### 貯めるの実行
作業ディレクトリに移動
```bash
cd Simulator/tameru
```

- 入力ファルダの作成
ここでは、シーケンシャルに実行するためにファイルを配置する方法を説明する。

入出力を行うためのディレクトリを用意する(既にある場合もある)
```bash
src/python/simulator/tameru/IOData/"形状名"/"比率"
# 例
src/python/simulator/tameru/IOData/Circle/11
```
上記のディレクトリに、[貯めるの環境作成](#貯めるの環境作成) の「4.壁と粒子の結合」の際に保存した2つのhdfファイルをコピーする。

- シーケンシャルにおこなうための設定  
実験設定応じて、Simulator/tameru/piledSimulationLoop_python.pyのコードを以下のように書き換える.  
    - RUN_NUMに実行するファイル数を指定  
    - WORKING＿DIR:読みこむファイルがあるディレクトリを指定
    - OBJECT_FILE:「壁と粒子の結合」で作成した、読むこむオブジェクトファイル
    - TEMPLATE_FILE：「壁と粒子の結合」で作成した、読むこむオブジェクトファイル  

    配列要素番号には、実行される順番を指定  
    run_listにmac, ubuntuの場合, .exeを削除。

- パラメータの設定  
DEM_test.xmlを開き、以下を実験設定に応じて書き換える。  
    - dt:タイムステップ  
    - dx_sample_points:サンプルポイント数  
    - ugrd_dx:ブロードフェーズで用いる、格子の幅  
    - max_time:何秒までシミュレーションを実行するか  
    - 属性penalty_impact_map:ペナルティ法のパラメータ  
    - 属性resume:入力ファイルの場所（尚これはpiledSimulationLoop_python.pyによって動的に書き換えられる）
    - 属性serialization:データを出力する場所と頻度

- シミュレータの実行  
python piledSimulationLoop_python.pyを実行することシミュレーションを開始する。  
出力データが"IOData/形状名/比/Output/"に出力される。  
<span style="color: red; ">ここで、OBJECT(TEMPLATE) FILE NOT FOUNDと出てきた場合、piledSimulationLoop_pythonの設定もしくは、ファイルを配置できていない。</span>

---

### 貯めるの可視化
作業ディレクトリに移動  
```bash
cd Visualization/tameru
```
#### 1. 貯めるの出力データを再配置
"Simulator/tameru/IOData"フォルダを"Visualization/tameru/"にコピー

#### 2. 連番画像の作成
render_obj.batを実行

#### 3. 連番画像を動画化  
    3.1 ffmpeg_pathにffmpeg.exeまでのpathに設定。  
    3.2 tameru_pathに連番画像が入っているディレクトリまでのpathに設定。  
    3.3 make_piled_video.batを実行

ファイル"Visualization/tameru/movie"に動画が出力される。

---

### 流すの環境作成
ここでは、流すの入力ファイルとなる貯まった状態から、右側の柵を取り除いたファイルを作成する。

作業ディレクトリに移動
```bash
cd initialization
```
#### 壁の取り外し
1. GUIを実行
```bash
python removetemplate.py
```
2. Loadを押し、全行程である「貯めるの実行」で入力としたtemplateファイル、そこで出力された"Output/object(最後の番号)"（貯め終わった状態のオブジェクトファイル）の２つのファイルを読み込む。 

3. GUI内の"Left_wall"を押して有効かした状態で、"Delete_seleceted"を押す。
画面内の右側の壁が消えていることを確認する。

4. Saveを押して、流すの入力データとなるファイルを保存するディレクトリを指定し、保存する。  
<span style="color: red; ">("Simulator/Inputdata/形状+比_flow.xml"というファイル名を推奨)  
ex)circle11_flow.h5, circle11_flow_template.h5
</span>  

---

### 流すの実行
#### 1. 入力データの配置
「壁の取り外し」で作成した、流すの入力データファイルを"Simulator/Inputdata/"にコピーする。  

#### 2. シーケンシャルにおこなうための設定
"Simulator/nagasu_loop.py"の以下のようにコードを編集する。  
- RUN_NUMに連続でおこなうシミュレーション数を記入
- OBJECT_FILE:「壁の取り外し」で作成した読むこむオブジェクトファイル
- TEMPLATE_FILE：「壁の取り外し」で作成した、読むこむオブジェクトファイル  

<span style="color: red; ">ここでのファイル名には"_flow"を取り除く。  
ex)実際のファイル名"circle11_flow.h5", "circle11_flow_template"　  
⇒ OBJECT_FILE[0]="circle11.h5", TEMPLATE_FILE[0]="circe11_template"</span>    

配列要素番号には、実行される順番を指定  

以下の例(macの際)のように、実行環境である行のコメントアウトを解除。その他2行をコメントアウト
```bash
#you should change with depending on your own laptop
HomogenizeForceSleep_EXE = ["sh", "./HomogenizeForceSleep_mac.sh"]
# HomogenizeForceSleep_EXE = ["HomogenizeForceSleep.bat"]
# HomogenizeForceSleep_EXE = ["sh", "./HomogenizeForceSleep_ubuntu.sh"]
```

#### 3. パラメータの設定
流すシミュレーションにおけるパラメータは以下のようになっている。  
- 3.1 DEM_test_resume.xml
    - dt:タイムステップ  
    - dx_sample_points:サンプルポイント数  
    - ugrd_dx:ブロードフェーズで用いる、格子の幅  
    - max_time:何秒までシミュレーションを実行するか  
    - 属性penalty_impact_map:ペナルティ法のパラメータ  
    - 属性resume:入力ファイルの場所（尚これはnagasu_loop.pyによって動的に書き換えられる）
    - 属性serialization:データを出力する場所と頻度
- 3.2 homogenize_stress.xml
    -  h:均質化用格子の幅  
    - interval:DEMのシミュレーションを1ステップで動かす秒数
    - packing_fraction_threshold:外れ値として扱われるパッキング率の閾値
    - distance_from_wall_threshold:外れ値として扱われる、格子の中心から壁までの距離  
- 3.3 homogenizerti.py
    - estimate_force_num:1ステップの衝突データの最大数(taichiで確保するGPUメモリ)
    - estimate_grid_num:1ステップの格子数の最大数(taichiで確保するGPUメモリ)

- 3.4 HomogenizeForceSleep_mac.sh(windowsの場合はHomogenizeForceSleep.sh, ubuntuの場合はHomogenizeForceSleep_ubuntu.shを編集)
    - MaxLoop:シミュレーションを回す回数

#### 4. 流すの実行
シミュレータをシーケンシャルに実行するコードを実行
```bash
python nagasu_loop.py
```
<span style="color: red; ">ここで、OBJECT(TEMPLATE) FILE NOT FOUNDと出てきた場合、piledSimulationLoop_pythonの設定もしくは、ファイルを配置できていない。</span>  

出力されるデータは以下のように出力される  
- 応力データ：Simulator/nagasu/Save_形状_比_flow/stress_pair.h5"  
- 毎ステップの粒子の状態：Simulator/nagasu/element_data.h5"

### 再開方法
- 1.  
Simulator/nagasu/Save_形状_比_flow/形状_比_flow.h5をInputDataにコピー
- 2.シミュレーションを実行
```bash
python3 nagasu_loop.py
```

---

### 流すの可視化
作業用ディレクトリに移動する。
```bash
cd Visualize/nagasu
```
#### 1. 貯めるの出力データを再配置
    1.1「流すの実行」で出力された"element_data.h5"を"Visualization/nagasu/IOData/形状名/比/Output/"にコピー  
    ex)Visualization/nagasu/IOData/Circle/11/Output/element_data.h5
    1.2 入力データとなったtemplateファイルを"Visualization/nagasu/IOData/形状名/比/"にコピー
    ex)Visualization/nagasu/IOData/Circle/11/circle11_flow_template.h5

#### 2. 連番画像の作成
render_obj.batを実行

#### 3. 連番画像を動画化  
    3.1 ffmpeg_pathにffmpeg.exeまでのpathに設定。  
    3.2 tameru_pathに連番画像が入っているディレクトリまでのpathに設定。  
    3.3 make_piled_video.batを実行

ファイル"Visualization/tameru/movie"に動画が出力される。

---

## 解析ツールの使い方
### データ圧縮・解析ツール(Simulator/stress_pair_compressor.py)
[stress_pair_compressor.py](../src/python/simulator/stress_pair_compressor.py) の main関数に対象ファイルのパスを設定し、データの圧縮・解析を行う。

- 圧縮後のファイル -> プロット用

- 解析結果 -> パラメータ算出用

詳細は[コード](../src/python/simulator/stress_pair_compressor.py)参照.
    
### プロット作成(Simulator/extractStressPlot.py)  
 [extractStressPlot.py](../src/python/simulator/extractStressPlot.py) の load メソッド内のパスを設定して実行することでプロットを作成できる。

### 範囲外にある不要な粒子を削除するツール(initialization/removeobject.py)  
 [removeobject.py](../src/python/initialization/removeobject.py) の load メソッド内のパスを設定して実行し、bounding_boxとなる範囲をスライダーで設定することで、範囲外にある粒子を削除することができる。

### 簡易的な粒子の可視化ツール(analysis/grainviewer.py)  
 [grainviewer.py](../src/python/analysis/grainviewer.py) の load メソッド内のパスを設定して実行することで粒子を可視化し、zoomスライダーによって拡大表示することができる。


# コード概要
ここでは、各コードの概要について解説する。

## 貯めるシミュレータ
ここでは、「貯める、流すの実行」で必要なシミュレータ"src/cpp/RigidBody2D"以下のファイルについて説明する。
### 入出力ファイル
シミュレータではコマンドライン引数として以下のxmlファイルとしてパラメータを与え、以下のようなhdfファイルである入出力データとして使用している
- xml:DEM設定
- hdf:粒子形状データ、シミュレーション再開用データ、DEM実行結果データ

### シミュレーションフロー
各フローの詳細はコードもしくは「ハイブリッドな粒状物質シミュレーションの一般化に向けて」3.3.3章の参照を推奨。

1.接触粒子の探索(collisiondetection2d.cpp)
broadPhaseCollisionDetection(ブロードフェーズ),narrowPhaseCollisionDetection(ナローフェーズ)によって衝突している粒子を探索。

2.粒子間の相互作用を計算(simulator.cpp)
1で衝突が検出した粒子のめり込み量に応じた力を計算する。

3.粒子の物理量の更新(simulator.cpp)
2で計算した各粒子にかかる力を用いて、速度と位置を更新する。

4.タイムステップの更新(main.cpp)
タイムステップを進め、最初の処理に戻る。

## 流すシミュレータ
ここでは、「流すの実行」で用いられているシミュレーション内の各コードの概要とシミュレーションフローについて説明していく。

### コード概要
- rigidbody2dsim.exe(前項である貯めるシミュレータを参照)
- MPM.exe( [前年度引継ぎ書](#引き継ぎ書2023年度) を参照)


### 入出力ファイル
シミュレータ内でデータを共有するために以下のファイルを入出力用ファイルとして使用している。  
- xml:全体設定、DEM 設定、MPM 設定  
- hdf:粒子形状データ、DEM 実行結果データ、接触力均質化データ、MPM実行結果データ、応力均質化データ、シミュレーション再開用データ、応力ペアデータ、可視化
用粒子データ

### シミュレーションフロー
各フローの詳細はコードもしくは「ハイブリッドな粒状物質シミュレーションの一般化に向けて」3.3章の参照を推奨。

1. 中間ファイルの削除(delteIntermediateFile.py)  
前ステップで生成されていた各種hdf出力データを削除する。  
これにより、データの上書きを防ぐ。

2. DEM実行
DEMによって衝突データファイルの出力 
出力：粒子ごとの衝突力データ(Save_形状_比/serialized_force.h5)  

3. 工程２終了通知(makeSleepFlag.py)    
出力：工程2が終了したことを常時起動しているtaichiのコード（allsteptiHomognizeSleep.py）に通知するファイル(sleep_flag.txt)  

4. 接触力の均質化(allsteptiHomogenizerSleep.py)  
sleep_flag.txtが生成された際に、粒子ごとの衝突力データを格子に均質化することで塑性流動後の応力データを出力する。  
入力：DEM実行結果データ(Save_形状_比/serialized_force.h5)  
出力：接触力均質化データ(DEMstress/DEM.h5), ひずみ用データ（DEMstress/DEM2）


5. MPM実行(MPM2D.exe) 
DEM均質化用格子を使用してMPMを実行し、粒子ごとの塑性流動前の応力を出力する。
入力：ひずみ用データ(DEMstress/DEM2.h5)  
出力：MPM実行結果データ(Save_形状_比/serialized_sigma.h5)  


6. 応力の均質化(allstepMPMBeforeflow.py)
格子ごとの塑性流動前の応力の出力  
入力：MPM実行結果データ(Save_形状_比/serialized_sigma.h5)   
出力：応力均質化データ(MPMstress/MPM.h5)  

7. 比較データ作成(storeStressPair.py )  
塑性流動前後の応力、粒子の情報の出力  
入力：応力均質化データ(MPMstress/MPM.h5), 接触力均質化データ(DEMstress/DEM.h5)  
出力：応力ペアデータ(Save_形状_比/stress_pair.h5), 可視化用粒子データ(Rolling_形状_比/element_data.h5)

## 解析ツール 
### データ圧縮・解析ツール(Simulator/stress_pair_compressor.py)

### プロット作成ツール(Simulator/extractStressPlot.py)  
各スライダーの機能は「ハイブリッドな粒状物質シミュレーションの一般化に向けて」3.3章の参照を推奨。


# 各ブランチの役割
ここでは各ブランチ間の違いを説明する。
## cpp/RigidBody2D
- main:OpenGLによって可視化されるコード。スペースキーを押すことではじめて起動する。
- mac:mainと同じ
- measure_process_time：:OpenMPによる高速化をおこなったDEMコード。処理時間をcsvに出力する。可視化無し。
- simulator:OpenMPによる高速化をおこなったDEMコード。可視化無し。

## simulator/nagasu
- main:ubuntu, windows用のシミュレータ
- mac: mac用のシミュレータ