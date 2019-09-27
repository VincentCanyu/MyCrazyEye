# -*- coding: utf-8 -*-
import sys,os
import time,paramiko
from concurrent.futures import ThreadPoolExecutor
import json

import paramiko

def ssh_cmd(sub_task_obj):
    host_to_user_obj = sub_task_obj.host_to_remote_user
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(hostname=host_to_user_obj.host.ip_addr,
                   port=host_to_user_obj.host.port,
                   username=host_to_user_obj.remote_user.username,
                   password=host_to_user_obj.remote_user.password)
        stdin, stdout, stderr = ssh.exec_command(sub_task_obj.task.content)
        stdout_res = stdout.read()
        stderr_res = stderr.read()

        sub_task_obj.result = stdout_res + stderr_res
        print('result>>>>',sub_task_obj.result)

        if stderr_res:
            sub_task_obj.status = 2
        else:
            sub_task_obj.status = 1
    except Exception as e:
        sub_task_obj.result = e
        sub_task_obj.status = 2
    sub_task_obj.save()
    ssh.close()

def file_transfer(sub_task_obj,task_data):
    print('===========')
    host_to_user_obj = sub_task_obj.host_to_remote_user
    try:
        t = paramiko.Transport((host_to_user_obj.host.ip_addr,host_to_user_obj.host.port))
        t.connect(username=host_to_user_obj.remote_user.username,password=host_to_user_obj.remote_user.password)
        sftp = paramiko.SFTPClient.from_transport(t)
        if task_data['file_transfer_type'] == 'send':
            print('send=======')
            sftp.put(task_data['local_file_path'],task_data['remote_file_path'])
            result = 'file [%s] sends to [%s] succed!'%(task_data['local_file_path'],task_data['remote_file_path'])
        else:
            print('get=======')
            local_file_path = conf.settings.DOWNLOAD_DIR
            if not os.path.isdir('%s%s'%(local_file_path,sub_task_obj.task.id)):
                os.mkdir('%s%s'%(local_file_path,sub_task_obj.task.id))
            filename = '%s.%s'%(sub_task_obj.host_to_remote_user.host.ip_addr,task_data['remote_file_path'].split('/')[-1])
            sftp.get(task_data['remote_file_path'],'%s%s/%s'%(local_file_path,sub_task_obj.task.id,filename))
            result = 'download remote file [%s] succed!'%(task_data['remote_file_path'])
        t.close()
        
        sub_task_obj.status = 1
    except Exception as e:
        print('e--->>',e)
        result = e
        sub_task_obj.status = 2
    sub_task_obj.result = result
    sub_task_obj.save()


if __name__ == '__main__':
    dir_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.append(dir_path) #把s3CrazyEye加到环境变量列表内

    os.environ.setdefault("DJANGO_SETTINGS_MODULE","s3CrazyEye.settings")
    import django
    django.setup()
    from django import conf
    from web import models

    if len(sys.argv) == 1:
        exit("task id not provided!")
    task_id = sys.argv[1]
    task_obj = models.Task.objects.get(id=task_id) #取到任务
    print('task runner--》',task_obj)

    pool = ThreadPoolExecutor(10)
    
    if task_obj.task_type == 'cmd':
        for sub_task_obj in task_obj.tasklogdetail_set.all(): #该任务所有任务子结果
            pool.submit(ssh_cmd,sub_task_obj)
    else:
        task_data = json.loads(task_obj.content)
        print('task_data>>>:',task_data)
        for sub_task_obj in task_obj.tasklogdetail_set.all(): #该任务所有任务子结果
            pool.submit(file_transfer,sub_task_obj,task_data)
            
    pool.shutdown(wait=True)
