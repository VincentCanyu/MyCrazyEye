# -*- coding: utf-8 -*-
import getpass
from django.contrib.auth import authenticate

from backend import paramiko_ssh
from web import models

class SshHandler(object):
    def __init__(self,argv_handler_instance):
        self.argv_handler_instance = argv_handler_instance
        self.models = models #模块也可以当作变量？？

    def auth(self):
        """认证程序"""
        count = 0
        while count < 3:  #最多允许输入三次账密
            username = input("堡垒机账号:").strip()
            password = getpass.getpass("Password:").strip()
            user = authenticate(username=username,password=password)
            if user:
                self.user = user
                return True
            else:
                count += 1

    def interactive(self):
        """启动交互脚本"""
        if self.auth():
            print("Ready to print all the authorized hosts ... to this user ...")
            while True:
                host_group_list = self.user.host_groups.all() #该用户所有主机组，如<QuerySet [<HostGroup: WEB server>, <HostGroup: DB>]>
                for index,host_group_obj in enumerate(host_group_list):
                    print("%s.\t%s[%s]"%(index, host_group_obj.name, host_group_obj.host_to_remote_users.count())) #最后一个是打印每个主机组关联的第三张表host_to_remote_users的数量
                print("z.\t未分组主机[%s]" % (self.user.host_to_remote_users.all()).count())

                choice = input("请选择主机组>>:").strip()
                if choice.isdigit(): #是正数数字的话
                    choice = int(choice)
                    if choice <= host_group_list.count()-1:
                        selected_host_group = host_group_list[choice] #选择该用户的主机组
                    else:
                        print('请正确输入主机组!!!!')
                        continue
                elif choice == 'z':
                    selected_host_group = self.user #没有分组的时候
                else:
                    print('请正确输入主机组!!!!')
                    continue
                while True:
                    for index,host_to_remote_obj in enumerate(selected_host_group.host_to_remote_users.all()): #打印所选主机组关联的第三张表host_to_remote_users
                        print("%s.\t%s" % (index,host_to_remote_obj))

                    choice = input("请选择主机>>:").strip()
                    if choice.isdigit():
                        choice = int(choice)
                        if choice <= selected_host_group.host_to_remote_users.all().count():
                            selected_host_to_user_obj = selected_host_group.host_to_remote_users.all()[choice] #选择关联的第三张表host_to_remote_users
                            print("going to logon %s" % selected_host_to_user_obj)
                            paramiko_ssh.ssh_connect(self, selected_host_to_user_obj)
                            continue #退出连接之后，再次进入主机选择项。避免报错
                        else:
                            print('请正确输入主机!!!!')
                            continue
                    if choice == 'b':
                        break
                    else:
                        print('请正确输入主机!!!!')
                        continue
