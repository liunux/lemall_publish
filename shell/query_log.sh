#!/bin/bash
[[ -z $1 ]] && echo  "Usage: query_log.sh [file] [key] [id]" && exit 1
[[ -z $2 ]] && echo  "Usage: query_log.sh [file] [key] [id]" && exit 1
[[ -z $3 ]] && echo  "Usage: query_log.sh [file] [key] [id]" && exit 1
file=$1
key=$2
id=$3
[[ $key == '*' ]] && cat $file && exit 0 
num=$(sed -n '/'$key'\|'$id'/='  $file)
[[ -z $num ]] && exit 1
all_count=$(echo $num|awk '{print NF}')
count=0
#b=''
for i in $num;do
    line=$(sed -n ${i}p $file)
    tag=$(echo "$line"|awk '{print $1}')
    key_line=$(echo "$line"|grep -Ew "$key|$id")
    if [[ -z $key_line ]];then
        query=$(echo "$line"|grep -w "^$tag")
        if [[ -z $query ]];then
            key_line=${line}
        else
           key_line="" 
        fi
    fi
    result=$resul$key_line
    echo "$result"|grep -v "^$"|grep -E "init.py|auto.py"
    (( count++ ))
    #echo $(echo "scale=3; $count / $all_count * 100" | bc -l)%
    #printf "progress:[%-50s]%d%%\r" $b $count
    #b=#$b
done
exit 0
