# coding: utf-8

import os
import sys
import logging
import time
import json
import base64
import pprint
import datetime
import subprocess
from pathlib import Path
from optparse import OptionParser

BASE_DIR = os.path.dirname(__file__)
DATA_DIR = os.environ.get('STATUS_DATA_DIR') or os.path.join(BASE_DIR, 'data')
TEMPLATE_DIR = (
    os.environ.get('STATUS_TEMPLATE_DIR') or os.path.join(BASE_DIR, 'template')
)
CONFIG_FILE = (
    os.environ.get('STATUS_CONFIG_FILE') or
    os.path.join(DATA_DIR, 'config.env')
)
ERROR_CONFIG = 'ERROR_CONFIG'
ERROR_RUN = 'ERROR_RUN'

STATUS_CONFIG_TIMEOUT = int(os.environ.get('STATUS_CONFIG_TIMEOUT') or 10)
STATUS_CONFIG_INTERVAL = int(os.environ.get('STATUS_CONFIG_INTERVAL') or 30)

logger = logging.getLogger('self-status-page')
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def read_config():
    config_lines = []
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            for line in f:
                if line and line.startswith('STATUS'):
                    config_lines.append(line.strip())
    for key, line in os.environ.items():
        if key.startswith('STATUS'):
            config_lines.append(key + '=' + line.strip())

    configs = {}
    for line in config_lines:
        if '=' not in line:
            continue
        index = line.index('=')
        key = line[0:index]
        value = line[index + 1:]
        if key and value:
            configs[key] = value

    task_groups = {
        'SERVICES': {
            'name': 'Services',
            'tasks': [],
        }
    }
    task_groups_map = {}
    for key, value in sorted(configs.items()):
        if key.startswith('STATUSGROUP_') and key.endswith('_NAME'):
            group_id = key.removeprefix('STATUSGROUP_').removesuffix('_NAME')
            task_groups.setdefault(group_id, {
                'name': value,
                'tasks': [],
            })
            task_groups[group_id]['name'] = value
            tasks = configs.get(f'STATUSGROUP_{group_id}_TASKS') or ''
            task_groups_map.update({
                token.strip(): task_groups[group_id]
                for token in tasks.split(',')
                if token and token.strip()
            })

    for key, value in sorted(configs.items()):
        if key.startswith('STATUS_') and key.endswith('_NAME') and value:
            task_id = key.removeprefix('STATUS_').removesuffix('_NAME')
            group = task_groups_map.get(task_id) or task_groups['SERVICES']
            prefix = f'STATUS_{task_id}_'
            task = dict(
                task_id=task_id,
                **{
                    k.removeprefix(prefix).lower(): v
                    for k, v in configs.items()
                    if k.startswith(prefix) and v
                }
            )
            group['tasks'].append(task)

    task_groups = {k: v for k, v in task_groups.items() if len(v)}
    return task_groups


def build_html():
    task_groups = read_config()
    datas = []
    for file in Path(DATA_DIR).glob('results-*.json'):
        with open(file) as f:
            datas.append(json.load(f))
    if not datas:
        return

    results = [result for data in datas for result in data['results']]
    results = sorted(results, key=lambda x: -x[1])[:1000]
    context = {
        'task_groups': {
            k: {
                'name': v['name'],
                'tasks': [
                    {
                        'name': t['name'],
                        'task_id': t['task_id'],
                        'type': t['type'],
                    }
                    for t in v['tasks']
                ]
            }
            for k, v in task_groups.items()
        },
        'results': results,
    }
    index_template = os.path.join(TEMPLATE_DIR, 'index.html')
    index_html = os.path.join(DATA_DIR, 'index.html')
    with open(index_template) as f:
        template = f.read()
    content = template.replace(
        r'{{ context }}', base64.b64encode(
            json.dumps(context).encode('utf-8')
        ).decode('utf-8')
    )
    with open(index_html, 'w') as f:
        f.write(content)


def run_task_http(task):
    url = task.get('url')
    if not url:
        return (ERROR_CONFIG, -1, f'task {task["id"]} need url')
    response = subprocess.check_output([
        'curl',
        '-H', 'User-Agent: Mozilla/5.0 Chrome/91.0.4469.4 self-status-page',
        '-o', '/dev/null',
        '-s',
        '-w', '%{time_total}',
        url,
    ], timeout=STATUS_CONFIG_TIMEOUT)
    total_time = float(response.decode('utf-8'))
    return None, total_time, 'OK'


def run_task_ping(task):
    ip = task.get('ip')
    if not ip:
        return (ERROR_CONFIG, -1, f'task {task["id"]} need ip')
    cmd = (
        f"ping -c 1 {ip}"
        "| tail -n 1"
        "| awk '{print $4}'"
        "| cut -d'/' -f1"
    )
    response = subprocess.check_output(
        cmd, shell=True, timeout=STATUS_CONFIG_TIMEOUT
    )
    total_time = float(response.decode('utf-8')) / 1000
    return None, total_time, 'OK'


def run_task_shell(task):
    cmd = task.get('cmd')
    if not cmd:
        return (ERROR_CONFIG, -1, f'task {task["id"]} need cmd')
    response = subprocess.check_output(
        cmd, shell=True, timeout=STATUS_CONFIG_TIMEOUT
    )
    response_text = response.decode('utf-8')
    try:
        total_time = float(response_text)
        return None, total_time, 'OK'
    except (ValueError, TypeError):
        return None, 0, response_text


def run_task(task):
    task_map = {
        'http': run_task_http,
        'ping': run_task_ping,
        'shell': run_task_shell
    }
    if task.get('type') not in task_map:
        return (
            ERROR_CONFIG,
            -1,
            f'task {task} type must in {task_map.keys()}'
        )
    try:
        return task_map[task['type']](task)
    except Exception as e:
        return ERROR_RUN, -1, str(e)


def run_tasks():
    task_groups = read_config()
    results = []
    for group_id, group in task_groups.items():
        logger.info(f'group={group_id}')
        for task in group['tasks']:
            error, total_time, message = run_task(task)
            logger.info(
                f"    task={task['task_id']} "
                f"error={error} total_time={total_time} message={message[:80]}"
            )
            results.append([
                task['task_id'],
                time.time(),
                error,
                total_time,
                message,
            ])
    file_path = os.path.join(
        DATA_DIR, datetime.datetime.now().strftime(r'results-%Y-%m-%d.json')
    )
    results_data = {
        'version': 1,
        'last_modified': time.time(),
        'results': results,
    }
    if os.path.exists(file_path):
        with open(file_path) as f:
            try:
                old_results_data = json.load(f)
                results_data['results'] = (
                    old_results_data.get('results', []) +
                    results_data['results']
                )
            except json.decoder.JSONDecodeError:
                pass
    with open(file_path, 'w') as f:
        json.dump(results_data, f, ensure_ascii=False)

    build_html()


def watch_html():
    while True:
        build_html()
        time.sleep(1)


def schedule():
    print('Self-status-page start with config:\n')
    pprint.pprint(read_config())
    print('\nPlease wait first build end...')
    while True:
        try:
            logger.info('Build start...')
            run_tasks()
            logger.info('Build end...')
        except Exception as e:
            logger.error(e)
            continue
        logger.info('Wait next build ...\n')
        time.sleep(STATUS_CONFIG_INTERVAL)


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        "--action",
        action="store",
        type="str",
        dest="action",
        default='run_tasks'
    )
    options, args = parser.parse_args()

    actions = dict(
        run_tasks=run_tasks,
        watch_html=watch_html,
        schedule=schedule,
    )
    if options.action in actions:
        actions[options.action]()
