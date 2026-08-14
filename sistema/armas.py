"""
Ticket 3 - Armamento Modular e Modificadores Piratas.

Padroes aplicados: Strategy + Decorator.

Strategy: cada arma base (Laser Continuo, Enxame de Misseis) implementa a
mesma interface Arma. A Nave so conhece essa interface e emite o comando
generico de "atirar", sem entender a fisica de disparo de cada fabricante.

Decorator: os modificadores (Dano de Fogo, Perfuracao de Blindagem) sao
decoradores que embrulham uma Arma, acrescentando efeitos ao disparo.
Como cada decorador tambem implementa a interface Arma, eles podem ser
empilhados dinamicamente uns sobre os outros sem que seja necessario
criar uma classe nova para cada combinacao possivel.
"""

from abc import ABC, abstractmethod


class Arma(ABC):
    """Interface (Strategy) comum a todas as armas e a todos os modificadores."""

    @abstractmethod
    def atirar(self) -> str:
        """
        Executa o disparo e descreve o resultado.

        Returns:
            Descricao textual do disparo, incluindo efeitos acumulados.
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def descricao(self) -> str:
        """
        Nome legivel da arma, incluindo a pilha de modificadores aplicados.

        Returns:
            Descricao curta usada no painel de status.
        """
        raise NotImplementedError


class LaserContinuo(Arma):
    """Arma base concreta: feixe de laser continuo."""

    def atirar(self) -> str:
        """Descreve o disparo basico do laser continuo."""
        return "Laser Contínuo disparado (dano base: 10)"

    @property
    def descricao(self) -> str:
        """Retorna o nome legivel da arma base."""
        return "Laser Contínuo"


class EnxameDeMisseis(Arma):
    """Arma base concreta: rajada de misseis teleguiados."""

    def atirar(self) -> str:
        """Descreve o disparo basico do enxame de misseis."""
        return "Enxame de Mísseis disparado (dano base: 25)"

    @property
    def descricao(self) -> str:
        """Retorna o nome legivel da arma base."""
        return "Enxame de Mísseis"


ARMAS_DISPONIVEIS: dict[str, type[Arma]] = {
    "laser": LaserContinuo,
    "misseis": EnxameDeMisseis,
}


class ModificadorArma(Arma):
    """
    Decorator base. Embrulha uma Arma (que pode ser base ou ja decorada)
    e implementa a mesma interface Arma, permitindo empilhamento dinamico.
    """

    rotulo: str = "Modificador"

    def __init__(self, arma_decorada: Arma) -> None:
        """
        Envolve a arma recebida, que pode ser base ou ja decorada.

        Args:
            arma_decorada: instancia de Arma a ser decorada com um efeito extra.
        """
        self._arma_decorada = arma_decorada

    def atirar(self) -> str:
        """Delega o disparo para a arma decorada antes de acrescentar o efeito."""
        return self._arma_decorada.atirar()

    @property
    def descricao(self) -> str:
        """Acrescenta o rotulo deste modificador a descricao da arma decorada."""
        return f"{self._arma_decorada.descricao} + {self.rotulo}"


class DanoDeFogo(ModificadorArma):
    """Decorador concreto: acrescenta dano de fogo ao disparo."""

    rotulo = "Fogo"

    def atirar(self) -> str:
        """Acrescenta o efeito de dano de fogo ao resultado do disparo."""
        resultado = super().atirar()
        return f"{resultado} + Dano de Fogo (queimadura ao longo do tempo)"


class PerfuracaoDeBlindagem(ModificadorArma):
    """Decorador concreto: acrescenta perfuracao de blindagem ao disparo."""

    rotulo = "Perfuração"

    def atirar(self) -> str:
        """Acrescenta o efeito de perfuracao de blindagem ao resultado do disparo."""
        resultado = super().atirar()
        return f"{resultado} + Perfuração de Blindagem (ignora parte da defesa)"


MODIFICADORES_DISPONIVEIS: dict[str, type[ModificadorArma]] = {
    "fogo": DanoDeFogo,
    "perfuracao": PerfuracaoDeBlindagem,
}
