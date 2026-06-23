"""
Trabalho Final - Teoria dos Grafos
Rede: Personagens de Dom Casmurro (Machado de Assis)
Dataset: D6_dom_casmurro.csv / D6_dom_casmurro_nodes.csv

Implementação SEM uso de bibliotecas de grafos (NetworkX, igraph).
Todas as estruturas e algoritmos foram implementados do zero.
"""

import csv
import heapq
from collections import deque


# =============================================================================
# ESTRUTURA DO GRAFO
# =============================================================================

class Grafo:
    """
    Grafo NÃO-DIRIGIDO representado por lista de adjacência.
    Suporta pesos nas arestas.
    """

    def __init__(self, dirigido=False):
        self.dirigido = dirigido
        self.adj = {}          # {vertice: [(vizinho, peso), ...]}
        self.rotulos = {}      # {vertice: label}
        self.arestas = []      # lista de (u, v, peso) sem duplicatas

    # ------------------------------------------------------------------
    # Construção do grafo
    # ------------------------------------------------------------------

    def adicionar_vertice(self, v, rotulo=""):
        if v not in self.adj:
            self.adj[v] = []
            self.rotulos[v] = rotulo

    def adicionar_aresta(self, u, v, peso=1):
        self.adicionar_vertice(u)
        self.adicionar_vertice(v)

        self.adj[u].append((v, peso))
        self.arestas.append((u, v, peso))

        if not self.dirigido:
            self.adj[v].append((u, peso))

    # ------------------------------------------------------------------
    # Carregamento dos arquivos CSV
    # ------------------------------------------------------------------

    def carregar_nos(self, caminho_csv):
        with open(caminho_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                self.adicionar_vertice(row['Id'].strip(), row['Label'].strip())

    def carregar_arestas(self, caminho_csv):
        """
        Para grafos não-dirigidos: evita duplicatas (A-B e B-A com mesmo peso).
        """
        vistos = set()
        with open(caminho_csv, newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                u = row['Source'].strip()
                v = row['Target'].strip()
                peso = int(row['Weight'])
                par = tuple(sorted([u, v]))
                if par not in vistos:
                    vistos.add(par)
                    self.adicionar_aresta(u, v, peso)

    # ------------------------------------------------------------------
    # Estatísticas básicas
    # ------------------------------------------------------------------

    def num_vertices(self):
        return len(self.adj)

    def num_arestas(self):
        return len(self.arestas)

    def grau(self, v):
        return len(self.adj[v])

    def grau_medio(self):
        if self.num_vertices() == 0:
            return 0
        total = sum(len(vizinhos) for vizinhos in self.adj.values())
        return total / self.num_vertices()

    def no_maior_grau(self):
        return max(self.adj, key=lambda v: len(self.adj[v]))

    def imprimir_estatisticas(self):
        maior = self.no_maior_grau()
        print("=" * 55)
        print("  ESTATÍSTICAS BÁSICAS DA REDE")
        print("=" * 55)
        print(f"  Tipo de grafo    : {'Dirigido' if self.dirigido else 'Não-dirigido'}")
        print(f"  Número de vértices (|V|) : {self.num_vertices()}")
        print(f"  Número de arestas  (|E|) : {self.num_arestas()}")
        print(f"  Grau médio               : {self.grau_medio():.2f}")
        print(f"  Nó de maior grau         : {maior} (grau {self.grau(maior)})")
        print("=" * 55)


# =============================================================================
# ALGORITMO 1: BFS — Busca em Largura com reconstrução de caminho
# Complexidade de tempo : O(V + E)
# Complexidade de espaço: O(V)
# =============================================================================

def bfs(grafo, origem, destino=None):
    """
    BFS a partir de 'origem'.
    - Retorna (predecessores, distancias) onde dist é em número de saltos.
    - Se 'destino' fornecido, reconstrói e retorna o caminho.
    """
    visitado = {origem}
    fila = deque([origem])
    predecessor = {origem: None}
    distancia = {origem: 0}

    while fila:
        u = fila.popleft()
        for (v, _peso) in grafo.adj[u]:
            if v not in visitado:
                visitado.add(v)
                predecessor[v] = u
                distancia[v] = distancia[u] + 1
                fila.append(v)

    if destino is not None:
        caminho = reconstruir_caminho(predecessor, origem, destino)
        return predecessor, distancia, caminho

    return predecessor, distancia


def reconstruir_caminho(predecessor, origem, destino):
    """Reconstrói caminho de origem até destino via dicionário de predecessores."""
    if destino not in predecessor:
        return None  # destino não alcançável
    caminho = []
    atual = destino
    while atual is not None:
        caminho.append(atual)
        atual = predecessor[atual]
    caminho.reverse()
    return caminho if caminho[0] == origem else None


# =============================================================================
# ALGORITMO 2: DFS — Busca em Profundidade com tempos de descoberta/finalização
# Complexidade de tempo : O(V + E)
# Complexidade de espaço: O(V)
# =============================================================================

class DFS:
    """
    DFS iterativa com marcação de tempos de descoberta e finalização.
    Identifica arestas de árvore, retorno, avanço e cruzamento.
    """

    def __init__(self, grafo):
        self.grafo = grafo
        self.cor = {}          # WHITE / GRAY / BLACK
        self.predecessor = {}
        self.tempo_desc = {}   # d[v]: tempo de descoberta
        self.tempo_fin = {}    # f[v]: tempo de finalização
        self.arestas_retorno = []
        self.arvore_dfs = {}   # {v: [filhos]}
        self.tempo = 0

    def executar(self, origem):
        # Inicializa todos os vértices como WHITE (não visitado)
        for v in self.grafo.adj:
            self.cor[v] = 'WHITE'
            self.predecessor[v] = None

        self.tempo = 0
        self._visitar(origem)

        # Continua para vértices não alcançados (componentes desconexas)
        for v in self.grafo.adj:
            if self.cor[v] == 'WHITE':
                self._visitar(v)

    def _visitar(self, u):
        self.cor[u] = 'GRAY'
        self.tempo += 1
        self.tempo_desc[u] = self.tempo
        self.arvore_dfs[u] = []

        for (v, _peso) in self.grafo.adj[u]:
            if self.cor[v] == 'WHITE':
                # Aresta de árvore
                self.predecessor[v] = u
                self.arvore_dfs[u].append(v)
                self._visitar(v)
            elif self.cor[v] == 'GRAY':
                # Aresta de retorno → indica ciclo
                self.arestas_retorno.append((u, v))

        self.cor[u] = 'BLACK'
        self.tempo += 1
        self.tempo_fin[u] = self.tempo

    def imprimir_arvore(self, raiz, prefix="", eh_ultimo=True):
        """Imprime a árvore DFS de forma textual (estilo árvore)."""
        conector = "└── " if eh_ultimo else "├── "
        d = self.tempo_desc.get(raiz, '?')
        f = self.tempo_fin.get(raiz, '?')
        print(f"{prefix}{conector}{raiz}  [d={d}, f={f}]")
        prefix += "    " if eh_ultimo else "│   "
        filhos = self.arvore_dfs.get(raiz, [])
        for i, filho in enumerate(filhos):
            self.imprimir_arvore(filho, prefix, i == len(filhos) - 1)


# =============================================================================
# ALGORITMO 3: Dijkstra — Caminho de menor peso
# Complexidade de tempo : O((V + E) log V)  com heap binário
# Complexidade de espaço: O(V)
# =============================================================================

def dijkstra(grafo, origem, destino=None):
    """
    Dijkstra com heap mínimo.
    Retorna (dist, predecessor) onde dist[v] = menor custo de origem até v.
    Se 'destino' fornecido, reconstrói e retorna o caminho de menor peso.
    """
    dist = {v: float('inf') for v in grafo.adj}
    predecessor = {v: None for v in grafo.adj}
    dist[origem] = 0

    # Heap: (custo_acumulado, vertice)
    heap = [(0, origem)]

    while heap:
        custo_atual, u = heapq.heappop(heap)

        # Relaxação: ignora entradas obsoletas no heap
        if custo_atual > dist[u]:
            continue

        for (v, peso) in grafo.adj[u]:
            novo_custo = dist[u] + peso
            if novo_custo < dist[v]:
                dist[v] = novo_custo
                predecessor[v] = u
                heapq.heappush(heap, (novo_custo, v))

    if destino is not None:
        caminho = reconstruir_caminho(predecessor, origem, destino)
        return dist, predecessor, caminho

    return dist, predecessor


# =============================================================================
# ALGORITMO 4: Componentes Conexas (Union-Find / BFS por componente)
# Complexidade de tempo : O(V + E)
# Complexidade de espaço: O(V)
# =============================================================================

def encontrar_componentes_conexas(grafo):
    """
    Retorna lista de componentes conexas (para grafo não-dirigido).
    Cada componente é um conjunto de vértices.
    """
    visitado = set()
    componentes = []

    for v in grafo.adj:
        if v not in visitado:
            # BFS a partir de v para encontrar todos os vértices da componente
            componente = set()
            fila = deque([v])
            visitado.add(v)
            while fila:
                u = fila.popleft()
                componente.add(u)
                for (w, _) in grafo.adj[u]:
                    if w not in visitado:
                        visitado.add(w)
                        fila.append(w)
            componentes.append(componente)

    return componentes


# =============================================================================
# ALGORITMO 5: Detecção de Ciclos via DFS
# Complexidade de tempo : O(V + E)
# Complexidade de espaço: O(V)
# =============================================================================

def detectar_ciclos(grafo):
    """
    Detecta ciclos em grafo não-dirigido usando DFS.
    Um ciclo existe se durante a DFS encontrarmos um vizinho GRAY
    que não é o predecessor do vértice atual.
    """
    cor = {v: 'WHITE' for v in grafo.adj}
    predecessor = {v: None for v in grafo.adj}
    arestas_retorno = []

    def dfs_ciclo(u):
        cor[u] = 'GRAY'
        for (v, _) in grafo.adj[u]:
            if cor[v] == 'WHITE':
                predecessor[v] = u
                dfs_ciclo(v)
            elif cor[v] == 'GRAY' and predecessor[u] != v:
                # Aresta de retorno real (não apenas a aresta pai)
                arestas_retorno.append((u, v))
        cor[u] = 'BLACK'

    for v in grafo.adj:
        if cor[v] == 'WHITE':
            dfs_ciclo(v)

    return len(arestas_retorno) > 0, arestas_retorno


# =============================================================================
# QUESTÃO 6 — ANÁLISE DE CENTRALIDADE (implementada do zero)
# Centralidade de intermediação (Betweenness Centrality) via BFS
# Complexidade de tempo : O(V * (V + E))
# Complexidade de espaço: O(V²)
# =============================================================================

def centralidade_intermediacao(grafo):
    """
    Calcula a centralidade de intermediação (betweenness centrality) de cada vértice.
    Para cada par (s, t), conta quantas vezes cada vértice v aparece nos
    menores caminhos entre s e t (em número de saltos — grafo não ponderado).

    Fórmula: BC(v) = Σ_{s≠v≠t} σ(s,t|v) / σ(s,t)
    onde σ(s,t) = número de menores caminhos entre s e t
         σ(s,t|v) = número desses caminhos que passam por v
    """
    vertices = list(grafo.adj.keys())
    n = len(vertices)
    bc = {v: 0.0 for v in vertices}

    for s in vertices:
        # BFS a partir de s
        dist = {v: -1 for v in vertices}
        sigma = {v: 0 for v in vertices}   # número de menores caminhos de s a v
        dist[s] = 0
        sigma[s] = 1
        fila = deque([s])
        ordem = []                          # ordem de finalização (para acumular)
        predecessores = {v: [] for v in vertices}

        while fila:
            u = fila.popleft()
            ordem.append(u)
            for (w, _) in grafo.adj[u]:
                if dist[w] == -1:          # primeira visita
                    dist[w] = dist[u] + 1
                    fila.append(w)
                if dist[w] == dist[u] + 1: # caminho mínimo passando por u
                    sigma[w] += sigma[u]
                    predecessores[w].append(u)

        # Acumular dependências (na ordem reversa de finalização)
        delta = {v: 0.0 for v in vertices}
        while ordem:
            w = ordem.pop()
            for u in predecessores[w]:
                if sigma[w] > 0:
                    delta[u] += (sigma[u] / sigma[w]) * (1 + delta[w])
            if w != s:
                bc[w] += delta[w]

    # Normalização para grafo não-dirigido: dividir por (n-1)(n-2)/2
    if n > 2:
        fator = (n - 1) * (n - 2) / 2
        bc = {v: bc[v] / fator for v in bc}

    return bc


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================

def main():
    # ------------------------------------------------------------------
    # 1. Construção do grafo
    # ------------------------------------------------------------------
    g = Grafo(dirigido=False)
    g.carregar_nos("D6_dom_casmurro_nodes.csv")
    g.carregar_arestas("D6_dom_casmurro.csv")

    print()
    g.imprimir_estatisticas()
    print()

    # Lista de adjacência resumida
    print("LISTA DE ADJACÊNCIA (resumida):")
    for v in sorted(g.adj.keys()):
        vizinhos = [(w, p) for w, p in sorted(g.adj[v], key=lambda x: x[0])]
        print(f"  {v:20s} → {vizinhos}")
    print()

    # ==================================================================
    # PERGUNTA 1 — Componentes conexas
    # ==================================================================
    print("=" * 55)
    print("  PERGUNTA 1 — Componentes Conexas")
    print("=" * 55)
    componentes = encontrar_componentes_conexas(g)
    print(f"  Número de componentes conexas: {len(componentes)}")
    for i, comp in enumerate(componentes, 1):
        print(f"  Componente {i} ({len(comp)} vértices): {sorted(comp)}")
    if len(componentes) == 1:
        print("  => O grafo É CONEXO.")
    else:
        print("  => O grafo NÃO é conexo.")
    print()

    # ==================================================================
    # PERGUNTA 2 — Menor caminho (Dijkstra com pesos)
    # ==================================================================
    print("=" * 55)
    print("  PERGUNTA 2 — Menor Caminho (Dijkstra)")
    print("=" * 55)
    origem_dij  = "Bentinho"
    destino_dij = "D.Fortunata"
    print(f"  Nós escolhidos: {origem_dij} → {destino_dij}")
    print(f"  Justificativa: Bentinho (protagonista) e D.Fortunata (mãe de Capitu)")
    print(f"  são dois extremos do enredo — interessante ver a distância ponderada.")
    print()

    dist, pred, caminho = dijkstra(g, origem_dij, destino_dij)
    if caminho:
        print(f"  Caminho: {' → '.join(caminho)}")
        print(f"  Custo total (soma dos pesos): {dist[destino_dij]}")
        # Detalhar pesos de cada aresta no caminho
        print("  Detalhamento:")
        custo_acc = 0
        for i in range(len(caminho) - 1):
            u, v = caminho[i], caminho[i+1]
            # Encontrar peso
            peso = next(p for (w, p) in g.adj[u] if w == v)
            custo_acc += peso
            print(f"    {u} → {v}  (peso {peso}, acumulado {custo_acc})")
    else:
        print("  Destino não alcançável.")
    print()

    # Também exibindo menor caminho em saltos (BFS sem peso)
    print(f"  [BFS sem peso] Saltos mínimos {origem_dij} → {destino_dij}:")
    _, dist_bfs, caminho_bfs = bfs(g, origem_dij, destino_dij)
    if caminho_bfs:
        print(f"  Caminho: {' → '.join(caminho_bfs)}")
        print(f"  Número de saltos: {dist_bfs[destino_dij]}")
    print()

    # ==================================================================
    # PERGUNTA 3 — Nó de maior grau
    # ==================================================================
    print("=" * 55)
    print("  PERGUNTA 3 — Nó de Maior Grau")
    print("=" * 55)
    graus = {v: g.grau(v) for v in g.adj}
    ordenados = sorted(graus.items(), key=lambda x: x[1], reverse=True)
    print("  Grau de todos os vértices (decrescente):")
    for v, gr in ordenados:
        label = g.rotulos.get(v, "")
        print(f"    {v:20s} grau={gr:2d}  [{label}]")
    maior_v, maior_g = ordenados[0]
    print()
    print(f"  => Nó de maior grau: {maior_v} (grau {maior_g})")
    print(f"     Rótulo: {g.rotulos.get(maior_v, '')}")
    print(f"     Significa: {maior_v} possui conexões com {maior_g} outros")
    print(f"     personagens, confirmando ser o centro narrativo do romance.")
    print()

    # ==================================================================
    # PERGUNTA 4 — DFS com árvore e arestas de retorno
    # ==================================================================
    print("=" * 55)
    print("  PERGUNTA 4 — DFS e Árvore de DFS")
    print("=" * 55)
    origem_dfs = "Bentinho"
    print(f"  Origem: {origem_dfs}")
    print()

    dfs_obj = DFS(g)
    dfs_obj.executar(origem_dfs)

    print("  Tempos de descoberta [d] e finalização [f]:")
    for v in sorted(dfs_obj.tempo_desc.keys()):
        d = dfs_obj.tempo_desc[v]
        f = dfs_obj.tempo_fin[v]
        pred = dfs_obj.predecessor[v] or "raiz"
        print(f"    {v:20s} d={d:2d}  f={f:2d}  predecessor={pred}")
    print()

    print("  Árvore DFS (estrutura textual):")
    dfs_obj.imprimir_arvore(origem_dfs)
    # Subárvores de vértices sem predecessor na raiz (florestas)
    for v in g.adj:
        if dfs_obj.predecessor[v] is None and v != origem_dfs:
            dfs_obj.imprimir_arvore(v)
    print()

    print("  Arestas de retorno encontradas (indicam ciclos):")
    if dfs_obj.arestas_retorno:
        for u, v in dfs_obj.arestas_retorno:
            print(f"    ({u}) → ({v})")
    else:
        print("    Nenhuma aresta de retorno detectada.")
    print()

    # ==================================================================
    # PERGUNTA 5 — Ciclos
    # ==================================================================
    print("=" * 55)
    print("  PERGUNTA 5 — Detecção de Ciclos")
    print("=" * 55)
    tem_ciclo, arestas_ret = detectar_ciclos(g)
    print(f"  O grafo possui ciclos? {'SIM' if tem_ciclo else 'NÃO'}")
    if tem_ciclo:
        print(f"  Evidência — arestas de retorno na DFS:")
        vistos = set()
        for u, v in arestas_ret:
            par = tuple(sorted([u, v]))
            if par not in vistos:
                vistos.add(par)
                print(f"    ({u}) ↔ ({v}): aresta de retorno → indica ciclo")
        print()
        print("  Como determinar: durante a DFS, se encontramos um vizinho v")
        print("  com cor GRAY e v ≠ predecessor[u], então existe uma aresta de")
        print("  retorno, o que implica a existência de um ciclo no grafo.")
    print()

    # ==================================================================
    # PERGUNTA 6 — Centralidade de Intermediação
    # ==================================================================
    print("=" * 55)
    print("  PERGUNTA 6 — Centralidade de Intermediação")
    print("  (Betweenness Centrality — implementada do zero)")
    print("=" * 55)
    print("  Pergunta proposta:")
    print("  'Quais personagens são pontes de comunicação entre os demais,")
    print("  ou seja, por quais nós passam mais caminhos mínimos da rede?'")
    print()
    print("  Por que é interessante: Em redes literárias, personagens com")
    print("  alta centralidade de intermediação funcionam como mediadores")
    print("  narrativos — sem eles, certas conexões entre personagens")
    print("  deixariam de existir. Isso revela o papel estrutural real")
    print("  de cada personagem além do seu simples número de conexões.")
    print()

    bc = centralidade_intermediacao(g)
    ordenados_bc = sorted(bc.items(), key=lambda x: x[1], reverse=True)
    print("  Centralidade de intermediação (normalizada):")
    for v, c in ordenados_bc:
        label = g.rotulos.get(v, "")
        barra = "█" * int(c * 30)
        print(f"    {v:20s} {c:.4f}  {barra}  [{label}]")
    print()
    top_v, top_c = ordenados_bc[0]
    print(f"  => Nó com maior betweenness: {top_v} ({top_c:.4f})")
    print(f"     Interpretação: {top_v} é o personagem que mais")
    print(f"     serve de ponte entre os demais na rede de Dom Casmurro.")
    print()

    # ==================================================================
    # RESUMO FINAL
    # ==================================================================
    print("=" * 55)
    print("  RESUMO GERAL")
    print("=" * 55)
    print(f"  Vértices     : {g.num_vertices()}")
    print(f"  Arestas      : {g.num_arestas()}")
    print(f"  Grau médio   : {g.grau_medio():.2f}")
    print(f"  Conexo       : {'Sim' if len(componentes) == 1 else 'Não'}")
    print(f"  Possui ciclos: {'Sim' if tem_ciclo else 'Não'}")
    print(f"  Maior grau   : {maior_v} (grau {maior_g})")
    print(f"  Maior betweenness: {top_v} ({top_c:.4f})")
    print("=" * 55)


if __name__ == "__main__":
    main()
