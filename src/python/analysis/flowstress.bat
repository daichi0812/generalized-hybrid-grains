set MaxLoop=0
python initResumefn.py homogenize_stress.xml
for /l %%i in (0,1,%MaxLoop%)do (
    @rem DEMを実行、f_fn(全ステップの力のデータ)、resume_fn次のresumeファイルを生成
    call rigidbody2dsim.exe DEM_test_resume.xml
    call MPM2D.exe herschel_bulkley.xml

    python allstepHomogenizer.py homogenize_stress.xml @rem ファイルiにすべての塑性前の応力を出力
    
    python allstepMPMBeforeflow.py homogenize_stress.xml @rem ファイルiにすべての塑性後の応力を出力
    
    @rem python storeStressPair.py homogenize_stress.xml @rem ファイル内すべての流動前後の応力を格子で比較、格子から外れたもの、応力がNoneを削除
    python allstressplot.py homogenize_stress.xml @rem 応力比較プロット(テスト)

    @rem 使い終わった全ステップの力のデータを削除する
    @rem del .\Save\serialized_forces.h5
    @rem del .\Save\serialized_sigma.h5

    @rem resume_file.xmlに次のresumeファイルをセットする.MAX＿TIMEを書き換える
    python rewriteResumefn.py homogenize_stress.xml
)