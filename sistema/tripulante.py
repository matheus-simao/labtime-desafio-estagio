"""
Ticket 2 - Comportamento Dinamico da Tripulacao.

Padrao aplicado: Strategy.

Cada funcao (canhoneiro, mecanico, etc) e uma estrategia concreta que
implementa a interface FuncaoStrategy. O Tripulante (Context) guarda uma
referencia para a estrategia atual e delega o trabalho a ela. Trocar de
funcao em tempo real e apenas trocar o objeto de estrategia guardado no
tripulante - o objeto Tripulante nunca e destruido e a classe nunca
precisa de if/else para decidir qual logica rodar.
"""

from abc import ABC, abstractmethod


class FuncaoStrategy(ABC):
    """Interface (Strategy) para as funcoes que um tripulante pode exercer."""

    nome_funcao: str = "Indefinida"

    @abstractmethod
    def trabalhar(self, nome_tripulante: str) -> str:
        """
        Executa a acao de trabalho especifica da funcao.

        Args:
            nome_tripulante: nome do tripulante que esta executando a acao.

        Returns:
            Mensagem descrevendo o resultado do trabalho realizado.
        """
        raise NotImplementedError


class OperadorCanhoes(FuncaoStrategy):
    """Estrategia concreta: tripulante operando os canhoes da nave."""

    nome_funcao = "operador de canhões"

    def trabalhar(self, nome_tripulante: str) -> str:
        """Descreve a acao de mirar e disparar os canhoes."""
        return f"{nome_tripulante} mira os canhões e aguarda a ordem de disparo."


class MecanicoMotor(FuncaoStrategy):
    """Estrategia concreta: tripulante fazendo manutencao do motor."""

    nome_funcao = "mecânico do motor"

    def trabalhar(self, nome_tripulante: str) -> str:
        """Descreve a acao de reparo no motor."""
        return f"{nome_tripulante} ajusta as válvulas e repara o motor da nave."


class MedicoDeBordo(FuncaoStrategy):
    """Estrategia concreta: tripulante cuidando da enfermaria."""

    nome_funcao = "médico de bordo"

    def trabalhar(self, nome_tripulante: str) -> str:
        """Descreve a acao de atendimento medico."""
        return f"{nome_tripulante} verifica os sinais vitais da tripulação na enfermaria."


FUNCOES_DISPONIVEIS: dict[str, type[FuncaoStrategy]] = {
    "canhoneiro": OperadorCanhoes,
    "mecanico": MecanicoMotor,
    "medico": MedicoDeBordo,
}


class Tripulante:
    """
    Context do padrao Strategy. Representa um NPC da tripulacao.

    Guarda uma referencia a estrategia de funcao atual e delega a ela a
    execucao do trabalho, permitindo trocar de funcao em tempo real sem
    recriar o objeto e sem condicionais gigantes.
    """

    def __init__(self, nome: str, funcao_inicial: FuncaoStrategy) -> None:
        """
        Cria o tripulante ja associado a uma estrategia de funcao.

        Args:
            nome: nome do tripulante.
            funcao_inicial: estrategia de funcao com a qual o tripulante comeca.
        """
        self._nome = nome
        self._funcao: FuncaoStrategy = funcao_inicial

    @property
    def nome(self) -> str:
        """Retorna o nome do tripulante."""
        return self._nome

    @property
    def funcao_atual(self) -> str:
        """Retorna o nome legivel da funcao atualmente atribuida."""
        return self._funcao.nome_funcao

    def trocar_funcao(self, nova_funcao: FuncaoStrategy) -> None:
        """
        Troca a estrategia de funcao do tripulante em tempo de execucao.

        Args:
            nova_funcao: nova estrategia concreta de FuncaoStrategy.

        Returns:
            None.
        """
        self._funcao = nova_funcao

    def trabalhar(self) -> str:
        """
        Delega a execucao do trabalho para a estrategia de funcao atual.

        Returns:
            Mensagem descrevendo o resultado do trabalho realizado.
        """
        return self._funcao.trabalhar(self._nome)
