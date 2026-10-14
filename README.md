# TA03 - Visão Computacional (Transformação de Perspectiva) 

A aplicação foi projetada para receber um conjunto de fotografias contendo quadros ou obras de arte emolduradas, processar essas imagens para identificar a região exata da tela/pintura e aplicar uma transformação de perspectiva (homografia). O resultado é uma imagem plana e retificada da obra, corrigindo o ângulo em que a foto foi tirada e isolando a arte de sua moldura e do ambiente externo.

## Fluxo de Trabalho

O fluxo de execução da aplicação é automatizado e dividido nas seguintes etapas:

1. **Leitura e Pré-Processamento:** As fotografias, que devem estar presentes no diretório `./dataset`, são carregadas, redimensionadas proporcionalmente para otimizar o processamento e convertidas para escala de cinza (*grayscale*) com aplicação de desfoque Gaussiano para redução de ruído.
2. **Detecção de Características e Bordas:** O algoritmo utiliza múltiplas abordagens combinadas para mapear bordas na imagem: 
   - Detecção de bordas adaptativa (`auto_canny`).
   - Gradientes morfológicos para destacar relevos de molduras complexas.
   - Limiarização adaptativa para lidar com variações locais de iluminação.
3. **Seleção do Melhor Quadro:** A partir dos contornos encontrados, a aplicação busca polígonos de quatro lados (quadriláteros). Para garantir que a tela da pintura seja selecionada (e não a moldura externa), o sistema avalia a área, verifica se há quadros contidos uns nos outros e calcula a complexidade visual/textura da região interna usando a variância da Laplaciana.
4. **Retificação de Perspectiva:** Com os quatro cantos da obra identificados e ordenados corretamente, calcula-se a matriz de transformação (`cv2.getPerspectiveTransform`) e aplica-se a distorção reversa (`cv2.warpPerspective`), "esticando" a imagem para que ela fique perfeitamente retangular e plana.
5. **Corte e Salvamento:** Uma pequena margem de segurança (3.5%) é recortada das bordas para eliminar eventuais sombras ou reflexos residuais da moldura física. A imagem final tratada é salva no diretório `./output`.

## Execução

Devido às dependências de sistema exigidas pelo `OpenCV`, a aplicação foi conteinerizada via **Docker** utilizando a versão `opencv-python-headless`. Isso garante um ambiente de execução leve e isolado, eliminando a necessidade de configurar dependências de interface gráfica (X11) ou instalar pacotes na máquina *host*.

### Pré-requisitos
Certifique-se de ter o [Docker](https://docs.docker.com/get-docker/) instalado no seu sistema. Coloque as fotografias que deseja processar (formatos suportados: `.jpg`, `.jpeg`, `.png`, `.bmp`) na pasta `./dataset/`.

### Usando Docker Compose (Recomendado)
A maneira mais fácil de executar o projeto é utilizando o Docker Compose, que constrói a imagem e mapeia automaticamente os volumes dos diretórios de entrada e saída.

No terminal, na raiz do projeto, execute:

```bash
docker-compose up --build
```