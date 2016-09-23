from ftplib import FTP
import os
from Oas import settings

def ftpconnect(host, username, password):
    ftp = FTP()
    #ftp.set_debuglevel(2)         #打开调试级别2，显示详细信息
    ftp.connect(host, 21)          #连接
    ftp.login(username, password)  #登录，如果匿名登录则用空串代替即可
    return ftp

def downloadfile(ftp, remotepath, localpath):
    bufsize = 1024                #设置缓冲块大小
    fp = open(localpath,'wb')     #以写模式在本地打开文件
    ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize) #接收服务器上文件并写入本地文件
    ftp.set_debuglevel(0)         #关闭调试
    fp.close()                    #关闭文件

def uploadfile(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'rb')
    ftp.storbinary('STOR '+ remotepath , fp, bufsize) #上传文件
    ftp.set_debuglevel(0)
    fp.close()

def uoload(file_name):
    local_path = os.path.dirname(os.path.abspath(__file__))
    ftp = ftpconnect(settings.FTP_CONN['host'],settings.FTP_CONN['user'],settings.FTP_CONN['password'])
    #downloadfile(ftp, "***", "***")
    uploadfile(ftp, file_name, "%s\%s"%(local_path,file_name))
    ftp.quit()