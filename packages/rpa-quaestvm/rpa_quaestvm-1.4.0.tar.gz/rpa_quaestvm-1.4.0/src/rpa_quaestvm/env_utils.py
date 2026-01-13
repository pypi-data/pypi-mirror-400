import os


def intenv(key: str, default: int = 0) -> int:
    """Lê uma variável de ambiente como inteiro."""
    val = os.getenv(key)
    if val is None:
        return default
    return int(val)

def boolenv(key: str, default: bool = False) -> bool:
    """Lê uma variável de ambiente como booleano.

    Interpreta os valores "true", "1", "yes" (case insensitive) como True,
    e "false", "0", "no" (qualquer outro valor, na verdade) como False.
    
    Se a variável não estiver definida, retorna o valor padrão fornecido.

    Args:
        key (str): Nome da variável de ambiente.
        default (bool, optional): Valor padrão se a variável não estiver definida. Padrão é False.

    Returns:
        bool: Valor booleano da variável de ambiente.
    """
    val = os.getenv(key)
    if val is None:
        return default
    return val.lower() in ("true", "1", "yes")