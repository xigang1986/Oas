import json,redis
from Hmt import models

class FetchCallbackInfo():
    def __init__(self,task_id,client_ip):
         self.task_id = task_id
         self.client_ip = client_ip

    def fetch(self):
        obj = models.Host.objects.get(ip=self.client_ip)
        client_id = obj.id
        self.redis_conn =redis.Redis(host='192.168.101.200',port=6379,db=0)
        fetch_info = self.redis_conn.get('TASK_%s_%s_INFO'%(self.task_id,client_id))
        if fetch_info:
            print(fetch_info,100000000000000)
            return fetch_info
        else:
            return '未获取到数据'