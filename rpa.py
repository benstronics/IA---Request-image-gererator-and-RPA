import logging
import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from subprocess import CREATE_NO_WINDOW
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from referencias import Referencias

ref = Referencias()

def get_src(elements):
    try:
        srcs =[element.get_attribute('src') for element in elements if 'http' in element.get_attribute('src')]
        return srcs
    except Exception as e:
        logging.exception(e)

def rpa_get_more_imgs(folder_imgs):
    # configurando argumentos para inicialização do chrome
    options = Options()
    options.add_experimental_option("prefs", {
        "download.default_directory": os.getcwd(),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
        # Disable Chrome's PDF Viewer
        "download.extensions_to_open": "applications/pdf",
        'plugins.always_open_pdf_externally': True
    })
    headless = str(ref.criar_filtros([0], ['headless'], 'filtro_chromedriver_headless')['headless'][0]).strip()
    if int(headless)==1:
        options.add_argument('headless')
    chrome_service = Service(ChromeDriverManager(path=os.getcwd()).install())
    chrome_service.creationflags = CREATE_NO_WINDOW
    driver = webdriver.Chrome(service=chrome_service, options=options)

    # Buscando imagens geradas pela IA
    images = os.listdir(folder_imgs)

    # Cria lista para armazenar os links de todas as imagens pesquisadas
    todos_links=[]

    # Loop para pesquisar outras imagens semelhantes no google para cada imagem gerada pela ia
    for image in images:
        try:
            path_img = os.path.abspath(os.getcwd() + f'\{folder_imgs}\{image}')
            print(path_img)

            # Acessa o google imagens
            driver.get('https://www.google.com/imghp')
            # create an ActionChains object
            actions = ActionChains(driver)

            # Verifica caixa de dialogo pedindo login e click em não fazer login
            try:
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable(
                    (By.TAG_NAME, 'iframe')))
                iframe = driver.find_element(By.TAG_NAME,'iframe')
                driver.switch_to.frame(iframe)
                WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/c-wiz/div/div/div/div[2]/div[2]/button')))
                nao_login = driver.find_element(By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div/div/c-wiz/div/div/div/div[2]/div[2]/button')
                actions.click(nao_login).perform()
                driver.switch_to.default_content()
            except Exception as e:
                logging.exception(e)

            # Click na opção de pesquisar por imagens google lens
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[3]/div[4]')))
            lens = driver.find_element(By.XPATH, '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[3]/div[4]')
            actions.click(lens).perform()

            # Envia a imagem para pesquisa
            WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="ow6"]/div[3]/c-wiz/div[2]/div/div[3]/div[2]/div/div[2]/span')))
            inputs = driver.find_elements(By.TAG_NAME, 'input')
            inputs[8].send_keys(path_img)

            # Espera resultado da pesquisa e coleta os links da imagens encontradas
            WebDriverWait(driver, 30).until(EC.element_to_be_clickable(
                (By.CLASS_NAME, 'aah4tc')))
            element = driver.find_element(By.CLASS_NAME, 'aah4tc')
            print(element.text)
            time.sleep(5)

            tags_a = element.find_elements(By.TAG_NAME, 'a')
            list_imgs = [tag_a.find_elements(By.TAG_NAME, 'img') for tag_a in tags_a]
            print(list_imgs, len(list_imgs))
            links_imgs = [get_src(imgs) for imgs in list_imgs]
            print(links_imgs)

            # Armazenandos os links
            todos_links+=sum(links_imgs,[])
        except Exception as e:
            logging.exception(e)
            continue
    df = pd.DataFrame(todos_links)
    df.columns = ['links']
    df.to_csv(os.getcwd()+'\links_pesquisa.csv',sep=';')
    print(len(todos_links))
    driver.quit()
    return todos_links



if __name__ == '__main__':
    links = rpa_get_more_imgs()
