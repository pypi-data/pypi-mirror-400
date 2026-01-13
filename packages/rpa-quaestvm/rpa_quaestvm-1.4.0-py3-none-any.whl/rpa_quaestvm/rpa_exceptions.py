class ImagemNaoEncontradaException(Exception):
    """Exceção levantada quando a imagem especificada não é encontrada na tela."""

    pass


class ItemInvalidoException(Exception):
    """Exceção lançada quando um item sendo executado no loop principal possui dados inválidos ou incompletos."""

    pass


class ItemJaProcessadoException(Exception):
    """Exceção lançada quando um item já estava finalizado no início do processo, não sendo necessário executar."""

    pass
