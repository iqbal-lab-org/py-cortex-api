# py-cortex-api
Python API for [cortex](https://github.com/iqbal-lab/cortex).

# Install
```
pip3 install git+https://github.com/iqbal-lab-org/py-cortex-api
```

#### Requirements

R and python 2 are required.
```
sudo apt install r-base-core python2.7
```

# Usage
Use a list to pass in reads files, even if there is only one file.

```python
import cortex.calls as cortex
cortex.run("./reference.fasta",
             ["./reads.fastq"],
             "./output.vcf")
```
The third argument is where to place the output vcf.

## Options

That can be passed to `cortex.calls`:
* `sample_name`: sample name to appear in output vcf.
* `mem_height`: if `cortex.calls` fails warning of too low memory, use higher than the default of 22.
* `tmp_directory`: where to place intermediate output and log files
* `cleanup`: whether to remove intermediate output and log files upon successful completion. (Default: True)

# Licence
MIT
