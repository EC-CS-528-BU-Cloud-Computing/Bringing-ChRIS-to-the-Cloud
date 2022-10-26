# _ChRIS_ Plugin From Template

## This plug-in was built to test the process of deploying an extremely simple app based on the ChRIS application environment on OpenShift

To test this, I wrote a really simple python script which makes an API call to ygoprodeck, available [here](https://ygoprodeck.com/api-guide/), requests 10 random cards from their database, and stores all of the information for each of those cards as a single line in a json file titled random_cards.json at the specified output_dir. 

In order to implement the app on OpenShift, a Docker image needed to be created. Building the image on my computer (an m1 mac) resulted in some issues, so I resorted to a bit of a workaround.
1. I used the OpenShift website to attempt to build the container from this github repository.
2. Once built, I copied the location of the image created on the internal OpenShift registry located in the administrator layout at Builds->ImageStreams->randomcard->details->Image Repository
3. I ran [create_randomcard.yml](https://github.com/lilloukas/ChRIS-App-From-Template/blob/a8947b4d6a8fe37d48270dcceef8d0812906689f/create_randomcard.yml) placing the copied image location at "image" [here](https://github.com/lilloukas/ChRIS-App-From-Template/blob/a8947b4d6a8fe37d48270dcceef8d0812906689f/create_randomcard.yml#L8) on my local computer, using oc apply -f create_randomcard.yml

A few notes:
1. The persistent volume claim used with this application was created on the OpenShift website
2. Given the pod is designed to start and then close, the restartPolicy specification needs to be set to OnFailure in the [create_randomcard.yml](https://github.com/lilloukas/ChRIS-App-From-Template/blob/a8947b4d6a8fe37d48270dcceef8d0812906689f/create_randomcard.yml#L13), otherwise the pod will enter into a CrashLoopBackOff error
3. This page will be updated after I've had the chance to build the docker image on a non-m1 mac to see if that resolves the need for the OpenShift imagestream workaround
<!-- BEGIN README TEMPLATE

# ChRIS Plugin Title

[![Version](https://img.shields.io/docker/v/fnndsc/pl-appname?sort=semver)](https://hub.docker.com/r/fnndsc/pl-appname)
[![MIT License](https://img.shields.io/github/license/fnndsc/pl-appname)](https://github.com/FNNDSC/pl-appname/blob/main/LICENSE)
[![ci](https://github.com/FNNDSC/pl-appname/actions/workflows/ci.yml/badge.svg)](https://github.com/FNNDSC/pl-appname/actions/workflows/ci.yml)

`pl-appname` is a [_ChRIS_](https://chrisproject.org/)
_ds_ plugin which takes in ...  as input files and
creates ... as output files.

## Abstract

...

## Installation

`pl-appname` is a _[ChRIS](https://chrisproject.org/) plugin_, meaning it can
run from either within _ChRIS_ or the command-line.

[![Get it from chrisstore.co](https://ipfs.babymri.org/ipfs/QmaQM9dUAYFjLVn3PpNTrpbKVavvSTxNLE5BocRCW1UoXG/light.png)](https://chrisstore.co/plugin/pl-appname)

## Local Usage

To get started with local command-line usage, use [Apptainer](https://apptainer.org/)
(a.k.a. Singularity) to run `pl-appname` as a container:

```shell
singularity exec docker://fnndsc/pl-appname commandname [--args values...] input/ output/
```

To print its available options, run:

```shell
singularity exec docker://fnndsc/pl-appname commandname --help
```

## Examples

`commandname` requires two positional arguments: a directory containing
input data, and a directory where to create output data.
First, create the input directory and move input data into it.

```shell
mkdir incoming/ outgoing/
mv some.dat other.dat incoming/
singularity exec docker://fnndsc/pl-appname:latest commandname [--args] incoming/ outgoing/
```

## Development

Instructions for developers.

### Building

Build a local container image:

```shell
docker build -t localhost/fnndsc/pl-appname .
```

### Running

Mount the source code `app.py` into a container to try out changes without rebuild.

```shell
docker run --rm -it --userns=host -u $(id -u):$(id -g) \
    -v $PWD/app.py:/usr/local/lib/python3.10/site-packages/app.py:ro \
    -v $PWD/in:/incoming:ro -v $PWD/out:/outgoing:rw -w /outgoing \
    localhost/fnndsc/pl-appname commandname /incoming /outgoing
```

### Testing

Run unit tests using `pytest`.
It's recommended to rebuild the image to ensure that sources are up-to-date.
Use the option `--build-arg extras_require=dev` to install extra dependencies for testing.

```shell
docker build -t localhost/fnndsc/pl-appname:dev --build-arg extras_require=dev .
docker run --rm -it localhost/fnndsc/pl-appname:dev pytest
```

## Release

Steps for release can be automated by [Github Actions](.github/workflows/ci.yml).
This section is about how to do those steps manually.

### Increase Version Number

Increase the version number in `setup.py` and commit this file.

### Push Container Image

Build and push an image tagged by the version. For example, for version `1.2.3`:

```
docker build -t docker.io/fnndsc/pl-appname:1.2.3 .
docker push docker.io/fnndsc/pl-appname:1.2.3
```

### Get JSON Representation

Run [`chris_plugin_info`](https://github.com/FNNDSC/chris_plugin#usage)
to produce a JSON description of this plugin, which can be uploaded to a _ChRIS Store_.

```shell
docker run --rm localhost/fnndsc/pl-appname:dev chris_plugin_info > chris_plugin_info.json
```

END README TEMPLATE -->
