#!/bin/bash
set -eux

input=$(echo $1 | tr 'onf/' 'ONFx' )
output=$(echo $2 | tr 'onf/' 'ONFx' )
output="$input-$output"

if [[ ! -f $input.grib ]]; then
mars<<EOF
retrieve,
   levtype=sfc,
   param=2t,
   grid=$1,
   target=$input.grib
EOF
fi

if [[ ! -f $output.json ]]; then

~/build/mir/src/tools/mir --grid=$2 --dump-weights-info=$output.json $input.grib /dev/null

fi

python3 -c "from earthkit.regrid import make_matrix; make_matrix('$output.json')"

rm -f $output.json
