#!/bin/bash
set -eux

input=$(echo $1 | tr 'onf/' 'ONFx' )
output=$(echo $2 | tr 'onf/' 'ONFx' )
output_dir=${3:=-"matrices"}
output="$input-$output"
use_mars_cli=0

input_dir="grib"

[[ ! -d $input_dir ]] && mkdir $input_dir
[[ ! -d $output_dir ]] && mkdir $output_dir

input_grib=$input_dir/${input}.grib
output_json=$output_dir/${output}.json

if [[ ! -f ${input_grib} ]] ; then

   if [[ $use_mars_cli -ne 1 ]] ; then
      python3 -c "from earthkit.data import from_source; ds=from_source('mars', levtype='sfc', param='2t', grid='$1'); ds.save('$input_grib')"
   else
      echo 2
# mars<<EOF
#  retrieve,
#    levtype=sfc,
#    param=2t,
#    grid=$1,
#    target=${input_grib}
# EOF 
   fi
fi

if [[ ! -f ${output_json} ]]; then

   ~/build/mir/release/bin/mir --grid=$2 --dump-weights-info=${output_json} ${input_grib} /dev/null
   #~/build/mir/src/tools/mir --grid=$2 --dump-weights-info=$output.json $input.grib /dev/null

fi

python3 -c "from earthkit.regrid.utils.matrix import make_matrix; make_matrix('$output_json','$output_dir',global_input=True,global_output=True)"

rm -f $output_json
