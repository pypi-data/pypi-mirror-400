from PIL import Image
from pathlib import Path

def gray_scale(input: str, output: str | None = None) -> str:
    """
    Converte uma imagem em tons de cinza e salva o resultado.

    Parâmetros:
    input : str
        Caminho do arquivo de entrada (imagem colorida).
    output : str | None
        Caminho do arquivo de saída. Se None, um nome padrão será gerado.

    Retorno:
    str
        Caminho do arquivo de saída salvo.
    """
    # Cria um objeto Path a partir do caminho de entrada.
    path = Path(input)

    # Se nenhum caminho de saída for informado, gera um nome padrão,
    # adicionando o sufixo "_gray" ao nome do arquivo original.
    if output is None:
        output = str(path.with_name(path.stem + "_gray.jpg"))

    # Abre a imagem original.
    img = Image.open(path)

    # Converte a imagem para tons de cinza (modo "L" no Pillow).
    gray = img.convert("L")

    # Salva a imagem convertida no caminho de saída.
    gray.save(output)

    return output

