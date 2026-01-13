## 0.1.1 - 2025-05-08
- Initial release

## 0.1.2 - 2025-05-12
- changed requirement from python-blosc2 to blosc2

## 0.1.3 - 2025-05-12
- changed executable names to hdf5vault_create and hdf5vault_check
- added missing dependencies
- moved main() dedicated function

## 0.1.4 - 2025-05-28
- updated README.md file

## 0.1.5 - 2025-05-28
- expanded documentation, fixed prog name in Argumentparser

## 0.1.6 - 2025-09-05
- added option to create zip archives instead of HDF5 archives
- added parallel extraction tool 
- fixed bug that skipped hidden files

## 0.1.7 - 2025-09-05
- added parallel extraction as standalone command

## 0.1.9 - 2025-12-11
- additional error handler for compression

## 0.2.0 - 2025-12-12
- overlapping file scanning with archiving.

## 0.2.1 - 2025-12-17
- overlapping file scanning with verification.

## 0.3.0 - 2025-12-22
- chunking large files into segments (`-s` or `--chunksize` option) to avoid BLOSC errors with files larger than 2.1 GB
- moved archive information (file name, chunk numbers and locations, compression) into HDF5 attribute `__HDF5Vault__info__` (as JSON)
- redesigned MPI schedule for unpacking tool. 
- added support for ZIP format in verification tool
- no longer compressing files where no storage gain is achieved
- introduced version number in archive header
- breaks compatibility with earlier versions for extraction and verification

## 0.3.1 -- 2026-07-01
- bug fix with importing common functions
