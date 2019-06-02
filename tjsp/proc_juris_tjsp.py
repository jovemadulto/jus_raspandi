# Em um primeiro momento procuraremos pelos processos relacionados com o tema de saúde para determinarmos o que está
# sendo discutido em juízo.
# Assim, entraremos na página do ESAJ e adicionaremos o código '6233', referente aos Planos de Saúde, no campo Assunto.
# A checkbox de origem deve estar marcada como 2º grau e os Tipos de Publicação devem ser Acórdãos, Homologações de
# Acordo e Decisões Monocráticas.
# Salvaremos todos os resultados em um CSV para ser analisado posteriormente de forma facilitada.#

import re
import json
import gspread
from authlib.client import AssertionSession
from time import sleep
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.chrome.options import Options
from tele_bot import ceres_bot


def cria_tabela(nome_tabela, ano_pesquisado, email):
    tabela = gc.create(f'{nome_tabela}_{ano_pesquisado}')
    tabela.share(email, perm_type='user', role='writer')
    end_tab = f'https://docs.google.com/spreadsheets/d/{tabela.id}'
    ceres_bot.send_msg('-1001306618533', message=f'{end_tab}')
    return tabela.title


def cria_cabecalho(tabela):
    tabela = gc.open(tabela)
    planilha = tabela.get_worksheet(index=0)
    planilha.insert_row(values=['ID_PROC', 'N_DO_PROCESSO', 'CLASSE', 'ASSUNTO', 'RELATOR', 'COMARCA', 'ORG_JULGADOR',
                                'DATA_JULGMNTO', 'DATA_PUBLI', 'DATA_REGSTR', 'EMENTA', 'REFERNC'])


def preenche_tabela(tabela, dados_raspados):
    tabela = gc.open(tabela)
    planilha = tabela.get_worksheet(index=0)
    planilha.append_row(values=dados_raspados)


def regex_limpa_pub(padrao, publicacao):
    pub_regex = padrao
    pub = re.findall(pattern=pub_regex, string=publicacao)[0]
    pub = str(pub).strip()
    return pub


def get_ementa(elemento_web_processo, id_do_acordao):
    browser.implicitly_wait(10)
    ement_bot = elemento_web_processo.find_element_by_class_name('textoSemFormatacao')
    browser.execute_script("arguments[0].click()", ement_bot)
    emen_text = browser.find_element_by_id(f'textAreaDados_{id_do_acordao}').text
    bot_fechar = browser.find_element_by_id('popupModalBotaoFechar')
    browser.execute_script("arguments[0].click()", bot_fechar)
    return emen_text


def get_acord_id(elemento_web_processo):
    elemento = elemento_web_processo
    proc_id = elemento.find_element_by_class_name('downloadEmenta')
    acord = proc_id.get_attribute('cdacordao')
    return acord


def exec_script(css_selector):
    browser.implicitly_wait(10)
    bot_click = browser.find_element_by_css_selector(css_selector)
    browser.execute_script("arguments[0].click()", bot_click)


def create_assertion_session(conf_file, scopes, subject=None):
    with open(conf_file, 'r') as f:
        conf = json.load(f)

    token_url = conf['token_uri']
    issuer = conf['client_email']
    key = conf['private_key']
    key_id = conf.get('private_key_id')

    header = {'alg': 'RS256'}
    if key_id:
        header['kid'] = key_id

    # Google puts scope in payload
    claims = {'scope': ' '.join(scopes)}
    return AssertionSession(
        grant_type=AssertionSession.JWT_BEARER_GRANT_TYPE,
        token_url=token_url,
        issuer=issuer,
        audience=token_url,
        claims=claims,
        subject=subject,
        key=key,
        header=header,
    )


scopes = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive',
]

session = create_assertion_session('F:\Diana-crawlers\credentials.json', scopes)

gc = gspread.Client(None, session=session)

ano_publi = '2012'
# Ano de publicação das ementas que deverão ser pesquisadas.
# Aparentemente são indexadas somente a partir de 2010.

assunto = '6233'

chrome_options = Options()
chrome_options.add_argument("--headless")
browser = webdriver.Chrome()
wait = WebDriverWait(browser, 10)

browser.maximize_window()
browser.get(url='https://esaj.tjsp.jus.br/cjsg/resultadoCompleta.do')
browser.implicitly_wait(30)
browser.find_element_by_id('iddados.dtPublicacaoInicio').send_keys(f'0101{ano_publi}')
browser.find_element_by_id('iddados.dtPublicacaoFim').send_keys(f'3112{ano_publi}')
browser.find_element_by_id('botaoLimpar_assuntos').click()
browser.find_element_by_id('botaoProcurar_assuntos').click()
browser.find_element_by_id('assuntos_treeSelectFilter').send_keys(assunto)
browser.find_element_by_css_selector('#filtroButton').click()
browser.find_element_by_css_selector(
    '#assuntos_treeSelectContainer > div.popupBar > table > tbody > tr > td > input:nth-child(2)').click()
browser.find_element_by_css_selector(
    '#assuntos_treeSelectContainer > div.popupBar > table > tbody > tr > td > input.spwBotaoDefaultGrid').click()
browser.find_element_by_css_selector(r'#iddados\2e buscaEmenta').submit()

qtde_procs = str(
    browser.find_element_by_xpath('/html/body/table[4]/tbody/tr/td/div/div[1]/div[1]/table/tbody/tr[1]/td[1]').text)
qtde_procs = int(qtde_procs.split()[-1])
qtde_pags = qtde_procs / 20
print(f'Foram encontrados {qtde_procs} processos divididos em aproximadamente {qtde_pags} paginas')

tab_google = cria_tabela(nome_tabela=f'Jurisprudencia Planos de Saúde', ano_pesquisado=ano_publi,
                         email='joaoernanepaula@gmail.com')
cria_cabecalho(tab_google)

id_proc = 1  # Posição do processo na busca. Variável iniciada neste momento para ser usada no loop abaixo.

for paginas in range(0):  # paginas a serem puladas
    browser.implicitly_wait(20)
    exec_script('a[title="Próxima página"]')
    sleep(3)

while id_proc != qtde_procs:
    for processo in browser.find_elements_by_class_name('fundocinza1'):
        sleep(1)
        browser.implicitly_wait(20)
        espera_carregar = WebDriverWait(browser, 10).until(expected_conditions.visibility_of(processo))
        juris = processo.text
        acord_id = get_acord_id(processo)
        try:
            id_proc = processo.find_element_by_class_name('ementaClass').text.split()[0]  # Posição do processo na busca
            num_proc = regex_limpa_pub(padrao=r"\d{7}.*\n", publicacao=juris)

            clas_assun_proc = regex_limpa_pub(padrao=r"Classe.*\n", publicacao=juris)
            sembarra = clas_assun_proc.split('/')
            semponto = sembarra[1].split(':')
            classe_proc = (semponto[1][1:]).strip(' ')
            assunto_proc = sembarra[-1][1:]

            relator_proc = regex_limpa_pub(padrao=r"Relat.*\n", publicacao=juris)[12:]

            comar_proc = regex_limpa_pub(padrao=r"Comar.*\n", publicacao=juris)[9:]

            orgao_proc = regex_limpa_pub(padrao=r"Ór.*\n", publicacao=juris)[16:]

            julgamento = regex_limpa_pub(padrao=r"Data do jul.*\n", publicacao=juris)[20:]

            publi = regex_limpa_pub(padrao=r"Data de pu.*\n", publicacao=juris)[20:]

            registro = regex_limpa_pub(padrao=r"Data de reg.*\n", publicacao=juris)[18:]

            ementa_compl = get_ementa(elemento_web_processo=processo, id_do_acordao=acord_id)
            ementa = ((ementa_compl.split('\n'))[0]).strip(' ')
            referen = ((ementa_compl.split('\n'))[-1]).strip(' ')

            data = [id_proc,  # ID do processo retornado após a busca
                    num_proc,  # Numero do processo
                    classe_proc,  # Classe do processo
                    assunto_proc,  # Assunto do processo
                    relator_proc,  # Relator do processo
                    comar_proc,  # Comarca de origem do processo
                    orgao_proc,  # Órgão julgador do Acórdão
                    julgamento,  # Data do julgamento
                    publi,  # Data da publicação do Acórdão
                    registro,  # Data do registro do Acórdão
                    ementa,
                    referen]

            preenche_tabela(tabela=tab_google, dados_raspados=data)

        except IndexError:
            data_except = [id_proc,
                           'Undefined',
                           'Undefined',
                           'Undefined',
                           'Undefined',
                           'Undefined',
                           'Undefined',
                           'Undefined',
                           'Undefined',
                           'Undefined',
                           'Undefined',
                           'Undefined']
            preenche_tabela(tabela=tab_google, dados_raspados=data_except)
            ceres_bot.send_msg(chat_id='-1001306618533', message=f'Ops! O item nº {id_proc}'
                                                                       f'não tinha todas as informações!')
            screenshot = browser.get_screenshot_as_png()
            ceres_bot.send_photo(chat_id='-1001306618533', file_object=screenshot)

        except gspread.exceptions.APIError() as ApiError:
            session = create_assertion_session('F:\Diana-crawlers\credentials.json', scopes)
            gc = gspread.Client(None, session=session)
            ceres_bot.send_msg(chat_id='-1001306618533', message=f'Ops! Parece que há algo errado em algum dos '
                                                                       f'crawlers! A seguinte mensagem de erro foi'
                                                                       f'retornada:'
                                                                       f'{ApiError}')
            browser.quit()

        # print(f"{num_proc}\n{ementa}\n{referen}\n------")
    exec_script('a[title="Próxima página"]')
browser.quit()
