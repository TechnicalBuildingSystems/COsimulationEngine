# -*- coding: utf-8 -*-
"""
Created on Wed Jul 25 17:06:03 2018

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
import pyads #version 3.0.2
import json

###   ###   ###   ###   ###   ###   ###   
# Define global variables
PLC = None 

# http://127.0.0.1/Service/testConnection
async def testConnection( request ):
    return web.json_response( { "Status" : "OK" } , status=200)

# http://127.0.0.1:8080/Service/initialize
async def initializeADS( request ):
    global PLC
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        AMSNetID = data[ "target" ]
    
        if AMSNetID != None:
            PLC = pyads.Connection( AMSNetID , 851 )
            PLC.open()
            return web.json_response( { "target" : AMSNetID, "description" : "Service initialized" } , status = 200)
        else:
            return web.json_response( { "description" : "Wrong init information" } , status = 400 )
    
# http://127.0.0.1:8080/Service/write
async def writeADS( request ):
    global PLC
    
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        
        ID = data[ "id" ]
        value = float( data[ "value" ] )

        if value != None and ID != None:
            PLC.write_by_name( ID , value , pyads.PLCTYPE_LREAL )
            return web.json_response( { "id" : ID , "value" : value } , status = 200 )
        else:
            return web.json_response( { "description" : "Did not receive valid address" } , status = 400 )

# http://127.0.0.1:8080/Service/read?id=MAIN.u
async def readADS(request):
    global PLC
    ID = request.rel_url.query[ "id" ]    
    if ID != None:
        value = PLC.read_by_name( ID , pyads.PLCTYPE_LREAL )
        return web.json_response( { "id" : ID , "value" : value } , status = 200 )
    else:
        return web.json_response( { "description" : "Did not receive valid variable name" } , status = 400 )
    
# http://127.0.0.1:8080/Service/shutdown
async def shutdownADS(request):
    global PLC
    PLC.close()
    return web.json_response( { "description" : "Succesful shutdown" } , status = 200 )


###   ###   ###   ###   
# Bind paths and launch app
if __name__ == "__main__":
    app = web.Application( )
    app.add_routes( [ web.post( "/Service/initialize" , initializeADS ) ,
                         web.get( "/Service/testConnection" , testConnection ),
                         web.put( "/Service/write" , writeADS ) ,
                         web.get( "/Service/read" , readADS ) ,
    					 web.delete( "/Service/shutdown" , shutdownADS ) ] )

    web.run_app( app , port = 8080 )

