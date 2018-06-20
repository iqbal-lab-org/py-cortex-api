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