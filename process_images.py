import os
from PIL import Image
import cv2
import numpy as np
from referencias import Referencias

ref = Referencias()

def process_imgs(folder,alpha:float=1,beta:int=15):
    images_pesquisa = os.listdir(os.getcwd() + f'\{folder}')
    alpha = ref.criar_filtros([alpha],['alpha(1-3)'],'filtro_contrast control (1-3)')['alpha(1-3)'][0]
    beta = ref.criar_filtros([beta],['beta(0-100)'],'filtro_brightness control (0-100)')['beta(0-100)'][0]

    if not os.path.exists(os.getcwd() + '\img_processadas'):
        os.mkdir('img_processadas')

    for image in images_pesquisa:
        # Open the input image
        input_image = Image.open(f'{folder}\{image}')

        # Resize the image to 512x512 using Lanczos filter for high-quality resizing
        output_image = input_image.resize((512, 512), resample=Image.LANCZOS)

        # Save the output image
        output_image.save(f'img_processadas\{image}')
        # Load the low-quality image
        img = cv2.imread(f'img_processadas\{image}')

        # Adjust the brightness and contrast
        alpha = alpha  # contrast control (1.0-3.0)
        beta = beta  # brightness control (0-100)
        adjusted_img = cv2.convertScaleAbs(img, alpha=alpha, beta=beta)

        # Apply noise reduction
        denoised_img = cv2.fastNlMeansDenoisingColored(adjusted_img, None, 10, 10, 7, 21)

        # Sharpen the image
        kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
        sharpened_img = cv2.filter2D(denoised_img, -1, kernel)

        # Upscale the image
        upscaled_img = cv2.resize(sharpened_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

        # Save the high-quality image
        cv2.imwrite(f'img_processadas\{image}', upscaled_img)