from selenium import webdriver
import re


def raspa_datas(mes, ano, comarca):
    """
    :param mes: Mês do ano no formato <MM>. O marco inicial é 05/2008.
    :param ano: Ano no formato <YYYY>. O marco inicial é 05/2008.
    :param comarca: Código da comarca no formato <####>. Conferir o arquivo comarcas.py para referências.
    :return: Código fonte da página.
    """

    driver.get(f"https://dje.tjmg.jus.br/diarioJudiciarioMesAno.do?mes={mes}&ano={ano}&tipoDiario=comarca%7C{comarca}&lista=Pesquisar+Di%E1rios")
    html = driver.page_source
    driver.close()
    return html


def salva_datas(html_source):
    regex = re.compile(pattern=r"\d{2}/\d{2}/\d{4}")
    datas = re.findall(string=html_source, pattern=regex)
    for item in datas:
        registro = "datas.csv"
        with open(registro, "a") as lista_datas:
            lista_datas.writelines(item + "\n")


if __name__ == "__main__":
    driver = webdriver.Firefox()
    for ano in range(2008, 2019 + 1):
        for mes in range(1, 12 + 1):
            driver = raspa_datas(mes=str(mes), ano=str(ano), comarca="0702")
            salva_datas(html_source=driver)