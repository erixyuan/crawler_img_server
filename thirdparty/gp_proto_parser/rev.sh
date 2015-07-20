#!/bin/bash

gp_apk=$1
gp_proto=$2
gp_code=code.txt.$RANDOM_$RANDOM

./apk_rev.py $gp_apk $gp_code
if [ $? -ne 0 ];then
    echo "fail to do apk_rev!"
    exit 1
fi

./parse_code.py $gp_code $gp_proto
if [ $? -ne 0 ];then
    echo "fail to do parse_code!"
    exit 1
fi

#rm -f $gp_code
echo "parse gp proto success!"

