#!/bin/bash

run_algo=1
del_output=0

if [ $del_output -eq 1 ]
then 
    rm -rf ./basic_outputs
    rm -rf ./efficient_outputs
    echo 'outputs deleted'
fi

mkdir basic_outputs
mkdir efficient_outputs
input_dir='datapoints' #SampleTestCase
if [ $run_algo -eq 1 ]
then
    for file in `ls $input_dir`
        do  
            sh basic.sh $input_dir"/"$file "basic_outputs/output"${file:2}
            sh efficient.sh $input_dir"/"$file "efficient_outputs/output"${file:2}
            # for testing 
            # python3 efficient_wrong.py $input_dir"/"$file "efficient_outputs/output"${file:2}
        done
fi  

python3 plot.py $input_dir "basic_outputs" "efficient_outputs"



echo 'done'





