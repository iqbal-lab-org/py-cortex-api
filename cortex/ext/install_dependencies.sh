#!/usr/bin/env bash

set -eu

install_root=$PWD/cortex/ext
mkdir -p $install_root


#________________________ minimap2 _________________________#
cd $install_root
minimap_version="v2.17"
minimap_dir="minimap2_dir"
if [[ ! -e "./${minimap_dir}" ]];then
  git clone https://github.com/lh3/minimap2 && mv minimap2 "$minimap_dir" 
  cd "$minimap_dir" && git checkout "$minimap_version" && make
  cd .. && mv "${minimap_dir}/minimap2" . && rm -rf "$minimap_dir"
fi


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
cortex_revision="f6ff4038238ca09e7e8ec4f6e45b260f1e51579b"
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
