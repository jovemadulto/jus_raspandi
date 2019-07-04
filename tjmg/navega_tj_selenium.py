import re
import pandas as pd
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import speech_recognition as sr
import os
from sys import exit


def navegador():
    """
    A variável "mimes" deve receber os MIME-Types de todos os arquivos que serão baixados automaticamente pelo Firefox
    (GeckoDriver).
    Setando as options para "permissions.default.imagem, 2" não são carregadas as imagens das páginas, porém não parece
    permitir que seja baixado o áudio dos captchas para serem analisados posterirmente.
    """

    options = Options()

    mimes = "audio/wave"

    # options.set_preference("permissions.default.image", 2)
    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("browser.download.folderList", 0)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.helperApps.alwaysAsk.force", False)
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", mimes)

    driver = webdriver.Firefox(firefox_options=options)
    driver.implicitly_wait(time_to_wait=2)

    return driver


def prepara_df(comarca):
    """Prepara csv para a utilização posterior, retirando os valores duplicados do arquivo original para economizar
    tempo durante a respagem de dados e cria um arquivo limpo que será utilizado no restante da execução do script"""

    csv_arq = Path(f"resultados/{comarca}.csv")
    arq_bruto = pd.read_csv(csv_arq,
                            names=["num_proc",
                                   "assunto"])
    arq_bruto.reset_index(drop=True, inplace=True)

    arq_limpo = arq_bruto["num_proc"].unique()
    del arq_bruto
    df_limpo = pd.DataFrame(arq_limpo, columns=["num_proc"])
    df_limpo["vara"] = ""
    df_limpo["status"] = ""
    df_limpo["data_distribuicao"] = ""
    df_limpo["valor_causa"] = ""
    df_limpo["assunto"] = ""
    df_limpo["classe"] = ""
    df_limpo["comarca"] = ""
    df_limpo["competencia"] = ""
    df_limpo["data_baixado"] = ""
    df_limpo["cod_juiz"] = ""
    df_limpo["cod_promotor"] = ""

    df_limpo.to_csv(f"resultados/{comarca}_limpo.csv")


def valida_dados(comarca, num_proc):
    """Procura detectar se o numero do processo se encontra no formato de 'Número CNJ' e o transforma para 'Número TJMG,
    de forma que o primeiro possui dígitos verificadores e, no momento, não possuo capacidades de gerá-los. Assim, o
    caminho 'Número CNJ' > 'Número TJMG' é possível, mas 'Número TJMG' > 'Número CNJ' não.
    A API do site parece aceitar ambos os formatos, se comportando de maneira similar em ambos os casos.

    :return num_proc: formato CCCCYYDDDDDDD"""

    regex_cnj = re.compile(r"\d{7}([-.])\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}")

    if regex_cnj.fullmatch(num_proc):
        cod_comarca = num_proc[-4:]
        ano_proc = num_proc[13:15]
        digitos = num_proc[:7]
        num_proc = cod_comarca + ano_proc + digitos

    if "-" in num_proc:
        num_proc = num_proc.replace("-", "")

    print(num_proc)
    return num_proc


def navega_pags_requests(numero_processo):
    """Analisando brevemente, me parece que durante dias úteis, entre as 12:00 > 19:00, é utilizado Captcha para inibir
    a navegação automatizada das páginas de informações processuais. Neste caso, caso a suspeita se confirme, deveríamos
    apresentar uma alternativa utilizando Selenium capaz de ultrapassar o Captcha, ou realizar a raspagem em horários
    agendados.
    São armazenados informações de duas seções a de 'Dados Completos' (onde são recolhidas a maioria das informações e a
    de 'Todos os Andamentos' onde é recolhido o código de servidores públicos que atuaram no processo, como magistrados
    e promotores."""

    cod_comarca = numero_processo[1:4]
    end_dd_complt = "https://www4.tjmg.jus.br/juridico/sf/proc_complemento.jsp?" \
        f"comrCodigo={cod_comarca}" \
                    "&numero=1" \
        f"&listaProcessos={numero_processo[4:-1]}"

    ff.get(end_dd_complt)
    print(end_dd_complt)
    dados_completos = ff.page_source

    return dados_completos


def resolve_captcha(audio_fp):
    with sr.AudioFile(audio_fp) as source:
        audio = r.record(source)
        try:
            # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
            captcha = r.recognize_google(audio, language="pt-BR")
            print(f"CAPTCHA: {captcha}")
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print("Could not request results from Google Speech Recognition service; {0}".format(e))

    return str(captcha)


def burla_captcha():
    audio_link = ff.find_element_by_link_text("Baixar o áudio").click()

    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    audio_filepath = str(Path(desktop) / 'audio.wav')

    captcha = resolve_captcha(audio_fp=audio_filepath)

    captcha_form = ff.find_element_by_id("captcha_text").send_keys(captcha)
    sleep(3)
    os.remove(audio_filepath)


def pega_metadados():
    sleep(3)
    if "Este processo é baixado de natureza criminal" not in ff.page_source:

        meta_vara = ff.find_element_by_xpath("/html/body/table[1]/tbody/tr[2]/td[1]/b").text
        meta_status = ff.find_element_by_xpath(
            "/html/body/table[1]/tbody/tr[2]/td[2]/b").text.strip()  # Ativo / Baixado
        meta_data_distribuicao = \
        ff.find_element_by_xpath("/html/body/table[2]/tbody/tr[1]/td[1]").text.strip().split(" ")[1]
        meta_valor_causa = ff.find_element_by_xpath("/html/body/table[2]/tbody/tr[1]/td[2]").text.strip().split(" ")[-1]

        meta_classe = ff.find_element_by_xpath("/html/body/table[2]/tbody/tr[2]/td").text.split()[1:]
        meta_classe = " ".join(meta_classe)

        meta_assunto = ff.find_element_by_xpath("/html/body/table[2]/tbody/tr[3]").text.split()[1:]
        meta_assunto = " ".join(meta_assunto)

        meta_municipio = ff.find_element_by_xpath("/html/body/table[2]/tbody/tr[4]/td[1]").text.split()[3:]
        meta_municipio = " ".join(meta_municipio)

        meta_competencia = ff.find_element_by_xpath("/html/body/table[2]/tbody/tr[4]/td[2]").text.split()[-1]

        dados = {
            "vara": meta_vara,
            "status": meta_status,
            "data_distribuicao": meta_data_distribuicao,
            "valor_causa": meta_valor_causa,
            "assunto": meta_assunto,
            "classe": meta_classe,
            "municipio": meta_municipio,
            "competencia": meta_competencia
        }

        num_juiz, num_promotor = pega_dados_mov(numero_processo=num_proc)

        return dados, num_juiz, num_promotor

    else:
        meta_vara = ff.find_element_by_xpath("/html/body/table[1]/tbody/tr[2]/td[1]/b").text
        meta_status = ff.find_element_by_xpath(
            "/html/body/table[1]/tbody/tr[2]/td[2]/b").text.strip()  # Ativo / Baixado

        dados = {
            "vara": meta_vara,
            "status": meta_status,
            "data_distribuicao": None,
            "valor_causa": None,
            "assunto": None,
            "classe": None,
            "municipio": None,
            "competencia": None
        }

        num_juiz = num_promotor = None

    return dados, num_juiz, num_promotor


def pega_dados_mov(numero_processo):
    cod_comarca = numero_processo[1:4]
    cod_promot = set()
    cod_magis = set()

    ff.get(f"https://www4.tjmg.jus.br/juridico/sf/proc_movimentacoes.jsp?"
                             f"comrCodigo={cod_comarca}"
                             f"&numero=1"
                             f"&listaProcessos={numero_processo[4:-1]}")

    if "clique em 'Gerar nova imagem'" in ff.page_source:
        burla_captcha()
        sleep(3)

    cod_html = ff.page_source
    df = pd.read_html(cod_html)
    print(len(df))
    df = df[2]
    df.drop(labels=[0], axis=1, inplace=True)
    for promotores in df.dropna()[df[2].dropna().astype("str").str.contains(r"PROMOTOR\(A\) \d+")][2]:
        cod_promot.add(promotores.split()[-1])

    for magis in df.dropna()[df[2].dropna().astype("str").str.contains(r"JUIZ\(A\) TITULAR \d+")][2]:
        cod_magis.add(magis.split()[-1])

    return cod_magis, cod_promot


def preenche_df(dados, cod_juiz="", cod_promotor=""):
    df_csv_limpo.at[index, "vara"] = dados["vara"]
    df_csv_limpo.at[index, "status"] = dados["status"]
    df_csv_limpo.at[index, "data_distribuicao"] = dados["data_distribuicao"]
    df_csv_limpo.at[index, "valor_causa"] = dados["valor_causa"]
    df_csv_limpo.at[index, "assunto"] = dados["assunto"]
    df_csv_limpo.at[index, "classe"] = dados["classe"]
    df_csv_limpo.at[index, "comarca"] = dados["municipio"]
    df_csv_limpo.at[index, "competencia"] = dados["competencia"]
    df_csv_limpo.at[index, "cod_juiz"] = cod_juiz
    df_csv_limpo.at[index, "cod_promotor"] = cod_promotor


if __name__ == "__main__":
    ff = navegador()
    r = sr.Recognizer()

    COMARCA = "uberlandia"

    # prepara_df(comarca=COMARCA)
    csv_limpo = Path(f"resultados/{COMARCA}_limpo.csv")
    df_csv_limpo = pd.read_csv(csv_limpo, index_col=0).astype(dtype="str")

    df_p_completar = df_csv_limpo[df_csv_limpo["vara"].isna()]
    while True:
        try:
            for index, row in df_p_completar.iterrows():
                numero = row["num_proc"]
                num_proc = valida_dados(comarca=COMARCA, num_proc=numero)
                html_dados = navega_pags_requests(numero_processo=num_proc)
                if "clique em 'Gerar nova imagem'" in html_dados:
                    burla_captcha()

                metadados, num_juiz, num_promotor = pega_metadados()
                preenche_df(dados=metadados, cod_juiz=num_juiz, cod_promotor=num_promotor)
                df_csv_limpo.to_csv(Path(f"resultados/{COMARCA}_limpo.csv"))

        except NoSuchElementException:
            novo_captcha = ff.find_element_by_link_text("Gerar nova imagem").click()
            burla_captcha()

            continue
