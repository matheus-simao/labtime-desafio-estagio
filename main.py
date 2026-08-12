"""
Ponto de entrada do desafio LabTIME: console interativo do sistema da nave.

Nenhuma saida deste script e pre-programada de forma linear: o loop abaixo
le comandos digitados pelo avaliador e reage dinamicamente, acionando os
padroes de projeto implementados no pacote `sistema`.

Digite `ajuda` a qualquer momento para ver a lista de comandos.
"""

from sistema import ui
from sistema.armas import ARMAS_DISPONIVEIS, MODIFICADORES_DISPONIVEIS
from sistema.nave import Nave
from sistema.nucleo import EstadoNucleo
from sistema.tripulante import FUNCOES_DISPONIVEIS, Tripulante
from sistema.ui import Cor

GRUPOS_AJUDA: list[tuple[str, str, list[tuple[str, str]]]] = [
    (
        "NÚCLEO DE ENERGIA",
        "Ticket 1 · Observer",
        [
            ("tomar_dano <valor>", "reduz a energia do núcleo"),
            ("reduzir_energia <valor>", "sinônimo de tomar_dano"),
            ("restaurar_energia <valor>", "recupera energia do núcleo"),
        ],
    ),
    (
        "TRIPULAÇÃO",
        "Ticket 2 · Strategy",
        [
            ("add_tripulante <nome> <função>", "adiciona um tripulante"),
            ("trocar_funcao <nome> <função>", "troca a função de um tripulante vivo"),
            ("trabalhar <nome>", "executa a função atual do tripulante"),
            ("tripulantes", "lista os tripulantes cadastrados"),
            ("funcoes", "lista as funções disponíveis"),
        ],
    ),
    (
        "ARMAMENTO",
        "Ticket 3 · Strategy + Decorator",
        [
            ("equipar_arma <tipo>", "equipa uma arma base na nave"),
            ("adicionar_modificador <tipo>", "empilha um modificador na arma"),
            ("atirar", "dispara a arma equipada"),
            ("armas", "lista as armas disponíveis"),
            ("modificadores", "lista os modificadores disponíveis"),
        ],
    ),
    (
        "GERAL",
        "",
        [
            ("status", "mostra o painel completo da nave"),
            ("ajuda", "mostra esta lista de comandos"),
            ("sair", "encerra o programa"),
        ],
    ),
]


def _formatar_comando(comando: str) -> tuple[str, int]:
    """
    Colore o nome do comando e seus argumentos de forma distinta.

    Args:
        comando: assinatura do comando (ex: "trabalhar <nome>").

    Returns:
        Tupla com o texto ja colorido e a sua largura visivel em caracteres.
    """
    nome, _, argumentos = comando.partition(" ")
    if argumentos:
        texto = f"{ui.colorir(nome, Cor.VERDE)} {ui.colorir(argumentos, Cor.CIANO)}"
    else:
        texto = ui.colorir(nome, Cor.VERDE)
    return texto, len(comando)


def cmd_ajuda() -> None:
    """Imprime a lista de comandos agrupada por ticket do briefing."""
    largura = max(len(comando) for _, _, comandos in GRUPOS_AJUDA for comando, _ in comandos)

    for titulo, padrao, comandos in GRUPOS_AJUDA:
        etiqueta = f"  {ui.colorir(padrao, Cor.FRACO)}" if padrao else ""
        print(f"\n{ui.colorir(titulo, Cor.NEGRITO + Cor.CIANO)}{etiqueta}")
        for comando, descricao in comandos:
            texto, visivel = _formatar_comando(comando)
            condutor = ui.colorir("·" * (largura - visivel + 3), Cor.FRACO)
            print(f"  {texto} {condutor}  {descricao}")
    print()


def cmd_status(nave: Nave) -> None:
    """Imprime o painel com energia do núcleo, tripulação e arma equipada."""
    nucleo = nave.nucleo
    barra = ui.barra_energia(nucleo.energia_atual, nucleo.energia_maxima)
    cor_estado = Cor.VERMELHO if nucleo.estado == EstadoNucleo.CRITICO else Cor.VERDE
    energia = f"{nucleo.energia_atual}/{nucleo.energia_maxima}".rjust(7)

    ui.titulo_painel("STATUS DA NAVE")
    ui.linha_painel(f"{'Núcleo'.ljust(12)} {barra} {energia}  {ui.colorir(nucleo.estado.value, cor_estado)}")

    arma = nave.arma_atual.descricao if nave.arma_atual else ui.colorir("nenhuma", Cor.FRACO)
    ui.linha_painel(f"{'Armamento'.ljust(12)} {arma}")

    ui.linha_painel("Tripulação")
    if nave.tripulantes:
        for tripulante in nave.tripulantes.values():
            ui.linha_painel(f"   • {tripulante.nome.ljust(10)} {tripulante.funcao_atual}")
    else:
        ui.linha_painel(f"   {ui.colorir('nenhum tripulante a bordo', Cor.FRACO)}")
    ui.fim_painel()


def cmd_tomar_dano(nave: Nave, args: list[str]) -> None:
    """Aplica dano/reducao de energia ao nucleo a partir do valor informado."""
    if not args or not args[0].isdigit():
        ui.erro("Uso: tomar_dano <valor numérico>")
        return
    nave.nucleo.tomar_dano(int(args[0]))
    ui.sucesso(f"Núcleo recebeu {args[0]} de dano. Energia atual: {nave.nucleo.energia_atual}")


def cmd_restaurar_energia(nave: Nave, args: list[str]) -> None:
    """Restaura energia do nucleo a partir do valor informado."""
    if not args or not args[0].isdigit():
        ui.erro("Uso: restaurar_energia <valor numérico>")
        return
    nave.nucleo.restaurar_energia(int(args[0]))
    ui.sucesso(f"Núcleo restaurou {args[0]} de energia. Energia atual: {nave.nucleo.energia_atual}")


def cmd_funcoes() -> None:
    """Lista as funcoes (estrategias) disponiveis para a tripulacao."""
    for chave, classe in FUNCOES_DISPONIVEIS.items():
        print(f"  {ui.colorir(chave.ljust(14), Cor.VERDE)} {classe.nome_funcao}")


def cmd_add_tripulante(nave: Nave, args: list[str]) -> None:
    """Cadastra um novo tripulante com a funcao informada."""
    if len(args) < 2 or args[1] not in FUNCOES_DISPONIVEIS:
        ui.erro(f"Uso: add_tripulante <nome> <função>. Funções: {', '.join(FUNCOES_DISPONIVEIS)}")
        return
    nome, funcao_chave = args[0], args[1]
    funcao = FUNCOES_DISPONIVEIS[funcao_chave]()
    nave.adicionar_tripulante(Tripulante(nome, funcao))
    ui.sucesso(f"{nome} entrou a bordo como {funcao.nome_funcao}.")


def cmd_trocar_funcao(nave: Nave, args: list[str]) -> None:
    """Troca a funcao (estrategia) de um tripulante ja cadastrado, sem recria-lo."""
    if len(args) < 2 or args[1] not in FUNCOES_DISPONIVEIS:
        ui.erro(f"Uso: trocar_funcao <nome> <função>. Funções: {', '.join(FUNCOES_DISPONIVEIS)}")
        return
    tripulante = nave.tripulantes.get(args[0].lower())
    if tripulante is None:
        ui.erro(f"Tripulante '{args[0]}' não encontrado. Use 'add_tripulante' primeiro.")
        return
    funcao_anterior = tripulante.funcao_atual
    tripulante.trocar_funcao(FUNCOES_DISPONIVEIS[args[1]]())
    ui.sucesso(f"{tripulante.nome}: {funcao_anterior} → {tripulante.funcao_atual} (mesmo objeto em memória)")


def cmd_trabalhar(nave: Nave, args: list[str]) -> None:
    """Manda o tripulante executar a acao da sua funcao atual."""
    if not args:
        ui.erro("Uso: trabalhar <nome>")
        return
    tripulante = nave.tripulantes.get(args[0].lower())
    if tripulante is None:
        ui.erro(f"Tripulante '{args[0]}' não encontrado. Use 'add_tripulante' primeiro.")
        return
    ui.fala(tripulante.trabalhar())


def cmd_tripulantes(nave: Nave) -> None:
    """Lista os tripulantes cadastrados e suas funcoes atuais."""
    if not nave.tripulantes:
        ui.erro("Nenhum tripulante a bordo.")
        return
    for tripulante in nave.tripulantes.values():
        print(f"  {ui.colorir('•', Cor.MAGENTA)} {tripulante.nome.ljust(12)} {tripulante.funcao_atual}")


def cmd_armas() -> None:
    """Lista os tipos de arma base disponiveis."""
    for chave, classe in ARMAS_DISPONIVEIS.items():
        print(f"  {ui.colorir(chave.ljust(14), Cor.VERDE)} {classe().descricao}")


def cmd_equipar_arma(nave: Nave, args: list[str]) -> None:
    """Equipa uma arma base nova na nave, descartando modificadores anteriores."""
    if not args or args[0] not in ARMAS_DISPONIVEIS:
        ui.erro(f"Uso: equipar_arma <tipo>. Tipos: {', '.join(ARMAS_DISPONIVEIS)}")
        return
    nave.equipar_arma(ARMAS_DISPONIVEIS[args[0]]())
    ui.sucesso(f"Arma equipada: {nave.arma_atual.descricao}")


def cmd_modificadores() -> None:
    """Lista os modificadores (decoradores) disponiveis."""
    for chave, classe in MODIFICADORES_DISPONIVEIS.items():
        print(f"  {ui.colorir(chave.ljust(14), Cor.VERDE)} {classe.rotulo}")


def cmd_adicionar_modificador(nave: Nave, args: list[str]) -> None:
    """Empilha um modificador (decorator) sobre a arma atualmente equipada."""
    if not args or args[0] not in MODIFICADORES_DISPONIVEIS:
        ui.erro(f"Uso: adicionar_modificador <tipo>. Tipos: {', '.join(MODIFICADORES_DISPONIVEIS)}")
        return
    if nave.arma_atual is None:
        ui.erro("Nenhuma arma equipada. Use 'equipar_arma <tipo>' primeiro.")
        return
    nave.arma_atual = MODIFICADORES_DISPONIVEIS[args[0]](nave.arma_atual)
    ui.sucesso(f"Pilha de disparo: {nave.arma_atual.descricao}")


def cmd_atirar(nave: Nave) -> None:
    """Dispara a arma atualmente equipada, delegando toda a logica a ela."""
    try:
        ui.disparo(nave.atirar())
    except ValueError as erro:
        ui.erro(str(erro))


def executar_comando(nave: Nave, linha: str) -> bool:
    """
    Interpreta e executa uma linha de comando digitada pelo avaliador.

    Args:
        nave: instancia da Nave que concentra os sistemas do desafio.
        linha: texto digitado no console.

    Returns:
        False se o comando for 'sair' (encerra o loop), True caso contrario.
    """
    partes = linha.replace("﻿", "").strip().split()
    if not partes:
        return True
    comando, args = partes[0].lower(), partes[1:]

    if comando in ("sair", "exit", "quit"):
        return False
    if comando in ("ajuda", "help"):
        cmd_ajuda()
    elif comando == "status":
        cmd_status(nave)
    elif comando in ("tomar_dano", "reduzir_energia"):
        cmd_tomar_dano(nave, args)
    elif comando == "restaurar_energia":
        cmd_restaurar_energia(nave, args)
    elif comando == "funcoes":
        cmd_funcoes()
    elif comando == "add_tripulante":
        cmd_add_tripulante(nave, args)
    elif comando == "trocar_funcao":
        cmd_trocar_funcao(nave, args)
    elif comando == "trabalhar":
        cmd_trabalhar(nave, args)
    elif comando == "tripulantes":
        cmd_tripulantes(nave)
    elif comando == "armas":
        cmd_armas()
    elif comando == "equipar_arma":
        cmd_equipar_arma(nave, args)
    elif comando == "modificadores":
        cmd_modificadores()
    elif comando == "adicionar_modificador":
        cmd_adicionar_modificador(nave, args)
    elif comando == "atirar":
        cmd_atirar(nave)
    else:
        ui.erro(f"Comando desconhecido: '{comando}'. Digite 'ajuda' para ver os comandos.")
    return True


def main() -> None:
    """Inicializa a Nave e mantem o loop interativo de leitura de comandos."""
    ui.preparar_saida()
    nave = Nave()
    ui.cabecalho()
    cmd_ajuda()

    continuar = True
    while continuar:
        try:
            linha = input(ui.prompt())
        except (EOFError, KeyboardInterrupt):
            print()
            break
        continuar = executar_comando(nave, linha)
    print(ui.colorir("Console encerrado. Até a próxima missão!", Cor.CIANO))


if __name__ == "__main__":
    main()
