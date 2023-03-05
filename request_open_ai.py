import os
import requests
import json
import rpa

def generate_imgs_from_text(text,qtde:int=10,size_img:str='1024x1024',key:str=''):
    url = "https://api.openai.com/v1/images/generations"

    querystring = {"":""}

    payload = {
        "prompt": f"{text}",
        "n": qtde,
        "size": f"{size_img}"
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {key}"
    }

    response = requests.request("POST", url, json=payload, headers=headers, params=querystring)
    content = response.json()
    print(content['data'])
    links = [url['url'] for url in content['data']]
    print(links)
    return links

def downloads_imgs_links(links,folder,name_img):
    if not os.path.exists(os.getcwd() + f'\{folder}'):
        os.mkdir(os.getcwd() + f'\{folder}')
    for i, link in enumerate(links):
        response = requests.get(link)

        if response.status_code == 200:
            with open(f"{folder}\{name_img}_{i}.png", "wb") as f:
                f.write(response.content)
                print("Image downloaded successfully.")
        else:
            print("Failed to download image.")


if __name__ == '__main__':
    pass


