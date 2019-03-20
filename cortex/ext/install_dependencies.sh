#!/usr/bin/env bash

install_root=$PWD/cortex/ext
mkdir -p $install_root


#________________________ stampy _________________________#
cd $install_root
wget http://www.well.ox.ac.uk/~gerton/software/Stampy/stampy-latest.tgz
tar xf stampy-latest.tgz
rm stampy-latest.tgz
cd stampy-*
make python=python2

# Warn if /usr/bin/env python does not point to python2; this is required for running stampy (is the stampy.py shebang).
match_py2=$(/usr/bin/env python --version 2>&1 | grep -E '[A-Za-z]+ 2\..*|^2\..*')
if [ -z "${match_py2}" ]; then
    echo -e "Warning: '/usr/bin/env python --version' does not return a python 2 version.\n"
    echo -e "Warning: Modifying shebang in file 'stampy.py' to point to python2."
    sed -i '1s@.*@#!'$(which python2)'@' stampy.py
fi


#________________________ vcftools _______________________#
cd $install_root
wget https://github.com/vcftools/vcftools/releases/download/v0.1.15/vcftools-0.1.15.tar.gz
tar xf vcftools-0.1.15.tar.gz
rm vcftools-0.1.15.tar.gz
mv vcftools-0.1.15 vcftools
cd vcftools
./configure --prefix $PWD/install
make
make install

# cortex needs the perl/ directory. It expects it to be in the vcftools root,
# but somehwere between v0.1.9 and v0.1.15 it moved into src/.
ln -s src/perl/ .



#________________________ cortex _________________________#
cd $install_root
wget --no-check-certificate -O cortex.tar.gz https://github.com/iqbal-lab/cortex/archive/master.tar.gz
tar xf cortex.tar.gz
rm cortex.tar.gz
mv cortex-master cortex
cd cortex/
bash install.sh
make NUM_COLS=1 cortex_var
make NUM_COLS=2 cortex_var
