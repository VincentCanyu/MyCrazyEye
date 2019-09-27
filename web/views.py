from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.decorators import login_required
import json

from backend.multitask import MultiTaskManager
from web import models

# Create your views here.
@login_required
def dashboard(request):
    return render(request,'index.html')

def acc_login(request):
    login_err = ''
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username,password=password)
        if user:
            login(request,user)
            return redirect(request.GET.get('next','/'))
        else:
            login_err = 'Username or Password error!'
    return render(request,'login.html',{'login_err':login_err})
    
def acc_logout(request):
    logout(request)
    return redirect('/login/')

@login_required
def web_ssh(request):
    return render(request,'web_ssh.html')

@login_required
def host_mgr(request):
    return render(request,'host_mgr.html')

@login_required
def file_transfer(request):
    return render(request,'file_transfer.html')

@login_required
def batch_task_mgr(request):
    print('request.POST:',request.POST)
    task_data = json.loads(request.POST.get('task_data'))
    print('request.user:',request.user) #vin@123.com
    print('task_data:',task_data)

    task_obj = MultiTaskManager(request)
    response = {'task_id':task_obj.task_obj.id,
                'selected_hosts':list(task_obj.task_obj.tasklogdetail_set.all().values('id',
                              'host_to_remote_user__host__name',
                              'host_to_remote_user__host__ip_addr',
                              'host_to_remote_user__remote_user__username'))}
    return HttpResponse(json.dumps(response))


def task_result(request):
    task_id = request.GET.get('task_id')
    sub_tasklog_objs = models.TaskLogDetail.objects.filter(task_id=task_id)
    log_data = list(sub_tasklog_objs.values('id','status','result'))

    return HttpResponse(json.dumps(log_data))
