# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 11:27:51 2018

.. module:: CoSimulationManager
    :synopsis: Something about CSM

.. moduleauthor: geos

/******************************************************************************
* Copyright 2019 Fraunhofer Institute for Building Physics IBP. All Rights Reserved.
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*    http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or  implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*****************************************************************************/

"""

import requests # version 2.18.4
import time

class CoSimulationManager( object ):
    """
    Class of the data base manager
    Introduced nomenclature in current values
    For inputs:
    serviceid_inputs_inputid
    For outputs:
    serviceid_outputs_outputid

    """

    def __init__( self , groupID , runID , startTime , endTime , stepSize , services , mappings ):
        """
        Constructor of the class

        """
        self.currentTime    = 0.0
        self.currentValues  = { }
        self.allValues      = { }
        self.groupID        = groupID
        self.runID          = runID
        self.startTime      = startTime
        self.endTime        = endTime
        self.stepSize       = stepSize
        self.services       = services
        self.mappings       = mappings
        
        
    def __str__( self ):
        """
        Magic string function of class 

        """
        print( "This csm has the following properties: startTime\n endTime\n stepSize\n servicesGroup\n mappingGroup\n" )
        return print( "{}\n, {}\n, {}\n, {}\n, {}\n".format( self.startTime ,
                                                             self.endTime , 
                                                             self.stepSize , 
                                                             self.services , 
                                                             self.mappings ) )

    def initialiseServices( self ):
        """
        (1): Set current time to startTime and initial values to be logged
        
        (2):            
        Function which sends an init request for all services included in this 
        co-simulation run.
        Provides the services with:
            - target -> item, e.g. AMSNetID of Beckhoff PLC or path to FMU
            - startTime -> Time where simulation starts, usually 0
            - endTime -> Time where simulation is supposed to stop
            - stepSize -> Simulation step size, i.e. time in between which 
                          co-simulation entities needs to sync
        
        (3):
        Writes initial values to inputs and outputs of services as obtained 
        from data base. # ??? TODO Does not happen
        
        """
        # (1) Set current time and currentValues to be logged
        self.currentTime = self.startTime
        self.currentValues[ "timestamp" ] =  self.currentTime
        self.allValues[ "timestamp" ] =  [ ]
        self.allValues[ "timestamp" ].append( self.currentTime )
                
        for service in self.services:
            url = "http://" + service[ "ip" ] + ":" + service[ "port" ] + "/Service/testConnection"
            
            r = requests.get( url )
            print(url, " - ", r.status_code )


        # (2)
        # Initialise the services
        for service in self.services:
            url = "http://" + service[ "ip" ] + ":" + service[ "port" ] + "/Service/initialize"
            pl = { "target"    : str( service[ "target" ] ) ,
                   "startTime" : int( self.startTime ) ,
                   "endTime"   : int( self.endTime ) ,
                   "stepSize"  : float( self.stepSize )
                 }
            
            r = requests.post( url , json = pl )

            if r.status_code == 200:
                # Initialise all inputs and outputs in current values
                for aInput in service[ "inputs" ]:
                    self.currentValues[ str( service[ "id" ] ) + "_inputs_" + str( aInput[ "id" ] ) ] = aInput[ "initialValue" ]
                    self.allValues[ str( service[ "id" ] ) + "_inputs_" + str( aInput[ "id" ] ) ] = [ ]
                    self.allValues[ str( service[ "id" ] ) + "_inputs_" + str( aInput[ "id" ] ) ].append( aInput[ "initialValue" ] )
                for aOutput in service[ "outputs" ]:
                    self.currentValues[ str( service[ "id" ] ) + "_outputs_" + str( aOutput[ "id" ] ) ] = aOutput[ "initialValue" ]
                    self.allValues[ str( service[ "id" ] ) + "_outputs_" + str( aOutput[ "id" ] ) ] = [ ]
                    self.allValues[ str( service[ "id" ] ) + "_outputs_" + str( aOutput[ "id" ] ) ].append( aOutput[ "initialValue" ] )
                print( "/initialize works - Status code is 200" )
            else:
                print( "/initialize - Status code is not 200." )
                return 1
        return 0
    
    def setInputsOfServices( self ):
        """
        Function which writes for all services and all inputs the last value to a 
        respective input of a service.
        Provides the service resource with:
            - id -> id of input variable in namespace of service
            - value -> value to which the input should be set

        """
        print( "debugging services: " , self.services )
        for service in self.services:
            url = "http://" + service[ "ip" ] + ":" + service[ "port" ] + "/Service/write"
            lInputs = service[ "inputs" ]
            for aInput in lInputs:
                
                pl = { "id"    : aInput[ "name" ] ,
                    "value" : self.allValues[ str( service[ "id" ] ) + "_inputs_" + str( aInput[ "id" ] ) ][ -1 ]
                    }
                
                r = requests.put( url , json = pl )

                if r.status_code == 200:
                    print( r.url )
                    print( "set inputs of services works - Status code is 200" )
                else:
                    print( "/write - Status code is not 200." )
                    return 1
        return 0
    
    def getOutputsOfServices( self ):
        """
        Function which reads for all services and all outputs the current value
        Provides the service resource with:
            - id -> id of output variable in namespace of service
        Services provide in response the current values in a json structure

        """
        self.currentValues[ "timestamp" ] = self.currentTime
        self.allValues[ "timestamp" ].append( self.currentTime )
        
        for service in self.services:
            url = "http://" + service[ "ip" ] + ":" + service[ "port" ] + "/Service/read"
            lOutputs = service[ "outputs" ]
            for aOutput in lOutputs:
                
                pl = { "id" : aOutput[ "name" ] }
                
                r = requests.get( url , params = pl )

                if r.status_code == 200:
                    print( r.url )
                    # Update outputs with new value
                    value = r.json()[ "value" ]
                    self.currentValues[ str( service[ "id" ] ) + "_outputs_" + str( aOutput[ "id" ] ) ] = value
                    self.allValues[ str( service[ "id" ] ) + "_outputs_" + str( aOutput[ "id" ] ) ].append( value )
                    # Update inputs mapped to the output
                    for aMap in self.mappings:
                        if aMap[ "soid" ] == service[ "id" ] and aMap[ "oid" ] == aOutput[ "id" ]:
                            self.allValues[ str( aMap[ "siid" ] ) + "_inputs_" + str( aMap[ "iid" ] ) ].append( value )
                else:
                    print( "/read - Status code is not 200." )
                    return 1
        return 0
    
    def shutDownServices( self ):
        """
        Function which shut downs a service.
        """
        for service in self.services:
            url = "http://" + service[ "ip" ] + ":" + service[ "port" ] + "/Service" + "/shutdown"
            r = requests.delete( url )

            if r.status_code == 200:
                print( r.url )
            else:
                print( "/shutdown - Status code is not 200." )
                return 1
        return 0
    
    def getResults( self ):
        """
        Function to return results
        
        """
        return self.allValues

    def runCoSimulation( self ):
        """
        This function performs the actual co-simulation task
        (1) Initialise the services and write initial values
        while loop
        (2) write current value to inputs of services
        (3) wait and increase time step
        (4) read and update current values of inputs from retrieved outputs
        
        """
        
        # (1)
        self.initialiseServices()
        
        while self.currentTime < self.endTime:            
            # (2) write current values
            self.setInputsOfServices()
          
            # (3) increase and wait
            self.currentTime = self.currentTime + self.stepSize
            time.sleep( self.stepSize )
                        
            # (4) read and update
            self.getOutputsOfServices()       
            print( "DEBUG | Current values is: " , self.currentValues )
        

        print(self.allValues)   
        # end
        self.shutDownServices()    
        
        return 0















