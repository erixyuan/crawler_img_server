#!/usr/bin/env python
# coding:utf-8

'''
解析反编译后的代码，输出.proto文件
'''

import sys
import re


REGEX_LIST = [
    ("string", re.compile(" *if \(\(this\.has.*\) \|\| \(\!this\.(.*).equals\(\".*\"\)\)\) \{")),
    ("string", re.compile(" *if \(!this\.(.*).equals\(\".*\"\)\) \{")),
    ("int",    re.compile(" *if \(\(this\.(.*) != .*\) \|\| \(this.has.*\)\) \{")),
    ("int",    re.compile(" *if \(this\.(.*) != \-*\d*\) \{")),
    ("int64",  re.compile(" *if \(\(this\.has.*\) \|\| \(this\.(.*) != \-*\d*\)\) \{")),
    ("object", re.compile(" *if \(this\.(.*) != null\) \{")),
    ("array",  re.compile(" *if \(\(this\.(.*) != null\) .*\(this\..*\.length.*\)\) \{")),
    ("bool",   re.compile(" *if \(\(this\.has.*\) \|\| \(this\.(.*)\)\) \{")),
    ("bool",   re.compile(" *if \(this\.(.*)\) \{")),
    ("bytes",  re.compile(" *if \(\(this\.has.*\) \|\| \(\!java.util.Arrays.equals\(this\.(.*), .*EMPTY_BYTES\)\)\) \{")),
    ("bytes",  re.compile(" *if \(\!java.util.Arrays.equals\(this\.(.*), .*EMPTY_BYTES\)\) \{")),
    ("float",  re.compile(" *if \(\(this\.has.*\) \|\| \(Float\.floatToIntBits\(this.(.*)\) \!.*\)\)\) \{")),
    ("float",  re.compile(" *if \(Float\.floatToIntBits\(this.(.*)\) \!.*\)\) \{")),
    ("double", re.compile(" *if \(\(this\.has.*\) \|\| \(Double\.doubleToLongBits\(this.(.*)\) \!.*\)\)\) \{")),
    ("double", re.compile(" *if \(Double\.doubleToLongBits\(this.(.*)\) \!.*\)\) \{")),
    ]
WT_RE = re.compile(" *p\d*\.write(.*)\((\d+),.*\);")

class MessageInfo:
    def __init__(self):
        self.msg_name = ""
        self.is_group = False
        self.fields = []

class FieldInfo:
    def __init__(self):
        self.prefix = ""        # optional or repeated
        self.is_group = False   # group or message
        self.type = ""          # string, int32, ...
        self.field_id = 0       # field id: 1,2,...
        self.field_name = ""    # field name: subItem, ...

def do_if_block(code):
    # if函数必须是以下几种情况之一：
    # string: if ((this.hasSubtitle) || (!this.subtitle.equals(""))) {
    # string: if (!this.initialValue.equals("")) {
    # int:    if ((this.docType != 1) || (this.hasDocType)) {
    # int:    if (this.maxLength != 0) {
    # object: if (this.productDetails != null) {
    # array： if ((this.image != null) && (this.image.length > 0)) {
    # bool:   if ((this.hasDetailsReusable) || (this.detailsReusable)) {
    # bytes:  if ((this.hasServerLogsCookie) || (!java.util.Arrays.equals(this.serverLogsCookie, com.google.protobuf.nano.WireFormatNano.EMPTY_BYTES))) {
    # float:  if ((this.hasStarRating) || (Float.floatToIntBits(this.starRating) != Float.floatToIntBits(0))) {
    for regex_item in REGEX_LIST:
        match = regex_item[1].match(code)
        if match:
            groups = match.groups()
            return groups[0], regex_item[0]
    return None, None

def do_write_to(wf_codes):
    ''' 处理writeTo函数 '''
    field_list = []
    state = "find_if"
    for code in wf_codes:
        if state == "find_if":
            if " "*8+"if" == code[0:10]:
                state = "if_block"
                name, type = do_if_block(code)
                if not type:
                    print "ERROR: bad type[%s]" % code 
                    sys.exit(1)
            continue
        elif state == "if_block":
            if " "*8+"if" == code[0:10] or " "*8+"}" == code[0:9]:
                print "ERROR: if block error[%s]" % code
                sys.exit(1)
            match = WT_RE.match(code)
            if not match:
                continue
            type2, field_id = match.groups()
            field_list.append([name, type, type2, field_id])
            state = "find_if"
            continue
    return field_list

def do_merge_from(mf_codes):    
    ''' 处理mergeFrom函数 '''
    msg_type_dict = {}
    state = "find_case"
    message = []
    for code in mf_codes:
        if state == "find_case":
            if code[0:20] == " "*16 + "case":
                field_id = str(int(code.split("case ")[-1].strip(":")) >> 3)
                if field_id == '0':
                    continue
                state = "find_new"
                message = []
            continue
        elif state == "find_new":
            # 对于Message和Group，需要通过new操作符提取真正的类名
            # com.google.android.finsky.protos.DocumentV2$DocV2[] v2_2 = new com.google.android.finsky.protos.Common$Offer[(v1_2 + v0_2)];
            # v2_2[v1_2] = new com.google.android.finsky.protos.Common$Offer();
            if " = new " in code:
                #msg_type = code.split(" = new ")[-1].split("$")[-1].split("[")[0].split("(")[0].split(".")[-1].split("/")[-1]
                msg_type = code.split(" = new ")[-1].split("[")[0].split("(")[0].replace("/", ".")
                if (field_id, msg_type) not in message:
                    message.append((field_id, msg_type))
                    continue
            elif " break;" in code:
                if len(message) != 0:
                    field_id, msg_type = message[0]
                    # 如果一个case中出现了多个不同的new，则可能导致解析错误
                    if len(message) > 1:
                        print "WARNING, more than one new[%s]" % mgs_type
                    msg_type_dict[field_id] = msg_type
                state = "find_case"
                continue
    return msg_type_dict

def get_class_codes(file_in):
    class_code_dict = {}
    state = "classname"
    classname = ""
    wt_codes = []
    mf_codes = []
    for line in file(file_in):
        # 跳过空行
        if not line.strip():
            continue
        if state == "classname":
            if ';' != line[-2]:
                print "ERROR: bad classname[%s]" %line.strip()
                sys.exit(1)
            #classname = line.split("$")[-1].rstrip("\n;").split("/")[-1]
            classname = line.lstrip("L").rstrip("\n;").replace("/", ".")
            state = "find_func"
            continue
        elif state == "find_func":
            if "public void writeTo(" in line:
                wt_codes = []
                state = "writeTo"
                continue
            elif " mergeFrom(" in line and "public bridge" not in line:
                mf_codes = []
                state = "mergeFrom"
                continue
            elif "------" in line:
                if classname in class_code_dict:
                    print "*** class: %s" % classname
                class_code_dict[classname] = [wt_codes, mf_codes]
                classname = ""
                state = "classname"
                wt_codes = []
                mf_codes = []
                continue
        elif state == "writeTo":
            if "    }" == line[0:5]:
                state = "find_func"
            else:
                wt_codes.append(line.rstrip("\n"))
            continue
        elif state == "mergeFrom":
            if "    }" == line[0:5]:
                state = "find_func"
            else:
                mf_codes.append(line.rstrip("\n"))
            continue
    return class_code_dict

def parse_from_code(class_code_dict):
    # 1. 提取每个类的字段信息，code -> class
    class_dict = {}
    for k,v in class_code_dict.items():
        wt_code = v[0]
        mf_code = v[1]
        field_list = do_write_to(wt_code)
        msg_type_dict = do_merge_from(mf_code)
        class_dict[k] = [field_list, msg_type_dict]
    
    # 2. 把类的信息转化成Pb的消息格式，class -> message
    msg_info_dict = {}
    group_set = set()
    for classname in class_dict:
        field_list, msg_type_dict = class_dict[classname]
        msg_info = MessageInfo()
        msg_info.msg_name = classname
        for name, type, type2, field_id in field_list:
            field_info = FieldInfo()
            if type == "array":
                field_info.prefix = "repeated"
            else:
                field_info.prefix = "optional"
            field_info.field_name = name
            field_info.field_id = field_id
            if type2 in ["Message", "Group"]:
                if field_id not in msg_type_dict:
                    print "ERROR: fail to get Message[%s:%s]" % (classname, name)
                    sys.exit(1)
                field_info.type = msg_type_dict[field_id]
            else:
                field_info.type = type2.lower()

            if type2 == "Group":
                field_info.is_group = True
                if field_info.type not in group_set:
                    group_set.add(field_info.type)
                else:
                    print "ERROR: group [%s] already exists!" % field_info.type
                    sys.exit(1)
            else:
                field_info.is_group = False
            msg_info.fields.append(field_info)
        msg_info_dict[classname] = msg_info

    # 3. 标记group
    for classname in msg_info_dict:
        if classname in group_set:
            msg_info_dict[classname].is_group = True
    return msg_info_dict

def name(msg_full_name, name_dict):
    if msg_full_name in name_dict:
        return name_dict[msg_full_name]
    return msg_full_name

def print_msg(out_str, msg_info_dict, name_dict, msg_info, 
        tab_n=0, group_type=None, group_field_id=None, group_prefix=None):
    if msg_info.is_group == False:
        out_str += "message %s {\n" % name(msg_info.msg_name, name_dict)
        for field_info in msg_info.fields:
            if field_info.is_group == False:
                out_str += 2*" " + "%s %s %s = %s;\n" % (
                    field_info.prefix, name(field_info.type, name_dict), 
                    field_info.field_name, field_info.field_id)
            else:
                group = msg_info_dict[field_info.type]
                out_str = print_msg(out_str, msg_info_dict, name_dict, group, tab_n+2, 
                    field_info.type, field_info.field_id, field_info.prefix)
        out_str += "}\n"
    else:
        out_str += tab_n*" " + "%s group %s = %s {\n" % (
            group_prefix, name(group_type, name_dict), group_field_id)
        for field_info in msg_info.fields:
            if field_info.is_group == False:
                out_str += (tab_n+2)*" " + "%s %s %s = %s;\n" % (
                    field_info.prefix, name(field_info.type, name_dict), 
                    field_info.field_name, field_info.field_id)
            else:
                group = msg_info_dict[field_info.type]
                out_str = print_msg(out_str, msg_info_dict, name_dict, group, tab_n+2, 
                    field_info.type, field_info.field_id, field_info.prefix)
        out_str += tab_n*" " + "}\n"
    return out_str

def name_map(msg_info_dict):
    name_dict = {}
    cnt_dict = {}
    for msg_name in msg_info_dict:
        name = msg_name.split("$")[-1].split(".")[-1]
        if name not in cnt_dict:
            cnt_dict[name] = 1
        else:
            cnt_dict[name] += 1
        cnt = cnt_dict[name]
        if cnt > 1:
            name_dict[msg_name] = name+"_"+str(cnt)
        else:
            name_dict[msg_name] = name
    return name_dict

def print_proto(msg_info_dict, name_dict, out_file):
    out_handle = open(out_file, 'w')
    for msg_name in msg_info_dict:
        msg_info = msg_info_dict[msg_name]
        if msg_info.is_group == False:
            out_str = print_msg("", msg_info_dict, name_dict, msg_info)
            out_handle.write(out_str+"\n")
    out_handle.close() 

def local_main():
    class_code_dict = get_class_codes(sys.argv[1])
    msg_info_dict = parse_from_code(class_code_dict)
    name_dict = name_map(msg_info_dict)
    print_proto(msg_info_dict, name_dict, sys.argv[2])

if __name__ == "__main__":
    local_main()
