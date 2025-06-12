import pyemvue
import datetime
import time
import os
from pyemvue.enums import Scale, Unit

# Cache variables
_cache_data = None
_cache_timestamp = 0
CACHE_DURATION = 180  # 180 seconds

def print_recursive(usage_dict, info, depth=0, result=None):
    if result is None:
        result = []

    for gid, device in usage_dict.items():
        for channelnum, channel in device.channels.items():
            name = channel.name
            if name == 'Main':
                name = info[gid].device_name
            usage = channel.usage if channel.usage is not None else 0.0
            usage_str = f'{usage:.4f} kwh'
            line = f"{'→' * depth}{gid}|{channelnum}|{name}|{usage_str}"
            result.append(line)
            if channel.nested_devices:
                print_recursive(channel.nested_devices, info, depth+1, result)

    return result


def get_all(vue):
    global _cache_data, _cache_timestamp

    current_time = time.time()
    # Check if cache is valid
    if _cache_data is not None and (current_time - _cache_timestamp) < CACHE_DURATION:
        print(f"[DEBUG] Using cached data (age: {current_time - _cache_timestamp:.1f}s)")
        return _cache_data

    # Cache is expired or doesn't exist, fetch new data
    devices = vue.get_devices()
    device_gids = []
    device_info = {}
    for device in devices:
        if not device.device_gid in device_gids:
            device_gids.append(device.device_gid)
            device_info[device.device_gid] = device
        else:
            device_info[device.device_gid].channels += device.channels

    device_usage_dict = vue.get_device_list_usage(deviceGids=device_gids, instant=None, scale=Scale.DAY.value, unit=Unit.KWH.value)
    result = ['device_gid channel_num name usage unit']
    result.extend(print_recursive(device_usage_dict, device_info))

    # Update cache
    _cache_data = result
    _cache_timestamp = current_time
    print(f"[DEBUG] Fetched fresh data from API, cache updated")

    return result, _cache_timestamp

def get_daily(vue):
    devices = vue.get_devices()

    usage_over_time, start_time = vue.get_chart_usage(devices[0].channels[0], datetime.datetime.now(datetime.timezone.utc)-datetime.timedelta(days=7), datetime.datetime.now(datetime.timezone.utc), scale=Scale.DAY.value, unit=Unit.KWH.value)

    return usage_over_time

def login_vue():
    vue = pyemvue.PyEmVue()
    username = os.environ.get('EMPORIA_USERNAME', 'daryl@darylchymko.ca')
    password = os.environ.get('EMPORIA_PASSWORD')
    vue.login(username=username, password=password, token_storage_file='keys.json')
    return vue;