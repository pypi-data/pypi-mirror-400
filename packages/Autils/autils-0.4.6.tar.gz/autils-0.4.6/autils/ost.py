'''
OS相关工具
'''
import uuid
import socket
import os
import tarfile


class OST(object):
    '''
    OS相关工具类
    '''

    @classmethod
    def get_mac(cls):
        '''
        获取mac地址
        '''
        try:
            return uuid.UUID(int=uuid.getnode()).hex[-12:]
        except Exception as ex:
            return None

    @classmethod
    def get_address(cls):
        '''
        获取本机ip
        '''
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            return ip
        except Exception as ex:
            return None

    @classmethod
    def sudo_cmd(cls, passwd, cmd):
        '''
        以sudo方式运行命令
        '''
        # 调用sudo命令执行
        os.system('echo %s|sudo -S %s' % (passwd, cmd))

    @classmethod
    def create_dir_if_not_exists(cls, path):
        '''
        创建文件夹
        '''
        if not os.path.exists(path):
            os.makedirs(path)

    @classmethod
    def untar(self, file, path):
        """
        解压压缩文件
        
        参数
        file: 压缩文件
        path: 解压文件的路径    
        """
        with tarfile.open(file) as f:
            for i in f.getnames():
                f.extract(i, path)
