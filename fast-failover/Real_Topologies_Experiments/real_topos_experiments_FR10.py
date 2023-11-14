import sys
from typing import List, Any, Union

import networkx as nx
import numpy as np
import itertools
import random
import time
import glob
from objective_function_experiments import *
from trees import multiple_trees_pre, multiple_trees_pre_breite_mod, multiple_trees_pre_invert_order_of_edps_mod, multiple_trees_pre_num_of_trees_mod, multiple_trees_pre_order_of_edps_mod, multiple_trees_pre_parallel, multiple_trees_pre_parallel_and_inverse, multiple_trees_pre_random_order_of_edps_mod, one_tree_pre
from routing import RouteMultipleTrees, PrepareSQ1, RouteSQ1, RouteOneTree
DEBUG = True

# Data structure containing the algorithms under
# scrutiny. Each entry contains a name and a pair
# of algorithms.
#
# The first algorithm is used for any precomputation
# to produce data structures later needed for routing
# on the graph passed along in args. If the precomputation
# fails, the algorithm must return -1.
# Examples for precomputation algorithms can be found in
# arborescences.py
#
# The second algorithm decides how to forward a
# packet from source s to destination d, despite the
# link failures fails using data structures from precomputation
# Examples for precomputation algorithms can be found in
# routing.py
#
# In this example we compare Bonsai and Greedy. You can add more
# algorithms to this data structure to compare the performance
# of additional algorithms.
#algos = {'One Tree': [one_tree_pre, RouteOneTree], 'Greedy': [GreedyArborescenceDecomposition, RouteDetCirc]}
algos = {'MultipleTrees FR10': [multiple_trees_pre, RouteMultipleTrees],
'OneTree FR10': [one_tree_pre, RouteOneTree],
'Parallel and Inverse FR10': [multiple_trees_pre_parallel_and_inverse, RouteMultipleTrees],
'SquareOne FR10': [PrepareSQ1, RouteSQ1],
'MultipleTrees Mod Parallel FR10': [multiple_trees_pre_parallel, RouteMultipleTrees],
'MultipleTrees Invert Order Mod FR10': [multiple_trees_pre_invert_order_of_edps_mod, RouteMultipleTrees],
'MultipleTrees Random Order Mod FR10': [multiple_trees_pre_random_order_of_edps_mod, RouteMultipleTrees]
}

# run one experiment with graph g
# out denotes file handle to write results to
# seed is used for pseudorandom number generation in this run
# returns a score for the performance:
#       if precomputation fails : 10^9
#       if success_ratio == 0: 10^6
#       otherwise (2 - success_ratio) * (stretch + load)
def one_experiment(g, seed, out, algo):
    [precomputation_algo, routing_algo] = algo[:2]
    if DEBUG: print('experiment for ', algo[0])

    # precomputation
    reset_arb_attribute(g)
    random.seed(seed)
    t = time.time()
    precomputation = precomputation_algo(g)
    print('Done with precomputation algo')
    pt = time.time() - t
    if precomputation == -1:  # error...
        out.write(', %f, %f, %f, %f, %f, %f\n' %
                  (float('inf'), float('inf'), float('inf'), 0, 0, pt))
        score = 1000*1000*1000
        return score

    # routing simulation (hier gebe ich den routing algorithmus mit)#################################################################################################################################
    print("Start routing")
    stat = Statistic(routing_algo, str(routing_algo))
    stat.reset(g.nodes())
    random.seed(seed)
    t = time.time()
    #hier sage ich dass ich den routing algorithmus simulieren soll (in stat steht welchen routing algorithmus ich ausführen will))#################################################################################################################################
    SimulateGraph(g, True, [stat], f_num, samplesize, precomputation=precomputation)
    rt = (time.time() - t)/samplesize
    success_ratio = stat.succ/ samplesize
    # write results
    if stat.succ > 0:
        if DEBUG: print('success', stat.succ, algo[0])
        # stretch, load, hops, success, routing time, precomputation time
        out.write(', %i, %i, %i, %f, %f, %f\n' %
                  (np.max(stat.stretch), stat.load, np.max(stat.hops),
                   success_ratio, rt, pt))
        score = (2 - success_ratio) * (np.max(stat.stretch) + stat.load)

    else:
        if DEBUG: print('no success_ratio', algo[0])
        out.write(', %f, %f, %f, %f, %f, %f\n' %
                  (float('inf'), float('inf'), float('inf'), 0, rt, pt))
        score = 1000*1000
    return score


# run experiments with AS graphs
# out denotes file handle to write results to
# seed is used for pseudorandom number generation in this run
# rep denotes the number of repetitions in the shuffle for loop
def run_AS(out=None, seed=0, rep=5):
    for i in range(4, 5):
        generate_trimmed_AS(i)
    files = glob.glob('./benchmark_graphs/AS*.csv')
    original_params = [n, rep, k, samplesize, f_num, seed, name]
    for x in files:
        random.seed(seed)
        kk = int(x[-5:-4])
        g = nx.read_edgelist(x).to_directed()
        g.graph['k'] = kk
        nn = len(g.nodes())
        mm = len(g.edges())
        ss = min(int(nn / 2), samplesize)
        fn = min(int(mm / 2), f_num)
        fails = random.sample(list(g.edges()), fn)
        g.graph['fails'] = fails
        set_parameters([nn, rep, kk, ss, fn, seed, name + "AS-"])
        shuffle_and_run(g, out, seed, rep, x)
        set_parameters(original_params)

# run experiments with zoo graphs
# out denotes file handle to write results to
# seed is used for pseudorandom number generation in this run
# rep denotes the number of repetitions in the shuffle for loop
def run_zoo(out=None, seed=0, rep=2):
    global f_num
    fr = 10 #die zahl muss geändert werden damit man die fr ändert
    min_connectivity = 2
    original_params = [n, rep, k, samplesize, f_num, seed, name]
    if DEBUG:
        print('n_before, n_after, m_after, connectivity, degree')
    zoo_list = list(glob.glob("./benchmark_graphs/*.graphml"))
    for i in range(len(zoo_list)):
        random.seed(seed)
        g = read_zoo(i, min_connectivity)
        if g is None:
            continue

        print("Len(g) = " , len(g.nodes))
        kk = nx.edge_connectivity(g)
        nn = len(g.nodes())

        
        if nn == 39 and len( list(g.edges)) == 143: #oteglobe
        #if nn == 105 and len( list(g.edges)) == 384: #cogentco
        #if nn == 39 and len( list(g.edges)) == 141:#missouri
        #if nn == 39 and len(g.edges) == 163:
            PG = nx.nx_pydot.write_dot(g, "./fixTruncation/graph_"+str(i))
            print("Passender Graph ")
            mm = len(g.edges())
            ss = min(int(nn / 2), samplesize)
            #f_num = kk * fr
            #fn = min(int(mm / 4), f_num)
            fn = 1
            if fn == int(mm / 4):
                print("SKIP ITERATION")
                continue
            print("Fehleranzahl : ", fn)
            set_parameters([nn, rep, kk, ss, fn, seed, name + "zoo-"])
            print("Node Number : " , nn)
            print("Connectivity : " , kk)
            print("Failure Number : ", fn)
            #print('parameters', nn, rep, kk, ss, fn, seed)
            shuffle_and_run(g, out, seed, rep, str(i))
            set_parameters(original_params)
            for (algoname, algo) in algos.items():
                index_1 = len(algo) - rep
                index_2 = len(algo)
                print('intermediate result: %s \t %.5E' % (algoname, np.mean(algo[index_1:index_2])))

# shuffle root nodes and run algorithm
def shuffle_and_run(g, out, seed, rep, x):
    random.seed(seed)
    nodes = list(g.nodes())
    random.shuffle(nodes)
    for count in range(rep):
        g.graph['root'] = nodes[count % len(nodes)]
        for (algoname, algo) in algos.items():
            # graph, size, connectivity, algorithm, index,
            out.write('%s, %i, %i, %s, %i' % (x, len(nodes), g.graph['k'], algoname, count))
            algos[algoname] += [one_experiment(g, seed + count, out, algo)]

# run experiments with d-regular graphs
# out denotes file handle to write results to
# seed is used for pseudorandom number generation in this run
# rep denotes the number of repetitions in the secondary for loop
def run_regular(out=None, seed=0, rep=5):
    ss = min(int(n / 2), samplesize)
    fn = min(int(n * k / 4), f_num)
    set_parameters([n, rep, k, ss, fn, seed, name + "regular-"])
    write_graphs()
    for i in range(rep):
        random.seed(seed + i)
        g = read_graph(i)
        random.seed(seed + i)
        for (algoname, algo) in algos.items():
            # graph, size, connectivity, algorithm, index,
            out.write('%s, %i, %i, %s, %i' % ("regular", n, k, algoname, i))
            algos[algoname] += [one_experiment(g, seed + i, out, algo)]

# start file to capture results
def start_file(filename):
    out = open(filename + ".txt", 'w')
    out.write(
        "#graph, size, connectivity, algorithm, index, " +
        "stretch, load, hops, success, " +
        "routing computation time, pre-computation time in seconds\n")
    out.write(
        "#" + str(time.asctime(time.localtime(time.time()))) + "\n")
    return out


# run experiments
# seed is used for pseudorandom number generation in this run
# switch determines which experiments are run

#hier kann rep geändert werden
def experiments(switch="all", seed=0, rep=100):
    if switch in ["regular", "all"]:
        out = start_file("results/benchmark-regular-all-multiple-trees-" + str(n) + "-" + str(k))
        run_regular(out=out, seed=seed, rep=rep)
        out.close()

    if switch in ["zoo", "all"]:
        out = start_file("results/benchmark-zoo-RealTopos-" + str(failure_rate) + "-" + str(k))
        run_zoo(out=out, seed=seed, rep=rep)
        out.close()

    if switch in ["AS"]:
        out = start_file("results/benchmark-as_seed_-all-multiple-trees-" + str(seed))
        run_AS(out=out, seed=seed, rep=rep)
        out.close()

    print()
    for (algoname, algo) in algos.items():
        print('%s \t %.5E' % (algoname, np.mean(algo[2:])))
    print("\nlower is better")



if __name__ == "__main__":
    f_num = 2
    for i in range(1,13):
        failure_rate = i
        #f_num = 26 #number of failed links
        n = 60 # number of nodes
        k = 5 #base connectivity
        samplesize = 5 #number of sources to route a packet to destination
        rep = 5 #number of experiments
        switch = 'all' #which experiments to run with same parameters
        seed = 0  #random seed
        name = "benchmark-" #result files start with this name
        short = None #if true only small zoo graphs < 25 nodes are run
        start = time.time()
        print(time.asctime(time.localtime(start)))
        if len(sys.argv) > 1:
            switch = sys.argv[1]
        if len(sys.argv) > 2:
            seed = int(sys.argv[2])
        if len(sys.argv) > 3:
            rep = int(sys.argv[3])
        if len(sys.argv) > 4:
            n = int(sys.argv[4])
        if len(sys.argv) > 4:
            samplesize = int(sys.argv[5])
        random.seed(seed)
        set_parameters([n, rep, k, samplesize, f_num, seed, "benchmark-"])
        experiments(switch=switch, seed=seed, rep=rep)
        end = time.time()
        print("time elapsed", end - start)
        print("start time", time.asctime(time.localtime(start)))
        print("end time", time.asctime(time.localtime(end)))
        f_num = f_num + 2
