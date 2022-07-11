try:
    import urequests as http
except Exception:
    import requests as http


_WLED_STATE = 'http://{}/json/state'
_WLED_PRESETS = 'http://{}/presets.json'


class WLED():

    def __init__(self, host):
        """Constructor

        host - WLED hostname or IP address.
        """
        self._host = host
        self._connected = False
        self._state = None
        self._presets = None

    def connect(self):
        """Connect to WLED and read state information."""
        res = http.get(_WLED_STATE.format(self._host))
        self._check_status(res)
        self._state = res.json()
        res = http.get(_WLED_PRESETS.format(self._host))
        self._check_status(res)
        data = res.json()
        presets = {v['n']: int(k) for k, v in data.items() if 'n' in v}
        self._presets = {n: presets[n] for n in sorted(presets.keys())}
        self._steserp = {presets[n]: n for n in sorted(presets.keys())}
        self._connected = True

    @property
    def on(self):
        """Return True if WLED is turned on."""
        self._check_connected()
        return self._state.get('on', False)

    @on.setter
    def on(self, value):
        """Turn WLED on/off.

        Value can be a bool or 'toggle'.
        """
        self._check_connected()
        url = _WLED_STATE.format(self._host)
        res = http.post(url, json={'on': value, 'v': True})
        self._check_status(res)
        self._state = res.json()

    @property
    def preset(self):
        """Return the active preset name, or None."""
        self._check_connected()
        id_ = self._state.get('ps', -1)
        return self._steserp.get(id_)

    @preset.setter
    def preset(self, value):
        """Activate a preset by name."""
        self._check_connected()
        id_ = self._presets.get(value)
        if id_ is not None:
            url = _WLED_STATE.format(self._host)
            res = http.post(url, json={'ps': id_, 'v': True})
            self._check_status(res)
            self._state = res.json()

    @property
    def presets(self):
        """Return a list of preset names."""
        self._check_connected()
        return list(self._presets.keys())

    def cycle_preset(self, offset):
        """Activate a next/previous preset."""
        self._check_connected()
        presets = self.presets
        if not presets:
            return
        try:
            index = presets.index(self.preset)
            preset = presets[(index + offset) % len(presets)]
        except ValueError:
            preset = presets[0]
        self.preset = preset

    def _check_connected(self):
        """Raise an exception if not connected."""
        if not self._connected:
            raise Exception('Not connected.')

    @staticmethod
    def _check_status(res):
        """Raise an exception if the response status is above 2xx."""
        if res.status_code >= 300:
            raise Exception(f'Status code: {res.status_code}')
