# Figlet as a Service

_FaaS_ provides the [FIGlet](https://en.wikipedia.org/wiki/FIGlet)
command over HTTP.

## Usage

```shell
$ curl https://figlet.chrisproject.org/\?message=Hello+World

 _   _      _ _         _    _            _     _
| | | |    | | |       | |  | |          | |   | |
| |_| | ___| | | ___   | |  | | ___  _ __| | __| |
|  _  |/ _ \ | |/ _ \  | |/\| |/ _ \| '__| |/ _` |
| | | |  __/ | | (_) | \  /\  / (_) | |  | | (_| |
\_| |_/\___|_|_|\___/   \/  \/ \___/|_|  |_|\__,_|

```

## Deployment on OpenShift

```shell
oc import-image nodejs:16 --from=quay.io/fedora/nodejs-16 --confirm
oc new-app nodejs:16~https://github.com/FNNDSC/figlet-faas.git
```
