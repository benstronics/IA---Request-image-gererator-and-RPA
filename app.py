from interface import Interface
from referencias import Referencias
import request_open_ai as ia
import rpa
import process_images as ps
import pandas as pd
import os
import threading as td

ref = Referencias()

def gerar_imgs(*args):
    ref.delete_Files_Folder('imgs_geradas')
    while True:
        frase = gui.ask_user('Digite aqui alguma frase que deseja gerar imagens')
        if len(frase)>0:
            break
    while True:
        qtde = str(gui.ask_user('Quantas Imagens?')).strip()
        if len(qtde)>0:
            break
    while True:
        dimensoes = str(gui.ask_user('Dimensões das Imagens? ex: (1024x1024)')).strip()
        if len(dimensoes)>0 and len(dimensoes.lower().split('x')) == 2:
            break
    links = ia.generate_imgs_from_text(frase,int(qtde),dimensoes)
    ia.downloads_imgs_links(links,'imgs_geradas','img_gerada')
    gui.info('Processo finalizado!')

def pesquisar_imgs(*args):
    links_pesquisa = rpa.rpa_get_more_imgs('imgs_geradas')
    links_pesquisa = [link for link in links_pesquisa if not 'favicon' in link and not 'fonts.gstatic' in link]
    print(len(links_pesquisa))
    gui.info('Processo finalizado!')

def baixar_imgs_pesquisadas():
    df = pd.read_csv(os.getcwd()+'\links_pesquisa.csv',sep=';')
    links_pesquisa = df.links.tolist()
    links_pesquisa = [link for link in links_pesquisa if not 'favicon' in link and not 'fonts.gstatic' in link]
    print(len(links_pesquisa))
    links_pesquisa = links_pesquisa[:int(qtde_p)] if len(links_pesquisa) > int(qtde_p) else links_pesquisa
    ia.downloads_imgs_links(links_pesquisa, 'imgs_pesquisadas', 'img_pesquisada')
    print('Finalizado!')


def thread_download(*args):
    global qtde_p
    ref.delete_Files_Folder('imgs_pesquisadas')
    while True:
        qtde_p = str(gui.ask_user('Quantas Imagens?')).strip()
        if len(qtde_p) > 0:
            break
    td.Thread(target=baixar_imgs_pesquisadas).start()


def process_imgs(*args):
    ps.process_imgs('imgs_pesquisadas')
    gui.info('Processo finalizado!')

def update_label():
    gui.set_image_labels('imgs_geradas',600,300,gui.home_frame,6)
    #gui.after(1000, update_label)

def app(title):
    global gui
    while True:
        gui = Interface(title=title)
        gui.create_menu_buttons(4,['GERAR IMAGEM A PARTIR DE TEXTO','PESQUISAR IMAGENS SEMELHANTES','BAIXAR IMAGENS ENCONTRADAS','PROCESSAR IMAGENS BAIXADAS'],[gerar_imgs,pesquisar_imgs,thread_download,process_imgs])
        gui.after(1000,update_label)
        gui.loop()

if __name__ == '__main__':
    app(' Benstronics')