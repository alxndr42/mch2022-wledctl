import os
import time

import buttons
import display
import easydraw
import keyboard
import listbox
import mch22
import system
import ujson
import wifi

try:
    from .wled import WLED  # Hatchery
except Exception:
    from wled import WLED  # Simulator


if system.currentApp().startswith('/'):
    CONFIG = f'{system.currentApp()}/config.json'  # Hatchery
else:
    CONFIG = '/apps/python/wledctl.json'  # Simulator


_config = {
    'host': '4.3.2.1',
    'wifi': False,
    'wifi_name': '',
    'wifi_pass': '',
}
_wled = None

_listbox = listbox.List(0, 0, display.width() - 1, display.height() - 1)
_listbox.bgColor = display.BLUE
_listbox.fgColor = display.WHITE


# Config


def read_config():
    print('read_config')
    global _config
    try:
        with open(CONFIG, 'r') as file:
            _config = ujson.load(file)
    except Exception:
        pass


def write_config():
    print('write_config')
    with open(CONFIG, 'w') as file:
        ujson.dump(_config, file)


# Network


def connect_to_wifi():
    print('connect_to_wifi')
    if _config['wifi']:
        if _config['wifi_pass']:
            wifi.connect(_config['wifi_name'], _config['wifi_pass'])
        else:
            wifi.connect(_config['wifi_name'])
    else:
        wifi.connect()
    if not wifi.wait():
        raise Exception('WiFi connection timeout.')


# UI


def draw_listbox(entries, callbacks):
    _listbox.enabled(False)
    _listbox.clear()
    for entry in entries:
        _listbox.add_item(entry)
    _listbox.enabled(True)
    _listbox.draw()
    display.flush()

    def on_up(pressed):
        if pressed:
            _listbox.moveUp()
            display.flush()

    def on_down(pressed):
        if pressed:
            _listbox.moveDown()
            display.flush()

    def on_a(pressed):
        if pressed:
            index = _listbox.selected_index()
            text = _listbox.selected_text()
            callbacks[index](text)

    buttons.attach(buttons.BTN_UP, on_up)
    buttons.attach(buttons.BTN_DOWN, on_down)
    buttons.attach(buttons.BTN_A, on_a)


def draw_setup():
    host = _config['host']
    custom_wifi = _config['wifi']
    wifi_name = _config['wifi_name']
    wifi_pass = _config['wifi_pass']
    entries = [
        'Connect',
        f'Host: {host}',
        f'Custom WiFi: {"Yes" if custom_wifi else "No"}',
    ]
    callbacks = [
        cb_setup_connect,
        cb_setup_host,
        cb_setup_custom_wifi,
    ]
    if custom_wifi:
        entries.append(f'Network: {wifi_name if wifi_name else "None"}')
        callbacks.append(cb_setup_network)
        entries.append(f'Password: {"****" if wifi_pass else "None"}')
        callbacks.append(cb_setup_password)
    draw_listbox(entries, callbacks)


def draw_controls():
    entries = [
        f'Power: {"On" if _wled.on else "Off"}',
        f'Preset: {_wled.preset}',
    ]
    callbacks = [
        cb_controls_power,
        cb_controls_preset,
    ]
    draw_listbox(entries, callbacks)


def draw_presets():
    presets = _wled.presets
    entries = presets
    callbacks = [cb_presets_accept for p in presets]
    draw_listbox(entries, callbacks)


def fail(message):
    easydraw.messageCentered(message)
    time.sleep(3)
    mch22.exit_python()


# Callbacks


def cb_setup_connect(text):
    print('cb_setup_connect')
    try:
        connect_to_wifi()
    except Exception as e:
        print(f'ERROR: {e}')
        fail('WiFi communication error.')
    global _wled
    _wled = WLED(_config['host'])
    try:
        _wled.connect()
    except Exception as e:
        print(f'ERROR: {e}')
        fail('WLED communication error.')
    draw_controls()


def cb_setup_host(text):
    print('cb_setup_host')
    keyboard.show('Host', _config['host'], cb_setup_host_accept)


def cb_setup_host_accept(text):
    print('cb_setup_host_accept')
    if text:
        _config['host'] = text
    write_config()
    draw_setup()


def cb_setup_custom_wifi(text):
    print('cb_setup_custom_wifi')
    _config['wifi'] = not _config['wifi']
    write_config()
    draw_setup()


def cb_setup_network(text):
    print('cb_setup_network')
    keyboard.show('Network', _config['wifi_name'], cb_setup_network_accept)


def cb_setup_network_accept(text):
    print('cb_setup_network_accept')
    _config['wifi_name'] = text
    write_config()
    draw_setup()


def cb_setup_password(text):
    print('cb_setup_password')
    keyboard.show('Password', _config['wifi_pass'], cb_setup_password_accept)


def cb_setup_password_accept(text):
    print('cb_setup_password_accept')
    _config['wifi_pass'] = text
    write_config()
    draw_setup()


def cb_controls_power(text):
    print('cb_controls_power')
    _wled.on = 'toggle'
    draw_controls()


def cb_controls_preset(text):
    print('cb_controls_preset')
    draw_presets()


def cb_presets_accept(text):
    print('cb_presets_accept')
    _wled.preset = text
    draw_controls()


def on_home(pressed):
    if pressed:
        print('on_home')
        mch22.exit_python()


# Main


read_config()
draw_setup()
buttons.attach(buttons.BTN_HOME, on_home)
