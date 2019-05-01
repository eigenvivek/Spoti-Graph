from pprint import pprint

import pickle

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from credentials import CLIENT_ID, CLIENT_SECRET


def setup_scrapper(client_id, client_secret):
    client_credentials_manager = SpotifyClientCredentials(
        client_id, client_secret)
    spotify = spotipy.Spotify(
        client_credentials_manager=client_credentials_manager)

    return spotify


def _get_artist_metadata(uri, scrapper, attributes):

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


def _get_related_artists(uri, connections, metadata, attributes, scrapper, limit, min_popularity):
    """Recursive implementation of depth-first search."""

    # Add input artist's attributes to metadata
    metadata[uri] = _get_artist_metadata(
        uri, scrapper=scrapper, attributes=attributes)

    # Get up to `limit` related artists and associated metadata, organized in a list
    related = scrapper.artist_related_artists(uri)
    pprint("PARENT {}:".format(metadata[uri]['name']))
    related = related['artists'][0:limit]

    # Iterate through related artists...
    for index, artist in enumerate(related):

        # 1a. Skip unpopular artists
        if int(artist['popularity']) < min_popularity:
            print("    {} is unpopular ({})".format(
                artist['name'], artist['popularity']))
            continue

        # 1b. Skip artists already adjacent to the input artist
        try:
            neighbors = [adjacent_uri for (
                adjacent_uri, _) in connections[uri]]
            if artist['uri'] in neighbors:
                continue
        except:
            pass

        # 2. Write related artist and weight to connections
        input_artist_uri = str(uri)         # URI of the input artist
        related_artist_uri = artist['uri']  # URI of the related artist
        edgeweight = limit - index          # Weight of connection between artists
        try:
            connections[input_artist_uri] += [(related_artist_uri, edgeweight)]
        except KeyError:
            connections[input_artist_uri] = [(related_artist_uri, edgeweight)]

        # 3. Save the related artist's attributes
        metadata[related_artist_uri] = _get_artist_metadata(
            related_artist_uri, scrapper=scrapper, attributes=attributes)

        # 4. Recursively call `_get_related_artists`
        _get_related_artists(related_artist_uri, connections,
                             metadata, attributes, scrapper, limit, min_popularity)


def _to_edgelist(connections, fname):
    with open('{}/{}.edgelist'.format('derivatives', fname), 'a') as f:
        for artist, values in connections.items():
            for related_arist, weight in values:
                f.write("{} {} {}\n".format(artist, related_arist, weight))


def _to_pickle(metadata, fname):
    with open('{}/{}.pkl'.format('derivatives', fname), 'wb') as f:
        pickle.dump(metadata, f, pickle.HIGHEST_PROTOCOL)


def write_edgelist(artist, file_identifier, limit=5, min_popularity=65):
    """
    `artist` should be a Spotify URI.
    """

    # Initialize Spotify object with proper authentification
    spotify = setup_scrapper(CLIENT_ID, CLIENT_SECRET)

    # Initialize empty dictionaries for outputs
    connections = {}
    metadata = {}

    # Run the search
    _get_related_artists(artist, connections, metadata, attributes=['name', 'popularity'],
                         scrapper=spotify, limit=limit, min_popularity=min_popularity)

    # Save the outputs
    print("Saving edgelist...")
    _to_edgelist(connections, fname='{}'.format(file_identifier))
    print("Saving attributes...")
    _to_pickle(metadata, fname='{}_attributes'.format(file_identifier))
