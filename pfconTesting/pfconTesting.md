# Controlling Plugins Execution on Local Computer Through pfcon and pman on Docker Swarm
## Initial Setup 
Following the steps from the pfcon [README](https://github.com/FNNDSC/pfcon/blob/71a76907402c61f7f8126d4652d6763f839908a9/README.rst):
<br>
1. Clone the pfcon repository, then change into the pfcon directory
```
clone https://github.com/FNNDSC/pfcon.git 
cd pfcon
```
2. Initialize a new docker swarm on your machine 
```
docker swarm init
```
3. Run ./make.sh
```
./make.sh
```

## Pulling Image Containers to Local Machine
Depending on the workflow you are trying to implement, you will need to pull the related docker images from the [FNNDSC docker hub](https://hub.docker.com/u/fnndsc). To do so, you just need to run
```
docker pull fnndsc/<DOCKER-IMGAGE-NAME>
```
where \<DOCKER-IMAGE-NAME> is the just the name of the app you want to run. 
## Initial Example Using pl-simplefsapp and pl-simpledsapp
First step was pulling the images down from Docker hub
```
docker pull fnndsc/pl-simplefsapp
docker pull fnndsc/pl-simpledsapp
```
Then, following the steps outlined [here](https://github.com/FNNDSC/pfcon/wiki/pfcon-http-API-call-examples#using-curl) execute the following:
<br>
### Request a JSON Web Token (JWT) from pfcon
```
curl -H 'Content-Type: application/json' -X POST -d '{"pfcon_user": "pfcon", "pfcon_password": "pfcon1234"}' http://localhost:30006/api/v1/auth-token/
```
This token will allow you to communicate with pfcon, and this token needs to be included in all requests sent to pfcon that involve job requests. You are sending a post request to the pfcon api at /auth_token/, and taking a look in pfcon's [app.py](https://github.com/FNNDSC/pfcon/blob/master/pfcon/app.py#L31) we see that this is an api endpoint defined in the [resources.py](https://github.com/FNNDSC/pfcon/blob/master/pfcon/resources.py#L184) file. This simply checks for a valid username and password, then assigns a JWT token that will be valid for 2 days. 
### Submit the pl-simplefsapp Plugin for Execution 
```
curl -H "Authorization: Bearer <token>" -F args=--saveinputmeta -F args=--saveoutputmeta -F args=--dir -F args=cube/uploads -F args_path_flags=--dir -F auid=cube -F number_of_workers=1 -F cpu_limit=1000 -F memory_limit=200 -F gpu_limit=0 -F image=fnndsc/pl-simplefsapp -F entrypoint=python3 -F entrypoint=/usr/local/bin/simplefsapp -F type=fs -F jid=chris-jid-1 -F data_file=@/tmp/in/test.zip http://localhost:30006/api/v1/jobs/
```
Using the \<token> provided from the previous step, we are submitting a job with jobid = 1 for execution. You specify the plugin you want to use with the "image", and the "entrypoint" arguments define the command(s) to be run within the container created using the specified image. With the exeption of the "args_path_flags" argument, all of the others are required, and if they are not included, the curl reqeust will return 400 status code, indicating there is a missing parameter. 
### Submit the pl-simpledsapp Plugin for Execution
```
curl -H "Authorization: Bearer <token>" -F args=--saveinputmeta -F args=--saveoutputmeta -F args=--prefix -F args=lolo -F auid=cube -F number_of_workers=1 -F cpu_limit=1000 -F memory_limit=200 -F gpu_limit=0 -F image=fnndsc/pl-simpledsapp -F entrypoint=python3 -F entrypoint=/usr/local/bin/simpledsapp -F type=ds -F data_file=@/tmp/in/test.zip -F jid=chris-jid-2 http://localhost:30006/api/v1/jobs/
```
Here we are copying the process from the previous step, updating the image and entrypoint agruments accordingly; we also need to update the job id number, otherwise we will get a 409 conflict status code indicating that the there is a conflict as the object already exists. 

---
 **_NOTE:_**  A python client for executing through the pfcon api is also available [here](https://github.com/FNNDSC/python-pfconclient/blob/c81546e0225d8e486f911fad4586d8dc4313b4ee/README.rst) 

---
## Submitting Other Plugins for Execution

 One of the plugins that I wanted to try exectuing was pl-create_tetra, and after submitting a similar request as seen above for simplefsapp, and replacing the two entrypoint arguments with 
```
-F entrypoint=python3 
-F entrypoint=/usr/local/bin/create_tetra_wrapper
``` 
 
 ``` 
 curl -H "Authorization: Bearer "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJwZmNvbl91c2VyIjoicGZjb24iLCJleHAiOjE2Njc2MzE4Mzh9.gAKsl7P4l9Uarw8-b06Y2p9vhVtoPCNSkCfvD2C7KCc"" -F args=--saveinputmeta -F args=--saveoutputmeta -F args=--dir -F args=cube/uploads -F args_path_flags=--dir -F auid=cube -F number_of_workers=1 -F cpu_limit=1000 -F memory_limit=200 -F gpu_limit=0 -F image=fnndsc/pl-create_tetra -F entrypoint=python3 -F entrypoint=/usr/local/bin/create_tetra_wrapper -F type=fs -F jid=chris-jid-19 -F data_file=@/tmp/in/test.zip http://localhost:30006/api/v1/jobs/

 ```
 which returned the following
 ```
 {
    "data": {
        "jid": "chris-jid-19",
        "nfiles": 1,
        "timestamp": "2022-11-03 07:56:07.829959",
        "path": "/var/local/storeBase/key-chris-jid-19/incoming"
    },
    "compute": {
        "jid": "chris-jid-19",
        "image": "fnndsc/pl-create_tetra",
        "cmd": "python3 /usr/local/bin/create_tetra_wrapper --saveinputmeta --saveoutputmeta --dir /share/incoming /share/outgoing",
        "status": "notstarted",
        "message": "pending task scheduling",
        "timestamp": "2022-11-03T07:56:07.86661151Z",
        "logs": ""
    }
}
 ```
One of the issues I ran into while trying to run plugins other than the simple fs/ds ones desribed above arose because the entrypoint argument specifying the location of the python app to run (create_tetra_wrapper in my case) was not located in the same position in the each containers file system. 

It appeared that the process had completed without error, but the expected final output sphere was absent in the target output directory, which indicated that the app within the container was not actually executing. This error happened because I had mistakenly assumed that all of the other plugins would follow a similar pattern for specifying the location of the python script within the container.

I spent a while trying to modify the other argument parameters to try and resolve this issue, but after that proved unsuccesful, I was pointed to [this documentation](https://github.com/FNNDSC/CHRIS_docs/blob/e65ac6a2cf3dabd6a5ef8b7057881f7fd06161d5/specs/ChRIS_Plugins.adoc#arguments) which explained why I was having trouble getting commands to execute as expected. Specifically, the "cmd" field - which is populated by the "entrypoint" arguments- needs to be structured in a particular fashion, which is:
 ```
 {execshell} {selfpath}{selfexec}
 ```
 In order to find the execshell, selfpath, and selfexec specifications for a given ChRIS plugin, you can send a curl request to the ChRIS store's api for your app of choice. Using pl-create_tetra as an example, you would navigate to https://chrisstore.co/plugin/pl-create_tetra, click on the "Install to ChRIS" button, and copy the provided link, in this case https://chrisstore.co/api/v1/plugins/217/. Then execute the following command
 ```
curl https://chrisstore.co/api/v1/plugins/217/ accept:application/json |json_pp
 ```

 ---

 **_NOTE:_** piping with "| json_pp" is not necessary, it just makes the response easier to read

 ---


 which returns the json specification for the plugin
 ```
{
 "collection": {
  "href": "https://chrisstore.co/api/v1/plugins/217/",
  "items": [
   {
    "data": [
     {
      "name": "id",
      "value": 217
     },
     {
      "name": "creation_date",
      "value": "2022-08-26T06:33:12.696307-04:00"
     },
     {
      "name": "name",
      "value": "pl-create_tetra"
     },
     {
      "name": "version",
      "value": "1.0.0"
     },
     {
      "name": "dock_image",
      "value": "fnndsc/pl-create_tetra:1.0.0"
     },
     {
      "name": "public_repo",
      "value": "https://github.com/FNNDSC/pl-create_tetra"
     },
     {
      "name": "icon",
      "value": ""
     },
     {
      "name": "type",
      "value": "fs"
     },
     {
      "name": "stars",
      "value": 0
     },
     {
      "name": "authors",
      "value": "Jennings Zhang <Jennings.Zhang@childrens.harvard.edu>"
     },
     {
      "name": "title",
      "value": "create_tetra"
     },
     {
      "name": "category",
      "value": "Modeling"
     },
     {
      "name": "description",
      "value": "A ChRIS fs plugin wrapper for create_tetra"
     },
     {
      "name": "documentation",
      "value": "https://github.com/FNNDSC/pl-create_tetra"
     },
     {
      "name": "license",
      "value": "MIT"
     },
     {
      "name": "execshell",
      "value": "/opt/conda/bin/python3.10"
     },
     {
      "name": "selfpath",
      "value": "/opt/conda/bin"
     },
     {
      "name": "selfexec",
      "value": "create_tetra_wrapper"
     },
     {
      "name": "min_number_of_workers",
      "value": 1
     },
     {
      "name": "max_number_of_workers",
      "value": 1
     },
     {
      "name": "min_cpu_limit",
      "value": 1000
     },
     {
      "name": "max_cpu_limit",
      "value": 2147483647
     },
     {
      "name": "min_memory_limit",
      "value": 100
     },
     {
      "name": "max_memory_limit",
      "value": 2147483647
     },
     {
      "name": "min_gpu_limit",
      "value": 0
     },
     {
      "name": "max_gpu_limit",
      "value": 0
     }
    ],
    "href": "https://chrisstore.co/api/v1/plugins/217/",
    "links": [
     {
      "href": "https://chrisstore.co/api/v1/plugins/217/parameters/",
      "rel": "parameters"
     },
     {
      "href": "https://chrisstore.co/api/v1/102/",
      "rel": "meta"
     }
    ]
   }
  ],
  "links": [],
  "version": "1.0"
 }
}
 ```
 Here we can see that for pl-create_tetra the execshell, selfpath, and selfexec are defined as: 
 ```
   {
      "name": "execshell",
      "value": "/opt/conda/bin/python3.10"
     },
     {
      "name": "selfpath",
      "value": "/opt/conda/bin"
     },
     {
      "name": "selfexec",
      "value": "create_tetra_wrapper"
     },
 ```
Replacing the entrypoint commands with the above arguments in the previous curl request resulted in the response:
 ```
{
    "data": {
        "jid": "chris-jid-9",
        "nfiles": 1,
        "timestamp": "2022-11-03 08:18:14.889246",
        "path": "/var/local/storeBase/key-chris-jid-9/incoming"
    },
    "compute": {
        "jid": "chris-jid-9",
        "image": "fnndsc/pl-create_tetra",
        "cmd": "/opt/conda/bin/python3.10 /opt/conda/bin/create_tetra_wrapper --saveinputmeta /share/outgoing",
        "status": "notstarted",
        "message": "pending task scheduling",
        "timestamp": "2022-11-03T08:18:14.947549847Z",
        "logs": ""
    }
}
 ```
 and the output folder was populated with the expected output file. Generally speaking, the process for launching any ChRIS plugin using pfcon is
1. Search for the plugin on the [ChRIS Store](https://chrisstore.co/)
2. Copy the url provided by clicking on the "Install to ChRIS" button
3. Send a curl request to that copied url
4. Make note specifically of the "execshell", "selfpath", and "selfexec" parameters that are returned 
5. Send a curl request with entrypoint arguments set as 
```
-f entrypoint={execshell} -f entrypoint={selfpath}{selfexec}
```

 **_NOTE:_** It was also necessary to specify the following argument in order for the output to show up in the target output directory. I'm still not sure why this is the case, though I thought it valuable to mention regardless. 
 ```
-f args=--saveoutputmeta 
 ```


## Closing Docker Swarm 
In order to shut down the swarm and its associated process, simply run 
```
./unmake.sh
```
## Adding API Endpoints to pfcon
 
I also added in a couple of new API endpoints for pfcon to get a better understanding of how the communication from outside is handled within pfcon. In the [app.py](https://github.com/FNNDSC/pfcon/blob/master/pfcon/app.py#L8) file, you can see that all of the api endpoints specified for pfcon are located in the [resources.py](https://github.com/FNNDSC/pfcon/blob/master/pfcon/resources.py) file. Depending on its expected function, the api endpoints will either require certain arguments, or in the case of the healthcheck endpoint, no arguments are required and it exists simply to let the user know the service is functional. Following the format from HealthCheck, I added in a similar class to return "hello world" to the user when the api was contacted at the specified endpoint ('/hello/'). 
<br><br>
I also added in another simple endpoint which I specified as requiring a post request. Its a fairly crude implementation, as it requires you submit the curl request with all of the arguments that would get passed in submiting jobs to pfcon, though its only checks the value of one of those arguments. When contacted, it returns a link to a gif if the argument args_path_flags is "hello", and returns the the ip address of the host otherwise. 

