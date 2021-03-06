# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:20:33 2019

@Author: Zhi-Jiang Yang(Kotori)
@Institution: CBDD Group, Xiangya School of Pharmaceutical Science, CSU, China
@Homepage: http://www.scbdd.com
@Mail: kotori@cbdd.me& kotori@csu.edu.cn
@Blog: https://blog.moyule.me

♥I love Princess Zelda forever♥
"""

print(__doc__)

import requests
from lxml import etree
from collections import namedtuple
import re
import json
from requests import exceptions
import xml.etree.ElementTree as ET



def GetInfoFromDrugBank(drugb_id,item_list=['Name','SMILES','ATC Codes']):
    """
    This function is aim to get molecular infomation through DrugBankID
    """
    def GetXpath(item):
        return '//*[@class="col-md-2 col-sm-4"][text()="{}"]/following-sibling::dd[1]'.format(item)
    
    def GetInfo(xpath_list):
        idx = 0
        while idx != len(xpath_list):
            XPATH = xpath_list[idx]
            if len(XPATH) != 64:
                check = html.xpath(XPATH)
                if check:
                    yield check[0].xpath('string(.)')
                else:
                    yield None
            else:
                check = html.xpath(XPATH)
                if check:
                    yield [item.replace('/atc/','') for item in check]
                else:
                    yield None
            idx += 1


    try:   
        request_url = "https://www.drugbank.ca/drugs/{}".format(drugb_id)
        s = requests.Session()
        html = s.get(request_url,timeout=30).text
        html = etree.HTML(html)
        
        atc_xpath = '//*[@class="col-md-10 col-sm-8"]/a[contains(@href, "atc")]/@href'
        xpath_list = [[GetXpath(item),atc_xpath][item=='ATC Codes'] for item in item_list]
        info_list = [item for item in GetInfo(xpath_list)]
        info_list.insert(0,drugb_id)
         
        item_list = [x.replace(' ','_') for x in item_list]
        item_list.insert(0,'DrugBankID')
        res = namedtuple('DrugBank',item_list)      
        return res(*info_list)    
    except exceptions.Timeout:
        return 'Timeout'  
    except:
        return None


def GetInfoFromUniprot(UniProt_id,):
    """
    UniProt_id = 'P23975'
    """
    request_url = 'https://www.uniprot.org/uniprot/{}.xml'.format(UniProt_id)
    s = requests.Session()
    try:
        r = s.get(request_url,timeout=30)
        if r.status_code == 200:
            tree = ET.fromstring(r.text)
            entry = tree[0]
            dbReference = entry.findall('{http://uniprot.org/uniprot}dbReference[@type="ChEMBL"]')
            res = [i.attrib['id'] for i in dbReference]
        else:
            res = [None]       
    except:
        res = [None]
    
    return '|'.join(res)


def GetInfoFromZinc():
    """
    """
    pass



def GetTargetFromChembel(Chembl_id,Xref_src_db=['UniProt']):
    """
    CHEMBL25
    """
    request_url = 'https://www.ebi.ac.uk/chembl/api/data/target/{}.json'.format(Chembl_id)
    s = requests.Session()
    response = s.get(request_url,timeout=60).text
    data = json.loads(response)
    info = [Chembl_id,data['organism'],data['pref_name']]
    xref = [x['xref_id']\
            for x in data['target_components'][0]['target_component_xrefs']\
            if x['xref_src_db'] in Xref_src_db]
    info.append(xref)
    
    items = ['Chembl_id','Organism','Pref_name']
    items.extend(Xref_src_db)
    res = namedtuple('ChEMBLTarget',items)   
    return res(*info)


def GetInfoFromPubChem(cid,item_list=['InChI','InChI Key','Canonical SMILES']):
    """
    *Now only support the info exist in 3rd level titls
    """
    def GetRegx(item):
        return r'"TOCHeading": "{}".*?"String": "(.*?)"'.format(item)
    
    def GetInfo(regx_list):
        idx = 0
        while idx != len(regx_list):
            regx = regx_list[idx]
            check = re.findall(regx,html,re.S)
            if check:
                yield check[0]
            else:
                yield None            
            idx += 1
    
    try:
        try:
            cid = str(int(cid))
        except:
            pass
        cid = cid.replace('cid','')
        request_url = 'https://pubchem.ncbi.nlm.nih.gov/rest/pug_view/data/compound/{}/JSON/'.format(cid)
        s = requests.Session()
        html = s.get(request_url,timeout=30).text
        regx_list = [GetRegx(item) for item in item_list]
        info_list = [info for info in GetInfo(regx_list)]
        info_list.insert(0,cid)
        item_list = [x.replace(' ','_') for x in item_list]
        item_list.insert(0,'CID')    
    except exceptions.Timeout:
        return 'Timeout'
    except:
        return None

    res = namedtuple('PubChem',item_list)
    return res(*info_list)
        
    

def GetInfoFromKegg():
    """
    """
    pass



def GetInfoFromPDBbind(PDBcode,item_list=['PDB ID','Protein Name','Ligand Name','Resolution','Canonical SMILES','InChI String']):
    """
    10gs
    """
    def GetXpath(item):
        return '//*[@class="register"][text()="{}"]/following-sibling::td'.format(item)
    
    def GetInfo(xpath_list):
        idx = 0
        while idx != len(xpath_list):
            XPATH = xpath_list[idx]           
            check = html.xpath(XPATH)
            if check:
                yield check[0].xpath('string(.)').strip('\n\r')
            else:
                yield None           
            idx += 1
    try:
        request_url = 'http://www.pdbbind-cn.org/quickpdb.asp'
        s = requests.Session()
        form_data = {'quickpdb': PDBcode,}
        response = s.post(request_url,data=form_data,timeout=30)
        html = response.text
        html = etree.HTML(html)
        xpath_list = [GetXpath(item) for item in item_list]
        info_list = [info for info in GetInfo(xpath_list)]
        info_list.insert(0,PDBcode)
        
        item_list.insert(0,'PDBcode')
        item_list = [x.replace(' ','_') for x in item_list]
        res = namedtuple('PDBbind',item_list)
        
        return res(*info_list)
    except:
        return None
    
##        
if '__main__' == __name__:
    drugbank_id = ['DB00010',
                   'DB00569',
                   'DB01226']
#    
    for drugb_id in drugbank_id:
        res = GetInfoFromDrugBank(drugb_id,item_list=['Name','SMILES','ATC Codes','CAS number','InChI Key'])
        print(res,end='\n\n')
##    
##    
##    cid = 'cid2244'
##    res = GetInfoFromPubChem(cid)
##    print(res,end='\n\n')
##        
##    pdbcode = '10gs'
##    res = GetInfoFromPDBbind(pdbcode)
##    print(res,end='\n\n')
##        
##
#    Chembl_id = 'CHEMBL3969'
#    res = GetTargetFromChembel(Chembl_id)
#    print(res)
#    