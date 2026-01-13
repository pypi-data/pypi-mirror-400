# RPA Quaestvm

Abstrações e implementações úteis para RPA

## Funcionalidades

### Classe Logger

Abstração do logging padrão do python. Cria uma única instância do logger para cada caminho de arquivo.

No construtor, deve-se passar o caminho do arquivo de logs criado, o nome do logger (opcional) e o nível de logs (opcional)

```python
def __init__(self, logs_path: str, name: str = 'RPA_Logger', level: str = 'INFO')
```

O método get_logger retorna a instância do objeto de acordo com o valor de logs_path, ou cria uma nova.

### classe Pyautoqstvm

Essa clase possui métodos úteis para navegação desktop usando pyautogui, listados abaixo.

No construtor, pode-se passar um objeto da classe rpa_quaestvm.Logger e o caminho padrão das imagens de mapemaento:

```python
from rpa_quaestvm.logger import Logger
from rpa_quaestvm.pyautoqstvm import Pyautoqstvm

logger = Logger.get_logger("logs/rpa.log")
pyautoqstvm = Pyautoqstvm(logger=logger, pasta_imagens="mapeamento")

pyautoqstvm.espera_imagem(...)

```

```python
def espera_imagem(
    self,
    imagem: str | list[str],
    timeout: int = 10,
    confidence: float = 0.9,
    raise_errors: bool = True,
    region: tuple[int, int, int, int] = None,
    verbose: bool = True,
    pasta_imagens: str = None,
    extensao_imagem: str = 'png'
):
    """Aguarda uma imagem surgir na tela e captura sua posição usando pyautogui

    Args:
        imagem (str): nome da imagem a buscar, sem extensão e pasta raiz. o caminho completo será a concatenação dos parâmetros pasta_imagens, imagem e extensao_imagem
        timeout (int, optional): quantos segundos esperar pela imagem na tela. Defaults to 10.
        confidence (float, optional): parâmetro de confiança passado para o pyautogui. interfere em quanto a imagem real precisa estar fiel à passada por parâmetro. Defaults to 0.9.
        raise_errors (bool, optional): se True, lança erro quando não encontra a imagem, se não retorna um booleano. Defaults to True.
        region (tuple[int, int, int, int], optional): região específica da tela na qual procurar a imagem. Defaults to None.
        verbose (bool, optional): se deve ou não logar informações usando o logger da biblioteca. Defaults to True.
        pasta_imagens (str, optional): pasta na qual as imagens de mapeamento são salvas, relativa à raiz. Sobrepõe o valor passado no construtor, se tiver passado. Defaults to "mapeamento".
        extensao_imagem (str, optional): extensão da imagem, sem o ponto. Defaults to 'png'.

    Returns:
        bool: se raise_errors for False e não achar a imagem
        Box: se encontrar a imagem, retorna o objeto Box do pyautogui
    """
```

```python
def get_coordenadas_location(
    self,
    location: Box,
    horizontal: Literal["esquerda", "direita", "centro"] = "centro",
    vertical: Literal["cima", "baixo", "centro"] = "centro",
):
    """busca as coordenadas de uma região específica dentro de uma Box
    
    A região pode ser uma combinação dos valores horizontal e vertical, sendo retornada a coordenada
    x e y daquele ponto.

    Args:
        location (Box): objeto retornado pelo pyautogui.locateOnScreen ou pelo pyautoqstvm.espera_imagem
        horizontal (Literal[&quot;esquerda&quot;, &quot;direita&quot;, &quot;centro&quot;], optional): região horizontal. Defaults to "centro".
        vertical (Literal[&quot;cima&quot;, &quot;baixo&quot;, &quot;centro&quot;], optional): região vertical. Defaults to "centro".

    Raises:
        ValueError: se os parâmetros horizontal ou vertical não forem válidos

    Returns:
        tuple(int, int): coordenadas x e y do ponto escolhido
    """
```

```python
def espera_imagem_e_clica(
    self,
    imagem: str | list[str],
    click: Literal["simples", "duplo", "triplo", "nada", "direito", "rodinha"] = "simples",
    horizontal: Literal["esquerda", "direita", "centro"] = "centro",
    vertical: Literal["cima", "baixo", "centro"] = "centro",
    timeout: int = 10,
    confidence: float = 0.9,
    raise_errors: bool = True,
    region: tuple[int, int, int, int] = None,
    verbose: bool = True,
    pasta_imagens: str = None,
    extensao_imagem: str = 'png'
) -> bool:
    """
    Espera por uma imagem na tela e clica nela. Usa os métodos espera_imagem e get_coordenadas_location

    Args:
        imagem (str): O caminho para o arquivo da imagem (.png) a ser localizada.
        click_type (str): Tipo de clique: "simples" para clique único, "duplo" para clique duplo. "nada" para não clicar.
                        (Padrão: "simples")
        horizontal (str): Posição horizontal do clique dentro da imagem:
                        "esquerda", "direita" ou "centro". (Padrão: "centro")
        vertical (str): Posição vertical do clique dentro da imagem:
                        "cima", "baixo" ou "centro". (Padrão: "centro")
        timeout (int): Tempo máximo em segundos para esperar pela imagem. (Padrão: 10)
        confidence (float): Nível de confiança para a detecção da imagem (0.0 a 1.0).
                            Valores mais altos são mais estritos. (Padrão: 0.9)
        raise_errors (bool, optional): se True, lança erro quando não encontra a imagem, se não retorna um booleano. Defaults to True.
        region (tuple[int, int, int, int], optional): região específica da tela na qual procurar a imagem. Defaults to None.
        verbose (bool, optional): se deve ou não logar informações usando o logger da biblioteca. Defaults to True.
        pasta_imagens (str, optional): pasta na qual as imagens de mapeamento são salvas, relativa à raiz. Sobrepõe o valor passado no construtor, se tiver passado. Defaults to "mapeamento".
        extensao_imagem (str, optional): extensão da imagem, sem o ponto. Defaults to 'png'.

    Returns:
        bool: se raise_errors for False e não achar a imagem
        Box: se encontrar a imagem, retorna o objeto Box do pyautogui
    """
```

```python
def limpar_campo(
    self,
    campo: str | tuple[int, int],
    horizontal: str = "direita",
    vertical: str = "centro",
):
    """Limpa um campo de texto usando atalhos de teclado (ctrl+a -> delete)

    Args:
        campo (str | tuple[int, int]): imagem a clicar (usando espera_imagem_e_clica), ou coordenadas x e y para clicar usando pyautogui.click
        horizontal (str, optional): região horizontal do clique, se passou uma imagem como campo. Defaults to "direita".
        vertical (str, optional): região vertical do clique, se passou uma imagem como campo. Defaults to "centro".
    """
```

```python
def validar_presenca_imagem(
    self,
    imagem: str,
    clique: Literal[
        "simples", "duplo", "triplo", "nada", "direito", "rodinha"
    ] = "nada",
    horizontal: Literal["esquerda", "direita", "centro"] = "centro",
    vertical: Literal["cima", "baixo", "centro"] = "centro",
    msg_erro: str = "Erro de validação de imagem",
    deve_existir: bool = True,
    campo_a_limpar: str | tuple[int, int] = None,
    timeout: int = 1,
    on_error: Callable | None = None,
    confidence: float = 0.9,
    region: tuple[int, int, int, int] = None,
):
    """Espera por uma imagem aparecer na tela, podendo realizar callbacks caso a imagem exista ou não

    Args:
        imagem (str): nome da imagem a buscar, sem extensão e pasta raiz. o caminho completo será a concatenação dos parâmetros pasta_imagens, imagem e extensao_imagem
        clique (str): Tipo de clique: "simples" para clique único, "duplo" para clique duplo. "nada" para não clicar.
                        (Padrão: "simples")
        horizontal (str): Posição horizontal do clique dentro da imagem:
                        "esquerda", "direita" ou "centro". (Padrão: "centro")
        vertical (str): Posição vertical do clique dentro da imagem:
                        "cima", "baixo" ou "centro". (Padrão: "centro")
        timeout (int): Tempo máximo em segundos para esperar pela imagem. (Padrão: 10)
        confidence (float): Nível de confiança para a detecção da imagem (0.0 a 1.0).
                            Valores mais altos são mais estritos. (Padrão: 0.9)
        region (tuple[int, int, int, int], optional): região específica da tela na qual procurar a imagem. Defaults to None.
        verbose (bool, optional): se deve ou não logar informações usando o logger da biblioteca. Defaults to True.
        pasta_imagens (str, optional): pasta na qual as imagens de mapeamento são salvas, relativa à raiz. Defaults to "mapeamento".
        extensao_imagem (str, optional): extensão da imagem, sem o ponto. Defaults to 'png'.
        msg_erro (str, optional): mensagem de erro lançada caso a validação falhe. Defaults to "Erro de validação de imagem".
        deve_existir (bool, optional): se a imagem deve ser encontrada ou não. Se for False, a existência da imagem se torna um erro. Defaults to True.
        campo_a_limpar (str | tuple[int, int], optional): nome da imagem ou coordenadas x e y passadas para o método limpar_campo caso a validação falhe. Defaults to None.
        on_error (Callable | None, optional): método chamado em caso de erro, sem parâmetros. Defaults to None.

    Raises:
        Exception: caso a validação falhe
    """
```

```python
def encerrar_task(self, task: str):
    """Encerra uma task do sistema usando taskkill

    Args:
        task (str): nome da task usada no taskkill
    """
```

```python
def abrir_e_focar_aplicacao(
    self,
    caminho_executavel: str = None,
    titulo_janela_re: str = ".*",
    tempo_limite: int = 30,
):
    """
    Inicia uma aplicação (se o caminho for fornecido) ou foca em uma já existente,
    aguardando sua janela principal e dando foco a ela, utilizando apenas pyautogui.

    Args:
        caminho_executavel (str, opcional): O caminho completo para o executável da aplicação
                                            (ex: "C:\\Windows\\notepad.exe").
                                            Se não for fornecido, a função tentará focar em
                                            uma janela existente com o título especificado.
        titulo_janela_re (str): Uma expressão regular para o título da janela principal esperada.
                                Use ".*" para qualquer título (padrão).
        tempo_limite (int): O tempo máximo em segundos para esperar a janela carregar.

    Returns:
        bool: True se a aplicação foi aberta/focada e a janela principal foi focada com sucesso,
            False caso contrário.
    """
```
