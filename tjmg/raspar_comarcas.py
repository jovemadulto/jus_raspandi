from selenium import webdriver
from time import sleep

com_file = 'comarcas.py'

browser = webdriver.Chrome()
num = 25

with open(com_file, 'a', encoding='UTF8') as file:

    while num < 730:
        url = f'http://www8.tjmg.jus.br/juridico/diario/index.jsp?dia=1810&completa=interior%7C{num:04d}'
        browser.get(url)
        if 'não está disponível' not in browser.page_source:
            comarca = str(browser.find_element_by_xpath('/html/body/div[8]/p[1]').text)
            comarca = comarca.split()
            comarca.remove('COMARCA')
            comarca.remove('DE')
            comarca = comarca[0:]
            comarca = ' '.join(comarca)
            comarca = comarca.title()
            print(f'''\"{comarca}\": \"{num:04d}\",\n''')
            file.writelines(f'''\"{comarca}\": \"{num:04d}\",\n''')
        elif 'Devido ao grande volume de publicações' in browser.page_source:
            pass
        else:
            pass
        num += 1
        sleep(2)
