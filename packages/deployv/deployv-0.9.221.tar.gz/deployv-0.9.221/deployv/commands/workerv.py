# coding: utf-8
# Compilation mode
# nuitka-project: --mode=onefile
# nuitka-project: --follow-stdlib
# nuitka-project: --no-deployment-flag=self-execution
# nuitka-project: --include-package-data=deployv
# nuitka-project: --include-package-data=deployv_static
# nuitka-project: --enable-plugin=pylint-warnings
# nuitka-project: --include-package=deployv.messaging
# nuitka-project: --include-package=deployv.base
# nuitka-project: --include-package=psycopg2
# nuitka-project: --include-package=passlib
# nuitka-project: --include-package=requests
# nuitka-project: --include-package=urllib3
# nuitka-project: --include-package=docker
# nuitka-project: --include-package=pika
# nuitka-project: --include-package=jinja2
# nuitka-project: --include-package=jsonschema
# nuitka-project: --include-package=branchesv
# nuitka-project: --include-package=retry_decorator
# nuitka-project: --include-package=transitions
# nuitka-project: --include-package=deployv_static
# nuitka-project: --include-package=ipaddress
# nuitka-project: --include-package=deepdiff
# nuitka-project: --include-package=cryptography
# nuitka-project: --include-package=markupsafe

import click
import signal
from deployv.base import errors
from deployv.base.worker import WorkerManager
from deployv.helpers import utils, configuration_helper


def signal_handler(signal_number, stack_frame):
    raise errors.GracefulExit(
        'Received a signal to terminate, stopping workers'
    )


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)


@click.command()
@click.option("-l", "--log_level", help="Log level to show", default='INFO')
@click.option("-h", "--log_file", help="Write log history to a file")
@click.option("-C", "--config", help="Additional .conf files.")
@click.option(
    "--worker_type", help="Parameter used to specify the type worker.")
def run(log_level, log_file, config, worker_type):
    utils.setup_deployv_logger(level=log_level, log_file=log_file)
    cfg = configuration_helper.DeployvConfig(worker_config=config)
    worker_tp = cfg.deployer.get('worker_type')
    module = __import__('deployv.messaging', fromlist=[str(worker_tp)])
    if not hasattr(module, worker_tp):
        raise ValueError
    msg_object = getattr(module, worker_tp)
    config_class = msg_object.CONFIG_CLASSES['file']
    keys = {'commit': 'Commit worker',
            'status': 'Status worker'}
    name = keys.get(worker_type, 'Deploy worker')
    # Pass the initialized manager to the class to avoid losing data when the worker reconnects.
    worker_manager = WorkerManager(name, cfg.deployer.get('workers'))
    worker = msg_object.factory(config_class(cfg, worker_type), name, worker_manager)
    while True:
        try:
            worker.run()
        except (KeyboardInterrupt, errors.GracefulExit):
            worker.signal_exit()
            break
        if not worker.should_reconnect():
            break
        # The old worker was killed and the connections it opened
        # have been closed by now, a new worker must be started
        worker = msg_object.factory(config_class(cfg, worker_type), name, worker_manager)


if __name__ == '__main__':
    run()
