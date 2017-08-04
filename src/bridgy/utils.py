from sys import platform as _platform
import collections
import inquirer
import logging
import sys
import os

import inventory

logger = logging.getLogger()

class UnsupportedPlatform(Exception): pass

class SupportedPlatforms(object):
    def __init__(self, *platforms):
        self.platforms = platforms

    def __call__(self, func):
        decorator_self = self
        def wrapper(*args, **kwargs):
            decorator_self.check_supported_platforms()
            func(*args,**kwargs)
        return wrapper

    def check_supported_platforms(self):
        if 'linux' in _platform:
            normalized = 'linux'
        elif 'darwin' in  _platform:
            normalized = 'osx'
        elif 'win' in _platform:
            normalized = 'windows'
        else:
            normalized = _platform

        if normalized not in self.platforms:
            raise UnsupportedPlatform('Unsupported platform (%s)' % normalized)


def prompt_targets(question, targets=None, instances=None, multiple=True, config=None):
    if targets == None and instances == None or targets != None and instances != None:
        raise RuntimeError("Provide exactly one of either 'targets' or 'instances'")

    if targets:
        instances = inventory.search(config, targets)

    if len(instances) == 0:
        return []

    if len(instances) == 1:
        return instances

    display_instances = collections.OrderedDict()
    for instance in sorted(instances):
        display = "%-55s (%s)" % instance
        display_instances[display] = instance

    questions = []

    if multiple:
        q = inquirer.Checkbox('instance',
                              message="%s (space to multi-select, enter to finish)" % question,
                              choices=display_instances.keys() + ['all'],
                              # default='all'
                              )
    else:
        q = inquirer.List('instance',
                           message="%s (enter to select)" % question,
                           choices=display_instances.keys(),
                           )
    questions.append(q)

    try:
        answers = inquirer.prompt(questions)
    except KeyboardInterrupt:
        logger.error("Cancelled by user")
        sys.exit(1)

    if 'all' in answers["instance"]:
        selected_hosts = instances
    else:
        selected_hosts = []
        if not multiple:
            answers["instance"] = [answers["instance"]]
        for answer in answers["instance"]:
            selected_hosts.append(display_instances[answer])

    return selected_hosts
