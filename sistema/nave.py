"""
Classe Nave: integra os tres sistemas do briefing (nucleo/observers,
tripulacao/strategy, armamento/strategy+decorator).

A Nave e apenas o ponto de fachada usado pelo console para acionar cada
sistema; ela nao contem a logica interna de nenhum dos padroes.
"""

from sistema.armas import Arma, LaserContinuo
from sistema.nucleo import NucleoEnergia
from sistema.sistemas_bordo import PainelNavegacao, SistemaEscudos, SistemaLuzes
from sistema.tripulante import MecanicoMotor, OperadorCanhoes, Tripulante


class Nave:
    """Agrega o nucleo de energia, a tripulacao e a arma atualmente equipada."""

    def __init__(self) -> None:
        """
        Monta a nave e inscreve os sistemas de bordo no nucleo de energia.

        E aqui, e apenas aqui, que os sistemas reativos sao ligados ao nucleo.
        Para atender a uma nova demanda de contingencia (ex: Suporte de Vida),
        basta acrescentar outra chamada a adicionar_observador, sem tocar em
        NucleoEnergia.
        """
        self.nucleo = NucleoEnergia(energia_maxima=100)
        self.nucleo.adicionar_observador(SistemaEscudos())
        self.nucleo.adicionar_observador(SistemaLuzes())
        self.nucleo.adicionar_observador(PainelNavegacao())

        self.tripulantes: dict[str, Tripulante] = {}
        self.arma_atual: Arma | None = None

    def adicionar_tripulante(self, tripulante: Tripulante) -> None:
        """
        Registra um novo tripulante na nave.

        Args:
            tripulante: instancia de Tripulante a ser adicionada.

        Returns:
            None.
        """
        self.tripulantes[tripulante.nome.lower()] = tripulante

    def equipar_arma(self, arma: Arma) -> None:
        """
        Equipa a arma que sera usada nos proximos disparos.

        Args:
            arma: instancia de Arma (base ou ja decorada com modificadores).

        Returns:
            None.
        """
        self.arma_atual = arma

    def atirar(self) -> str:
        """
        Emite o comando generico de disparo. A Nave nao sabe qual arma
        esta equipada nem como ela funciona internamente, apenas delega.

        Returns:
            Descricao do disparo realizado.

        Raises:
            ValueError: se nenhuma arma estiver equipada.
        """
        if self.arma_atual is None:
            raise ValueError("Nenhuma arma equipada. Use 'equipar_arma' primeiro.")
        return self.arma_atual.atirar()


def criar_nave_padrao() -> Nave:
    """
    Monta a nave usada na demonstracao, ja com tripulacao e armamento.

    A Nave em si nasce generica; e esta funcao que define o cenario inicial,
    para que o avaliador possa usar comandos como `trabalhar` e `atirar` logo
    na primeira interacao, sem precisar cadastrar nada antes.

    Returns:
        Uma Nave com dois tripulantes a bordo e o laser equipado.
    """
    nave = Nave()
    nave.adicionar_tripulante(Tripulante("Ana", OperadorCanhoes()))
    nave.adicionar_tripulante(Tripulante("Bruno", MecanicoMotor()))
    nave.equipar_arma(LaserContinuo())
    return nave
