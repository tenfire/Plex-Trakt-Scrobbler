from plugin.sync.core.enums import SyncData, SyncMedia, SyncMode
from plugin.sync.handlers.core import DataHandler, PullHandler, bind
from plugin.sync.handlers.ratings.base import RatingsHandler

from plex import Plex
import logging

log = logging.getLogger(__name__)


class Base(PullHandler, RatingsHandler):
    @staticmethod
    def build_action(action, p_item, p_value, t_value, **kwargs):
        data = {}

        if action in ['added', 'changed']:
            if type(t_value) is tuple:
                data['t_previous'], data['t_value'] = t_value
            else:
                data['t_value'] = t_value

        if action == 'changed':
            data['p_value'] = p_value

        data.update(kwargs)
        return data

    @staticmethod
    def rate(key, value):
        return Plex['library'].rate(key, value)

    #
    # Handlers
    #

    @bind('added')
    def on_added(self, key, t_value, **kwargs):
        log.debug('%s.on_added(%r, %r)', self.media, key, t_value)

        return self.rate(key, t_value)

    @bind('changed', [SyncMode.Full, SyncMode.FastPull])
    def on_changed(self, key, p_value, t_previous, t_value, **kwargs):
        log.debug('%s.on_changed(%r, %r, %r, %r)', self.media, key, p_value, t_previous, t_value)

        return self.rate(key, t_value)

    @bind('removed', [SyncMode.Full, SyncMode.FastPull])
    def on_removed(self, key, **kwargs):
        log.debug('%s.on_removed(%r)', self.media, key)

        return self.rate(key, 0)


class Movies(Base):
    media = SyncMedia.Movies


class Episodes(Base):
    media = SyncMedia.Episodes


class Pull(DataHandler):
    data = SyncData.Ratings
    mode = [SyncMode.FastPull, SyncMode.Pull]

    children = [
        Movies,
        Episodes
    ]
