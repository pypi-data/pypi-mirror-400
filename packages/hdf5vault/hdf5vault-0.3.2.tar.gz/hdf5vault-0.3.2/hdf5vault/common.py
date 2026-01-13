import h5py
import logging
from pathlib import Path
import json
import zipfile

# determine archive format (h5 or zip) from multiple files
def determine_format(files: list[Path]):
    ext = set([Path(a).suffix.lstrip('.') for a in files])
    assert len(ext) == 1, 'all archives must be of same type (have same extension)'

    cext=ext.pop().lower()

    if cext not in ["h5", "zip"]: 
        return False

    return cext

def check_archive_files(archive_files: list, logger: logging.RootLogger):
    n_archives = len(archive_files)

    multifile = False if n_archives == 1 else True

    filelist_inarch = dict()

    numbered_archives={}

    qc_passed=True

    for n,archive_file in enumerate(archive_files):
        logger.info(f'Reading HDF5 attributes from {archive_file}...')
        if not Path(archive_file).is_file():
            logger.error(f"archive file {archive_file} does not exist or is not a regular file.")
            return None, None, False

        with h5py.File(archive_file, 'r') as hfile:
            if "__HDF5Vault_version__" not in hfile.attrs.keys():
                logger.error("This archive was created with a prior version < 0.3.0 of HDFVault and can not be verified with this version.")
                return None, None, False
            if multifile:
                n_archives2=hfile.attrs["__HDF5Vault_number_of_archive_files__"]
                if n_archives != n_archives2:
                    logger.error(f"number of archives in {archive_file} is inconsistent with number of files passed to program.")
                    qc_passed=False

                filenum=hfile.attrs["__HDF5Vault_archive_file_number__"]
            else:
                if "__HDF5Vault_number_of_archive_files__" in hfile.attrs.keys():
                    logger.error(f"{archive_file} attribute suggets multi-file-archive, but only one HdF5 file was provided.")
                    qc_passed=False
                filenum=0

            numbered_archives[int(filenum)] = archive_file

            # filelist_inarch is a dictionary where each key is a file name
            if n==0:
                filelist_inarch=json.loads(hfile.attrs["__HDF5Vault_info__"])
            else:
                if "__HDF5Vault_info__" not in hfile.attrs.keys():
                    logger.warning(f"Error. Archive {archive_file} does not contain entry __HDF5Vault_info__.")
            
    if set(numbered_archives.keys()) != set(range(n_archives)):
        logger.error('inconsistent file numbering')
        qc_passed=False

    return filelist_inarch, numbered_archives, qc_passed


def check_zip_files(archive_files: list[str], logger: logging.RootLogger):
    archive_file = archive_files[0]

    if not Path(archive_file).is_file():
        return None, False

    ctx=zipfile.ZipFile(archive_file, 'r')

    try:
        filelist_inarch=json.loads(ctx.read('__HDF5Vault_info__'))

    except KeyError:
        logger.error(f'Could not read __HDF5Vault__ from {archive_file}.  Zipfile was not created by HDF5Vault >= 0.3.0 or is incomplete.')
        return None, False

    except:
        logger.error(f'Could not parse __HDF5Vault__ from {archive_file}.')
        return None, False

    numbered_archives={}

    for n,archive_file in enumerate(archive_files):
        archnum=int(Path(archive_file).stem.split("_")[-1])
        if archnum != n:
            logger.warning(f"Inferred archive number {archnum} inconsistent with order as passed {n}. Aborting.")
        numbered_archives[n] = archive_file
    
    return filelist_inarch, numbered_archives, True