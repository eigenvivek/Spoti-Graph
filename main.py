from search import write_edgelist
from utils import get_graph
from plot import plot


if __name__ == '__main__':

    uri = 'spotify:artist:329e4yvIujISKGKz1BZZbO'
    fname = 'farruko_no_collab'
    write_edgelist(
        uri,
        fname=fname,
        limit=5,
        min_popularity=65,
        include_collaborators=False,
        breakpoint=None,
        verbose=True,
    )

    G = get_graph('derivatives/{}_attributes.pkl'.format(fname),
                  'derivatives/{}.edgelist'.format(fname))
    plot(G)
