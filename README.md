# py-cortex-api

Python API for [cortex](https://github.com/iqbal-lab/cortex).


# Install
```
pip3 install git+https://github.com/iqbal-lab-org/py-cortex-api
```

# Usage

```python
import cortex
cortex.calls("./reference.fasta",
             "./reads.fastq",
             "./output",
             "sample_name")
```