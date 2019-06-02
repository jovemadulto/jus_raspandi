from selenium import webdriver
from tjmg.comarcas import com_dict
from tjmg.dje_tjmg import get_procs
import re

def get_infos_com(cidade, num_proc): #
    comarca = com_dict[cidade.title()]
    ano_proc = num_proc[13:15]
    rest_proc = num_proc[:6]
    proc = ano_proc + rest_proc
    options = webdriver.FirefoxOptions()
    # options.add_argument('-headless')
    browser = webdriver.Firefox(firefox_options=options)
    browser.get(f'http://www4.tjmg.jus.br/juridico/sf/proc_complemento.jsp?comrCodigo={comarca}&numero=1&listaProcessos={proc}')

    def format_text(xpath, purge):
        # purge é a string que deverá ser deletada da lista com afim de retornar somente os dados que nos interessam.
        texto = str(browser.find_element_by_xpath(xpath).text)
        texto = re.sub(pattern=purge, repl=' ', string=texto)
        texto = texto.split()
        texto = (" ".join(texto)).title()
        return texto

    # Atenção especial para o segundo argumento da função def_format. Ainda que ele seja uma string, ele é passado #
    # como um re object, ou seja, é necessário escapar os caracteres especiais como ( ) $ \n, \r, , entre outros, caso
    # exsistam.

    juiz = format_text('/html/body/table[2]/tbody/tr[5]/td', 'Juiz\(iza\):')
    distrib = format_text('/html/body/table[2]/tbody/tr[1]/td[1]', 'Distribuição:')
    valor_causa = format_text('/html/body/table[2]/tbody/tr[1]/td[2]', 'Valor da causa: R\$')

    print(juiz)
    print(distrib)
    print(valor_causa)


# get_infos_com('Patos De Minas', '0088153-31.2016.8.13.0480')
procs = get_procs(18, 10, 'Patos De Minas')
for itens in procs:
    get_infos_com('Patos De Minas', itens)