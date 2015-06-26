from plugin.sync.core.enums import SyncData, SyncMedia, SyncMode
from plugin.sync.handlers.core import DataHandler, PushHandler, bind
from plugin.sync.handlers.watched.base import WatchedHandler

import logging

log = logging.getLogger(__name__)


class Base(PushHandler, WatchedHandler):
    pass


class Movies(Base):
    media = SyncMedia.Movies

    @bind('added', [SyncMode.Full, SyncMode.Push])
    def on_added(self, key, p_guid, p_item, p_value, t_value, **kwargs):
        log.debug('Movies.on_added(%r, ...)', key)

        if t_value:
            return

        self.store_movie('add', p_guid,
            p_item,
            watched_at=p_value
        )

    @bind('removed', [SyncMode.Full, SyncMode.Push])
    def on_removed(self, key, t_value, **kwargs):
        log.debug('Movies.on_removed(%r, ...)', key)


class Episodes(Base):
    media = SyncMedia.Episodes

    @bind('added', [SyncMode.Full, SyncMode.Push])
    def on_added(self, key, p_guid, identifier, p_show, p_value, t_value, **kwargs):
        log.debug('Episodes.on_added(%r, ...)', key)

        if t_value:
            return

        self.store_episode('add', p_guid,
            identifier, p_show,
            watched_at=p_value
        )

    @bind('removed', [SyncMode.Full, SyncMode.Push])
    def on_removed(self, key, t_value, **kwargs):
        log.debug('Episodes.on_removed(%r, ...)', key)


class Push(DataHandler):
    data = SyncData.Watched
    mode = SyncMode.Push

    children = [
        Movies,
        Episodes
    ]
