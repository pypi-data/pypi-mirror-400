import k3txutil
import threading


class Foo(object):
    def __init__(self):
        self.lock = threading.RLock()
        self.val = 0
        self.ver = 0

    def _get(self, db, key, **kwargs):
        # db, key == 'dbname', 'mykey'
        with self.lock:
            return self.val, self.ver

    def _set(self, db, key, val, prev_stat, **kwargs):
        # db, key == 'dbname', 'mykey'
        with self.lock:
            if prev_stat != self.ver:
                raise k3txutil.CASConflict(prev_stat, self.ver)

            self.val = val
            self.ver += 1

    def test_cas(self):
        for curr in k3txutil.cas_loop(
            self._get,
            self._set,
            args=(
                "dbname",
                "mykey",
            ),
        ):
            curr.v += 2

        print((self.val, self.ver))  # (2, 1)


"""
while True:
    curr_val, stat = getter(key="mykey")
    new_val = curr_val + ':foo'
    try:
        setter(new_val, stat, key="mykey")
    except CASConflict:
        continue
    else:
        break

#`cas_loop` simplifies the above workflow to:
for curr in k3txutil.cas_loop(getter, setter, args=("mykey", )):
    curr.v += ':foo'
"""
