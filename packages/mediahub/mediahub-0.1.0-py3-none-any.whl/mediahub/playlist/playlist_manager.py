# src/playlist/playlist_manager.py
class PlaylistManager:
    def __init__(self):
        self.playlists = {}

    def create_playlist(self, name):
        self.playlists[name] = []

    def add_to_playlist(self, name, item):
        if name in self.playlists:
            self.playlists[name].append(item)

    def remove_from_playlist(self, name, item):
        if name in self.playlists:
            self.playlists[name].remove(item)

    def get_playlist(self, name):
        return self.playlists.get(name, [])
