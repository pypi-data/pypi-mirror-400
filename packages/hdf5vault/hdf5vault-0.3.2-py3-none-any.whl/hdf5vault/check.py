#! /usr/bin/env python

# Carries out comparison of checksum in files from given directory
# and in data from HDF5 archive.

GET_FILENAME_TAG = 0
REQUEST_FILENAME_TAG = 1

import argparse
from mpi4py import MPI
from pathlib import Path
from sys import argv
#from os.path import join, isdir, isfile, getsize, basename, dirname, relpath
import numpy as np
import h5py
from sys import stdout
import time
import blosc2
import hashlib
import pandas as pd
from functools import reduce
import logging
from os import walk
from humanize import intcomma
import json
import zipfile

from hdf5vault.common import determine_format, check_archive_files, check_zip_files

logger = logging.getLogger(__name__)
logging.basicConfig(stream=stdout)

def get_files_to_check(tdir: str) -> list:
    filelist=[]

    for root,dirs,files in walk(tdir):
        for file in files:
            filelist.append(join(root, file))
        print(f"\rfound {intcomma(len(filelist))} files", end="")

    filelist=[relpath(item, tdir) for item in filelist]

    return filelist

# flatten a lists of list (returned by mpi.gather) to list:
def flatten_list(inlist: list[list]) -> list:
    return reduce(lambda x,y: x+y, inlist)

def run_verification(archive_files: list, filelist_inarch: list, target_dir: Path, archive_type: str, rank: int, comm: MPI.Comm, progress_step:int=100):
    success = True
    error_files = []

    # checksum information to be collected and stored
    filesize_ondisk = []
    filesize_inarch = []

    md5_ondisk = []
    md5_inarch = []

    file_passed = []
    number_of_chunks = []

    filelist = []

    # open all HDF5 files
    if archive_type == 'h5':
        hfile={n: h5py.File(archive_files[n], 'r') for n in archive_files.keys()}
    else:
        hfile={n: zipfile.ZipFile(archive_files[n], 'r') for n in archive_files.keys()}

    finished = False
    n=0

    while not finished:
        if rank==1:
            if n % progress_step == 0:
                logger.info(f"Processing file {n} out of {len(filelist_inarch)} on rank {rank}")

        logger.debug(f'rank {rank}: requesting file from 0')
        comm.send(None, dest=0, tag=REQUEST_FILENAME_TAG)
        logger.debug(f'rank {rank}: waiting to receive file to verify')
        filename = comm.recv(source=0, tag=GET_FILENAME_TAG)

        if filename is None:
            logger.debug(f'rank {rank}: no more files left to verify')
            break

        diskfile = target_dir.joinpath(filename)

        filelist.append(filename)

        odata=open(diskfile, "rb").read()
        filesize_ondisk.append(len(odata))

        logger.debug(f"Rank {rank}: looking for file {filename} in archives ...")

        # find in which archive this dataset is stored

        if filename not in filelist_inarch.keys():
            success=False
            logger.error(f"FAIL: {filename} not found in any archive file")
            error_files.append(filename + "(missing)")
            filesize_inarch.append(0)
            md5_inarch.append('N/A')
            md5_ondisk.append('N/A')
            file_passed.append(False)
        else:
            # loop over all chunks ## CONTINUE HERE
            ainfo = filelist_inarch[filename]

            rdata = b''
            nchunks = len(ainfo)

            # in the file info dictionary, each file contains a list of dicts with chunknumber, archive, dataset name, and compression
            # this list may not be sorted ascending by chunk number
            # create dictionary that maps chunk number to entry in list
            cnmap = {a['chunk'] if a['chunk'] is not None else 0: p for p,a in enumerate(ainfo)}
            for chunknum in range(nchunks):
                cinfo = ainfo[cnmap[chunknum]]

                archnum = cinfo["archive_number"]
                dataset=cinfo["dataset"]
                if archive_type == 'h5':
                    compdata=hfile[archnum][dataset][:].tobytes()
                elif archive_type == 'zip':
                    compdata=hfile[archnum].read(dataset)

                if cinfo["compression"] is None:
                    rdata += compdata
                elif cinfo["compression"].lower() in ['blosc','blosc2']:
                    rdata += blosc2.decompress(compdata)
                else:
                    logger.error(f"Unknown compression method {cinfo['compression']} for file {filename}, part {chunknum}")
                    comm.Abort()
            
            number_of_chunks.append(nchunks)

            filesize_inarch.append(len(rdata))

            md5_ondisk.append(hashlib.md5(odata).hexdigest())
            md5_inarch.append(hashlib.md5(rdata).hexdigest())

            if len(odata) != len(rdata):
                success=False
                logger.error(f"FAIL: size of {diskfile} ({len(odata)}) does not match size of dataset {filename} ({len(rdata)}) in archive(s)")
                error_files.append(diskfile.as_posix() + "(size)")
                file_passed.append(False)
            else:

                if md5_ondisk[-1] != md5_inarch[-1]:
                    success=False
                    logger.error(f"FAIL: checksum {md5_ondisk[-1]} of {diskfile} != {md5_inarch[-1]} of {filename} in archive(s)")
                    error_files.append(diskfile.as_posix() + "(md5)")
                    file_passed.append(False)
                else:
                    file_passed.append(True)
        n+=1

    for f in hfile.values():
        f.close()

    return success, file_passed, error_files, filesize_ondisk, filesize_inarch, md5_ondisk, md5_inarch, filelist, number_of_chunks

# this function is called by rank 0.  It scans the target directory for files and continuously passed the
# names of files it found to the other ranks, which do the verification
def scan_and_distribute_files(target_dir:Path, comm: MPI.Comm, ncpus:int, progress_step:int=100):
    if not target_dir.is_dir():
        logger.error(f"Target directory {target_dir} not found. Aborting.")
        comm.Abort()

    status=MPI.Status()
    nfiles_ondisk=0

    filelist_ondisk=[]

    for p in target_dir.rglob('*'):
        if p.is_file():
            filename_r = p.relative_to(target_dir)
            logger.debug("Rank 0: accepting request for filename...")

            comm.recv(None, source=MPI.ANY_SOURCE, tag=REQUEST_FILENAME_TAG, status=status)

            destination=status.Get_source()

            logger.debug(f"Rank 0: ready to send out filename {filename_r} to {destination}")
            comm.send(filename_r.as_posix(), dest=destination, tag=GET_FILENAME_TAG)
            nfiles_ondisk+=1

            if nfiles_ondisk % progress_step == 0:
                logger.info(f"Found {nfiles_ondisk} files, still scanning")

            filelist_ondisk.append(filename_r.as_posix())

    # notify each other rank that there are no more files left

    other_ranks = set([a for a in range(1, ncpus)])
    for n in range(1,ncpus):
        comm.recv(None, source=MPI.ANY_SOURCE, tag=REQUEST_FILENAME_TAG, status=status)
        destination=status.Get_source()
        logger.debug(f"Rank 0: sending None (= no more files to verify) to {destination}")
        comm.send(None, dest=destination, tag=GET_FILENAME_TAG)
        other_ranks.remove(destination)

    if len(other_ranks) > 0:
        logger.error(f"Ranks {other_ranks} were not notified of end of file scanning.")

    return nfiles_ondisk

def compare_archive_checksums(target_dir: str, archive_files: str, summary_file: str|None):

    comm=MPI.COMM_WORLD
    rank=comm.Get_rank()
    ncpus=comm.Get_size()

    if ncpus == 1:
        logger.error("The number of MPI processes (NUM_TASKS) must be at least 2. Aborting.")
        comm.Abort()

    # read the contents of each archive. make available to all ranks.
    archive_type = determine_format(archive_files)

    if rank==0:
        if archive_type == 'h5':
            filelist_inarch, numbered_archives, qc_passed = check_archive_files(archive_files, logger)
        elif archive_type == 'zip':
            filelist_inarch, numbered_archives, qc_passed = check_zip_files(archive_files, logger)
        if not qc_passed:
            logger.error("Archive files failed initial quality control")
            comm.Abort()

    else:
        filelist_inarch = {}
        numbered_archives = {}
     
    filelist_inarch = comm.bcast(filelist_inarch, root=0)
    numbered_archives = comm.bcast(numbered_archives, root=0)

    if rank==0:
        nfiles_ondisk=scan_and_distribute_files(target_dir, comm, ncpus)
        logger.debug(f"Rank 0: done scanning, found {nfiles_ondisk}")

        success = True
        filesize_ondisk = []
        filesize_inarch = []
        md5_ondisk = []
        md5_inarch = []
        file_passed = []
        number_of_chunks = []
        filelist_ondisk = []
        error_files = []

    else:
        success, file_passed, error_files, filesize_ondisk, filesize_inarch, md5_ondisk, md5_inarch, filelist_ondisk, number_of_chunks = \
            run_verification(numbered_archives, filelist_inarch, target_dir, archive_type, rank, comm)

    comm.Barrier()

    # gather information from different processes
    overall_sucess = comm.allreduce(success, op=MPI.MIN)
    error_files_all = comm.gather(error_files)

    if rank==0:
        if overall_sucess:
            logger.info(f"archive(s) {archive_files} passed.")
        else:
            logger.error(f"archive(s) {archive_files} FAILED!.  The following files had errors:")
            logger.error(error_files_all)

    if summary_file is not None:

        filesize_ondisk_all = comm.gather(filesize_ondisk, root=0)
        filesize_inarch_all = comm.gather(filesize_inarch, root=0)
        
        md5_ondisk_all = comm.gather(md5_ondisk, root=0)
        md5_inarch_all = comm.gather(md5_inarch, root=0)

        file_passed_all = comm.gather(file_passed, root=0)
        # get the file list in the same order as the verification parameters
        filenames_all = comm.gather(filelist_ondisk, root=0)

        number_of_chunks = comm.gather(number_of_chunks, root=0)

        if rank==0:
            summary_info=  pd.DataFrame({"size_orig": flatten_list(filesize_ondisk_all),
                        "size_arch": flatten_list(filesize_inarch_all),
                        "md5_orig": flatten_list(md5_ondisk_all),
                        "md5_arch": flatten_list(md5_inarch_all),
                        "chunks": flatten_list(number_of_chunks),
                        "passed": flatten_list(file_passed_all)
                        }, index=flatten_list(filenames_all))

            summary_info.index.name = "filename"
            summary_info.to_json(summary_file)

    comm.Barrier()

            
def main():

    parser = argparse.ArgumentParser(
                prog='hdf5vault_check',
                description='Parallel tool to verify contents of archive ')

    parser.add_argument('-d', '--directory', required=True, type=str, help='name of directory to verify archive content against')
    parser.add_argument('-f', '--files', nargs="+", required=True, type=str, help="HDF5 archive file(s)")
    parser.add_argument('-j', '--json', required=False, type=str, help='JSON summary file (default: None)')
    parser.add_argument('-e', '--debug', action="store_true", help="log debugging information")
    parser.add_argument('-q', '--quiet', action="store_true", help='minimal output')

    args=parser.parse_args()

    rank=MPI.COMM_WORLD.Get_rank()

    target_dir = Path(args.directory)
    archive_files = args.files
    summary_file = args.json

    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)

    if rank==0:
        logger.info(f"Checking directory {target_dir} against archvive file(s) {archive_files}.")

    compare_archive_checksums(target_dir, archive_files, summary_file)

if __name__ == '__main__':
    main()
