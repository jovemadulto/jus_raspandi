def classe_assunto(item):
    texto = item.get_text()
    texto = texto.strip()
    texto = texto.split(' ')
    del texto[0]
    texto = ' '.join(texto)
    texto = texto.split('/')
    classe_proc, assunto_proc = texto[0].strip(), texto[1].strip()
    return classe_proc, assunto_proc


def nums(item):
    texto = item.get_text()
    return texto


def relator(item):
    texto = item.get_text().strip().split(' ')
    del texto[0]
    texto = ' '.join(texto)
    return texto


def comarca(item):
    texto = item.get_text().strip().split(' ')
    del texto[0]
    texto = ' '.join(texto).strip()
    return texto


def datas(item):
    texto = item.get_text().strip().split(' ')
    del texto[0: 2]
    texto = texto[-1].split(':')[-1].strip()
    return texto


def ementa(item):
    texto = item.get_text().strip()
    texto = texto.split('\xa0')
    ementa = texto[0].strip()
    referencia = ' '.join(texto[1:])
    return ementa, referencia
