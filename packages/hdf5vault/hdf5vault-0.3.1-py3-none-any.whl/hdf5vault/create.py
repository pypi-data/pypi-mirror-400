#! /usr/bin/env python3

import sys
try:
    from mpi4py import MPI
except RuntimeError:
    print("Error loading mpi4py. Make sure MPI is available and mpi4py is installed")
    print("You might have to load the mpi module on a cluster (module load mpi)")
    sys.exit(1)
except ModuleNotFoundError:
    print("mpi4py module not found.")
import numpy as np
from humanize import naturalsize, intword, intcomma
import h5py
import blosc2
from time import sleep, time
import logging
import argparse
import zipfile
from pathlib import Path
import json

from importlib.metadata import version

__version__ = version("hdf5vault")

from hdf5_archive_info import HDF5_ARCHIVE_INFO

# define MPI communication tags 
request_filename_tag = 1  # worker from master
send_filename_tag = 2     # master to worker
file_compressed_tag = 3   # worker to master
cdata_wo_to_co_tag = 4    # worker to write coordinator
cdata_co_to_wr_tag = 5    # write coordinator to writer
request_cdata_tag = 6     # writer to write coordinator
data_written_tag = 7      # writer to master
wait_tag = 97             # write coordinator to writer
compression_complete_tag = 98 # master to write coordinator
stop_tag = 99             # master to worker and write coordinator to writers

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout)

# splits file into chunks (if larger than chunksize) and compresses each chunk
# does not compress chunk if no storage gains are found
# returns an iterator over chunk numbers; each item is a dict with compressed buffer, chunk number and compression method 
def compress_file(filepath: Path, method: str, comm:MPI.Comm, 
                  chunksize:int = 2_000_000_000, 
                  nthreads=4, clevel=8, use_dict=False):

    from math import ceil
    
    max_chunk_size = 2_147_483_600
    filesize=filepath.stat().st_size

    if chunksize > max_chunk_size:
        logger.error(f"chunksize {chunksize} is larger than maximum of {max_chunk_size}")
        comm.Abort()

    nchunks = max(ceil(filesize / chunksize), 1) # nchunks is 1 even for an empty file

    if method.lower() == "blosc2":

        cparams = { 
                "codec": blosc2.Codec.ZSTD,
                "typesize": 8,
                "clevel": clevel,
                "use_dict": use_dict,
                "nthreads": nthreads
                }

    else: 
        cparams = None

    if not filepath.is_file():
        logger.error(f"{filepath} does not exist or is not a regular file")
        comm.Abort()    

    with filepath.open('rb') as fid:
        for n in range(nchunks):
            t0=time()
            buffdata = fid.read(chunksize)
            t1=time()

            if method.lower() == 'none':
                cdata = buffdata
                used_method = None
                compression_time = 0.

            else:
                cdata=None
                t2=time()
    
                try:
                    cdata=blosc2.compress2(buffdata, **cparams)
            
                except RuntimeError:
                    if use_dict:
                        cparams_nodict = cparams.copy()
                        cparams_nodict["use_dict"] = False
                        logger.info(f"file {filepath}, chunk {n} compressed with use_dict=False")
                        cdata=blosc2.compress2(buffdata, **cparams_nodict)
                    else:
                        logger.error(f"file {filepath}, chunk {n} can not be compressed, even with dict=False.")
                        comm.Abort()
                        
                except Exception as e:
                    logger.error(f"Received error {e} while compressing {filepath} chunk {n}")
                    comm.Abort()
    
                assert cdata is not None, "compressed data is none. this should not happen"
                t3=time()
                compression_time = t3-t2
            
            read_time = t1-t0

            # if compression results in no storage saving, chunk is stored uncompressed
            if len(cdata) >= len(buffdata):
                cdata = buffdata
                used_method = None
            else:
                used_method = method

            if nchunks > 1:
                chunk_number = n
            else:
                chunk_number = None

            out = {"buffer": cdata, 
                   "chunk": chunk_number, 
                   "compression": used_method, 
                   "raw_size": len(buffdata),
                   "read_time": read_time,
                   "total_chunks": nchunks,
                   "compression_time": compression_time}

            yield out

def iter_files(tdir: Path):
    for p in tdir.rglob('*'):
        if p.is_file():
            yield p.relative_to(tdir).as_posix()

# determine wait time based on size that has already been written to file
# the scope is to even out HDF5 file sizes, making writers that have already
# written a lot of data wait longer
def determine_wait_time(wnum, filesizes, min_wait=0.001, max_wait=0.010):
    min_size = min(filesizes.values())
    max_size = max(filesizes.values())

    dw = max_wait - min_wait
    dsize = max_size - min_size
    if dsize == 0:
        return min_wait
    asize = filesizes[wnum]

    return min_wait + (asize - min_size) / dsize * dw

# HDF5Vault uses many processes to open files and compress their data, and (typically) 
# fewer processes to write that data into an archive.

# There are four different type of tasks a process can do, depending on its rank:

# master: obtain list of files, inform compressors which files to compress. track progress.
# compressors: obtain name of file to read and compress. send compressed data to write coordinator. repeat.
# write coordinator: receive compressed data from compressors. send off to writers upon request.
# writer: ask write coordinator which data to write. write it to file. repeat.

# Master (rank=0): obtains list of files and listens to incoming connections. 1 requests types:
# - RECV: give me the path to a new file that I can compress (worker)
# - SEND: here's a file to compress
# - RECV: I have compressed file X and sent it off to a writer
# Write coordinator (rank=1): Receives compressed data and sends it to writers
# - RECV: here's data for file X I compressed (from worker)
# - RECV: send me more data (from writer)
# - SEND: write this to disk (to worker)
# writer (rank=2 to 2+nwriters): 
# - RECV: write this data to disk
# worker (rank=1+nwriters to ncpus):
# - SEND: send me a filename (to master) 
# - RECV: filename (from master)
# - SEND: here's a compressed file (to write coordinator)
# - SEND: i compressed this file and sent it to the write coordinator (to master)

def master_function(tdir: Path, nworkers: int, comm: MPI.Intracomm, comm_writers: MPI.Intracomm, prog_step: int):
    filelist=[]

    if not tdir.is_dir():
        logger.error(f"{tdir} is not a directory")
        comm.Abort(1)

    t0=time()
    file_iter = iter_files(tdir)
    t1=time()
    list_files_time=t1-t0

    # dict with key filename and value number of chunks in that file
    files_compressed = {}

    # a dict with an entry for each file written to disk. each entry is a dict with chunk_number: writer_rank
    files_written = {}

    workers_finished = set()

    status = MPI.Status()

    nchunks_written = 0
    chunk_counter=0

    file_counter=0

    # loop continues until all workers have been sent stop tag and all files have been confirmed stored
    while len(workers_finished) < nworkers or nchunks_written < chunk_counter:
        logger.debug(f'MA: waiting for connections')
        rdata = comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)
        worker_rank = status.Get_source()
        logger.debug(f'MA: received message with tag {status.Get_tag()} from rank {worker_rank}')

        if status.Get_tag() == request_filename_tag:
            filename = next(file_iter, False) # return False if iterator is exhausted
            if filename: 
                files_written[filename] = []
                comm.send(filename, dest=worker_rank, tag=send_filename_tag)
                logger.debug(f'MA: sending {filename} to {worker_rank}')
                if (file_counter % 1000 == 0):
                    logger.info(f'Found {file_counter} files ...')
                file_counter+=1
            else:
                comm.send(None, dest=worker_rank, tag=stop_tag)
                logger.debug(f'MA: sending stop tag to {worker_rank}')
                workers_finished.add(worker_rank)

        elif status.Get_tag() == file_compressed_tag:
            compressed_file=rdata["filename"]
            files_compressed[compressed_file] = rdata["total_chunks"]
            logger.debug(f'MA: received compression confirmation from {worker_rank} for file {compressed_file}')

            chunk_counter+=rdata["total_chunks"]

        elif status.Get_tag() == data_written_tag:
            written_file=rdata["filename"]
            chunk=rdata["chunk"]
            # continue here: this will be list, with each entry a dict
            #files_written[written_file][chunk] = worker_rank
            files_written[written_file].append(
                {"chunk": chunk, "archive_number": rdata["archive_number"], "dataset": rdata["dataset"], "compression": rdata["compression"] } 
            )
            
            nchunks_written += 1
            logger.debug(f'MA: received write confirmation from {worker_rank}')

            if nchunks_written % prog_step == 0:
                logger.info(f'{nchunks_written}  files or chunks written to archive.')

    logger.debug(f'MA: sending stop tag to rank=1 (write coordinator)')
    comm.send(None, dest=1, tag=compression_complete_tag)

    logger.debug(f'MA: asserting all chunks have been written')

    success = True
    for key in files_written.keys():
        #if files_written[key] is False:
        if len(files_written[key]) != files_compressed[key]:
            logger.error(f"MA: file {key} has not been confirmed as written (completely). Number of chunks = {files_compressed[key]}, chunks_written = {len(files_written[key])}.")
            success = False

    # exchange archive info with writers
    logger.debug('MA: broadcasting archive info ')
    comm_writers.bcast(files_written, root=0)

    if not success:
        comm.Abort(1)
    else:
        logger.info('MA: all chunks confirmed as written')

    return file_counter, chunk_counter, list_files_time

def write_coordinator_function(nwriters: int, comm: MPI.Intracomm):
    status = MPI.Status()

    compression_completed = False
    writers_stopped = set()

    cdata = []
    
    filesizes = {n: 0 for n in range(nwriters)}

    # the write coordinator is active until
    # - all files have been compressed and sent off to write coordinator) AND
    # - all writers have been sent a stop_tag by the write coordinator

    while not compression_completed or len(writers_stopped) < nwriters:
        logger.debug(f"CO: waiting for messages")
        ndata=comm.recv(source=MPI.ANY_SOURCE, tag=MPI.ANY_TAG, status=status)

        msg_source = status.Get_source()

        # a compressor (worker) is delivering data that has been compressed
        if status.Get_tag() == cdata_wo_to_co_tag:
            logger.debug(f'CO: received data of type {type(ndata)} from {msg_source}')
            """
            filename=ndata["filename"]
            buffer_cmp=ndata["buffer_cmp"]

            if filename in cdata.keys():
                logger.error(f'CO: data for file {filename} is already in cdata')
                comm.Abort()

            cdata[filename] = buffer_cmp
            """
            # in this version, the fifo stack is just a list, and I add the whole dict
            # as received to it
            cdata.append(ndata)

        # a writer is requesting data to write
        elif status.Get_tag() == request_cdata_tag:
            logger.debug(f'CO: received data request from {msg_source}')
            if msg_source == 0 or msg_source >= nwriters + 2:
                logger.error("CO: received cdata request from unexpected source")
                comm.Abort(1)

            writer_rank = msg_source - 2

            # 3 possibilities: 
            # a. there is data to write -> send it to the writer, and remove it from buffer
            # b. there is currently no data to write available, but compression ongoing. send wait_tag to writer 
            # c. there is no data, and compression is complete. send stop_tag to writer

            if len(cdata) == 0:
                if not compression_completed:
                    sleeptime = determine_wait_time(writer_rank, filesizes)
                    comm.send(sleeptime, dest=msg_source, tag=wait_tag)
                    logger.debug(f'CO: sent sleep tag (sleeptime = {sleeptime}) to {msg_source}')
                else:
                    comm.send(None, dest=msg_source, tag=stop_tag)
                    writers_stopped.add(msg_source)
                    logger.debug(f"CO: sent stop tag to writer {msg_source}")
            else:
                #filename = list(cdata.keys())[0]
                #ndata = cdata.pop(filename)
                ndata=cdata.pop()

                comm.send(#{"filename": filename,
                          #  "buffer_cmp": ndata}, 
                          ndata,
                            dest=msg_source, 
                            tag=cdata_co_to_wr_tag)

                filesizes[writer_rank] += len(ndata["buffer"])

        elif status.Get_tag() == compression_complete_tag and status.Get_source() == 0:
            logger.debug(f'CO: received compression complete tag from {msg_source}')
            compression_completed=True

    return

def writer_function(nwriters: int, comm: MPI.Intracomm, comm_writers: MPI.Intracomm, rank: int, 
                    archive_basename: str, cmethod: str, 
                    chunksize: int, 
                    usezip: bool=False):

    status = MPI.Status()
    waittime = 0 # time writers spend waiting
    metatime = 0 # time for writing metadata
    writetime = 0 # time for writing bytes
    wrcotime = 0 # time for communication (writers)

    stopped=False

    # each writers writes to its own file
    if nwriters == 1:
        multifile = False
        filenum = 0
    else:
        multifile = True
        filenum = rank - 2

    ext = "h5" if not usezip else "zip"

    if multifile:
        ndecimals = len(str(nwriters))
        h5filename=f"{archive_basename}_{filenum:0{ndecimals}d}.{ext}"
        print(h5filename)
    else:
        h5filename=f"{archive_basename}.{ext}"
    
    all_dsets = []

    if not usezip: 
        ctx=h5py.File(h5filename, 'w')

    else:
        ctx=zipfile.ZipFile(h5filename, mode='w', compression=zipfile.ZIP_STORED)

    with ctx as archive:
        while not stopped:
            if not usezip:
                archive.attrs["__Description__"] = HDF5_ARCHIVE_INFO
                archive.attrs["__HDF5Vault_version__"] = __version__
                if multifile:
                    archive.attrs["__HDF5Vault_archive_file_number__"] = filenum
                    archive.attrs["__HDF5Vault_number_of_archive_files__"] = nwriters
                archive.attrs["__HDF5Vault_chunksize__"] = chunksize

            logger.debug(f'WR {rank} is waiting for data to write')
            comm.send(None, dest=1, tag=request_cdata_tag)

            ta=time()
            ndata=comm.recv(source=1, tag=MPI.ANY_TAG, status=status)

            msg_tag = status.Get_tag()

            if msg_tag == wait_tag:
                logger.debug(f'WR {rank} received wait tag')
                sleep(ndata) # the transmitted number is the wait time
                waittime += ndata

            elif msg_tag == stop_tag:
                logger.debug(f'WR {rank} received stop tag')
                stopped=True

            elif msg_tag == cdata_co_to_wr_tag:
                if ndata is None:
                    logger.error("WR: received None data to write")
                    comm.Abort(1)
                logger.debug(f"WR {rank} received data to write for file {ndata['filename']}")

                # now dump the data to disk
                t0 = time()
                #if cmethod.lower() == 'none':

                if ndata["chunk"] is None:
                    dset_basename = ndata["filename"]
                else:
                    chunknumber=ndata["chunk"]
                    total_chunks = ndata["total_chunks"]
                    ndecimals = len(str(total_chunks))
                    dset_basename = ndata["filename"] + f"____part{chunknumber:0{ndecimals}d}"

                if ndata['compression'] is None:
                    dset_name = dset_basename
                else:
                    dset_name = dset_basename + "." + cmethod

                if not usezip:
                    dset_shape = len(ndata["buffer"])
                    all_dsets.append(ndata["filename"])

                    archive.create_dataset(dset_name, 
                                        shape=dset_shape,
                                        dtype=np.byte,
                                        compression=None)

                t1=time()

                if not usezip:
                    archive[dset_name][:] = np.frombuffer(ndata["buffer"], dtype=np.byte)

                    if ndata["chunk"] is not None:
                        archive[dset_name].attrs['chunk'] = chunknumber
                        archive[dset_name].attrs['number_of_chunks'] = total_chunks

                    # compression is now file-specific
                    archive[dset_name].attrs['compression'] = ndata["compression"] if ndata["compression"] is not None else "None"
                    archive.flush()


                else:
                    archive.writestr(dset_name, ndata["buffer"])

                t2=time()

                wrcotime += t0 - ta
                metatime += t1 - t0
                writetime += t2 - t1

                logger.debug(f"WR: sending write confirmation from rank {rank} to rank 0")

                # confirmation data to be sent back to master
                conf_data={"filename": ndata["filename"],
                           "chunk": ndata["chunk"],
                           "dataset": dset_name,
                           "archive_number": filenum,
                           "compression": ndata["compression"]}

                comm.send(conf_data, 
                          dest=0, tag=data_written_tag)

        # end of while loop

        logger.debug('WR: waiting for archive info broadcast')
        archive_info={}
        archive_info = comm_writers.bcast(archive_info, root=0 )
        # create HDF5 dataset with list of files
        logger.debug(f'Writing archive info attribute to {h5filename}.') # formerly __filelist__
        if not usezip:
            archive.attrs["__HDF5Vault_info__"] = json.dumps(archive_info, indent=3)

        else:
            archive.writestr("__HDF5Vault_info__", json.dumps(archive_info, indent=3))


    # end of with, closing file

    return waittime, metatime, writetime, wrcotime

def compressor_function(comm: MPI.Intracomm, rank: int, tdir: Path, cmethod: str, nthreads: int, clevel: int, use_dict: bool, chunksize:int):
    status = MPI.Status()

    finished = False

    # keep track of times and sizes

    readtime = 0 # time for reading
    comptime = 0 # time for compression
    raw_size = 0 # raw data size
    comp_size = 0 # compressed data size
    wocotime = 0 # time for communication (compressors)

    while not finished:
        logger.debug(f"WO: rank {rank}: Requesting new file from master")
        comm.send(None, dest=0, tag=request_filename_tag)
        filename=comm.recv(source=0, tag=MPI.ANY_TAG, status=status)

        if status.Get_tag() == stop_tag:
            finished = True
            logger.debug(f"WO: finished on worker {rank}")
        else:

            # do compression
            filepath = tdir.joinpath(filename)
            logger.debug(f"WO: opening {filepath} on rank {rank}")

            #buffer_cmp=compress_buffer(buffer, cmethod, nthreads=nthreads, clevel=clevel, use_dict=use_dict, filename=filename)
            for cfiled in compress_file(filepath, cmethod, comm, chunksize=chunksize, nthreads=nthreads, clevel=clevel, use_dict=use_dict):
                if cfiled["buffer"] is None:
                    comm.Abort(1)

                raw_size += cfiled["raw_size"]
                comp_size += len(cfiled["buffer"])

                logger.debug(f"WO: sending compressed data from {filename} (chunk {cfiled['chunk']}) from rank {rank} to rank 1")

                # add filename 
                cfiled["filename"] = filename
                t2=time()
                comm.send(cfiled,
                        dest=1, # to write coordinator
                        tag=cdata_wo_to_co_tag)

                t3=time()

                readtime += cfiled["read_time"]
                comptime += cfiled["compression_time"]
                wocotime += t3-t2

                # try removing this to speed things up
                #req.wait()

            logger.debug(f"WO: sending compression confirmation from rank {rank} to rank 0")
            # sending to rank 0 the filename and the number of chunks that file was split into
            comm.send({key: cfiled[key] for key in ["filename","total_chunks"]},
                       dest=0, tag=file_compressed_tag)
    
    return readtime, comptime, wocotime, comp_size, raw_size

def create_hdf5_archive(tdir,
                        h5file_basename,
                        nwriters=2, 
                        cmethod='blosc2', 
                        nthreads=4,
                        clevel=8,
                        use_dict=True,
                        prog_step=1000,
                        usezip=False,
                        chunksize=100_000_000):

    comm=MPI.COMM_WORLD

    ncpus=comm.Get_size()
    rank=comm.Get_rank()

    if rank==0 and usezip:
        print("Using zip format.")

    assert ncpus > (2 + nwriters), 'The number of ranks must be at least 2 + nwriters + 1'

    nworkers = ncpus - 2 - nwriters

    """
    Example:
    0 master
    1 write coordinator
    2 writer
    3 writer
    4 worker
    """

    # create a communicator with the master and all the workers
    if rank == 0 or rank >= 2+nwriters:
        color = 0 # master
        readtime = 0
        comptime = 0
        raw_size = 0
        comp_size = 0
        wocotime = 0
    else:
        color = 1
    comm_workers=comm.Split(color, 0)
        
    # create a communicator with the master and all the writers
    if rank == 0 or rank > 1 and rank < 2+nwriters:
        color2 = 0
        metatime = 0
        writetime = 0
        wrcotime = 0
        waittime = 0
    else:
        color2 = 1
    comm_writers=comm.Split(color2, 0)

    status = MPI.Status()

    time_begin = time()

    # master
    if rank == 0:
        nfiles,nchunks,list_files_time=master_function(tdir, nworkers, comm, comm_writers,prog_step)

    # write coordinator
    elif rank==1:
        write_coordinator_function(nwriters, comm)
        
    # writer
    elif rank > 1 and rank < 2+nwriters:
        waittime,metatime,writetime,wrcotime=writer_function(nwriters, comm, comm_writers, rank, h5file_basename, cmethod, 
                                                             chunksize, usezip)

    # compressor
    elif rank >= nwriters+2:
        readtime,comptime,wocotime,comp_size,raw_size=compressor_function(comm, rank, tdir, cmethod, nthreads, 
                                                                          clevel, use_dict, chunksize)
        
    logger.debug(f'ALL: rank {rank} at end of code.')
    comm.Barrier()
    time_end = time()

    # collecting statistics

    if color == 0:
        readtime = comm_workers.allreduce(readtime, op=MPI.SUM)
        comptime = comm_workers.allreduce(comptime, op=MPI.SUM)
        raw_size = comm_workers.allreduce(raw_size, op=MPI.SUM)
        comp_size = comm_workers.allreduce(comp_size, op=MPI.SUM)
        wocotime = comm_workers.allreduce(wocotime, op=MPI.SUM)

    if color2 == 0:
        metatime = comm_writers.allreduce(metatime, op=MPI.SUM)
        writetime = comm_writers.allreduce(writetime, op=MPI.SUM)
        wrcotime = comm_writers.allreduce(wrcotime, op=MPI.SUM)
        waittime = comm_writers.allreduce(waittime, op=MPI.SUM)

    if rank==0:
        sratio = raw_size / comp_size
        tp = naturalsize(comp_size / (writetime / nwriters))

        #effective throughput, data written during session divided by wallclock time
        tpe = naturalsize(comp_size / (time_end-time_begin))

        print(f'------------- Compression and performance summary ----------')
        print(f'Raw data size: {naturalsize(raw_size)}, {intword(nfiles)} files ({intcomma(raw_size)} bytes, {intcomma(nfiles)} files, {intcomma(nchunks)} chunks)')
        print(f'Compressed data size {cmethod}: {naturalsize(comp_size)} ({comp_size} bytes); storage ratio = {sratio}')
        print(f'Wallclock time to read, compress and write ({nworkers} compressors ({nthreads} threads), {nwriters} writers: {(time_end-time_begin):.3f} seconds.')
        print(f'Wallclock time retrieve list of files to archive (serial): {list_files_time:.3f} seconds.')
        print(f'Total CPU time spent on reading : {readtime:.3f} seconds.')
        print(f'Total CPU time spent on compressing ({cmethod}): {comptime:.3f} seconds.')
        print(f'Total CPU time spent on writing : {writetime:.3f} seconds, throughput {tp}/s (effective {tpe}/s).')
        print(f'Total CPU time spent on metadata : {metatime:.3f} seconds.')
        print(f'Total CPU time spent on communication by workers: {wocotime:.3f} seconds.')
        print(f'Total CPU time spent on communication by writer(s): {wrcotime:.3f} seconds.')
        print(f'Total CPU time spent idling by writer(s): {waittime:.3f} seconds.')

def main():
    parser = argparse.ArgumentParser(
                    prog='hdf5vault_create',
                    description=f'MPI tool for parallel archiving of large number of files in HDF5 container (version {__version__})')

    parser.add_argument('target_directory', type=Path, help='name of directory to archive')
    parser.add_argument('HDF5_archive_file_base', help='base of HDF5 archive file name')
    parser.add_argument('-w', '--writers', type=int, default=2, help='number of writers and archive files (default: 2)')
    parser.add_argument('-t', '--threads', type=int, default=4, help='number of threads per compressor (default: 4)')
    parser.add_argument('-c', '--clevel', type=int, default=8, help='compression level (1-9, default: 8)')
    parser.add_argument('-m', '--cmethod', type=str, default='blosc2', help='compression method: blosc2 (default) or None)')
    parser.add_argument('-d', '--use_dict', action='store_true', help='use dictionaries in compression (default: False)')
    parser.add_argument('-z', '--zip', action='store_true', help='create ZIP container(s) instead of HDF5 (default: False)')
    parser.add_argument('-s', '--chunksize', type=int, default=1_000_000_000, help='maximum chunk size to compress, in bytes (default 1 GB, max 2.1 GB)')
    parser.add_argument('-e', '--debug', action="store_true", help='print debugging information')
    parser.add_argument('-q', '--quiet', action="store_true", help='minimal output')

    args=parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)

    assert args.clevel > 0 and args.clevel < 9, "clevel must be between 1 and 9."

    create_hdf5_archive(args.target_directory,
                        args.HDF5_archive_file_base,
                        nwriters=args.writers,
                        clevel=args.clevel,
                        use_dict=args.use_dict,
                        nthreads=args.threads,
                        cmethod=args.cmethod,
                        usezip=args.zip,
                        chunksize=args.chunksize
                       )
                        

    return

if __name__ == "__main__":
    main()
