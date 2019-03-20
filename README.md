# py-cortex-api
Python API for [cortex](https://github.com/iqbal-lab/cortex).

# Install
```
pip3 install git+https://github.com/iqbal-lab-org/py-cortex-api
```

#### Requirements
```
sudo apt install r-base-core
```

# Usage
```python
import cortex
cortex.calls("./reference.fasta",
             "./reads.fastq",
             "./output",
             "sample_name")
```

# Licence
MIT