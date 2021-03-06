# -*- coding: utf-8 -*-

"""
Luigi patches.
"""

__all__ = ["patch_all"]


import os

import luigi


_patched = False


def patch_all():
    global _patched

    if not _patched:
        patch_worker_factory()
        patch_worker_add_task()
        patch_task_process_run()
        _patched = True


def patch_worker_factory():
    def create_worker(self, scheduler, worker_processes, assistant=False):
        worker_id = os.environ.get("LAW_SANDBOX_WORKER_ID")
        return luigi.worker.Worker(
            scheduler=scheduler, worker_processes=worker_processes, assistant=assistant,
            worker_id=worker_id)

    luigi.interface._WorkerSchedulerFactory.create_worker = create_worker


def patch_worker_add_task():
    _add_task = luigi.worker.Worker._add_task

    def add_task(self, *args, **kwargs):
        if os.environ.get("LAW_SANDBOX_SWITCHED") == "1" and "deps" in kwargs:
            kwargs["deps"] = None
        return _add_task(self, *args, **kwargs)

    luigi.worker.Worker._add_task = add_task


def patch_task_process_run():
    _run_get_new_deps = luigi.worker.TaskProcess._run_get_new_deps

    def run_get_new_deps(self, *args, **kwargs):
        self.task.worker_id = self.worker_id
        res = _run_get_new_deps(self, *args, **kwargs)
        self.task.worker_id = None
        return res

    luigi.worker.TaskProcess._run_get_new_deps = run_get_new_deps
