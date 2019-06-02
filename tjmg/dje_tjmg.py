from tjmg.comarcas import com_dict
from datetime import datetime
from selenium import webdriver
import re

date = datetime.now()
dia = date.day
mes = date.month


def get_procs(dia, mes, nome_comarca):
    browser = webdriver.Firefox()
    url_dje = f'http://www8.tjmg.jus.br/juridico/diario/index.jsp?dia={dia}{mes:02d}&completa=interior%7C{com_dict[(nome_comarca).title]}'
    browser.get(url=url_dje)
    pub = str(browser.find_element_by_xpath('/html/body/div[8]').text)
    rx_pat = r"\d{7}\.\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}"
    proc_id = re.findall(pattern=rx_pat, string=pub)
    print(proc_id)
    return proc_id