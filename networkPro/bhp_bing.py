#-*- coding:utf8 -*-
from burp import IBurpExtender
from burp import IContextMenuFactory

from javax.swing import JMenuItem
from java.util import List, ArrayList
from java.net import URL

import socket
import urllib
import json
import re
import base64

bing_api_key = "這里用你的密鑰"

class BurpExtender(IBurpExtender, IContextMenuFactory):
    def registerExtenderCallbacks(self,callbacks):
        self._callbacks = callbacks
        self._helpers = callbacks.getHelpers()
        self.context = None

        # 我們建立起擴展工具
        callbacks.setExtensionName("Use Bing")
        callbacks.registerContextMenuFactory(self)

        return

    # 創建菜單並處理點擊事件，就是actionPerformed那里，點擊調用bing_menu函數
    def createMenuItems(self, context_menu):
        self.context = context_menu
        menu_list = ArrayList()
        menu_list.add(JMenuItem("Send to Bing", actionPerformed=self.bing_menu))
        return menu_list

    def bing_menu(self, event):
        # 獲取用戶點擊的詳細信息
        http_traffic = self.context.getSelectedMessages()

        print "%d requests highlighted" % len(http_traffic)

        # 獲取ip或主機名(域名)
        for traffic in http_traffic:
            http_service = traffic.getHttpService()
            host = http_service.getHost()

            print "User selected host: %s" % host

            self.bing_search(host)

        return

    def bing_search(self, host):
        # 檢查參數是否為ip地址或主機名(域名)------使用正則
        is_ip = re.match("[0-9]+(?:\.[0-9]+){3}", host)

        # 若為ip
        if is_ip:
            ip_address = host
            domain = False
        else:
            ip_address = socket.gethostbyname(host)
            domain = True

        # 查尋同一ip是否存在不同虛擬機
        bing_query_string ="'ip:%s'" % ip_address
        self.bing_query(bing_query_string)

        # 若為域名則執行二次搜索，搜索子域名
        if domain:
            bing_query_string = "'domain:%s'" % host
            self.bing_query(bing_query_string)



    def bing_query(self, bing_query_string):
        print "Performing Bing search: %s" % bing_query_string
        # 編碼我們的查詢(如　urllib.quote('ab c')－－＞　'ab%20c')
        quoted_query = urllib.quote(bing_query_string)

        http_request  = "GET https://api.datamarket.azure.com/Bing/Search/Web?$format=json&$top=20&Query=%s HTTP/1.1\r\n" % quoted_query
        http_request += "Host: api.datamarket.azure.com\r\n"
        http_request += "Connection: close\r\n"
        # 對API密鑰使用base64編碼
        http_request += "Authorization: Basic %s\r\n" % base64.b64encode(":%s" % bing_api_key)
        http_request += "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36\r\n\r\n"

        json_body = self._callbacks.makeHttpRequest("api.datamarket.azure.com", 443, True, http_request).tostring()

        # 去掉HTTP響應頭，只取正文
        json_body = json_body.split("\r\n\r\n", 1)[1]

        #print json_body

        try:
            # 傳遞給json解析器
            r = json.loads(json_body)

            # 輸出查詢到的網站的相關信息
            if len(r["d"]["results"]):
                for site in r["d"]["results"]:

                    print "*" * 100
                    print site['Title']
                    print site['Url']
                    print site['Description']
                    print "*" * 100

                    j_url = URL(site['Url'])

            # 如果網站不在brup的目標列表中，就添加進去
            if not self._callbacks.isInScope(j_url):
                print "Adding to Burp scope"
                self._callbacks.includeInScope(j_url)

        except:
            print "No results from Bing"
            pass

        return