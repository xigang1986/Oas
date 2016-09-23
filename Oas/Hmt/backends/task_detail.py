import json,redis
from Hmt import models
from Oas import settings

class HandleCallback():
    def __init__(self,task_id,flag):
        self.task_id = task_id
        self.flag = flag
        self.fetch_task_data()

    def fetch_task_data(self):
        self.redis_conn =redis.Redis(host=settings.REDIS_CONN['host'],port=settings.REDIS_CONN['port'],db=0)
        task_host_list = self.redis_conn.get('TASK_CALLBACK_%s_HOST_LIST'%self.task_id)
        callback_all_ok_list = self.redis_conn.get('TASK_CALLBACK_%s_ALL_OK'%self.task_id)
        callback_all_no_ok_list = self.redis_conn.get('TASK_CALLBACK_%s_ALL_NO_OK'%self.task_id)
        if task_host_list:
            self.task_host_list = json.loads(task_host_list.decode())
        print(callback_all_ok_list,111111111111)
        print(callback_all_no_ok_list,22222222222)
        print(task_host_list,33333333)
        if callback_all_ok_list:
            self.callback_all_ok_list = json.loads(callback_all_ok_list.decode())
            print(self.callback_all_ok_list,11111111111144)
        if callback_all_no_ok_list:
            if callback_all_no_ok_list.decode() == 'is_none':
                self.callback_all_no_ok_list = 'is_none'
            else:
                self.callback_all_no_ok_list = json.loads(callback_all_no_ok_list.decode())

    def handle1(self):
        fetch_info = {}
        if self.callback_all_ok_list:
            suc_ips = {}
            print('flag:%s'%self.flag)
            print(self.callback_all_ok_list)
            if self.flag == 0:
                print(12121)
                for client in self.callback_all_ok_list:
                    print(client,1985)
                    obj = models.Host.objects.get(id=client['client_id'])
                    print(obj,19860121)
                    suc_ips[obj.ip] = client['callback_code']
                fetch_info['suc_ips'] = suc_ips
                fetch_info['code'] = 0
                print(fetch_info,98989898989)
                return fetch_info
            else:
                print(17173)
                while True:
                    print(self.redis_conn.lrange('TASK_CALLBACK_%s'%self.task_id,start=0,end=-1),44444444444444444443)
                    if self.redis_conn.lrange('TASK_CALLBACK_%s'%self.task_id,start=0,end=-1):
                        redis_pop = self.redis_conn.rpop('TASK_CALLBACK_%s'%self.task_id)
                        print(redis_pop,876876)
                        callback_suc = json.loads(redis_pop.decode())
                        if callback_suc:
                            obj = models.Host.objects.get(id=callback_suc['client_id'])
                            print(obj.ip,1986012190909999)
                            suc_ips[obj.ip] = callback_suc['callback_code']
                    else:
                        break
                fetch_info['suc_ips'] = suc_ips
                fetch_info['code'] = 0
                return fetch_info
    def handle2(self):
        print(211111111111111)
        fetch_info = {}
        if self.callback_all_no_ok_list:
            print(22222222222222)
            suc_ips = {}
            if self.flag == 0:
                set_all = set(self.task_host_list)
                set_suc = set()
                if not self.callback_all_no_ok_list == 'is_none':
                    for suc_ip in self.callback_all_no_ok_list:
                        obj1 = models.Host.objects.get(id=suc_ip['client_id'])
                        suc_ips[obj1.ip] = suc_ip['callback_code']
                        set_suc.add(obj1.ip)
                print(type(set_all),91919191)
                print(type(set_suc),92929292)
                set_timeout = list(set_all-set_suc)
                # set_timeout = self.task_host_list
                fetch_info['code'] = 0
                fetch_info['timeout_ips'] = set_timeout
                fetch_info['suc_ips'] = suc_ips
                print(fetch_info,56565656)
                return fetch_info
            else:
                while True:
                    if self.redis_conn.lrange('TASK_CALLBACK_%s'%self.task_id,start=0,end=-1):
                        redis_pop = self.redis_conn.rpop('TASK_CALLBACK_%s'%self.task_id)
                        print(redis_pop,876876)
                        callback_suc = json.loads(redis_pop.decode())
                        if not callback_suc:
                            obj = models.Host.objects.get(id=callback_suc['client_id'])
                            print(obj.ip,1986012190909999)
                            suc_ips[obj.ip] = callback_suc['callback_code']
                    else:
                        break
                if suc_ips:
                    fetch_info['suc_ips'] = suc_ips
                set_all = set(self.task_host_list)
                set_suc = set()
                if not self.callback_all_no_ok_list == 'is_none':
                    for suc_ip in self.callback_all_no_ok_list:
                        obj1 = models.Host.objects.get(id=suc_ip['client_id'])
                        set_suc.add(obj1.ip)
                print(type(set_all),91919191)
                print(type(set_suc),92929292)
                set_timeout = list(set_all-set_suc)
                # set_timeout = self.task_host_list
                fetch_info['code'] = 0
                fetch_info['timeout_ips'] = set_timeout
                print(fetch_info,56565656)
                return fetch_info
    def handle3(self):
        fetch_info = {}
        suc_ips = {}
        task_obj = models.Task.objects.filter(id=self.task_id)
        if task_obj:
            while True:
                if self.redis_conn.lrange('TASK_CALLBACK_%s'%self.task_id,start=0,end=-1):
                    redis_pop = self.redis_conn.rpop('TASK_CALLBACK_%s'%self.task_id)
                    print(redis_pop,876876)
                    callback_suc = json.loads(redis_pop.decode())
                    if callback_suc:
                        obj = models.Host.objects.get(id=callback_suc['client_id'])
                        print(obj.ip,1986012190909999)
                        suc_ips[obj.ip] = callback_suc['callback_code']
                else:
                    break
            if suc_ips:
                fetch_info['suc_ips'] = suc_ips
            fetch_info['code'] = 1
            print(fetch_info,9494949494)
            return fetch_info
        else:
            fetch_info['code'] = 2
            return fetch_info