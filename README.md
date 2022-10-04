# Bringing ChRIS (Storage and Compute) Fully to OpenShift and Kubernetes

## 1. Vision and Goals of the Project
ChRIS is an open source distributed data and computation platform, which aims to dramatically reduce the barrier to cloud and distributed computing for researchers, developers, and physicians. By providing easy access to these resources, users without years of technical experience in software development and deployment can reap the benefits of access to these systems, without the need to build their own computing infrastructure or understand complicated technical setup instructions.

For our project specifically, the objectives are as follows:

* Learn about containerization, with a particular focus on working within the docker/kubernetes/OpenShift development environment.
* Bring the ChRIS Ultron Back End (CUBE) and its storage container fully to the cloud. Currently this needs to be run on a local machine. 
* Update the ChRIS system’s process controller (pfcon) and process manager (pman) from OpenShift 3 to be compatible with OpenShift 4.

** **
## 2. Users/Personas of the Project
The users of the ChRIS system are researchers and physicians from hospitals, and ChRIS provides them with the means to abstract the computational resources needed to perform various tasks on medical data.

User characteristics: The users are assumed to have little to no technical knowledge, but have a need to easily and quickly transform medical data in a way that is abstracted away from any underlying hardware. They upload medical data (i.e. X-Rays, clinical data, etc) from their local environment to ChRIS through a REST API and select appropriate analysis functions.

** **
## 3. Scope and Features Of The Project
All of the components of ChRIS need to be able to run on the MOC cloud ecosystem. 
Those components include:

* pman
* pfcon
* CUBE
* Swift storage 

All tasks which directly contribute to that transition are within the scope of our project. For example, pman and pfcon are currently working on OpenShift 3; getting them compatible with OpenShift 4 is within scope. However, updating or changing the functionalities of pman or pfcon  would be out of scope. 

** **
## 4. Solution Concept
### Global Architecture

![ChRIS Architechture](https://www.bu.edu/rhcollab/files/2019/10/ChRIS-architecture.png)
ChRIS consists of several mostly independent parts, all of which already exist as Docker containers. For the purposes of this project, the primary components of ChRIS are the ChRIS Ultron backend, the backend’s associated Swift object storage container, the process controller, and the process manager. Additionally, ChRIS consists of many separate containerized applications managed by Docker, each of which can be used to process users’ input data in different ways.

The ChRIS Ultron backend, called CUBE, is represented in the above architectural diagram by the ChRIS logo at the main web entry. CUBE handles all incoming user requests, data storage and manipulation, and logic pertaining to sending and receiving necessary information to and from the other components of the system. When a user wants to run a containerized ChRIS app on a dataset that has been provided to the CUBE, CUBE pulls the data out of its Swift storage container, packages the data into a zip file, and sends the file to the process controller via https. The process controller, hosted in the Mass Open Cloud (MOC), receives the zipped file, unpacks the data into a file system, and sets up the environment for the requested ChRIS application. The process controller then functions to facilitate communication between the CUBE and the process manager. The CUBE will tell the process manager, via the controller, that the data is ready for processing and the program manager will begin running the ChRIS application on the data. The application pulls the data from the controller-specified file system and publishes its output to an output directory within the MOC. As the application runs, CUBE periodically pings the process manager via the process controller to check job status until the program has finished, after which the process controller returns the zipped output files back to the CUBE via https.

The CUBE, as well as its associated Swift container, are not currently cloud-based/supported by Kubernetes or OpenShift. However, the process controller and process manager are currently deployed on the Mass Open Cloud via OpenShift v3. Our solution entails moving the CUBE and its Swift storage onto the MOC alongside the process controller and process manager. In doing so, the portion of the architectural diagram above represented by the purple cloud would all move into the blue MOC cloud, allowing for the entirety of ChRIS to function within the cloud.

### Design Implications and Discussion
One of the advantages of a highly segmented project structure is that it lends itself towards easier testing. If ChRIS was built as a monolithic application, we would need to port all of its components in a single pass. As is, each modular component of the system can be moved into the cloud (or updated to be compatible with OpenShift 4 in the case of pman and pfcon) without concern that these moves will impact the functionality of ChRIS as a whole.

In addition, by moving all components of ChRIS to the cloud, we minimize the learning curve for new users seeking to use the ChRIS platform, as they would no longer need to perform any local environment setup in order to use the application. These design choices will increase the size of the target audience capable of using ChRIS while also simplifying the process for current users.

** **
## 5. Acceptance Criteria
The acceptance criteria for this project would be to successfully run a ChRIS plugin with all components of ChRIS running on the MOC. This achievement would constitute a successful project. 

Our stretch goals include:
1. Currently, when a user wants to run a given ChRIS program on their input data, the process controller receives the zipped data from CUBE and unpacks it into an input directory in some local file system associated with the cloud. The different ChRIS programs, however, are located in a different file system. So, when the program manager needs to run a program, the file system containing the input data is mounted as a network drive into the file system that houses the ChRIS programs. This mounting strategy for co-locating the input data and the programs is not supported by Kubernetes (but may be supported by OpenShift). One stretch goal is to implement an alternative strategy here that would work with Kubernetes.
2. Replacing all Swift storage with AWS S3 storage if possible.

** **
## 6a. Release Planning
All team members' work will take place on a fork of the existing ChRIS repositories, resembling the equivalent of a development branch in industry. For work on a given task/feature, team members will create a new branch and perform all code changes for that feature within that branch. Once the work for the task/feature has been completed, a pull request will be submitted for approval by the project lead. After code review and approval, the project lead will pull the code into the main branch of the forked repository. Ideally, all features completed within a sprint will be reviewed and merged into the main branch by the end of each sprint.

## 6b. Initial Timeline 
Every member of the group has little to no experience working with containers or containerized application management. For this reason, the initial stages of our project will focus on team research related to:

* Containerization 
* Storage systems solutions (object storage, file storage, block storage)
    * Amazon S3 and Openstack swift
* OpenShift and Kubernetes implementations

Our initial timeline is roughly as follows:
Deploy a simple application (non-ChRIS related) on the MOC
Get a ChRIS plugin running on the MOC, independent of any other ChRIS components
Run the same ChRIS app on the MOC using pman to manage the process
Be able to execute the process from step 3 with pfcon as the controller 
Have steps 2-4 run without user involvement, with all interactions controlled through ChRIS 

As the semester progresses, we will be able to more effectively gauge the time and work requirements associated with the above steps, and the timeline will be updated/adjusted to include more detailed sprint planning information. 

