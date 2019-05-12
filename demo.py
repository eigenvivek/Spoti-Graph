from search import NetworkMiner
from utils import get_graph
from plot import plot


if __name__ == '__main__':

    miner = NetworkMiner(
        breadth_limit=5,
        min_popularity=65,
        include_collaborators=False,
        max_pop_size=None,
        verbose=True,
    )

    uri = 'spotify:artist:329e4yvIujISKGKz1BZZbO'
    fname = 'farruko_no_collab'

    miner.write_edgelist(artist=uri, fname=fname)

    G = get_graph('derivatives/{}_attributes.pkl'.format(fname),
                  'derivatives/{}.edgelist'.format(fname))

    plot(G, fname='./demo/farruko')
