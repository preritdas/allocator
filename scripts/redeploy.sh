#!/bin/sh

shopt -s extglob

mkdir protected &&
mv *.ini protected &&
sudo rm -rf !(protected) &&
git clone https://github.com/preritdas/allocator.git &&
mv allocator/* . &&
mv protected/* . &&
sudo rm -rf allocator protected