import os
import glob
import shutil
import tempfile
import sys
from pathlib import Path
from typing import List, Union

from . import settings
from . import utils

StrPath = str
PathLike = Union[StrPath, Path]


class _CortexIndex:
    def __init__(self, directory: Path):
        self.base = directory.resolve()

        self.ref_names_file = self.base / 'fofn'
        self.reference_fasta = self.base / 'ref.fa'
        self.dump_binary_ctx = self.base / 'k31.ctx'
        self.stampy = self.base / 'stampy'

    def make(self, reference_fasta: Path, mem_height=22):
        with self.ref_names_file.open('w') as f:
            print(str(reference_fasta), file=f)

        cortex_var = os.path.join(settings.CORTEX_ROOT, 'bin', 'cortex_var_31_c1')
        utils.syscall([
            cortex_var,
            '--kmer_size', 31,
            '--mem_height', str(mem_height),
            '--mem_width', 100,
            '--se_list', self.ref_names_file,
            '--max_read_len', 10000,
            '--dump_binary', self.dump_binary_ctx,
            '--sample_id', 'REF',
        ])

        self.ref_names_file.unlink()

        utils.syscall([
            'python2',
            settings.STAMPY_SCRIPT,
            '-G', self.stampy,
            reference_fasta,
        ])

        utils.syscall([
            'python2',
            settings.STAMPY_SCRIPT,
            '-g', self.stampy,
            '-H', self.stampy,
        ])


class _CortexCall:
    """
    fofn: file of file names
    """

    def __init__(self, directory: Path, reference_fasta: Path):
        self.base: Path = directory.resolve()
        self.base.mkdir(parents=True, exist_ok=True)

        self.cortex_log = self.base / 'cortex.log'
        self.cortex_output_directory = self.base / 'cortex_output'
        self.cortex_reads_fofn = self.base / 'cortex_in.fofn'
        self.cortex_reads_index = self.base / 'cortex_in.index'
        self.cortex_reference_fofn = self.base / 'cortex_in_index_ref.fofn'

        self.index = _CortexIndex(self.base)
        self.index.make(reference_fasta)


    def make_input_files(self, reads_files: List[Path]):
        self.base.mkdir(parents=True, exist_ok=True)

        # List sample's read files
        with self.cortex_reads_fofn.open('w') as f:
            for reads_file in reads_files:
                print(reads_file, file=f)

        # Sample name + file listing read files
        with self.cortex_reads_index.open('w') as f:
            print('sample', self.cortex_reads_fofn, '.', '.', sep='\t', file=f)

        with self.cortex_reference_fofn.open('w') as f:
            print(self.index.reference_fasta, file=f)


    def execute_calls(self, reference_fasta, mem_height=22):
        number_of_bases_in_reference = utils.get_sequence_length(reference_fasta)
        cortex_calls_script = os.path.join(settings.CORTEX_ROOT, 'scripts', 'calling', 'run_calls.pl')

        # See https://github.com/iqbal-lab/cortex/tree/master/doc for guidance on command arguments
        command = [
            cortex_calls_script,
            '--first_kmer', 31,
            '--fastaq_index', self.cortex_reads_index,
            '--auto_cleaning', 'yes',
            '--bc', 'yes',
            '--pd', 'no',
            '--outdir', self.cortex_output_directory,
            '--outvcf', 'cortex',
            '--ploidy', '2',
            '--stampy_hash', self.index.stampy,
            '--stampy_bin', settings.STAMPY_SCRIPT,
            '--list_ref_fasta', self.cortex_reference_fofn,
            '--refbindir', self.index.base,
            '--genome_size', number_of_bases_in_reference,
            '--qthresh', 5,
            '--mem_height', mem_height,
            '--mem_width', 100,
            '--vcftools_dir', settings.VCFTOOLS_DIRECTORY,
            '--do_union', 'yes',
            '--ref', 'CoordinatesAndInCalling',
            '--workflow', 'independent',
            '--logfile', self.cortex_log,
        ]

        try:
            utils.syscall(command)
        except Exception:
            # In cortex, stderr and stdout gets written log files so that raised errors in this API do not necessarily get what
            # Actually caused the error.
            print("----------------------------\n"
                  "Please refer to cortex log file at {} for more information.".format(self.cortex_log),
                  file=sys.stderr)
            exit()


def _find_final_vcf_file_path(cortex_directory: Path):
    path_pattern = cortex_directory / 'cortex_output/vcfs/*_wk_*FINAL*raw.vcf'
    found = list(glob.glob(path_pattern, recursive=True))
    if len(found) == 0:
        return None
    if len(found) > 1:
        raise ValueError("Multiple possible output cortex VCF files found")
    return found[0]


def _replace_sample_name_in_vcf(input_file_path, output_file_path, sample_name):
    changed_name = False

    with open(input_file_path) as f_in, open(output_file_path, 'w') as f_out:
        for line in f_in:
            if not line.startswith('#CHROM'):
                print(line, end='', file=f_out)
                continue

            fields = line.rstrip().split('\t')
            if len(fields) < 10:
                raise RuntimeError('Not enough columns in VCF header line of VCF', line)
            elif len(fields) == 10:
                fields[9] = sample_name
                print(*fields, sep='\t', file=f_out)
                changed_name = True
            else:
                raise RuntimeError('More than one sample in VCF', line)

    if not changed_name:
        raise RuntimeError('No #CHROM line found in VCF file', input_file_path)


def _cleanup_calls_files(sample_name, calls_paths: _CortexCall):
    shutil.rmtree(calls_paths.cortex_output_directory / 'tmp_filelists')

    for filename in glob.glob(calls_paths.cortex_output_directory / 'binaries' /
                              'uncleaned' / '**' / '**'):
        if not (filename.endswith('log') or filename.endswith('.covg')):
            os.unlink(filename)

    for filename in glob.glob(calls_paths.cortex_output_directory / 'calls' / '**'):
        if os.path.isdir(filename):
            for filename2 in os.listdir(filename):
                if not filename2.endswith('log'):
                    os.unlink(os.path.join(filename, filename2))
        elif not (filename.endswith('log') or filename.endswith('callsets.genotyped')):
            os.unlink(filename)

    for filename in glob.glob(calls_paths.cortex_output_directory / 'vcfs' / '**'):
        if filename.endswith('.vcf'):
            tmp_vcf = filename + '.tmp'
            _replace_sample_name_in_vcf(filename, tmp_vcf, sample_name)
            utils.rsync_and_md5(tmp_vcf, filename)
            os.unlink(tmp_vcf)

        if not ((filename.endswith('.vcf') and 'FINAL' in filename) or filename.endswith(
                'log') or filename.endswith('aligned_branches')):
            if os.path.isdir(filename):
                shutil.rmtree(filename)
            else:
                os.unlink(filename)


def run(reference_fasta: StrPath, reads_files: List[StrPath], output_vcf_file_path: StrPath,
        sample_name='sample_name', tmp_directory=None, cleanup=True) -> None:
    reference_fasta = Path(reference_fasta)
    reads_files = [Path(reads_file).resolve() for reads_file in reads_files]

    if tmp_directory is None:
        tmp_directory = tempfile.mkdtemp()
    tmp_directory = Path(tmp_directory).resolve()

    caller = _CortexCall(tmp_directory, reference_fasta)
    caller.make_input_files(reads_files)
    caller.execute_calls(reference_fasta)

    final_vcf_path = _find_final_vcf_file_path(tmp_directory)
    if final_vcf_path is not None:
        shutil.copyfile(final_vcf_path, output_vcf_file_path)
    else:
        message = f"No vcf found as output. Please check logs in {tmp_directory} for reasons."
        raise FileNotFoundError(message)

    if cleanup:
        shutil.rmtree(tmp_directory)
    else:
        _cleanup_calls_files(sample_name, caller)
