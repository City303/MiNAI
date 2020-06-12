#@OpService ops

from ij import IJ
IJ.log("Hello world")
IJ.log("This is a string followed by an int " + str(10))

import net.imagej.ops.OpUtils
ops_list = {}
IJ.log(ops.help())
for op in ops:
    ns   = OpUtils.getNamespace(op)
    name = OpUtils.stripNamespace(op)
    if (ns not in ops_list):
        ops_list['name'] = str(ns)
    else:
        ops_list['name'] = str(ops_list['name']) + ', ' + ns

IJ.log(ops_list)
