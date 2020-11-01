#!/bin/sh
rm -rf spegg
git clone https://github.com/spilikin/spegg.git
./spegg/mongo_import.sh
rm -rf spegg
