#! /usr/bin/env python

# An MPI (parallel) tool for unpacking HDF5 and zip archives
import argparse
from mpi4py import MPI
from pathlib import Path
import h5py
import zipfile
import blosc2
import logging
import sys
from humanize import intcomma, naturalsize
from time import time
from importlib.metadata import version

from hdf5vault.common import check_archive_files, check_zip_files, determine_format

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout)


# Split up dict with file archive information among CPUs
def scatter_items(filelist, ncpus):
    filelist_scattered=[{} for n in range(ncpus)]

    for n, key in enumerate(filelist.keys()):
        # first item goes to CPU 0, second to CPU 1, etc.
        cpu_num = n % ncpus

        filelist_scattered[cpu_num][key] = filelist[key]

    return filelist_scattered

def get_unpack_directory(dstdir: Path, files: list, comm: MPI.Comm):
    if len(files) == 1:
        tdir=Path(files[0]).stem

    else:
        basenames=[Path(f).stem for f in files]
        basenames=["_".join(f.split("_")[:-1]) for f in basenames]

        if len(set(basenames)) != 1: 
            logger.error('the expected format for multipart archives is archive_0.h5, archive_1.h5, etc...')
            comm.Abort()

        tdir=basenames[0]

    updir=dstdir.joinpath(tdir)

    return updir

def restore_file(filename: str, dstdir: str, archive_info: list, ctx: dict, archive_type: str, comm: MPI.Comm):

    nchunks = len(archive_info)
    # create dictionary that maps chunk number to entry in list (they might not be in order)
    cnmap = {a['chunk'] if a['chunk'] is not None else 0: p for p,a in enumerate(archive_info)}

    destfile = Path(dstdir).joinpath(filename)
    if destfile.is_file():
        logger.error(f'{destfile} already exists, aborting unpack.')
        comm.Abort()

    parentdir = destfile.parent

    # create output directory if it doesn't exist
    if not parentdir.is_dir():
        parentdir.mkdir(parents=True, exist_ok=True)

    restored_size=0

    with open(destfile, 'wb') as fid:
        for chunknum in range(nchunks):
            cinfo = archive_info[cnmap[chunknum]]

            archnum = cinfo["archive_number"]
            dataset=cinfo["dataset"]
            logger.debug(f"Restoring chunk {chunknum} from dataset {dataset} in archive {archnum}")

            if archive_type == 'h5':
                compdata = ctx[archnum][dataset][:].tobytes()
            elif archive_type == 'zip':
                compdata = ctx[archnum].read(dataset)
            else:
                logger.error(f"Unknown format type {archive_type}")
                comm.Abort()

            if cinfo["compression"] is None:
                rawdata=compdata

            elif cinfo["compression"].lower() in ['blosc','blosc2']:
                rawdata=blosc2.decompress(compdata)
            else:
                logger.error(f"Unknown compression method {cinfo['compression']} for file {filename}, part {chunknum}")
                comm.Abort()

            fid.write(rawdata)
            restored_size+=len(rawdata)

    return restored_size
 
def unpack_files(fileinfo: dict, numbered_archives: list[str], archive_type: str, dstdir:str, comm: MPI.Comm, progress_steps:int=100):
    rank=comm.Get_rank()
    nitems = len(fileinfo)

    restored_size = 0
    restored_files = 0

    # each archive is opened only once
    ctx={}
    for n in numbered_archives.keys():
        if archive_type == 'h5':
            ctx[n] = h5py.File(numbered_archives[n])
        elif archive_type == 'zip':
            ctx[n] = zipfile.ZipFile(numbered_archives[n])
        else:
            print(archive_type)
            logger.error('Unknown archive type.')

    # unpack each file
    for n,key in enumerate(fileinfo.keys()):
        if rank==0:
            if n % progress_steps == 0:
                logger.info(f'Unpacking file {n} out of {nitems} on rank 0')
        restored_size += restore_file(key, dstdir, fileinfo[key], ctx, archive_type, comm)
        restored_files += 1

    for n in ctx.keys():
        ctx[n].close()

    return restored_size, restored_files
    

def unpack_archives(files: list, dstdir: Path, format: str = 'H5'):

    comm=MPI.COMM_WORLD
    rank=comm.Get_rank()
    ncpus=comm.Get_size()

    if rank==0:
        archive_type=determine_format(files)
        if not archive_type:
            logger.error('Only .h5 and .zip files are supported.')
            comm.Abort()

    nfiles=len(files)

    t0=time()

    updir=get_unpack_directory(dstdir, files, comm)
    __version__ = version("hdf5vault")

    if rank==0:
        logger.info(f"HDF5/ZIP Archive unpacker, version f{__version__}.")
        logger.info(f"{archive_type} format detected.")
        logger.info(f"Unpacking {nfiles} files:")
        for file in files:
            logger.info(f" - {file}")
        logger.info(f"Destination directory: {dstdir}")


        if archive_type == 'h5':
            filelist_inarch,numbered_archives,qc_passed=check_archive_files(files, logger)
        elif archive_type == 'zip':
            filelist_inarch,numbered_archives,qc_passed=check_zip_files(files, logger)

        if not qc_passed:
            logger.error('QC not passed, aborting.')
            comm.Abort()

    else:
        filelist_inarch={}
        numbered_archives={}
        archive_type = ''

    filelist_inarch=comm.bcast(filelist_inarch, root=0)
    numbered_archives=comm.bcast(numbered_archives, root=0)
    archive_type=comm.bcast(archive_type, root=0)

    if rank==0:
        filelist_scattered = scatter_items(filelist_inarch, ncpus)
    else:
        filelist_scattered = []

    myfilelist = comm.scatter(filelist_scattered, root=0)

    logger.debug(f"Rank {rank}: received info for {len(myfilelist)} files to unpack.")
    nbytes_restored,nfiles_restored = unpack_files(myfilelist, numbered_archives, archive_type, updir, comm)

    logger.debug(f"Global rank {rank} at end of loop.")

    global_count=comm.allreduce(nfiles_restored, op=MPI.SUM)
    global_size=comm.allreduce(nbytes_restored, op=MPI.SUM)

    comm.Barrier()
    t1=time()
    if rank==0:
        logger.info(f"{intcomma(global_count)} files ({naturalsize(global_size)}) restored from {nfiles} archives in {t1-t0} seconds.")

def main():
    parser = argparse.ArgumentParser(
                prog='hdf5vault_unpack',
                description='Parallel tool to unpack HDF5 and zip archives')

    parser.add_argument('-f', '--files', nargs="+", required=True, type=str, help="archive file(s)")
    parser.add_argument('-d', '--destdir', required=False, type=Path, default=Path().cwd(), help='destination directory (default: current working directory)')
    parser.add_argument('-e', '--debug', action="store_true", help="log debugging information")
    parser.add_argument('-q', '--quiet', action="store_true", help='minimal output')

    args=parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.WARN)
    else:
        logger.setLevel(logging.INFO)

    unpack_archives(files=args.files, dstdir=args.destdir) 

if __name__ == "__main__": 
    main()
