#!/usr/bin/env bash

set -eu

install_root=$PWD/cortex/ext
mkdir -p $install_root


#________________________ stampy _________________________#
python_path=$(which python2.7 || which python2)
if [[ -z "$python_path" ]]; then
  echo "ERROR: could not find python2.7 or python2 in \$PATH. Python 2 is needed
  to install and run cortex (dependency: stampy). Please install python 2 and try again"
  exit 1
fi

cd $install_root
stampy_version="1.0.32"
stampy_dir="stampy-${stampy_version}"
if [[ ! -e "./${stampy_dir}" ]];then
  wget "https://www.well.ox.ac.uk/~gerton/software/Stampy/${stampy_dir}r3761.tgz"
  tar xf "${stampy_dir}r3761.tgz"
  rm "${stampy_dir}r3761.tgz"
fi
cd "${stampy_dir}"
make python=python2
echo "Modifying shebang in file 'stampy.py' to point to python2."
sed -i '1s@.*@#!'"${python_path}"'@' stampy.py


#________________________ vcftools _______________________#
cd $install_root
vcftools_version="0.1.15"
vcftools_versioned_dir="vcftools-${vcftools_version}"
vcftools_target_dir="vcftools"
  if [[ ! -e "./${vcftools_target_dir}" ]];then
    wget "https://github.com/vcftools/vcftools/releases/download/v${vcftools_version}/${vcftools_versioned_dir}.tar.gz"
    tar xf "${vcftools_versioned_dir}.tar.gz"
    rm "${vcftools_versioned_dir}.tar.gz"
    mv "${vcftools_versioned_dir}" "${vcftools_target_dir}"
  fi
cd "${vcftools_target_dir}"
./configure --prefix $PWD/install
make
make install

# cortex needs the perl/ directory. It expects it to be in the vcftools root,
# but somehwere between v0.1.9 and v0.1.15 it moved into src/.
ln -sf src/perl/ .


#________________________ cortex _________________________#
cortex_revision="6d8e2f9f1984651c253bdd9d748acf6efa54c165"
cd $install_root
cortex_dir="cortex"
if [[ ! -e ${cortex_dir} ]];then
  git clone https://github.com/iqbal-lab/cortex
fi
cd cortex/
git checkout "${cortex_revision}"
bash install.sh
make NUM_COLS=1 cortex_var
make NUM_COLS=2 cortex_var
