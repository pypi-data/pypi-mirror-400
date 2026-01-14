"""Init module."""

import os
from comet.PTEmu import PTEmu as comet

def download(url, filename, size):
    """ Download file
    """
    from tqdm import tqdm
    import urllib.request

    with urllib.request.urlopen(url) as response:
        total = int(response.headers.get('Content-Length', 0))
        if total == 0: total = size
        with open(filename, 'wb') as f, tqdm(
            total=total, unit='B', unit_scale=True, unit_divisor=1024
        ) as bar:
            while True:
                chunk = response.read(8192)
                if not chunk:
                    break
                f.write(chunk)
                bar.update(len(chunk))

def download_data(download_dir):
    """
    Download the data needed for the emulators to the specified directory.

    Parameters
    ----------
    download_dir : str
        the data will be downloaded to this directory
    """
    from six.moves import urllib
    import shutil
    import gzip
    import glob

    urls = ['https://saco.csic.es/s/pqf9E5HERL6Pmw4/download',
            'https://saco.csic.es/s/WfPiczxNwFE8C7r/download',
            'https://saco.csic.es/s/Ct6zSczjoKXMJZJ/download']
    filenames = ['tables.zip', 'models.zip', 'VERSION']
    out_filenames = ['tables', 'models', 'VERSION']
    sizes = [734344124, 1523864502, 4]

    for i, url in enumerate(urls):

        file_path = os.path.join(download_dir+"/data_dir", filenames[i])
        final_path = os.path.join(download_dir+"/data_dir", out_filenames[i])

        print (f"Downloading {filenames[i]}")
        download(url, file_path, sizes[i])

        if out_filenames[i] != 'VERSION':
            print("Extracting files...")
            shutil.unpack_archive(
                filename=file_path, extract_dir=download_dir+"/data_dir")
            os.remove(file_path)
        print("Done.\n")

expected_version = "2.0"

base_dir = os.path.join(os.path.dirname(__file__))
data_dir = base_dir + "/data_dir"

version_path = os.path.join(data_dir, "VERSION")
if not os.path.exists(version_path):
    check = "missing"
else:
    with open(version_path, "r") as f:
        local_version = f.read().strip()
    if local_version != expected_version:
        check = "mismatch"
    else:
        check = "match"

if check == "missing":
    print(f"\nVERSION file is missing from {data_dir} folder. This may be due "
           "to attempting running the code for the first time or to a migration "
           "to version 2.1.0. The correct emulator files are going to be "
           "downloaded. This may take few minutes, depending on the speed of "
           "the download.\n")
    download_data(base_dir)
elif check == "mismatch":
    print (f"\nVERSION of emulator files specified in {version_path} is not "
           "consistent with the installed version of COMET. This may be due "
           "to a migration to a new version of COMET. The correct "
           "emulator files are going to be downloaded. This may take few "
           "minutes, depending on the speed of the download.\n")
    download_data(base_dir)

if __name__ == '__main__':
    comet = comet()
