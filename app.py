import logging
from interface import Interface
from referencias import Referencias
import request_open_ai as ia
import rpa
import process_images as ps
import pandas as pd
import os
import threading as td
from functools import partial

# As funções aqui apenas implementam alguns tratamentos para melhorar a interface como usuario
# Fazendo a chamada das funções principais de seus respectivos modulos

# Função que gera as imagens a partir do texto fornecido
def gerar_imgs(*args):
    global key,nome_pasta
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
        ts = ['' for _ in links]
        for i, image in enumerate(links):
            ts[i] = td.Thread(target=partial(ia.downloads_imgs_links,[image],'imgs_geradas',f'img_gerada_{i}'))
            ts[i].start()

        _ = [ts[k].join() for k in range(len(links))]
        nome_pasta = "imgs_geradas"
        gui.after(1000, update_label)
        gui.info('Processo finalizado!')
    except Exception as e:
        logging.exception(e)
        msg = 'Não foi possivel gerar imagens! Tente novamente'
        gui.warning(msg,len(msg))

# Função que pesquisa no google lens as imagens geradas pela IA para encontrar mais imagens semelhantes
def pesquisar_imgs(*args):
    global click
    if click:
        click=False
        try:
            images = os.listdir('imgs_geradas')
            ts = ['' for _ in images]
            for i, image in enumerate(images):
                ts[i] = td.Thread(target=partial(rpa.rpa_get_more_imgs,'imgs_geradas',[image]))
                ts[i].start()
            _ = [ts[k].join() for k in range(len(images))]
            click=True
            lista_df = os.listdir('dfs')
            df_completo = pd.DataFrame()
            for df in lista_df:
                df_completo = pd.concat([df_completo, pd.read_csv(os.getcwd() + f'\dfs\{df}', sep=';')],ignore_index=True)
            df_completo.to_csv(os.getcwd() + f'\links_pesquisa.csv', sep=';')
            links_pesquisa = df_completo.links.tolist()
            links_pesquisa = [link for link in links_pesquisa if not 'favicon' in link and not 'fonts.gstatic' in link]
            print(len(links_pesquisa))
            gui.info(f'{len(links_pesquisa)} imagens encontradas'if len(links_pesquisa)>1 else f'{len(links_pesquisa)} imagem encontrada')
        except Exception as e:
            logging.exception(e)
            gui.warning(str(e))

# funcao chamada pela função que implementa o download paralelo
def baixar_imgs_pesquisadas(link,nome_img):
    try:
        ia.downloads_imgs_links([link], 'imgs_pesquisadas', nome_img)
        print('Finalizado!')
    except Exception as e:
        logging.exception(e)
        gui.warning(str(e))

# Faz o download as imagens encontradas nas pesquisas por processamento paralelo
def thread_download(*args):
    global qtde_p
    try:
        ref.delete_Files_Folder('imgs_pesquisadas')
        while True:
            qtde_p = str(gui.ask_user('Quantas Imagens?')).strip()
            if len(qtde_p) > 0:
                break

        df = pd.read_csv(os.getcwd() + '\links_pesquisa.csv', sep=';')
        links_pesquisa = df.links.tolist()
        links_pesquisa = [link for link in links_pesquisa if not 'favicon' in link and not 'fonts.gstatic' in link]
        print(len(links_pesquisa))
        links_pesquisa = links_pesquisa[:int(qtde_p)] if len(links_pesquisa) > int(qtde_p) else links_pesquisa
        ts = ['' for _ in links_pesquisa]
        for i, link in enumerate(links_pesquisa):
            ts[i] = td.Thread(target=partial(baixar_imgs_pesquisadas,link,f'img_pesquisada_{i}'))
            ts[i].start()
        _ = [ts[k].join() for k in range(len(links_pesquisa))]
        global nome_pasta
        nome_pasta = "imgs_pesquisadas"
        gui.after(1000, update_label)
        gui.info('Processo finalizado!')
    except Exception as e:
        logging.exception(e)
        gui.warning(str(e))

# Processa as imagens baixadas para tentar melhorar a qualidade
def process_imgs(*args):
    global nome_pasta
    try:
        ref.delete_Files_Folder('img_processadas')
        ps.process_imgs('imgs_pesquisadas',gui=gui)
        nome_pasta = "img_processadas"
        gui.after(1000, update_label)
        gui.info('Processo finalizado!')

    except Exception as e:
        logging.exception(e)
        gui.warning(str(e))

# Atualiza a interface grafica com as imagens
def update_label():
    gui.set_image_labels(nome_pasta,600,250,gui.home_frame,6,update_label)

# Muda a pasta de vizualização das imagens
def change_folder(option:str=''):
    global nome_pasta
    nome_pasta = option
    gui.after(1000, update_label)

# Função que constroe o corpo da interface com o usuario fazendo uso de funções já pre-moldadas no modulo interface
def app(title):
    global gui,ref
    global nome_pasta,key,click
    nome_pasta = "imgs_geradas"
    gui = Interface(title=title)
    ref = Referencias(gui=gui)
    click = True
    while True:
        ref.verificar_ou_criar_pasta(nome_pasta)
        key = ref.descriptografar_dados(ref.criar_credenciais('openai_api_key', ['api_key'])['API_KEY'])
        gui.create_menu_buttons(4,['GERAR IMAGEM A PARTIR DE TEXTO','PESQUISAR IMAGENS SEMELHANTES','BAIXAR IMAGENS ENCONTRADAS','PROCESSAR IMAGENS BAIXADAS'],[gerar_imgs,pesquisar_imgs,thread_download,process_imgs])
        gui.create_menu_lista(gui.home_frame,['imgs_geradas','imgs_pesquisadas','img_processadas'],change_folder,offset_row=6)
        gui.after(1000,update_label)
        gui.loop()


if __name__ == '__main__':
    app(' Benstronics')