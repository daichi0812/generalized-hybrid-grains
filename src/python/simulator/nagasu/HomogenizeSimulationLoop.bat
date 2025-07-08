# initSimulationEnv.py shape_ratio_ratio homogenize_stress.xml
python .\initSimulationEnv.py circle_025_025 homogenize_stress.xml
copy .\init_data\circle_025_025.h5 .\Save_circle_025_025\circle_025_025.h5
copy .\init_data\circle_025_025_template.h5 .\Save_circle_025_025\circle_025_025_template.h5
.\HomogenizeForceSleep.bat & .\HomogenizeDEMLoop.bat

# initSimulationEnv.py shape_ratio_ratio homogenize_stress.xml
python .\initSimulationEnv.py square_025_025 homogenize_stress.xml
copy .\init_data\square_025_025.h5 .\Save_square_025_025\square_025_025.h5
copy .\init_data\square_025_025_template.h5 .\Save_square_025_025\square_025_025_template.h5
.\HomogenizeForceSleep.bat & .\HomogenizeDEMLoop.bat

# initSimulationEnv.py shape_ratio_ratio homogenize_stress.xml
python .\initSimulationEnv.py triangle_025_025 homogenize_stress.xml
copy .\init_data\triangle_025_025.h5 .\Save_triangle_025_025\triangle_025_025.h5
copy .\init_data\triangle_025_025_template.h5 .\Save_triangle_025_025\triangle_025_025_template.h5
.\HomogenizeForceSleep.bat & .\HomogenizeDEMLoop.bat

