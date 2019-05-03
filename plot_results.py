import sys

from utils import get_graph
from plot import plot

if __name__ == '__main__':

    fname = sys.argv[1]
    G = get_graph('derivatives/{}_attributes.pkl'.format(fname),
                  'derivatives/{}.edgelist'.format(fname))
    plot(G)
