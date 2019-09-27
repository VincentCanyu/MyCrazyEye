# -*- coding: utf-8 -*-
import json
import subprocess
from django import conf

from web import models

class MultiTaskManager(object):
    def __init__(self,request):
        self.request = request
        self.run_task()

    def task_parser(self):
        '''解析任务'''
        self.task_data = json.loads(self.request.POST.get('task_data'))
        task_type = self.task_data.get('task_type')

        if hasattr(self,task_type):
            task_func = getattr(self,task_type)
            task_func()
        else:
            print('cannot find task',task_type)

    def run_task(self):
        '''调用任务'''
        self.task_parser()

    def cmd(self):
        '''批量命令
        1.生成任务在数据库中的记录，拿到任务id
        2.触发任务，不阻塞
        3.返回任务id给前端
        '''
        task_obj = models.Task.objects.create(
            task_type = 'cmd',
            content = self.task_data.get('cmd'),
            user = self.request.user
        )

        selected_host_ids = set(self.task_data['selected_hosts']) #取出所有主机的id。有可能选择的是同一个主机，使用set去重
        task_log_objs = []
        for id in selected_host_ids:
            task_log_objs.append(
                models.TaskLogDetail(task=task_obj,host_to_remote_user_id=id,result='init...')
            )
        # 每创建一条记录，然后save()的时候都会访问一次数据库，数据库commit一次，导致性能问题。使用bulk_create批量创建，要么全部成功，或全部失败。（事务）
        models.TaskLogDetail.objects.bulk_create(task_log_objs)

        task_script = "python3 %s/backend/task_runner.py %s"%(conf.settings.BASE_DIR,task_obj.id)

        # Popen对象创建后，主程序不会自动等待子进程完成。我们必须调用对象的wait()方法，即cmd_process.wait()，父进程才会等待 (也就是阻塞block)。
        #subprocess.Popen开启一个独立的进程，交给操作系统，启动这个独立脚本task_script，他脱离了django。
        cmd_process = subprocess.Popen(task_script,shell=True)

        print('running batch commands.....')

        self.task_obj = task_obj
        
        
    def file_transfer(self):
        '''文件分发'''
        task_obj = models.Task.objects.create(
            task_type = 'file-transfer',
            content = json.dumps(self.task_data),
            user = self.request.user
        )
        selected_host_ids = set(self.task_data['selected_hosts']) #取出所有主机的id。有可能选择的是同一个主机，使用set去重
        task_log_objs = []
        for id in selected_host_ids:
            task_log_objs.append(
                models.TaskLogDetail(task=task_obj,host_to_remote_user_id=id,result='init...')
            )
        models.TaskLogDetail.objects.bulk_create(task_log_objs)

        task_script = "python3 %s/backend/task_runner.py %s"%(conf.settings.BASE_DIR,task_obj.id)
        cmd_process = subprocess.Popen(task_script,shell=True)

        print('running batch file transfer.....')

        self.task_obj = task_obj	
