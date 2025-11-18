# Agent Directory

This is a simple webapp that allows to explore agents in a multi-agent system (MAS) based on a digital twin. It relys on a NGSI-LD context server that provides a REST API to create, delete, update, and read the representation of the agents in the MAS.

See how to deploy, use, and configure the app to use it in a custom MAS system environment.

- [Agent Directory](#agent-directory)
  - [Environment](#environment)
  - [Build app](#build-app)
  - [Run app](#run-app)
    - [Standalone](#standalone)
    - [As a docker container](#as-a-docker-container)
  - [Test app](#test-app)
  - [Use app](#use-app)
    - [Data Model](#data-model)
    - [Navigation](#navigation)
  - [Configure app](#configure-app)
    - ['app' Section](#app-section)
    - ['broker' Section](#broker-section)
    - ['token' Section](#token-section)


## Environment

This app uses python and a set of libraries and has been tested with Python 3.10.4 on Windows 10 and Ubuntu 22.04.

Moreover it can be deployed standalone or containerized (see section 'Run app'). There is no need for additional dependencies other than the deployment solution and the installation of listed python dependencies in this environment (see [requirements.txt](/src/requirements.txt)).

## Build app

The app can be deployed in a container in case you don't want to deploy it standalone. Therefore you need to create an image using docker beforehand:
1. open a cmd and change to src location of the project 
2. to build an image execute: ```docker build . -t agent-directory:1.0```
   1. Remark: In newer releases it can also be ```docker buildx build . -t agent-directory:1.0```
3. check newly created image: ```docker images```
4. If you want to export it to a file execute: ```docker save -o ./releases/agent-directory-1.0.tar agent-directory:1.0```

## Run app

The app can be deployed using 2 different ways:
1. Standalone (see [Standalone](#standalone))
2. As a docker container (see [Docker](#as-a-docker-container))

### Standalone

First you have to create the virtual environment (only needed when you use deploy it on a system for the first time):
1. Create venv using ```python -m venv venv``` or alternatively skip the step to enter existing one
2. Enter venv using ```.\venv\Scripts\activate```
3. If not already installed install flask using ```pip install -r requirements.txt```

Afterwards you can run the app like that:
1. Enter venv using ```.\venv\Scripts\activate```
2. Go to src-directory: ```cd \src```
3. Run flask app: ```python -m flask run``` or simply ```flask run```
4. Afterwards the webserver should run and your should be able to access the webapp via browser (see [Test app](#test-app))
5. Press Strg+C to stop the app

### As a docker container

1. Build the image as explained above or import it using ```docker load -i <tar-file for image>.tar```
2. Execute a docker run command: ```docker run --name agent-directory -d -p 8000:5000 --rm agent-directory:1.0```
3. Check if container is running: ```docker ps -a```
4. If you want to stop the container run: ```docker stop <container-id>```

## Test app
1. Open URL in browser http://<domain>:<port>, for example, 
   1. Standalone: http://localhost:5000
   2. Docker: http://localhost:8000 (if run with 8000:5000 port parameter)
2. As a result you should be able to see all available agents and navigate through their asset administration shell (AAS) data representation to explore their data model and possibly invoke actions. 

Home (index):</br>
![Agent Directory Index Page](/src/app/static/images/index_page.png)

## Use app

### Data Model
As an example the app shows agents that are represented based on an asset administration shell (AAS) data model. Each agent is represented by an own AAS instance which is comprimised of an AAS Model, Submodels, Submodel Elements and Relationships. The Agent Directory web app allows to browser through the AAS representation hierarchically starting with AAS instances, their submodels, their submodel elements, and possibly relationships of the submodel elements.

In productive usage the app should be conected with a NGSI-LD context server as discussed in [Configuration Section](#configure-app). For testing purposed the local model of a MAS comprimised out of two dummy agents can be used. Therefore, configure test mode and explore the AAS representation of the dummy agent. The agent is represented by an AAS instance (DummyAgent), which is related to a bunch of submodels (Capabilities and Skills), which are related to submodel elements (Capabilities and Skill elements). The submodel elements can again be related to each other by an explicit realized by relationship.

Data Model of the dummy agent:</br>
![Agent Directory Index Page](/src/app/static/images/Dummy-Agent-Data-Model.png)

You can explore the model files of the dummy agent at [/src/app/static/aas-model/](/src/app/static/aas-model/).

### Navigation
The index page shows all AAS instances of a system:
![Agent Directory Index Page](/src/app/static/images/index_page.png)

Each AAS instances is illustrated in a tile and allows to see model details, navigate to subelement or execute actions by clicking one of the buttons.

Navigating to subelement the user can navigate through the AAS representation by starting with AAS model, followed by its submodels, followed by its submodel elements. 

While at AAS and submodel level are no context actions supported, the capabilities and skills submodel elements support context actions:
1) **Capabilities:** Provide input variables and execute a capability
   ![Execute Capability Pop-Up](/src/app/static/images/execute_capability.png)
2) **Skills:** Monitor current execution state of the skill which can be invoked by a capability
   ![Monitor Skill Pop-Up](/src/app/static/images/monitor_skill.png)

## Configure app

The app can be configured using a configuration file in [/src/app/config/](/src/app/config/) named config.yaml. Copy the file [config.example.yaml](/src/app/config/config.example.yaml) as a template for your custom environment configuration.

### 'app' Section
First, you can configure the app to connect it to different backends:
1) **Broker:** In broker mode the app reads the agent models from a NGSI-LD Context Broker backend
2) **Files:** In file-based mode the app reads the agent models from a files in folder [/src/app/static/aas-model/](/src/app/static/aas-model/). Here the files [AAS.json](/src/app/static/aas-model/AAS.json), [Submodels.json](/src/app/static/aas-model/Submodels.json), [SubmodelElements_Capability.json](/src/app/static/aas-model/SubmodelElements_Capability.json), [SubmodelElements_Skills.json](/src/app/static/aas-model/SubmodelElements_Skills.json), [Relationships.json](/src/app/static/aas-model/Relationships.json) include the AAS models for agent representation.

```
app:
    # backend mode (file-based, broker)
    backend_mode: "file-based"
    ...
``` 

For productive usage you have to configure a broker and possibly a token-based authentication. 

### 'broker' Section
Configure broker-related settings in the broker section of the configuration file:

```
broker:
    # url to platform broker
    url: "http://digital-twin-infrastructure/orion-ld"

    # tenant name for multi-agent-model
    fiware_service: "rest_mas"
    
    # tenant path for multi-agent-model
    fiware_service_path: "/agent"

    # url to context file
    context_url: "http://digital-twin-infrastructure/ld-context/datamodels.context-ngsild.jsonld"

```

If you have a backend of type 'broker' you will need to configure a url, service, service path and a context url to read and write data from the context broker successfully. 

### 'token' Section
Configure token-related settings in the token section of the configuration file:

```
token:
    # enable token authentication
    enable: true

    # url identity provider
    url: "http://digital-twin-infrastructure/identity-provider/protocol/openid-connect/token"
    # token maximum age in minutes
    token_max_age: 30

    # username to request token
    username: "user"
    # password for user to request token
    password: "changeme"
    # id of the identity provider client to login
    client_id: "client_id"
    # client secret of the identity provider client to login
    client_secret: "3edkjfjgiw.xngpw"

```

First, decide if you want to enable token-based authentication. If yes, configure a NGSI-LD context broker by providing a url, token_max_age, username, password, client_id and client_secret. 

