import numpy as np
from skimage.color import rgb2gray
from skimage.exposure import match_histograms
from skimage.metrics import structural_similarity

# Calcula a diferença estrutural entre duas imagens.
# Indica se são iguais ou parecidas com base em um limiar.
def find_difference(image1, image2, threshold=0.95):
    # Verifica se as imagens têm o mesmo tamanho antes da comparação.
    if image1.shape != image2.shape:
        print("As imagens têm tamanhos diferentes, logo não são iguais!")
        return None
    # Converte as imagens RGB em escala de cinza no intervalo [0, 1].
    gray_image1 = rgb2gray(image1)
    gray_image2 = rgb2gray(image2)

    # Calcula o SSIM (Structural Similarity Index) e
    # obtém o mapa de diferença entre as imagens.
    score, difference_image = structural_similarity(
        gray_image1,
        gray_image2,
        full=True,
        data_range=1.0,
    )

    print("Similaridade das imagens:", score)

    # Decide se as imagens podem ser consideradas iguais
    # de acordo com o limiar definido.
    if score >= threshold:
        print("As imagens são iguais (ou muito parecidas)!")

    else:
        print("As imagens são diferentes!")

    # Normaliza o mapa de diferenças para o intervalo [0, 1].
    diff_min = np.min(difference_image)
    diff_max = np.max(difference_image)
    den = diff_max - diff_min

    # Evita a divisão por zero quando não há variação no mapa.
    if den == 0:
        normalized_difference_image = np.zeros_like(difference_image)
    else:
        normalized_difference_image = (difference_image - diff_min) / den

    return normalized_difference_image


# Ajusta o histograma da imagem1 para que fique semelhante ao da imagem2
# Preserva os canais de cor ao longo do último eixo.
def transfer_histogram(image1, image2):
    matched_image = match_histograms(image1, image2, channel_axis=-1)
    return matched_image
