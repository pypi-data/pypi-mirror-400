import os
import re
import subprocess
import time
from typing import Callable, Literal

import pyautogui
import pygetwindow as gw
from pyscreeze import Box

from .logger import Logger, LoggerInstance
from .rpa_exceptions import ImagemNaoEncontradaException

cliques = {
    "simples": lambda x, y: pyautogui.click(x, y),
    "duplo": lambda x, y: pyautogui.doubleClick(x, y),
    "triplo": lambda x, y: pyautogui.tripleClick(x, y),
    "direito": lambda x, y: pyautogui.rightClick(x, y),
    "rodinha": lambda x, y: pyautogui.middleClick(x, y),
    "nada": lambda x, y: None,
}


class Pyautoqstvm:
    logger: LoggerInstance

    def __init__(self, logger: Logger = None, pasta_imagens: str = "mapeamento"):
        self.logger = logger or Logger.get_logger("logs/rpa.log")
        self.pasta_imagens = pasta_imagens or self.pasta_imagens

    def _raise_or_print(self, msg, raise_errors, verbose=True):
        if raise_errors:
            raise ImagemNaoEncontradaException(msg)
        if verbose:
            self.logger.info(msg)

        return False

    def espera_imagem(
        self,
        imagem: str | list[str],
        timeout: int = 10,
        confidence: float = 0.9,
        raise_errors: bool = True,
        region: tuple[int, int, int, int] = None,
        verbose: bool = True,
        pasta_imagens: str = None,
        extensao_imagem: str = "png",
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
        caminho_imagem = os.path.join(
            pasta_imagens or self.pasta_imagens, f"{imagem}.{extensao_imagem}"
        )

        start_time = time.time()
        found_location = None

        while time.time() - start_time < timeout:
            try:
                # Tenta localizar as imagens na tela
                # for imagem in imagens:
                # self.logger.info(f"Procurando pela imagem: {imagem}")
                found_location = pyautogui.locateOnScreen(
                    caminho_imagem, confidence=confidence, region=region
                )
                if found_location:
                    break  # Imagem encontrada, sai do loop
            except pyautogui.PyAutoGUIException:
                # Algumas versões do pyautogui podem levantar um erro se a imagem não for encontrada
                # mas geralmente ele retorna None. Capturamos para robustez.
                pass

            time.sleep(0.5)  # Pequena pausa para não sobrecarregar a CPU

        if not found_location:
            msg = f"Imagem '{caminho_imagem}' não encontrada na tela após {timeout} segundos."
            return self._raise_or_print(msg, raise_errors, verbose)

        return found_location

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
        # Verificar se a posição horizontal é válida
        if horizontal not in ["esquerda", "direita", "centro"]:
            raise ValueError(f"A posição horizontal '{horizontal}' não é válida")

        # Verificar se a posição vertical é válida
        if vertical not in ["cima", "baixo", "centro"]:
            raise ValueError(f"A posição vertical '{vertical}' não é válida")

        # Calcula as coordenadas de clique com base na posição desejada
        x_click = location.left
        y_click = location.top

        if horizontal == "centro":
            x_click += location.width // 2
        elif horizontal == "direita":
            x_click += (
                location.width - 1
            )  # -1 para garantir que esteja dentro da imagem
        # Se "esquerda", já é found_location.esquerda

        if vertical == "centro":
            y_click += location.height // 2
        elif vertical == "baixo":
            y_click += (
                location.height - 1
            )  # -1 para garantir que esteja dentro da imagem
        # Se "top", já é found_location.top

        return x_click, y_click

    def espera_imagem_e_clica(
        self,
        imagem: str | list[str],
        clique: Literal[
            "simples", "duplo", "triplo", "nada", "direito", "rodinha"
        ] = "simples",
        horizontal: Literal["esquerda", "direita", "centro"] = "centro",
        vertical: Literal["cima", "baixo", "centro"] = "centro",
        timeout: int = 10,
        confidence: float = 0.9,
        raise_errors: bool = True,
        region: tuple[int, int, int, int] = None,
        verbose: bool = True,
        pasta_imagens: str = None,
        extensao_imagem: str = "png",
    ) -> bool:
        """
        Espera por uma imagem na tela e clica nela. Usa os métodos espera_imagem e get_coordenadas_location

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
            raise_errors (bool, optional): se True, lança erro quando não encontra a imagem, se não retorna um booleano. Defaults to True.
            region (tuple[int, int, int, int], optional): região específica da tela na qual procurar a imagem. Defaults to None.
            verbose (bool, optional): se deve ou não logar informações usando o logger da biblioteca. Defaults to True.
            pasta_imagens (str, optional): pasta na qual as imagens de mapeamento são salvas, relativa à raiz. Sobrepõe o valor passado no construtor, se tiver passado. Defaults to "mapeamento".
            extensao_imagem (str, optional): extensão da imagem, sem o ponto. Defaults to 'png'.

        Returns:
            bool: se raise_errors for False e não achar a imagem
            Box: se encontrar a imagem, retorna o objeto Box do pyautogui
        """
        # Verificar se o tipo de clique é válido
        if clique not in ["simples", "duplo", "triplo", "nada"]:
            raise ValueError(f"O tipo de clique '{clique}' não é válido")

        found_location = self.espera_imagem(
            imagem,
            timeout=timeout,
            confidence=confidence,
            region=region,
            raise_errors=raise_errors,
            verbose=verbose,
            pasta_imagens=pasta_imagens,
            extensao_imagem=extensao_imagem,
        )

        if not found_location:
            return False

        x_click, y_click = self.get_coordenadas_location(
            found_location, horizontal=horizontal, vertical=vertical
        )

        try:
            cliques[clique](x_click, y_click)
            if verbose:
                msg = (
                    "NÃO clique realizado"
                    if clique == "nada"
                    else f"Clique {clique} realizado"
                )
                self.logger.info(f"{msg} na imagem '{imagem}' ({x_click}, {y_click})")
            return found_location
        except Exception as e:
            msg = f"Erro ao tentar clicar na imagem '{imagem}': {e}"
            return self._raise_or_print(msg, raise_errors, verbose)

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
        if isinstance(campo, str):
            self.espera_imagem_e_clica(
                campo, "simples", horizontal, vertical, timeout=2
            )
        else:
            x, y = campo
            pyautogui.click(x, y)
        time.sleep(0.5)
        pyautogui.hotkey("ctrl", "a", interval=0.5)
        time.sleep(0.5)
        pyautogui.press("delete")
        time.sleep(0.5)

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
        pasta_imagens: str = None,
        extensao_imagem: str = "png",
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
            pasta_imagens (str, optional): pasta na qual as imagens de mapeamento são salvas, relativa à raiz. Sobrepõe o valor passado no construtor, se tiver passado. Defaults to "mapeamento".
            extensao_imagem (str, optional): extensão da imagem, sem o ponto. Defaults to 'png'.
            msg_erro (str, optional): mensagem de erro lançada caso a validação falhe. Defaults to "Erro de validação de imagem".
            deve_existir (bool, optional): se a imagem deve ser encontrada ou não. Se for False, a existência da imagem se torna um erro. Defaults to True.
            campo_a_limpar (str | tuple[int, int], optional): nome da imagem ou coordenadas x e y passadas para o método limpar_campo caso a validação falhe. Defaults to None.
            on_error (Callable | None, optional): método chamado em caso de erro, sem parâmetros. Defaults to None.

        Raises:
            Exception: caso a validação falhe
        """
        existe = (
            self.espera_imagem(
                imagem,
                timeout,
                raise_errors=False,
                verbose=False,
                confidence=confidence,
                region=region,
                pasta_imagens=pasta_imagens,
                extensao_imagem=extensao_imagem,
            )
            if clique == "nada"
            else self.espera_imagem_e_clica(
                imagem,
                clique,
                horizontal,
                vertical,
                timeout,
                raise_errors=False,
                verbose=False,
                confidence=confidence,
                region=region,
                pasta_imagens=pasta_imagens,
                extensao_imagem=extensao_imagem,
            )
        )
        erro = existe if not deve_existir else not existe

        if erro:
            if campo_a_limpar:
                self.limpar_campo(campo_a_limpar)

            if on_error:
                on_error()

            raise ImagemNaoEncontradaException(msg_erro)

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
        start_time = time.time()

        try:
            # 1. Iniciar a aplicação se o caminho for fornecido
            if caminho_executavel:
                self.logger.info(f"Iniciando a aplicação: {caminho_executavel}")
                try:
                    # Usamos Popen para não bloquear o script
                    # Considerar 'creationflags=subprocess.DETACHED_PROCESS' para Windows
                    # se o processo não deve ser filho do Python script.
                    subprocess.Popen(caminho_executavel, shell=True)
                    time.sleep(2)  # Pequena pausa para a aplicação começar a aparecer
                    self.logger.info(f"{titulo_janela_re}: Aplicação iniciada.")
                except FileNotFoundError:
                    self.logger.info(
                        f"Erro: Executável não encontrado em '{caminho_executavel}'."
                    )
                    return False
                except Exception as e:
                    self.logger.info(
                        f"Erro ao iniciar a aplicação '{caminho_executavel}': {e}"
                    )
                    return False
            else:
                self.logger.info(
                    f"Procurando por uma aplicação existente com título correspondente a '{titulo_janela_re}'..."
                )

            # 2. Esperar e focar na janela
            while time.time() - start_time < tempo_limite:
                todas_as_janelas_gw = gw.getAllWindows()
                janelas_candidatas = []

                for janela_gw in todas_as_janelas_gw:
                    # self.logger.info(janela_gw.title)
                    # Filtrar pelo título usando expressão regular
                    # Usar .title para garantir que estamos pegando o atributo correto
                    if re.search(titulo_janela_re, janela_gw.title, re.IGNORECASE):
                        # self.logger.info("Janela Encontrada: "+ janela_gw.title)
                        janelas_candidatas.append(janela_gw)

                if janelas_candidatas:
                    janela_foco = None

                    # Priorizar janelas que NÃO ESTÃO MINIMIZADAS e são ativas ou visíveis para o usuário
                    for j in janelas_candidatas:
                        if (
                            not j.isMinimized
                        ):  # Se não está minimizada, é uma boa candidata
                            janela_foco = j
                            break  # Pegamos a primeira não minimizada

                    # Se todas estiverem minimizadas, ou a primeira não minimizada não for encontrada,
                    # pegamos a primeira da lista de candidatas e tentamos restaurá-la.
                    if not janela_foco and janelas_candidatas:
                        janela_foco = janelas_candidatas[0]

                    if janela_foco:
                        self.logger.info(
                            f"Janela encontrada: '{janela_foco.title}'. Tentando focar..."
                        )
                        try:
                            if janela_foco.isMinimized:
                                self.logger.info(
                                    f"Janela '{janela_foco.title}' está minimizada. Restaurando..."
                                )
                                janela_foco.restore()
                                time.sleep(0.5)  # Pequena pausa após restaurar

                            # Tenta ativar a janela
                            janela_foco.activate()

                            # Verificação final de foco
                            time.sleep(1)  # Dar um tempo para o sistema focar

                            # Pegar a janela ativa do pyautogui e verificar o título
                            janela_ativa_pyautogui = pyautogui.getActiveWindow()
                            if janela_ativa_pyautogui and re.search(
                                titulo_janela_re,
                                janela_ativa_pyautogui.title,
                                re.IGNORECASE,
                            ):
                                self.logger.info(
                                    f"Janela '{janela_ativa_pyautogui.title}' focada com sucesso!"
                                )
                                return True
                            else:
                                self.logger.info(
                                    f"Aviso: Janela '{janela_foco.title}' não parece estar focada. Tentando Alt+Tab...",
                                )
                                # Fallback para Alt+Tab se a ativação direta não funcionar consistentemente
                                pyautogui.hotkey("alt", "tab")
                                time.sleep(0.5)  # Aguarda a janela do Alt+Tab aparecer

                                # Pressione Tab até encontrar a janela desejada
                                # Limitado para evitar loop infinito e para liberar 'alt'
                                for _ in range(
                                    min(len(todas_as_janelas_gw) * 2, 10)
                                ):  # Tenta no máximo o dobro de janelas ou 10 vezes
                                    janela_ativa_pyautogui = pyautogui.getActiveWindow()
                                    if janela_ativa_pyautogui and re.search(
                                        titulo_janela_re,
                                        janela_ativa_pyautogui.title,
                                        re.IGNORECASE,
                                    ):
                                        self.logger.info(
                                            f"Janela '{janela_ativa_pyautogui.title}' focada via Alt+Tab!"
                                        )
                                        pyautogui.keyUp(
                                            "alt"
                                        )  # Liberar Alt após encontrar e focar
                                        return True
                                    pyautogui.press("tab")
                                    time.sleep(0.2)
                                pyautogui.keyUp(
                                    "alt"
                                )  # Libera Alt se não encontrou após as tentativas

                        except Exception as e:
                            self.logger.info(
                                f"Erro ao tentar focar a janela '{janela_foco.title}': {e}",
                            )

                time.sleep(1)  # Espera 1 segundo antes de tentar novamente

            self.logger.info(
                f"Erro: Janela com título correspondente a '{titulo_janela_re}' não encontrada ou não pôde ser focada após {tempo_limite} segundos.",
            )
            return False

        except Exception as e:
            self.logger.info(f"Ocorreu um erro inesperado: {e}")
            return False

    def encerrar_task(self, task: str):
        """Encerra uma task do sistema usando taskkill

        Args:
            task (str): nome da task usada no taskkill
        """
        os.system(f'taskkill /f /im "{task}" 2>nul')
