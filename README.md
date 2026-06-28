# NCE0144 — Trabalho Final de Grafos
## Dataset D6 — Rede de Personagens de *Dom Casmurro*

> Machado de Assis, 1899  
> Disciplina: Algoritmos e Estruturas de Dados II  
> Dataset: D6 (grafo não-dirigido, ponderado)

---

## Estrutura do repositório

```
/
├── grafo_dom_casmurro.py          # Código principal — todos os algoritmos
├── D6_dom_casmurro.csv            # Arestas: Source, Target, Weight
├── D6_dom_casmurro_nodes.csv      # Nós: Id, Label
└── README.md                      # Este arquivo
```

---

## Como executar

**Pré-requisito:** Python 3.8 ou superior — nenhuma biblioteca externa necessária.

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/nome-do-repo.git
cd nome-do-repo

# 2. Execute o script principal
python3 grafo_dom_casmurro.py
```

Os arquivos CSV precisam estar na **mesma pasta** do script.

---

## Sobre a rede

| Propriedade     | Valor                          |
|-----------------|-------------------------------|
| Tipo            | Não-dirigido, ponderado        |
| Vértices \|V\|  | 18 personagens                 |
| Arestas \|E\|   | 32 únicas (CSV tem 34 linhas)  |
| Grau médio      | 3.56                           |
| Conexo          | Sim                            |
| Possui ciclos   | Sim                            |
| Hub principal   | Bentinho (grau 11)             |

O peso de cada aresta representa a **frequência de interações** entre
os dois personagens ao longo do texto de Dom Casmurro.

---

## Algoritmos implementados

Todos implementados **do zero**, sem NetworkX, igraph ou similares.

| Algoritmo                         | Função / Classe              | Complexidade Tempo   | Complexidade Espaço |
|-----------------------------------|------------------------------|----------------------|---------------------|
| Construção (lista de adjacência)  | `Grafo.adicionar_aresta()`   | O(V + E)             | O(V + E)            |
| BFS com reconstrução de caminho   | `bfs()`                      | O(V + E)             | O(V)                |
| DFS com tempos d/f                | `class DFS`                  | O(V + E)             | O(V)                |
| Dijkstra (heap binário)           | `dijkstra()`                 | O((V+E) log V)       | O(V)                |
| Componentes conexas               | `encontrar_componentes_conexas()` | O(V + E)        | O(V)                |
| Detecção de ciclos                | `detectar_ciclos()`          | O(V + E)             | O(V)                |
| Betweenness Centrality (Brandes)  | `centralidade_intermediacao()` | O(V·(V+E))        | O(V + E)            |

---

## Perguntas respondidas

### 1. Componentes conexas
O grafo possui **1 componente** — é totalmente conexo. Todos os 18
personagens estão interligados.

### 2. Menor caminho (Dijkstra)
**Bentinho → D.Fortunata**
- Dijkstra (menor custo): `Bentinho → Tio_Cosme → Jose_Dias → Capitu → D.Fortunata` (custo = 46)
- BFS (menos saltos): `Bentinho → Capitu → D.Fortunata` (2 saltos)
> Os dois algoritmos divergem: BFS ignora os pesos; Dijkstra evita a aresta Bentinho→Capitu (peso 50) e prefere um caminho mais longo porém mais barato.

### 3. Nó de maior grau
**Bentinho** com grau 11. Como protagonista e narrador, ele interage
com praticamente todos os outros personagens.

### 4. DFS
Árvore DFS a partir de Bentinho com tempos de descoberta [d] e
finalização [f]. Foram identificadas **32 arestas de retorno**
(evidência direta de ciclos).

### 5. Ciclos
**Sim** — detectados pela DFS. Exemplo: `Bentinho → Capitu → Escobar → Bentinho`.

### 6. Betweenness Centrality (proposta pela dupla)
*"Quais personagens são pontes narrativas na rede?"*

| Personagem    | BC (normalizada) |
|---------------|-----------------|
| Bentinho      | 0.9657          |
| Jose_Dias     | 0.5000          |
| Capitu        | 0.4804          |
| Sancha        | 0.2353          |
| Prima_Justina | 0.2353          |

Bentinho não só tem mais conexões — ele **medeia quase todos os
caminhos mínimos da rede**, papel coerente com o de narrador onipresente.

---

## Uso de IA

O código foi gerado com auxílio do **Claude (Anthropic)**.  
Todos os trechos gerados por IA estão declarados no relatório com
indicação da ferramenta.  
A defesa oral verificará o entendimento linha a linha de cada algoritmo.
