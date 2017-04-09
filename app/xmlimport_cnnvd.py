# -*- coding: utf-8 -*-
"""
Created on Wed Apr  5 15:44:55 2017

@author: leo
"""

import xml.etree.ElementTree as ET
from .models import db, Vulninfo,Vulntype,Vulnref,Cncpe,Vulnseverity,Vulnsoftwarelist
from datetime import datetime as dt
"""

"""
class CnnvdXmlImport():
    tree = ET.parse('test.xml')
    root = tree.getroot()
    vuln_software_list = root.getiterator("vuln-software-list")
    ns={"cnnvd_vuln":"http://www.cnnvd.org.cn/vuln/1.0","cnnvd_xsi": \
            "http://www.w3.org/2001/XMLSchema-iself.nstance"}
    
    
    def parseEntry(self,entryObj):
        vulninfo = Vulninfo()
        vulninfo.name = entryObj.find('cnnvd_vuln:name',self.ns)
        print("name:"+vulninfo.name.text)
        vulninfo.vuln_id = entryObj.find('cnnvd_vuln:vuln-id',self.ns)
        print("vuln_id:"+vulninfo.vuln_id.text)    
        vulninfo.published =dt.strptime(entryObj.find('cnnvd_vuln:published',self.ns),"%Y-%m-%d")
        print("published:"+vulninfo.published.text)
        vulninfo.modified = dt.strptime(entryObj.find('cnnvd_vuln:modified',self.ns),"%Y-%m-%d")
        print("modified:"+vulninfo.modified.text)
        
        vulninfo.vulninfo.source = entryObj.find('cnnvd_vuln:source',self.ns)    
        if vulninfo.source.text is None:     
            print("source:")
        else:
            print("source:" + vulninfo.source.text)
            
        vulninfo.severity = entryObj.find('cnnvd_vuln:severity',self.ns)
        print("severity:"+vulninfo.severity.text)
        vulninfo.vuln_type = entryObj.find('cnnvd_vuln:vuln-type',self.ns)
        print("vuln-type:"+vulninfo.vuln_type.text)
        vulninfo.thrtype = entryObj.find('cnnvd_vuln:thrtype',self.ns)
        print("thrtype:"+vulninfo.thrtype.text)
        
 
        vulninfo.vuln_software_list=entryObj.find('cnnvd_vuln:vuln-software-list',self.ns)
        print("vuln_software_list:")
        for i in vulninfo.vuln_software_list:
            print("  " +i.tag+": "+i.text)
        
        vulninfo.vuln_descript = entryObj.find('cnnvd_vuln:vuln-descript',self.ns)
        print("vuln_descript:"+'\n    '+vulninfo.vuln_descript.text)
    
        
        print("other-id:")       
        other_id = entryObj.find('cnnvd_vuln:other-id',self.ns)        
        (vulninfo.cve_id,vulninfo.bugtraq_id)=self.parseOid(other_id)
#do right?        

        """
        vulnrefs表单 ××××××××××××××××××待处理
        """        
        print("refs:")
        for aref in entryObj.find('cnnvd_vuln:refs',self.ns):
            self.parseRef(aref)#TODOvulnrefs表单 ××××××××××××××××××待处理
        
        vulninfo.vuln_solution = entryObj.find('cnnvd_vuln:vuln-solution',self.ns)
        print("vuln-solution:"+vulninfo.vuln_solution.text)
        
        return vulninfo
    

    def parseRef(self,refObj):    
        ref_source=refObj.find('cnnvd_vuln:ref-source',self.ns)
        print("  ref-source:"+ref_source.text)
        ref_url=refObj.find('cnnvd_vuln:ref-url',self.ns)
        print("  ref-url:"+ref_url.text)
        return(ref_source,ref_url)
        
       
    """
    
    """    
    def parseOid(self,oidObj):    
        cve_id=oidObj.find('cnnvd_vuln:cve-id',self.ns)
        print("cve-id:"+cve_id.text)
        bugtraq_id=oidObj.find('cnnvd_vuln:bugtraq-id',self.ns)
        print("bugtraq-id:"+bugtraq_id.text)
        return (cve_id,bugtraq_id)
        
     
    
    def xmlimport(self):   
        vulinfoes = set()
        for entry in self.root.findall('cnnvd_vuln:entry',self.ns):
            print("______________"+entry.tag+"______________") 
            
            vulinfo = self.parseEntry(entry)
            vulinfoes.add(vulinfo)
            
        db.session.addAll(vulinfoes)
        db.session.commit()