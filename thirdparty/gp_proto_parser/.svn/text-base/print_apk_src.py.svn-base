#!/usr/bin/env python
# coding:utf-8

'''
反编译apk
'''

import sys
sys.path.append("../androguard")

from androguard.core import *
from androguard.core.androgen import *
from androguard.core.androconf import *
from androguard.core.bytecode import *
from androguard.core.bytecodes.jvm import *
from androguard.core.bytecodes.dvm import *
from androguard.core.bytecodes.apk import *
from androguard.core.analysis.analysis import *
from androguard.decompiler.dad import decompile

apk_file = sys.argv[1]
code_dir = sys.argv[2]
apk = APK(apk_file)
dvm = DalvikVMFormat(apk.get_dex())
vma = uVMAnalysis(dvm)

classes = dvm.get_classes()
class_names = map(lambda c: c.get_name(), classes)
methods = dvm.get_methods()

for class_name in class_names:
    out_file = code_dir+'/'+class_name.replace("/", "_").replace(";", "").replace("$", "__")+'.java'
    out_handle = open(out_file, 'w')
    # 得到该类的所有方法: 
    class_methods = filter(lambda c: c.get_class_name() == class_name, methods)
    for method in class_methods:
        ms = decompile.DvMethod(vma.get_method(method))
        ms.process()
        out_handle.write(ms.get_source()+"\n")
    out_handle.close()


