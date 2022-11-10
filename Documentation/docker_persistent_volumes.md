# Using Docker Volumes to Persist ChRIS Plugin Data

## [Volume Creation in Docker](https://docs.docker.com/engine/reference/commandline/volume_create/)
The first step is to initialize an empty volume through docker using the following command:
```
docker volume create my_data
```
This volume can then be mounted inside a container to provide it with the ability for its data to persist beyond a single run.
## Illustrating the Lack of Data Persistence in Containers
After establishing a volume you can run the following command:
```
docker run --rm -it alpine sh -c 'echo hello > /tmp/example.txt
```
This is simply running a container using an alipne linux image and executing the command:
```
sh -c 'echo hello > /tmp/example.txt'
```
which prints the word hello to a plain text file named example.txt inside the container. As soon as the container exits, all data that was contained inside (including the newly created text file) is deleted. 
## Mounting a Volume Inside a Container
In order to have access to the data created by the container after it has exited, we need to specify a path inside the container where we can mount an external volume; this is accomplished using the following command:
```
docker run --rm -it --volume my_data:/insideContainer alpine sh -c 'echo hello >/insideContainer/example.txt'
```
We are executing the same command as seen in the previous section, except this time we are storing the output file `example.txt` inside the mounted volume at directory `/insideContainer`
## Confirming the Persisted Data Exists
We can confirm that the data was saved after the alpine container exited by executing the following:
```
run --rm -it --volume my_data:/differentPath debian cat /differentPath/example.txt
```
This runs a new debian container which executes the `cat` command to print the information read from the `example.txt` file which was mounted in this new container at directory `/differentPath`.
## Docker Volume Location on Local Computer
When creating the volume in the first step, docker is creating a path on your local filesystem, which can be confirmed by running: 
```
docker volume inspect my_data
```
which will show you the location of the volume on your local computer.
## ChRIS Specific Example
### Running an fs Plugin
Following a similar setup as before, first we create a new volume:
```
docker volume create my_chris_data
```
Then we run a ChRIS plugin as a container- in this case [pl-mri10yr06mo01da_normal](https://github.com/FNNDSC/pl-mri10yr06mo01da_normal)- with the volume mounted at `/outgoing`:
```
docker run --rm -it --volume my_chris_data:/outgoing fnndsc/pl-mri10yr06mo01da_normal mri10yr06mo01da_normal.py /outgoing
```
This plugin simply copies its data (an anonymized MRI from a child aged 10 years, 6 motnhs, and 1 day) to its output directory.

### Running a ds Plugin
Create a new volume for the ds plugin:
```
docker volume create my_chris_output_data
```
Run the ds plugin [pl-dcm2niix](https://github.com/FNNDSC/pl-dcm2niix)
```
docker run --rm -it -volume my_chris_data:/input -volume my_chris_output_data:/output fnndsc/pl-dcm2niix dcm2niix /input /output
```
This is mounting the first volume we created to store the output from the fs plugin to the `/input` directory inside the pl-dcm2niix container, followed by mounting the newly created my_chris_output_data volume to the `/output` directory inside the container. Then, we are executing dcm2niix and specifying the input and output directories. 
### Checking the Output Using Containers
To provide an example that mirrors your use-case on the MOC/OpenShift, we wont simply check the location on our local hardrive where the volume was created to confirm execution. Instead, we will create another container which mounts the my_chris_output_data volume, and inspect its elements from within this new container. To do so, we execute:
```
docker run --rm -it -p 8000:8000 -volume my_chris_output_data:/pathDoesntMatter python:slim bash
```
This is creating a simple container running [python](https://hub.docker.com/layers/library/python/slim/images/sha256-244c0b0e6e7608a16f87382fc8a5ef3c330d042113a9a7b6fc15a95360181651?context=explore), and also binds port 8000 in the container to port 8000 on the local machine in interactive mode. This allows us to then execute the following:
```
python -m http.server 8000
```
which runs an http server inside the container on port 8000. Because we previously bound the ports on our local machine, we can then go to `http://localhost:8000/` to see the output files. 

## General Setup for ChRIS fs Plugin
```
docker run <FLAGS> --volume <VOLUME_NAME> <PLUGIN_NAME> <PLUGIN_COMMAND> <OUTPUT_DIRECTORY>
```
## General Setup for ChRIS ds Plugin
```
docker run <FLAGS> --volume <INPUT_VOLUME_NAME> --volume <OUTPUT_VOLUME_NAME> <PLUGIN_NAME> <PLUGIN_COMMAND> <INPUT_DIRECTORY> <OUTPUT_DIRECTORY>
```
## Flags
### Docker Flags
#### [`--rm`](https://docs.docker.com/engine/reference/commandline/rm/) 
Used to delete the container (not image) after it has executed, and helps save space when you are running a container which is being used to execute a simple task. 
#### [`-it`](https://docs.docker.com/engine/reference/commandline/run/#:~:text=The%20%2Dit%20instructs%20Docker%20to,bash%20shell%20in%20the%20container.)  
Starts the container in interactive mode, which gives you access to the /bin/bash directory inside a container. This is helpful when you want to execute commands within the container.
#### [`--volume`](https://docs.docker.com/storage/volumes/) 
Specifies which volume you are mounting, and the path where the direcotry is mounted inside the container.
### General Flags
#### [`-c`](https://linux.die.net/man/1/bash) 
Allows you to pass sh commands as a string.

#### [`-v`](https://linux.die.net/man/1/bash)
Equivalent to -verbose
### Python Flags
#### [`-m`](https://peps.python.org/pep-0338/)
Helpful for exectuting modules for which you don't know the filename, check [here](https://stackoverflow.com/questions/7610001/what-is-the-purpose-of-the-m-switch) for additional information