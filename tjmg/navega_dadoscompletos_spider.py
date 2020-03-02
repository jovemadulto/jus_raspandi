import scrapy
import pandas as pd
from pathlib import Path
import re


class TjMGSpider(scrapy.Spider):
    name = "tjmg"

    custom_settings ={
        # "CLOSESPIDER_ITEMCOUNT": "10",
        "ROBOTSTXT_OBEY": "False",
        "HTTPCACHE_ENABLED": "0",
        "HTTPCACHE_IGNORE_HTTP_CODES": ["500"],
        "CONCURRENT_REQUESTS": "8",
        "FEED_EXPORT_ENCODING": "utf-8",
        "DOWNLOADER_MIDDLEWARES.update": ({
             'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
             'scrapy_useragents.downloadermiddlewares.useragents.UserAgentsMiddleware': 500,
         }),

        "USER_AGENTS": [
        ('Mozilla/5.0 (X11; Linux x86_64) '
         'AppleWebKit/537.36 (KHTML, like Gecko) '
         'Chrome/57.0.2987.110 '
         'Safari/537.36'),  # chrome
        ('Mozilla/5.0 (X11; Linux x86_64) '
         'AppleWebKit/537.36 (KHTML, like Gecko) '
         'Chrome/61.0.3163.79 '
         'Safari/537.36'),  # chrome
        ('Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) '
         'Gecko/20100101 '
         'Firefox/55.0')] # firefox
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
        csv_limpo = Path(f"dano_moral.csv")
        df_csv_limpo = pd.read_csv(csv_limpo, index_col=0, dtype="str")
        num_p_buscar = df_csv_limpo

        for num, rows in num_p_buscar.iterrows():
            processos = rows["num_proc"]
            numero_processo = valida_dados(num_proc=processos)
            links = f"juridico//sf/proc_movimentacoes.jsp??comrCodigo={cod_comarca}&numero=1&listaProcessos={numero_processo[4:-1]}"

            yield scrapy.Request(response.urljoin(links), callback=self.parse_new)

    def parse_new(self, response):

        def pandas_extract(link):
            

        num_proc = response.xpath('//tr/td/text()').extract()[12].strip()
        data_trans = response.xpath('//tr/td/text()').extract()[13].strip()
        data_sent = response.xpath('//tr/td/text()').extract()[13].strip()

        yield {
            "num_proc": num_proc,
            "data_trans": data_trans,
            "data_sent": data_sent,
        }