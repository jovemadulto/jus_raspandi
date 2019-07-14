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
        "HTTPCACHE_ENABLED": "1",
        "CONCURRENT_REQUESTS": "5",
        "FEED_EXPORT_ENCODING": "utf-8"

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

        numero = len(response.xpath('//tr/td/b').extract())
        check_disp = len(response.xpath("//p/b/text()").extract())
        """check_disp procura tags de parágrafos nas páginas de metadados dos procssos. Nos casos onde não é possível
        obter dados em decorrência de sua natureza, existe somente 1 tag na página. Por outro lado, onde não é possível
        navegar, o conteúdo da página é substituído por um texto dentro de <p> tags, por isso a checagem."""

        if numero != 0:
            if check_disp != 3:
                num_proc = response.xpath('//tr/td/b/text()').re("\d{7}-\d{2}.\d{4}\.\d.\d{2}.\d{4}")[0]
                vara = response.xpath('//table/tr/td/b').re_first(r"((INFÂNCIA|\d{1,2}ª|CR.PESSOA/PREC.CRIME|EXECUÇÕES|JESP CÍVEL) "
                                                                  r"(E|VARA|UJ-\dº JD|UJ - \dº JD|T. RECURSAL|FAZENDA|FAZ.L.12153/09|FAMÍLIA/SUCESSÕES|CRIMINAIS) "
                                                                  r"(JUVENTUDE|CRIMINAL|CÍVEL|JESP CÍVEL|CRIME|PÚBLICA))")
                status = response.xpath('//tr/td/b/text()').re_first("(ATIVO|BAIXADO)")

                data_distrib = response.xpath('//tr/td/text()').extract()[8].strip()
                valor_causa = response.xpath('//tr/td/text()').extract()[9].strip("R$ ").replace(".", "").replace(",", ".")
                classe_proc = response.xpath('//tr/td/text()').extract()[10].strip()
                assunto = response.xpath('//tr/td/text()').extract()[11].strip()
                municip = response.xpath('//tr/td/text()').extract()[12].strip()
                competencia = response.xpath('//tr/td/text()').extract()[13].strip()

                yield {
                    "num_proc": num_proc,
                    "vara": vara,
                    "status": status,
                    "data_distrib": data_distrib,
                    "valor_causa": valor_causa,
                    "classe_proc": classe_proc,
                    "assunto": assunto,
                    "municip": municip,
                    "competencia": competencia,
                }

            else:
                num_proc = response.xpath('//tr/td/b/text()').re("\d{7}-\d{2}.\d{4}\.\d.\d{2}.\d{4}")[0]
                vara = response.xpath('//tr/td/b/text()').extract()[1].strip()
                status = response.xpath('//tr/td/b/text()').extract()[2].strip()
                yield {
                    "num_proc": num_proc,
                    "vara": vara,
                    "status": status,
                    "data_distrib": None,
                    "valor_causa": None,
                    "classe_proc": None,
                    "assunto": None,
                    "municip": None,
                    "competencia": None
                }
        else:
            yield {
                "num_proc": None,
                "vara": None,
                "status": None,
                "data_distrib": None,
                "valor_causa": None,
                "classe_proc": None,
                "assunto": None,
                "municip": None,
                "competencia": None
            }