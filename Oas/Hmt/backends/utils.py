import os
from hashlib import md5
# import django                       #先导入django的app，这样才能导入相关模块和配置
# django.setup()
from Hmt import models
from Oas import settings
from Hmt.backends import tasks
class ArgvManagement(object):
    '''
    接收用户指令并分配到相应模块
    '''
    def __init__(self,data):
        self.data = data
        # self.check_data()

    def check_data(self):
        file_check = self.file_md5()
        hosts_check = self.fetch_hosts()
        print('fetch_hosts:%s'%hosts_check)
        callback_error = '输入错误'
        if file_check and hosts_check:
            callback_error += file_check + hosts_check
            return callback_error
        elif not file_check and not hosts_check:
            self.new_task_obj = tasks.TaskHandle(self.data_dic,self)
        else:
            if file_check:
                callback_error += file_check
            elif hosts_check:
                callback_error += hosts_check
            return callback_error
    # def fetch_task_id(self):
    #     return self.new_task_obj.apply_new_task()

    def process(self):
        #生成新任务
        self.new_task_obj.dispatch_task()


    def worker(self,obj):
        obj.dispatch_task()

    def file_md5(self):
        file_name = self.data['scripte_name']
        file_path = '%s/%s'%(settings.SCRIPTS_DIR,file_name)
        if os.path.exists(file_path):
            m = md5()
            a_file = open(file_path, 'rb')    #需要使用二进制格式读取文件内容
            m.update(a_file.read())
            a_file.close()
            self.data_dic = {'file_name':file_name,
                             'file_md5':m.hexdigest()}
        else:
            return "<br/>&nbsp&nbsp&nbsp&nbsp&nbsp脚本文件:[%s] 不存在!"%file_name
        # except Exception as e:
        #     print('ERROR:the script_file upload ftp_server faiure !!')

    def fetch_hosts(self):
        '''
        获取主机
        :return:
        '''
        print('--fetching hosts---')
        host_list = []
        host_list_src = []
        group_list = []
        unregistered_hosts =[]
        unregistered_groups =[]
        data_hosts = self.data['hosts']
        data_groups = self.data['groups']
        for data_host in data_hosts:
            if models.Host.objects.filter(ip=data_host):
                host_list.append(data_host)
            else:
                unregistered_hosts.append(data_host)
        for data_group in data_groups:
            if not models.HostGroup.objects.filter(name=data_group):
                unregistered_groups.append(data_group)
            else:
                group_list.append(data_group)
        check_info = ''
        if unregistered_hosts and unregistered_groups:
            check_info +=  '<br/>&nbsp&nbsp&nbsp&nbsp&nbsp未注册主机：%s!'%unregistered_hosts + '<br/>&nbsp&nbsp&nbsp&nbsp&nbsp未注册主机组：%s!'%unregistered_groups
        elif not unregistered_hosts and not unregistered_groups:
            host_list += models.Host.objects.filter(ip__in=host_list_src)
            group_obj_list = models.HostGroup.objects.filter(name__in=group_list)
            for group in group_obj_list:
                host_list += group.hosts.select_related()
            self.host_list = set(host_list)
        else:
            if unregistered_hosts:
                check_info +=  '<br/>&nbsp&nbsp&nbsp&nbsp&nbsp未注册主机：%s!'%unregistered_hosts
            elif unregistered_groups:
                check_info += '<br/>&nbsp&nbsp&nbsp&nbsp&nbsp未注册主机组：%s!'%unregistered_groups
        return check_info