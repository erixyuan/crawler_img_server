#!/usr/bin/env python
# coding:utf-8

'''
反编译GP的apk文件，得到所有继承自MessageNano的类，并输出其
writeTo和mergeFrom函数到文本文件
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
code_file = sys.argv[2]
apk = APK(apk_file)
dvm = DalvikVMFormat(apk.get_dex())
vma = uVMAnalysis(dvm)

# 所有proto类都继承自MessageNano
proto_classes = filter(lambda c: "MessageNano;" in c.get_superclassname(), dvm.get_classes())
proto_class_names = map(lambda c: c.get_name(), proto_classes)
methods = dvm.get_methods()

out_handle = open(code_file, 'w')
for class_name in proto_class_names:
    # 得到该类的所有方法: 
    class_methods = filter(lambda c: c.get_class_name() == class_name, methods)
    out_handle.write(class_name+"\n")
    # 打印出其writeto和mergefrom方法
    for method in class_methods:
        ms = decompile.DvMethod(vma.get_method(method))
        ms.process()
        out_handle.write(ms.get_source()+"\n\n")
    out_handle.write(20*"-"+"\n")
out_handle.close()


