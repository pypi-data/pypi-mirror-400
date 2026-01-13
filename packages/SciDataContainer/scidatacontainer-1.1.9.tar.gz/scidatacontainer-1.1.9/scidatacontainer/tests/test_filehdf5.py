import os
from io import BytesIO
from unittest import TestCase
from zipfile import ZipFile

import h5py
import numpy as np

from scidatacontainer import Container

from . import get_test_container


class FileHdf5Test(TestCase):
    def test_encode_decode(self):
        a = get_test_container()

        data = np.random.randint(0, 256, (100, 100, 3))
        moredata = {
            "data1": np.random.randint(0, 256, (100, 100, 3)),
            "data2": np.random.randint(0, 256, (100, 100, 3)),
            "attr1": "test123",
            "attr2": 123,
            "attr3": 1.23,
        }

        a["data/test.hdf5"] = data
        a["data/test2.hdf5"] = moredata

        a.write("test.zdc")

        b = Container(file="test.zdc")
        self.assertTrue(np.allclose(a["data/test.hdf5"], b["data/test.hdf5"]))
        self.assertTrue(np.allclose(moredata["data1"], a["data/test2.hdf5"]["data1"]))
        self.assertTrue(np.allclose(moredata["data2"], a["data/test2.hdf5"]["data2"]))
        self.assertEqual(moredata["attr1"], a["data/test2.hdf5"]["attr1"])
        self.assertEqual(moredata["attr2"], a["data/test2.hdf5"]["attr2"])
        self.assertEqual(moredata["attr3"], a["data/test2.hdf5"]["attr3"])

        a.release()
        a["data/test3.hdf5"] = [data]
        with self.assertRaisesRegex(NotImplementedError, "Unknown data type list!"):
            a.write("test.zdc")

    def test_file_content(self):
        a = get_test_container()

        data = np.random.randint(0, 256, (100, 100, 3))
        moredata = {
            "data1": np.random.randint(0, 256, (100, 100, 3)),
            "data2": np.random.randint(0, 256, (100, 100, 3)),
            "attr1": "test123",
            "attr2": 123,
            "attr3": 1.23,
        }

        a["data/test.hdf5"] = data
        a["data/test2.hdf5"] = moredata

        a.write("test.zdc")

        with ZipFile("test.zdc") as zfile:
            with BytesIO(zfile.read("data/test.hdf5")) as fp:
                with h5py.File(fp) as h5file:
                    self.assertTrue(np.allclose(a["data/test.hdf5"], h5file["dataset"]))
            with BytesIO(zfile.read("data/test2.hdf5")) as fp:
                with h5py.File(fp) as h5file:
                    self.assertTrue(np.allclose(moredata["data1"], h5file["data1"]))
                    self.assertTrue(np.allclose(moredata["data2"], h5file["data2"]))
                    self.assertEqual(moredata["attr1"], h5file.attrs["attr1"])
                    self.assertEqual(moredata["attr2"], h5file.attrs["attr2"])
                    self.assertEqual(moredata["attr3"], h5file.attrs["attr3"])
