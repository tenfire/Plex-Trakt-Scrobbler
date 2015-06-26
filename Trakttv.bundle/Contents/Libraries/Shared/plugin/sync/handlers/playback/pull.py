from plugin.sync.core.enums import SyncData, SyncMedia, SyncMode
from plugin.sync.handlers.core import DataHandler, PullHandler, bind
from plugin.sync.handlers.playback.base import PlaybackHandler

from plex import Plex
import logging

log = logging.getLogger(__name__)


class Base(PullHandler, PlaybackHandler):
    @staticmethod
    def build_action(action, p_item, p_value, t_value, **kwargs):
        data = {}

        # Retrieve plex parameters
        p_duration = p_item.get('part', {}).get('duration')

        if p_duration is None:
            # Missing data required for playback syncing
            return None

        data['p_value'] = p_item.get('settings', {}).get('view_offset')

        # Set arguments for action
        if action in ['added', 'changed']:
            # Calculate trakt view offset
            t_value = p_duration * (float(t_value) / 100)
            t_value = int(round(t_value, 0))

            data['p_duration'] = p_duration
            data['t_value'] = t_value

            if t_value <= 60 * 1000:
                # Ignore progress below one minute
                return None

        data.update(kwargs)
        return data

    @staticmethod
    def update_progress(rating_key, time, duration):
        return Plex[':/timeline'].update(rating_key, 'stopped', time, duration)

    #
    # Handlers
    #

    @bind('added')
    def on_added(self, key, p_duration, p_value, t_value, **kwargs):
        log.debug('%s.on_added(%s, %r, %r, %r)', self.media, key, p_duration, p_value, t_value)

        if p_value is not None and p_value > t_value:
            # Already updated progress
            return

        return self.update_progress(key, t_value, p_duration)

    @bind('changed')
    def on_changed(self, key, p_duration, p_value, t_value, **kwargs):
        log.debug('%s.on_changed(%s, %r, %r, %r)', self.media, key, p_duration, p_value, t_value)

        if p_value > t_value:
            # Ignore change, plex progress has advanced
            return

        return self.update_progress(key, t_value, p_duration)


class Movies(Base):
    media = SyncMedia.Movies


class Episodes(Base):
    media = SyncMedia.Episodes


class Pull(DataHandler):
    data = SyncData.Playback
    mode = [SyncMode.FastPull, SyncMode.Pull]

    children = [
        Movies,
        Episodes
    ]
