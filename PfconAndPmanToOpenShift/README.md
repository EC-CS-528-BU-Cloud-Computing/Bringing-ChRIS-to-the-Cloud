# Setup

Prior to creating pfcon and pman using the provided template, you must create a persistent volume claim named 'storebase', as well as the required secret keys pfcon-secret and pman-secret.

To create the persistent volume claim, either use the OpenShift GUI or a yaml file and `oc apply -f <filename>` to create one.

For the secrets, feel free to change the values for the environment variables listed within the yaml files (do NOT change the actual variable names). Then, create the secrets by using `oc apply -f pfcon-secret.yml pman-secret.yml`.

# Creating Pfcon and Pman

With the setup completed, all you have to run is the following:

`oc process -f pfcon-pman-template-new.yml | oc create -f -`

That's it! If for whatever reason you'd like to change/update the instances of pfcon and pman currently running on OpenShift, run the following:

`oc process -f pfcon-pman-template-new.yml | oc replace -f -`
