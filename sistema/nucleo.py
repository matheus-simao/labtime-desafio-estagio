"""
Ticket 1 - Sistema de Contingencia do Nucleo da Nave.

Padrao aplicado: Observer.

O NucleoEnergia (Subject) nao conhece nenhuma classe concreta que reage as
suas mudancas de estado. Ele apenas mantem uma lista de observadores que
implementam a interface ObservadorNucleo e os notifica quando o estado de
energia muda. Isso permite adicionar novas reacoes (ex: Suporte de Vida)
sem alterar nenhuma linha desta classe.
"""

from abc import ABC, abstractmethod
from enum import Enum

from sistema import ui


class EstadoNucleo(Enum):
    """Estados possiveis do nucleo de energia da nave."""

    NORMAL = "NORMAL"
    CRITICO = "CRÍTICO"


class ObservadorNucleo(ABC):
    """
    Interface (Observer) para qualquer sistema que precise reagir a
    mudancas de estado do nucleo de energia.
    """

    @abstractmethod
    def notificar(self, estado: EstadoNucleo, energia_atual: int) -> None:
        """
        Chamado pelo NucleoEnergia (Subject) sempre que o estado muda.

        Args:
            estado: novo estado do nucleo (NORMAL ou CRITICO).
            energia_atual: valor atual de energia do nucleo.

        Returns:
            None.
        """
        raise NotImplementedError


class NucleoEnergia:
    """
    Subject do padrao Observer. Representa o nucleo de energia da nave.

    Mantem a lista de observadores inscritos e dispara notificacoes quando
    a energia cruza o limiar critico, sem conhecer quem sao esses
    observadores (Escudos, Luzes, Paineis, etc).
    """

    LIMIAR_CRITICO_PERCENTUAL = 0.3

    def __init__(self, energia_maxima: int = 100) -> None:
        """
        Args:
            energia_maxima: capacidade maxima de energia do nucleo.
        """
        self._energia_maxima = energia_maxima
        self._energia_atual = energia_maxima
        self._observadores: list[ObservadorNucleo] = []
        self._estado = EstadoNucleo.NORMAL

    @property
    def energia_atual(self) -> int:
        """Retorna a energia atual do nucleo."""
        return self._energia_atual

    @property
    def energia_maxima(self) -> int:
        """Retorna a capacidade maxima de energia do nucleo."""
        return self._energia_maxima

    @property
    def estado(self) -> EstadoNucleo:
        """Retorna o estado atual do nucleo (NORMAL ou CRITICO)."""
        return self._estado

    def adicionar_observador(self, observador: ObservadorNucleo) -> None:
        """
        Inscreve um novo observador para receber notificacoes do nucleo.

        Args:
            observador: instancia que implementa ObservadorNucleo.

        Returns:
            None.
        """
        self._observadores.append(observador)

    def remover_observador(self, observador: ObservadorNucleo) -> None:
        """
        Remove um observador previamente inscrito.

        Args:
            observador: instancia previamente adicionada.

        Returns:
            None.
        """
        if observador in self._observadores:
            self._observadores.remove(observador)

    def tomar_dano(self, valor: int) -> None:
        """
        Reduz a energia do nucleo em razao de dano sofrido em combate.

        Args:
            valor: quantidade de energia perdida.

        Returns:
            None.
        """
        self._energia_atual = max(0, self._energia_atual - valor)
        self._avaliar_estado()

    def restaurar_energia(self, valor: int) -> None:
        """
        Restaura energia do nucleo (ex: reparo ou recarga).

        Args:
            valor: quantidade de energia recuperada.

        Returns:
            None.
        """
        self._energia_atual = min(self._energia_maxima, self._energia_atual + valor)
        self._avaliar_estado()

    def _avaliar_estado(self) -> None:
        """
        Recalcula o estado do nucleo a partir da energia atual e notifica
        os observadores caso o estado tenha mudado.

        Returns:
            None.
        """
        limiar = self._energia_maxima * self.LIMIAR_CRITICO_PERCENTUAL
        novo_estado = EstadoNucleo.CRITICO if self._energia_atual <= limiar else EstadoNucleo.NORMAL

        if novo_estado != self._estado:
            self._estado = novo_estado
            self._notificar_observadores()

    def _notificar_observadores(self) -> None:
        """
        Notifica todos os observadores inscritos sobre o estado atual.

        Returns:
            None.
        """
        for observador in self._observadores:
            observador.notificar(self._estado, self._energia_atual)


class SistemaEscudos(ObservadorNucleo):
    """Observador concreto: muda o foco de defesa quando o nucleo entra em crise."""

    def __init__(self) -> None:
        self._foco_atual = "PADRAO"

    def notificar(self, estado: EstadoNucleo, energia_atual: int) -> None:
        """Ajusta o foco dos escudos de acordo com o estado do nucleo."""
        if estado == EstadoNucleo.CRITICO:
            self._foco_atual = "EMERGÊNCIA"
            ui.evento("Escudos", "Foco de defesa alterado para EMERGÊNCIA.", critico=True)
        else:
            self._foco_atual = "PADRÃO"
            ui.evento("Escudos", "Foco de defesa restaurado para PADRÃO.", critico=False)


class SistemaLuzes(ObservadorNucleo):
    """Observador concreto: apaga/acende as luzes das salas conforme o estado do nucleo."""

    def notificar(self, estado: EstadoNucleo, energia_atual: int) -> None:
        """Liga ou desliga as luzes de acordo com o estado do nucleo."""
        if estado == EstadoNucleo.CRITICO:
            ui.evento("Luzes", "Luzes das salas APAGADAS para poupar energia.", critico=True)
        else:
            ui.evento("Luzes", "Luzes das salas ACESAS novamente.", critico=False)


class PainelNavegacao(ObservadorNucleo):
    """Observador concreto: exibe ou remove alertas no painel de navegacao."""

    def notificar(self, estado: EstadoNucleo, energia_atual: int) -> None:
        """Exibe ou remove o alerta de emergencia no painel."""
        if estado == EstadoNucleo.CRITICO:
            ui.evento("Painel", f"ALERTA DE EMERGÊNCIA exibido (energia: {energia_atual}).", critico=True)
        else:
            ui.evento("Painel", f"Alerta removido (energia: {energia_atual}).", critico=False)
