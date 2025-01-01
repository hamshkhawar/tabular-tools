# Tabular Feature Concat (v0.1.0-dev3)

The **Tabular Feature Concat** plugin is designed to concatenate Nyxus channel features from multiple files, rename channels, and associate metadata according to user-defined parameters.

For more information on WIPP, visit the [official WIPP page](https://isg.nist.gov/deepzoomweb/software/wipp).

## Building

To build the Docker image for the conversion plugin, run
`./build-docker.sh`.

## Install WIPP Plugin

If WIPP is running, navigate to the plugins page and add a new plugin. Paste the contents of `plugin.json` into the pop-up window and submit.

## Options

This plugin takes nine input argument and one output argument:

| Name               | Description                                                | I/O    | Type          |
|--------------------|------------------------------------------------------------|--------|---------------|
| `--inpDir`         | Input data collection to be processed by this plugin       | Input  | genericData   |
| `--filePattern`    | Pattern to parse tabular files                             | Input  | string        |
| `--groupBy`        | Group files based on variable                              | Input  | string       |
| `--channelName`    | Variable for channel name                                 | Input  | string         |
| `--features`       | Merge tabular files with the same number of rows?          | Input  | string       |
| `--metaDir`        | Path to metadata directory                             | Input  | genericData       |
| `--metaCols`        | Metadata features for merging                             | Input  | string       |
| `--plateName`        | Plate name for merging with metadata                             | Input  | string      |
| `--outDir`         | Output file                                                | Output | genericData   |
| `--preview`        | Generate JSON file with outputs                            | Output | JSON          |

