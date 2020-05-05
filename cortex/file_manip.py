import glob
import hashlib
from typing import Optional, Union
from pathlib import Path

from cortex.utils import syscall

StrPath = str
PathLike = Union[StrPath, Path]


class MissingVcfFile(Exception):
    pass


class TooManyVcfFiles(Exception):
    pass


def _find_final_vcf_file_path(cortex_directory: Path) -> Optional[PathLike]:
    vcf_pattern = cortex_directory / "cortex_output" / "vcfs" / "*.vcf"
    found_vcfs = glob.glob(str(vcf_pattern))

    if not found_vcfs:
        return None

    final_vcf_pattern = "*_wk_*FINAL*raw.vcf"
    path_pattern = cortex_directory / "cortex_output" / "vcfs" / final_vcf_pattern
    found = glob.glob(str(path_pattern))
    if len(found) == 0:
        raise MissingVcfFile(
            f"Vcfs found in output: {found_vcfs}, "
            f"but none matches {final_vcf_pattern}."
        )
    if len(found) > 1:
        raise TooManyVcfFiles(
            f"Multiple possible final "
            f"cortex VCF files matching {final_vcf_pattern} found: {found}"
        )
    return found[0]


def _make_empty_vcf(output_file_path: PathLike, sample_name: str):
    print(
        "Cortex made no vcfs, so making an empty one.\n"
        "Known possible reasons why no vcf:\n"
        "\t Read or reference size < kmer size\n"
        "\t No variants found during bubble calling"
    )
    header_lines = [
        "##fileformat=VCFv4.2",
        '##FILTER=<ID=PASS,Description="All filters passed">',
    ]
    header_tabs = [
        "#CHROM",
        "POS",
        "ID",
        "REF",
        "ALT",
        "QUAL",
        "FILTER",
        "INFO",
        "FORMAT",
        sample_name,
    ]
    with open(str(output_file_path), "w") as f_out:
        print(*header_lines, sep="\n", file=f_out)
        print(*header_tabs, sep="\t", file=f_out)


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
