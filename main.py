"""
Ponto de entrada do desafio LabTIME: console interativo do sistema da nave.

Nenhuma saida deste script e pre-programada de forma linear: o loop abaixo
le comandos digitados pelo avaliador e reage dinamicamente, acionando os
padroes de projeto implementados no pacote `sistema`.

Os comandos ficam registrados em uma tabela unica (COMANDOS), a partir da qual
sao gerados tanto a tela de ajuda quanto o despacho das acoes. Isso evita que
a documentacao dos comandos e a execucao deles se desencontrem.

Digite `ajuda` a qualquer momento para ver a lista de comandos.
"""

import difflib
import re
from dataclasses import dataclass, field
from typing import Callable

from sistema import ui
from sistema.armas import ARMAS_DISPONIVEIS, MODIFICADORES_DISPONIVEIS
from sistema.nave import Nave, criar_nave_padrao
from sistema.nucleo import EstadoNucleo, NucleoEnergia
from sistema.tripulante import FUNCOES_DISPONIVEIS, Tripulante
from sistema.ui import Cor


@dataclass(frozen=True)
class Grupo:
    """Agrupamento de comandos exibido na ajuda, associado a um ticket."""

    titulo: str
    resumo: str
    etiqueta: str = ""


GRUPO_NUCLEO = Grupo("NÚCLEO DE ENERGIA", "Núcleo", "Ticket 1 · Observer")
GRUPO_TRIPULACAO = Grupo("TRIPULAÇÃO", "Tripulação", "Ticket 2 · Strategy")
GRUPO_ARMAMENTO = Grupo("ARMAMENTO", "Armamento", "Ticket 3 · Strategy + Decorator")
GRUPO_GERAL = Grupo("GERAL", "Geral")

GRUPOS: tuple[Grupo, ...] = (GRUPO_NUCLEO, GRUPO_TRIPULACAO, GRUPO_ARMAMENTO, GRUPO_GERAL)


@dataclass(frozen=True)
class Comando:
    """
    Um comando do console: sua documentacao e a acao que ele executa.

    Manter os dois lados na mesma estrutura garante que todo comando
    despachavel apareca na ajuda, e vice-versa.
    """

    nome: str
    descricao: str
    grupo: Grupo
    acao: Callable[[Nave, list[str]], None]
    argumentos: str = ""
    apelidos: tuple[str, ...] = ()
    encerra: bool = False

    @property
    def assinatura(self) -> str:
        """Nome do comando seguido dos seus argumentos, como aparece na ajuda."""
        return f"{self.nome} {self.argumentos}".strip()

    @property
    def nomes(self) -> tuple[str, ...]:
        """Todos os nomes aceitos para invocar o comando, incluindo apelidos."""
        return (self.nome, *self.apelidos)


@dataclass(frozen=True)
class Resolucao:
    """
    Resultado da tentativa de identificar qual comando o usuario digitou.

    Apenas um dos tres campos vem preenchido: o comando encontrado, os
    candidatos de um prefixo ambiguo, ou as sugestoes para um nome errado.
    """

    comando: "Comando | None" = None
    ambiguos: list[str] = field(default_factory=list)
    sugestoes: list[str] = field(default_factory=list)


def _converter_inteiro(texto: str) -> int | None:
    """
    Converte um texto digitado em um numero inteiro positivo.

    Aceita variacoes comuns de digitacao, como casas decimais ("65.0") e
    virgula como separador ("65,5").

    Args:
        texto: valor digitado pelo usuario.

    Returns:
        O inteiro correspondente, ou None se o texto nao for um numero valido.
    """
    try:
        valor = float(texto.replace(",", "."))
    except ValueError:
        return None
    if valor <= 0:
        return None
    return int(valor)


def _pedir_numero(pergunta: str) -> int | None:
    """
    Pergunta um numero ao usuario ate receber um valor valido.

    Args:
        pergunta: texto exibido no prompt.

    Returns:
        O numero informado, ou None se o usuario cancelou com Enter vazio.
    """
    while True:
        resposta = ui.perguntar(pergunta)
        if resposta is None or not resposta.strip():
            return None
        valor = _converter_inteiro(resposta)
        if valor is not None:
            return valor
        ui.erro("Informe um número maior que zero (ou tecle Enter para cancelar).")


def _pedir_texto(pergunta: str) -> str | None:
    """
    Pergunta um texto livre ao usuario.

    Args:
        pergunta: texto exibido no prompt.

    Returns:
        O texto informado, ou None se o usuario cancelou com Enter vazio.
    """
    resposta = ui.perguntar(pergunta)
    if resposta is None or not resposta.strip():
        return None
    return resposta.strip()


def _pedir_opcao(pergunta: str, opcoes: dict, rotulos: list[str] | None = None) -> str | None:
    """
    Pergunta ao usuario qual das opcoes disponiveis ele deseja usar.

    Args:
        pergunta: texto exibido no prompt.
        opcoes: dicionario cujas chaves sao as opcoes aceitas.
        rotulos: nomes exibidos ao usuario, quando diferentes das chaves.

    Returns:
        A chave escolhida, ou None se o usuario cancelou com Enter vazio.
    """
    exibidas = ", ".join(rotulos if rotulos is not None else list(opcoes))
    while True:
        resposta = ui.perguntar(f"{pergunta} [{exibidas}]")
        if resposta is None or not resposta.strip():
            return None
        escolha = resposta.strip().lower()
        if escolha in opcoes:
            return escolha
        ui.erro(f"Opção inválida. Use: {exibidas} (ou tecle Enter para cancelar).")


def _resolver_numero(args: list[str], pergunta: str, exemplo: str) -> int | None:
    """
    Obtem um numero do argumento digitado ou, na falta dele, perguntando.

    Concentra o tratamento de erro comum aos comandos que recebem um valor
    numerico, para que cada um deles cuide apenas do seu efeito no nucleo.

    Args:
        args: argumentos que vieram junto ao comando.
        pergunta: texto usado quando o valor precisa ser solicitado.
        exemplo: uso correto, exibido caso o argumento nao seja numerico.

    Returns:
        O numero informado, ou None se invalido ou cancelado - nesse caso a
        mensagem ao usuario ja foi emitida.
    """
    if not args:
        valor = _pedir_numero(pergunta)
        if valor is None:
            ui.aviso("Comando cancelado.")
        return valor

    valor = _converter_inteiro(args[0])
    if valor is None:
        ui.erro(f"'{args[0]}' não é um número válido. Exemplo: {exemplo}")
    return valor


def _resolver_opcao(
    args: list[str], indice: int, opcoes: dict, rotulo: str, pergunta: str
) -> str | None:
    """
    Obtem uma opcao valida do argumento digitado ou, na falta dele, perguntando.

    Serve a todos os comandos que escolhem um item de um catalogo: funcoes de
    tripulante, armas base e modificadores.

    Args:
        args: argumentos que vieram junto ao comando.
        indice: posicao esperada da opcao dentro de args.
        opcoes: dicionario cujas chaves sao as opcoes aceitas.
        rotulo: como o tipo de opcao e chamado na mensagem de erro.
        pergunta: texto usado quando a opcao precisa ser solicitada.

    Returns:
        A chave escolhida, ou None se invalida ou cancelada - nesse caso a
        mensagem ao usuario ja foi emitida.
    """
    if len(args) > indice:
        bruto = args[indice]
        if bruto.lower() not in opcoes:
            ui.erro(f"{rotulo} '{bruto}' não existe. Opções: {', '.join(opcoes)}")
            return None
        return bruto.lower()

    escolha = _pedir_opcao(pergunta, opcoes)
    if escolha is None:
        ui.aviso("Comando cancelado.")
    return escolha


def _formatar_assinatura(assinatura: str) -> tuple[str, int]:
    """
    Colore o nome do comando e seus argumentos de forma distinta.

    Args:
        assinatura: nome do comando seguido dos argumentos.

    Returns:
        Tupla com o texto ja colorido e a sua largura visivel em caracteres.
    """
    nome, _, argumentos = assinatura.partition(" ")
    if argumentos:
        texto = f"{ui.colorir(nome, Cor.VERDE)} {ui.colorir(argumentos, Cor.CIANO)}"
    else:
        texto = ui.colorir(nome, Cor.VERDE)
    return texto, len(assinatura)


def cmd_ajuda(nave: Nave, args: list[str]) -> None:
    """Imprime a lista completa de comandos, agrupada por ticket do briefing."""
    largura = max(len(comando.assinatura) for comando in COMANDOS)

    for grupo in GRUPOS:
        etiqueta = f"  {ui.colorir(grupo.etiqueta, Cor.FRACO)}" if grupo.etiqueta else ""
        print(f"\n{ui.colorir(grupo.titulo, Cor.NEGRITO + Cor.CIANO)}{etiqueta}")
        for comando in COMANDOS:
            if comando.grupo is not grupo:
                continue
            texto, visivel = _formatar_assinatura(comando.assinatura)
            condutor = ui.colorir("·" * (largura - visivel + 3), Cor.FRACO)
            print(f"  {texto} {condutor}  {comando.descricao}")
            if comando.apelidos:
                apelidos = ", ".join(comando.apelidos)
                print(f"  {ui.colorir(f'└ também aceita: {apelidos}', Cor.FRACO)}")

    print(
        "\n"
        + ui.colorir(
            "Os trechos entre < > são valores que você escolhe — não digite os sinais.\n"
            "Pode digitar só o nome do comando que o console pergunta o resto,\n"
            "e abreviar enquanto não ficar ambíguo (atir → atirar).",
            Cor.FRACO,
        )
        + "\n"
    )


def _linha_energia(nucleo: NucleoEnergia) -> str:
    """
    Monta a leitura visual do nucleo: barra, valor e estado.

    Usada tanto no painel de status quanto no retorno dos comandos que
    alteram a energia, para que as duas leituras nunca divirjam.

    Args:
        nucleo: nucleo de energia a ser representado.

    Returns:
        Linha colorida com a barra, a energia atual e o estado.
    """
    barra = ui.barra_energia(nucleo.energia_atual, nucleo.energia_maxima)
    energia = f"{nucleo.energia_atual}/{nucleo.energia_maxima}".rjust(7)
    cor_estado = Cor.VERMELHO if nucleo.estado == EstadoNucleo.CRITICO else Cor.VERDE
    return f"{barra} {energia}  {ui.colorir(nucleo.estado.value, cor_estado)}"


def cmd_status(nave: Nave, args: list[str]) -> None:
    """Imprime o painel com energia do núcleo, tripulação e arma equipada."""
    nucleo = nave.nucleo

    ui.titulo_painel("STATUS DA NAVE")
    ui.linha_painel(f"{'Núcleo'.ljust(12)} {_linha_energia(nucleo)}")

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
    """Aplica dano/reducao de energia ao nucleo, perguntando o valor se necessario."""
    valor = _resolver_numero(args, "Quanto de dano?", "tomar_dano 40")
    if valor is None:
        return
    antes = nave.nucleo.energia_atual
    nave.nucleo.tomar_dano(valor)
    perdido = antes - nave.nucleo.energia_atual
    if perdido == 0:
        ui.aviso("O núcleo já está sem energia. Nada mudou.")
        return
    ui.sucesso(f"Núcleo perdeu {perdido} de energia.")
    print(f"  {_linha_energia(nave.nucleo)}")


def cmd_restaurar_energia(nave: Nave, args: list[str]) -> None:
    """Restaura energia do nucleo, perguntando o valor se necessario."""
    valor = _resolver_numero(args, "Quanta energia restaurar?", "restaurar_energia 30")
    if valor is None:
        return
    antes = nave.nucleo.energia_atual
    nave.nucleo.restaurar_energia(valor)
    ganho = nave.nucleo.energia_atual - antes
    if ganho == 0:
        ui.aviso("O núcleo já está com energia máxima. Nada mudou.")
        return
    ui.sucesso(f"Núcleo recuperou {ganho} de energia.")
    print(f"  {_linha_energia(nave.nucleo)}")


def cmd_add_tripulante(nave: Nave, args: list[str]) -> None:
    """Cadastra um novo tripulante, perguntando nome e funcao se necessario."""
    nome = args[0] if args else _pedir_texto("Nome do tripulante?")
    if nome is None:
        ui.aviso("Comando cancelado.")
        return

    funcao_chave = _resolver_opcao(args, 1, FUNCOES_DISPONIVEIS, "Função", "Qual função?")
    if funcao_chave is None:
        return

    funcao = FUNCOES_DISPONIVEIS[funcao_chave]()
    nave.adicionar_tripulante(Tripulante(nome, funcao))
    ui.sucesso(f"{nome} entrou a bordo como {funcao.nome_funcao}.")


def _resolver_tripulante(nave: Nave, args: list[str], pergunta: str) -> Tripulante | None:
    """
    Localiza um tripulante pelo nome informado, perguntando se necessario.

    Args:
        nave: instancia da Nave com a tripulacao cadastrada.
        args: argumentos digitados junto ao comando.
        pergunta: texto usado caso o nome precise ser solicitado.

    Returns:
        O tripulante encontrado, ou None se cancelado ou inexistente.
    """
    if not nave.tripulantes:
        ui.erro("Nenhum tripulante a bordo. Use 'add_tripulante' primeiro.")
        return None

    nomes = [tripulante.nome for tripulante in nave.tripulantes.values()]
    nome = args[0] if args else _pedir_opcao(pergunta, nave.tripulantes, nomes)
    if nome is None:
        ui.aviso("Comando cancelado.")
        return None

    tripulante = nave.tripulantes.get(nome.lower())
    if tripulante is None:
        ui.erro(f"Tripulante '{nome}' não encontrado. A bordo: {', '.join(nomes)}")
    return tripulante


def cmd_trocar_funcao(nave: Nave, args: list[str]) -> None:
    """Troca a funcao (estrategia) de um tripulante ja cadastrado, sem recria-lo."""
    tripulante = _resolver_tripulante(nave, args, "Qual tripulante?")
    if tripulante is None:
        return

    funcao_chave = _resolver_opcao(args, 1, FUNCOES_DISPONIVEIS, "Função", "Nova função?")
    if funcao_chave is None:
        return

    funcao_anterior = tripulante.funcao_atual
    tripulante.trocar_funcao(FUNCOES_DISPONIVEIS[funcao_chave]())
    ui.sucesso(f"{tripulante.nome}: {funcao_anterior} → {tripulante.funcao_atual} (mesmo objeto em memória)")


def cmd_trabalhar(nave: Nave, args: list[str]) -> None:
    """Manda o tripulante executar a acao da sua funcao atual."""
    tripulante = _resolver_tripulante(nave, args, "Quem deve trabalhar?")
    if tripulante is None:
        return
    ui.fala(tripulante.trabalhar())


def cmd_equipar_arma(nave: Nave, args: list[str]) -> None:
    """Equipa uma arma base nova na nave, descartando modificadores anteriores."""
    chave = _resolver_opcao(args, 0, ARMAS_DISPONIVEIS, "Arma", "Qual arma?")
    if chave is None:
        return
    nave.equipar_arma(ARMAS_DISPONIVEIS[chave]())
    ui.sucesso(f"Arma equipada: {nave.arma_atual.descricao}")


def cmd_adicionar_modificador(nave: Nave, args: list[str]) -> None:
    """Empilha um modificador (decorator) sobre a arma atualmente equipada."""
    if nave.arma_atual is None:
        ui.erro("Nenhuma arma equipada. Use 'equipar_arma' primeiro.")
        return
    chave = _resolver_opcao(args, 0, MODIFICADORES_DISPONIVEIS, "Modificador", "Qual modificador?")
    if chave is None:
        return
    nave.arma_atual = MODIFICADORES_DISPONIVEIS[chave](nave.arma_atual)
    ui.sucesso(f"Pilha de disparo: {nave.arma_atual.descricao}")


def cmd_atirar(nave: Nave, args: list[str]) -> None:
    """Dispara a arma atualmente equipada, delegando toda a logica a ela."""
    try:
        ui.disparo(nave.atirar())
    except ValueError as erro:
        ui.erro(str(erro))


def cmd_sair(nave: Nave, args: list[str]) -> None:
    """
    Encerra o console.

    Nao executa nenhuma acao: quem interrompe o loop principal e a flag
    `encerra` do proprio comando, lida em executar_comando.
    """


COMANDOS: tuple[Comando, ...] = (
    Comando(
        nome="tomar_dano",
        argumentos="<valor>",
        descricao="reduz a energia do núcleo",
        grupo=GRUPO_NUCLEO,
        acao=cmd_tomar_dano,
        apelidos=("reduzir_energia",),
    ),
    Comando(
        nome="restaurar_energia",
        argumentos="<valor>",
        descricao="recupera energia do núcleo",
        grupo=GRUPO_NUCLEO,
        acao=cmd_restaurar_energia,
    ),
    Comando(
        nome="trabalhar",
        argumentos="<nome>",
        descricao="executa a função atual do tripulante",
        grupo=GRUPO_TRIPULACAO,
        acao=cmd_trabalhar,
    ),
    Comando(
        nome="trocar_funcao",
        argumentos="<nome> <função>",
        descricao="troca a função de um tripulante vivo",
        grupo=GRUPO_TRIPULACAO,
        acao=cmd_trocar_funcao,
    ),
    Comando(
        nome="add_tripulante",
        argumentos="<nome> <função>",
        descricao="traz um novo tripulante a bordo",
        grupo=GRUPO_TRIPULACAO,
        acao=cmd_add_tripulante,
    ),
    Comando(
        nome="equipar_arma",
        argumentos="<tipo>",
        descricao="equipa uma arma base na nave",
        grupo=GRUPO_ARMAMENTO,
        acao=cmd_equipar_arma,
    ),
    Comando(
        nome="adicionar_modificador",
        argumentos="<tipo>",
        descricao="empilha um modificador na arma",
        grupo=GRUPO_ARMAMENTO,
        acao=cmd_adicionar_modificador,
    ),
    Comando(
        nome="atirar",
        descricao="dispara a arma equipada",
        grupo=GRUPO_ARMAMENTO,
        acao=cmd_atirar,
    ),
    Comando(
        nome="status",
        descricao="mostra o painel completo da nave",
        grupo=GRUPO_GERAL,
        acao=cmd_status,
    ),
    Comando(
        nome="ajuda",
        descricao="mostra a lista detalhada de comandos",
        grupo=GRUPO_GERAL,
        acao=cmd_ajuda,
        apelidos=("help",),
    ),
    Comando(
        nome="sair",
        descricao="encerra o programa",
        grupo=GRUPO_GERAL,
        acao=cmd_sair,
        apelidos=("exit", "quit"),
        encerra=True,
    ),
)

INDICE_COMANDOS: dict[str, Comando] = {
    nome: comando for comando in COMANDOS for nome in comando.nomes
}


def resolver_comando(entrada: str) -> Resolucao:
    """
    Descobre a qual comando corresponde o texto digitado.

    A busca segue esta ordem: nome exato (ou apelido), prefixo unico e, por
    fim, nomes parecidos. Um prefixo que sirva a mais de um comando nunca e
    adivinhado - os candidatos sao devolvidos para que o usuario escolha.

    Args:
        entrada: primeira palavra digitada pelo usuario, em minusculas.

    Returns:
        Uma Resolucao com o comando encontrado, os candidatos ambiguos ou
        as sugestoes de correcao.
    """
    exato = INDICE_COMANDOS.get(entrada)
    if exato is not None:
        return Resolucao(comando=exato)

    prefixados = sorted({
        comando.nome
        for comando in COMANDOS
        for nome in comando.nomes
        if nome.startswith(entrada)
    })
    if len(prefixados) == 1:
        return Resolucao(comando=INDICE_COMANDOS[prefixados[0]])
    if prefixados:
        return Resolucao(ambiguos=prefixados)

    parecidos = difflib.get_close_matches(entrada, list(INDICE_COMANDOS), n=3, cutoff=0.6)
    return Resolucao(sugestoes=parecidos)


def executar_comando(nave: Nave, linha: str) -> bool:
    """
    Interpreta e executa uma linha de comando digitada pelo avaliador.

    Args:
        nave: instancia da Nave que concentra os sistemas do desafio.
        linha: texto digitado no console.

    Returns:
        False se o comando encerra o console, True caso contrario.
    """
    limpa = re.sub(r"\s*<([^>]*)>", r" \1", linha.replace("﻿", ""))
    partes = limpa.strip().split()
    if not partes:
        return True

    entrada, args = partes[0].lower(), partes[1:]
    resolucao = resolver_comando(entrada)

    if resolucao.comando is None:
        if resolucao.ambiguos:
            ui.erro(f"'{entrada}' pode ser vários comandos: {', '.join(resolucao.ambiguos)}")
        elif resolucao.sugestoes:
            ui.erro(f"Comando '{entrada}' não existe. Você quis dizer: {', '.join(resolucao.sugestoes)}?")
        else:
            ui.erro(f"Comando '{entrada}' não existe. Digite 'ajuda' para ver a lista.")
        return True

    resolucao.comando.acao(nave, args)
    return not resolucao.comando.encerra


def mostrar_resumo() -> None:
    """Imprime o resumo compacto dos comandos, um grupo por linha."""
    for grupo in GRUPOS:
        nomes = " · ".join(comando.nome for comando in COMANDOS if comando.grupo is grupo)
        print(f"  {ui.colorir(grupo.resumo.ljust(11), Cor.CIANO)} {nomes}")

    print(
        "\n"
        + ui.colorir(
            "Digite só o nome do comando que o console pergunta o resto. "
            "Abreviações funcionam (atir → atirar).\n"
            "Use 'ajuda' para a lista detalhada.",
            Cor.FRACO,
        )
    )


def main() -> None:
    """Inicializa a Nave e mantem o loop interativo de leitura de comandos."""
    ui.preparar_saida()
    nave = criar_nave_padrao()

    ui.cabecalho()
    cmd_status(nave, [])
    print()
    mostrar_resumo()
    print()

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
