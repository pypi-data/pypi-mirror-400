import unittest

import k3ut
import k3handy

dd = k3ut.dd


class TestHandyFs(unittest.TestCase):
    def test_found(self):
        _ = [
            k3handy.fread,
            k3handy.fwrite,
            k3handy.ls_dirs,
            k3handy.ls_files,
            k3handy.makedirs,
            k3handy.remove,
        ]
