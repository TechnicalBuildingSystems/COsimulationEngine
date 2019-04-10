# -*- coding: utf-8 -*-
"""
Created on Mon Nov 26 12:36:19 2018

@author: geos
"""
import os
import requests
import time

class TesterREST2FMI( object ):
    """
    Class of the configuration manager
    """

    def __init__( self , ip , port ):
        """
        Constructor of the class
        """
        self.ip = ip
        self.port = port
        
    def test( self ):
        """
        Test connection to FMI endpoint
        """
        url = "http://" + self.ip + ":" + self.port + "/Service/testConnection"
                
        r = requests.get( url )
        if r.status_code != 200:
            print( "/Service/testConnection - ERROR!" )
        else:
            data = r.json()
            print( data[ "description" ] )

    def initialise( self , pl ):
        """
        Initialise FMI endpoint
        """
        url = "http://" + self.ip + ":" + self.port + "/Service/initialize"
                
        r = requests.post( url , json = pl )
        if r.status_code != 200:
            print( "/Service/initialise - ERROR!" )
        else:
            data = r.json()
            print( data[ "description" ] )

    def write( self , pl ):
        """
        Function to sent to endpoint
        """
        url = "http://" + self.ip + ":" + self.port + "/Service/write"

        

        r = requests.put( url , json = pl )
        if r.status_code != 200:
            print( "/Service/write - ERROR!" )
        else:
            data = r.json()
            print( data[ "description" ] )
            
    def read( self , name ):
        """
        Function to read to endpoint
        """
        url = "http://" + self.ip + ":" + self.port + "/Service/read"

        pl = { "id" : name }

        r = requests.get( url , params = pl )
        if r.status_code != 200:
            print( "/Service/read - ERROR!" )
        else:
            data = r.json()
            print( data[ "description" ] )

    def shutdown( self ):
        """
        Function to shutdown to endpoint
        """
        url = "http://" + self.ip + ":" + self.port + "/Service/shutdown"
    
        r = requests.delete( url )
        if r.status_code != 200:
            print( "/Service/shotdown - ERROR!" )
        else:
            data = r.json()
            print( data[ "description" ] )


if __name__ == "__main__":
    """
    Test code only executed when module is not imported
    Test for simple to service use case
    """
    ip = "127.0.0.1"
    port = "8081"
    
    t = TesterREST2FMI( ip , port )
    
    t.test()
    print( "Tested connection" )
    time.sleep( 1 )
    
    pl = { "target" : "/home/ibp/Documents/ControlledTemperature.fmu" ,
           "startTime" : 0 ,
           "endTime" : 10 ,
           "stepSize" : 1 }
    t.initialise( pl )
    print( "Initialised" )
    time.sleep( 1 )
    
    pl = { "id" : "u" ,
          "value" : 0 }
    t.write( pl )
    print( "write" )
    time.sleep( 1 )
    
    name = "TemperatureOut"
    t.read( name )
    print( "read" )
    time.sleep( 1 )
    
    t.shutdown()
    print( "shutdown" )
    time.sleep( 1 )
    
    print( "Done" )
