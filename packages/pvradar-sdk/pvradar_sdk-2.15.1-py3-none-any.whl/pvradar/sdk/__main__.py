from getpass import getpass
import os
from sys import stdout
import argparse
import sys


from .common.exceptions import PvradarSdkError
from .caching.caching_factory import make_kv_storage
from .caching.kv_storage.kv_storage_with_expiration_adaptor import KVStorageWithExpirationAdaptor
from .common.settings import SdkSettings, get_settings_file_path
from .client.client import PvradarClient
from .client.dock.dock_sync_client import DockSyncClient
from . import __version__


def _diagnostics() -> int:
    error_count = 0
    print(f'\nPVRADAR SDK ({__version__}) diagnostics\n')

    settings = SdkSettings.instance()
    verify = settings.httpx_verify
    if verify is True or verify is False:
        verify_str = str(verify)
    else:
        verify_str = verify.__class__.__name__
    print('   verify:', verify_str)

    if settings.outlet_token:
        if settings.outlet_token == settings.platform_token:
            print('   API key is set')
        else:
            print('   token set but customized for outlet')
    else:
        error_count += 1
        print('   API key is NOT set')

    if settings.outlet_token:
        print('   outlet summary:', end=' ')
        stdout.flush()
        try:
            outlet_client = PvradarClient.instance()._get_outlet_client()
            summary = outlet_client.get_json('util/summary')
            assert isinstance(summary, dict), f'Unexpected response type: {type(summary)}'
            assert 'api_version' in summary, 'API version not found in summary'
            print('OK', summary.get('api_version'))
        except Exception as e:
            error_count += 1
            print(f'failed: {e}')
    else:
        print('skipping outlet summary test')

    print('   platform status:', end=' ')
    stdout.flush()
    try:
        platform_client = PvradarClient.instance()._get_platform_client()
        response = platform_client.get_json('pvwave-util/version')
        assert isinstance(response, dict), f'Unexpected response type: {type(response)}'
        assert 'foundation' in response, 'foundation not found in summary'
        assert 'hub' in response, 'hub not found in summary'
        print('OK', response.get('foundation'), response.get('hub'))
    except Exception as e:
        error_count += 1
        print(f'failed: {e}')

    print('   dock status:', end=' ')
    stdout.flush()
    try:
        dock_client = DockSyncClient()
        response = dock_client.get_json('util/self')
        assert isinstance(response, dict), f'Unexpected response type: {type(response)}'
        for key in ('v', 'org_ids', 'ha', 'ho'):
            if key in response and response[key] != []:
                print(f'{key}:{response[key]} ', end='')
        print('... OK')
    except Exception as e:
        error_count += 1
        print(f'failed: {e}')

    if error_count > 0:
        print(f'\n{error_count} errors occurred\n')
    else:
        print('\nAll tests passed\n')
    return error_count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='pvradar.sdk', description='CLI for pvradar SDK', usage='python -m pvradar.sdk [-hv] {command}'
    )

    truncate_choice = 'cache_truncate'
    clean_expired_choice = 'cache_clean_expired'
    api_key_choice = 'api_key'
    diagnostics = 'diagnostics'
    settings_command = 'settings'
    command_choices = [truncate_choice, clean_expired_choice, api_key_choice, diagnostics, settings_command]

    parser.add_argument('command', choices=command_choices)

    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    parser.add_argument(
        '--disable-httpx-verify',
        action='store_true',
        help='set verify=False when making requests with httpx',
    )
    args = parser.parse_args()
    if args.command == truncate_choice:
        storage = make_kv_storage(settings=SdkSettings.instance())
        storage.truncate()
        print('cache truncated:', storage.__class__.__name__)
    elif args.command == clean_expired_choice:
        kv_storage = make_kv_storage(settings=SdkSettings.instance())
        if isinstance(kv_storage, KVStorageWithExpirationAdaptor):
            print(f'{kv_storage.clean_expired()} expired keys removed')
        else:
            raise NotImplementedError(
                f'Command {clean_expired_choice} is not supported for {kv_storage}.'
                f' It should be a subclass of KVStorageWithExpirationAdaptor'
            )
    elif args.command == api_key_choice:
        try:
            print('args', args)
            api_key = getpass('Enter your API key or press Ctrl+C to cancel: ')
            PvradarClient.set_api_key(api_key, disable_httpx_verify=args.disable_httpx_verify)
            print('API key set successfully!')
        except KeyboardInterrupt:
            print('\nAPI key setting cancelled by user')
            exit(130)
        except PvradarSdkError as e:
            print(f'Error: {e}')
            exit(1)
    elif args.command == diagnostics:
        error_count = _diagnostics()
        os._exit(error_count)
    elif args.command == settings_command:
        file_path = get_settings_file_path()
        printed_path = f'"{file_path}"' if ' ' in str(file_path) else file_path
        print('Settings file path:', printed_path, file=sys.stderr)
        print(file=sys.stderr)

        if file_path.exists():
            with open(file_path, 'r') as f:
                print(f.read())
        else:
            print('*** does NOT exist!', file=sys.stderr)
            sys.exit(1)
    else:
        raise ValueError(f'Unexpected command: {args.command}. Expected one of {command_choices}')
