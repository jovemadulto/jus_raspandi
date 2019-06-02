import requests
from bs4 import BeautifulSoup as bs
import re
import csv
from pathlib import Path
import pandas as pd
from sys import exit


COMARCA = "702"
DAY = "07"
MONTH = "08"


def prepara_arquivos():
    tjmg_dump_folder = Path('processos')
    arq_proc_dje = tjmg_dump_folder / 'processos_dje_tjmg.csv'
    arq_proc_infos = tjmg_dump_folder / 'processos_infos_tjmg.csv'

    if not tjmg_dump_folder.exists():
        tjmg_dump_folder.mkdir()
        arq_proc_dje.write_text(data="numero_processo;comarca\n")
        arq_proc_infos.write_text(data="numero_processo;comarca\n")


def coleta_processos_dje(dia, mes, comarca):
    response_dje = requests.get(f"http://www8.tjmg.jus.br/juridico/diario/index.jsp?dia={DAY}{MONTH}&completa=interior%7C0{COMARCA}")
    dje_soup = bs(response_dje.text, 'html.parser')
    lista_procs = re.findall(pattern=r'\d{7}\.\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', string=str(dje_soup))
    return lista_procs


def salva_dados_dje(linha_de_dados):
    tjmg_dump_folder = Path('processos')
    arq_proc_dje = tjmg_dump_folder / 'processos_dje_tjmg.csv'

    with open(file=arq_proc_dje, mode="a", newline="") as bd:
        escreve_bd = csv.writer(bd, delimiter=';')
        escreve_bd.writerow([linha_de_dados])


def get_info_page(numero_processo):
    tjmg_proc_folder = Path('processos')
    arq_proc_dje = tjmg_proc_folder / 'processos_dje_tjmg.csv'
    df = pd.read_csv(filepath_or_buffer=arq_proc_dje,
                     sep=';'
                     )

    for index, row in df.iterrows():
        numero_proc = row["numero_processo"]
        comarca = COMARCA
        ano_proc = numero_proc[13:15]
        id_unico = numero_proc[:6]
        numero_id = str(ano_proc) + str(id_unico)
        endereco = f"https://www4.tjmg.jus.br/juridico/sf/proc_complemento.jsp?comrCodigo={comarca}&numero=1&listaProcessos={numero_id}"
        print(endereco)
        response_dados_completos = requests.get(endereco)
        info_soup = bs(response_dados_completos.text, 'html.parser')
        return info_soup


def vara_parser(page_source):
    tjmg_proc_folder = Path('processos')
    arq_proc_infos = tjmg_proc_folder / 'processos_infos_tjmg.csv'

    numero_proc = page_source.body.find_all("table")[1].td.text.split(" ")[-1].strip()

    vara = page_source.body.find_all("table")[1].find_all("td")[1].text.strip().title()

    data_distribuicao = page_source.body.find_all("table")[2].find_all("td")[0].text.split(" ")[1]

    valor_causa = page_source.body.find_all("table")[2].find_all("td")[1].text.strip().split()[-1]

    classe = page_source.body.find_all("table")[2].find_all("td")[2].text.strip().split()[1:]
    classe = ' '.join(classe)

    classe_origin = page_source.body.find_all("table")[2].find_all("td")[3].text.strip().split()[2:]
    classe_origin = ' '.join(classe_origin).title()

    assunto = page_source.body.find_all("table")[2].find_all("td")[4].text.split(">")[-1].strip()

    comarca = page_source.body.find_all("table")[2].find_all("td")[5].text.split()[-1].strip().title()

    competencia = page_source.body.find_all("table")[2].find_all("td")[6].text.split()[-1].strip().title()

    dados = [numero_proc, vara, data_distribuicao, valor_causa, classe, classe_origin, assunto, comarca, competencia]

    with open(file=arq_proc_infos, mode="a", encoding="UTF8") as proc_infos:
        escreve_infos = csv.writer(proc_infos, delimiter=';')
        escreve_infos.writerow(dados)


if __name__ == "__main__":
    prepara_arquivos()
    lista_processos = coleta_processos_dje(dia=DAY, mes=MONTH, comarca=COMARCA)
    for item in lista_processos:
        salva_dados_dje(linha_de_dados=item)
    with open("processos/processos_dje_tjmg.csv") as proc_dje:
        for linhas in proc_dje.readlines():
            html = get_info_page(numero_processo=linhas.strip())
    vara_parser(page_source=html)