import argparse
import os
import sys
import csv

from pvactools.lib.optimal_peptide import OptimalPeptide

from pvactools.tools.pvacvector.run import *

def define_parser():
    parser = argparse.ArgumentParser(
        "pvacvector find_ordering",
        description="Given a junctions.tsv file produced by a previous pVACvector runk, find a peptide ordering that minimizes the effects of junctional epitopes (that may create novel peptides) between the sequences.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "junctions_tsv",
        help="A junctions.tsv file with junction score information from a previous pVACvector run.",
    )
    parser.add_argument(
        "output_directory",
        help="The output directory to save results to",
    )
    return parser

def main(args_input = sys.argv[1:]):
    parser = define_parser()
    args = parser.parse_args(args_input)

    nodes = set()
    edges = []
    with open(args.junctions_tsv, 'r') as fh:
        reader = csv.DictReader(fh, delimiter="\t")
        for line in reader:
            nodes.update([line['left_peptide'], line['right_peptide']])
            edges.append(line)

    graph = pvactools.tools.pvacvector.run.initialize_graph(nodes)
    for edge in edges:
        graph.add_edge(
            edge['left_peptide'],
            edge['right_peptide'],
            weight=float(edge['junction_score']),
            percentile=edge['percentile'],
            spacer=edge['spacer'],
            left_partner_trim=int(edge['left_partner_clip']),
            right_partner_trim=int(edge['right_partner_clip'])
        )

    init_state = sorted(graph.nodes())
    distance_matrix = pvactools.tools.pvacvector.run.create_distance_matrix(graph)
    if not os.environ.get('TEST_FLAG') or os.environ.get('TEST_FLAG') == '0':
        random.shuffle(init_state)
    peptide = OptimalPeptide(init_state, distance_matrix)
    peptide.copy_strategy = "slice"
    peptide.save_state_on_exit = False
    state, e = peptide.anneal()

    (names, cumulative_weight, all_scores, problematic_junctions) = pvactools.tools.pvacvector.run.parse_state(state, graph)
    if len(problematic_junctions) > 0:
        raise Exception("No valid junction between peptides: {}".format(", ".join(problematic_junctions)))

    print(state)

if __name__ == "__main__":
    main()
