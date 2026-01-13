"""
slow5/blow5 top-level API, interface consistent with old fast5 scripts
"""

import sys, os
from glob import glob
from functools import partial
from multiprocessing import Pool
from tqdm import tqdm
import numpy as np
import pyslow5
from itertools import chain
from pathlib import Path
import numpy as np
from dateutil import parser
from datetime import timedelta, timezone
import densecall.reader


class Slow5Read(densecall.reader.Read):

    def __init__(self, s5_read, filename, meta=False, do_trim=True, scaling_strategy=None, norm_params=None):
        """
        s5_read : pyslow5.Read object
        filename: Path or str
        """
        self.meta = meta
        # print(s5_read)
        self.read_id = s5_read["read_id"]
        self.filename = Path(filename).name

        self.offset = int(s5_read["offset"])
        self.sample_rate = s5_read["sampling_rate"]
        self.scaling = s5_read["range"] / s5_read["digitisation"]
        self.duration = s5_read["len_raw_signal"] / self.sample_rate
        self.start = s5_read["start_time"] / self.sample_rate
        self.run_id = "unset"
        self.mux = s5_read["start_mux"]
        self.channel = s5_read["channel_number"]
        self.read_number = s5_read["read_number"]
        self.start_time = parser.parse("2024-01-01") + timedelta(seconds=self.start)

        # ---------- signal ----------
        raw = s5_read["signal"]
        self.scaled = np.array(self.scaling * (raw + self.offset), dtype=np.float32)
        self.num_samples = len(self.scaled)

        # Reuse densecall normalization/trimming
        self.shift, self.scale = densecall.reader.normalisation(self.scaled, scaling_strategy, norm_params)
        self.trimmed_samples = densecall.reader.trim(self.scaled, threshold=self.scale * 2.4 + self.shift) if do_trim else 0
        self.template_start = self.start + (self.trimmed_samples / self.sample_rate)
        self.template_duration = self.duration - (self.trimmed_samples / self.sample_rate)
        self.signal = (self.scaled[self.trimmed_samples :] - self.shift) / self.scale


# ---------- single file meta ----------
def get_meta_data(filename, read_ids=None, skip=False):
    meta_reads = []
    try:
        s5 = pyslow5.Open(str(filename), "r")
        for read in s5:
            if read_ids is None or (read.read_id in read_ids) ^ skip:
                meta_reads.append(Slow5Read(read, filename, meta=True))
        s5.close()
    except Exception as e:
        sys.stderr.write(f"> warning: {filename} - {e}\n")
    return meta_reads


# ---------- single file (filename, read_id) list ----------
def get_read_ids(filename, read_ids=None, skip=False):
    try:
        s5 = pyslow5.Open(str(filename), "r")
        read_ids, num_reads = s5.get_read_ids()
        ids = [(filename, rid) for rid in read_ids]
        s5.close()
        if read_ids is None:
            return ids
        return [rid for rid in ids if (rid[1] in read_ids) ^ skip]
    except Exception as e:
        sys.stderr.write(f"> warning: {filename} - {e}\n")
        return []


# ---------- actual signal reading ----------
def get_raw_data_for_read(info, do_trim=True, scaling_strategy=None, norm_params=None):
    filename, rid = info
    s5 = pyslow5.Open(str(filename), "r")
    read = s5.get_read(rid, aux='all')
    s5.close()
    return Slow5Read(read, filename, do_trim=do_trim, scaling_strategy=scaling_strategy, norm_params=norm_params)


# ---------- traverse directory ----------
def get_reads(directory, read_ids=None, skip=False, n_proc=1, recursive=False, cancel=None, do_trim=True, scaling_strategy=None, norm_params=None):
    """
    Get all reads in a given `directory`.
    """
    # Determine if directory is file or folder
    if os.path.isfile(directory):
        reads = [Path(directory)]
    else:
        pattern = "**/*.slow5" if recursive else "*.slow5"
        reads1 = [Path(x) for x in glob(directory + "/" + pattern, recursive=True)]
        pattern = "**/*.blow5" if recursive else "*.blow5"
        reads2 = [Path(x) for x in glob(directory + "/" + pattern, recursive=True)]
        reads = reads1 + reads2

    get_filtered_reads = partial(get_read_ids, read_ids=read_ids, skip=skip)
    get_raw_data = partial(get_raw_data_for_read, do_trim=do_trim, scaling_strategy=scaling_strategy, norm_params=norm_params)

    # Shuffle file order
    poem = np.arange(len(reads))
    np.random.seed(1)
    np.random.shuffle(poem)
    reads = [reads[i] for i in poem]

    with Pool(n_proc) as pool:
        for job in chain(pool.imap(get_filtered_reads, reads)):
            for read in pool.imap(get_raw_data, job):
                yield read
                if cancel is not None and cancel.is_set():

                    return


# ---------- compatible with get_read_groups in old scripts ----------
def get_read_groups(directory, model, read_ids=None, skip=False, n_proc=1, recursive=False, cancel=None):
    groups = set()
    num_reads = 0
    pat1 = "**/*.slow5" if recursive else "*.slow5"
    pat2 = "**/*.blow5" if recursive else "*.blow5"
    files1 = [Path(x) for x in Path(directory).glob(pat1)]
    files2 = [Path(x) for x in Path(directory).glob(pat2)]
    files = files1 + files2

    get_filtered = partial(get_meta_data, read_ids=read_ids, skip=skip)
    with Pool(n_proc) as pool:
        for reads in tqdm(pool.imap(get_filtered, files), total=len(files), desc="> preprocessing reads", unit=" files", ascii=True, ncols=100):
            groups.update({read.readgroup(model) for read in reads})
            num_reads += len(reads)
    return groups, num_reads
