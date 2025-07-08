# 引き継ぎ書

- [引き継ぎ書](#引き継ぎ書)
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
    tar xvfz libffi-3.2.1.tar.gz

    # インストール
    cd libffi-3.2.1
    ./configure --prefix=$HOME/local/libffi/3_2_1
    make
    make install

    # パスを通す
    mkdir -p ~/local/include
    ln -s $HOME/local/libffi/3_2_1/lib/libffi-3.2.1/include/ffi.h $HOME/local/include/
    ln -s $HOME/local/libffi/3_2_1/lib/libffi-3.2.1/include/ffitarget.h $HOME/local/include/

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
