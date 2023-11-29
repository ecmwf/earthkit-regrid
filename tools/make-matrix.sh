#!/bin/bash

# (C) Copyright 2023 ECMWF.
#
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.

set -eux

echo "-------------------------------------------------"

input=$(echo $1 | tr 'onf/' 'ONFx' )
output=$(echo $2 | tr 'onf/' 'ONFx' )
output_dir=${3:=-"matrices"}
output="$input-$output"
use_mars_cli=0

input_dir="grib"

[[ ! -d $input_dir ]] && mkdir $input_dir
[[ ! -d $output_dir ]] && mkdir $output_dir

# get mir version
version=$(~/build/mir/release/bin/mir --version x x 2>/dev/null | grep mir | cut -d ' '  -f 2)

input_grib=$input_dir/${input}.grib
output_json=$output_dir/${output}-${version}.json

# retrieve sameple grib file
if [[ ! -f ${input_grib} ]] ; then

   if [[ $use_mars_cli -ne 1 ]] ; then
      if [[  $input == "N2560" || $input == "O2560" ]] ; then
         class="rd"
         expver="i4ql"
      else
         class="od"
         expver="1"
      fi

      python3 -c "from earthkit.data import from_source; ds=from_source('mars', {'levtype': 'sfc', 'param': '2t', 'grid': '$1', 'class': '$class', 'expver': '$expver', 'type': 'fc', 'time': '0'}); ds.save('$input_grib')"
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

# generate interpolation matrix
if [[ ! -f ${output_json} ]]; then

   ~/build/mir/release/bin/mir --grid=$2 --dump-weights-info=${output_json} ${input_grib} /dev/null
   #~/build/mir/src/tools/mir --grid=$2 --dump-weights-info=$output.json $input.grib /dev/null
fi
   # process matrix and add it to index json file
   python3 -c "from earthkit.regrid.utils.matrix import make_matrix; make_matrix('$output_json','$output_dir',global_input=True,global_output=True,version='$version')"

   #rm -f $output_json
