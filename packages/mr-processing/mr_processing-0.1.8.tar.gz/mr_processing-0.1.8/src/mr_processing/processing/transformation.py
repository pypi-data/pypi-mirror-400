from skimage.transform import resize

# Redimensiona a imagem mantendo a proporção informada.
def resize_image(image, proportion):
    # Garante que a proporção esteja no intervalo [0, 1].
    assert 0 <= proportion <= 1, "Informe uma proporção válida entre 0 e 1."

    # Calcula nova altura e largura com base na proporção informada.
    height = round(image.shape[0] * proportion)
    width = round(image.shape[1] * proportion)

    # Redimensiona a imagem com suavização para evitar aliasing.
    image_resized = resize(image, (height, width), anti_aliasing=True)
    return image_resized
