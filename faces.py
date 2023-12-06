import pprint
import secrets
import statistics
import sys
import traceback
import networkx as nx
import numpy as np
import itertools
import random
import time
from routing import *



def create_random_planar_graph(number_nodes, number_edges):
    retry =0
    while retry < 1000000:
        print("Retry : ", retry)
        Grand = nx.random_regular_graph(number_edges, number_nodes, secrets.randbits(200))
        is_planar, embedding = nx.check_planarity(Grand)
        if is_planar:
            return embedding
        retry = retry + 1
    
    raise Exception("No planar graph found.:(")



# Find all the faces of a planar graph
def find_faces(G, pos):
    half_edges_in_faces = set()
    faces = []

    nx.draw(G, pos, with_labels=True, node_size=700, node_color="green", font_size=8)
    plt.show()

    for node in G.nodes:

        for dest in nx.neighbors(G, node):

            # check every half edge of node if it is in a face
            if (node, dest) not in half_edges_in_faces:

                # This half edge has no face assigned
                found_half_edges = set()

                try:
                    face_nodes = G.traverse_face(node, dest, found_half_edges)

                except Exception as e:

                    nx.draw(G, pos, with_labels=True, node_size=700, node_color="red", font_size=8)

                    plt.show()
                    traceback.print_exc()
                    print(f"An unexpected error occurred: {e}")
                    
                half_edges_in_faces.update(found_half_edges)

                # Create a subgraph for the face
                face_graph = G.subgraph(face_nodes).copy()

                # Add positions to nodes in the face graph
                for face_node in face_graph.nodes:
                    face_graph.nodes[face_node]['pos'] = pos[face_node]

                faces.append(face_graph)


    #ganz am ende muss der ganze Graph noch rein um die imaginäre Kante in jedem Durchlauf zu bilden
    #und dann immer die Schnittpunkte zu bestimmen
    graph_last = G
    for node in graph_last:
        graph_last.nodes[node]['pos'] = pos[node]
    faces.append(graph_last)
    return faces


# Find all the faces of a planar graph
def find_faces_Old(G,pos):
    half_edges_in_faces = set()
    faces = []

    for node in G.nodes:

        for dest in nx.neighbors(G, node):
            # check every half edge of node if it is in a face
            if (node, dest) not in half_edges_in_faces:
                # This half edge has no face assigned
                found_half_edges = set()
                face = G.traverse_face(node, dest, found_half_edges)
                half_edges_in_faces.union(found_half_edges)
                faces.append(face)

    return faces


def intersection_point(edge1, edge2, pos):
    x1, y1 = pos[edge1[0]]
    x2, y2 = pos[edge1[1]]
    x3, y3 = pos[edge2[0]]
    x4, y4 = pos[edge2[1]]

    # Berechne die Parameter für die Geradengleichungen der beiden Kanten
    a1 = y2 - y1
    b1 = x1 - x2
    c1 = x2 * y1 - x1 * y2

    a2 = y4 - y3
    b2 = x3 - x4
    c2 = x4 * y3 - x3 * y4

    # Berechne den Schnittpunkt
    det = a1 * b2 - a2 * b1

    if det == 0:
        # Die Kanten sind parallel, es gibt keinen eindeutigen Schnittpunkt
        return None
    else:
        x = (b1 * c2 - b2 * c1) / det
        y = (a2 * c1 - a1 * c2) / det
        return x, y

# Return true if line segments vec1 and vec2 intersect
def intersect(vec1, vec2):
    A = vec1[0]
    B = vec1[1]
    C = vec2[0]
    D = vec2[1]
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)

#hilfsmethode um den Schnittpunkt zu bestimmen
def ccw(A,B,C):
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])


# alte Methode um Cycles zu bestimmen aus denen man die Faces zu nehmen hätte sollen
def find_all_cycles(G, source=None, cycle_length_limit=None):
    """forked from networkx dfs_edges function. Assumes nodes are integers, or at least
    types which work with min() and > ."""
    if source is None:
        # produce edges for all components
        nodes=[list(i)[0] for i in nx.connected_components(G)]
    else:
        # produce edges for components with source
        nodes=[source]
    # extra variables for cycle detection:
    cycle_stack = []
    output_cycles = set()
    
    def get_hashable_cycle(cycle):
        """cycle as a tuple in a deterministic order."""
        m = min(cycle)
        mi = cycle.index(m)
        mi_plus_1 = mi + 1 if mi < len(cycle) - 1 else 0
        if cycle[mi-1] > cycle[mi_plus_1]:
            result = cycle[mi:] + cycle[:mi]
        else:
            result = list(reversed(cycle[:mi_plus_1])) + list(reversed(cycle[mi_plus_1:]))
        return tuple(result)
    
    for start in nodes:
        if start in cycle_stack:
            continue
        cycle_stack.append(start)
        
        stack = [(start,iter(G[start]))]
        while stack:
            parent,children = stack[-1]
            try:
                child = next(children)
                
                if child not in cycle_stack:
                    cycle_stack.append(child)
                    stack.append((child,iter(G[child])))
                else:
                    i = cycle_stack.index(child)
                    if i < len(cycle_stack) - 2: 
                      output_cycles.add(get_hashable_cycle(cycle_stack[i:]))
                
            except StopIteration:
                stack.pop()
                cycle_stack.pop()
    
    return [list(i) for i in output_cycles]

#alte methode, als die faces noch arrays waren mit zahlen drin und keine networkx nodes
def move_source_to_beginning(array, source):
    if source not in array:
        print("Error: Source node not found in the array.")
        return array

    # Index der Source-Knoten im Array finden
    source_index = array.index(source)

    # Neues Array erstellen, beginnend mit dem Source-Knoten
    new_array = array[source_index:] + array[:source_index]

    return new_array

#alte methode um die planaren Graphen zu genrerien
#parameter sind obere Limits für die Graph erstellung
def create_random_planar_graph_old(number_nodes, number_edges):
    G = nx.PlanarEmbedding()
    #erstellung der nodes an zufälligen positionen
    positions = []
    for i in range(number_nodes):

        position = ( random.randrange(45), random.randrange(45) )

        while position in positions:

            position = ( random.randrange(45), random.randrange(45) )  

        positions.append(position)
        
        G.add_node(i)
    
    #erstellung der kanten

    edges = []

    for i in range(number_edges):

        edge = (random.randrange(number_nodes), random.randrange(number_nodes))

        RETRY = 0
        while RETRY < 100:
            RETRY = RETRY +1

            # wenn die edge nicht verfügbar ist neue edge und von vorne starten
            if (edge in edges) or (edge[0] == edge[1]):
                edge = (random.randrange(number_nodes), random.randrange(number_nodes))
                print("Edge nicht verfügbar : ", edge)
                continue
            
            
            #der versuch war es beim Einfügen der Kante, den neuen Nachbarn auf der einen Seite clockwise als nächstes einzufügen
            #und auf dem rückweg der kante den anderen Nachbarn als counterclockwise einzufügen
            #jedoch hat das nicht hingehauen weil man es nicht einfach so machen kann und es nie zu einem ende führt
            if not ( "first_nbr" in G.nodes[edge[0]]):
                G.add_half_edge_cw(edge[0], edge[1], None)
                G.add_half_edge_ccw(edge[1], edge[0], None)
            else:
                first_nbr = G.nodes[edge[0]]["first_nbr"]
                G.add_half_edge_cw(edge[0], edge[1], first_nbr)
            
                if not "first_nbr" in G.nodes[edge[1]]:
                    G.add_half_edge_ccw(edge[1], edge[0], None)
                else:
                    G.add_half_edge_ccw(edge[1], edge[0],  G.nodes[edge[1]]["first_nbr"])


            try:
                print("check structure")
                print("RETRY : ", RETRY)
                G.check_structure()
                #Edge fits, we are done        
                edges.append(edge)
                break
            except:
                # Remove edge and try again
                G.remove_edge(edge[0], edge[1])
                continue 
            
    
    if not nx.is_connected(G):
        return create_random_planar_graph(number_nodes, number_edges)
    return G