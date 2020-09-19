import requests
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
from sys import exit
from time import sleep
import parseadores


def navegador():
    session = requests.Session()
    tj_req = session.post(
                url='https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do',
                data=payload,
                headers={
                    'X-Requested-With': 'XMLHttpRequest'
                },
                verify=True)
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
        assunto_proc, class_proc = parseadores.classe_assunto(clas_assunto)

        relator = processo.find_all('tr', class_='ementaClass2')[1]
        relator = parseadores.relator(relator)

        comarca = processo.find_all('tr', class_='ementaClass2')[2]
        comarca = parseadores.comarca(comarca)

        julgamento = processo.find_all('tr', class_='ementaClass2')[4]
        julgamento = parseadores.datas(julgamento)

        publicacao = processo.find_all('tr', class_='ementaClass2')[5]
        publicacao = parseadores.datas(publicacao)

        ementa = processo.find_all('div', class_='mensagemSemFormatacao')[0]
        ementa, referencia = parseadores.ementa(ementa)
        print(f"""-----------------------
Numero do Processo: {nums_procs}
Assunto: {assunto_proc}
Classe: {class_proc}
Relator: {relator}
Comarca: {comarca}
Julgamento: {julgamento}
Publicação: {publicacao}
Ementa: {ementa}
Referencia: {referencia}""")

        dados_procs = {
            "num_procs": nums_procs,
            "assunto_proc": assunto_proc,
            "class_proc": class_proc,
            "relator": relator,
            "comarca": comarca,
            "julgamento": julgamento,
            "publicacao": publicacao,
            "ementa": ementa,
            "referencia": referencia
            }
        return dados_procs

    pagina_esaj += 1
    sleep(2)


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
            "dados.origensSelecionadas": ["T"],
            "tipoDecisaoSelecionados": ["A"],
            "dados.ordenarPor": "dtPublicacao"
        }

arquivo_html = open(file='teste.html', mode='w')

if __name__ == "__main__":
    sessao, source, paginas = navegador()

    pasta_logs = Path('logs')
    if not pasta_logs.exists():
        pasta_logs.mkdir()

    df_processos = pd.DataFrame(columns=["num_procs",
                                        "assunto_proc",
                                        "class_proc",
                                        "relator",
                                        "comarca",
                                        "julgamento",
                                        "publicacao",
                                        "ementa",
                                        "referencia"])

    for pagina in range(1, paginas + 1):
        dados = raspador(session=sessao, pagina_esaj=pagina)
        linha = 1
        try:
            for metadados in dados.keys():
                df_processos.at[linha, metadados] = dados[metadados]
        except AttributeError as e:
            pass
        linha += 1

        df_processos.to_csv(f"{pasta_logs}/df_{ASSUNTO}.csv", mode="a")
