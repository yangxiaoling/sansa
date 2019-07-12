#!/bin/bash

echo $0 $1
md5_str=$1
for i in $(seq 1 30);do
    ssh_pid=`ps -ef | grep $md5_str | grep -v 'grep' | grep -v 'session_tracker.sh' | grep -v sshpass | awk '{print $2}'`
    echo "ssh session pid:$ssh_pid"
    if ["$ssh_pid" = ""];then
        sleep 2;
        continue;
    else
        today=`date "+%Y_%m_%d"`
        today_audit_dir="logs/audit/$today"
        echo "today_audit_dir" $today_audit_dir
        if [ -d $today_audit_dir ];  # 判断目录是否存在
        then
            echo "--start tracking log--"
        else
            sudo mkdir -r $today_audit_dir
        fi;
        echo 123456 | sudo -S /usr/bin/strace -ttt -f -p $ssh_pid -o "$today_audit_dir/$md5_str.log"  # 这样会默认在用户主目录下生成文件, 不是脚本所在目录哦, mmp...
        break;
    fi;

done;