import sys
import hashlib
import subprocess


def syscall(command):
    completed_process = subprocess.run(command,
                                       shell=True,
                                       stderr=subprocess.STDOUT,
                                       stdout=subprocess.PIPE,
                                       universal_newlines=True)
    if completed_process.returncode == 0:
        return completed_process

    print('Error running this command:', command, file=sys.stderr)
    print('Return code:', completed_process.returncode, file=sys.stderr)
    print('Output from stdout and stderr:', completed_process.stdout, sep='\n', file=sys.stderr)
    raise Exception('Error in system call. Cannot continue')


def md5(filename):
    """Given a file, returns a string that is the md5 sum of the file"""
    # see https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def rsync_and_md5(old_name, new_name, md5sum=None):
    """Copies a file from old_name to new_name using rsync.
    Double-checks the copy was successful using md5. Returns md5.
    If you already know the md5 of the file, then save time
    by providing it with the md5sum option - this will avoid
    calculating it on the old file.
    """
    if md5sum is None:
        md5sum = md5(old_name)

    syscall('rsync ' + old_name + ' ' + new_name)
    new_md5sum = md5(new_name)

    if new_md5sum != md5sum:
        raise Exception('Error copying file ' + old_name + ' -> ' + new_name + '\n. md5s do not match')
    else:
        return md5sum
