# initSimulationEnv.py shape_ratio_ratio homogenize_stress.xml
python ./initSimulationEnv.py circle_025_025_flow homogenize_stress.xml
cp ./init_data/circle_025_025_flow.h5 ./Save_circle_025_025_flow/
cp ./init_data/circle_025_025_flow_template.h5 ./Save_circle_025_025_flow/
./HomogenizeForceSleep.sh & ./HomogenizeDEMLoop.sh

# initSimulationEnv.py shape_ratio_ratio homogenize_stress.xml
python ./initSimulationEnv.py circle_025_025_flow homogenize_stress.xml
cp ./init_data/circle_025_025_flow.h5 ./Save_circle_025_025_flow/
cp ./init_data/circle_025_025_flow_template.h5 ./Save_circle_025_025_flow/
./HomogenizeForceSleep.sh & ./HomogenizeDEMLoop.sh