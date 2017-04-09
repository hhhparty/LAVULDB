# -*- coding: utf-8 -*-
"""
Created on Wed Feb  1 09:16:46 2017

@author: leo
"""

from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.error import HTTPError,URLError
from .models import db
import re
from datetime import datetime as dt
import time
import requests
from .models import Vulninfo,Vulntype,Vulnref,Cncpe,Vulnseverity,Vulnsoftwarelist

class Cnnvdvulninfo:
    '''
    本程序用于抽取http://www.cnnvd.org.cn/vulnerability中的漏洞信息
    预先分析：
    1.所有漏洞信息在<table width="100%" class="qtld_details sortable" ...>中;
    2.每个漏洞信息均有详细说明，链接为/vulnerability/show/cv_cnnvdid/CNNVD-201701-794,
    即每个链接的前缀均为/vulnerability/show/cv_cnnvdid/CNNVD;
    3.<a href="/vulnerability/show/cv_cnnvdid/CNNVD-201701-794" title="CNNVD-201701-794">CNNVD-201701-794</a>
    标签a中含有href属性和title属性
    '''
    vunlinfo = Vulninfo()
    
    """
    方法： getVulnInfoLink
    功能：获取漏洞信息链接
    思路：1.使用request方法获得初始访问页面;2.创建BeautifulSoup对象以便后续处理;
         3.获取漏洞信息页的总页数，以备后续循环访问;4.返回BeautifulSoup对象中的每页的漏洞信息列表
    """
    def getVulnInfoLink(self,website='http://www.cnnvd.org.cn/vulnerability/', vulinfourl='index/p/1',pagenumber=1):#xiugai
        total_links = set()    #save vuln links  that is found    
        session = requests.Session()
        headers = {"Connection":"keep-alive",
                   "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36",
                   "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                   "Cache-Control":"max-age=0",
                   "Upgrade-Insecure-Requests":"1",
                   "DNT":"1",
                   "Accept-Encoding":"gzip, deflate, sdch",
                   "Accept-Language":"zh-CN,zh;q=0.8"}        
        try: 
            if pagenumber == 1:
                url = website
                req = session.get(url,headers=headers)
                bsObj = BeautifulSoup(req.text,"html.parser")
                links = bsObj.findAll("a",href=re.compile("^(/vulnerability/show/cv_cnnvdid/CNNVD)"))
                for j in links:                    
                    total_links.add(j)
                
            elif pagenumber > 1:
                for i in range(1,pagenumber +1):
                    url = website + 'index/p/'+str(i)+'/'
                    print(url)                
                    req = session.get(url,headers=headers)
                    bsObj = BeautifulSoup(req.text,"html.parser")
                    links = bsObj.findAll("a",href=re.compile("^(/vulnerability/show/cv_cnnvdid/CNNVD)"))
                                       
                    for j in links:                    
                        total_links.add(j)                    
                    time.sleep(1)    
        except requests.exceptions.ConnectionError as e:
            print("Network Connection Error！ Please check it！")
            return None#
        except AttributeError as e:
            print("BeautifulSoup handle Error！")
            return None   
            
        return total_links
    
    
    def outputFile(self,text,destDir="./nowscrapy.html"):
        file_object = open(destDir, 'w') 
        file_object.write(text)
        file_object.close()
     
    """
    方法：getPageNumber
    功能：获取页数
    思路：1.使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
    """
    def getPageNumber(self,url="http://www.cnnvd.org.cn/vulnerability/"):
        #打开首页获取总页数
        session = requests.Session()
        headers = {"Connection":"keep-alive",
                   "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36",
                   "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                   "Cache-Control":"max-age=0",
                   "Upgrade-Insecure-Requests":"1",
                   "DNT":"1",
                   "Accept-Encoding":"gzip, deflate, sdch",
                   "Accept-Language":"zh-CN,zh;q=0.8"}
        
        try:
            req = session.get(url,headers=headers)
            bsObj = BeautifulSoup(req.text,"html.parser")           
            pagetext = bsObj.find("div",{"class":"dispage"}).get_text() #获取漏洞信息分页总数 find div
        except requests.exceptions.ConnectionError as e:
            print("Network Connection Error！ ")
            return None
        except AttributeError as e:
            print("BeautifulSoup handle Error！")
            return None
        
       
        # 将正则表达式编译成Pattern对象
        pattern = re.compile("(1/)([0-9]\d*)")
        # 使用Pattern匹配文本，获得匹配结果，无法匹配时将返回None
        #print(pagetext)
        match = pattern.search(pagetext)
        #print((match.group()[2:]).strip())
        return int((match.group()[2:]).strip())
    """     
    方法：getVulnInfo
    功能： 获取漏洞信息
    思路：1.使用request方法访问页面表头;2.创建BeautifulSoup对象以便后续处理;
         3.获取漏洞信息页的总页数，以备后续循环访问;4.返回BeautifulSoup对象中的每页的漏洞信息列表    
    """    
    def getVulnInfo(self,link):
        
        session = requests.Session()
        headers = {"Connection":"keep-alive",
                   "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36",
                   "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                   "Cache-Control":"max-age=0",
                   "Upgrade-Insecure-Requests":"1",
                   "DNT":"1",
                   "Accept-Encoding":"gzip, deflate, sdch",
                   "Accept-Language":"zh-CN,zh;q=0.8"}
        try:
            req = session.get(link,headers=headers)
        except requests.exceptions.RequestException as e:
            return None       
        try:
            bsObj = BeautifulSoup(req.text,"html.parser")
        except AttributeError as e:
            return None
        new = bsObj.findAll("div",{"class":"cont_details"})
        print("the length of new list:%d" % len(new))
        #f = open("./1.html","w+")
        #print(i.decode('utf-8'),file=f)
        #f.close()
        for i in new:       
            if i.find("table",{"class":"details"}) is not None:
                #print(i)
                vulninfo = self.getVulnBaseInfo(i)
            #TODO:
            #仅完成了基本信息的录入，还有4个块信息未处理
        
        return vulninfo
                
    """
    方法：getVulnBaseInfo
    功能：获取漏self洞信息
    思路：使用Pattern匹getPageNumber配文本，获得匹配结果，无法匹配时将返回None，获得漏洞的基本信息
    """      
    def getVulnBaseInfo(self,bsObj):
        vulninfo = Vulninfo()
        if bsObj.find("table",{"class":"details"}) is None:
            return None
        #vulninfo = Vulninfo()
        base = bsObj.find("table",{"class":"details"})
        for i in base.findAll("tr"):
            print("-------------------getVulnBaseInfo-------------------------")
            
            pattern = re.compile("漏洞名称")              
            if pattern.search(str(i)):               
                vulninfo.name = i.find("td",{"class":"displayitem"}).get_text()
                print(vulninfo.name)
            pattern = re.compile("CNNVD编号")               
            if pattern.search(str(i)):
                vulninfo.vuln_id = i.find("td",{"class":"displayitem"}).get_text()
                print(vulninfo.vuln_id)
            pattern = re.compile("发布时间")               
            if pattern.search(str(i)):
                pubstr = i.find("td",{"class":"displayitem"}).get_text()
                vulninfo.published = dt.strptime(pubstr,"%Y-%m-%d")                
                print(vulninfo.published)
            pattern = re.compile("更新时间")               
            if pattern.search(str(i)):
                modstr = i.find("td",{"class":"displayitem"}).get_text()
                vulninfo.modified = dt.strptime(modstr,"%Y-%m-%d")                
                print(vulninfo.modified)
            pattern = re.compile("危害等级")               
            if pattern.search(str(i)):
                td = i.find("td",{"class":"displayitem"})
                #如果有文字，直接匹配录入相应威胁等级的id值
                if td.get_text().strip():
                    if td.get_text().find("超危") > -1 :
                        vulninfo.severity = Vulnseverity.query.filter_by(description="超危").first().id
                    if td.get_text().find("高危") > -1 :
                        vulninfo.severity = Vulnseverity.query.filter_by(description="超危").first().id
                    if td.get_text().find("中危") > -1 :
                        vulninfo.severity = Vulnseverity.query.filter_by(description="中危").first().id
                    if td.get_text().find("低危") > -1 :
                        vulninfo.severity = Vulnseverity.query.filter_by(description="低危").first().id
                    if td.get_text().find("未知") > -1 :
                        vulninfo.severity = Vulnseverity.query.filter_by(description="未知").first().id
                 
                else:#如果没有字 
                     src = td.find("img").attrs["src"]
                     if src.lower().find("001.jpg") > -1:#低危
                         vulninfo.severity = Vulnseverity.query.filter_by(description="低危").first().id
                     if src.lower().find("002.jpg") > -1:#中危
                         vulninfo.severity = Vulnseverity.query.filter_by(description="中危").first().id
                     if src.lower().find("003.jpg") > -1:#高危
                         vulninfo.severity = Vulnseverity.query.filter_by(description="高危").first().id
                     if src.lower().find("002.jpg") > -1:#超危
                         vulninfo.severity = Vulnseverity.query.filter_by(description="超危").first().id
                     if src.lower().find("002.jpg") > -1:#未知
                         vulninfo.severity = Vulnseverity.query.filter_by(description="未知").first().id
                 
                
                
                
                print(vulninfo.severity)
            pattern = re.compile("漏洞类型")               
            if pattern.search(str(i)):
                vulninfo.vuln_type = i.find("td",{"class":"displayitem"}).get_text()
                print(vulninfo.vuln_type)
            pattern = re.compile("威胁类型")               
            if pattern.search(str(i)):
                vulninfo.vuln_type_alias = i.find("td",{"class":"displayitem"}).get_text()
                print(vulninfo.vuln_type_alias)
            #pattern = re.compile("CVE编号")               
            #if pattern.search(str(i)):
                #vulninfo.cve_id = i.find("td",{"class":"displayitem"}).get_text()
                #print(vulninfo.cve_id)
                #p = re.compile("((CVE|cve)-([0-9]*)-([0-9]*))") 
                #match = p.search(str(i))
                #if match:
                    #print(match.group())
                
            #TODO:
            #    MORE INFO 
        return vulninfo     
           
            
    def getCnnvdAbsoluteURL(self,baseUrl,source):
        if source.startswith("http://www."):
            url = "http://"+source[11:]
        elif source.startswith("http://"):
            url = source
        elif source.startswith("www."):
            url = "http://"+source[4:]
        elif source.startswith("//"):
            url = "http://"+source[2:]
        elif source.startswith("/"):
            url = baseUrl + source
        else:
            url = baseUrl + '/' + source
            #raise URLError('Unexpected url:'+source)
        
        if baseUrl not in url:
            return None
        return url
    
        
    def crawl(self):
        baseUrl = 'http://www.cnnvd.org.cn'
        pagenumber = self.getPageNumber()
        #vulInfolink = self.getVulnInfoLink(pagenumber=pagenumber)#目前仅仅获取了首页的漏洞信息列表
        totallinks = self.getVulnInfoLink(pagenumber=1)
        print("dangqian link number :------------%d----------" % len(totallinks))
        #检查异常并排除
        if totallinks is None: 
            print("Cannot crawl any vulnerability information!")
            return None
        vulninfoes = []   
        count = 1
        for link in totallinks:
            href = self.getCnnvdAbsoluteURL(baseUrl,link.attrs['href'])
            #getVulzadddata
            print(href)
            time.sleep(1)
            vulninfo = self.getVulnInfo(href)
            if vulninfo.vuln_id is not None:
                #TODO：要避免和数据库中数据重复
                #db.query.find
                if Vulninfo.query.filter_by(vuln_id = vulninfo.vuln_id).first() is None:
                    vulninfoes.append(vulninfo)
                    count += 1   
            if count > 5:
                break
        db.session.add_all(vulninfoes)            
        db.session.commit() 
