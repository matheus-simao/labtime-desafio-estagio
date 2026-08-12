"""
Utilitarios de apresentacao no terminal.

Este modulo cuida apenas da camada visual do console (cores ANSI, cabecalho,
paineis e barra de energia). Ele e proposital e completamente separado da
logica dos padroes de projeto, que vive nos demais modulos do pacote.
"""

import os
import sys

LARGURA_BARRA = 20


def _habilitar_vt_windows() -> bool:
    """
    Habilita o processamento de sequencias ANSI no console do Windows.

    Returns:
        True se o modo de terminal virtual foi habilitado com sucesso.
    """
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)
        modo = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(modo)):
            return False
        return bool(kernel32.SetConsoleMode(handle, modo.value | 0x0004))
    except Exception:
        return False


def _suporta_cores() -> bool:
    """
    Detecta se o terminal atual suporta cores ANSI.

    Returns:
        True se as cores devem ser aplicadas na saida.
    """
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not sys.stdout.isatty():
        return False
    if sys.platform == "win32":
        return _habilitar_vt_windows()
    return True


_COR_ATIVA = _suporta_cores()


class Cor:
    """Codigos ANSI usados na interface, desativados quando nao ha suporte."""

    RESET = "\033[0m" if _COR_ATIVA else ""
    NEGRITO = "\033[1m" if _COR_ATIVA else ""
    FRACO = "\033[2m" if _COR_ATIVA else ""
    VERMELHO = "\033[31m" if _COR_ATIVA else ""
    VERDE = "\033[32m" if _COR_ATIVA else ""
    AMARELO = "\033[33m" if _COR_ATIVA else ""
    AZUL = "\033[34m" if _COR_ATIVA else ""
    MAGENTA = "\033[35m" if _COR_ATIVA else ""
    CIANO = "\033[36m" if _COR_ATIVA else ""


def preparar_saida() -> None:
    """
    Garante que a saida padrao aceite os caracteres acentuados e de caixa.

    Returns:
        None.
    """
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def colorir(texto: str, cor: str) -> str:
    """
    Aplica uma cor ANSI ao texto informado.

    Args:
        texto: conteudo a ser colorido.
        cor: codigo de cor da classe Cor.

    Returns:
        Texto envolvido pelos codigos de cor e reset.
    """
    return f"{cor}{texto}{Cor.RESET}"


def cabecalho() -> None:
    """
    Imprime o banner de abertura do console.

    Returns:
        None.
    """
    linhas = [
        "╭────────────────────────────────────────────────╮",
        "│   SISTEMA DA NAVE · Console Interativo         │",
        "│   LabTIME — Desafio Técnico de Estágio         │",
        "╰────────────────────────────────────────────────╯",
    ]
    for linha in linhas:
        print(colorir(linha, Cor.CIANO))


def titulo_painel(texto: str) -> None:
    """
    Imprime a linha de abertura de um painel.

    Args:
        texto: titulo exibido no topo do painel.

    Returns:
        None.
    """
    print(colorir(f"┌─ {texto}", Cor.CIANO))


def linha_painel(texto: str) -> None:
    """
    Imprime uma linha de conteudo dentro de um painel.

    Args:
        texto: conteudo da linha (pode conter cores).

    Returns:
        None.
    """
    print(f"{colorir('│', Cor.CIANO)} {texto}")


def fim_painel() -> None:
    """
    Imprime a linha de fechamento de um painel.

    Returns:
        None.
    """
    print(colorir("└─", Cor.CIANO))


def barra_energia(atual: int, maximo: int) -> str:
    """
    Monta uma barra visual de energia colorida conforme o nivel restante.

    Args:
        atual: energia atual do nucleo.
        maximo: energia maxima do nucleo.

    Returns:
        Barra formatada e colorida pronta para impressao.
    """
    proporcao = atual / maximo if maximo else 0
    preenchido = int(LARGURA_BARRA * proporcao)
    barra = "█" * preenchido + "░" * (LARGURA_BARRA - preenchido)

    if proporcao <= 0.3:
        cor = Cor.VERMELHO
    elif proporcao <= 0.6:
        cor = Cor.AMARELO
    else:
        cor = Cor.VERDE
    return colorir(barra, cor)


def sucesso(texto: str) -> None:
    """Imprime uma mensagem de confirmacao de acao bem-sucedida."""
    print(f"{colorir('✓', Cor.VERDE)} {texto}")


def erro(texto: str) -> None:
    """Imprime uma mensagem de erro ou uso incorreto de comando."""
    print(f"{colorir('✗', Cor.VERMELHO)} {texto}")


def aviso(texto: str) -> None:
    """Imprime uma mensagem informativa de baixa severidade."""
    print(f"{colorir('•', Cor.AMARELO)} {texto}")


def perguntar(rotulo: str) -> str | None:
    """
    Solicita um dado complementar ao usuario durante a execucao de um comando.

    Args:
        rotulo: pergunta exibida ao usuario.

    Returns:
        Texto digitado, ou None se a entrada foi interrompida.
    """
    try:
        return input(f"  {colorir('?', Cor.AMARELO)} {rotulo} {colorir('›', Cor.CIANO)} ")
    except (EOFError, KeyboardInterrupt):
        print()
        return None


def evento(origem: str, texto: str, critico: bool) -> None:
    """
    Imprime um evento emitido por um sistema da nave.

    Args:
        origem: nome do subsistema que emitiu o evento (ex: Escudos).
        texto: descricao do que aconteceu.
        critico: True para destacar o evento como situacao de crise.

    Returns:
        None.
    """
    cor = Cor.VERMELHO if critico else Cor.VERDE
    print(f"  {colorir(f'[{origem}]', cor)} {texto}")


def fala(texto: str) -> None:
    """Imprime a acao narrada de um tripulante."""
    print(f"  {colorir('»', Cor.MAGENTA)} {texto}")


def disparo(texto: str) -> None:
    """Imprime o resultado de um disparo da nave."""
    print(f"  {colorir('◈', Cor.AMARELO)} {texto}")


def prompt() -> str:
    """
    Monta o texto do prompt de entrada de comandos.

    Returns:
        Prompt formatado para ser usado no input().
    """
    return f"{Cor.CIANO}nave ›{Cor.RESET} "
