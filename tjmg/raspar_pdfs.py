from pathlib import Path
from os import listdir
import re
import shutil
import os
import fitz
from sys import exit


def converter_pdfs(pasta_pdfs):

    for nome_arquivo in os.listdir(pasta_pdfs):
        print(f"Escaneando {nome_arquivo}")
        pdf = fitz.Document(pasta_input.joinpath(nome_arquivo))

        for pag_num in range(0, pdf.pageCount):
            pagina = pdf.loadPage(pag_num)
            texto = pagina.getText("text")
            raspa_conteudo(conteudo=texto)


def raspa_conteudo(conteudo):
    """
    Dependendo do formato do número do processo encontrado pelo regex, o número retornava no achados[0] (quando segue
    o formato XXXXXXX.|-VV.YYYY.8.13.CCCC), e em outros retornava no achados[-1] (no formato CCCCYYXXXXXXX-D). O regex
    também retorna "." e "-".Assim, foi necessário incluir o condicional no final do arquivo para poder identificar o
    item correto para ser incluído no arquivo de coleta.
    """
    procs_pad = re.compile(r"(\d{7}([-.])\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})|(\d{12}-\d)")
    ocorrencias = procs_pad.findall(string=conteudo)
    processos = "uberlandia.csv"
    with open(pasta_output.joinpath(processos).absolute(), mode="a") as processos:
        for achados in ocorrencias:
            for item in achados:
                if len(item) > 3:
                    print(item)
                    # processos.writelines(item + ",\n")


if __name__ == "__main__":
    pasta_input = Path("downloads/teste/")
    pasta_output = Path("resultados")

    if not pasta_output.exists():
        pasta_output.mkdir()

    for arquivos in listdir(pasta_input):
        converter_pdfs(pasta_pdfs=pasta_input)

        shutil.move(f"{pasta_input}\\{arquivos}", f"{pasta_output}")