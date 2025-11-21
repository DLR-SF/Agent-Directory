from flask import render_template, request, jsonify, Response
from app import app
import json
from app.platformHandler import platformHandler
from dpam.model.platformQuery import platformQuery
from dpam.model.tokenRequest import tokenRequest
from app.configurationHandler import configurationHandler


@app.route('/')
@app.route('/index')
@app.route('/AssetAdministrationShell')
def index():
    '''
    Landing page to show all available agent AAS
    '''
    # get all agents
    agent_aas = get_aas_model_data_by_parent_id("AssetAdministrationShell", None)
    error = None
    if isinstance(agent_aas, tuple):
        # error during request to broker 
        error = str(agent_aas)
        agent_aas = []

    # render template
    model_title = "Asset Administration Shell"
    model_type = "AssetAdministrationShell"
    tile_nav = "Submodel"
    icon = "/static/images/aas-icon.png"
    parent = "Multi-Agent System"

    return render_template('index.html', agents=agent_aas, model_title=model_title, model_type=model_type, tile_nav=tile_nav, icon=icon, parent=parent, error=error)

@app.route('/Submodel/<aas_id>')
def submodels(aas_id):
    '''
    Landing page to show all available submodels
    '''
    # get all submodels to aas
    submodels = get_aas_model_data_by_parent_id("Submodel", aas_id)
    error = None
    if isinstance(submodels, tuple):
        # error during request to broker 
        error = str(submodels)
        submodels = []

    # render template
    model = "Submodel"
    tile_nav = "SubmodelElement"
    icon = "/static/images/submodel-icon.png"
    return render_template('index.html', agents=submodels, model_title=model, model_type=model, tile_nav=tile_nav, icon=icon, parent=aas_id, error=error)


@app.route('/SubmodelElement/<submodel_id>')
def submodelelements(submodel_id):
    '''
    Landing page to show all available submodel elements
    '''
    # get all submodel element
    submodelelements = get_aas_model_data_by_parent_id("SubmodelElement", submodel_id)

    error = None
    if isinstance(submodelelements, tuple):
        # error during request to broker 
        error = str(submodelelements)
        submodelelements = []
    
    # render template
    model_title = "Submodel Element"
    model_type = "SubmodelElement"
    tile_nav = "SubmodelElement"
    icon = "/static/images/submodel-element-icon.png"
        
    return render_template('index.html', agents=submodelelements, model_title=model_title, model_type=model_type, tile_nav=tile_nav, icon=icon, parent=submodel_id, error=error)

@app.route('/SubmodelElement/<submodel_id>/<submodelelement_id>')
def related_submodelelements(submodel_id, submodelelement_id):
    '''
    Landing page to show all related elements to a submodel element
    '''
    # get all related submodel element ids
    related_element_id = []
    relationships = get_aas_model_data_by_parent_id("SubmodelElementRelationship", submodelelement_id)
    error = None
    if isinstance(relationships, tuple):
        # error during request to broker 
        error = str(relationships)
        related_elements = []
    else:
        # get ids by looping through relationships
        for relationship in relationships:
            if relationship["first"]["value"] == submodelelement_id:
                related_element_id.append(relationship["second"]["value"])
            elif relationship["second"]["value"] == submodelelement_id:
                related_element_id.append(relationship["first"]["value"])

        # get all related submodel elements
        related_elements = get_submodelelements_to_id_list(related_element_id)
        if isinstance(related_elements, tuple):
            # return error
            return related_elements

    # render template
    model_title = "Submodel Element Relationship"
    model_type = "SubmodelElementRelationship"
    tile_nav = "SubmodelElement"
    url = tile_nav + "/" + submodel_id
    icon = "/static/images/submodel-element-icon.png"

    return render_template('index.html', agents=related_elements, model_title=model_title, model_type=model_type, tile_nav=url, icon=icon, parent=submodelelement_id, error=error)


@app.route('/about')
def about():
    '''
    Landing page for a brief introduction to the agent directory
    '''
    about_text = '''
    The Agent Directory Service is a webapp which allows to manage, monitor, and control agents in a multi-agent system (MAS) environment based on a digital twin.
    In the digital twin all agents in the MAS are represented virtually and a digital twin infrastructure is responsible to manage and provide access to digital twin data. 
    The Agent Directory Service integrates into this scenario by providing an interface to explore the digital representation of the agents from a digital twin infrastructure 
    and functionalities to invoke their capabilities and monitor skill execution.
    '''
    
    return render_template('about.html', title="About", text=about_text)





def read_file_data(filename):
    '''
    read data from aas model file and return 
    as JSON 
    '''
    # Opening JSON file
    path = './app/static/aas-model/{}'.format(filename)
    f = open(path)

    # returns JSON object as
    # a dictionary
    data = json.load(f)

    # Closing file
    f.close()

    # return data
    return data    

def filter_by_parent_id(model, parent_id):
    '''
    filter model file by parent id
    '''
    # filtered model result
    filtered_model = []

    # loop through entities
    for element in model:
        # if there is a parent_id present (not in case of AAS)
        if parent_id:
            # filter by parent id
            for key in parent_id:
                # check if key field i of parent_id is included in model
                if key in element: 
                    # check if field parent_id value is the same than element value
                    if element[key]["value"] == parent_id[key]:
                        # include model
                        filtered_model.append(element)
        # do not filter by parent id and provide whole model file
        else:
            filtered_model.append(element)

    return filtered_model

def get_aas_model_file(model_type, parent_id):   
    '''
    Read model from json file
    ''' 
    # get model file depending on type
    if model_type == "AssetAdministrationShell":
        filename = "AAS.json"
    elif model_type == "Submodel":
        filename = "Submodels.json" 
        parent_id = {"refI4AASId": parent_id}
    elif model_type == "SubmodelElement":
        parent_id = {"refI4SubmodelId": parent_id}
        if "Skills" in parent_id["refI4SubmodelId"]:
            filename = "SubmodelElements_Skills.json"
        else:
            filename = "SubmodelElements_Capability.json"
    elif model_type == "SubmodelElementRelationship":
        filename = "Relationships.json"
        # collect all relationships -> they are filtered by relationship first / second by caller
        parent_id = None
    else:
        print("Not supported File Type")
        return None

    model = read_file_data(filename)

    filtered_model = filter_by_parent_id(model, parent_id)

    return filtered_model
    

def get_aas_model_from_broker(model_type, parent_id):
    '''
    Get all entities of given model type and parent element
    from broker
    '''
    ph = platformHandler()

    # create attributes to filter for type and parent element
    if model_type == "AssetAdministrationShell":
        # all aas models
        attrs = {"type":"I4AAS"}
    elif model_type == "Submodel":
        # all submodels of specific aas
        attrs = {"type":"I4Submodel", "q": "refI4AASId==\"{}\"".format(parent_id)}
    elif model_type == "SubmodelElement":
        # all submodel elements of specific submodel
        attrs = {"q": "refI4SubmodelId==\"{}\"".format(parent_id)}    
    elif model_type == "SubmodelElementRelationship":
        # all relationship elemeents
        attrs = {"type":"I4SubmodelElementRelationship"}
    else:
        print("Not implemented")
        attrs = {"type":"None"}

    # read all entites
    result = ph.read_entities_by_type(options="normalized",attrs=attrs)
    if isinstance(result, tuple) and result[1] == 200:
        # return json if success
        result_json = json.loads(result[0])
        return result_json
    else:
        # otherwise return error tuple
        return result


def get_aas_model_data_by_parent_id(model_type, parent_id):
    '''
    Check backend mode and get model data
    by file-based or context broker backend optionally
    using parent id
    '''
    # check configuration
    ch = configurationHandler()
    backend_mode = ch.return_element_value("app", "backend_mode")
    
    # file-based backend
    if backend_mode == "file-based":
        result = get_aas_model_file(model_type, parent_id)
        return result
    # broker-based backend
    elif backend_mode == "broker":
        return get_aas_model_from_broker(model_type, parent_id)
    else:
        print("Backend mode not supported")


def get_element_by_id_file(file, id):
    '''
    get an element from a file by id
    '''
    # check all elements in file
    all_elements = read_file_data(file)
    for element in all_elements:
        if element["id"] == id:
            return element
    # not found
    return None


def get_submodelelements_to_id_list(id_list):
    '''
    Get all subelements to a list of ids
    either from file or broker
    '''
    # check configuration
    ch = configurationHandler()
    backend_mode = ch.return_element_value("app", "backend_mode")
    
    # file-based backend
    if backend_mode == "file-based":
        return get_submodelelements_to_id_list_file(id_list)
    # broker-based backend
    elif backend_mode == "broker":
        return get_submodelelements_to_id_list_broker(id_list)
    else:
        print("Backend mode not supported")    

def get_submodelelements_to_id_list_broker(id_list):
    '''
    Get a list of entities by id from broker
    '''
    ph = platformHandler()
    subelements = []
    for id in id_list:
        result = ph.read_entity(id, "normalized", [])
        if isinstance(result, tuple) and result[1] == 200:
            subelements.append(json.loads(result[0]))
        else:
            # return error
            return result

    # read all entites
    return subelements

def get_submodelelements_to_id_list_file(id_list):
    '''
    loop through a list of element ids and get all
    elements from a given list of submodel element files
    '''
    elements = []
    files = ["SubmodelElements_Capability.json", "SubmodelElements_Skills.json"]
    for file in files:
        for element_id in id_list:
            element = get_element_by_id_file(file, element_id)
            if element is not None:
                elements.append(element)
    
    return elements

