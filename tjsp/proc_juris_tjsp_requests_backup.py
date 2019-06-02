import requests
import csv
from bs4 import BeautifulSoup
from sys import exit

payload = {
            "conversationId":"",
            "dados.buscaInteiroTeor":"",
            "dados.pesquisarComSinonimos":["S", "S"],
            "dados.buscaEmenta":"",
            "dados.nuProcOrigem":"",
            "dados.nuRegistro":"",
            "agenteSelectedEntitiesList":"",
            "contadoragente":"0",
            "contadorMaioragente":"0",
            "codigoCr":"",
            "codigoTr":"",
            "nmAgente":"",
            "juizProlatorSelectedEntitiesList":"",
            "contadorjuizProlator":"0",
            "contadorMaiorjuizProlator":"0",
            "codigoJuizCr":"",
            "codigoJuizTr":"",
            "nmJuiz":"",
            "classesTreeSelection.values":"",
            "classesTreeSelection.text":"",
            "assuntosTreeSelection.values":"1156,7771,6233,12222,12223,12224,12225",
            "assuntosTreeSelection.text":"7+Registros+selecionados",
            "comarcaSelectedEntitiesList":"",
            "contadorcomarca":"0",
            "contadorMaiorcomarca":"0",
            "cdComarca":"",
            "nmComarca":"",
            "secoesTreeSelection.values":"",
            "secoesTreeSelection.text":"",
            "dados.dtJulgamentoInicio":"",
            "dados.dtJulgamentoFim":"",
            "dados.dtPublicacaoInicio":"01/01/2011",
            "dados.dtPublicacaoFim":"31/12/2011",
            "dados.dtRegistroInicio":"",
            "dados.dtRegistroFim":"",
            "dados.origensSelecionadas":["T", "R"],
            "tipoDecisaoSelecionados":["A", "H", "D"],
            "dados.ordenarPor":"dtPublicacao"
        }
pag_iter = 1

arquivo_html = open(file='C:/Users/joaoe/Desktop/teste.html', mode='w')

session = requests.Session()

tj_req = session.post(
                url='https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do',
                data=payload,
                headers={
                    'X-Requested-With': 'XMLHttpRequest'
                },
                verify=False)

tj_html = BeautifulSoup(tj_req.text, 'html.parser')
qtde_acords = tj_html.find(id='paginacaoSuperior-A').find('td').text.strip().split()[-1]
qtde_pags = int(qtde_acords) // 20

print(f'Foram encontrados {qtde_acords} acórdãos, divididos em {qtde_pags} páginas.')
# Substituir o final do range com o `qtde_pags` no final do processo.

for paginas in range(1, 2):
    print(f'Acessando página {pag_iter}...')
    pagina = [
        ("tipoDeDecisao", "A"),
        ("pagina", pag_iter,),
        ("conversationId", "")
    ]
    session.params = payload
    session.params.update(pagina)
    t = session.get('https://esaj.tjsp.jus.br/cjsg/trocaDePagina.do')
    tjsp_html = BeautifulSoup(t.text, 'html.parser')
    quadros = tjsp_html.find('tr')
    nums_procs = tjsp_html.find_all('tr', class_='ementaClass')
    clas_assunto = quadros.find_all('tr', class_='ementaClass2')[0]
    relator = quadros.find_all('tr', class_='ementaClass2')[1]
    comarca = quadros.find_all('tr', class_='ementaClass2')[2]
    julgamento = quadros.find_all('tr', class_='ementaClass2')[4]
    publicacao = quadros.find_all('tr', class_='ementaClass2')[5]
    registro = quadros.find_all('tr', class_='ementaClass2')[6]
    outros_nmrs = quadros.find_all('tr', class_='ementaClass2')[7]
    arquivo_html.write(str(quadros))
    pag_iter += 1
    with open('juris.csv', 'w', newline='',) as juris:
        writer = csv.writer(juris)
        writer.writerows(relator)