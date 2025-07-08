echo %time%
set MaxLoop=1500
set i=0

python initResumefn.py homogenize_stress.xml

START HomogenizeDEMLoop.bat

:start
IF %i% neq %MaxLoop% (
    python deleteIntermediateFile.py DEM_test_resume.xml

    .\rigidbody2dsim.exe DEM_test_resume.xml

    python makeSleepFlag.py

    goto :label
) else (
    fsutil file createnew exit_flag.txt 1
    echo %time%
    exit /b
)

:label
 powershell sleep 1
 if exist ".\DEMstress\DEM.h5" (
    .\MPM2D.exe herschel_bulkley.xml

    python allstepMPMBeforeflow.py homogenize_stress.xml

    python storeStressPair.py homogenize_stress.xml

    python rewriteResumefn.py homogenize_stress.xml

    set /a i=%i% + 1
    goto :start
 )
 goto :label





