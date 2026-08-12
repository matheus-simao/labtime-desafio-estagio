"""
Ponto de entrada do desafio LabTIME: console interativo do sistema da nave.

Nenhuma saida deste script e pre-programada de forma linear: o loop abaixo
le comandos digitados pelo avaliador e reage dinamicamente, acionando os
padroes de projeto implementados no pacote `sistema`.

Digite `ajuda` a qualquer momento para ver a lista de comandos.
"""

from sistema.armas import ARMAS_DISPONIVEIS, MODIFICADORES_DISPONIVEIS
from sistema.nave import Nave
from sistema.tripulante import FUNCOES_DISPONIVEIS, Tripulante

AJUDA = """
Comandos disponiveis:
  ajuda                                 - mostra esta lista de comandos
  status                                - mostra energia/estado do nucleo, tripulacao e arma
  tomar_dano <valor>                    - reduz a energia do nucleo (ex: tomar_dano 40)
  reduzir_energia <valor>               - sinonimo de tomar_dano
  restaurar_energia <valor>             - aumenta a energia do nucleo

  funcoes                               - lista as funcoes disponiveis para a tripulacao
  add_tripulante <nome> <funcao>        - adiciona um tripulante (ex: add_tripulante Ana canhoneiro)
  trocar_funcao <nome> <nova_funcao>    - troca a funcao de um tripulante vivo
  trabalhar <nome>                      - manda o tripulante executar a funcao atual
  tripulantes                           - lista os tripulantes cadastrados

  armas                                 - lista os tipos de arma disponiveis
  equipar_arma <tipo>                   - equipa uma arma base na nave (ex: equipar_arma laser)
  modificadores                         - lista os modificadores disponiveis
  adicionar_modificador <tipo>          - empilha um modificador na arma equipada
  atirar                                - dispara a arma atualmente equipada

  sair                                  - encerra o programa
"""


def cmd_status(nave: Nave) -> None:
    """Imprime o estado atual do nucleo, da tripulacao e da arma equipada."""
    print(f"Nucleo: {nave.nucleo.energia_atual} de energia | estado: {nave.nucleo.estado.value}")
    if nave.tripulantes:
        for tripulante in nave.tripulantes.values():
            print(f"  - {tripulante.nome}: {tripulante.funcao_atual}")
    else:
        print("  (nenhum tripulante cadastrado)")
    if nave.arma_atual is not None:
        print("Arma equipada: pronta para disparo (use 'atirar' para ver o efeito atual)")
    else:
        print("Arma equipada: nenhuma")


def cmd_tomar_dano(nave: Nave, args: list[str]) -> None:
    """Aplica dano/reducao de energia ao nucleo a partir do valor informado."""
    if not args or not args[0].isdigit():
        print("Uso: tomar_dano <valor numerico>")
        return
    nave.nucleo.tomar_dano(int(args[0]))
    print(f"Nucleo recebeu {args[0]} de dano. Energia atual: {nave.nucleo.energia_atual}")


def cmd_restaurar_energia(nave: Nave, args: list[str]) -> None:
    """Restaura energia do nucleo a partir do valor informado."""
    if not args or not args[0].isdigit():
        print("Uso: restaurar_energia <valor numerico>")
        return
    nave.nucleo.restaurar_energia(int(args[0]))
    print(f"Nucleo restaurou {args[0]} de energia. Energia atual: {nave.nucleo.energia_atual}")


def cmd_funcoes() -> None:
    """Lista as funcoes (estrategias) disponiveis para a tripulacao."""
    print("Funcoes disponiveis:", ", ".join(FUNCOES_DISPONIVEIS.keys()))


def cmd_add_tripulante(nave: Nave, args: list[str]) -> None:
    """Cadastra um novo tripulante com a funcao informada."""
    if len(args) < 2 or args[1] not in FUNCOES_DISPONIVEIS:
        print(f"Uso: add_tripulante <nome> <funcao>. Funcoes: {', '.join(FUNCOES_DISPONIVEIS.keys())}")
        return
    nome, funcao_chave = args[0], args[1]
    funcao = FUNCOES_DISPONIVEIS[funcao_chave]()
    nave.adicionar_tripulante(Tripulante(nome, funcao))
    print(f"Tripulante {nome} adicionado como {funcao.nome_funcao}.")


def cmd_trocar_funcao(nave: Nave, args: list[str]) -> None:
    """Troca a funcao (estrategia) de um tripulante ja cadastrado, sem recria-lo."""
    if len(args) < 2 or args[1] not in FUNCOES_DISPONIVEIS:
        print(f"Uso: trocar_funcao <nome> <nova_funcao>. Funcoes: {', '.join(FUNCOES_DISPONIVEIS.keys())}")
        return
    tripulante = nave.tripulantes.get(args[0].lower())
    if tripulante is None:
        print(f"Tripulante '{args[0]}' nao encontrado. Use 'add_tripulante' primeiro.")
        return
    nova_funcao = FUNCOES_DISPONIVEIS[args[1]]()
    tripulante.trocar_funcao(nova_funcao)
    print(f"{tripulante.nome} agora e {tripulante.funcao_atual}.")


def cmd_trabalhar(nave: Nave, args: list[str]) -> None:
    """Manda o tripulante executar a acao da sua funcao atual."""
    if not args:
        print("Uso: trabalhar <nome>")
        return
    tripulante = nave.tripulantes.get(args[0].lower())
    if tripulante is None:
        print(f"Tripulante '{args[0]}' nao encontrado. Use 'add_tripulante' primeiro.")
        return
    print(tripulante.trabalhar())


def cmd_tripulantes(nave: Nave) -> None:
    """Lista os tripulantes cadastrados e suas funcoes atuais."""
    if not nave.tripulantes:
        print("Nenhum tripulante cadastrado.")
        return
    for tripulante in nave.tripulantes.values():
        print(f"  - {tripulante.nome}: {tripulante.funcao_atual}")


def cmd_armas() -> None:
    """Lista os tipos de arma base disponiveis."""
    print("Armas disponiveis:", ", ".join(ARMAS_DISPONIVEIS.keys()))


def cmd_equipar_arma(nave: Nave, args: list[str]) -> None:
    """Equipa uma arma base nova na nave, descartando modificadores anteriores."""
    if not args or args[0] not in ARMAS_DISPONIVEIS:
        print(f"Uso: equipar_arma <tipo>. Tipos: {', '.join(ARMAS_DISPONIVEIS.keys())}")
        return
    nave.equipar_arma(ARMAS_DISPONIVEIS[args[0]]())
    print(f"Arma '{args[0]}' equipada.")


def cmd_modificadores() -> None:
    """Lista os modificadores (decoradores) disponiveis."""
    print("Modificadores disponiveis:", ", ".join(MODIFICADORES_DISPONIVEIS.keys()))


def cmd_adicionar_modificador(nave: Nave, args: list[str]) -> None:
    """Empilha um modificador (decorator) sobre a arma atualmente equipada."""
    if not args or args[0] not in MODIFICADORES_DISPONIVEIS:
        print(f"Uso: adicionar_modificador <tipo>. Tipos: {', '.join(MODIFICADORES_DISPONIVEIS.keys())}")
        return
    if nave.arma_atual is None:
        print("Nenhuma arma equipada. Use 'equipar_arma <tipo>' primeiro.")
        return
    nave.arma_atual = MODIFICADORES_DISPONIVEIS[args[0]](nave.arma_atual)
    print(f"Modificador '{args[0]}' adicionado a arma equipada.")


def cmd_atirar(nave: Nave) -> None:
    """Dispara a arma atualmente equipada, delegando toda a logica a ela."""
    try:
        print(nave.atirar())
    except ValueError as erro:
        print(erro)


def executar_comando(nave: Nave, linha: str) -> bool:
    """
    Interpreta e executa uma linha de comando digitada pelo avaliador.

    Args:
        nave: instancia da Nave que concentra os sistemas do desafio.
        linha: texto digitado no console.

    Returns:
        False se o comando for 'sair' (encerra o loop), True caso contrario.
    """
    partes = linha.strip().split()
    if not partes:
        return True
    comando, args = partes[0].lower(), partes[1:]

    if comando in ("sair", "exit", "quit"):
        return False
    if comando in ("ajuda", "help"):
        print(AJUDA)
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
        print(f"Comando desconhecido: '{comando}'. Digite 'ajuda' para ver os comandos.")
    return True


def main() -> None:
    """Inicializa a Nave e mantem o loop interativo de leitura de comandos."""
    nave = Nave()
    print("=== Sistema da Nave - Console Interativo ===")
    print(AJUDA)
    continuar = True
    while continuar:
        try:
            linha = input("> ")
        except EOFError:
            break
        continuar = executar_comando(nave, linha)
    print("Encerrando console. Ate a proxima missao!")


if __name__ == "__main__":
    main()
