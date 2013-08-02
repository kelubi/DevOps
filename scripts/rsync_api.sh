#!/bin/bash

#Script:bshare_rsync.sh
#Author:damon
#DATE:2013/07/15
#REV:1.0
#Action:package rsync function into an api

SYNC_USER=""
SYNC_USER_ID=""
SYNC_PORT=
SYNC_AUTH="ssh -p $SYNC_PORT -i $SYNC_USER_ID"
RSYNC="/usr/bin/rsync"

function move_file(){
    #3 parametes for this function
    #move files by rsync
    CP="/bin/cp"
    REMOTE_IP=$1
    MV_SOURCE=$2
    MV_TARGET=$3
    MV_LOG="$(dirname $0)/$FUNCNAME.log"
    #commond to run
    $SYNC_AUTH $SYNC_USER@$REMOTE_IP "sudo $RSYNC -PHXaz --stats --delete $MV_SOURCE $MV_TARGET" >/dev/null 2>&1
    #return result and record in log
    if [ $? -eq 0 ]; then
        echo "[Successful] $FUNCNAME $MV_SOURCE to $MV_TARGET on $REMOTE_IP"
        echo "`date +'%Y-%m-%d %H:%M:%S'` [Successful] $FUNCNAME $MV_SOURCE to $MV_TARGET on $REMOTE_IP">> $MV_LOG
    else
        echo "[Error] $FUNCNAME $MV_SOURCE to $MV_TARGET on $REMOTE_IP"
        echo "`date +'%Y-%m-%d %H:%M:%S'` [Error] $FUNCNAME $MV_SOURCE to $MV_TARGET on $REMOTE_IP" >> $MV_LOG
    fi
}

function send_file(){
    #2 parametes for this function
    RSYNC_SOURCE=$1
    RSYNC_TARGET=$2
    MV_LOG="$(dirname $0)/$FUNCNAME.log"
    $RSYNC -PHXaz --rsh "$SYNC_AUTH" --stats --delete --rsync-path "sudo rsync" $RSYNC_SOURCE $SYNC_USER@$RSYNC_TARGET >/dev/null 2>&1
    if [ $? -eq 0 ]; then
        echo "[Successful] $FUNCNAME $RSYNC_SOURCE to $RSYNC_TARGET"
        echo "`date +'%Y-%m-%d %H:%M:%S'` [Successful] $FUNCNAME $RSYNC_SOURCE to $RSYNC_TARGET">> $MV_LOG
    else
        echo "[Error] $FUNCNAME $RSYNC_SOURCE to $RSYNC_TARGET"
        echo "`date +'%Y-%m-%d %H:%M:%S'` [Error] $FUNCNAME $RSYNC_SOURCE to $RSYNC_TARGET" >> $MV_LOG
    fi
}

function service(){
    #3 parametes for this function
    REMOTE_IP=$1
    S_SHELL=$2
    S_CMD=$3
    #commond to run
    $SYNC_AUTH $SYNC_USER@$REMOTE_IP "sudo bash $S_SHELL $S_CMD" >/dev/null 2>&1
    if [ $? -eq 0 ];then
        echo "[Successful] $S_SHELL $S_CMD on $REMOTE_IP"
    fi
}

#$1 is function name,running as function $2 $3 ...
#echo $*
eval $*
