HDF5_ARCHIVE_INFO= """
This HDF5 file is (part of) a file archive created with HDF5Vault (https://pypi.org/project/hdf5vault/). 

In this archive format, HDF5 is used as a hierarchival container for storing the content of a number of archived files.  Every HDF5 dataset in this archive contains the contents of a file or file chunk.  The (raw or compressed) bytes in the file or chunk are interpreted as 1-D dimensional array of type byte.  The dataset name mirrors the file name, while group names reflect directories and subdirectories in the archived data structure.

If the file is stored uncompressed and unchunked, the dataset name reflects the file name exactly. If the file has been split into chunks, the chunk number is appended to the dataset name (e.g., `___part1`). If the contents of the file have been compressed, the suffix `.blosc2` is added the the dataset name. 

This HDF5 file contains several attributes with additonal information:

__Description__: This text
__HD5Vault_version__: HDF5Vault version number
__HD5Vault_chunksize__: The size of a file chunk. Files smaller than this size are stored unchunked.
__HDF5Vault_info__: A JSON string with information on the chunking, compression and archive number of each archived file.

This file may be a part of a multi-file HDF5 archive. In this case, the following two attributes are present in each archive file:
__HDF5Vault_archive_file_number__: number of current file
__HDF5Vault_number_of_archive_files__: total number of files that make up the archive

EXAMPLE 

The original archived directory contains these files:
    README.txt
    directory1/small_datafile.bin
    directory2/big_datafile.bin

The resulting HDF5 archive(s) contains the datasets
    README.txt (dataset, type bytes)
    directory1/ (group)
    direcory1/small_datafile.bin.blosc2 (dataset, type bytes)
    direcory2/big_datafile.bin___part1.blosc2 (dataset, type bytes)
    direcory2/big_datafile.bin___part2.blosc2 (dataset, type bytes)

The HDF5 attribute __HDF5Vault_info__ is a JSON-formatted dictionary with information on the archived files.  Each key represents the path of the archived file, and the value is a list of dictionaries with storage information for each chunk, including chunk number (null if unchunked), dataset name, archive number, and compression used.

In the above example, __HDF5VAULT_info__  contains:

{
    "README.txt": [
        {
        "chunk": null,
        "archive_number": 0,
        "dataset": "README.txt",
        "compression": null
        }
    ],
    "directory1/small_datafile.bin": [
        {
        "chunk": null,
        "archive_number": 1,
        "dataset": "directory1/small_datafile.bin.blosc2",
        "compression": "blosc2"
        }
    ],
    "directory2/big_datafile.bin": [
        {
        "chunk": 0,
        "archive_number": 0,
        "dataset": "directory2/big_datafile.bin____part0.blosc2",
        "compression": "blosc2"
        },
        {
        "chunk": 1,
        "archive_number": 1,
        "dataset": "directory2/big_datafile.bin____part1.blosc2",
        "compression": "blosc2"
        }
            ]
}

That is, the file README.txt is stored unchunked and uncompressed in archive number 0 (example_0.h5).  The file directory2/big_datafile.bin is stored in two chunks located in archive 0 and 1, respectively, and each chunk was compressed using BLOSC2.  In multipart HDF5 archives, the attribute HDF5Vault is replicated in each archive file.

ARCHIVE UNPACKING

HDF5Vault comes with a parallel unpacking tool, hdf5vault_unpack. The following Python code snippet illustrates how the content of a compressed file in the archive can be restored:

    import h5py
    import blosc2

    with h5py.File('example_1.h5') as hfile:
        compressed_data = hfile["directory1/small_datafile.bin.blosc2"][:].tobytes()

    raw_data = blosc2.decompress(raw_data)

    with open("directory1/small_datafile.bin", "rb") as fid:
        fid.write(raw_data)

"""