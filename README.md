# py-cortex-api
Python API for [cortex](https://github.com/iqbal-lab/cortex).

# Install
```
pip3 install git+https://github.com/iqbal-lab-org/py-cortex-api
```

#### Requirements

R is required by `cortex` at runtime.
```
sudo apt install r-base-core
```

# Usage
Inputs:
    * a reference genome in fasta[.gz] 
    * one or more reads file in fasta/q[.gz]
    
>Use a list to pass in reads files, even if there is only one file.
    
Output:
    A vcf with variants detected by cortex.


```python
import cortex.calls as cortex
cortex.run("./reference.fasta",
             ["./reads.fastq"],
             "./output.vcf")
```
The third argument is where to place the output vcf.

## Options

The following options can be passed to `cortex.run`:
* `sample_name`: sample name to appear in output vcf (default: 'sample').
* `ploidy`: 1 or 2, for haploid or diploid genotyping (default: 1)
* `mem_height`: if `cortex.calls` fails warning of too low memory, use a higher value (default: 22).
* `tmp_directory`: where to place intermediate output and log files (default: system-defined)
* `cleanup`: whether to remove intermediate output and log files upon successful completion. (Default: True)

# Licence
MIT
