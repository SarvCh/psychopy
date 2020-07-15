#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Writes the current version, build platform etc.
"""

from __future__ import absolute_import, print_function
from setuptools.config import read_configuration
import os
import platform
import subprocess
from psychopy.constants import PY3
from pathlib import Path

root = Path(__file__).parent.parent
# import versioneer
# get version from file
with open('version') as f:
    version = f.read().strip()


def createInitFile(dist=None, version=None, sha=None):
    """Create psychopy/__init__.py

    :param:`dist` can be:
        None:
            writes __version__
        'sdist':
            for python setup.py sdist - writes git id (__git_sha__)
        'bdist':
            for python setup.py bdist - writes git id (__git_sha__)
            and __build_platform__
    """
    # get default values if None
    if version is None:
        with open(str(root/'version')) as f:
            version = f.read().strip()
    if sha is None:
        sha = _getGitShaString(dist)
    platformStr = _getPlatformString(dist)

    metadata = read_configuration('setup.cfg')['metadata']
    infoDict = {'version': version,
                'author': metadata['author'],
                'author_email': metadata['author_email'],
                'maintainer_email': metadata['maintainer_email'],
                'url': metadata['url'],
                'download_url': metadata['download_url'],
                'license': metadata['license'],
                'shaStr': sha,
                'platform': platformStr}

    # write it
    with open(str(root/'psychopy/__init__.py'), 'w') as f:
        outStr = template.format(**infoDict)
        f.write(outStr)
    print('wrote init for ', version, sha)
    # and return it
    return outStr


template = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Part of the PsychoPy library
# Copyright (C) 2002-2018 Jonathan Peirce (C) 2019 Open Science Tools Ltd.
# Distributed under the terms of the GNU General Public License (GPL).

# --------------------------------------------------------------------------
# This file is automatically generated during build (do not edit directly).
# --------------------------------------------------------------------------

import os
import sys

__version__ = '{version}'
__license__ = '{license}'
__author__ = '{author}'
__author_email__ = '{author_email}'
__maintainer_email__ = '{maintainer_email}'
__url__ = '{url}'
__download_url__ = '{download_url}'
__git_sha__ = '{shaStr}'
__build_platform__ = '{platform}'

__all__ = ["gui", "misc", "visual", "core",
           "event", "data", "sound", "microphone"]

# for developers the following allows access to the current git sha from
# their repository
if __git_sha__ == 'n/a':
    from subprocess import check_output, PIPE
    # see if we're in a git repo and fetch from there
    try:
        thisFileLoc = os.path.split(__file__)[0]
        output = check_output(['git', 'rev-parse', '--short', 'HEAD'],
                              cwd=thisFileLoc, stderr=PIPE)
    except Exception:
        output = False
    if output:
        __git_sha__ = output.strip()  # remove final linefeed

# update preferences and the user paths
if 'installing' not in locals():
    from psychopy.preferences import prefs
    for pathName in prefs.general['paths']:
        sys.path.append(pathName)

    from psychopy.tools.versionchooser import useVersion, ensureMinimal

# import readline here to get around an issue with sounddevice
# issues GH-2230 GH-2344 GH-2662
try:
    import readline
except ImportError:
    pass  # all that will happen is the stderr/stdout might get redirected

"""


def _getGitShaString(dist=None, sha=None):
    """If generic==True then returns empty __git_sha__ string
    """
    shaStr = 'n/a'
    if dist is not None:
        proc = subprocess.Popen('git rev-parse --short HEAD',
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                cwd='.', shell=True)
        repo_commit, _ = proc.communicate()
        if PY3:
            repo_commit = repo_commit.decode('utf-8')
        del proc  # to get rid of the background process
        if repo_commit:
            shaStr = "{}".format(repo_commit.strip())
        else:
            shaStr = 'n/a'
    return shaStr


def _getPlatformString(dist=None):
    """If generic==True then returns empty __build_platform__ string
    """
    if dist == 'bdist':
        # get platform-specific info
        if os.sys.platform == 'darwin':
            OSXver, _, architecture = platform.mac_ver()
            systemInfo = "OSX_%s_%s" % (OSXver, architecture)
        elif os.sys.platform == 'linux':
            import distro
            systemInfo = '%s_%s_%s' % (
                'Linux',
                ':'.join([x for x in distro.linux_distribution() if x != '']),
                platform.release())
        elif os.sys.platform == 'win32':
            ver = os.sys.getwindowsversion()
            if len(ver[4]) > 0:
                systemInfo = "win32_v%i.%i.%i (%s)" % (ver[0], ver[1], ver[2],
                                                       ver[4])
            else:
                systemInfo = "win32_v%i.%i.%i" % (ver[0], ver[1], ver[2])
        else:
            systemInfo = platform.system() + platform.release()
    else:
        systemInfo = "n/a"

    return systemInfo


if __name__ == "__main__":
    createInitFile()