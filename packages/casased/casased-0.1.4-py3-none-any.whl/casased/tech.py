import requests 
from bs4 import BeautifulSoup
from .utils import *

def getCours(name, raise_on_error: bool = False):
    """
         load : Session data, latest transaction, best limit and  data of the last 5 sessions

         Input  | Type              |Description
         ===============================================================================
         name   | String            |Name of the company.You must respect the notation.
                |                   |To get the notation : casased.notation()

         Output |Type               |Description
         =====================================================
                |Dictionary         | 
    """
    code=get_valeur(name) 
    data={"__EVENTTARGET": "SocieteCotee1$LBIndicCle"}
    headers =   {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
    link="https://www.casablanca-bourse.com/bourseweb/Societe-Cote.aspx?codeValeur="+code+"&cat=7"
    try:
        resp = fetch_url(link, method='post', data=data, headers=headers, timeout=10)
        content = resp.content if hasattr(resp, 'content') else resp.text.encode()
        soup = BeautifulSoup(content,'html.parser')
        result= getTables(soup)
        return result
    except Exception as e:
        if raise_on_error:
            raise
        print(f"Warning: could not fetch course data for {name}: {e}")
        return {}

def getKeyIndicators(name,decode='utf-8', raise_on_error: bool = False):
    """
         load : get key indicators

         Input  | Type              |Description
         ===============================================================================
         name   | String            |Name of the company.You must respect the notation.
                |                   |To get the notation : casased.notation()

         Output |Type               |Description
         =====================================================
                |Dictionary         | 
    """
    code=get_valeur(name)
    data={"__EVENTTARGET": "SocieteCotee1$LBFicheTech"}
    headers =   {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
    link="https://www.casablanca-bourse.com/bourseweb/Societe-Cote.aspx?codeValeur="+code+"&cat=7"
    try:
        resp = fetch_url(link, method='post', data=data, headers=headers, timeout=10)
        res = resp.content.decode(decode) if hasattr(resp, 'content') else resp.text
        soup = BeautifulSoup(res,'html.parser')
        result=getTablesFich(soup)
        return result
    except Exception as e:
        if raise_on_error:
            raise
        print(f"Warning: could not fetch key indicators for {name}: {e}")
        return {}

def getDividend(name,decode='utf-8', raise_on_error: bool = False):
    """
         load :get dividends

         Input  | Type              |Description
         ===============================================================================
         name   | String            |Name of the company.You must respect the notation.
                |                   |To get the notation : casased.notation()

         Output |Type               |Description
         =====================================================
                |Dictionary         | 
    """
    code=get_valeur(name)
    data={"__EVENTTARGET": "SocieteCotee1$LBDividende"}
    headers =   {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
    link="https://www.casablanca-bourse.com/bourseweb/Societe-Cote.aspx?codeValeur="+code+"&cat=7"
    try:
        resp = fetch_url(link, method='post', data=data, headers=headers, timeout=10)
        res = resp.content.decode(decode) if hasattr(resp, 'content') else resp.text
        soup = BeautifulSoup(res,'html.parser')
        result=getDivi(soup)
        return result
    except Exception as e:
        if raise_on_error:
            raise
        print(f"Warning: could not fetch dividend info for {name}: {e}")
        return {}

def getIndex():
    """
         load : indexes summary

         Input  | Type              |Description
         ===============================================================================
                |                   |

         Output |Type               |Description
         =====================================================
                |Dictionary         | 
    """
    link="https://www.casablanca-bourse.com/bourseweb/Activite-marche.aspx?Cat=22&IdLink=297"
    try:
        resp = fetch_url(link, method='get', headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(resp.content,features="lxml")
        result = getAllIndex(soup)
        return result
    except Exception as e:
        print(f"Warning: could not fetch or parse index page: {e}")
        return {}

def getPond(raise_on_error: bool = False):
    """
         load : weights(Pondération)

         Input  | Type              |Description
         ===============================================================================
                |                   |

         Output |Type               |Description
         =====================================================
                |Dictionary         | 
    """
    link="https://www.casablanca-bourse.com/bourseweb/indice-ponderation.aspx?Cat=22&IdLink=298"
    try:
        resp = fetch_url(link, method='get', headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
        soup = BeautifulSoup(resp.content,'html.parser')
        return getPondval(soup)
    except Exception as e:
        if raise_on_error:
            raise
        print(f"Warning: could not fetch ponderation page: {e}")
        return {}

def getIndexRecap(raise_on_error: bool = False):
    """
         load : session recap

         Input  | Type              |Description
         ===============================================================================
                |                   |

         Output |Type               |Description
         =====================================================
                |Dictionary         | 
    """
    data={"TopControl1$ScriptManager1": "FrontTabContainer1$ctl00$UpdatePanel1|FrontTabContainer1$ctl00$ImageButton1"}
    link="https://www.casablanca-bourse.com/bourseweb/index.aspx"
    headers =   {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
    try:
        resp = fetch_url(link, method='post', data=data, headers=headers, timeout=10)
        res = resp.content.decode('utf8') if hasattr(resp, 'content') else resp.text
        soup = BeautifulSoup(res,'html.parser')
        return getIndiceRecapScrap(soup)
    except Exception as e:
        if raise_on_error:
            raise
        print(f"Warning: could not fetch index recap: {e}")
        return {}