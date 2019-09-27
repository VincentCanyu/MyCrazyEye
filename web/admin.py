from django.contrib import admin
from .import models

# Register your models here.

class TaskAdmin(admin.ModelAdmin):
    list_display = ('id','task_type','content','data')
    
class TaskLogAdmin(admin.ModelAdmin):
    list_display = ('task','result','status','data')

class HostAdmin(admin.ModelAdmin):
    list_display = ('name','ip_addr','port','idc')

class AuditAdmin(admin.ModelAdmin):
    list_display = ('host_to_remote_user','log_type','content','date')


admin.site.register(models.Host,HostAdmin)
admin.site.register(models.HostToRemoteUser)
admin.site.register(models.HostGroup)
admin.site.register(models.RemoteUser)
admin.site.register(models.UserProfile)
admin.site.register(models.IDC)
admin.site.register(models.AuditLog,AuditAdmin)
admin.site.register(models.Task,TaskAdmin)
admin.site.register(models.TaskLogDetail,TaskLogAdmin)
