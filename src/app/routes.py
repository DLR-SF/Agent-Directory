from flask import render_template, request, jsonify, Response
from app import app
import requests
import json


def get_aas_model_file(filename):   
    '''
    Parse external configuration file
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


@app.route('/')
@app.route('/index')
@app.route('/AssetAdministrationShell')
def index():
    '''
    Landing page to show all available agent AAS
    '''
    # get all agents
    agents_aas = get_aas_model_file("AAS.json")

    # render template
    model_title = "Asset Administration Shell"
    model_type = "AssetAdministrationShell"
    tile_nav = "Submodel"
    icon = "/static/images/aas-icon.png"
    parent = "Multi-Agent System"
    return render_template('index.html', agents=agents_aas, model_title=model_title, model_type=model_type, tile_nav=tile_nav, icon=icon, parent=parent)

@app.route('/Submodel/<aas_id>')
def submodels(aas_id):
    '''
    Landing page to show all available submodels
    '''
    # get all submodels to aas
    submodels = get_aas_model_file("Submodels.json")

    # render template
    model = "Submodel"
    tile_nav = "SubmodelElement"
    icon = "/static/images/submodel-icon.png"
    return render_template('index.html', agents=submodels, model_title=model, model_type=model, tile_nav=tile_nav, icon=icon, parent=aas_id)


@app.route('/SubmodelElement/<submodel_id>')
def submodelelements(submodel_id):
    '''
    Landing page to show all available submodel elements
    '''
    # get all submodel element
    if "Skills" in submodel_id:
        submodelelements = get_aas_model_file("SubmodelElements_Skills.json")
    else:
        submodelelements = get_aas_model_file("SubmodelElements_Capability.json")

    # render template
    model_title = "Submodel Element"
    model_type = "SubmodelElement"
    tile_nav = "SubmodelElement"
    icon = "/static/images/submodel-element-icon.png"
    return render_template('index.html', agents=submodelelements, model_title=model_title, model_type=model_type, tile_nav=tile_nav, icon=icon, parent=submodel_id)


def get_element_by_id(file, id):
    '''
    get an element from a file by id
    '''
    # check all elements in file
    all_elements = get_aas_model_file(file)
    for element in all_elements:
        if element["id"] == id:
            return element
    # not found
    return None

def get_submodelelements_to_id_list(files, id_list):
    '''
    loop through a list of element ids and get all
    elements from a given list of submodel element files
    '''
    elements = []
    for file in files:
        for element_id in id_list:
            element = get_element_by_id(file, element_id)
            if element is not None:
                elements.append(element)
    
    return elements

@app.route('/SubmodelElement/<submodel_id>/<submodelelement_id>')
def related_submodelelements(submodel_id, submodelelement_id):
    '''
    Landing page to show all related elements to a submodel element
    '''
    # get all related submodel element ids
    related_element_id = []
    relationships = get_aas_model_file("Relationships.json")
    for relationship in relationships:
        if relationship["first"]["value"] == submodelelement_id:
            related_element_id.append(relationship["second"]["value"])
        elif relationship["second"]["value"] == submodelelement_id:
            related_element_id.append(relationship["first"]["value"])

    # get all related submodel elements
    related_elements = get_submodelelements_to_id_list(["SubmodelElements_Capability.json", "SubmodelElements_Skills.json"], related_element_id)

    # render template
    model_title = "Submodel Element Relationship"
    model_type = "SubmodelElementRelationship"
    tile_nav = "SubmodelElement"
    url = tile_nav + "/" + submodel_id
    icon = "/static/images/submodel-element-icon.png"
    return render_template('index.html', agents=related_elements, model_title=model_title, model_type=model_type, tile_nav=url, icon=icon, parent=submodelelement_id)



@app.route('/about')
def about():
    '''
    Landing page for a brief introduction to the agent directory
    '''
    about_text = " This is an Agent Directory Service to manage, monitor, and control agents in a MAS environment. All agents are represented by asset adminstration shell (AAS) model composed of a) AAS model b) submodels c) submodel elements d) submodel element relationships. Per default the app loads a MAS with dummy-agents which provide capabilities and skills to automate tasks at an industrial plant. Each capability is related to one or more skills that implement functionality to conduct the capability. Each capability can be executed with Agent Directory service optionally with input variables if required. If a capability is executed skills are invoked to conduct the requested task which can be monitored with the digital twin. "
    return render_template('about.html', title="About", text=about_text)


@app.route('/proxy/agent-capabilities/<idShort>', methods=['POST', 'OPTIONS'])
def proxy_agent_capability(idShort):
    """
    Proxy endpoint to forward capability calls to the backend service on localhost:3000.
    This lets the browser call our Flask app (same-origin) and avoids CORS issues.
    """
    # Handle preflight quickly; Flask-CORS is configured globally but respond to OPTIONS anyway
    if request.method == 'OPTIONS':
        return Response(status=200)

    target = f'http://localhost:3000/agent-capabilities/{idShort}'
    try:
        resp = requests.post(target, json=request.get_json(), timeout=10)
    except requests.RequestException as e:
        return jsonify({'error': str(e)}), 502

    # Forward response content and status code; set content-type from target if present
    content_type = resp.headers.get('Content-Type', 'application/json')
    return Response(resp.content, status=resp.status_code, content_type=content_type)
