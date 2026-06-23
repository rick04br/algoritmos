# algoritmos
Trabalho Prático — Exploração de Grafos em Redes Reais
Grafo de Personagens — Dom Casmurro (Machado de Assis)
Trabalho Final de Teoria dos Grafos — Rede D6
---
Estrutura do projeto
```
.
├── grafo_dom_casmurro.py          # Implementação principal
├── D6_dom_casmurro.csv            # Arestas (Source, Target, Weight)
├── D6_dom_casmurro_nodes.csv      # Nós (Id, Label)
└── README.md
```
---
Como executar
```bash
# Coloque os dois CSVs na mesma pasta do script e rode:
python3 grafo_dom_casmurro.py
```
Requisito: Python 3.8+, sem dependências externas (apenas `csv`, `heapq`, `collections`).
---
Sobre a rede
Propriedade	Valor
Tipo	Não-dirigido, ponderado
Vértices |V|	18
Arestas |E|	32
Grau médio	3.56
Conexo	Sim
Possui ciclos	Sim
---
Estruturas e algoritmos implementados
Algoritmo	Complexidade Tempo	Complexidade Espaço
Construção (lista de adjacência)	O(V + E)	O(V + E)
BFS (com reconstrução de caminho)	O(V + E)	O(V)
DFS (com tempos d/f)	O(V + E)	O(V)
Dijkstra (heap binário)	O((V+E) log V)	O(V)
Componentes conexas (BFS)	O(V + E)	O(V)
Detecção de ciclos (DFS)	O(V + E)	O(V)
Betweenness Centrality	O(V * (V + E))	O(V²)
---
Perguntas respondidas
Componentes conexas: 1 componente — o grafo É conexo.
Menor caminho (Dijkstra) Bentinho → D.Fortunata: custo 46 (via Tio_Cosme → Jose_Dias → Capitu).
Nó de maior grau: Bentinho (grau 11) — protagonista/narrador.
DFS: árvore textual com tempos d/f e 15 arestas de retorno identificadas.
Ciclos: SIM — detectados pelas arestas de retorno na DFS.
Betweenness Centrality: Bentinho (0.9657) serve de ponte em praticamente todos os caminhos mínimos da rede.
---
Uso de IA
80 a 90% do código gerado com o auxilio da IA para acerto do código.
