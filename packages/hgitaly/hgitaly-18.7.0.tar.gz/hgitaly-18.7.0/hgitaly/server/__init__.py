# Copyright 2020-2022 Georges Racinet <georges.racinet@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
# flake8: noqa F401
from .address import (
    InvalidUrl,
    UnsupportedUrlScheme,
)
from .mono import (
    BindError,
    server_process,
)

def run_forever(listen_urls, storages, **process_kwargs):
    return server_process(0, listen_urls, storages,
                          mono_process=True,
                          **process_kwargs)
