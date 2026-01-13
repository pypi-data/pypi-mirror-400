import json
import os
import sys
import tomllib
from datetime import datetime
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import humanize

factory_defaults: dict[str, dict[str, str | int | None]] = {
    'ntfy': {
        'url': 'https://ntfy.sh',
        'token': None,
        'priority': 'default',
        'title-template': '{title}',
        'body-template': '{loc} [{humantime}]',
        'issue-open-tag': 'warning',
        'issue-closed-tag': 'heavy_check_mark',
        'pull-open-tag': 'adhesive_bandage',
        'pull-closed-tag': 'x',
        'pull-merged-tag': 'heavy_check_mark',
        'repo-tag': 'hut',
    },
    'forgejo': {
        'max-on-init': 3,
        'request-limit': 50,
        'subject-type': None,
    },
}

forgejo_params = (
    'api-url',
    'token',
    'request-limit',
    'subject-type',
    'max-on-init',
)
ntfy_params = (
    'url',
    'token',
    'topic',
    'priority',
    'issue-open-tag',
    'issue-closed-tag',
    'pull-open-tag',
    'pull-closed-tag',
    'pull-merged-tag',
    'repo-tag',
    'title-template',
    'body-template',
)
template_params = (
    'title',
    'humantime',
    'url',
)


class ForgejoNtfyError(RuntimeError):
    pass


def init(cfg: dict) -> dict:
    """Initialize the state, load/apply all configuration and saved states"""
    # fill configuration with factory defaults, if any such item is unset
    if 'defaults' not in cfg:
        cfg['defaults'] = {}
    for sec in ('ntfy', 'forgejo'):
        cfg_sec = cfg['defaults'].get(sec, {})
        for k, v in factory_defaults[sec].items():
            if k not in cfg_sec:
                cfg_sec[k] = v
        cfg['defaults'][sec] = cfg_sec

    # load the timestamps of the last notification (update) per monitor.
    # this is optional to limit the queries
    try:
        with (xdg_state_home() / 'forgejo-ntfy.json').open('r') as f:
            state = json.load(f)
    except FileNotFoundError:
        state = {}

    # keys are monitor names, values are fully specified configuration
    # for a monitor, all config default logic applied here
    spec = {}
    for monitor in cfg.get('monitors', {}):
        mspec = cfg['monitors'][monitor]
        for sec, plist in (('ntfy', ntfy_params), ('forgejo', forgejo_params)):
            if sec not in mspec:
                mspec[sec] = {}
            for param in plist:
                if sec not in mspec or param not in mspec[sec]:
                    try:
                        mspec[sec][param] = cfg['defaults'][sec][param]
                    except KeyError as e:
                        msg = (
                            f"Parameter '{sec}.{param}' is required,"
                            ' but it is not set and no default is configured'
                        )
                        raise ForgejoNtfyError(msg) from e
        # pull the latest timestamp from any previous state
        mspec['forgejo']['latest'] = (
            None if monitor not in state else datetime.fromisoformat(state[monitor])
        )
        spec[monitor] = mspec
    return spec


def proc_monitor(spec: dict) -> datetime | None:
    """Process a single monitor, return latest notification timestamp"""

    fapi_cfg = spec['forgejo']
    fapi_url = f'{fapi_cfg["api-url"]}/v1/notifications'
    fapi_headers = {
        'Authorization': f'token {fapi_cfg["token"]}',
    }
    fapi_params = {
        'limit': fapi_cfg['request-limit'],
    }
    if fapi_cfg['subject-type']:
        fapi_params['subject-type'] = fapi_cfg['subject-type']
    if fapi_cfg['latest']:
        fapi_params['since'] = fapi_cfg['latest'].isoformat()
    latest = fapi_cfg['latest']
    page = 1
    while True:
        req = httpx.get(
            fapi_url,
            params=dict(fapi_params, page=page),
            headers=fapi_headers,
        )
        notifications = req.json()
        for notification in (
            # when there was no prior state,
            # process at most N notifications to communicate
            # that things are working
            notifications
            if fapi_cfg['latest']
            else notifications[: fapi_cfg['max-on-init']]
        ):
            ts = proc_notification(spec, notification, fapi_cfg['latest'])
            if latest is None or (ts and ts > latest):
                latest = ts
        if not notifications or fapi_cfg['latest'] is None:
            break
        page += 1
    return latest


def notification_rec2template_blocks(rec: dict, ts: datetime) -> dict:
    """Prepare placeholder values for/from a particular notification"""

    split_url = urlsplit(rec['subject']['html_url'])
    return {
        'title': rec['subject']['title'],
        'url': rec['subject']['html_url'],
        'loc': f'{split_url.hostname}{split_url.path}',
        'humantime': humanize.naturaltime(ts),
    }


def proc_notification(
    spec: dict,
    notification: dict,
    thresh_ts: datetime | None,
) -> datetime:
    """Process a single notification, return timestamp"""
    ts = datetime.fromisoformat(notification['updated_at'])
    if thresh_ts and ts <= thresh_ts:
        return ts

    ntfy_spec = spec['ntfy']
    blocks = notification_rec2template_blocks(notification, ts)
    title = ntfy_spec['title-template'].format(**blocks)
    body = ntfy_spec['body-template'].format(**blocks)

    subj = notification['subject']
    tags = []
    stype = subj['type'].lower()
    sstate = subj['state'].lower()
    if stype == 'pull':
        if sstate == 'open':
            tags.append(ntfy_spec['pull-open-tag'])
        elif sstate == 'closed':
            tags.append(ntfy_spec['pull-closed-tag'])
        elif sstate == 'merged':
            tags.append(ntfy_spec['pull-merged-tag'])
    elif stype == 'issue':
        if sstate == 'open':
            tags.append(ntfy_spec['issue-open-tag'])
        elif sstate == 'closed':
            tags.append(ntfy_spec['issue-closed-tag'])
    elif stype == 'repository':
        tags.append(ntfy_spec['repo-tag'])

    n_props = {
        'Title': title,
        'Click': subj['html_url'],
        'Priority': ntfy_spec['priority'],
        'Tags': ','.join(t.strip() for t in tags),
    }
    print(f'POST {blocks["loc"]}', file=sys.stdout)  # noqa: T201
    res = httpx.post(
        f'{ntfy_spec["url"]}/{ntfy_spec["topic"]}',
        data=body,
        headers=n_props,
        auth=('', spec['ntfy']['token']) if spec['ntfy']['token'] else None,
    )
    res.raise_for_status()
    return ts


def main():
    """Entrypoint. Thing wrapper, see `_main()`"""
    try:
        return _main()
    except ForgejoNtfyError as e:
        print(f'{e}', file=sys.stderr)  ## noqa: T201
        sys.exit(1)


def _main():
    """Actual entrypoint implementation"""
    with (xdg_config_home() / 'forgejo-ntfy.toml').open('rb') as f:
        cfg = tomllib.load(f)

    if cfg.get('locale'):
        humanize.i18n.activate(cfg['locale'])
    monitors = init(cfg)

    state = {}
    for mname, mspec in monitors.items():
        ts = proc_monitor(mspec)
        if ts is not None:
            state[mname] = ts.isoformat()

    state_dir = xdg_state_home()
    state_dir.mkdir(exist_ok=True)
    with (state_dir / 'forgejo-ntfy.json').open('w') as f:
        json.dump(state, f, sort_keys=True)


# Below is taken from https://github.com/srstevenson/xdg-base-dirs
# Copyright © Scott Stevenson <scott@stevenson.io>
# https://spdx.org/licenses/ISC.html


def _path_from_env(variable: str, default: Path) -> Path:
    """Read an environment variable as a path.

    The environment variable with the specified name is read, and its
    value returned as a path. If the environment variable is not set, is
    set to the empty string, or is set to a relative rather than
    absolute path, the default value is returned.

    Args:
        variable: Name of the environment variable.
        default: Default value.

    Returns:
        Value from environment or default.

    """
    if (value := os.environ.get(variable)) and (path := Path(value)).is_absolute():
        return path
    return default


def xdg_config_home() -> Path:
    """Return a Path corresponding to XDG_CONFIG_HOME."""
    return _path_from_env('XDG_CONFIG_HOME', Path.home() / '.config')


def xdg_state_home() -> Path:
    """Return a Path corresponding to XDG_STATE_HOME."""
    return _path_from_env('XDG_STATE_HOME', Path.home() / '.local' / 'state')
