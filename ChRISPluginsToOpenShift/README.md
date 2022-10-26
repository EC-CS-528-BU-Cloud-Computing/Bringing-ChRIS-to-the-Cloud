The YAML files contained within this folder were used to create the components of a simple ChRIS pipeline consisting of a FS plugin (pl-lungs_pnc) and a DS plugin (pl-dcm2niix) on OpenShift.

To create the resources represented by any of the yaml files above, ensure you have downloaded the OpenShift CLI and type the following command into your terminal:

`oc apply -f INSERT_FILENAME`

File Descriptions:
* input_pv.yml: Intended to create a persistent volume claim (CURRENTLY BUGGED - USE OPENSHIFT GUI FOR PV CREATION INSTEAD). This persistent volume was intended to hold the data produced by the FS plugin.
* fs_plugin.yml: Specifies a Pod on OpenShift that will run the FS plugin container. Mounts a persistent volume claimed on OpenShift.
* ds_plugin.yml: Specifies a Pod on OpenShift that will run the DS plugin container. Mounts the persistent volume containing the output data from the FS plugin as well as an additional persistent volume used to hold the output of the DS plugin.

*Note*: An additional persistent volume needs to be created to hold the data produced from the DS plugin. This was done using the OpenShift GUI, so no YAML file has been included.
