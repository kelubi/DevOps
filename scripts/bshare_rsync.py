#!/usr/bin/python
import sys, time, string
from subprocess import call
from threading import Thread
from Queue import Queue

"""
#Script:bshare_rsync.py
#Author:damon
#DATE:2013/07/22
#REV:1.0
#Action:rsync file to production environment
#Update:modify rsync function by damon @20130715
#Update:modify add thread by damon @201307122
#Update:modify parameters name by damon @20130801
"""

Hostlist = {
    }

Applist = {
    }

#backup:backup file(running on remote server)
#send:send the latest code to remote server
#update:move the latest code to working directory(running on remote server)
#rollcak:move backup file to working directory(running on remote server)
Modelist = {
    'send':{'type':'send_file','from':'source_dir','to':'update_dir'},
    'backup':{'type':'move_file','from':'working_dir','to':'backup_dir'},
    'update':{'type':'move_file','from':'update_dir','to':'working_dir'},
    'rollback':{'type':'move_file','from':'backup_dir','to':'working_dir'}
    }

#function:running cmd
def rsyncer(n, Cmd_queue):
    Host = Cmd_queue.get()
    Rsync_Source = Applist[App][Modelist[Mode]['from']]
    Rsync_Target = Applist[App][Modelist[Mode]['to']]
    Ip = Hostlist[App][Host]['ip']
    if Modelist[Mode]['type'] == 'send_file':
        Cmd = "bash rsync_api.sh %s %s %s" % ('send_file', Rsync_Source, Ip + ':' + Rsync_Target)
        call(Cmd, shell=True)
    if Modelist[Mode]['type'] == 'move_file':
        if Mode in Applist[App]['restart_mode']:
            Stop = "bash rsync_api.sh %s %s %s %s" % ('service', Ip, Applist[App]['restart_mode']['restart_file'], 'stop')
            call(Stop, shell=True)
        Cmd = "bash rsync_api.sh %s %s %s %s" % ('move_file', Ip, Rsync_Source, Rsync_Target)
        call(Cmd, shell=True)
        if Mode in Applist[App]['restart_mode']:
            Start = "bash rsync_api.sh %s %s %s %s" % ('service', Ip, Applist[App]['restart_mode']['restart_file'], 'start')
            call(Start, shell=True)
    Cmd_queue.task_done()
    #Rsync_log = ''
    #Ret = call(Cmd, stdout=open(Rsync_log, 'a') , shell=True)

##########Main##########
#get parameters,check parameters
Mode, App, Hosts = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
if Mode not in Modelist:
    print "[ERROR] no %s Mode ." % Mode
    sys.exit()
if App not in Applist:
    print "[ERROR] no %s App ." % App
    sys.exit()
for Host in Hosts:
    if Host not in Hostlist[App]:
        print "[ERROR] server %s is not in %s cluster ." % (Host,App)
        sys.exit()

#create a queue,running cmd by thread
Num_threads = len(Hosts)
Cmd_queue = Queue()

for n in range(Num_threads):
    worker = Thread(target = rsyncer, args=(n, Cmd_queue))
    worker.setDaemon(True)
    worker.start()

for h in Hosts:
  Cmd_queue.put(h)

Cmd_queue.join()
print "Done!"
