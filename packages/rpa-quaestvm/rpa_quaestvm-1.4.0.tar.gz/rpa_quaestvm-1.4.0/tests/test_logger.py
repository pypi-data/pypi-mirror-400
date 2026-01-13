import sys
from pathlib import Path

# inclui o src/ no sys.path para permitir importações
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rpa_quaestvm.logger import Logger


def teste_get_logger_deve_retornar_sempre_a_mesma_instância_para_o_mesmo_caminho(tmp_path):
    log_file = tmp_path / "singleton.log"
    logger1 = Logger.get_logger(str(log_file))
    logger2 = Logger.get_logger(str(log_file))
    assert logger1 is logger2


def teste_get_logger_deve_retornar_instancias_diferentes_para_caminhos_diferentes(tmp_path):
    f1 = tmp_path / "a.log"
    f2 = tmp_path / "b.log"

    logger1 = Logger.get_logger(str(f1))
    logger2 = Logger.get_logger(str(f2))

    assert logger1 is not logger2

def teste_logger_deve_escrever_no_arquivo_e_no_console(tmp_path, capsys):
    log_file = tmp_path / "out.log"
    logger = Logger.get_logger(str(log_file))

    teste_info = ":)"
    teste_warn = ":O"
    logger.info(teste_info)
    logger.warning(teste_warn)

    # Captura saída do console
    captured = capsys.readouterr()
    out = captured.out
    assert teste_info in out
    assert teste_warn in out

    # Verifica conteúdo do arquivo de log
    content = log_file.read_text(encoding="utf-8")
    assert teste_info in content
    assert teste_warn in content


def teste_multiplos_loggers_não_duplicam_no_console(tmp_path, capsys):
    f1 = tmp_path / "l1.log"
    f2 = tmp_path / "l2.log"

    l1 = Logger.get_logger(str(f1))
    l2 = Logger.get_logger(str(f2))

    teste_l1 = "yo"
    teste_l2 = "hohoho"
    l1.info(teste_l1)
    l2.info(teste_l2)

    captured = capsys.readouterr()
    out = captured.out

    # Cada mensagem deve aparecer exatamente uma vez no console
    assert out.count(teste_l1) == 1
    assert out.count(teste_l2) == 1

    # Cada arquivo deve conter apenas suas próprias mensagens
    c1 = f1.read_text(encoding="utf-8")
    c2 = f2.read_text(encoding="utf-8")
    assert teste_l1 in c1
    assert teste_l2 in c2

