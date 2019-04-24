# -*- coding: utf-8 -*-
"""
Created on Fri Nov  9 15:04:57 2018

.. module:: CoSimulationOrchestrator

@author: geos + viho

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

from aiohttp import web # aiohttp version 3.3.2
from CoSimulationManager import CoSimulationManager
from DatabaseManager import DatabaseManager
import os
import json #version 2.0.9
import aiohttp_cors #version 0.7.0

###   ###   ###   ###   
# Global properties and initialisation
# 1 DatabaseManager:
#C:\Users\viho\Documents\COE_Docker\COE docker\sharedFolder
#pathToDB = os.path.join( "C:/" ,
#                         "Users" ,
#                         "viho" ,
#                         "Documents" ,
#                         "COE_Docker" ,
#                         "COE docker" ,
#                         "sharedFolder" ,
#                         "test.db" )

pathToDB = os.path.join( "/" ,
                   "database" , 
                   "test.db" )
dbm = DatabaseManager( pathToDB )
dbm.initTables()


# 2 CoSimulationManager
csm = None




###   ###   ###   ###   
# REST API resources

# http://127.0.0.1:3030/cso/testConnection
async def testConnection( request ):
    """
    Function to test if CSO is online and operative

    :param request:
    :type http-request:

    :Endpoint: http://127.0.0.1:3030/cso/testConnection

    :returns: Statusmessage, HTTP statuscode = 200
    :rtype: JSON

    :Example:

    .. code-block:: python

        { "Status" : "OK"}

    """
    print( "Connection works." )
    
    return web.json_response( { "status" : "OK" } , status = 200 )

# http://127.0.0.1:3030/cso/uploadYAML
async def uploadYAML( request ):
    """
    Endpoint to receive json encoded full group from YAML file
    Load to database afterwards
    """
    global dbm
    
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        
        # create group
        gid = int(dbm.createGroup( data[ "name" ] ))
        
        # create services of group
        for name , s in data[ "services" ].items():
            sid = dbm.createService( name ,
                                     s[ "ip" ] ,
                                     s[ "port" ] ,
                                     s[ "target" ] ,
                                     gid )
            s[ "id" ] = sid
            
            # create inputs
            lInputs = s[ "inputs" ]
            for i in lInputs:
                iid = dbm.createInput( sid , i[ "name" ] , i[ "initialValue" ] )
                i[ "id" ] = iid
                
            # create outputs
            lOutputs = s[ "outputs" ]
            for o in lOutputs:
                oid = dbm.createOutput( sid , o[ "name" ] , o[ "initialValue" ] )
                o[ "id" ] = oid
        
        # create mappings
        lMappings = data[ "mappings" ]
        
        for m in lMappings:
            soid = None
            oid  = None
            siid = None
            iid  = None 
            
            for name , s in data[ "services" ].items():
                if name == m[ "oservice" ]:
                    soid = s[ "id" ]
                    
                    lOutputs = s[ "outputs" ]
                    for o in lOutputs:
                        if o[ "name" ] == m[ "oname" ]:
                            oid = o[ "id" ]
            
                if name == m[ "iservice" ]:
                    siid = s[ "id" ]
                    
                    lInputs = s[ "inputs" ]
                    for i in lInputs:
                        if i[ "name" ] == m[ "iname" ]:
                            iid = i[ "id" ]
            if gid == None or soid == None or oid == None or siid == None or iid == None:
                return web.json_response( { "description" : "Illness in mappings" } , status = 500 )
                    
            
            mapping = { "gid"  : gid  ,
                        "soid" : soid ,
                        "oid"  : oid  ,
                        "siid" : siid ,
                        "iid"  : iid }
            dbm.createMapping( mapping )
        
        # create simconfig
        lConfigs = data[ "simconfigs" ]
        # create run    
        valueTableName = "Table" + str( gid )
        rid = dbm.createRun( valueTableName , gid )
       
        for c in lConfigs:
            # create config
            dbm.setSimConfig( rid , c[ "startTime" ] , c[ "endTime" ] , c[ "stepSize" ] )
    
    return web.json_response( { "description" : "Created group" , "id" : int( gid ) , "rid" : int( rid ) } , status = 200 )

# http://127.0.0.1:3030/cso/create/group
async def createGroup( request ):
    """
    Function to create a group using the DatabaseManager
    
    :param request: Request is sent with JSON-Body 
    :type request: POST

    :Endpoint: http://127.0.0.1:3030/cso/create/group

    :returns: Statusmessage with created group id, HTTP statuscode = 200
    :rtype: JSON

    :Example: JSON Body

    .. code-block:: python

        { "name" : <name_of_group> }
    
    Returns:
    
    .. code-block:: python
        
        { "Status" : "Group successfully created. ", "id" : <gid> }
    
    .. note:: 
        
        <gid> : Group identifier ( integer )
        
    """
    global dbm
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        gname = data[ "name" ]
        gid = dbm.createGroup( gname )
    return web.json_response( { "description" : "Group successfully created. ", "id" : int( gid ) } , status = 200 )

# http://127.0.0.1:3030/cso/edit/group
async def editGroup( request ):
    """
   Function to edit a group using the DatabaseManager
    
    :param request: Request is sent with JSON-Body 
    :type request: PUT

    :Endpoint: http://127.0.0.1:3030/cso/edit/group

    :returns: Statusmessage with edited group id , HTTP statuscode = 200
    :rtype: JSON
        
    :Example: JSON Body

    .. code-block:: python

        { "name" : <name_of_group> , 
          "id"   : <gid> }
    
    Returns:
    
    .. code-block:: python
        
        { "Status" : "Group successfully edited. ", "id" : <gid> }

    .. note:: 
        
        <gid> : Group identifier ( integer )
    """
    global dbm
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        gname = data[ "name" ] 
        gid = data[ "id" ] 
        gid = dbm.editGroup( gid , gname )
    return web.json_response( { "name" : str( gname ) , "id" : int( gid ) } , status = 200 )

# http://127.0.0.1:3030/cso/group?id=1
async def retrieveGroup( request ):
    """
    Function to retrieve a group
    
    :param request: Request with group id
    :type request: GET
    :param id: Additional request parameter
    :type id: integer

    :Endpoint: http://127.0.0.1:3030/cso/group?id=1

    :returns: Requested group of given group identifier , HTTP statuscode = 200
    :rtype: JSON
    
    :Example: 

    .. code-block:: python

        { "services" : [ { 
                "id"     : <sid> , 
                "name"   : <name_of_service> ,
                "ip"     : <ip_of_service> ,
                "port"   : <port_of_service> ,
                "target" : <address_of_service>, 
                "inputs" : [ { 
                    "id"         : <id_of_input> , 
                    "inputName"  : <name_of_input> ,
                    "initialVal" : <float_value>
                } , { anotherInput }  ]  ,  
                "outputs": [ { 
                    "id"         : <id_of_output> , 
                    "inputName"  : <name_of_output>,
                    "initialVal" : <float_value> 
                } , { anotherOutput } ]  
          } , { another service }
          ]
        }
        
    """
    global dbm
    gid = int( request.rel_url.query[ "id" ] )
    group = dbm.retrieveServices( gid )
    if group != None:
        return web.json_response( group , status = 200 )
    else:
        return web.json_response( { "description" : "ID provided not known" } , status = 404 )

# http://127.0.0.1:3030/cso/groups
async def groups( request ):
    """
    Function to retrieve all groups
    
    :param request: Http request
    :type request: GET

    :Endpoint: http://127.0.0.1:3030/cso/groups

    :returns: All groups saved in the database , HTTP statuscode = 200
    :rtype: JSON
    
    :Example:

    .. code-block:: python
    
        [ { "id"  : <gid> ,
            "name" : <gname> , 
            "services" : [ {
                "id"   : <sid> , 
                "name" : <sname> , 
                "ip"   : <sip> , 
                "port" : <sport> , 
                "target" : <starget> , 
                "inputs" : [ {
                    "id" : <iid> , 
                    "inputName" : <iname> , 
                    "initialVal" : <iinitvalue> } , { another input } 
                ] , 
                "outputs" : [ {
                    "id" : <oid> , 
                    "outputName" : <oname> , 
                    "initialVal" : <oinitvalue> } , { another output } 
                ] } , 
                {  another Service } 
            ]
          } , { another Group } 
        ]
    """
    global dbm
    lGroups = dbm.getAllGroups()
    return web.json_response( lGroups , status = 200 )

# http://127.0.0.1:3030/cso/delete/group?id=1
async def deleteGroup( request ):
    """
    Function to delete a group
    
    :param request: Request is sent with group id
    :type request: DELETE
    :param id: Additional request parameter
    :type id: integer
    

    :Endpoint: http://127.0.0.1:3030/cso/delete/group?id=1

    :returns: Statusmessage with deleted group id , HTTP statuscode = 200
    :rtype: JSON
    
    :Example: 
    
    Returns:

    .. code-block:: python
        
        { "Status" : "Group successfully deleted. " ,  "id" : <gid> }
        
        
    .. note::
    
        <gid> : group identifier
    """
    global dbm
    gid = int( request.rel_url.query[ "id" ] )
    dbm.deleteGroup( gid )
    return web.json_response( { "description" : "Group successfully deleted. " ,  "id" : gid } , status = 200 )

# http://127.0.0.1:3030/cso/create/service
async def createService( request ):
    """
    Function to create a service of a group using the DatabaseManager
    
    :param request: Request is sent with JSON-Body 
    :type request: POST

    :Endpoint: http://127.0.0.1:3030/cso/create/service

    :returns: Statusmessage with created service id , HTTP statuscode = 200
    :rtype: JSON
    
    :Example: JSON Body
    
    .. code-block:: python
        
        { "name"   : <sname> , 
          "ip"     : <sip> , 
          "port"   : <sport> , 
          "target" : <starget> ,
          "gid" :   <gid>
        }
    
    Returns:

    .. code-block:: python
        
        { "Status" : "Service successfully created. " ,  "id" : <sid> }
        
        
    .. note::
    
        <sid> : service identifier
    """
    global dbm
    sid = 0
    if request.body_exists:
        print( "body exists" )
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )        
                
        print( data )
        sid = dbm.createService( data[ "name" ], data[ "ip" ] , data[ "port" ] , data[ "target" ] , data[ "gid" ])
        
        
    return web.json_response( { "description" : "Service successfully created. " , "id" : sid } , status = 200 )   

# http://127.0.0.1:3030/cso/service?id=1
async def getService( request ):
    """
    Function to get specific service of given ID
    
    :param request: Request with service id
    :type request: GET
    
    :param id: Service id as additional request parameter
    :type id: integer
    
    :Endpoint: http://127.0.0.1:3030/cso/service?id=1
    
    :returns: Requested service , HTTP statuscode = 200
    :rtype: LIST of JSON , HTTP-statuscode
    
    :Example: 
    
    Returns: 
    
    .. code-block:: python
        
        { "gid" : <gid> , 
          "id"  : <sid> , 
          "name" : <sname> ,
          "ip"     : <sip> , 
          "port"   : <sport> , 
          "target" : <starget> 
        }
    """
    global dbm
    
    sid = int( request.rel_url.query[ "id" ] )
    service = dbm.retrieveService( sid )
    
    return web.json_response( service , status = 200 )

# http://127.0.0.1:3030/cso/services?group=1
async def getServicesOfGroup( request ):
    """
    Function to retrieve all services of given group id
    
    :param request: Request with group id
    :type request: GET
    
    :param id: Additional request parameter
    :type id: integer
    
    :Endpoint: http://127.0.0.1:3030/cso/services?group=1
    
    :returns: Requested service of given group id , HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example:
    
    Returns:

    .. code-block:: python
        
        [ { "gid" : <gid> , 
            "id"  : <sid> , 
            "name" : <sname> ,
            "ip"     : <sip> , 
            "port"   : <sport> , 
            "target" : <starget> 
            } , { another Serivce }
        ]
    """
    global dbm
    gid = int( request.rel_url.query[ "group" ] )
    services = dbm.retrieveServices( gid )
    
    return web.json_response( services , status = 200)


# http://127.0.0.1:3030/cso/edit/service
async def editService( request ):
    """
    Function to edit a service using the DatabaseManager
    specific editting is possible -> split request to attribute instead of full json body ( implemented on request )
    
    :param request: Request with JSON Body
    :type request: PUT
    
    :Endpoint: http://127.0.0.1:3030/cso/edit/service
    
    :returns: Statusmessage , HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: JSON Body
    
    .. code-block:: python
        
        { "gid" : <gid> , 
          "id"  : <sid> , 
          "name" : <sname> ,
          "ip"     : <sip> , 
          "port"   : <sport> , 
          "target" : <starget> 
        }
    
    Returns:

    .. code-block:: python
        
        { "Status" : "Service successfully edited. " ,  "id" : <sid> }
    
    .. note::
        
        <gid> : group identifier ( integer )
    """
    global dbm
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        sname = str( data[ "name" ] )
        gid = int( data[ "gid" ] )
        sid = int( data[ "id" ] ) 
        sip = str( data[ "ip" ] )
        sport = str( data[ "port" ] )
        starget = str( data[ "target" ] )
        
        dbm.editServiceGroup( sid , gid ) 
        dbm.editServiceName( sid , sname )
        dbm.editServiceIP( sid , sip )
        dbm.editServicePort( sid , sport )
        dbm.editServiceTarget( sid , starget )
        
        
    return web.json_response( { "description" : "Service successfully edited. " , "id" : int( sid ) } , status = 200 )

# http://127.0.0.1:3030/cso/service?id=1
async def retrieveService( request ):
    """
    Function to get specific service of given ID
    
    :param request: Request with service id
    :type request: GET
    
    :param id: Service id as additional request parameter
    :type id: integer
    
    :Endpoint: http://127.0.0.1:3030/cso/service?id=1
    
    :returns: Requested service , HTTP statuscode = 200
    :rtype: LIST of JSON , HTTP-statuscode
    
    :Example: 
    
    Returns: 
    
    .. code-block:: python
        
        { "gid" : <gid> , 
          "id"  : <sid> , 
          "name" : <sname> ,
          "ip"     : <sip> , 
          "port"   : <sport> , 
          "target" : <starget> 
        }
    """
    global dbm
    
    sid = int( request.rel_url.query[ "id" ] )
    dService = dbm.retrieveService( sid )
    
    return web.json_response( dService , status = 200 )


# http://127.0.0.1:3030/delete/service?id=1
async def deleteService( request ):
    """
    Function to delete Service with given ID
    
    :param request: Request with service id
    :type request: DELETE
    
    :param id: Service id as additional request parameter
    :type id: integer
    
    :Endpoint: http://127.0.0.1:3030/cso/delete/service?id=1
    
    :returns: Statusmessage with deleted service id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: 
    
    Returns: 
    
    .. code-block:: python
        
        { "status" : "Service successfully deleted. " , "id" : <sid> }
    """
    global dbm
    sid = int( request.rel_url.query[ "id" ] )
    
    delID = dbm.deleteService( sid )
    
    if( sid == delID ):
        return web.json_response( { "description" : "Service successfully deleted. " , "id" : sid } , status = 200)

    ### MISSING ERROR HANDLING ###

# http://127.0.0.1:3030/cso/create/output
async def createOutput( request ):
    """
    Function to create Output
    
    :param request: Request is sent with JSON body
    :type request: POST
    
    :Endpoint: http://127.0.0.1:3030/cso/create/output
    
    :returns: Statusmessage with created output id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: JSON Body
    
    .. code-block:: python
        
        { "sid" : <soid> , 
          "name"      : <oname> , 
          "initialValue": <ovalue> 
        }       
    
    Returns: 
    
    .. code-block:: python
        
        { "status" : "Output successfully created. " , "id" : <oid> }
        
    .. note:: 
    
        <soid> : service output identifier ( integer )
        <ovalue> : output initial value ( float )
    """
    global dbm

    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        
        oid = dbm.createOutput( data[ "sid" ] , data[ "name" ] , data[ "initialValue" ] )
                
    return web.json_response( { "description" : "output successfully created" , "id" : oid } , status = 200)

# http://127.0.0.1:3030/cso/edit/output
async def editOutput( request ):
    """
    Function to edit an output using the DatabaseManager
    specific editting is possible -> split request to attribute instead of full json body
    
    :param request: Request is sent with JSON body
    :type request: PUT
    
    :Endpoint: http://127.0.0.1:3030/cso/edit/output
    
    :returns: Statusmessage with edited output id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: JSON Body
    
    .. code-block:: python
        
        { "serviceid" : <soid> , 
          "id"        : <oid> ,
          "name"      : <oname> , 
          "initialValue": <ovalue> 
        }       
    
    Returns: 
    
    .. code-block:: python
        
        { "status" : "Output successfully edited. " , "id" : <oid> }
        
    .. note:: 
    
        <oid> : output identifier ( integer )
    """
    global dbm
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        sid = int( data[ "sid" ] ) 
        oid = int( data[ "id" ] )
        oname = str( data[ "name" ] )
        oiv = float( data[ "initialValue" ] )
        
        dbm.editNameOfOutput( oid , oname )
        dbm.editServiceOfOutput( oid , sid )
        dbm.editInitValueOfOutput( oid , oiv )
        
        
    return web.json_response( { "description" : "Output successfully edited. " , "id" : oid } , status = 200 )

# http://127.0.0.1:3030/cso/output?id=1
async def retrieveOutput( request ):
    """
    Function to get specific output of given ID
    
    :param request: Request is sent with output id
    :type request: GET
    
    :param id: Output id as additional request parameter
    :type id: integer
    
    :Endpoint: http://127.0.0.1:3030/cso/output?id=1
    
    :returns: Requested output, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example:
    
    Returns: 
    
    .. code-block:: python
        
        { "id" : <oid> , 
          "name" : <oname> , 
          "initialValue" : <ovalue>
          "serviceid" : <sid>
        }
        
    .. note:: 
    
        <sid> : reference to service identifier ( integer )
    """
    global dbm
    
    oid = int( request.rel_url.query[ "id" ] )
    
    out = dbm.retrieveOutput( oid )
    
    return web.json_response( out , status = 200 )

# http://127.0.0.1:3030/cso/alloutputs
async def outputs( request ):
    """
    Function to get all outputs
    
    :param request: Simple
    :type request: GET

    :Endpoint: http://127.0.0.1:3030/cso/alloutputs
    
    :returns: Requested inputs, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example:
    
    Returns: 
    
    .. code-block:: python
        
        [ { "id" : <oid> , 
            "name" : <oname> , 
            "initialValue" : <ivalue>
            "sid" : <sid>
            } , { another input }
        ]
    """
    global dbm
    
    ios = dbm.retrieveOutputs()   
    
    return web.json_response( ios , status = 200)


# http://127.0.0.1:3030/cso/outputs?service=1
async def serviceOutputs( request ):
    """
    Function to get all outputs of specific service
    
    :param request: Request is sent with service id
    :type request: GET
    
    :param service: Service id as additional request parameter
    :type service: integer
    
    :Endpoint: http://127.0.0.1:3030/cso/outputs?service=1
    
    :returns: Requested outputs of given service, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example:
    
    Returns: 
    
    .. code-block:: python
        
        [ { "id" : <oid> , 
            "name" : <oname> , 
            "initialValue" : <ovalue>
            "serviceid" : <sid>
            } , { another output }
        ]
    """
    global dbm
    sid = int( request.rel_url.query[ "service" ] )
    
    oos = dbm.retrieveOutputsOfService( sid )
    
    
    return web.json_response( oos , status = 200)

# http://127.0.0.1:3030/cso/delete/output?id=1
async def deleteOutput( request ):
    """
    Function to delete specific output of given ID
    
    :param request: Request is sent with output id
    :type request: DELETE
    
    :param id: Output id as additional request parameter
    :type id: integer
    
    :Endpoint: http://127.0.0.1:3030/cso/delete/output?id=1
    
    :returns: Statusmessage with deleted output id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example:
    
    Returns: 
    
    .. code-block:: python
        
        { "Status" : "Output successfully deleted. " , "id" : <oid> }
    """
    global dbm
    oid = request.rel_url.query[ "id" ]
    delO = dbm.deleteOutput( oid )
    return web.json_response( { "description" : "Output successfully deleted. " , "id" : delO } , status = 200)

# http://127.0.0.1:3030/cso/create/input
async def createInput( request ):
    """
    Function to create Input
    
    :param request: Request is sent with JSON body
    :type request: POST
    
    :Endpoint: http://127.0.0.1:3030/cso/create/input
    
    :returns: Statusmessage with created input id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: JSON Body
    
    .. code-block:: python
        
        { "sid" : <siid> , 
          "name"      : <iname> , 
          "initialValue": <ivalue> 
        }       
    
    Returns: 
    
    .. code-block:: python
        
        { "status" : "Input successfully created. " , "id" : <iid> }
        
    .. note:: 
    
        <siid> : service input identifier ( integer )
        <ivalue> : input initial value ( float )
    """
    global dbm
    
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        
        iid = dbm.createInput( data[ "sid" ] , data[ "name" ] , data[ "initialValue" ] )

        
    return web.json_response( { "description" : "input successfully created" , "id" : iid } , status = 200)

# http://127.0.0.1:3030/cso/edit/input
async def editInput( request ):
    """
    Function to edit an input using the DatabaseManager
    specific editting is possible -> split request to attribute instead of full json body
    
    :param request: Request is sent with JSON body
    :type request: PUT
    
    :Endpoint: http://127.0.0.1:3030/cso/edit/input
    
    :returns: Statusmessage with edited input id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: JSON Body
    
    .. code-block:: python
        
        { "sid"   : <siid> , 
          "id"          : <iid> ,
          "name"        : <iname> , 
          "initialValue": <ivalue> 
        }       
    
    Returns: 
    
    .. code-block:: python
        
        { "status" : "Input successfully edited. " , "id" : <iid> }
    """
    global dbm
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        sid = int( data[ "sid" ] ) 
        iid = int( data[ "id" ] )
        iname = str( data[ "name" ] )
        iiv = float( data[ "initialValue" ] )
        
        dbm.editNameOfInput( iid , iname )
        dbm.editServiceOfInput( iid , sid )
        dbm.editInitValueOfInput( iid , iiv )
        
        
    return web.json_response( { "description" : "Input successfully edited. " , "id" : iid } , status = 200 )

# http://127.0.0.1:3030/cso/input?id=1
async def retrieveInput( request ):
    """
    Function to get specific output of given ID
    
    :param request: Request is sent with input id
    :type request: GET
    
    :Endpoint: http://127.0.0.1:3030/cso/input?id=1
    
    :returns: Requested input, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example:
    
    Returns: 
    
    .. code-block:: python
        
        { "serviceid"   : <siid> , 
          "id"          : <iid> ,
          "name"        : <iname> , 
          "initialValue": <ivalue> 
        }
    """
    global dbm
    
    iid = int( request.rel_url.query[ "id" ] )
    
    inp = dbm.retrieveInput( iid )
    
    return web.json_response( inp , status = 200 )


# http://127.0.0.1:3030/cso/inputs?service=1
async def serviceInputs( request ):
    """
    Function to get all inputs of specific service
    
    :param request: Request is sent with service id
    :type request: GET
    
    :param service: Service id as additional request parameter
    :type service: integer
    
    :Endpoint: http://127.0.0.1:3030/cso/inputs?service=1
    
    :returns: Requested outputs of given service, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example:
    
    Returns: 
    
    .. code-block:: python
        
        [ { "id" : <iid> , 
            "name" : <iname> , 
            "initialValue" : <ivalue>
            "sid" : <sid>
            } , { another input }
        ]
    """
    global dbm
    sid = int( request.rel_url.query[ "service" ] )
    
    ios = dbm.retrieveInputsOfService( sid )   
    
    return web.json_response( ios , status = 200)

# http://127.0.0.1:3030/cso/allinputs
async def inputs( request ):
    """
    Function to get all inputs
    
    :param request: Simple
    :type request: GET

    :Endpoint: http://127.0.0.1:3030/cso/allinputs
    
    :returns: Requested inputs, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example:
    
    Returns: 
    
    .. code-block:: python
        
        [ { "id" : <iid> , 
            "name" : <iname> , 
            "initialValue" : <ivalue>
            "sid" : <sid>
            } , { another input }
        ]
    """
    global dbm
    
    ios = dbm.retrieveInputs()   
    
    return web.json_response( ios , status = 200)

# http://127.0.0.1:3030/cso/delete/input?id=1
async def deleteInput( request ):
    """
    Function to delete specific input of given ID
    
    :param request: Request is sent with input id
    :type request: DELETE
    
    :param id: Input id as additional request parameter
    :type id: integer
    
    :Endpoint: http://127.0.0.1:3030/cso/delete/input?id=1
    
    :returns: Statusmessage with deleted input id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example:
    
    Returns: 
    
    .. code-block:: python
        
        { "Status" : "Input successfully deleted. " , "id" : <iid> }
    """
    global dbm
    iid = request.rel_url.query[ "id" ]
    
    delI = dbm.deleteInput( iid )
    return web.json_response( { "description" : "Input successfully deleted." , "id" : delI } , status = 200 )

# http://127.0.0.1:3030/cso/create/mapping
async def createMapping( request ):
    """
    function to create mapping

    :param request: Request is sent with JSON body
    :type request: POST
    
    :Endpoint: http://127.0.0.1:3030/cso/create/mapping
    
    :returns: Statusmessage with created mapping id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: JSON Body
    
    .. code-block:: python
        
        { "gid"  : <gid> , 
          "soid" : <soid> ,
          "oid"  : <oid> ,
          "siid" : <siid> ,
          "iid"  : <iid> 
        }
    
    Returns: 
    
    .. code-block:: python
        
        { "status" : "Mapping successfully set. " , "id" : <mid> }
        
    .. note:: 
    
        <mid> : mapping identifier ( integer )
        <soid> , <siid> : service of output/input identifier ( integer )
        <gid> : group identifier ( integer )
        <oid> , <iid> : output/input identifier ( integer )
    """    
    global dbm
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        mid = dbm.createMapping( data )
        
    return web.json_response( { "Status" : "Mappings successfully created." , "id" : mid } , status = 200 ) 

# http://127.0.0.1:3030/cso/edit/mapping
async def editMapping( request ):
    """
    Function to edit mapping using the DatabaseManager
    specific editting is possible -> split request to attribute instead of full json body
    
    :param request: Request is sent with JSON body
    :type request: PUT
    
    :Endpoint: http://127.0.0.1:3030/cso/edit/mapping
    
    :returns: Statusmessage with edited mapping id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: JSON Body
    
    .. code-block:: python
        
        { "id"   : <mid> ,
          "gid"  : <gid> , 
          "soid" : <soid> ,
          "oid"  : <oid> ,
          "siid" : <siid> ,
          "iid"  : <iid> 
        }
    
    Returns: 
    
    .. code-block:: python
        
        { "status" : "Mapping successfully edited. " , "id" : <mid> }
        
    .. note:: 
    
        <mid> : mapping identifier ( integer )
    """
    global dbm
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        mid = dbm.editMapping( data )
    
    return web.json_response( { "description" : "Mapping successfully edited. " , "id" : mid } , status = 200 )

# http://127.0.0.1:3030/cso/mappings?group=1
async def retrieveMappings( request ):
    """
    Function to retrieve all existing mappings of a group

    :param request: Request is sent with group id
    :type request: GET
    
    :param group: group identifier
    :type group: integer
    
    
    :Endpoint: http://127.0.0.1:3030/cso/mappings?group=1
    
    :returns: Requested mapping of given group id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: 
    
    Returns: 
    
    .. code-block:: python
        
        [ { "id"   : <mid> ,
            "gid"  : <gid> , 
            "soid" : <soid> ,
            "oid"  : <oid> ,
            "siid" : <siid> ,
            "iid"  : <iid> 
            } , { another Mapping }
        ]
    """
    global dbm
    gid = int( request.rel_url.query[ "group" ] )
    
    maps = dbm.retrieveMappings( gid )
    
    
    return web.json_response( maps , status = 200 )

# http://127.0.0.1:3030/cso/mapping?id=1
async def retrieveMapping( request ):
    """
    Function to retrieve one specified mapping

    :param request: Request is sent with mapping id
    :type request: GET
    
    :param id: mapping identifier
    :type id: integer
    
    
    :Endpoint: http://127.0.0.1:3030/cso/mapping?id=1
    
    :returns: Requested mapping of given mapping id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: 
    
    Returns: 
    
    .. code-block:: python
        
        { "id"   : <mid> ,
          "gid"  : <gid> , 
          "soid" : <soid> ,
          "oid"  : <oid> ,
          "siid" : <siid> ,
          "iid"  : <iid> 
        }
    """
    global dbm
    mid = int( request.rel_url.query[ "id" ] )
    
    omap = dbm.retrieveMap( mid )
    
    
    return web.json_response( omap , status = 200 )

# http://127.0.0.1:3030/cso/delete/mapping?id=1
async def deleteMapping( request ):
    """
    Function to delete mapping
    
    :param request: Request is sent with mapping id
    :type request: DELETE
    
    :param id: mapping identifier
    :type id: integer
    
    
    :Endpoint: http://127.0.0.1:3030/cso/delete/mapping?id=1
    
    :returns: Statusmessage with deleted mapping id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: 
    
    Returns: 
    
    .. code-block:: python
        
        { "Status" : "Mapping successfully deleted. " , "id" : <mid> }
    """
    global dbm
    mid = int( request.rel_url.query[ "id" ] )
    
    dMid = dbm.deleteMapping( mid )
    
    return web.json_response( { "description" : "Mapping successfully deleted. " ,  "id" : dMid } , status = 200 )

# http://127.0.0.1:3030/cso/create/run
async def createRun( request ):
    """
    Function to create run to save table of values and corresponding configuration

    :param request: Request is sent with JSON body
    :type request: POST
    
    :Endpoint: http://127.0.0.1:3030/cso/create/run
    
    :returns: Statusmessage with created run id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: JSON Body
    
    .. code-block:: python
        
        { "tableName" : <tname> , 
          "group" : <gid> 
        }       
    
    Returns: 
    
    .. code-block:: python
        
        { "status" : "Run successfully initiated. " , "id" : <iid> }
        
    .. note:: 
    
        <tname> : name of table where the values are logged ( string )
    """
    global dbm
    
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        tabName = data[ "tableName" ]
        gid = data[ "gid" ]
        tid = dbm.createRun( tabName , gid )
    
    return web.json_response( { "description" : "Run successfully initiated. " , "Table to log values of run created with id: ": tid } , status = 200 )

# http://127.0.0.1:3030/cso/edit/run
async def editRunTable( request ):
    """
    Function to create run to save table of values and corresponding configuration

    :param request: Request is sent with JSON body
    :type request: POST
    
    :Endpoint: http://127.0.0.1:3030/cso/edit/run
    
    :returns: Statusmessage with created run id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: JSON Body
    
    .. code-block:: python
        
        { 
          "id" : <rid> , 
          "tableName" : <tname> , 
          "group" : <gid> 
        }       
    
    Returns: 
    
    .. code-block:: python
        
        { "status" : "Run successfully edited. " , "id" : <rid> }
        
    .. note:: 
    
        <tname> : name of table where the values are logged ( string )
    """
    global dbm
    
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        tabName = data[ "tableName" ]
        rid = data[ "id" ]
        dbm.editRunTableName( rid , tabName )
    
    return web.json_response( { "description" : "Table Name of Run successfully edited. " } , status = 200 )

# http://127.0.0.1:3030/cso/runs?group=1

async def retrieveRuns( request ):
    """
    Function to get all runs
    
    :param request: Simple get request
    :type request: GET

    :Endpoint: http://127.0.0.1:3030/cso/runs
    
    :returns: Requested runs, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example:
    
    Returns: 
    
    .. code-block:: python
        
        [ { "id" : <rid> , 
            "valueTableName" : <tname> , 
            "group" : <group>
            } , { another run }
        ]

    """

    global dbm

    gid = int( request.rel_url.query[ "group" ] )

    runs = dbm.retrieveRuns( gid )

    return web.json_response( runs , status = 200 )


# http://127.0.0.1:3030/cso/delete/run?id=1
async def deleteRun( request ):
    """
    Function to edit run using the DatabaseManager
    specific editting is possible -> split request to attribute instead of full json body
    
    :param request: Request is sent with JSON body
    :type request: DELETE
    
    :Endpoint: http://127.0.0.1:3030/cso/delete/run
    
    :returns: Statusmessage with edited mapping id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    
    Returns: 
    
    .. code-block:: python
        
        { "status" : "Run successfully deleted. " , "id" : <rid> }
        
    .. note:: 
    
        <rid> : run identifier ( integer )
    """
    global dbm
    rid = int( request.rel_url.query[ "id" ] )
    mid = dbm.deleteRun( rid )
    
    return web.json_response( { "Status": "Run successfully deleted. " , "id" : mid } , status = 200 )


# http://127.0.0.1:3030/cso/logValues
async def logValues( request ):
    """
    Function to log run into table

    :param request: Request is sent with JSON body
    :type request: POST
    
    :Endpoint: http://127.0.0.1:3030/cso/logValues
    
    :returns: Statusmessage with row id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: JSON Body
    
    .. code-block:: python
        
        { "runid" : <rid> , 
          "inputValues" : [ <ival1> , <ival2> , <ival3> , ... ]
          "outputValues" : [ <oval1> , <oval2> , <oval3> , ... ]
        }       
    
    Returns: 
    
    .. code-block:: python
        
        { "status" : "Run successfully initiated. " , "id" : <iid> }
        
    .. note:: 
    
        <ivalX> : float values of respective input names ( float ), ORDER HAS TO BE FIXED
        <ovalX> : same as above for output
    """
    global dbm
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        runID = data[ "runid" ]
        linputVal = data[ "inputValues" ]
        loutputVal = data[ "outputValues" ]
        vid = dbm.insertValues( runID , 0.0 , linputVal , loutputVal )
        
    return web.json_response( { "description" : "Values successfully stored." , "id" : vid } , status = 200 )


# http://127.0.0.1:3030/cso/table?rid=1

async def retrieveTableName( request ): 
    """
    function to retrieve table name of a run.

    :param request: Request
    :type request: GET

    :Endpoint: http://127.0.0.1:3030/cso/tables?run=1

    :returns: Name of requested table
    :rtype: JSON, HTTP-Statuscode


    :Example:

    Returns: 

    .. code-block:: python

        { "table" : <tname> }

    """

    global dbm

    rid = int( request.rel_url.query[ "rid" ] )

    tname = dbm.retrieveTableName( rid )
    
    return web.json_response( tname , status = 200 )

# http://127.0.0.1:3030/cso/tableKeys?tname=

async def retrieveTableKeys( request ):
    """
    function to retrieve coloumn keys of a table

    :param request: Request is sent with name of table
    :type request: GET

    :Endpoint: http://127.0.0.1:3030/cso/tableKeys?tname=tableName

    :returns: Requested coloumn names of a table
    :rtype: JSON list, HTTP-Statuscode

     Returns:

        .. code-block:: python

            [ "value_id" , "run_id" , "timestamp" , "var1_service_input" , .... ]

    """
    global dbm
    tname = request.rel_url.query[ "tname" ]
    keys = dbm.retrieveTableKeys( tname )

    return web.json_response( keys , status = 200 )


# http://127.0.0.1:3030/cso/values?rid=1
async def retrieveValues( request ):
    """
    function to retrieve value of given run id
    
    :param request: Request is sent with run id
    :type request: GET
    
    :Endpoint: http://127.0.0.1:3030/cso/values?id=1
    
    :returns: Requested values of given run id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: 
    
    Returns: 
    
    .. code-block:: python
        
        [
            [ <vid> , <val1> , <val2> , ... ] , #first row of value loggs 
            [ <vid> , <val1> , <val2> , ... ] , #second row of value loggs 
            [ <vid> , <val1> , <val2> , ... ] #third row of value loggs 
            ...
        ]
        
    .. note:: 
    
        <vid> : identifier of value set ( integer )
    """
    global dbm
    rid = int( request.rel_url.query[ "rid" ] )
    runs = dbm.retrieveValues( rid )
    out = []
    for run in runs:
        out.append( list( run ) )
        
    return web.json_response( out , status = 200)
    

# http://127.0.0.1:3030/cso/delete/valueTable?id=1
async def deleteValueTable( request ):
    """
    function to delete log table of given table id
    
    :param request: Request is sent with run id
    :type request: DELETE
    
    :Endpoint: http://127.0.0.1:3030/cso/delete/valueTable?id=1
    
    :returns: Statusmessage with deleted table name and id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example:
    
    Returns: 
    
    .. code-block:: python
        
        { "Status" : "Table successfully deleted. " , "name" : <tname> , "id" : <tid> }
        
    .. note:: 
    
        <tid> : table identifier ( integer )

    """
    global dbm
    rid = int( request.rel_url.query[ "id" ] )
    dtidmessage = dbm.deleteValueTable( rid )
    
    return web.json_response( { "Status" : dtidmessage , "id" : rid } , status = 200 )

# http://127.0.0.1:3030/cso/create/config
async def createConfig( request ):
    """
    function to create simulation configuration to  specific logging table
    
    :param request: Request is sent with JSON body
    :type request: POST
    
    :Endpoint: http://127.0.0.1:3030/cso/create/config
    
    :returns: Statusmessage with created simulation configuration id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: JSON Body
    
    .. code-block:: python
    
        { "rid" : <rid> , 
          "startTime" : <stime> , 
          "endTime" : <etime> , 
          "stepSize" <ssize> 
        }
    
    
    Returns: 
    
    .. code-block:: python
        
        { "Status" : "Simulation configuration successfully set to run. " , "id" : <cid> }
        
    .. note:: 
    
        <cid> : simulation configuration identifier ( integer ) , 
        <stime> , <etime> : starting time and ending time of simulation run ( integer )
        <ssize> : step size of time steps ( float )
    """
    global dbm
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        rid = data[ "rid" ]
        stime = data[ "startTime" ]
        etime = data[ "endTime" ]
        ssize = data[ "stepSize" ]
        
        cid = dbm.setSimConfig( rid , stime , etime , ssize )
        
    return web.json_response( { "description" : "Configuration successfully set to run. " , "runID" : rid  , "id" : cid } , status = 200 )
 
# http://127.0.0.1:3030/cso/edit/config
async def editConfig( request ):
    """
    Function to edit an input using the DatabaseManager
    specific editting is possible -> split request to attribute instead of full json body
    
    :param request: Request is sent with JSON body
    :type request: PUT
    
    :Endpoint: http://127.0.0.1:3030/cso/edit/config
    
    :returns: Statusmessage with edited simulation configuration id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: JSON Body
    
    .. code-block:: python
    
        { "runid" : <rid> , 
          "id"    : <cid> ,
          "startTime" : <stime> , 
          "endTime" : <etime> , 
          "stepSize" <ssize> 
        }
    
    
    Returns: 
    
    .. code-block:: python
        
        { "Status" : "Simulation configuration successfully edited. " , "id" : <cid> }
    """
    global dbm
    if request.body_exists:
        data = await request.read()
        data = json.loads( data.decode( "utf-8" ) )
        rid = int( data[ "rid" ] ) 
        cid = int( data[ "id" ] )
        stime = int( data[ "startTime" ] )
        etime = int( data[ "endTime" ] )
        ssize = float( data[ "stepSize" ] )
        
        dbm.editConfig( cid , rid , stime , etime , ssize )
        
    return web.json_response( { "description" : "Configuration successfully edited. " , "id" : cid } , status = 200 )    

# http://127.0.0.1:3030/cso/config?id=1
async def retrieveConfig( request ):
    """
    function to retrieve configuration of given config id
    
    :param request: Request is sent with configuration id
    :type request: GET
    
    :Endpoint: http://127.0.0.1:3030/cso/config?id=1
    
    :returns: Requested configuration, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: 
    
    Returns:
    
    .. code-block:: python
    
        { "runid" : <rid> ,
          "id" : <cid> , 
          "startTime" : <stime> , 
          "endTime" : <etime> , 
          "stepSize" <ssize> 
        }
    """
    global dbm
    cid = int( request.rel_url.query[ "id" ] )
    
    config = dbm.retrieveConfig( cid )
    
    return web.json_response( config , status = 200 )

# http://127.0.0.1:3030/cso/configs?group=1
async def retrieveConfigsOfGroup( request ):
    """
    Function to retrieve all configurations of a given group
    
    :param request: Request is sent with group id
    :type request: GET
    
    :Endpoint: http://127.0.0.1:3030/cso/configs?group=1
    
    :returns: Requested configurations of given group, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: 
    
    Returns:
    
    .. code-block:: python
    
        [ { "rid" : <rid> ,
            "id" : <cid> , 
            "startTime" : <stime> , 
            "endTime" : <etime> , 
            "stepSize" <ssize> 
            } , { another config }
        ]
    """
    global dbm
    gid = int( request.rel_url.query[ "group" ] )
    
    configs = dbm.retrieveConfigsOfGroup( gid )


    return web.json_response( configs , status = 200 )

# http://127.0.0.1:3030/cso/delete/config?id=1
async def deleteConfig( request ):
    """
    function to delete config with given ID
    
    :param request: Request is sent with configuration id
    :type request: DELETE
    
    :Endpoint: http://127.0.0.1:3030/cso/delete/config?id=1
    
    :returns: Statusmessage with deleted config id, HTTP statuscode = 200
    :rtype: JSON , HTTP-statuscode
    
    :Example: 
    
    Returns:
    
    .. code-block:: python
    
        { "Status" : "Successfully deleted config. " , "id" : <cid> }
    """
    global dbm
    cid = int( request.rel_url.query[ "id" ] )
    
    dcid = dbm.deleteConfig( cid )
    
    return web.json_response( { "description" : "Successfully deleted config" , "id" : dcid } , status = 200 )
    

# http://127.0.0.1:3030/cso/initiateCSM?gid=1&rid=1
async def initiateCSM( request ):
    """
    function to initiate CoSimulationManager
    """
    global dbm
    global csm

    gid = int( request.rel_url.query[ "gid" ] )
    rid = int( request.rel_url.query[ "rid" ] )
    
    config = startTime  = dbm.retrieveConfig( rid )
    startTime  = config[ "start_time" ]
    endTime    = config[ "end_time" ]
    stepSize   = config[ "stepsize" ]
    services   = dbm.retrieveServicesDetailed( gid )
    mappings   = dbm.retrieveMappings( gid ) 
    csm = CoSimulationManager( gid , rid , startTime , endTime , stepSize , services , mappings )

    return web.json_response( { "description" : "OK, CSM successfully initialized." } , status = 200 )

# http://127.0.0.1:3030/cso/runCSM
async def runCSM( request ):
    """
    function to start CoSimulationManager
    """

    global csm
    global dbm

    csm.runCoSimulation()
    results = csm.getResults()
    
    keys = results.keys()
    
    columnsTuple = ( 'run_id' ,list(keys)[0], )
    for key in keys:

        if( "_inputs_" in key):
            ids = key.replace("_inputs_" , ' ').split()

            sid = int( ids[ 0 ] )
            iid = int( ids[ 1 ] )

            sname = dbm.retrieveService( sid )["name"]
            iname = dbm.retrieveInput( iid )[ "name" ]
            columnsTuple += ( sname + "_inputs_" + iname , )
        
        else:
            if( "_outputs_" in key):
                ids = key.replace("_outputs_" , ' ').split()

                sid = int( ids[ 0 ] )
                oid = int( ids[ 1 ] )

                sname = str(dbm.retrieveService( sid )[ "name" ])
                iname = str(dbm.retrieveOutput( oid )[ "name" ])
                columnsTuple += ( sname + "_outputs_" + iname , )

    columnsString = str(columnsTuple).replace("'", '')

    

    for i in range( len( results[ 'timestamp' ] ) ):
        values = ( csm.runID , )
        for key in keys:
            values += ( results[ key ].pop( 0 ) , )

        values = str( values )

        dbm.insertValues( csm.runID , columnsString , values )


    return web.json_response( { "description" : "OK, CSM successfully run." } , status = 200 )



# http://127.0.0.1:3030/cso/getValues?rid=1
async def getValues( request ):
    """
    Function to get Values of given run
    """

    global dbm

    rid = int( request.rel_url.query[ "rid" ] )
    out = dbm.retrieveValues( rid )

    return web.json_response( out , status = 200)

###   ###   ###   ###   
# Bind paths and launch app
if __name__ == "__main__":
    cso = web.Application( )
    cso.add_routes( [ web.get( "/cso/testConnection" , testConnection ) ,
                    web.post( "/cso/uploadYAML" , uploadYAML ) , 
                    web.post( "/cso/create/group" , createGroup ) ,
                    web.put( "/cso/edit/group" , editGroup ) ,
                    web.get( "/cso/group" , retrieveGroup ) ,
                    web.get( "/cso/groups" , groups ) ,
                    web.delete( "/cso/delete/group" , deleteGroup ) ,
                    web.post( "/cso/create/service" , createService ) ,
                    web.put( "/cso/edit/service" , editService ) ,
                    web.get( "/cso/service" , getService ) , 
                    web.get( "/cso/services" , getServicesOfGroup ) , 
                    web.delete( "/cso/delete/service" , deleteService ) , 
                    web.post( "/cso/create/output" , createOutput ) ,
                    web.put( "/cso/edit/output" , editOutput ) , 
                    web.get( "/cso/output" , retrieveOutput ) , 
                    web.get( "/cso/outputs" , serviceOutputs ) ,
                    web.get( "/cso/alloutputs" , outputs ) ,
                    web.delete( "/cso/delete/output" , deleteOutput ) , 
                    web.post( "/cso/create/input" , createInput ) ,
                    web.put( "/cso/edit/input" , editInput ) ,
                    web.get( "/cso/input" , retrieveInput ) ,
                    web.get( "/cso/inputs" , serviceInputs ) ,
                    web.get( "/cso/allinputs" , inputs ) ,
                    web.delete( "/cso/delete/input" , deleteInput ) , 
                    web.post( "/cso/create/mapping" , createMapping ) ,
                    web.put( "/cso/edit/mapping" , editMapping ) ,
                    web.get( "/cso/mappings" , retrieveMappings ) , 
                    web.get( "/cso/mapping" , retrieveMapping ) ,
                    web.delete( "/cso/delete/mapping" , deleteMapping ) ,
                    web.post( "/cso/create/run" , createRun ) ,
                    web.put( "/cso/edit/run" , editRunTable ) , 
                    web.get( "/cso/runs" , retrieveRuns ) , 
                    web.delete( "/cso/delete/run" , deleteRun ) , 
                    web.post( "/cso/logValues" , logValues ) , 
                    web.get( "/cso/values" , retrieveValues ) ,
                    web.get( "/cso/table" , retrieveTableName ) ,
                    web.get( "/cso/tableKeys" , retrieveTableKeys ) ,
                    web.delete( "/cso/delete/valueTable" , deleteValueTable ) ,
                    web.post( "/cso/create/config" , createConfig ) , 
                    web.put( "/cso/edit/config" , editConfig ) ,
                    web.get( "/cso/config" , retrieveConfig ) ,
                    web.get( "/cso/configs" , retrieveConfigsOfGroup ) ,
                    web.delete( "/cso/delete/config" , deleteConfig ) ,
                    web.get( "/cso/initiateCSM" , initiateCSM ) ,
                    web.get( "/cso/runCSM" , runCSM ) ,
                    web.get( "/cso/getValues" , getValues ) ] )

    cors = aiohttp_cors.setup( cso , defaults = {
        "*" : aiohttp_cors.ResourceOptions(
            allow_credentials = True ,
            allow_headers = "*" ,
            expose_headers = "*" ,
        )
    })

    for route in list( cso.router.routes() ):
        cors.add( route )

    web.run_app( cso , port = 3030 )