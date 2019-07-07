import re
import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
from pathlib import Path


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
    """Analisando brevemente, me parece que durante dias úteis, e em horário comercial, é utilizado Captcha para inibir
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
    r_dd_complt = requests.get(url=end_dd_complt)
    dados_completos = bs(r_dd_complt.text, "html.parser")

    print(end_dd_complt)

    return dados_completos


def pega_metadados(codigo_fonte):
    try:
        if "Este processo é baixado de natureza criminal" not in codigo_fonte.getText():

            meta_vara = codigo_fonte.find_all("tr")[2].find_all("td")[0].text.strip()
            meta_status = codigo_fonte.find_all("tr")[2].find_all("td")[1].text.strip()  # Ativo / Baixado
            meta_data_distribuicao = codigo_fonte.find_all("tr")[3].find_all("td")[0].text.strip().split(" ")[1]
            meta_valor_causa = codigo_fonte.find_all("tr")[3].find_all("td")[1].text.strip().split(" ")[-1]

            meta_classe = codigo_fonte.find_all("tr")[4].find_all("td")[0].text.split()[1:]
            meta_classe = " ".join(meta_classe)

            meta_assunto = codigo_fonte.find_all("tr")[5].find_all("td")[0].text.split()[1:]
            meta_assunto = " ".join(meta_assunto)

            meta_municipio = codigo_fonte.find_all("tr")[6].find_all("td")[0].text.split()[3:]
            meta_municipio = " ".join(meta_municipio)

            meta_competencia = codigo_fonte.find_all("tr")[6].find_all("td")[1].text.split()[-1]

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
            meta_vara = codigo_fonte.find_all("tr")[2].find_all("td")[0].text.strip()
            meta_status = codigo_fonte.find_all("tr")[2].find_all("td")[1].text.strip()

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

    except IndexError:

        dados = {
            "vara": None,
            "status": None,
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
    cod_promot = []
    cod_magis = []
    df = pd.read_html(f"https://www4.tjmg.jus.br/juridico/sf/proc_movimentacoes.jsp?"
                      f"comrCodigo={cod_comarca}"
                      f"&numero=1"
                      f"&listaProcessos={numero_processo[4:-1]}")[2]

    df.drop(labels=[0], axis=1, inplace=True)
    for promotores in df.dropna()[df[2].dropna().astype("str").str.contains(r"PROMOTOR\(A\) \d+")][2]:
        cod_promot.append(promotores.split()[-1])

    for magis in df.dropna()[df[2].dropna().astype("str").str.contains(r"JUIZ\(A\) TITULAR \d+")][2]:
        cod_magis.append(magis.split()[-1])

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
    COMARCA = "uberlandia"
    # prepara_df(comarca=COMARCA)
    csv_limpo = Path(f"resultados/{COMARCA}_limpo.csv")
    df_csv_limpo = pd.read_csv(csv_limpo, index_col=0, dtype="str")
    df_p_completar = df_csv_limpo[df_csv_limpo["vara"].isna()]
    for index, row in df_p_completar.iterrows():
        print(index)
        numero = row["num_proc"]
        num_proc = valida_dados(comarca=COMARCA, num_proc=numero)
        html_dados = navega_pags_requests(numero_processo=num_proc)
        metadados, num_juiz, num_promotor = pega_metadados(codigo_fonte=html_dados)
        preenche_df(dados=metadados, cod_juiz=num_juiz, cod_promotor=num_promotor)
        df_csv_limpo.to_csv(Path(f"resultados/{COMARCA}_limpo.csv"))
