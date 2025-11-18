from dpam.controller.platformController import platformController
from dpam.model.platformQuery import platformQuery
from dpam.model.tokenRequest import tokenRequest
import json
from app.configurationHandler import configurationHandler
import datetime


class platformHandler:
    '''
    Helper class to handle json operations
    '''
    def __init__(self):
        # initialize platform controller
        self.platform_controller = platformController()
        self.config_handler = configurationHandler()

        # static variables
        self.broker_url = self.config_handler.return_element_value("broker", "url")
        self.context = self.config_handler.return_element_value("broker", "context_url")
        self.fiware_service = self.config_handler.return_element_value("broker", "fiware_service")
        self.fiware_service_path = self.config_handler.return_element_value("broker", "fiware_service_path")

        # token
        self.token_enabled = self.config_handler.return_element_value("token", "enabled")       
        self.token = None
        self.token_age = None
        self.max_token_age_min = self.config_handler.return_element_value("token", "token_max_age")        


    def create_message_json(self, messages):
        '''
        Create list of message objects as json
        '''
        json_msg_list = []
        for message in messages:
            json_msg = json.loads(json.dumps(message.__dict__))
            json_msg_list.append(json_msg)
        return json_msg_list
        
    def check_age_token(self):
        '''
        Check if token is older than configured maximum token age
        '''
        valid = False
        if self.token_age != None:
            timespan = (datetime.datetime.now()-self.token_age).total_seconds() / 60
            if timespan < self.max_token_age_min:
                valid = True

        return valid

    def get_new_token(self):
        '''
        Get new token and set token age
        '''
        # read parameter from configuration
        url = self.config_handler.return_element_value("token", "url")        
        username = self.config_handler.return_element_value("token", "username")        
        password = self.config_handler.return_element_value("token", "password")        
        client_id = self.config_handler.return_element_value("token", "client_id")        
        client_secret = self.config_handler.return_element_value("token", "client_secret")        

        # create tokenRequest object
        tr = tokenRequest(url, username, password, client_id, client_secret)

        # get token
        token_result = self.platform_controller.get_token(tr)
        if token_result.messageType == "info":
            # successfully got token
            self.token = token_result.text
            self.token_age = datetime.datetime.now()
        else:
            # error during token request
            error_message = "Error: Can not get token. Reason: {}".format(token_result.text)
            return error_message

    def handle_token(self):
        '''
        Get or re-use token if token authentication is enabled'''
        
        if self.token_enabled == True:
            # get or re-use token
            if self.token == None or (self.token and not self.check_age_token()):
                # get new token if there is none or token is too old
                token_result = self.get_new_token()
                if token_result and token_result[1] != 200:
                    # if message instance return error
                    return token_result  
        else:
            return None

    def read_entity(self, entity_id, options, attrs):
        '''
        read single entity
        '''
        # create platformQuery object as input parameter
        pq = platformQuery(self.broker_url, self.fiware_service, self.fiware_service_path, self.context)
        pq.entity_id = entity_id
        pq.options = options
        pq.attributes = attrs

        # get or re-use token
        token_result = self.handle_token()

        # read entity from data platform
        if isinstance(token_result, tuple):
            # return token error
            return token_result
        else:
            # query data platform
            result = self.platform_controller.read_single_entity(self.token, pq)
            return result.text, result.code
        
    def read_entities_by_type(self, options, attrs):
        '''
        read single entity
        '''
        # create platformQuery object as input parameter
        pq = platformQuery(self.broker_url, self.fiware_service, self.fiware_service_path, self.context)
        pq.options = options
        pq.attributes = attrs

        # get or re-use token
        token_result = self.handle_token()

        # read entity from data platform
        if isinstance(token_result, tuple):
            # return token error
            return token_result
        else:
            # query data platform
            result = self.platform_controller.read_entities_by_type(self.token, pq)
            return result.text, result.code        
        
    def create_entity(self, body):
        '''
        Update single entity
        '''
        # create platformQuery object as input parameter
        pq = platformQuery(self.broker_url, self.fiware_service, self.fiware_service_path, self.context)
        pq.body = json.dumps(body)
        
        # get or re-use token
        token_result = self.handle_token()

        # create entity at data platform
        if isinstance(token_result, tuple):
            # return token error
            return token_result
        else:
            # create entity at data platform
            result = self.platform_controller.create_single_entity(self.token, pq)
            return result.text, result.code

    def update_entity(self, entity_id, body):
        '''
        Update single entity
        '''
        # create platformQuery object as input parameter
        pq = platformQuery(self.broker_url, self.fiware_service, self.fiware_service_path, self.context)
        pq.entity_id = entity_id
        pq.body = json.dumps(body)
        
        # get or re-use token
        token_result = self.handle_token()

        # update entity at data platform
        if isinstance(token_result, tuple):
            # return token error
            return token_result
        else:
            # update entity at data platform
            result = self.platform_controller.update_single_entity(self.token, pq)
            return result.text, result.code

    def delete_entity(self, entity_id):
        '''
        Delete single entity
        '''
        # create platformQuery object as input parameter
        pq = platformQuery(self.broker_url, self.fiware_service, self.fiware_service_path, self.context)
        pq.entity_id = entity_id
        
        # get or re-use token
        token_result = self.handle_token()

        # read entity from data platform
        if isinstance(token_result, tuple):
            # return token error
            return token_result
        else:
            # delete entity from data platform
            result = self.platform_controller.delete_single_entity(self.token, pq)
            return result.text, result.code


    def create_update_operation_state_body(self, execution_state, operation_result):
        '''
        Create JSON body from runtime information and context 
        information for update entity operation
        '''

        # concatinate runtime information and context in normalized form for update
        dict_body = {
            "executionState": {
                "type": "Property",
                "value": execution_state
            },
            "operationResult": {
                "type": "Property",
                "value":     {
                    "success": operation_result.success,
                    "isException": operation_result.isException,
                    "entity": operation_result.entity,
                    "entityType": operation_result.entityType,
                    "messages": self.create_message_json(operation_result.messages)
                }
            },
            "dateModified": {
                "type": "Property",
                "value": datetime.datetime.now().replace(
                            microsecond=0).isoformat() + ".00Z"
            },
            "@context": [self.context] 
        }

        # create json body
        #json_body = json.dumps(dict_body)

        return dict_body

