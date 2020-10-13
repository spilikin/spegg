#!/bin/sh
git clone https://github.com/spilikin/spegg.git
cp -r spegg/mongo_import.sh spegg/data/ .
./mongo_import.sh