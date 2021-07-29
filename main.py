#coding:utf-8
import os
import re
import sys
from glob import glob
import subprocess as sp

class PowerShell:
    # from scapy
    def __init__(self, coding, ):
        cmd = [self._where('PowerShell.exe'),
               "-NoLogo", "-NonInteractive",  # Do not print headers
               "-Command", "-"]  # Listen commands from stdin
        startupinfo = sp.STARTUPINFO()
        startupinfo.dwFlags |= sp.STARTF_USESHOWWINDOW
        self.popen = sp.Popen(cmd, stdout=sp.PIPE, stdin=sp.PIPE, stderr=sp.STDOUT, startupinfo=startupinfo)
        self.coding = coding

    def __enter__(self):
        return self

    def __exit__(self, a, b, c):
        self.popen.kill()

    def run(self, cmd, timeout=15):
        b_cmd = cmd.encode(encoding=self.coding)
        try:
            b_outs, errs = self.popen.communicate(b_cmd, timeout=timeout)
        except sp.TimeoutExpired:
            self.popen.kill()
            b_outs, errs = self.popen.communicate()
        outs = b_outs.decode(encoding=self.coding)
        return outs, errs

    @staticmethod
    def _where(filename, dirs=None, env="PATH"):
        """Find file in current dir, in deep_lookup cache or in system path"""
        if dirs is None:
            dirs = []
        if not isinstance(dirs, list):
            dirs = [dirs]
        if glob(filename):
            return filename
        paths = [os.curdir] + os.environ[env].split(os.path.pathsep) + dirs
        try:
            return next(os.path.normpath(match)
                        for path in paths
                        for match in glob(os.path.join(path, filename))
                        if match)
        except (StopIteration, RuntimeError):
            raise IOError("File not found: %s" % filename)

if __name__ == '__main__':
    pfile = open('WIFI历史密码列表.txt', 'a+')
    empty_str=''
    wifi_names_arr_str = os.popen('netsh wlan show profiles')
    wifi_names_arr = re.findall('所有用户配置文件 : (.*?)\n', wifi_names_arr_str.read(), re.S)
    wifi_names_arr_len = str(len(wifi_names_arr))
    pfile.write('本机共有'+wifi_names_arr_len+'个WiFi，历史密码如下：\n')
    if not len(wifi_names_arr_len):
        pfile.close()
        sys.exit()
    pfile.write('\n【需要密码的wifi】:\n')
    index=0
    for i in wifi_names_arr:
        index = index + 1
        os.system("cls")
        print('该程序由吾爱破解论坛-GMCN制作 完全开源免费')
        print('密码生成中，请稍等........')
        print('本机共有' + wifi_names_arr_len + '个WiFi')
        print(str(index)+'/'+wifi_names_arr_len)
        with PowerShell('GBK') as ps:
            outs, errs = ps.run("netsh wlan show profiles '" + i + "' key=clear")
        c = re.findall('关键内容\s.*:(.*?)费用设置', outs, re.S)
        if len(c) :
            pfile.write(i + ' : ' + c[0].strip() + '\n')
        else:
            empty_str += i + ' : \n'
    pfile.write('\n【直接连接的wifi】:\n')
    pfile.write(empty_str)
    pfile.close()
    print('密码生成完毕！请查看【WIFI历史密码列表.txt】文件')
    os.system("pause")
    sys.exit()