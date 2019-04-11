# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 15:39:51 2018

@author: viho + geos

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

from aiohttp import web #version 3.3.2
import fmpy as fm #version 0.2.5
from fmpy.fmi2 import FMU2Slave
import json

###   ###   ###   ###   ###   ###   ###   
# Define global variables
FMU = None
FACTORY =  { "pathToFMU" : None ,
             "model_description" : None ,
             "unzipdir" : None ,
             "vrs" : None ,
             "inputVars" : { } ,
             "inputVarsTemp" : { } ,
            }

FMU     = None
TIME    = None
RESULTS = None

# http://127.0.0.1:8081/Service/testConnection
async def testConnection( request ):
    return web.json_response( { "description" : "Instance is running." } , status = 200 )

# http://127.0.0.1:8081/Service/initialize
async def initialize( request ):
    global FACTORY
    global FMU
    global TIME
    global RESULTS
    
    if request.body_exists:
        
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        # ???
        FACTORY[ "pathToFMU" ] = data[ "target" ]
        FACTORY[ "modelDescription" ] = fm.read_model_description( FACTORY[ "pathToFMU" ] )
        FACTORY[ "unzipdir" ] = fm.extract( FACTORY[ "pathToFMU" ] )
        
        # Get variable references and input variables
        FACTORY[ "vrs"] = {} 
        for variable in FACTORY[ "modelDescription" ].modelVariables:
            FACTORY[ "vrs" ][ variable.name ] = variable.valueReference
            if variable.causality == "input":
                FACTORY[ "inputVars" ][ variable.name ] = None
    
        FMU = FMU2Slave( guid            = FACTORY[ "modelDescription" ].guid ,
                         unzipDirectory  = FACTORY[ "unzipdir" ] ,
                         modelIdentifier = FACTORY[ "modelDescription" ].coSimulation.modelIdentifier ,
                         instanceName    = "instance1" )
    
        ###   ###   ###   ###   ###   ###   
        # Init FMU
        FACTORY[ "startTime" ] = data[ "startTime" ]
        FACTORY[ "endTime" ] = data[ "endTime" ]
        FACTORY[ "stepSize" ] = data[ "stepSize" ]
        TIME = FACTORY[ "startTime" ]
        RESULTS = [] # list to record the results
    
        FMU.instantiate()
        FMU.setupExperiment( startTime = FACTORY[ "startTime" ] )
        FMU.enterInitializationMode()
        FMU.exitInitializationMode()
        
        return web.json_response( { "description" : "Service initialized." } , status = 200 )
    
    return web.json_response( { "description" : "Wrong init information" } , status = 500 )

# http://127.0.0.1:8081/Service/write
async def write( request ):
    """
    Route to write a single real value of an input of the FMU
    """
    global FACTORY
    global TIME
    global FMU
    
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        
        name = data[ "id" ]
        value = float( data[ "value" ] )
        
        if value != None and name != None:
            # Write to FMU and add to written input in this time frame
            # Only real numbers can be written, only inputs can be written
            FMU.setReal( [ FACTORY[ "vrs" ][ name ] ] , [ value ] )
            
            FACTORY[ "inputVarsTemp" ][ name ] = None

            # If all inputs have been written in this time step, doStep()
            if len( FACTORY[ "inputVarsTemp" ].keys() ) == len( FACTORY[ "inputVars" ].keys() ):
                FMU.doStep( currentCommunicationPoint = TIME , 
                            communicationStepSize     = FACTORY[ "stepSize" ] )
                TIME += FACTORY[ "stepSize" ]
                
                #Reset temporary storage of input vars
                FACTORY[ "inputVarsTemp" ] = { }
            
            return web.json_response( { "id" : name , "value" : value , "description" : "Writing successful" } , status = 200 )
        
        else:
            return web.json_response( { "description" : "Did not receive valid address" } , status = 400 )

# http://127.0.0.1:8081/Service/read?id=outputs[4]
async def read( request ):
    """
    Function to read the current value of any variable of an FMU
    """
    global FMU
    
    name = request.rel_url.query[ "id" ]
    
    if name != None:
        value = FMU.getReal( [ FACTORY[ "vrs" ][ name ] ] )
        return web.json_response( { "id" : name , "value" : value[ 0 ] , "description" : "Reading successful" } , status = 200 )
    else: 
        return web.json_response( { "description" : "Did not receive valid variable name" } , status = 400 )
    
# http://127.0.0.1:8081/Service/shutdown

async def shutdown( request ):
    """
    Terminate FMU execution and cleanup
    """
    global FMU
    global FACTORY
    
    FMU.terminate()
    FMU.freeInstance()
    
    return web.json_response( { "description" : "Succesful shutdown" } , status = 200 )


###   ###   ###   ###   
# Bind paths and launch app
if __name__ == "__main__":
    appFMU = web.Application( )
    appFMU.add_routes( [ web.get( "/Service/testConnection" , testConnection ) ,
			             web.post( "/Service/initialize" , initialize ) ,
                         web.put( "/Service/write" , write ) ,
                         web.get( "/Service/read" , read ) ,
    			         web.delete( "/Service/shutdown" , shutdown ) ] )

    web.run_app( appFMU , port = 8081 )
    
