class WLED():

    def __init__(self, host):
        self._host = host
        self._on = True
        self._preset = 'Foo'
        self._presets = ['Foo', 'Bar', 'Baz']

    def connect(self):
        if self._host != 'error':
            print(f'Connected to {self._host}')
        else:
            raise Exception('Could not connect to WLED.')

    @property
    def on(self):
        return self._on

    @on.setter
    def on(self, value):
        if type(value) == bool:
            self._on = value
        else:
            self._on = not self._on

    @property
    def preset(self):
        return self._preset

    @preset.setter
    def preset(self, value):
        if value in self._presets:
            self._preset = value

    @property
    def presets(self):
        return list(self._presets)

    def cycle_preset(self, offset):
        """Activate a next/previous preset."""
        presets = self.presets
        if not presets:
            return
        try:
            index = presets.index(self.preset)
            preset = presets[(index + offset) % len(presets)]
        except ValueError:
            preset = presets[0]
        self.preset = preset
