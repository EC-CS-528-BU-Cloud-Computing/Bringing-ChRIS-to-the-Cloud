# Running ChRIS Apps on OpenShift Using pfcon and pman

## **Deploying pfcon and pman**
### **Setting up a New Service Account**
In order to run pfcon and pman on OpenShift, the first step was to create a new ServiceAccount, and associated Role and RoleBinding. 
To do so, you can use:
```
oc apply -f sa.yml
oc apply -f role.yml
oc apply -f binding.yml
```
This creates a new Service Account with the neccesary permissions to execute the required operations on OpenShift using kubernetes.
### **Updating the Deployment Template**

 We needed to make some modifications to our initial template, which is located [here](https://github.com/EC-CS-528-BU-Cloud-Computing/Bringing-ChRIS-to-the-Cloud/blob/main/PfconAndPmanToOpenShift/pfcon-pman-template-new.yml). 
 
 First, we needed to update the pman image that was being used. The updated `lilloukas/pman:v3` image- which was built using [this fork](https://github.com/lilloukas/pman_test) of the [original pman repository](https://github.com/FNNDSC/pman)- makes use of the changes [detailed below](#required-pman-modifications), all of which are neccesary for this setup to be operational.
 
 Then we needed to set the environment variable `CONTAINER_ENV = kubernetes`. This ensures that pman uses kubernetes to handle all tasks related to job creation within the cluster. 

 Finally, we needed to specify the Service Account that would be used by the pman pod. To do this, we added in `serviceAccountName: job-creator` (the Service Account created above) in the [pman pod specifications](add link). 

 Once these steps are complete, following the steps outlined [here](https://github.com/EC-CS-528-BU-Cloud-Computing/Bringing-ChRIS-to-the-Cloud/tree/main/PfconAndPmanToOpenShift) we can login to our OpenShift account and run the following:
 ```
oc process -f final_pfcon_pman_template.yml | oc create -f -
 ```

---
 **Note:** We added in the ` REMOVE_JOBS = no` environment variable for demo purposes, so that we could make sure the ChRIS plugins were running correctly. It is not necessary and can be removed if desired. 

## **Example of Running ChRIS Plugin using pfcon and pman on OpenShift**

TODO

## Required pman Modifications 
In order to get pman working correctly, a few modifications needed to be made in the existing pman code
1. Set the volume type as Persistent Volume in [kubernetesmgr.py](https://github.com/lilloukas/pman_test/blob/master/pman/kubernetesmgr.py#L173). You also need to hard-code the name of the persistent volume that will be used to store the input and output data for the ChRIS plugins, which is done by setting `claim_name = <PERSISTENT_VOLUME_CLAIM_NAME>`. The PVC that we mounted in pfcon was named 'storebase', so thats the name required for this setup to work. 
```
volume = k_client.V1Volume(
            name='storebase',
            persistent_volume_claim=k_client.V1PersistentVolumeClaimVolumeSource(claim_name = 'storebase')
        )
```
2. Update the argparser to set the type for the `jid` variable to a string in the [resources.py](https://github.com/lilloukas/pman_test/blob/master/pman/resources.py#L18). There was an issue with jid combing back as 'NoneType' and explicitly setting its type as a string solved this issue. 
```
parser.add_argument('jid', dest='jid', required=True,type = str)
```
3. In the call to `schedule_job` on [line 89 of resources.py](https://github.com/lilloukas/pman_test/blob/master/pman/resources.py#L89), we no longer need to pass the `share_dir` variable, since we are handling the directory issues in the previous step. 
4. In [JobListResource](https://github.com/lilloukas/pman_test/blob/master/pman/resources.py#L53), we need to hard-code the location of the input and output directories for the incoming and outgoing folders in the `build_app_command` method. This also requires that we pass `jid` as an argument to the `build_app_command` on [line 75 in resources.py](https://github.com/lilloukas/pman_test/blob/master/pman/resources.py#L75). 
```
def build_app_cmd(
            self,
            args: List[str],
            args_path_flags: Collection[str],
            entrypoint: List[str],
            plugin_type: Literal['ds', 'fs', 'ts'],
            job_id: str
    ) -> List[str]:
        input_dir = f'/share/key-{job_id}/incoming'
        output_dir = f'/share/key-{job_id}/outgoing'
        cmd = entrypoint + localize_path_args(args, args_path_flags, input_dir)
        if plugin_type == 'ds':
            cmd.append(input_dir)
        cmd.append(output_dir)
        return cmd
```
