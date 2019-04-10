# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 12:36:19 2018

@author: geos
"""

import yaml
import os
import requests

class ConfiguationLoader( object ):
    """
    Class of the configuration manager
    """

    def __init__( self , path , ip , port ):
        """
        Constructor of the class
        """
        self.path = path
        self.ip = ip
        self.port = port
        self.loadedInput = None

    def loadConfigurationFile( self ):
        with open( path , 'r' ) as stream:
            try:
                self.loadedInput = yaml.load( stream )
                #print( self.loadedInput )
            except yaml.YAMLError as exc:
                print( "Error when loading file" )
                print( exc )

    def sendToEndpoint( self ):
        '''
        Function to sent to endpoint
        '''
        url = u"http://" + self.ip + u":" + self.port + u"/cso/testConnection"
        r = requests.get( url )
        if r.status_code != 200:
            print( "error" )
        else:
            data = r.json()
            print( data[ "description" ] )
        url = u"http://" + self.ip + u":" + self.port + u"/cso/uploadYAML"
        r = requests.post( url , json = self.loadedInput )
        
        if r.status_code != 200:
            print( "error" )
        if r.status_code == 200:
            data = r.json()
            print( data[ "description" ] + " with id " + str( data[ "id" ] ) )
        
        print( u"Send to endpoint: " + url )

if __name__ == "__main__":
    """
    Test code only executed when module is not imported
    Test for simple to service use case
    """
    cwd = os.getcwd()
    path = os.path.join( cwd ,
                         "configTestSetupRuleBaseControl.yml" )
    ip = "127.0.0.1"
    port = "3030"
    
    cl = ConfiguationLoader( path , ip , port )
    cl.loadConfigurationFile()
    print( "OK, File Loaded" )
    cl.sendToEndpoint()
    print( "OK, File Loaded" )