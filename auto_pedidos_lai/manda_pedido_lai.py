from selenium import webdriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time

# usando o navegador firefox
firefox = webdriver.Firefox()
wait = WebDriverWait(firefox, 5)

# abrindo o Portal da Transparência
firefox.get('https://esic.cgu.gov.br/sistema/Pedido/RegistroPedido.aspx')

# Colocando Credenciais

# usuário
usuario = firefox.find_element_by_name("ctl00$ConteudoForaDoPortlet$txtUsuario")
usuario.send_keys("")

# senha
senha = firefox.find_element_by_name("ctl00$ConteudoForaDoPortlet$txtSenha")
senha.send_keys("")
time.sleep(2)
# entrar no sistema

senha.send_keys(Keys.RETURN)

rejeita = [
    'Selecione',
           ]

repetir = True


def faz_pedido(nome_orgao):
    firefox.get('https://esic.cgu.gov.br/sistema/Pedido/RegistroPedido.aspx')
    time.sleep(10)
    orgao = firefox.find_elements_by_id("ConteudoGeral_ConteudoFormComAjax_txtOrgaoSuggest")[0]
    wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#ConteudoGeral_ConteudoFormComAjax_txtOrgaoSuggest")))
    selectorgao = Select(orgao)
    time.sleep(10)
    selectorgao.select_by_visible_text(nome_orgao)
    time.sleep(5)
    resumo_da_solicitacao = firefox.find_element_by_name(
        'ctl00$ctl00$ConteudoGeral$ConteudoFormComAjax$txtResumoSolicitacao')
    resumo_da_solicitacao.send_keys('')
    solicitacao = firefox.find_element_by_name('ctl00$ctl00$ConteudoGeral$ConteudoFormComAjax$txtDescricao')
    solicitacao.send_keys('')
    proximo = firefox.find_element_by_name("ctl00$ctl00$ConteudoGeral$ConteudoFormComAjax$btnProximo").click()
    time.sleep(5)
    concluir = firefox.find_element_by_name("ctl00$ctl00$ConteudoGeral$ConteudoFormComAjax$btnConcluir").click()
    time.sleep(5)
    ok = firefox.find_element_by_name("ctl00$ctl00$ConteudoGeral$ConteudoFormComAjax$btnOkMensagem").click()
    time.sleep(5)
    pedido = firefox.find_element_by_css_selector("div.acesso:nth-child(1) > a:nth-child(1) > p:nth-child(1)")
    pedido.click()


# Adquirindo os nomes dos órgaos:
campo_orgaos = firefox.find_element_by_name("ctl00$ctl00$ConteudoGeral$ConteudoFormComAjax$txtOrgaoSuggest")
itens_orgaos = Select(campo_orgaos)
lista_orgaos = []
for itens in itens_orgaos.options:
    lista_orgaos.append(itens.text)

while repetir:
    for orgaos in lista_orgaos:
        if orgaos not in rejeita:
            try:
                print(orgaos)
                faz_pedido(nome_orgao=orgaos)
            except StaleElementReferenceException:
                orgao = firefox.find_elements_by_id("ConteudoGeral_ConteudoFormComAjax_txtOrgaoSuggest")[0]
                wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "#ConteudoGeral_ConteudoFormComAjax_txtOrgaoSuggest")))
                selectorgao = Select(orgao)
                faz_pedido(nome_orgao=orgaos)
