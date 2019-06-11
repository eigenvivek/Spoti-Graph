import pickle
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from requests.exceptions import ConnectionError

import os
from dotenv import load_dotenv, find_dotenv


class NetworkMiner():

    def __init__(
        self,
        include_collaborators=True,
        breadth_limit=5,
        max_pop_size=100,
        min_popularity=65,
        verbose=True,
    ):
        # Object to interface with Spotify API
        self.scrapper = self._setup_scrapper()

        # Search paremeters
        self.include_collaborators = include_collaborators
        self.breadth_limit = breadth_limit
        self.max_pop_size = max_pop_size
        self.min_popularity = min_popularity
        self.verbose = verbose

    def _setup_scrapper(self):
        """Initialize Spotify object with proper authentification.

        Assumes there exists a .env somewhere in the directory that contains
        SPOTIPY_CLIENT_ID and SPOTIPY_CLIENT_SECRET.
        """

        # Find .env and load the entries as environment variables
        dotenv_path = find_dotenv()
        load_dotenv(dotenv_path)
        SPOTIPY_CLIENT_ID = os.environ.get("SPOTIPY_CLIENT_ID")
        SPOTIPY_CLIENT_SECRET = os.environ.get("SPOTIPY_CLIENT_SECRET")

        # Initialize the scrapper
        client_credentials_manager = SpotifyClientCredentials(
            SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET
        )
        spotify = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager
        )

        return spotify

    def _get_artist_metadata(self, uri, attributes):
        """Return well formatted metadata. Fields of interest are specified in
        `attributes`.
        """

        # Search for the artist
        artist = self.scrapper.artist(uri)

        # Collect all valid metadata
        artist_metadata = {}
        for attr in attributes:
            try:
                artist_metadata[attr] = artist[attr]
            except KeyError:
                print("{} is not a valid key".format(attr))

        return artist_metadata

    def _get_collaborators(self, uri):
        """Find artists that the given artist has collaborated with."""

        # Get the top tracks
        top_tracks = self.scrapper.artist_top_tracks(uri)
        top_tracks = top_tracks['tracks'][0:self.breadth_limit]

        # Get the metadata for each artist and store in list
        collaborators = []
        for track in top_tracks:
            for artist in track['artists']:
                target = artist['uri']
                if (target == uri) or (artist in collaborators):
                    continue

                artist = self.scrapper.artist(target)
                collaborators.append(artist)

        return collaborators

    def _get_related_artists(
        self,
        uri,
        connections,
        metadata,
        attributes,
    ):
        """Iterative implementation of breadth-first search."""

        explored, queue = set(), [uri]
        explored.add(uri)

        # While there are artists in the queue:
        while queue:

            # Get the leftmost artist in the queue
            uri = queue.pop(0)

            # Add artist's attributes to metadata
            metadata[uri] = self._get_artist_metadata(
                uri, attributes=attributes
            )
            if self.verbose:
                # Verbose output: "Node <NUMBER>: <ARTIST> (<POPULARITY>)"
                msg = "Node {}: {} ({})".format(
                    len(explored),
                    metadata[uri]['name'],
                    metadata[uri]['popularity']
                )
                print(msg)

            # Get up to `self.breadth_limit` related artists
            related = self.scrapper.artist_related_artists(uri)
            related = related['artists'][0:self.breadth_limit]
            related_uri = [artist['uri'] for artist in related]

            # Get up to `self.breadth_limit` collaborators and add unique
            # artists to `related`
            if self.include_collaborators:
                collaborators = self._get_collaborators(uri)
                for artist in collaborators:
                    if artist['uri'] not in related_uri:
                        related.append(artist)

            # Iterate through related artists...
            for artist in related:

                # 1a. Skip unpopular artists
                if int(artist['popularity']) < self.min_popularity:
                    if self.verbose:
                        msg = "\t{} is unpopular ({})".format(
                            artist['name'], artist['popularity']
                        )
                        print(msg)
                    continue

                # 1b. Skip artists that have already been added to the network
                if artist['uri'] in explored:
                    continue

                # 2. Write related artist and weight to connections
                input_artist_uri = str(uri)         # URI of the input artist
                related_artist_uri = artist['uri']  # URI of the related artist
                # TODO: find better way of initializing new keys in dictionary
                try:
                    connections[input_artist_uri] += [related_artist_uri]
                except KeyError:
                    connections[input_artist_uri] = [related_artist_uri]

                # 3. Save the related artist's attributes
                metadata[related_artist_uri] = self._get_artist_metadata(
                    related_artist_uri, attributes=attributes)

                # 4. Add the artist's uri to the set of explored artists and
                # to the queue
                explored.add(artist['uri'])
                queue.append(artist['uri'])
                if self.verbose:
                    # Verbose output: "Node <NUMBER>: <ARTIST> (<POPULARITY>)"
                    msg = "Node {}: {} ({})".format(
                        len(explored),
                        metadata[related_artist_uri]['name'],
                        metadata[related_artist_uri]['popularity']
                    )
                    print(msg)

                # 5. Check if the max_pop_size has been hit
                if len(explored) == self.max_pop_size:
                    raise RuntimeError("Maximum population size reached.")

    def _to_edgelist(self, connections, fname):
        """Write dictionary of connections to a NetworkX-compatible weighted
        edgelist.
        """

        with open('{}/{}.edgelist'.format('derivatives', fname), 'a') as f:
            for artist, values in connections.items():
                for related_arist in values:
                    f.write("{} {}\n".format(artist, related_arist))

    def _to_pickle(self, metadata, fname):
        """Pickle dictionary of metadata."""

        with open('{}/{}.pkl'.format('derivatives', fname), 'wb') as f:
            pickle.dump(metadata, f, pickle.HIGHEST_PROTOCOL)

    def write_edgelist(
        self,
        artist,
        attributes=['name', 'popularity'],
        fname=None,
    ):
        """Main function for constructing graph of related artists.
        `artist` should be a Spotify URI.
        """

        # Initialize empty dictionaries for outputs
        connections = {}
        metadata = {}

        # Get the input artist's name
        if fname is None:
            fname = self.scrapper.artist(artist)['name']

        # Run the search
        try:
            self._get_related_artists(
                artist,
                connections,
                metadata,
                attributes=attributes,
            )
        except RuntimeError as error:
            print(repr(error))
        except ConnectionError as error:
            print(repr(error))
            print("Saving current progress...")

        # Save the outputs
        print("Saving edgelist...")
        self._to_edgelist(connections, fname='{}'.format(fname))
        print("Saving attributes...")
        self._to_pickle(metadata, fname='{}_attributes'.format(fname))
