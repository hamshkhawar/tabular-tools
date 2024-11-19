#!/bin/bash
version=$(<VERSION)
datapath=$(readlink --canonicalize data)

# Inputs
inpDir=/data/input
metaDir=/data/meta
filePattern="{row:c+}_{col:d+}_c{c:d}.arrow"
groupBy=row,col
channelName=c 
features=intensity_image,mask_image,MEAN

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
            --outDir ${outDir}
