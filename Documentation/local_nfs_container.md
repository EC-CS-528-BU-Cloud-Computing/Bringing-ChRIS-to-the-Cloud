# Trying to Setup an NFS Server Locally
## Prerequisites
1. Have docker running
2. Have a terminal window open in your home folder

Also note, all of the steps below were executed on macos Monterey 
## Setting up the NFS Server
In order to test out the functionality of pfcon and pman on OpenShift, we need a workaround to allow both to interact with storage using NFS. Sincce our project space does not have access to this by default, one of the options was to try and deploy an NFS server inside a container running in the project space, mounting a persistent volume inside of this NFS server container, and then using the server as a shim to get pfcon/pman working. In order to test this out, I tried setting up an NFS server using [this](https://hub.docker.com/r/erichough/nfs-server/) image from the docker hub. 
To get it setup, first create a docker volume:
```
docker volume create nfs_test
```
then execute the following:
```
docker run                                            \
  -v nfs_test:/test  \
  -e NFS_EXPORT_0='/test                  *(rw,no_subtree_check,fsid=0)'  \
  --cap-add SYS_ADMIN --platform linux/amd64                                \
  -p 2049:2049                                       \
  --name nfs erichough/nfs-server
```
If not already downloaded, this downloads the latest version of the nfs-server image from docker hub, then mounts the volume that was just created at `/test` inside the container. The `NFS_EXPORT_0` value is an environent variable that specifies who can connect to the server (set here for any ip address by leading with "*"). The [fsid](https://unix.stackexchange.com/questions/427597/implications-of-using-nfsv4-fsid-0-and-exporting-the-nfs-root-to-entire-lan-or)=0 is needed to specify that the entire server can be [viewed as a single file system](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/5/html/deployment_guide/s1-nfs-server-config-exports). 
The container needs to be run in privileged mode, or with --cap-add SYS_ADMIN. the SYS_ADMIN approach is preffered as it [grants a smaller subset of capabilities to the container](https://serverfault.com/questions/824809/chrome-under-docker-cap-sys-admin-vs-privileged#:~:text=One%20difference%20is%20that%20%2D%2D,doesn't%20give%20you%20that.). 
`-p 2049:2049` is used for exposing container port(s). 
## Creating a Test File
In order to test that the nfs server is properly serving files, we need to add a dummy file to the nfs_test volume which we will be attempting to make accessible. I did this by creating a new container from an [ubuntu image](https://hub.docker.com/_/ubuntu) which mounts the same nfs_test volume from previous steps, then creating a test file inside that volume. To do so, run:
```
docker run --rm -v nfs_test:/test -it ubuntu:16.04 bash
```
followed by 
```
cd test
echo "Testing NFS, please work">>test.txt
exit #Closing the container
```
## Setting up an Ubuntu Container as the NFS Client
Now that we have setup our NFS server and have added in some data to the volume mounted to the shared path inside it, we can attempt to mount the shared directory inside a different container. To do this, we will create a new container using the same ubuntu image as before:

```
docker run --rm --privileged -it ubuntu:latest bash
```
The only difference between this and our setup in the previous step is that we are not mounting the nfs_test volume inside this container. 
Next, we can create a new directory (not neccessary), in which we will mount the shared directory from the NFS server container. 
```
mkdir /test_directory
```
In order to handle the mounting process, we also need to intall `nfs-common`:
```
apt-get update
apt-get install nfs-common
```
The final step is to get the ip address of the container which is running the NFS server. In a new terminal window run:
```
docker inspect -f '{{range.NetworkSettings.Networks}}{{.IPAddress}}{{end}}' <CONTAINER_NAME> # container name is nfs in this example
```
Finally, we can mount the shared directory from the NFS server inside the newly created `/test_directory`
```
mount <NFS_SERVER_CONTAINER_IP>:/ /test_directory
```
If everything has worked, you should now see the `test.txt` file created in the previous step inside `/test_directory` folder. 
```
cd test_directory
ls
```
## Final Testing to Ensure Data is Available (Optional)
In order to confirm that everything had been setup correctly, I wanted to do one final test. I created a third container using the latest [debian image](https://hub.docker.com/_/debian), mounting the same nfs_test volume we have been using. In a new terminal window, run:
```
docker run --rm -v nfs_test:/test -it debian:latest bash
```
Then I created a new file named `test2.txt` in the mounted volume. 
```
cd test
echo "Just making sure">>test2.txt
```
The final step is to go back to the ubuntu container (the NFS client) and checking to see whether the `/test_directory` folder now contains a new file called test2.txt. 
```
# Inside the ubuntu container
cd test_directory
ls 
```
