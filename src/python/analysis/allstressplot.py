from sysconfig import parse_config_h
from stressviewer import *
from allhomogenizationh5 import *
from progressh5 import *
from stresspairh5 import *
import xml.etree.ElementTree as ET 
import sys

stress_plot = StressPlot()
fig = go.Figure()
args = sys.argv
if len(args) < 2:
    print('rewriteResumefn.py homogenize_stress_fn')
resume_xml_fn = args[1]
tree = ET.parse(resume_xml_fn)
root = tree.getroot()
if root[1].tag !="stress":
    print("not resume line")
pre_fn = root[1].attrib["pre_stress"]
post_fn = root[1].attrib["post_stress"]


allpre_homogenization_data = AllHomogenizeData()
allpost_homogenization_data = AllHomogenizeData()
allpre_homogenization_data.load(pre_fn)
allpost_homogenization_data.load(post_fn)


for i in range(len(allpost_homogenization_data.all_step_homogenization)):
    pre_homogenization_data = allpre_homogenization_data.all_step_homogenization[i]
    post_homogenization_data = allpost_homogenization_data.all_step_homogenization[i]
    stress_plot = StressPlot()
    stress_plot.setData(pre_homogenization_data, post_homogenization_data, fig)

fig.show()

    

