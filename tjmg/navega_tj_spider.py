import scrapy
import pandas as pd
import ipdb
from pathlib import Path
import re


class TjMGSpider(scrapy.Spider):
    name = "tjmg"

    custom_settings ={
        "CLOSESPIDER_ITEMCOUNT": "10",
        "ROBOTSTXT_OBEY": "False",
        "HTTPCACHE_ENABLED": "1"

    }

    start_urls = ["https://www4.tjmg.jus.br"]  # <- Start page

    def parse(self, response):

        def valida_dados(num_proc):
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
            return num_proc

        cod_comarca = "702"
        csv_limpo = Path(f"resultados/uberlandia_limpo.csv")
        df_csv_limpo = pd.read_csv(csv_limpo, index_col=0, dtype="str")
        num_p_buscar = df_csv_limpo[df_csv_limpo["vara"].isna()]

        for num, rows in num_p_buscar.iterrows():
            processos = rows["num_proc"]
            numero_processo = valida_dados(num_proc=processos)
            links = f"juridico//sf/proc_complemento.jsp?comrCodigo={cod_comarca}&numero=1&listaProcessos={numero_processo[4:-1]}"

            yield scrapy.Request(response.urljoin(links), callback=self.parse_new)

    def parse_new(self, response):
        """Projetos de natureza criminal, depois de baixados, não estão mais disponíveis para pesquisa na internet.
        Deste modo, ao tentar coletar informações destes, só é possível obter conhecimento em qual vara o feito
        tramitou"""

        vara = response.css("html body table.tabela_formulario b::text").extract()[1].strip()
        status = response.css("html body table.tabela_formulario b::text").extract()[2].strip()
        data_distrib = response.css("html body table.corpo td").extract()[2].split()[2].split("</b>")[-1]
        valor_causa = response.css("html body table.corpo td").extract()[3].split("R$")[-1].strip().split(" ")[0]

        classe_proc = response.css("html body table.corpo td").extract()[4].split("</b> ")[-1].split(' </td>')[0]
        assunto = response.css("html body table.corpo td").extract()[6].split("Assunto:")[-1].strip().split("</b>")[-1].strip().strip("</td>").strip().replace("&gt;", ">")

        municip = response.css("html body table.corpo td").extract()[7].split("</b>")[-1].strip(" </td>")

        competencia = response.css("html body table.corpo td").extract()[8].split("</b>")[-1].strip(" </td>")

        yield {
            "vara": vara,
            "status": status,
            "data_distrib": data_distrib,
            "valor_causa": valor_causa,
            "classe_proc": classe_proc,
            "assunto": assunto,
            "municip": municip,
            "competencia": competencia
        }