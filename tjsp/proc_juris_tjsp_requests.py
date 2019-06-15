import requests
import csv
from pathlib import Path
from bs4 import BeautifulSoup
from sys import exit
from time import sleep


def plan_csv():
    pasta_logs = Path('logs')
    arq_log = pasta_logs / f'resultado-raspagem-cod{ASSUNTO}.csv'
    if not pasta_logs.exists():
        pasta_logs.mkdir()
    arq_log.write_text(data='nums_procs|assunto_proc|class_proc|relator|comarca|julgamento|publicacao|registro|ementa|referencia\n', encoding='UTF8')
    return arq_log


def parse_classe_assunto(item):
    texto = item.get_text()
    texto = texto.strip()
    texto = texto.split(' ')
    del texto[0]
    texto = ' '.join(texto)
    texto = texto.split('/')
    classe_proc, assunto_proc = texto[0].strip(), texto[1].strip()
    return classe_proc, assunto_proc

def parse_nums(item):
    texto = item.get_text()
    return texto


def parse_relator(item):
    texto = item.get_text().strip().split(' ')
    del texto[0]
    texto = ' '.join(texto)
    return texto


def parse_comarca(item):
    texto = item.get_text().strip().split(' ')
    del texto[0]
    texto = ' '.join(texto).strip()
    return texto


def parse_datas(item):
    texto = item.get_text().strip().split(' ')
    del texto[0: 2]
    texto = texto[-1].split(':')[-1].strip()
    return texto


def parse_ementa(item):
    texto = item.get_text().strip()
    texto = texto.split('\xa0')
    ementa = texto[0].strip()
    referencia = ' '.join(texto[1:])
    return ementa, referencia


def navegador():
    session = requests.Session()
    tj_req = session.post(
                url='https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do',
                data=payload,
                headers={
                    'X-Requested-With': 'XMLHttpRequest'
                },
                verify=False)
    tj_html = BeautifulSoup(tj_req.text, 'html.parser')
    qtde_acordaos = tj_html.find(id='paginacaoSuperior-A').find('td').text.strip().split()[-1]
    qtde_paginas = int(qtde_acordaos) // 20
    print(f'Foram encontrados {qtde_acordaos} acórdãos, divididos em {qtde_paginas} páginas.')
    return session, tj_html, qtde_paginas


def raspador(session, pagina_esaj):
    pagina = [
        ("tipoDeDecisao", "A"),
        ("pagina", pagina_esaj,),
        ("conversationId", "")
    ]
    session.params = payload
    session.params.update(pagina)
    t = session.get('https://esaj.tjsp.jus.br/cjsg/trocaDePagina.do')
    tjsp_html = BeautifulSoup(t.text, 'html.parser')
    arquivo_html.write(str(tjsp_html))
    for processo in tjsp_html.find_all('tr', class_="fundocinza1"):
        nums_procs = processo.find('a', class_='esajLinkLogin downloadEmenta').get_text().strip()

        clas_assunto = processo.find_all('tr', class_='ementaClass2')[0]
        assunto_proc, class_proc = parse_classe_assunto(clas_assunto)

        relator = processo.find_all('tr', class_='ementaClass2')[1]
        relator = parse_relator(relator)

        comarca = processo.find_all('tr', class_='ementaClass2')[2]
        comarca = parse_comarca(comarca)

        julgamento = processo.find_all('tr', class_='ementaClass2')[4]
        julgamento = parse_datas(julgamento)

        publicacao = processo.find_all('tr', class_='ementaClass2')[5]
        publicacao = parse_datas(publicacao)

        registro = processo.find_all('tr', class_='ementaClass2')[6]
        registro = parse_datas(registro)

        ementa = processo.find_all('div', class_='mensagemSemFormatacao')[0]
        ementa, referencia = parse_ementa(ementa)
        print("-----------------------\n"
              "Numero do Processo: {}\n"
              "Assunto: {}\n"
              "Classe: {}\n"
              "Relator: {}\n"
              "Comarca: {}\n"
              "Julgamento: {}\n"
              "Publicação: {}\n"
              "Registro: {}\n"
              "Ementa: {}\n"
              "Referencia: {}\n"
              .format(nums_procs, assunto_proc, class_proc, relator, comarca, julgamento, publicacao, registro, ementa,
                      referencia))

        dados_procs = ["{}|{}|{}|{}|{}|{}|{}|{}|{}|{}"
                           .format(nums_procs, assunto_proc, class_proc, relator, comarca, julgamento, publicacao,
                                   registro, ementa, referencia)]
        return dados_procs



    pagina_esaj += 1
    sleep(5)


ASSUNTO = "10433,10434,10435,10436,10437"
DATA_INICIO = "01/01/2011"
DATA_FIM = "31/12/2011"

payload = {
            "conversationId": "",
            "dados.buscaInteiroTeor": "",
            "dados.pesquisarComSinonimos": ["S", "S"],
            "dados.buscaEmenta": "",
            "dados.nuProcOrigem": "",
            "dados.nuRegistro": "",
            "agenteSelectedEntitiesList": "",
            "contadoragente": "0",
            "contadorMaioragente": "0",
            "codigoCr": "",
            "codigoTr": "",
            "nmAgente": "",
            "juizProlatorSelectedEntitiesList": "",
            "contadorjuizProlator": "0",
            "contadorMaiorjuizProlator": "0",
            "codigoJuizCr": "",
            "codigoJuizTr": "",
            "nmJuiz": "",
            "classesTreeSelection.values": "",
            "classesTreeSelection.text": "",
            "assuntosTreeSelection.values": ASSUNTO,
            "assuntosTreeSelection.text": "5+Registros+selecionados",
            "comarcaSelectedEntitiesList": "",
            "contadorcomarca": "0",
            "contadorMaiorcomarca": "0",
            "cdComarca": "",
            "nmComarca": "",
            "secoesTreeSelection.values": "",
            "secoesTreeSelection.text": "",
            "dados.dtJulgamentoInicio": "",
            "dados.dtJulgamentoFim": "",
            "dados.dtPublicacaoInicio": DATA_INICIO,
            "dados.dtPublicacaoFim": DATA_FIM,
            "dados.dtRegistroInicio": "",
            "dados.dtRegistroFim": "",
            "dados.origensSelecionadas": ["T", "R"],
            "tipoDecisaoSelecionados": ["A", "H", "D"],
            "dados.ordenarPor": "dtPublicacao"
        }

arquivo_html = open(file='teste.html', mode='w')

if __name__ == "__main__":
    arquivo_logs = plan_csv()
    arq_log = Path(arquivo_logs)
    sessao, source, paginas = navegador()

    for pagina in range(1, paginas + 1):
        dados = raspador(session=sessao, pagina_esaj=pagina)
        with open(arq_log, mode='a', encoding='UTF-8', newline='') as arquivo_csv:
            writer = csv.writer(arquivo_csv)
            writer.writerow(dados)
            sleep(5)
