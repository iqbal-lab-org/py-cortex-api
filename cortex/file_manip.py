import hashlib

from cortex.utils import syscall


# TODO: unused
def _replace_sample_name_in_vcf(input_file_path, output_file_path, sample_name):
    changed_name = False

    with open(input_file_path) as f_in, open(output_file_path, "w") as f_out:
        for line in f_in:
            if not line.startswith("#CHROM"):
                print(line, end="", file=f_out)
                continue

            fields = line.rstrip().split("\t")
            if len(fields) < 10:
                raise RuntimeError("Not enough columns in VCF header line of VCF", line)
            elif len(fields) == 10:
                fields[9] = sample_name
                print(*fields, sep="\t", file=f_out)
                changed_name = True
            else:
                raise RuntimeError("More than one sample in VCF", line)

    if not changed_name:
        raise RuntimeError("No #CHROM line found in VCF file", input_file_path)


# TODO: unused
def md5(filename):
    """Given a file, returns a string that is the md5 sum of the file"""
    # see https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file # noqa: E501
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


# TODO: unused
def rsync_and_md5(old_name, new_name, md5sum=None):
    """Copies a file from old_name to new_name using rsync.
    Double-checks the copy was successful using md5. Returns md5.
    If you already know the md5 of the file, then save time
    by providing it with the md5sum option - this will avoid
    calculating it on the old file.
    """
    if md5sum is None:
        md5sum = md5(old_name)

    syscall("rsync " + old_name + " " + new_name)
    new_md5sum = md5(new_name)

    if new_md5sum != md5sum:
        raise Exception(
            "Error copying file "
            + old_name
            + " -> "
            + new_name
            + "\n. md5s do not match"
        )
    else:
        return md5sum
