# Jusraspandi MG

## Sites disponíveis
[ X ] https://www.tjmg.jus.br/ // Esfera Estadual

[   ] https://portal.trf1.jus.br/portaltrf1/pagina-inicial.htm // TRF 1ª Região

[   ] http://www.tre-mg.jus.br/ // Tribunal Regional Eleitoral - MG

### TJMG - Esfera Estadual

- raspar_datas.py 

Primeiro programa a ser executado, reúne em um arquivo `datas.csv` os dias em que houveram publicações de diários oficiais em determina comarca.

- pegar_pdfs.py

Próximo programa a ser executado, reúne as datas conhecidas através do passo anterior e faz download dos arquivos no site do Tribunal.

        # TO-DO #

        Incluir rotina que faça backup dos diários no InternetArchive.org para que seja possível fazer o download do pacote inteiro mais facilmente no futuro.

- raspar_pdfs.py 

Abre os arquivos com extensão PDF, extrai o texto destes e realiza uma busca utilizando expressão regular com o formato de numeração conhecido dos processos.

