#!/usr/bin/env python
# coding: utf-8


import copy
import logging

logger = logging.getLogger(__name__)


class CASError(Exception):
    pass


class CASConflict(CASError):
    """
    User should raise this exception when a CAS conflict detect in a user defined
    `set` function.
    """

    pass


class CASRecord(object):
    """
    The class of a record yielded from `txutil.cas_loop()`.
    It has 3 attributes `v`, `stat` and `n`.

    `v` stores the value and the `stat` stores value stat information that is used
    to identify in `setter` whether the stat changed.

    `n` is the number of times it CAS runs.
    The first time `n` is 0.
    """

    def __init__(self, v, stat, n):
        self.v = v
        self.stat = stat
        self.n = n


def cas_loop(getter, setter, args=(), kwargs=None, conflicterror=CASConflict):
    """
    The loop body runs several times until a successful update is made(`setter` returns `True`).
    :param getter: is a `callable` receiving one argument and returns a tuple of `(value, stat)`
    `stat` is any object that will be send back to `setter` for it to check
    whether stat changed after `getter` called.
    :param setter: is a `callable` to check and set the changed value.
    :param args and kwargs: optional positioned arguments and key-value arguments that will be
    passed to `getter` and `setter`
    By default it is an empty tuple `()` and `None`.
    :param conflicterror: specifies what raised error indicating a CAS conflict, instead of
    using the default `CASConflict`.
    :return:
    a `generator` that yields a `CASRecord` for user to update its attribute `v`.
    If a user modifies `v`, an attempt to update by calling `setter`  will be made.

    If the update succeeds, the `generator` quits.

    If the update detects a conflict, it yields a new `CASRecord` and repeat the
    update.
    """
    if kwargs is None:
        kwargs = {}

    i = -1
    while True:
        i += 1

        val, stat = getter(*args, **kwargs)
        rec = CASRecord(copy.deepcopy(val), stat, i)

        yield rec

        if rec.v == val:
            # nothing to update
            return

        try:
            setter(*(args + (rec.v, rec.stat)), **kwargs)
            return
        except conflicterror as e:
            logger.info(repr(e) + " while cas set")
            continue
