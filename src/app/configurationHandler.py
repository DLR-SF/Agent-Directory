import yaml
import logging

class configurationHandler:
    '''
    Configuration Handling
    '''    

    logger = logging.getLogger(__name__)
    config_path = "app/config/config.yaml"

    def __init__(self):
        '''
        Initialize configuration
        '''
        # parse configuration
        self.data = []
        self.read_config()

    def read_config(self):
        '''
        Read configuration and parse it into dictionary
        :return:
        '''
        try:
            with open(self.config_path, "r") as stream:
                self.data = yaml.safe_load(stream)
        except FileNotFoundError as ex:       
            error_message= "Can not open configuration file. Reason: {}. Please provide a config.yaml file according to documentation.".format(ex)
            self.logger.error(error_message)
            raise Exception(error_message)


    def return_element_value(self, section, element):
        '''
        return configuration value based on configuration
        section and element
        :param section:
        :param element:
        :return:
        '''
        try:
            return self.data[section][element]
        except KeyError as ex:
            # create error message object 
            error_message= "Can not find configuration value '{}' in section '{}'. Error text: {}".format(element, section, ex)
            self.logger.error(error_message)
            raise Exception(error_message)