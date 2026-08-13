"""
Ticket 1 - Sistemas de bordo que reagem ao estado do nucleo de energia.

Estes sao os Observers concretos do padrao Observer. Eles vivem em um modulo
separado do Subject de proposito: a dependencia e sempre deste modulo para o
nucleo, nunca o contrario. O modulo `sistema.nucleo` nao importa nada daqui,
o que torna explicita a restricao arquitetural do Ticket 1 - a classe do
Nucleo nao conhece, nao referencia e nao chama Escudos, Luzes ou Paineis.

Para atender a uma nova demanda de contingencia basta acrescentar aqui outra
classe que implemente ObservadorNucleo e inscreve-la na Nave.
"""

from sistema import ui
from sistema.nucleo import EstadoNucleo, ObservadorNucleo


class SistemaEscudos(ObservadorNucleo):
    """Observador concreto: muda o foco de defesa quando o nucleo entra em crise."""

    def notificar(self, estado: EstadoNucleo, energia_atual: int) -> None:
        """Ajusta o foco dos escudos de acordo com o estado do nucleo."""
        if estado == EstadoNucleo.CRITICO:
            ui.evento("Escudos", "Foco de defesa alterado para EMERGÊNCIA.", critico=True)
        else:
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


class SuporteDeVida(ObservadorNucleo):
    """
    Observador concreto: corta o suporte de vida para o modo de reserva.

    Esta e a demanda futura citada pelo Tech Lead no Ticket 1. Ela foi
    atendida criando esta classe e inscrevendo-a na Nave, sem alterar uma
    linha sequer de NucleoEnergia.
    """

    def notificar(self, estado: EstadoNucleo, energia_atual: int) -> None:
        """Alterna o suporte de vida entre modo de reserva e operacao plena."""
        if estado == EstadoNucleo.CRITICO:
            ui.evento("Suporte de Vida", "Reduzido ao MÍNIMO: reserva de oxigênio ativada.", critico=True)
        else:
            ui.evento("Suporte de Vida", "Restabelecido em operação plena.", critico=False)
