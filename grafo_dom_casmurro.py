"""
================================================================
NCE0144 — Algoritmos e Estruturas de Dados II
Trabalho Final de Grafos
Dataset D6 — Dom Casmurro (Machado de Assis)
================================================================

DESCRIÇÃO DA REDE
─────────────────
Rede de personagens do romance "Dom Casmurro" de Machado de Assis.
Cada nó representa um personagem; cada aresta representa interação
entre dois personagens. O PESO da aresta indica a frequência dessas
interações ao longo do texto — quanto maior, mais vezes os dois
personagens aparecem juntos.

Tipo de grafo : Não-dirigido, ponderado
Vértices |V|  : 18
Arestas  |E|  : 32  (CSV original tem 34 linhas; 2 pares aparecem
                      com direções invertidas e mesmo peso — tratados
                      como duplicatas de um grafo não-dirigido)

REPRESENTAÇÃO INTERNA
──────────────────────
Lista de adjacência: dicionário {vértice: [(vizinho, peso), ...]}
Escolhida por ser mais eficiente para grafos ESPARSOS (|E| << |V|²).
Aqui |E|=32 e |V|²=324 → grafo muito esparso → lista é O(V+E) em
memória, enquanto matriz de adjacência gastaria O(V²)=O(324).

USO DE IA
──────────
Código gerado com auxílio do Claude (Anthropic).
Todos os trechos gerados por IA estão declarados no relatório.

DEPENDÊNCIAS
─────────────
Python 3.8+ — sem bibliotecas externas de grafos.
Módulos padrão usados: csv, heapq, collections.deque, os.path
"""

import csv
import heapq
import os
from collections import deque


# ================================================================
# LOCALIZAÇÃO DOS ARQUIVOS DE DADOS
# ================================================================
# Os CSVs devem estar na MESMA PASTA deste script.
# Se quiser outra localização, altere BASE_DIR abaixo.

BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
ARQUIVO_ARESTAS = os.path.join(BASE_DIR, "D6_dom_casmurro.csv")
ARQUIVO_NOS     = os.path.join(BASE_DIR, "D6_dom_casmurro_nodes.csv")


# ================================================================
# CLASSE GRAFO — Estrutura principal
# ================================================================

class Grafo:
    """
    Grafo representado por LISTA DE ADJACÊNCIA.

    POR QUE LISTA E NÃO MATRIZ DE ADJACÊNCIA?
    ─────────────────────────────────────────────
    A matriz de adjacência tem tamanho fixo V×V = 18×18 = 324 células
    e só vale a pena quando o grafo é DENSO (|E| próximo de V²).
    Este grafo tem |E|=32, muito abaixo de 324 — é ESPARSO.
    A lista de adjacência ocupa apenas O(V+E) = O(18+32) = O(50)
    posições e, nos algoritmos, percorre apenas os vizinhos REAIS
    de cada vértice, sem visitar células vazias.

    ATRIBUTOS PRINCIPAIS
    ─────────────────────
    dirigido : bool
        True  → arestas têm direção (A→B ≠ B→A)  [não é o caso do D6]
        False → arestas são bidirecionais (A—B = B—A)
    adj : dict {str: list[(str, int)]}
        Núcleo do grafo. Para cada vértice, lista de (vizinho, peso).
    rotulos : dict {str: str}
        Nome legível de cada personagem, lido do arquivo de nós.
    arestas : list[(str, str, int)]
        Lista plana de todas as arestas sem duplicatas.
        Usada para calcular |E| e percorrer arestas sem repetição.
    """

    def __init__(self, dirigido=False):
        self.dirigido = dirigido
        self.adj      = {}   # {vertice: [(vizinho, peso), ...]}
        self.rotulos  = {}   # {id_vertice: "nome legível"}
        self.arestas  = []   # [(u, v, peso)] sem duplicatas

    # ------------------------------------------------------------
    # CONSTRUÇÃO DO GRAFO
    # ------------------------------------------------------------

    def adicionar_vertice(self, v, rotulo=""):
        """
        Garante que o vértice v existe no dicionário adj.
        Se já existir, NÃO faz nada (operação idempotente).
        Isso evita sobrescrever o rótulo de um vértice já criado.

        Complexidade: O(1) amortizado (acesso a dicionário hash).
        """
        if v not in self.adj:
            self.adj[v]     = []
            self.rotulos[v] = rotulo

    def adicionar_aresta(self, u, v, peso=1):
        """
        Adiciona a aresta entre u e v com o peso dado.

        Para grafos NÃO-DIRIGIDOS (nosso caso):
          - Insere (v, peso) na lista de u  [u enxerga v]
          - Insere (u, peso) na lista de v  [v enxerga u]
          - A lista self.arestas guarda APENAS uma direção (u→v)
            para não contar a mesma aresta duas vezes nas estatísticas.

        Complexidade: O(1) amortizado.
        """
        self.adicionar_vertice(u)
        self.adicionar_vertice(v)

        # Insere na lista de adjacência de u
        self.adj[u].append((v, peso))

        # Armazena aresta sem duplicar na lista plana
        self.arestas.append((u, v, peso))

        # Grafo não-dirigido: a relação é simétrica
        if not self.dirigido:
            self.adj[v].append((u, peso))

    # ------------------------------------------------------------
    # CARREGAMENTO DOS ARQUIVOS CSV
    # ------------------------------------------------------------

    def carregar_nos(self, caminho_csv):
        """
        Lê o arquivo de nós (colunas: Id, Label) e registra cada
        personagem com seu rótulo legível. Opcional para os algoritmos,
        mas torna a saída do programa muito mais compreensível.

        Complexidade: O(V) — uma leitura por nó.
        """
        with open(caminho_csv, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                self.adicionar_vertice(row['Id'].strip(), row['Label'].strip())

    def carregar_arestas(self, caminho_csv):
        """
        Lê o arquivo de arestas (colunas: Source, Target, Weight).

        TRATAMENTO DE DUPLICATAS
        ─────────────────────────
        O CSV do D6 tem 34 linhas, mas contém 2 pares repetidos com
        direções invertidas e mesmo peso:
          • Capitu  → Padua  (peso 20)  e  Padua  → Capitu  (peso 20)
          • Sancha  → Gurgel (peso 15)  e  Gurgel → Sancha  (peso 15)
        Num grafo NÃO-DIRIGIDO, A→B e B→A são a MESMA aresta.
        O conjunto 'vistos' guarda a chave canônica de cada par
        (tupla ordenada alfabeticamente) e ignora a 2ª ocorrência.
        Resultado: 34 - 2 = 32 arestas únicas.

        Complexidade: O(E) — uma leitura por linha do CSV.
        """
        vistos = set()
        with open(caminho_csv, newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                u    = row['Source'].strip()
                v    = row['Target'].strip()
                peso = int(row['Weight'])

                # Par canônico: ordem alfabética garante que (A,B) == (B,A)
                par = tuple(sorted([u, v]))
                if par not in vistos:
                    vistos.add(par)
                    self.adicionar_aresta(u, v, peso)

    # ------------------------------------------------------------
    # ESTATÍSTICAS BÁSICAS
    # ------------------------------------------------------------

    def num_vertices(self):
        """Retorna |V|. Complexidade: O(1)."""
        return len(self.adj)

    def num_arestas(self):
        """Retorna |E|. Complexidade: O(1)."""
        return len(self.arestas)

    def grau(self, v):
        """
        Grau do vértice v = número de vizinhos.
        Em grafos não-dirigidos, cada aresta (u,v) é inserida em adj[u]
        e em adj[v], então len(adj[v]) já dá o grau correto.
        Complexidade: O(1).
        """
        return len(self.adj[v])

    def grau_medio(self):
        """
        Grau médio = (soma de todos os graus) / |V|.
        Pelo Handshaking Lemma: soma_graus = 2×|E|
        Logo: grau_médio = 2×|E| / |V| = 2×32/18 ≈ 3.56

        Complexidade: O(V).
        """
        if self.num_vertices() == 0:
            return 0
        total = sum(len(viz) for viz in self.adj.values())
        return total / self.num_vertices()

    def no_maior_grau(self):
        """
        Vértice com mais vizinhos diretos.
        Complexidade: O(V) — percorre todos os vértices.
        """
        return max(self.adj, key=lambda v: len(self.adj[v]))

    def imprimir_estatisticas(self):
        """Imprime um resumo formatado da rede."""
        maior = self.no_maior_grau()
        sep   = "=" * 60
        print(sep)
        print("  ESTATÍSTICAS BÁSICAS — D6 Dom Casmurro")
        print(sep)
        print(f"  Tipo de grafo : {'Dirigido' if self.dirigido else 'Não-dirigido, ponderado'}")
        print(f"  Vértices |V|  : {self.num_vertices()}")
        print(f"  Arestas  |E|  : {self.num_arestas()}  "
              f"(CSV tem 34 linhas; 2 duplicatas removidas)")
        print(f"  Grau médio    : {self.grau_medio():.2f}  "
              f"(= 2×{self.num_arestas()} / {self.num_vertices()}, Handshaking Lemma)")
        print(f"  Nó maior grau : {maior}  (grau {self.grau(maior)})")
        print(sep)


# ================================================================
# FUNÇÃO AUXILIAR — Reconstrução de caminho
# ================================================================

def _reconstruir_caminho(predecessor, origem, destino):
    """
    Dado o dicionário predecessor[v] = quem veio antes de v,
    reconstrói a lista de vértices do caminho origem → destino.

    Estratégia: começa em 'destino' e segue predecessor[] até 'origem',
    depois inverte a lista.

    Retorna None se 'destino' não foi alcançado (não está em predecessor).

    Complexidade: O(V) no pior caso (caminho percorre todos os vértices).
    """
    if destino not in predecessor:
        return None
    caminho = []
    atual   = destino
    while atual is not None:
        caminho.append(atual)
        atual = predecessor[atual]
    caminho.reverse()
    # Confirma que o caminho realmente começa na origem
    return caminho if caminho[0] == origem else None


# ================================================================
# ALGORITMO 1 — BFS (Busca em Largura)
# ================================================================
#
# IDEIA CENTRAL
# ──────────────
# Explora o grafo nível por nível a partir da origem,
# usando uma fila FIFO (First In, First Out).
# O primeiro momento em que chegamos a um vértice garante
# que encontramos o caminho de MENOR NÚMERO DE SALTOS até ele.
#
# FUNCIONAMENTO PASSO A PASSO
# ────────────────────────────
# 1. Marca a origem como visitada, coloca na fila, dist[origem]=0
# 2. Enquanto a fila não estiver vazia:
#    a. Retira o vértice u da FRENTE da fila
#    b. Para cada vizinho v de u:
#       - Se v ainda NÃO foi visitado:
#         • Marca como visitado
#         • predecessor[v] = u  (de onde viemos)
#         • dist[v] = dist[u] + 1
#         • Adiciona v no FINAL da fila
#
# POR QUE FILA E NÃO PILHA?
# ──────────────────────────
# A fila FIFO garante que todos os vértices a distância k sejam
# processados ANTES dos de distância k+1. Trocar por pilha
# resultaria em DFS, não BFS.
#
# COMPLEXIDADE
# ─────────────
# Tempo : O(V + E)  — cada vértice entra/sai da fila 1 vez → O(V)
#                     cada aresta é examinada 1 vez      → O(E)
# Espaço: O(V)      — fila, visitado, predecessor e distancia

def bfs(grafo, origem, destino=None):
    """
    BFS a partir de 'origem' com reconstrução opcional de caminho.

    Parâmetros
    ──────────
    grafo   : instância de Grafo
    origem  : vértice de partida
    destino : (opcional) se fornecido, reconstrói e retorna o caminho

    Retorno (sem destino)  : (predecessor, distancia)
    Retorno (com destino)  : (predecessor, distancia, caminho)
      predecessor : dict {v: quem veio antes de v no BFS}
      distancia   : dict {v: nº de arestas da origem até v}
      caminho     : list [origem, ..., destino] ou None
    """
    visitado    = {origem}          # conjunto para busca O(1)
    fila        = deque([origem])   # fila FIFO — núcleo do BFS
    predecessor = {origem: None}    # predecessor[origem]=None (é a raiz)
    distancia   = {origem: 0}

    while fila:
        u = fila.popleft()              # retira da FRENTE (FIFO)
        for (v, _peso) in grafo.adj[u]:
            if v not in visitado:
                visitado.add(v)
                predecessor[v] = u
                distancia[v]   = distancia[u] + 1
                fila.append(v)          # insere no FINAL

    if destino is not None:
        caminho = _reconstruir_caminho(predecessor, origem, destino)
        return predecessor, distancia, caminho

    return predecessor, distancia


# ================================================================
# ALGORITMO 2 — DFS (Busca em Profundidade)
# ================================================================
#
# IDEIA CENTRAL
# ──────────────
# Mergulha o mais fundo possível em cada ramo antes de retroceder.
# Usa coloração dos vértices (WHITE → GRAY → BLACK) e registra
# os tempos de descoberta [d] e finalização [f] — exatamente como
# descrito no CLRS (Cormen et al.), Capítulo 22.
#
# COLORAÇÃO
# ──────────
#   WHITE = ainda não visitado
#   GRAY  = em visita (está na pilha de recursão atual)
#   BLACK = totalmente finalizado (todos os vizinhos processados)
#
# CLASSIFICAÇÃO DE ARESTAS (grafo não-dirigido)
# ───────────────────────────────────────────────
#   Aresta de árvore  : vizinho está WHITE → filho na árvore DFS
#   Aresta de retorno : vizinho está GRAY e NÃO é o pai direto
#                       → existe um ciclo!
#
# IMPLEMENTAÇÃO
# ──────────────
# Recursiva (pilha implícita de chamadas de função).
# Com V=18 isso é seguro; o limite padrão do Python é ~1000 níveis.
#
# COMPLEXIDADE
# ─────────────
# Tempo : O(V + E)  — igual ao BFS, mesmo raciocínio
# Espaço: O(V)      — pilha de recursão + dicionários de cor/tempo

class DFS:
    """Busca em Profundidade com marcação de tempos e classificação de arestas."""

    def __init__(self, grafo):
        self.grafo           = grafo
        self.cor             = {}    # WHITE / GRAY / BLACK por vértice
        self.predecessor     = {}    # predecessor na árvore DFS
        self.tempo_desc      = {}    # d[v]: instante de descoberta
        self.tempo_fin       = {}    # f[v]: instante de finalização
        self.arestas_retorno = []    # back edges detectadas (indicam ciclos)
        self.arvore_dfs      = {}    # {v: [filhos diretos na árvore DFS]}
        self._tempo          = 0     # contador global de tempo (incrementa 1 a 1)

    def executar(self, origem):
        """
        Ponto de entrada da DFS.
        Inicializa todos os vértices como WHITE e começa em 'origem'.
        Se o grafo tiver componentes desconexas, continua pelos
        vértices ainda não visitados após terminar a partir da origem.
        Isso garante que TODOS os vértices recebam tempos d e f.
        """
        # Inicializa todos como não visitados
        for v in self.grafo.adj:
            self.cor[v]         = 'WHITE'
            self.predecessor[v] = None

        self._tempo = 0
        self._visitar(origem)   # visita a componente da origem

        # Se houver componentes desconexas, visita os demais
        for v in self.grafo.adj:
            if self.cor[v] == 'WHITE':
                self._visitar(v)

    def _visitar(self, u):
        """
        Núcleo recursivo: processa o vértice u.

        PASSO A PASSO
        ──────────────
        1. Pinta u de GRAY → "estou visitando u agora"
        2. Incrementa o tempo e registra d[u] (descoberta)
        3. Para cada vizinho v de u:
           • WHITE → aresta de árvore: v é filho de u, visita recursivamente
           • GRAY  → aresta de retorno: v é ancestral de u → há um CICLO
           • BLACK → aresta já processada (ignorada — não classifica ciclo)
        4. Pinta u de BLACK → "terminei u e todos os seus descendentes"
        5. Registra f[u] (finalização)
        """
        self.cor[u]        = 'GRAY'
        self._tempo       += 1
        self.tempo_desc[u] = self._tempo
        self.arvore_dfs[u] = []          # lista de filhos de u na árvore DFS

        for (v, _peso) in self.grafo.adj[u]:
            if self.cor[v] == 'WHITE':
                # ── Aresta de árvore ──
                self.predecessor[v] = u
                self.arvore_dfs[u].append(v)
                self._visitar(v)          # mergulho recursivo em v
            elif self.cor[v] == 'GRAY':
                # ── Aresta de retorno ── v é ancestral de u → ciclo!
                self.arestas_retorno.append((u, v))

        self.cor[u]       = 'BLACK'
        self._tempo      += 1
        self.tempo_fin[u] = self._tempo

    def imprimir_arvore(self, raiz, prefixo="", eh_ultimo=True):
        """
        Imprime a árvore DFS em formato textual (estilo 'tree' do Unix).
        Exibe os tempos d e f de cada nó ao lado do nome.

        Exemplo de saída:
            └── Bentinho  [d=1, f=36]
                ├── Capitu  [d=2, f=29]
                │   └── Sancha  [d=3, f=24]
        """
        conector = "└── " if eh_ultimo else "├── "
        d = self.tempo_desc.get(raiz, '?')
        f = self.tempo_fin.get(raiz, '?')
        print(f"{prefixo}{conector}{raiz}  [d={d}, f={f}]")

        # Prefixo dos filhos: recua com espaço ou barra vertical
        prefixo += "    " if eh_ultimo else "│   "
        filhos   = self.arvore_dfs.get(raiz, [])
        for i, filho in enumerate(filhos):
            self.imprimir_arvore(filho, prefixo, i == len(filhos) - 1)


# ================================================================
# ALGORITMO 3 — Dijkstra (caminho de menor custo ponderado)
# ================================================================
#
# POR QUE DIJKSTRA E NÃO BFS PARA O CAMINHO MÍNIMO?
# ───────────────────────────────────────────────────
# BFS encontra o caminho com MENOS ARESTAS (saltos), mas trata todos
# os pesos como iguais. Como o D6 tem pesos diferentes em cada aresta,
# BFS pode devolver um caminho com poucos saltos mas custo acumulado
# maior. Dijkstra minimiza a SOMA DOS PESOS — exatamente o que o
# enunciado pede para "redes com peso nas arestas".
#
# FUNCIONAMENTO COM HEAP MÍNIMO
# ──────────────────────────────
# 1. dist[v] = ∞ para todos; dist[origem] = 0
# 2. Insere (0, origem) no heap mínimo
# 3. Extrai u = vértice de menor dist atual
# 4. Para cada vizinho v de u, tenta RELAXAR a aresta (u, v):
#    SE dist[u] + peso(u,v) < dist[v]:
#      → atualiza dist[v]           ← RELAXAMENTO
#      → predecessor[v] = u
#      → insere (novo_dist, v) no heap
# 5. Repete até o heap esvaziar
#
# RELAXAMENTO: é o coração do Dijkstra. "Relaxar" uma aresta significa
# perguntar: "passando por u, chego a v mais barato do que o melhor
# caminho que conheço até agora?"
#
# COMPLEXIDADE
# ─────────────
# Tempo : O((V + E) log V)  com heap binário (heapq do Python)
#         — cada extração do heap custa O(log V)
#         — cada aresta gera no máximo uma inserção no heap: O(E log V)
# Espaço: O(V)  — dicionários dist, predecessor e heap com ≤ V+E entradas
#
# RESTRIÇÃO: pesos devem ser NÃO-NEGATIVOS.
# Todos os pesos do D6 são positivos → Dijkstra é válido aqui.

def dijkstra(grafo, origem, destino=None):
    """
    Dijkstra com heap binário mínimo (heapq).

    Parâmetros
    ──────────
    grafo   : instância de Grafo (não-dirigido, pesos positivos)
    origem  : vértice de partida
    destino : (opcional) se fornecido, reconstrói e retorna o caminho

    Retorno (sem destino)  : (dist, predecessor)
    Retorno (com destino)  : (dist, predecessor, caminho)
      dist        : dict {v: menor custo acumulado da origem até v}
      predecessor : dict {v: vértice anterior no caminho ótimo}
      caminho     : list [origem, ..., destino] ou None
    """
    # Inicializa distâncias como infinito, exceto a origem
    dist        = {v: float('inf') for v in grafo.adj}
    predecessor = {v: None         for v in grafo.adj}
    dist[origem] = 0

    # Heap mínimo: entradas (custo_acumulado, vertice)
    heap = [(0, origem)]

    while heap:
        custo_atual, u = heapq.heappop(heap)   # extrai o de menor custo

        # LAZY DELETION: o heap pode ter entradas antigas para u com
        # custo maior do que o atual dist[u]. Ignoramos essas entradas.
        if custo_atual > dist[u]:
            continue

        # Tenta relaxar cada aresta (u → v)
        for (v, peso) in grafo.adj[u]:
            novo_custo = dist[u] + peso          # ← RELAXAMENTO
            if novo_custo < dist[v]:
                dist[v]        = novo_custo
                predecessor[v] = u
                heapq.heappush(heap, (novo_custo, v))

    if destino is not None:
        caminho = _reconstruir_caminho(predecessor, origem, destino)
        return dist, predecessor, caminho

    return dist, predecessor


# ================================================================
# ALGORITMO 4 — Componentes Conexas (BFS exaustiva)
# ================================================================
#
# Uma componente conexa é um subconjunto MÁXIMO de vértices tal que
# todo par dentro do subconjunto está ligado por algum caminho.
#
# ESTRATÉGIA
# ───────────
# Para cada vértice ainda não visitado, faz uma BFS completa.
# Todos os vértices alcançados formam uma componente.
# Repete até cobrir todos os vértices do grafo.
#
# COMPLEXIDADE
# ─────────────
# Tempo : O(V + E)  — no total, cada vértice e cada aresta são
#                     processados exatamente uma vez entre todas as BFS
# Espaço: O(V)      — conjunto visitado + fila + lista de componentes

def encontrar_componentes_conexas(grafo):
    """
    Retorna lista de conjuntos, cada um sendo uma componente conexa.
    Ex.: se o grafo for conexo → retorna [{v1, v2, ..., v18}] (1 elemento).

    Para o D6, esperamos 1 componente (grafo conexo segundo o guia).
    """
    visitado    = set()
    componentes = []

    for v_inicio in grafo.adj:
        if v_inicio in visitado:
            continue   # já pertence a uma componente descoberta

        # BFS completa a partir de v_inicio
        componente = set()
        fila       = deque([v_inicio])
        visitado.add(v_inicio)

        while fila:
            u = fila.popleft()
            componente.add(u)
            for (w, _) in grafo.adj[u]:
                if w not in visitado:
                    visitado.add(w)
                    fila.append(w)

        componentes.append(componente)

    return componentes


# ================================================================
# ALGORITMO 5 — Detecção de Ciclos via DFS
# ================================================================
#
# Em grafos NÃO-DIRIGIDOS, existe ciclo se e somente se a DFS
# encontrar uma "aresta de retorno" — aresta que leva a um vértice
# GRAY que NÃO é o predecessor imediato do vértice atual.
#
# POR QUE EXCLUIR O PREDECESSOR?
# ────────────────────────────────
# Em grafos não-dirigidos, a aresta (u, pai(u)) aparece NA LISTA DE
# ADJACÊNCIA de u. Se não excluíssemos o pai, toda aresta geraria
# uma falsa aresta de retorno. A condição "v ≠ predecessor[u]"
# filtra esses falsos alarmes e detecta apenas ciclos reais.
#
# EXEMPLO NA NOSSA REDE
# ──────────────────────
# Bentinho → Capitu → Escobar → Bentinho
# Quando a DFS visita Escobar e vê Bentinho como vizinho GRAY
# (e Bentinho ≠ predecessor de Escobar), detecta o ciclo.
#
# COMPLEXIDADE
# ─────────────
# Tempo : O(V + E)   — DFS padrão
# Espaço: O(V)       — cor, predecessor, pilha de recursão

def detectar_ciclos(grafo):
    """
    Detecta ciclos em grafo não-dirigido via DFS com coloração.

    Retorno
    ────────
    (tem_ciclo : bool, arestas_retorno : list[(u, v)])
      tem_ciclo       : True se pelo menos uma aresta de retorno foi encontrada
      arestas_retorno : lista de todas as back edges detectadas
    """
    cor         = {v: 'WHITE' for v in grafo.adj}
    predecessor = {v: None    for v in grafo.adj}
    back_edges  = []

    def _dfs(u):
        cor[u] = 'GRAY'
        for (v, _) in grafo.adj[u]:
            if cor[v] == 'WHITE':
                predecessor[v] = u
                _dfs(v)
            elif cor[v] == 'GRAY' and predecessor[u] != v:
                # Vizinho GRAY que NÃO é o pai direto → ciclo real
                back_edges.append((u, v))
        cor[u] = 'BLACK'

    for v in grafo.adj:
        if cor[v] == 'WHITE':
            _dfs(v)

    return len(back_edges) > 0, back_edges


# ================================================================
# ALGORITMO 6 — Centralidade de Intermediação (Betweenness Centrality)
# ================================================================
#
# PERGUNTA PROPOSTA PELA DUPLA
# ─────────────────────────────
# "Quais personagens são pontes narrativas — ou seja, por quais
#  nós passam a maior proporção dos caminhos mínimos entre os demais?"
#
# POR QUE ESSA PERGUNTA É INTERESSANTE?
# ───────────────────────────────────────
# Grau alto indica muitas conexões diretas, mas não revela intermediação.
# Um personagem de grau baixo pode ser o ÚNICO elo entre dois grupos —
# se removido, a rede se fragmenta. A Betweenness Centrality captura
# exatamente esse papel de "conector crítico":
#   BC(v) = Σ_{s≠v≠t}  σ(s,t|v) / σ(s,t)
#   σ(s,t)   = nº total de caminhos mínimos de s a t
#   σ(s,t|v) = quantos desses caminhos passam por v
#
# ALGORITMO DE BRANDES (2001) — adaptado para grafos não-dirigidos
# ─────────────────────────────────────────────────────────────────
# Para cada vértice fonte s:
#   FASE 1 — BFS: calcula σ(s,v) e lista de predecessores de cada v
#   FASE 2 — Acumulação reversa: propaga as dependências de volta
#
# NORMALIZAÇÃO
# ─────────────
# Divide por (n-1)(n-2)/2 → valor em [0, 1]
# (total de pares distintos de vértices diferentes de v)
#
# COMPLEXIDADE
# ─────────────
# Tempo : O(V × (V + E))  — uma BFS de custo O(V+E) por vértice fonte
# Espaço: O(V + E)        — dicionários de tamanho V por iteração

def centralidade_intermediacao(grafo):
    """
    Calcula a Betweenness Centrality normalizada de todos os vértices.
    Usa o algoritmo de Brandes com BFS (caminhos mínimos em saltos).

    Retorno: dict {vertice: float} com valores em [0, 1].
    """
    vertices = list(grafo.adj.keys())
    n        = len(vertices)
    bc       = {v: 0.0 for v in vertices}

    for s in vertices:

        # ── FASE 1: BFS a partir de s ──────────────────────────────
        dist          = {v: -1 for v in vertices}   # -1 = não visitado
        sigma         = {v:  0 for v in vertices}   # nº de caminhos mínimos s→v
        predecessores = {v: [] for v in vertices}   # predecessores no caminho mínimo

        dist[s]  = 0
        sigma[s] = 1
        fila     = deque([s])
        ordem    = []   # ordem de processamento (para fase 2)

        while fila:
            u = fila.popleft()
            ordem.append(u)
            for (w, _) in grafo.adj[u]:
                if dist[w] == -1:           # primeira visita a w
                    dist[w] = dist[u] + 1
                    fila.append(w)
                if dist[w] == dist[u] + 1:  # u está num caminho mínimo até w
                    sigma[w] += sigma[u]
                    predecessores[w].append(u)

        # ── FASE 2: Acumulação de dependências (ordem reversa) ─────
        delta = {v: 0.0 for v in vertices}
        while ordem:
            w = ordem.pop()                  # do mais distante para o mais próximo
            for u in predecessores[w]:
                if sigma[w] > 0:
                    # Fração dos caminhos s→w que passam por u
                    delta[u] += (sigma[u] / sigma[w]) * (1.0 + delta[w])
            if w != s:
                bc[w] += delta[w]

    # ── Normalização ────────────────────────────────────────────────
    # Para grafo não-dirigido, par (s,t) é contado como (s→t) e (t→s);
    # dividimos por (n-1)(n-2)/2 para chegar ao valor em [0,1].
    if n > 2:
        fator = (n - 1) * (n - 2) / 2.0
        bc    = {v: bc[v] / fator for v in bc}

    return bc


# ================================================================
# FUNÇÃO PRINCIPAL — Executa todos os algoritmos e responde
#                    as 6 perguntas do enunciado
# ================================================================

def main():
    sep = "=" * 60

    # ────────────────────────────────────────────────────────────
    # CONSTRUÇÃO DO GRAFO
    # ────────────────────────────────────────────────────────────
    g = Grafo(dirigido=False)
    g.carregar_nos(ARQUIVO_NOS)         # lê os rótulos dos 18 personagens
    g.carregar_arestas(ARQUIVO_ARESTAS) # constrói as 32 arestas únicas

    print()
    g.imprimir_estatisticas()
    print()

    # Exibe a lista de adjacência completa (evidência para o relatório)
    print("LISTA DE ADJACÊNCIA COMPLETA:")
    for v in sorted(g.adj.keys()):
        vizinhos = sorted(g.adj[v], key=lambda x: x[0])
        print(f"  {v:20s}  grau={len(vizinhos):2d}  → {vizinhos}")
    print()

    # ════════════════════════════════════════════════════════════
    # PERGUNTA 1 — Quantos componentes conexos? O grafo é conexo?
    # ════════════════════════════════════════════════════════════
    print(sep)
    print("  PERGUNTA 1 — Componentes Conexas")
    print(sep)

    componentes = encontrar_componentes_conexas(g)
    conexo      = (len(componentes) == 1)

    print(f"  Número de componentes conexas: {len(componentes)}")
    for i, comp in enumerate(componentes, 1):
        print(f"  Componente {i} ({len(comp)} vértices): {sorted(comp)}")

    print(f"\n  => O grafo {'É' if conexo else 'NÃO é'} CONEXO.")
    if conexo:
        print("     Todos os 18 personagens estão interligados por algum caminho.")
    print()

    # ════════════════════════════════════════════════════════════
    # PERGUNTA 2 — Menor caminho entre dois nós
    # ════════════════════════════════════════════════════════════
    print(sep)
    print("  PERGUNTA 2 — Menor Caminho")
    print(sep)

    origem_q2  = "Bentinho"
    destino_q2 = "D.Fortunata"

    print(f"  Nós escolhidos : {origem_q2}  →  {destino_q2}")
    print(f"  Justificativa  : Bentinho é o hub central (grau 11) e")
    print(f"  D.Fortunata é personagem periférica (grau 2, mãe de Capitu).")
    print(f"  Eles representam dois extremos narrativos da rede — o")
    print(f"  protagonista e uma figura secundária da família de Capitu.")
    print(f"  A distância ponderada revela por quais intermediários")
    print(f"  esses dois extremos se conectam na rede.")
    print()

    # Dijkstra: minimiza SOMA DOS PESOS
    print("  [Dijkstra — menor CUSTO PONDERADO]")
    dist_dij, _, caminho_dij = dijkstra(g, origem_q2, destino_q2)
    if caminho_dij:
        print(f"  Caminho : {' → '.join(caminho_dij)}")
        print(f"  Custo total (Σ pesos): {dist_dij[destino_q2]}")
        print("  Detalhamento aresta a aresta:")
        acum = 0
        for i in range(len(caminho_dij) - 1):
            u, v  = caminho_dij[i], caminho_dij[i + 1]
            peso  = next(p for (w, p) in g.adj[u] if w == v)
            acum += peso
            print(f"    {u:20s} → {v:20s}  peso={peso:3d}  acumulado={acum}")
    else:
        print("  Destino não alcançável.")
    print()

    # BFS: minimiza NÚMERO DE SALTOS (ignora pesos)
    print("  [BFS — menor número de SALTOS (sem considerar pesos)]")
    _, dist_bfs, caminho_bfs = bfs(g, origem_q2, destino_q2)
    if caminho_bfs:
        print(f"  Caminho : {' → '.join(caminho_bfs)}")
        print(f"  Saltos  : {dist_bfs[destino_q2]}")
    print()
    print("  Observação: Dijkstra e BFS podem devolver caminhos DIFERENTES.")
    print("  BFS ignora os pesos e prefere o caminho com menos arestas.")
    print("  Dijkstra pode usar mais saltos para evitar arestas de peso alto.")
    print()

    # ════════════════════════════════════════════════════════════
    # PERGUNTA 3 — Qual é o nó de maior grau?
    # ════════════════════════════════════════════════════════════
    print(sep)
    print("  PERGUNTA 3 — Nó de Maior Grau")
    print(sep)

    graus     = {v: g.grau(v) for v in g.adj}
    ordenados = sorted(graus.items(), key=lambda x: x[1], reverse=True)

    print("  Grau de todos os vértices (ordem decrescente):")
    for v, gr in ordenados:
        label = g.rotulos.get(v, "")
        barra = "█" * gr
        print(f"    {v:20s}  grau={gr:2d}  {barra:12s}  [{label}]")

    maior_v, maior_g = ordenados[0]
    print()
    print(f"  => Nó de maior grau: {maior_v} (grau {maior_g})")
    print(f"     Rótulo          : {g.rotulos.get(maior_v, '')}")
    print(f"     Contexto real   : como protagonista e narrador do romance,")
    print(f"     {maior_v} interage com praticamente todos os personagens —")
    print(f"     daí o grau dominante. Machado de Assis o coloca no centro")
    print(f"     de todas as relações, o que a rede reflete numericamente.")
    print()

    # ════════════════════════════════════════════════════════════
    # PERGUNTA 4 — DFS: árvore e arestas de retorno
    # ════════════════════════════════════════════════════════════
    print(sep)
    print("  PERGUNTA 4 — DFS e Árvore de Busca em Profundidade")
    print(sep)

    origem_dfs = "Bentinho"
    print(f"  Origem escolhida: {origem_dfs}  (hub central, grau {g.grau(origem_dfs)})")
    print()

    dfs_obj = DFS(g)
    dfs_obj.executar(origem_dfs)

    # Tabela de tempos
    print("  Tabela de tempos de descoberta [d] e finalização [f]:")
    print(f"  {'Vértice':20s}  {'d':>3}  {'f':>3}  Predecessor")
    print("  " + "-" * 50)
    for v in sorted(dfs_obj.tempo_desc.keys()):
        d    = dfs_obj.tempo_desc[v]
        f    = dfs_obj.tempo_fin[v]
        pred = dfs_obj.predecessor[v] or "— (raiz)"
        print(f"  {v:20s}  {d:3d}  {f:3d}  {pred}")
    print()

    # Árvore DFS visual
    print("  Árvore de DFS (representação textual):")
    dfs_obj.imprimir_arvore(origem_dfs)
    # Se houvesse componentes desconexas, suas raízes apareceriam aqui
    for v in g.adj:
        if dfs_obj.predecessor[v] is None and v != origem_dfs:
            dfs_obj.imprimir_arvore(v)
    print()

    # Arestas de retorno
    print("  Arestas de retorno identificadas (back edges):")
    if dfs_obj.arestas_retorno:
        for u, v in dfs_obj.arestas_retorno:
            print(f"    ({u}) → ({v})  ← vizinho GRAY → indica ciclo")
    else:
        print("    Nenhuma aresta de retorno.")
    print()

    # ════════════════════════════════════════════════════════════
    # PERGUNTA 5 — O grafo possui ciclos?
    # ════════════════════════════════════════════════════════════
    print(sep)
    print("  PERGUNTA 5 — Detecção de Ciclos")
    print(sep)

    tem_ciclo, back_edges = detectar_ciclos(g)
    print(f"  O grafo possui ciclos? {'SIM' if tem_ciclo else 'NÃO'}")
    print()

    if tem_ciclo:
        # Exibe apenas pares únicos (sem contar (u,v) e (v,u))
        pares = set(tuple(sorted([u, v])) for u, v in back_edges)
        print(f"  Evidência — {len(pares)} pares de back edges únicos:")
        for u, v in sorted(pares):
            print(f"    {u} ↔ {v}")
        print()
        print("  MÉTODO DE DETECÇÃO (via DFS com coloração):")
        print("    WHITE = vértice ainda não visitado")
        print("    GRAY  = vértice em visita (está na pilha de recursão)")
        print("    BLACK = vértice finalizado")
        print("    → Se encontramos (u → v) com v GRAY e v ≠ predecessor[u],")
        print("      então v é ANCESTRAL de u na árvore DFS,")
        print("      e a aresta (u,v) forma um ciclo com o caminho u→...→v.")
        print()
        print("  EXEMPLO CONCRETO NESTA REDE:")
        print("    Bentinho → Capitu → Escobar → Bentinho")
        print("    (ciclo de comprimento 3 entre os personagens centrais)")
    print()

    # ════════════════════════════════════════════════════════════
    # PERGUNTA 6 — Centralidade de Intermediação (proposta pela dupla)
    # ════════════════════════════════════════════════════════════
    print(sep)
    print("  PERGUNTA 6 — Centralidade de Intermediação")
    print("  (proposta pela dupla — implementada do zero)")
    print(sep)
    print()
    print("  PERGUNTA PROPOSTA:")
    print("  'Quais personagens funcionam como pontes narrativas na rede")
    print("   — ou seja, por quais nós passam a maior proporção dos")
    print("   caminhos mínimos entre todos os outros pares?'")
    print()
    print("  POR QUE É INTERESSANTE:")
    print("  Grau alto revela personagens com muitas conexões diretas,")
    print("  mas não captura intermediação. A Betweenness Centrality")
    print("  (BC) responde: 'se eu fosse removido da rede, quantas")
    print("  ligações entre outros personagens seriam perdidas?'")
    print("  Em literatura, BC alta = mediador narrativo insubstituível.")
    print()

    bc            = centralidade_intermediacao(g)
    ordenados_bc  = sorted(bc.items(), key=lambda x: x[1], reverse=True)

    print("  Centralidade de Intermediação normalizada [0 a 1]:")
    print(f"  {'Personagem':20s}  {'BC':>6}  Barra visual")
    print("  " + "-" * 55)
    for v, c in ordenados_bc:
        label = g.rotulos.get(v, "")
        barra = "█" * int(c * 25)
        print(f"  {v:20s}  {c:.4f}  {barra}  [{label}]")

    top_v, top_c = ordenados_bc[0]
    print()
    print(f"  => Maior betweenness: {top_v} ({top_c:.4f})")
    print(f"     {top_v} medeia quase todos os caminhos mínimos da rede.")
    print(f"     Sem ele, a maioria das conexões entre personagens dependeria")
    print(f"     de rotas muito mais longas — ou deixaria de existir.")
    print(f"     Isso é consistente com o papel de narrador onipresente")
    print(f"     que Machado de Assis lhe atribui no romance.")
    print()

    # ════════════════════════════════════════════════════════════
    # RESUMO GERAL
    # ════════════════════════════════════════════════════════════
    print(sep)
    print("  RESUMO GERAL")
    print(sep)
    print(f"  Vértices       : {g.num_vertices()}")
    print(f"  Arestas        : {g.num_arestas()}")
    print(f"  Grau médio     : {g.grau_medio():.2f}")
    print(f"  Conexo         : {'Sim' if conexo else 'Não'}")
    print(f"  Possui ciclos  : {'Sim' if tem_ciclo else 'Não'}")
    print(f"  Maior grau     : {maior_v}  (grau {maior_g})")
    print(f"  Maior BC       : {top_v}  ({top_c:.4f})")
    print(sep)
    print()


if __name__ == "__main__":
    main()
