from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pathlib import Path
from io import StringIO
from os import listdir
import re
import shutil
from sys import exit


def converter_pdfs(pasta_pdfs):
    for arquivos in listdir(pasta_pdfs):
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)

        with open(pasta_pdfs.joinpath(arquivos), 'rb') as fp:
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            password = ""
            maxpages = 0
            caching = True
            pagenos=set()

            for page in PDFPage.get_pages(fp,
                                          pagenos,
                                          maxpages=maxpages,
                                          password=password,
                                          caching=caching,
                                          check_extractable=True):
                interpreter.process_page(page)

            text = retstr.getvalue()

            device.close()
            retstr.close()
            return text


def raspa_conteudo(conteudo):
    procs_pad = re.compile(pattern=r"(\d{7}(\.|\-)\d{2}\.\d{4}\.\d\.\d{2}\.\d{4})|(\d{12}-\d)")
    ocorrencias = procs_pad.findall(string=conteudo)
    processos = "uberlandia.csv"
    with open(pasta_output.joinpath(processos).absolute(), mode="a") as processos:
        for achados in ocorrencias:
            processos.writelines(achados[-1] + ",\n")


if __name__ == "__main__":
    pasta_input = Path("downloads/UDI/")
    pasta_output = Path("resultados")

    if not pasta_output.exists():
        pasta_output.mkdir()

    for arquivos in listdir(pasta_input):
        texto = converter_pdfs(pasta_pdfs=pasta_input)
        raspa_conteudo(conteudo=texto)
        shutil.move(f"{pasta_input}\\{arquivos}", f"{pasta_output}")