from datetime import datetime, timezone
from enum import Enum


class RenderFieldTools:

    @staticmethod
    def render_http_verb_badges(verbs):
        """
        Render a list of HTTP verbs as HTML <span> badges with background
        colors according to the mapping:

          GET       → blue
          POST      → green
          PUT       → orange
          DELETE    → red
          PATCH     → yellow
          WEBSOCKET → purple (with special styling)
          HEAD      → gray
          OPTIONS   → gray
          TRACE     → gray

        Any unrecognized verb also falls back to gray.
        """
        # 1. define your color map
        color_map = {
            'GET': 'blue',
            'POST': 'green',
            'PUT': 'orange',
            'DELETE': 'red',
            'PATCH': 'yellow',
            'WEBSOCKET': 'purple',
        }

        # 2. build badges
        badges = []
        for raw in verbs:
            verb = raw.upper()
            color = color_map.get(verb, 'gray')
            # inline style for background + ensure text is readable
            badge = f'<span class="badge badge-outline text-{color}">{verb}</span>'
            badges.append(badge)

        # 3. return one HTML string you can drop into your page
        return ' '.join(badges)

    @staticmethod
    def render_enum(value):
        if isinstance(value, Enum):
            label = value.name.title()
            badge_class = value.badge_class if value.badge_class else 'badge-success'
            return f'<span class="badge {badge_class}">{label}</span>'
        return value

    @staticmethod
    def render_boolean(value):
        return '<span class="badge bg-green">Yes</span>' if value else '<span class="badge bg-red">No</span>'

    @staticmethod
    def render_icon(value):
        return f'<i class="{value}"></i>'

    @staticmethod
    def render_datetime(value):
        return value.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if isinstance(value, datetime) else ""

    @staticmethod
    def pretty_time_delta(seconds, show_sign: bool = False):
        """
        Convert a number of seconds to a compact human friendly delta string.

        Parameters:
        - seconds: int | float. The delta in seconds (can be negative).
        - show_sign: bool. If True, include a leading '+' for positive deltas and '-' for negative ones.
          By default (False), only negative deltas will include a leading '-' while positive/zero will have no sign.
        """
        sign_string = '-' if seconds < 0 else ('+' if show_sign and seconds > 0 else '')
        seconds = abs(int(seconds))
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        if days > 0:
            return '%s%dd%dh%dm%ds' % (sign_string, days, hours, minutes, seconds)
        elif hours > 0:
            return '%s%dh%dm%ds' % (sign_string, hours, minutes, seconds)
        elif minutes > 0:
            return '%s%dm%ds' % (sign_string, minutes, seconds)
        else:
            return '%s%ds' % (sign_string, seconds)