from search import write_edgelist
from graph_io import get_graph
from plot import plot


if __name__ == '__main__':

    uri = 'spotify:artist:329e4yvIujISKGKz1BZZbO'
    write_edgelist(uri, file_identifier='farruko', min_popularity=65)

    G = get_graph('derivatives/farruko_attributes.pkl',
                  'derivatives/farruko.edgelist')
    plot(G)
