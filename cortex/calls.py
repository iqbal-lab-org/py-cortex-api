import os
import glob
import shutil

import pyfastaq

from . import settings
from . import utils


class _IndexPaths:
    def __init__(self, directory):
        self.directory = directory

        self.names_file = os.path.join(self.directory, '.fofn')
        self.dump_binary_ctx = os.path.join(self.directory, '.k31.ctx')
        self.stampy = os.path.join(self.directory, '.stampy')
        self.reference_fai = os.path.join(self.directory, 'ref.fa.fai')


def _make_indexes_files(reference_fasta, index_paths, mem_height=22):
    with open(index_paths.names_file, 'w') as f:
        print(os.path.abspath(reference_fasta), file=f)

    cortex_var = os.path.join(settings.CORTEX_ROOT, 'bin', 'cortex_var_31_c1')
    utils.syscall(' '.join([
        cortex_var,
        '--kmer_size 31',
        '--mem_height', str(mem_height),
        '--mem_width 100',
        '--se_list', index_paths.names_file,
        '--max_read_len 10000',
        '--dump_binary', index_paths.dump_binary_ctx,
        '--sample_id REF',
    ]))

    os.unlink(index_paths.names_file)

    utils.syscall(' '.join([
        settings.STAMPY_SCRIPT,
        '-G', index_paths.stampy,
        reference_fasta,
    ]))

    utils.syscall(' '.join([
        settings.STAMPY_SCRIPT,
        '-g', index_paths.stampy,
        '-H', index_paths.stampy,
    ]))


def _replace_sample_name_in_vcf(infile, outfile, sample_name):
    changed_name = False

    with open(infile) as f_in, open(outfile, 'w') as f_out:
        for line in f_in:
            if not line.startswith('#CHROM'):
                print(line, end='', file=f_out)
                continue

            fields = line.rstrip().split('\t')
            if len(fields) < 10:
                raise Exception('Not enough columns in VCF header line of VCF', line)
            elif len(fields) == 10:
                fields[9] = sample_name
                print(*fields, sep='\t', file=f_out)
                changed_name = True
            else:
                raise Exception('More than one sample in VCF', line)

    if not changed_name:
        raise Exception('No #CHROM line found in VCF file', infile)


class _CortexCallsPaths:
    def __init__(self, directory):
        self.directory = os.path.abspath(directory)

        self.cortex_log = os.path.join(self.directory, 'cortex.log')
        self.cortex_output_directory = os.path.join(self.directory, 'cortex.out')
        self.cortex_reads_fofn = os.path.join(self.directory, 'cortex.in.fofn')
        self.cortex_reads_index = os.path.join(self.directory, 'cortex.in.index')
        self.cortex_reference_fofn = os.path.join(self.directory, 'cortex.in.index_ref.fofn')


def _make_calls_input_files(reads_file, calls_paths: _CortexCallsPaths, index_paths: _IndexPaths):
    os.mkdir(calls_paths.directory)

    with open(calls_paths.cortex_reads_fofn, 'w') as f:
        print(reads_file, file=f)

    with open(calls_paths.cortex_reads_index, 'w') as f:
        print('sample', calls_paths.cortex_reads_fofn, '.', '.', sep='\t', file=f)

    with open(calls_paths.cortex_reference_fofn, 'w') as f:
        print(os.path.join(index_paths.directory, 'ref.fa'), file=f)


def _cleanup_calls_files(sample_name, calls_paths: _CortexCallsPaths):
    shutil.rmtree(os.path.join(calls_paths.cortex_output_directory, 'tmp_filelists'))

    for filename in glob.glob(os.path.join(calls_paths.cortex_output_directory, 'binaries', 'uncleaned', '**', '**')):
        if not (filename.endswith('log') or filename.endswith('.covg')):
            os.unlink(filename)

    for filename in glob.glob(os.path.join(calls_paths.cortex_output_directory, 'calls', '**')):
        if os.path.isdir(filename):
            for filename2 in os.listdir(filename):
                if not filename2.endswith('log'):
                    os.unlink(os.path.join(filename, filename2))
        elif not (filename.endswith('log') or filename.endswith('callsets.genotyped')):
            os.unlink(filename)

    for filename in glob.glob(os.path.join(calls_paths.cortex_output_directory, 'vcfs', '**')):
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


def _execute_calls(calls_paths: _CortexCallsPaths, index_paths: _IndexPaths, mem_height=22):
    genome_size = pyfastaq.tasks.stats_from_fai(index_paths.reference_fai)['total_length']
    cortex_calls_script = os.path.join(settings.CORTEX_ROOT, 'scripts', 'calling', 'run_calls.pl')

    command = ' '.join([
        cortex_calls_script,
        '--fastaq_index', calls_paths.cortex_reads_index,
        '--auto_cleaning yes',
        '--first_kmer 31',
        '--bc yes',
        '--pd no',
        '--outdir', calls_paths.cortex_output_directory,
        '--outvcf cortex',
        '--ploidy 2',
        '--stampy_hash', os.path.join(index_paths.directory, 'ref.stampy'),
        '--stampy_bin', settings.STAMPY_SCRIPT,
        '--list_ref_fasta', calls_paths.cortex_reference_fofn,
        '--refbindir', index_paths.directory,
        '--genome_size', str(genome_size),
        '--qthresh 5',
        '--mem_height', str(mem_height),
        '--mem_width 100',
        '--vcftools_dir', settings.VCFTOOLS_DIRECTORY,
        '--do_union yes',
        '--ref CoordinatesAndInCalling',
        '--workflow independent',
        '--logfile', calls_paths.cortex_log,
    ])
    utils.syscall(command)


def run(reference_fasta, reads_file, output_directory, sample_name):
    indexes_directory = os.path.join(output_directory, 'indexes')
    index_paths = _IndexPaths(indexes_directory)
    _make_indexes_files(reference_fasta, index_paths, mem_height=22)

    calls_paths = _CortexCallsPaths(output_directory)

    _make_calls_input_files(reads_file, calls_paths, index_paths)
    _execute_calls(calls_paths, index_paths)
    _cleanup_calls_files(sample_name, calls_paths)
