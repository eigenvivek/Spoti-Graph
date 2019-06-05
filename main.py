import argparse

from search import NetworkMiner
from utils import get_graph
from plot import plot

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Spotify network discovery")

    parser.add_argument('--uri', type=str, required=True,
                        help="URI for a Spotify artist.")
    parser.add_argument('-f', '--fname', type=str, required=True,
                        help="Write edgelist and attributes to files with common filename")
    parser.add_argument('--breadth_limit', type=int,
                        default=5, help="Number of adjacent nodes")
    parser.add_argument('--min_popularity', type=float, default=65,
                        help="Minimum popularity for artist to be entered in network")
    parser.add_argument('--include_collaborators', type=bool, default=True,
                        help="Include collaborators in related artists (Y/n)?")
    parser.add_argument('--max_pop_size', type=int, default=20,
                        help="Maximum number of nodes in network")
    parser.add_argument('-v', '--verbose', type=bool,
                        default=True, help="Display output messages")

    args = parser.parse_args()
    print(args)
    miner = NetworkMiner(
        include_collaborators=args.include_collaborators,
        breadth_limit=args.breadth_limit,
        max_pop_size=args.max_pop_size,
        min_popularity=args.min_popularity,
        verbose=args.verbose,
    )
    miner.write_edgelist(artist=args.uri, fname=args.fname)

    G = get_graph('derivatives/{}_attributes.pkl'.format(args.fname),
                  'derivatives/{}.edgelist'.format(args.fname))

    params = [args.fname, args.include_collaborators, args.breadth_limit,
        args.max_pop_size, args.min_popularity, args.verbose]
    params = [str(param) for param in params]
    outname = ("_").join(params)
    plot(G, fname=outname)
