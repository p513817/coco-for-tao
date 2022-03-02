#!/bin/bash

function check(){
    REQUIRED_PKG=$1
    PKG_OK=$(dpkg-query -W --showformat='${Status}\n' $REQUIRED_PKG|grep "install ok installed")
    echo Checking for $REQUIRED_PKG: $PKG_OK
    if [ "" = "$PKG_OK" ]; then
    echo "No $REQUIRED_PKG. Setting up $REQUIRED_PKG."
    sudo apt-get --yes install $REQUIRED_PKG > /dev/null
    fi
}

check boxes
check bsdmainutils

INFO="\
Index; Name; Jetson Nano; Jetson Xavier; Weights\n\
1; ${NAME_1}; 22; 251; download (81MB)\n\
2; ${NAME_2}; 12; 101; download (84MB)"



INFO="\
MSCOCO ( COCO 2014 )\n\
\n\
Option; Name; Size\n\
train; train2014.zip; 13G\n\
val; val2014; 6G\n\
test; test2014; 6G\n\
anno; annotations_trainval2014.zip; 241M\n"

awk -v var="$INFO" 'BEGIN {print var}' | column -t -s ';' | boxes -p a1l4r4
printf "Select a mscoco dataset you want to download [train/test/val/anno/all]: "
read SEL

case ${SEL} in

    "train")
        # train images 13GB
        wget http://images.cocodataset.org/zips/train2014.zip
        ;;
    "val")
        # val images 6GB
        wget http://images.cocodataset.org/zips/val2014.zip
        ;;
    "all")
        # test images 6GB
        wget http://images.cocodataset.org/zips/test2014.zip
        ;;
    "anno")
        wget http://images.cocodataset.org/annotations/annotations_trainval2014.zip
        ;;
    *)
        echo "Unexcepted input, please run again."
        exit
        ;;
esac