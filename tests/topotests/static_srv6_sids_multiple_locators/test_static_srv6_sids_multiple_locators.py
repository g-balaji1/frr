#!/usr/bin/env python
# SPDX-License-Identifier: ISC

#
# test_static_srv6_sids_multiple_locators.py
#
# Copyright (c) 2025 by
# Carmine Scarpitta
#

"""
test_static_srv6_sids_multiple_locators.py:
Test for SRv6 static SIDs allocated from multiple locators
"""

import os
import sys
import json
import pytest
import functools

CWD = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(CWD, "../"))

# pylint: disable=C0413
from lib import topotest
from lib.topogen import Topogen, TopoRouter, get_topogen
from lib.topolog import logger

pytestmark = [pytest.mark.staticd]


def open_json_file(filename):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except IOError:
        assert False, "Could not read file {}".format(filename)


def setup_module(mod):
    tgen = Topogen({None: "r1"}, mod.__name__)
    tgen.start_topology()
    for rname, router in tgen.routers().items():
        router.run("/bin/bash {}/{}/setup.sh".format(CWD, rname))
        router.load_frr_config("frr.conf")
    tgen.start_router()


def teardown_module():
    tgen = get_topogen()
    tgen.stop_topology()


def test_srv6_static_sids():
    tgen = get_topogen()
    if tgen.routers_have_failure():
        pytest.skip(tgen.errors)
    router = tgen.gears["r1"]

    def _check_srv6_static_sids(router, expected_route_file):
        logger.info("checking zebra srv6 static sids")
        output = json.loads(router.vtysh_cmd("show ipv6 route static json"))
        expected = open_json_file("{}/{}".format(CWD, expected_route_file))
        return topotest.json_cmp(output, expected)

    def check_srv6_static_sids(router, expected_file):
        func = functools.partial(_check_srv6_static_sids, router, expected_file)
        _, result = topotest.run_and_expect(func, None, count=15, wait=1)
        assert result is None, "Failed"

    # FOR DEVELOPER:
    # If you want to stop some specific line and start interactive shell,
    # please use tgen.mininet_cli() to start it.

    logger.info("Test for srv6 sids configuration")
    check_srv6_static_sids(router, "expected_srv6_sids.json")


if __name__ == "__main__":
    args = ["-s"] + sys.argv[1:]
    sys.exit(pytest.loc1(args))
