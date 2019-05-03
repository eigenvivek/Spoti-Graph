from pprint import pprint

import pickle

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from credentials import CLIENT_ID, CLIENT_SECRET


def setup_scrapper(client_id, client_secret):
    """Return a authenticated Spotify object."""
    client_credentials_manager = SpotifyClientCredentials(
        client_id, client_secret)
    spotify = spotipy.Spotify(
        client_credentials_manager=client_credentials_manager)

    return spotify


def _get_artist_metadata(uri, attributes, scrapper):
    """Return well formatted metadata. Fields of interest are specified in `attributes`."""

    # Search for the artist
    artist = scrapper.artist(uri)

    # Collect all valid metadata
    artist_metadata = {}
    for attr in attributes:
        try:
            artist_metadata[attr] = artist[attr]
        except KeyError:
            print("{} is not a valid key".format(attr))

    return artist_metadata


def _get_collaborators(uri, limit, attributes, scrapper):
    """Find artists that the given artist has collaborated with."""

    # Get the top tracks
    top_tracks = scrapper.artist_top_tracks(uri)
    top_tracks = top_tracks['tracks'][0:limit]

    # Get the metadata for each artist and store in list
    collaborators = []
    for track in top_tracks:
        for artist in track['artists']:
            target = artist['uri']
            if (target == uri) or (artist in collaborators):
                continue

            artist = scrapper.artist(target)
            collaborators.append(artist)

    return collaborators


def _get_related_artists(uri, connections, metadata, attributes, scrapper, limit, min_popularity, verbose, include_collaborators, breakpoint):
    """Recursive implementation of depth-first search."""

    if breakpoint is not None:
        if len(metadata.keys()) == breakpoint:
            raise Exception("breakpoint reached")

    # Add input artist's attributes to metadata
    metadata[uri] = _get_artist_metadata(
        uri, attributes=attributes, scrapper=scrapper)
    if verbose:
        # "Node <NUMBER>: <ARTIST> (<POPULARITY>)"
        pprint("Node {}: {} ({})".format(
            len(metadata.keys()), metadata[uri]['name'], metadata[uri]['popularity']))

    # Get up to `limit` related artists and associated metadata, organized in a list
    related = scrapper.artist_related_artists(uri)
    related = related['artists'][0:limit]

    # Get up to `limit` collaborators and add unique artists to `related`
    if include_collaborators:
        collaborators = _get_collaborators(uri, limit, attributes, scrapper)
        related_uri = [artist['uri'] for artist in related]
        for artist in collaborators:
            if artist['uri'] not in related_uri:
                related.append(artist)

    # Iterate through related artists...
    for artist in related:

        # 1a. Skip unpopular artists
        if int(artist['popularity']) < min_popularity:
            if verbose:
                print("    {} is unpopular ({})".format(
                    artist['name'], artist['popularity']))
            continue

        # 1b. Skip artists already adjacent to the input artist
        try:
            neighbors = [adjacent_uri for adjacent_uri in connections[uri]]
            if artist['uri'] in neighbors:
                continue
        except:
            pass

        # 2. Write related artist and weight to connections
        input_artist_uri = str(uri)         # URI of the input artist
        related_artist_uri = artist['uri']  # URI of the related artist
        try:
            connections[input_artist_uri] += [related_artist_uri]
        except KeyError:
            connections[input_artist_uri] = [related_artist_uri]

        # 3. Save the related artist's attributes
        metadata[related_artist_uri] = _get_artist_metadata(
            related_artist_uri, scrapper=scrapper, attributes=attributes)

        # 4. Recursively call `_get_related_artists`
        _get_related_artists(related_artist_uri, connections, metadata, attributes,
                             scrapper, limit, min_popularity, verbose, include_collaborators, breakpoint)


def _to_edgelist(connections, fname):
    """Write dictionary of connections to a NetworkX-compatible weighted edgelist."""

    with open('{}/{}.edgelist'.format('derivatives', fname), 'a') as f:
        for artist, values in connections.items():
            for related_arist in values:
                f.write("{} {}\n".format(artist, related_arist))


def _to_pickle(metadata, fname):
    """Pickle dictionary of metadata."""

    with open('{}/{}.pkl'.format('derivatives', fname), 'wb') as f:
        pickle.dump(metadata, f, pickle.HIGHEST_PROTOCOL)


def write_edgelist(artist, include_collaborators=True, limit=5, min_popularity=65, verbose=False, fname=None, breakpoint=None):
    """
    Main function for constructing graph of related artists.
    `artist` should be a Spotify URI.
    """

    # Initialize Spotify object with proper authentification
    spotify = setup_scrapper(CLIENT_ID, CLIENT_SECRET)

    # Initialize empty dictionaries for outputs
    connections = {}
    metadata = {}

    # Get the input artist's name
    if fname is None:
        artist = scrapper.artist(uri)
        fname = artist['name']

    # Run the search
    try:
        _get_related_artists(artist,
                             connections,
                             metadata,
                             attributes=['name', 'popularity'],
                             scrapper=spotify,
                             limit=limit,
                             min_popularity=min_popularity,
                             include_collaborators=include_collaborators,
                             breakpoint=breakpoint,
                             verbose=verbose)

    except Exception as error:
        print(repr(error))

    # Save the outputs
    print("Saving edgelist...")
    _to_edgelist(connections, fname='{}'.format(fname))
    print("Saving attributes...")
    _to_pickle(metadata, fname='{}_attributes'.format(fname))
