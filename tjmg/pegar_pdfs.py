from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException
import csv
import speech_recognition as sr
import os
import shutil
from pathlib import Path
from sys import exit
from time import sleep


def navegador():

    options = Options()

    mimes = "multipart/x-zip, application/zip, application/x-zip-compressed, text/xml, application/xml, application/plain, application/x-rtf, application/rtf, text/richtext, www/mime, multipart/x-gzip, application/x-gzip, application/x-compressed, application/msword, text/plain, application/x-www-form-urlencoded, application/x-pdf, application/pdfss, application/vnd.adobe.xfdf, application/vnd.fdf, application/vnd.adobe.xdp+xml, audio/wave, application/pdf, application/octet-stream"

    options.set_preference("browser.download.useDownloadDir", True)
    options.set_preference("browser.download.folderList", 0)
    options.set_preference("browser.download.manager.showWhenStarting", False)
    options.set_preference("browser.helperApps.alwaysAsk.force", False)
    options.set_preference("browser.download.lastDir", str(downloads.absolute()))
    options.set_preference("browser.helperApps.neverAsk.saveToDisk", mimes)

    driver = webdriver.Firefox(firefox_options=options)
    driver.implicitly_wait(time_to_wait=2)

    return driver


def resolve_captcha(audio_file):
    with sr.AudioFile(audio_file) as source:
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


def baixa_diario(driver, data):
    dia, mes, ano = data.split(sep="/")
    driver.get(url="https://dje.tjmg.jus.br/diarioJudiciarioData.do")
    data_campo = driver.find_element_by_id("data").send_keys(data)
    comarca = Select(driver.find_element_by_id("tipoDiario"))
    comarca_campo = comarca.select_by_value("comarca|0702")

    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    diario_path = str(Path(desktop))
    diario_file = f"SF0702{ano}{mes}{dia}.PDF" #SFCCCCYYYYMMDD.PDF
    audio_file = str(Path(desktop) / 'audio.wav')
    sleep(1)

    if diario_file not in os.listdir(downloads.absolute()):
        try:
            audio_link = driver.find_element_by_link_text("escute o código").click()
            captcha = resolve_captcha(audio_file=audio_file)

            if captcha.isdigit():
                captcha_form = driver.find_element_by_id("captcha_text").send_keys(captcha)
                download_diario = driver.find_element_by_css_selector(".botao_vinho").click()
                sleep(5)
                shutil.move(f"{diario_path}\\{diario_file}", f"{str(downloads.absolute())}\\SF0702{ano}{mes}{dia}.PDF")
                os.remove(audio_file)
            else:
                os.remove(audio_file)


        except FileNotFoundError:
            os.remove(audio_file)

        except UnexpectedAlertPresentException:
            alert = driver.switch_to.alert()
            alert.accept()


if __name__ == "__main__":
    downloads = Path("downloads")
    if not downloads.exists():
        downloads.mkdir()
    browser = navegador()
    r = sr.Recognizer()
    with open("datas.csv") as datas:
        # while len(os.listdir(downloads)) != 2520:
        for linha in datas:
            dia, mes, ano = linha.split(sep="/")
            ano = ano.strip()
            if f"SF0702{ano}{mes}{dia}.PDF" not in os.listdir(downloads):
                print(f"Buscando o diario de {linha.strip()}")
                baixa_diario(browser, data=linha.strip())