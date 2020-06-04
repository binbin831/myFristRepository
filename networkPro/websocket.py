from urllib.request import urlopen

body =urlopen("http://www.baidu.com")

print(body.read())