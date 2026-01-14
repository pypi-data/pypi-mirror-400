#!/bin/bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR
cd ..
bash scripts/build-install.sh

seastar ifcb_v4_features -i testdata/*.hdr -o testout/
seastar ifcb_to_ecotaxa -i testdata/*.hdr testdata/*.csv testmetadata/static_metadata.csv --operator "Placeholder Name" --project "Test Project" --ship "Very Nice Ship" --depth 5 --tableonly -o testout/ecotaxa_test.tsv
