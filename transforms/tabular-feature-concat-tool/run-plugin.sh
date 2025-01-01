#!/bin/bash
version=$(<VERSION)
datapath=$(readlink --canonicalize data)

# Inputs
inpDir=/data/input
metaDir=/data/meta
filePattern="x{x:d+}_y{y:d+}_c{c:d}.arrow"
groupBy=x,y
channelName=c 
plateName=CD_SOD1_2_E1023974__1
features=intensity_image,mask_image,MEAN
metaCols=row_number,col_number

# Output paths
outDir=/data/output


# Log level, must be one of ERROR, CRITICAL, WARNING, INFO, DEBUG
LOGLEVEL=INFO

docker run --mount type=bind,source=${datapath},target=/data/  \
            --env POLUS_LOG=${LOGLEVEL} \
            polusai/tabular-feature-concat-tool:${version} \
            --inpDir ${inpDir} \
            --filePattern ${filePattern} \
            --groupBy ${groupBy} \
            --channelName ${channelName} \
            --features ${features} \
            --metaDir ${metaDir} \
            --metaCols ${metaCols} \
            --plateName ${plateName} \
            --outDir ${outDir}
