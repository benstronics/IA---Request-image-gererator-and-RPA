import logging
from interface import Interface
from referencias import Referencias
import request_open_ai as ia
import rpa
import process_images as ps
import pandas as pd
import os
import threading as td


def gerar_imgs(*args):
    global key
    ref.delete_Files_Folder('imgs_geradas')
    try:
        while True:
            frase = gui.ask_user('Digite aqui alguma frase que deseja gerar imagens')
            if len(frase)>0:
                break
        while True:
            qtde = str(gui.ask_user('Quantas Imagens?')).strip()
            if len(qtde)>0:
                break

        dimensoes = '512x512'
        links = ia.generate_imgs_from_text(frase,int(qtde),dimensoes,key)
        ia.downloads_imgs_links(links,'imgs_geradas','img_gerada')
        gui.after(1000, update_label)
        gui.info('Processo finalizado!')
    except Exception as e:
        logging.exception(e)
        gui.warning(str(e))
def pesquisar_imgs(*args):
    try:
        links_pesquisa = rpa.rpa_get_more_imgs('imgs_geradas')
        links_pesquisa = [link for link in links_pesquisa if not 'favicon' in link and not 'fonts.gstatic' in link]
        print(len(links_pesquisa))
        gui.info(f'{len(links_pesquisa)} imagens encontradas'if len(links_pesquisa)>1 else f'{len(links_pesquisa)} imagem encontrada')
    except Exception as e:
        logging.exception(e)
        gui.warning(str(e))
def baixar_imgs_pesquisadas():
    try:
        df = pd.read_csv(os.getcwd()+'\links_pesquisa.csv',sep=';')
        links_pesquisa = df.links.tolist()
        links_pesquisa = [link for link in links_pesquisa if not 'favicon' in link and not 'fonts.gstatic' in link]
        print(len(links_pesquisa))
        links_pesquisa = links_pesquisa[:int(qtde_p)] if len(links_pesquisa) > int(qtde_p) else links_pesquisa
        ia.downloads_imgs_links(links_pesquisa, 'imgs_pesquisadas', 'img_pesquisada')
        print('Finalizado!')
    except Exception as e:
        logging.exception(e)
        gui.warning(str(e))


def thread_download(*args):
    global qtde_p
    try:
        ref.delete_Files_Folder('imgs_pesquisadas')
        while True:
            qtde_p = str(gui.ask_user('Quantas Imagens?')).strip()
            if len(qtde_p) > 0:
                break
        td.Thread(target=baixar_imgs_pesquisadas).start()
        global nome_pasta
        nome_pasta = "imgs_pesquisadas"
        gui.after(1000, update_label)
    except Exception as e:
        logging.exception(e)
        gui.warning(str(e))


def process_imgs(*args):
    global nome_pasta
    try:
        ref.delete_Files_Folder('img_processadas')
        nome_pasta = "img_processadas"
        gui.after(1000,update_label)
        ps.process_imgs('imgs_pesquisadas')
        nome_pasta = "img_processadas"
        gui.after(1000, update_label)
        gui.info('Processo finalizado!')
    except Exception as e:
        logging.exception(e)
        gui.warning(str(e))

def update_label():
    gui.set_image_labels(nome_pasta,600,300,gui.home_frame,6)


def app(title):
    global gui,ref
    global nome_pasta,key
    nome_pasta = "imgs_geradas"
    while True:
        gui = Interface(title=title)
        ref = Referencias(gui=gui)
        key = ref.descriptografar_dados(ref.criar_credenciais('openai_api_key', ['api_key'])['API_KEY'])
        gui.create_menu_buttons(4,['GERAR IMAGEM A PARTIR DE TEXTO','PESQUISAR IMAGENS SEMELHANTES','BAIXAR IMAGENS ENCONTRADAS','PROCESSAR IMAGENS BAIXADAS'],[gerar_imgs,pesquisar_imgs,thread_download,process_imgs])
        gui.after(1000,update_label)
        gui.loop()

if __name__ == '__main__':
    app(' Benstronics')