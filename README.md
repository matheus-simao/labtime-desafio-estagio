# LabTIME - Desafio Técnico de Estágio

Solução do desafio técnico "Primeiro Dia no Laboratório": sistema da nave espacial
implementado em Python puro (biblioteca padrão apenas), com um console interativo
para testar os três tickets propostos pelo Tech Lead.

## 1. Mapeamento e Justificativa dos Padrões

### Ticket 1 — Sistema de Contingência do Núcleo → **Observer**

**Restrição:** o Núcleo não pode conhecer/chamar diretamente Escudos, Luzes ou
Painéis, e novas reações (ex: Suporte de Vida) devem poder ser adicionadas sem
tocar na classe do Núcleo.

Isso é exatamente o problema que o **Observer** resolve: o Núcleo (Subject) mantém
apenas uma lista de objetos que implementam uma interface genérica de observador e
os notifica quando seu estado muda — sem nunca importar ou referenciar uma classe
concreta como `SistemaEscudos`. Para adicionar "Suporte de Vida" no futuro, basta
criar uma nova classe que implemente `ObservadorNucleo` e registrá-la; nenhuma
linha de `NucleoEnergia` precisa mudar.

### Ticket 2 — Comportamento Dinâmico da Tripulação → **Strategy**

**Restrição:** proibido destruir/recriar o tripulante para mudar de função, e
proibido usar blocos gigantes de `if/else`/`switch` para decidir a lógica; as
regras de cada função devem ser isoladas e trocáveis em tempo real.

O **Strategy** encaixa porque cada função (canhoneiro, mecânico, médico) vira uma
classe independente com a mesma interface (`FuncaoStrategy`), e o `Tripulante`
apenas guarda uma referência a essa estratégia e delega o trabalho a ela. Trocar
de função é apenas trocar o objeto guardado (`trocar_funcao`) — o `Tripulante`
nunca é destruído, e a classe `Tripulante` nunca precisa saber o que cada função
faz internamente.

### Ticket 3 — Armamento Modular e Modificadores Piratas → **Strategy + Decorator**

**Restrição:** a Nave só pode emitir o comando genérico "atirar" sem conhecer a
física de cada arma; os modificadores devem poder se empilhar dinamicamente sem
uma classe nova para cada combinação possível.

Duas restrições, dois padrões trabalhando juntos, ambos sob a mesma interface `Arma`:

- **Strategy** resolve a escolha da arma base: `Nave.atirar()` delega para
  `self.arma_atual.atirar()` sem saber se é um Laser Contínuo ou um Enxame de
  Mísseis.
- **Decorator** resolve o empilhamento de modificadores: `DanoDeFogo` e
  `PerfuracaoDeBlindagem` embrulham a arma atual (que pode já estar decorada),
  adicionando um efeito e repassando a chamada adiante. Isso evita a explosão
  combinatória de classes como `LaserComFogoEPerfuracao`.

## 2. Papéis do Código

```
labtime-desafio-estagio/
├── main.py                 # loop interativo de comandos (ponto de entrada)
├── README.md
└── sistema/
    ├── nucleo.py           # Ticket 1 · Observer
    ├── tripulante.py       # Ticket 2 · Strategy
    ├── armas.py            # Ticket 3 · Strategy + Decorator
    ├── nave.py             # integra os três sistemas
    └── ui.py               # apresentação no terminal (sem lógica de padrões)
```

| Arquivo | Padrão | Papel |
|---|---|---|
| `sistema/nucleo.py` | Observer | `ObservadorNucleo` = interface Observer; `SistemaEscudos`, `SistemaLuzes`, `PainelNavegacao` = observadores concretos; `NucleoEnergia` = Subject |
| `sistema/tripulante.py` | Strategy | `FuncaoStrategy` = interface da estratégia; `OperadorCanhoes`, `MecanicoMotor`, `MedicoDeBordo` = estratégias concretas; `Tripulante` = Context |
| `sistema/armas.py` | Strategy + Decorator | `Arma` = interface comum (estratégia); `LaserContinuo`, `EnxameDeMisseis` = estratégias concretas (armas base); `ModificadorArma` = Decorator base; `DanoDeFogo`, `PerfuracaoDeBlindagem` = decoradores concretos |
| `sistema/nave.py` | — | `Nave` = fachada que integra os três sistemas acima, usada pelo console |
| `sistema/ui.py` | — | Camada de apresentação do terminal (cores ANSI, painéis, barra de energia), isolada da lógica dos padrões |
| `main.py` | — | Loop interativo de leitura de comandos no terminal |

## 3. Instruções de Execução

Requisitos: Python 3.10+ (usa apenas a biblioteca padrão, sem dependências externas).

```bash
git clone https://github.com/matheus-simao/labtime-desafio-estagio.git
cd labtime-desafio-estagio
python main.py
```

No Windows, se `python` não estiver no PATH, use `py main.py` ou `python3 main.py`.
O programa precisa ser executado a partir da raiz do repositório.

Ao iniciar, o console mostra a lista de comandos (também disponível a qualquer
momento digitando `ajuda`). Uma sessão que exercita os três tickets:

```
nave › tomar_dano 80                   # Ticket 1: dispara os três observers
nave › status
nave › restaurar_energia 60            # Ticket 1: observers reagem à normalização
nave › add_tripulante Ana canhoneiro   # Ticket 2
nave › trabalhar Ana
nave › trocar_funcao Ana mecanico      # Ticket 2: troca sem recriar o objeto
nave › trabalhar Ana
nave › equipar_arma laser              # Ticket 3
nave › adicionar_modificador fogo      # Ticket 3: empilha o 1º decorator
nave › adicionar_modificador perfuracao  # empilha o 2º sobre o 1º
nave › atirar
nave › sair
```

### Duas formas de usar cada comando

Os trechos entre `< >` na tabela abaixo são valores que você escolhe — os sinais
não devem ser digitados. Todo comando aceita duas formas de uso:

```
nave › tomar_dano 40                  # informando o valor direto
```

```
nave › tomar_dano                     # ou deixando o console perguntar
  ? Quanto de dano? › 40
```

O mesmo vale para tripulantes, armas e modificadores, que apresentam as opções
válidas no próprio prompt. Um Enter vazio cancela a operação.

### Comandos disponíveis

**Núcleo de energia — Ticket 1 (Observer)**

| Comando | Descrição |
|---|---|
| `tomar_dano <valor>` | reduz a energia do núcleo |
| `reduzir_energia <valor>` | sinônimo de `tomar_dano` |
| `restaurar_energia <valor>` | recupera energia do núcleo |

**Tripulação — Ticket 2 (Strategy)**

| Comando | Descrição |
|---|---|
| `add_tripulante <nome> <função>` | adiciona um tripulante |
| `trocar_funcao <nome> <função>` | troca a função de um tripulante vivo |
| `trabalhar <nome>` | executa a função atual do tripulante |
| `tripulantes` | lista os tripulantes cadastrados |
| `funcoes` | lista as funções disponíveis (`canhoneiro`, `mecanico`, `medico`) |

**Armamento — Ticket 3 (Strategy + Decorator)**

| Comando | Descrição |
|---|---|
| `equipar_arma <tipo>` | equipa uma arma base (`laser`, `misseis`) |
| `adicionar_modificador <tipo>` | empilha um modificador (`fogo`, `perfuracao`) |
| `atirar` | dispara a arma equipada |
| `armas` | lista as armas disponíveis |
| `modificadores` | lista os modificadores disponíveis |

**Geral**

| Comando | Descrição |
|---|---|
| `status` | painel com energia do núcleo, tripulação e pilha de disparo |
| `ajuda` | mostra a lista de comandos |
| `sair` | encerra o programa |

### Observação sobre a saída no terminal

O console usa cores ANSI e caracteres de caixa para facilitar a leitura. As cores
são detectadas automaticamente e desligadas quando a saída não é um terminal
(ou quando a variável de ambiente `NO_COLOR` está definida), então o programa
continua legível em qualquer ambiente.
