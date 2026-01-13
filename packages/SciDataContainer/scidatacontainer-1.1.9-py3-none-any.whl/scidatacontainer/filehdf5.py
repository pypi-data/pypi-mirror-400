import io

import h5py
import numpy as np

from scidatacontainer import AbstractFile


class Hdf5File(AbstractFile):
    def encode(self):
        with io.BytesIO() as fp:
            with h5py.File(fp, "w") as h5file:
                if isinstance(self.data, np.ndarray):
                    _ = h5file.create_dataset(
                        "dataset",
                        data=self.data,
                        compression="gzip",
                        compression_opts=9,
                    )
                elif isinstance(self.data, dict):
                    for key, value in self.data.items():
                        assert key != "dataset"
                        if isinstance(value, np.ndarray):
                            _ = h5file.create_dataset(
                                key, data=value, compression="gzip", compression_opts=9
                            )
                        else:
                            h5file.attrs[key] = value
                else:
                    raise NotImplementedError(
                        f"Unknown data type {type(self.data).__name__}!"
                    )
            _ = fp.seek(0)
            data = fp.read()
        return data

    def decode(self, data):
        with io.BytesIO(data) as fp:
            with h5py.File(fp, "r") as h5file:
                datasets = [
                    name
                    for name in h5file.keys()
                    if isinstance(h5file[name], h5py.Dataset)
                ]
                if datasets == ["dataset"]:
                    self.data = h5file["dataset"][()]
                else:
                    self.data = {name: h5file[name][()] for name in datasets}
                    self.data.update(
                        {name: h5file.attrs[name] for name in h5file.attrs.keys()}
                    )


register = [("hdf5", Hdf5File, np.ndarray)]
