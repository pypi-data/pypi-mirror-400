from datetime import datetime
import logging
import time
from typing import Callable
from dotenv import dotenv_values
from rpa_quaestvm import env_utils
from rpa_quaestvm.logger import Logger, LoggerInstance


class Inicializador:
    logger: LoggerInstance
    log_sep = "*"

    def __init__(self, app_name: str, logger: Logger = None, log_sep="*"):
        self.app_name = app_name
        self.logger = logger or Logger.get_logger("logs/rpa.log")
        self.log_sep = log_sep

    def validar_env(
        self, env_file: str = ".env", env_example_file: str = ".env.example"
    ):
        """Verifica se o .env possui os valores do .env.example

        Args:
            logger (Logger): objeto de logger usado para mostrar mensagens
            env_file (str): Opcional, nome do arquivo .env. Padrão: .env
            env_example_file (str): Opcional, nome do arquivo .env de exemplo. Padrão: .env.example

        Raises:
            EnvironmentError: erro lançado quando uma das variáveis não está presente ou possui valor None
        """
        self.logger.info("Validando se o .env possui os valores do .env.example")
        env_exemplo = dotenv_values(env_example_file, verbose=True)
        env_real = dotenv_values(env_file, verbose=True)

        for key in env_exemplo:
            if key not in env_real or env_real[key] is None:
                raise EnvironmentError(f"Variável de ambiente não definida: {key}")

    def log_com_separador(self, texto, level=logging.INFO):
        half_sep = self.log_sep * 3
        full_sep = self.log_sep * (len(texto) + 6 + (len(half_sep) * 2))

        self.logger.log(level, full_sep)
        self.logger.log(level, f"{half_sep}   {texto}   {half_sep}")
        self.logger.log(level, full_sep)

    def esperar_horario_execucao(
        self,
    ):
        """Verifica de 1 em 1 minuto se está no horário de execução, saindo do loop caso esteja.

        Assume que as variáveis `HORARIO_INICIO_ROBO` e `HORARIO_TERMINO_ROBO` estão definidas no .env e são um número entre 0 e 23.

        Raises:
            EnvironmentError: caso as vairiáveis de ambiente não estejam configuradas
        """
        horario_inicio = env_utils.intenv("HORARIO_INICIO_ROBO")
        horario_fim = env_utils.intenv("HORARIO_TERMINO_ROBO")

        if not horario_inicio or not horario_fim:
            raise EnvironmentError(
                "HORARIO_INICIO_ROBO ou HORARIO_TERMINO_ROBO não configurados no .env"
            )

        def dentro_intervalo(hora, inicio, fim):
            # intervalo normal no mesmo dia
            if inicio < fim:
                return inicio <= hora < fim
            # intervalo que atravessa meia-noite (ex: 16 -> 4)
            return hora >= inicio or hora < fim

        is_descansando = False
        while True:
            hora_atual = datetime.now().hour

            if dentro_intervalo(hora_atual, horario_inicio, horario_fim):
                is_descansando = False
                break
            else:
                if not is_descansando:
                    self.log_com_separador("DESCANSANDO...")
                    is_descansando = True
                time.sleep(60)  # Espera 1 minuto antes de verificar novamente

    def loop_execucao(
        self,
        run: Callable[[], bool],
        esperar_horario_execucao: bool = False,
        repeticoes_por_falha=0,
    ):
        """Inicia o loop de execução inifinito. Se esperar_horario_execucao for True,
        irá esperar estar dentro do horário definido no .env (HORARIO_INICIO_ROBO e HORARIO_TERMINO_ROBO)

        Recebe por parâmetro o método que será chamado a cada execução.

        Encerra a execução com KeyboardInterrupt, e com exeções gerais tenta
        novamente até um limite configurável no .env (1 se não exisitir), na
        variável MAXIMO_TENTATIVAS_LOOP_PRINCIPAL

        Args:
            run (Callable[[], bool]): método chamado a cada execução
            esperar_horario_execucao (bool): se deve esperar no horário definido para executar. Padrão False
            repeticoes_por_falha (int, optional): Não preencher. Usado internamente para chamar o método recursivamente com um limite de vezes. Padrão 0.
        """
        MAX_TENTATIVAS = env_utils.intenv("MAXIMO_TENTATIVAS_LOOP_PRINCIPAL", 1)
        try:
            while True:
                if esperar_horario_execucao:
                    self.esperar_horario_execucao()
                sucesso = run()
                if sucesso:
                    time.sleep(env_utils.intenv("TEMPO_DESCANSO_ENTRE_EXECUCOES", 0))
                else:
                    self.logger.warning(
                        "Última execução falhou. Tentando novamente imediatamente"
                    )

        except KeyboardInterrupt:
            self.log_com_separador(
                "Execução abortada pelo usuário (KeyboardInterrupt)", logging.WARNING
            )
        except Exception:
            self.logger.error("Erro desconhecido no loop principal", exc_info=True)
            if repeticoes_por_falha < MAX_TENTATIVAS:
                self.log_com_separador(
                    f"Reiniciando loop (tentativa {repeticoes_por_falha:02}/{MAX_TENTATIVAS:02})",
                    logging.WARNING,
                )
                self.loop_execucao(
                    run=run, repeticoes_por_falha=repeticoes_por_falha + 1
                )

        # plyer.notification.notify(
        #     message="Script finalizado", app_name=self.app_name, timeout=2
        # )
