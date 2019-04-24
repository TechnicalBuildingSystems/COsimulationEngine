# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 16:06:53 2018

.. module:: DatabaseManager
   :synopsis: This module manages the editting of the service database.

.. moduleauthor::viho

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

import os
import re #version 2.2.1
import sqlite3 #version 2.6.0


class DatabaseManager( object ):
    """

    THIS IS THE DBM CLASS

    """
    #instance attributes , if DBManager is instantiated , the connection to
    #Database is automatically set
    #Parameters: ( os.path JOIN )
    def __init__( self , pathToDB ):
        #Point of error handling???
        self.__inst_db = sqlite3.connect( pathToDB )
        self.instCursor = self.__inst_db.cursor( )
        self.instCursor.execute('PRAGMA foreign_keys = ON')
        self.pathToDB = pathToDB
        

    def __str__( self ):
        """
        Magic string function of class
        """
        print( "This is a Database manager" )
        print( "It is connected to db in path: "  , self.pathToDB )

    def initTables( self ):
        """
        create table statements for sql queries, initiate tables with constraints
        """
        createGroup = """CREATE TABLE IF NOT EXISTS groups(
                                group_id integer PRIMARY KEY,
                                group_name text
                                );"""

        createSimConfig = """CREATE TABLE IF NOT EXISTS simconfigs(
                                config_id integer PRIMARY KEY,
                                run_id integer,
                                start_time integer,
                                end_time integer,
                                stepsize real,
                                FOREIGN KEY ( run_id ) REFERENCES runs( run_id ) ON DELETE CASCADE
                                );"""

        createServices = """CREATE TABLE IF NOT EXISTS services(
                                service_id integer PRIMARY KEY,
                                service_name text,
                                ip text,
                                port text,
                                target text,
                                groups integer,
                                FOREIGN KEY( groups ) REFERENCES groups( group_id ) ON DELETE CASCADE
                                );"""

        createInputs = """CREATE TABLE IF NOT EXISTS inputs(
                                input_id integer PRIMARY KEY,
                                variable_name text,
                                service integer,
                                initial_value real,
                                FOREIGN KEY( service ) REFERENCES services( service_id ) ON DELETE CASCADE
                                );"""

        createOutputs = """CREATE TABLE IF NOT EXISTS outputs(
                                output_id integer PRIMARY KEY,
                                variable_name text,
                                service integer,
                                initial_value real,
                                FOREIGN KEY( service ) REFERENCES services( service_id ) ON DELETE CASCADE
                                );"""

        createMappings = """CREATE TABLE IF NOT EXISTS mappings(
                                map_id integer PRIMARY KEY,
                                groups integer,
                                input integer,
                                serviceOfinput integer,
                                output integer,
                                serviceOfoutput integer,
                                FOREIGN KEY( groups ) REFERENCES groups( group_id ) ON DELETE CASCADE,
                                FOREIGN KEY( input ) REFERENCES inputs( input_id ) ON DELETE CASCADE,
                                FOREIGN KEY( serviceOfinput ) REFERENCES services( service_id ) ON DELETE CASCADE,
                                FOREIGN KEY( output ) REFERENCES outputs( output_id ) ON DELETE CASCADE,
                                FOREIGN KEY( serviceOfoutput ) REFERENCES services( service_id ) ON DELETE CASCADE
                                );"""

        createRun = """CREATE TABLE IF NOT EXISTS runs(
                                run_id integer PRIMARY KEY,
                                valueTableName text UNIQUE,
                                groups integer,
                                FOREIGN KEY ( groups ) REFERENCES groups( group_id ) ON DELETE CASCADE
                                );"""

        self.instCursor.execute( createGroup )
        self.instCursor.execute( createRun )
        self.instCursor.execute( createSimConfig )
        self.instCursor.execute( createServices )
        self.instCursor.execute( createInputs )
        self.instCursor.execute( createOutputs )
        self.instCursor.execute( createMappings )

###################################################
###                                             ###
###               GROUP SECTION                 ###
###                                             ###
###################################################

    def createGroup( self , groupName ):
        """
        Creates a group, as an entry in connected Database.

        :param groupName: Name of group.
        :type groupName: string

        :returns: ID of inserted entry.
        :rtype: integer
        """
        makeGroup = "INSERT INTO groups ( group_name ) VALUES ( ? )"
        self.instCursor.execute( makeGroup , ( groupName , ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editGroup( self , groupIdentifier , groupName ):
        """
        Edits a group of given group identifier

        :param groupIdentifier: Group identifier.
        :type groupIdentifier: integer

        :param groupName: New name of group.
        :type groupName: string

        :returns: ID of edited row.
        :rtype: integer
        """
        editGroup = "UPDATE groups SET group_name = ? WHERE group_id = ?"
        self.instCursor.execute( editGroup , ( groupName , groupIdentifier ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid

    def getAllGroups( self ):
        """
        Gets all groups and its contents

        :returns: A list of all groups in the database.
        :rtype: list
        :Example:

        .. code-block:: python

            [ 
                {
                "id"       : <id_of_group> ,
                "name"     : <name_of_group> , 
                "services" : [ {
                                    "id"     : <id_of_service> , 
                                    "name"   : <name_of_service> ,
                                    "ip"     : <name_of_service> ,
                                    "port"   : <name_of_service> ,
                                    "target" : <name_of_service> ,
                                    "inputs" : [ {
                                                    "id"         : <id_of_input> ,
                                                    "inputName"  : <name_of_input> ,
                                                    "initialVal" : <float_value>
                                                } , { another input } 
                                                ] , 
                                    "outputs" : [ {
                                                    "id"         : <id_of_output> ,
                                                    "outputName" : <name_of_output> ,
                                                    "initialVal" : <float_value>
                                                } , { another output } 
                                                ] 
                                } , { another Service }
                             ] 
                } , { another group }
            ]
            


        """

        selectGroupQ = "SELECT * FROM groups"
        self.instCursor.execute( selectGroupQ )
        lGroups = self.instCursor.fetchall( )

        groups = []

        for aGroup in lGroups:

            group = {}
            group[ "id" ] = aGroup[ 0 ]
            group[ "name" ] = aGroup[ 1 ]
            groups.append( group )

        return groups


    def deleteGroup( self , groupID ):
        """
        Deletes a group with given group identifier

        :param groupID: Group identifier.
        :type groupID: integer
        :returns: Deleted row ID.
        :rtype: integer
        """
        deleteQ = "DELETE FROM services WHERE groups = ?"
        self.instCursor.execute( deleteQ , ( groupID , ) )
        deletedService = self.instCursor.lastrowid

        deleteQ = "DELETE FROM inputs WHERE service = ?"
        self.instCursor.execute( deleteQ , ( deletedService , ) )
        deleteQ = "DELETE FROM outputs WHERE service = ?"
        self.instCursor.execute( deleteQ , ( deletedService , ) )

        deleteQ = "DELETE FROM mappings WHERE groups = ?"
        self.instCursor.execute( deleteQ , ( groupID , ) )

        selectQ = "SELECT valueTableName FROM runs WHERE groups = ?"
        self.instCursor.execute( selectQ , ( groupID , ) )
        tableName = self.instCursor.fetchone()
        rowid = self.instCursor.lastrowid

        if tableName != None:
            deleteQ = "DELETE FROM {} WHERE run_id = ?".format( tableName )
            self.instCursor.execute( deleteQ , ( rowid , ) )

        deleteQ = "DELETE FROM groups WHERE group_id = ?"
        self.instCursor.execute( deleteQ , ( groupID , ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


###################################################
###                                                ###
###              SERVICE SECTION                    ###
###                                                ###
###################################################


    #returns ID of inserted Service
    def createService( self , serviceName , ip , port , target , groupID ):
        """
        Creates a service as an entry in database

        :param serviceName: Name of service.
        :type serviceName: string
        :param ip: IP address of service.
        :type ip: string
        :param port: Port, service is listening on.
        :type port: string
        :param target: Either a path to a file or a specific address.
        :type target: string
        :returns: ID of created service.
        :rtype: integer
        """
        insertService = "INSERT INTO services ( service_name , ip , port , target , groups ) VALUES ( ?,?,?,?,? )"
        vals = ( serviceName , ip , port , target , groupID )
        self.instCursor.execute( insertService , vals )
        self.__inst_db.commit()
        return self.instCursor.lastrowid

    def retrieveServices( self , groupID ):
        """
        Retrieves services to given group id

        :param groupID: Group identifier.
        :type groupID: integer
        :returns: Services with contents.
        :rtype: dict
        :Example:

        .. code-block:: python

            [
                {
                  "id"       : <id_of_service> ,
                  "name"   : <name_of_service> ,
                  "ip"       : <ip_of_service> ,
                  "port"   : <port_of_service>,
                  "target" : <target_of_service> ,
                  "group"  : <id_of_group>
                } , { ... }
            ]

        """
        selectQ = "SELECT * FROM services WHERE groups =?"
        self.instCursor.execute( selectQ , ( groupID , ) )
        services = self.instCursor.fetchall()

        lServices = []
        for service in services:
            output = {}
            output[ u"id" ] = service[ 0 ]
            output[ u"name" ] = service[ 1 ]
            output[ u"ip" ] = service[ 2 ]
            output[ u"port" ] = service[ 3 ]
            output[ u"target" ] = service[ 4 ]
            output[ u"gid" ] = groupID
            lServices.append( output )

        return lServices

    def retrieveServicesDetailed( self , groupID ):
        """
        Retrieves services to given group id

        :param groupID: Group identifier.
        :type groupID: integer
        :returns: Services with contents.
        :rtype: dict
        :Example:

        .. code-block:: python

            [
                {
                  "id"       : <id_of_service> ,
                  "name"   : <name_of_service> ,
                  "ip"       : <ip_of_service> ,
                  "port"   : <port_of_service>,
                  "target" : <target_of_service> ,
                  "group"  : <id_of_group>
                } , { ... }
            ]

        """
        selectQ = "SELECT * FROM services WHERE groups =?"
        self.instCursor.execute( selectQ , ( groupID , ) )
        services = self.instCursor.fetchall()

        lServices = []
        for service in services:
            output = {}
            output[ u"id" ] = service[ 0 ]
            output[ u"name" ] = service[ 1 ]
            output[ u"ip" ] = service[ 2 ]
            output[ u"port" ] = service[ 3 ]
            output[ u"target" ] = service[ 4 ]
            output[ u"gid" ] = groupID
            output[ u"outputs" ] = self.retrieveOutputsOfService( service[ 0 ] )
            output[ u"inputs"] = self.retrieveInputsOfService( service[ 0 ] )
            lServices.append( output )

        return lServices


    def retrieveService( self , serviceID ):
        """
        Retrieves a single service

        :param serviceID: Service identifier.
        :type serviceID: integer
        :returns: Service with contents.
        :rtype: dict
        :Example:

        .. code-block:: python

            
            { 
                "id"     : <id_of_service> ,
                "name"   : <name_of_service> ,
                "ip"     : <ip_of_service> ,
                "port"   : <port_of_service> ,
                "target" : <target_of_service> ,
                "group"  : <group_of_service>
            }
            
        """
        selectQ = "SELECT * FROM services WHERE service_id =?"
        self.instCursor.execute( selectQ , ( serviceID , ) )
        services = self.instCursor.fetchone()
        output = {}
        output[ u"id" ] = services[ 0 ]
        output[ u"name" ] = services[ 1 ]
        output[ u"ip" ] = services[ 2 ]
        output[ u"port" ] = services[ 3 ]
        output[ u"target" ] = services[ 4 ]
        output[ u"group" ] = services[ 5 ]

        return output

    def retrieveInputsOfService( self , serviceID ):
        """
        Retrieves inputs of a service

        :param serviceID: Service identifier.
        :type serviceID: integer
        :returns: Inputs of a service.
        :rtype: dict
        :Example:

        .. code-block:: python

            [
                { "id"           : ___ , 
                  "name"         : ___ ,
                  "sid"          : ___ ,
                  "initialValue" : ___
                } ,
              { another input } ,
              [...]
            ]
        """
        selectQ = "SELECT * FROM inputs WHERE service = ?"
        self.instCursor.execute( selectQ , ( serviceID , ) )
        inputs = self.instCursor.fetchall()
        output = []

        for row in inputs:
            temp = {}
            temp[ u"id" ] = row[ 0 ]
            temp[ u"name" ] = row[ 1 ]
            temp[ u"sid" ] = row[ 2 ]
            temp[ u"initialValue" ] = row[ 3 ]
            output.append( temp )

        return output

    def retrieveOutputsOfService( self , serviceID ):
        """
        Retrieves outputs of a service

        :param serviceID: Service identifier.
        :type serviceID: integer
        :returns: All outputs of a service.
        :rtype: dict
        :Example:

        .. code-block:: python

            [ { "id" : <oid> , 
                "name" : <oname> , 
                "initialValue" : <ovalue>
                "serviceid" : <sid>
              } , { another output }
            ]

        """
        selectQ = "SELECT * FROM outputs WHERE service = ?"
        self.instCursor.execute( selectQ , ( serviceID , ) )
        outputs = self.instCursor.fetchall()
        output = []
        
        for row in outputs:
            outitem = {}
            outitem[ "id" ] = row[ 0 ]
            outitem[ "name" ] = row[ 1 ]
            outitem[ "sid" ] = row[ 2 ]
            outitem[ "initialValue" ] = row[ 3 ]
            output.append( outitem )
            
        return output
    

    def deleteService( self , serviceID ):
        """
        Deletes a service

        :param serviceID: Service identifier.
        :type serviceID: integer
        :returns: Id of deleted service.
        :rtype: integer

        """
        deleteQ = "DELETE FROM inputs WHERE service = ?"
        self.instCursor.execute( deleteQ , ( serviceID , ) )
        deleteQ = "DELETE FROM outputs WHERE service = ?"
        self.instCursor.execute( deleteQ , ( serviceID , ) )
        deleteQ = "DELETE FROM mappings WHERE serviceOfinput = ?"
        self.instCursor.execute( deleteQ , ( serviceID , ) )
        deleteQ = "DELETE FROM mappings WHERE serviceOfoutput = ?"
        self.instCursor.execute( deleteQ , ( serviceID , ) )
        deleteQ = "DELETE FROM services WHERE service_id = ?"
        self.instCursor.execute( deleteQ , ( serviceID , ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editServiceName( self , serviceID , newName ):
        """
        Edits the name of a service

        :param serviceID: Service identifier.
        :type serviceID: integer
        :param newName: New name of service.
        :type newName: string
        :returns: Id of edited service.
        :rtype: integer

        """

        editQ = "UPDATE services SET service_name = ? WHERE service_id = ? "

        self.instCursor.execute( editQ , ( newName , serviceID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid

    def editServiceIP( self , serviceID , newIP ):
        """
        Edits the IP of a service

        :param serviceID: Service identifier.
        :type serviceID: integer
        :param newIP: New ip of service.
        :type newIP: string
        :returns: Id of edited service.
        :rtype: integer

        """

        editQ = "UPDATE services SET ip = ? WHERE service_id = ? "

        self.instCursor.execute( editQ , ( newIP , serviceID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editServicePort( self , serviceID , newPort ):
        """
        Edits the port of a service

        :param serviceID: Service identifier.
        :type serviceID: integer
        :param newPort: New port of service.
        :type newPort: string
        :returns: Id of edited service.
        :rtype: integer

        """

        editQ = "UPDATE services SET port = ? WHERE service_id = ? "

        self.instCursor.execute( editQ , ( newPort , serviceID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editServiceTarget( self , serviceID , newTarget ):
        """
        Edits the target of a service

        :param serviceID: Service identifier.
        :type serviceID: integer
        :param newTarget: New target of service.
        :type newTarget: string
        :returns: Id of edited service.
        :rtype: integer

        """

        editQ = "UPDATE services SET target = ? WHERE service_id = ? "

        self.instCursor.execute( editQ , ( newTarget , serviceID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editServiceGroup( self , serviceID , newGroup ):
        """
        Edits the group reference of a service

        :param serviceID: Service identifier.
        :type serviceID: integer
        :param newGroup: New group reference of service.
        :type newGroup: string
        :returns: Id of edited service.
        :rtype: integer

        """

        editQ = "UPDATE services SET groups = ? WHERE service_id = ? "

        self.instCursor.execute( editQ , ( newGroup , serviceID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


###################################################
###                                             ###
###               RUN / Values SECTION          ###
###                                             ###
###################################################

    def createRun( self , tableName , groupID ):
        """
        Creates a run as an entry in database

        :param tableName: Name of table to log values of run.
        :type tableName: string
        :param groupID: Reference to group the run belongs to.
        :type groupID: integer
        :returns: Id of created run.
        :rtype: integer

        """
        lVars = []

        getServicesQ = "SELECT * FROM services WHERE groups =?"
        self.instCursor.execute( getServicesQ , ( groupID, ) )
        services = self.instCursor.fetchall()

        for service in services:
            getInputsOfServiceQ = "SELECT * FROM inputs WHERE service =?"
            self.instCursor.execute( getInputsOfServiceQ , ( service[ 0 ] , ) )
            inputs = self.instCursor.fetchall()
            for iitem in inputs:
                lVars.append(service[ 1 ] + "_inputs_" + re.sub( r'\W+' , '' , iitem[ 1 ] ) )

            getInputsOfServiceQ = "SELECT * FROM outputs WHERE service =?"
            self.instCursor.execute( getInputsOfServiceQ , ( service[ 0 ] , ) )
            outputs = self.instCursor.fetchall()
            for oitem in outputs:
                lVars.append(service[ 1 ] + "_outputs_" + re.sub( r'\W+' , '' , oitem[ 1 ] ) )


        insertQ = "INSERT INTO runs ( valueTableName, groups) VALUES ( ? , ?)"
        self.instCursor.execute( insertQ , ( tableName, groupID ) )
        
        createQuery = "CREATE TABLE {}( values_id INTEGER PRIMARY KEY , run_id INTEGER , timestamp REAL, ".format( tableName )

        for name in lVars:
            createQuery += name + " real" + ", "

        createQuery += "FOREIGN KEY( run_id ) REFERENCES runs( run_id ) ON DELETE CASCADE );"
                
        self.instCursor.execute( createQuery )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def retrieveTableName( self, runID ):
        """
        Retrieves table name of a run

        :param runID: Run identifier.
        :type runID: integer
        :returns: Name of table of given run id
        :rtype: String.

        """

        getTableNameQ = "SELECT valueTableName FROM runs WHERE run_id = ?"
        self.instCursor.execute( getTableNameQ , ( runID ,  ) )

        tname = self.instCursor.fetchone()

        return tname

    def retrieveTableKeys( self , tableName ):
        """
        Retrieves coloumn keys of a table

        :param tableName: Name of table.
        :type tableName: string
        :returns: list of coloumn keys
        :rtype: list
       

        """

        getTableKeysQ = "PRAGMA table_info({})".format(tableName)
        self.instCursor.execute( getTableKeysQ )

        tkeys = self.instCursor.fetchall()

        tkeysOut = []
        
        for key in tkeys:
            tkeysOut.append(key[1])
            
        return tkeysOut
    
    def retrieveRuns( self , groupID ):
        """

        Retrieves runs of a group

        :param groupID: Group identifier.
        :type groupID: integer
        :returns: Runs of a group.
        :rtype: list

        """

        getRunsQ = "SELECT * FROM runs WHERE groups = ?"
        self.instCursor.execute( getRunsQ , ( groupID , ) )
        rows = self.instCursor.fetchall()

        runs = []

        for row in rows:
            run = {}
            run[ u"id" ] = row[ 0 ]
            run[ u"tableName"] = row[ 1 ]
            run[ u"gid" ] = row[ 2 ]
            runs.append( run )

        return runs



    def editRunTableName( self , runID , tableName ):
        """
        Edits the table name where values of runs are logged.

        :param runID: Run identifier.
        :type runID: integer
        :param tableName: New name of table.
        :type tableName: string
        :returns: Id of edited run.
        :rtype: integer

        """

        getNameQ = "SELECT valueTableName FROM runs WHERE run_id = ?"
        self.instCursor.execute( getNameQ , ( runID , ) )

        tname = self.instCursor.fetchone()

        updateNameQ = "UPDATE runs SET valueTableName = '{}' WHERE run_id = ?".format( tableName )
        self.instCursor.execute( updateNameQ , ( runID , ) )
        

        alterTableQ = "ALTER TABLE {} RENAME TO {}".format( tname[ 0 ] , tableName )

        self.instCursor.execute( alterTableQ )
        self.__inst_db.commit()
        return self.instCursor.lastrowid

    def editRunGroupRef( self , runID , newGroupID ):
        """
        Edits the group references of a run.

        :param runID: Run identifier.
        :type runID: integer
        :param newGroupID: New reference of group.
        :type newGroupID: integer
        :returns: Id of edited run.
        :rtype: integer

        """

        alterRunQ = "UPDATE runs SET groups = ? WHERE run_id = ?"

        self.instCursor.execute( alterRunQ , ( newGroupID , runID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid

    def deleteRun( self , runID ):
        """
        Deletes run and corresponding configuration and table of logged values.

        :param runID: Run identifier.
        :type runID: integer
        :returns: Id of deleted run.
        :rtype: integer

        """

        getValuesQ = "SELECT valueTableName FROM runs WHERE run_id = ? "
        self.instCursor.execute( getValuesQ , ( runID , )  )
        tableName = self.instCursor.fetchone()[ 0 ]

        deleteValueTableQ = "DROP TABLE {}".format( tableName )
        self.instCursor.execute( deleteValueTableQ )

        deleteConfigQ = "DELETE FROM simconfigs WHERE run_id = ?"
        self.instCursor.execute( deleteConfigQ , ( runID , ) )

        deleteRunQ = "DELETE FROM runs WHERE run_id = ?"
        self.instCursor.execute( deleteRunQ , ( runID , ) )
        self.__inst_db.commit()
        
        return self.instCursor.lastrowid



    def deleteValueTable( self , runID ):
        """
        Deletes(completely dropping) table of values of a run

        :param runID: Run identifier.
        :type runID: integer
        :returns: Name of deleted table.
        :rtype: string

        """

        selectTableQ = "SELECT valueTableName FROM runs WHERE run_id = ?"
        self.instCursor.execute( selectTableQ , ( runID,  ) )
        tableName = self.instCursor.fetchone()[ 0 ]

        deleteTableQ = "DROP TABLE {}".format( tableName )
        self.instCursor.execute( deleteTableQ )
        self.__inst_db.commit()
        out = "Table {} deleted. ".format( tableName )

        return out



    def insertValues( self , runID , coloumns , values ):
        """
        Writes values to database.

        :param runID: Run identifier.
        :type runID: integer
        :param timestamp: Timestamp of valueset.
        :type timestamp: float
        :param lVarIn: List of input values.
        :type lVarIn: list
        :param lVarOut: List of output values.
        :type lVarOut: list
        :returns: Id of inserted values.
        :rtype: integer

        """
        selectTab = "SELECT valueTableName FROM runs WHERE run_id = ?"
        self.instCursor.execute(selectTab, ( runID, ) )
        tableName = self.instCursor.fetchone()

        insertQ = "INSERT INTO {}{} VALUES {}".format( tableName[0] , coloumns , values )
        self.instCursor.execute( insertQ )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def retrieveValues( self , runID ):
        """
        Retrieves all values logged of a run

        :param runID: Run identifier.
        :type runID: integer
        :returns: list of tuples of values ( id , ValueOfVar1 , ValueOfVar2 , [ ... ] )
        :rtype: list

        """
        selectQ = "SELECT valueTableName FROM runs WHERE run_id = ?"
        self.instCursor.execute(selectQ, ( runID, ) )

        name = self.instCursor.fetchone()

        selectQ = "SELECT * FROM {} ".format( name[ 0 ] )
        self.instCursor.execute( selectQ )
        out = self.instCursor.fetchall()

        return out

    def deleteValues( self , tableName , valuesID ):
        """
        Deletes single value row from log

        :param tableName: Name of table with logs.
        :type tableName: string
        :param valuesID: Value identifier.
        :type valuesID: integer
        :returns: Id of deleted row.
        :rtype: integer

        """
        deleteQ = "DELETE FROM {} WHERE values_id = ?".format( tableName )
        self.instCursor.execute( deleteQ , ( valuesID , ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


###################################################
###                                                ###
###         SIMULATION CONFIGURATION SECTION        ###
###                                                ###
###################################################

    #returns id of inserted row
    def setSimConfig( self , runID , start_time , end_time , stepsize ):
        """
        Sets the configuration of a run.

        :param runID: Run identifier.
        :type runID: integer
        :param start_time: Start time.
        :type start_time: integer
        :param end_time: End time.
        :type end_time: integer
        :param stepsize: Stepsize of timeinterval.
        :type stepsize: integer
        :returns: Id of set configuration
        :rtype: integer

        """
        insertQuery = "INSERT INTO simconfigs ( run_id , start_time , end_time , stepsize ) VALUES ( ? , ? , ? , ? )"
        vals = ()
        vals += ( runID , start_time , end_time , stepsize )
        self.instCursor.execute( insertQuery , vals )
        self.__inst_db.commit()
        return self.instCursor.lastrowid

    def retrieveConfig( self , runID ):
        """
        Retrieves configuration of corresponding run.

        :param runID: Run identifier.
        :type runID: integer
        :returns: Configuration of run.
        :rtype: dict
        :Example:

        .. code-block:: python

            { "id"           : id_of_config , 
              "run_id"       : id_of_run_ref , 
              "start_time" : starting_time , 
              "end_time"   : end_time , 
              "stepsize"   : size_of_timesteps 
            }

        """
        getRunQ ="SELECT * FROM simconfigs WHERE run_id = ?"
        self.instCursor.execute( getRunQ , ( runID ,  ) )
        configs = self.instCursor.fetchall()
        out = {}
        out[ "id" ] = configs[ 0 ][ 0 ]
        out[ "run_id" ] = configs[ 0 ][ 1 ]
        out[ "start_time" ] = configs[ 0 ][ 2 ]
        out[ "end_time" ] = configs[ 0 ][ 3 ]
        out[ "stepsize" ] = configs[ 0 ][ 4 ]

        return out


    def editConfig( self , cid , runID , start_time , end_time , stepsize ):
        """
        Edits the configuration of a run.

        :param id: config identifier.
        :type rid: integer
        :param runID: Run identifier.
        :type runID: integer
        :param start_time: Start time.
        :type start_time: integer
        :param end_time: End time.
        :type end_time: integer
        :param stepsize: Stepsize of timeinterval.
        :type stepsize: integer
        :returns: Id of set configuration
        :rtype: integer

        """
        editQuery = "UPDATE simconfigs SET run_id = ? , start_time = ? , end_time = ? , stepsize = ? WHERE config_id = ?"
        self.instCursor.execute( editQuery , ( runID , start_time , end_time , stepsize , cid) )
        self.__inst_db.commit()
        
        return self.instCursor.lastrowid

    def retrieveConfigsOfGroup( self , groupID ):
        """
        Retrieves all corresponding configurations of a group.

        :param groupID: Group identifier.
        :type groupID: integer

        :returns: a list of configurations
        :rtype: list

        :Example:

        .. code-block:: python

            [
                {
                    "config_id" : <idOfconfig> ,
                    "run_id"      : <idOfrun> ,
                    "start_time": <starttime> ,
                    "end_time"    : <endtime> ,
                    "step_size" : <stepsize>
                } ,
                {
                    another config
                } ,

                [ ... ]
            ]

        """
        configs = []
        selectRunsQ = "SELECT run_id FROM runs WHERE groups = ?"
        self.instCursor.execute( selectRunsQ , ( groupID , ) )
        runs = self.instCursor.fetchall()

        for run in runs:
            selectConfigQ = "SELECT * FROM simconfigs WHERE run_id = ?"
            self.instCursor.execute( selectConfigQ , ( run[ 0 ] , ) )
            row = self.instCursor.fetchone()
            if row != None:
                config = {}
                config[ "id" ] = row[ 0 ]
                config[ "rid" ] = row[ 1 ]
                config[ "startTime" ] = row[ 2 ]
                config[ "endTime" ] = row[ 3 ]
                config[ "stepSize" ] = row[ 4 ]
                configs.append( config )
            

        return configs


    def deleteConfig( self , configID ):
        """
        Deletes a configuration

        :param configID: Simulation configuration identifier.
        :type configID: integer
        :returns: Id of deleted config.
        :rtype: integer

        """
        deleteQ = "DELETE FROM simconfigs WHERE config_id = ?"
        self.instCursor.execute( deleteQ , ( configID , ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editStartTime( self , runID , configID , newStartTime ):
        """
        Edits the starting time of the configuration.

        :param runID: Run identifier.
        :type runID: integer
        :param configID: Configuration identifier.
        :type configID: integer
        :param newStartTime: New starting time.
        :type newStartTime: integer
        :returns: Id of edited configuration.
        :rtype: integer

        """
        alterConfigQ = "UPDATE simconfigs SET start_time = ? WHERE config_id = ? AND run_id = ?"

        self.instCursor.execute( alterConfigQ , ( newStartTime , configID , runID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editEndTime( self , runID , configID , newEndTime ):
        """
        Edits the ending time of the configuration.

        :param runID: Run identifier.
        :type runID: integer
        :param configID: Configuration identifier.
        :type configID: integer
        :param newEndTime: New starting time.
        :type newEndTime: integer
        :returns: Id of edited configuration.
        :rtype: integer

        """
        alterConfigQ = "UPDATE simconfigs SET end_time = ? WHERE config_id = ? AND run_id = ?"

        self.instCursor.execute( alterConfigQ , ( newEndTime , configID , runID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editStepSize( self , runID , configID , newStepSize ):
        """
        Edits the stepsize time of the configuration.

        :param runID: Run identifier.
        :type runID: integer
        :param configID: Configuration identifier.
        :type configID: integer
        :param newStartTime: New starting time.
        :type newStartTime: integer
        :returns: Id of edited configuration.
        :rtype: integer

        """
        alterConfigQ = "UPDATE simconfigs SET stepsize = ? WHERE config_id = ? AND run_id = ?"

        self.instCursor.execute( alterConfigQ , ( newStepSize , configID , runID  ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid

###################################################
###                                                ###
###               MAPPING SECTION                    ###
###                                                ###
###################################################


    def createMapping( self , mapping ):
        """
        Sets a mapping of output to input of a group.

        :param mapping: Output to Input mapping.
        :type mapping: dict
        :returns: List of IDs of mappings set.
        :rtype: list of int

        """
        gid = mapping[ u"gid" ]
        soid = mapping[ u"soid" ]
        oid = mapping[ u"oid" ]
        siid = mapping[ u"siid" ]
        iid = mapping[ u"iid" ]

        insertMap = "INSERT INTO mappings ( groups , input , serviceOfinput , output , serviceOfoutput ) VALUES ( ? , ? , ? , ? , ? )"

        self.instCursor.execute( insertMap , ( gid , iid , siid , oid , soid  ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editMapping( self , mapping):
        """
        Edits a mapping.

        :param mapping: Mapping of output to input
        :typer mapping: integer
        :returns: id of edited mapping.
        :rtype: list of int

        """
        mid = mapping[ u"id" ]
        gid = mapping[ u"gid" ]
        soid = mapping[ u"soid" ]
        oid = mapping[ u"oid" ]
        siid = mapping[ u"siid" ]
        iid = mapping[ u"iid" ]

        updateMappingQ = "UPDATE mappings SET groups = ? , input = ? , serviceOfinput = ? , output = ? , serviceOfoutput = ? WHERE map_id = ? "

        self.instCursor.execute( updateMappingQ , ( gid , iid , siid , oid , soid , mid ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid



    def retrieveMap( self , mapID ):
        """
        Retrieves a single row of mapping.

        :param mapID: Mapping identifier.
        :type mapID: integer
        :returns: Mapping item as dict
        :rtype: dict
        :Example:

        .. code-block:: python

            { "id" : <id_of_map> ,
              "gid" : <id_of_group> ,
              "iid" : <id_of_input> ,
              "siid" : <id_of_service> ,
              "oid" : <id_of_output> ,
              "soid" : <id_of_service>
            }

        """
        getMapQ = "SELECT * FROM mappings WHERER map_id =?"
        self.instCursor.execute( getMapQ , ( mapID , ) )
        mapping = self.instCursor.fetchone()

        out = {}
        out[ "id" ] = mapping[ 0 ]
        out[ "gid" ] = mapping[ 1 ]
        out[ "iid" ] = mapping[ 2 ]
        out[ "siid" ] = mapping[ 3 ]
        out[ "oid" ] = mapping[ 4 ]
        out[ "soid" ] = mapping[ 5 ]

        return out



    def retrieveMappings( self , groupID ) :
        """
        retrieves mappings of a group.

        :param groupID: Groupd identifier.
        :type groupID: integer
        :returns: All mappings of a group
        :rtype: list
        :Example:

        .. code-block:: python

            [ { "id"     : <mapping_id> ,
                "gid"     : <group_id> ,
                "iid"     : <input_id> ,
                "siid"     : <service_input_id> ,
                "oid"     : <output_id> ,
                "soid"     : <service_output_id>
              } ,
              { "id"     : <mapping_id> ,
                "gid"     : <group_id> ,
                "iid"     : <input_id> ,
                "siid"     : <service_input_id> ,
                "oid"     : <output_id> ,
                "soid"     : <service_output_id>
              }
            ]

        """
        selectQ = "SELECT * FROM mappings WHERE groups = ?"
        self.instCursor.execute( selectQ , ( groupID , ) )
        maps = self.instCursor.fetchall()
        output = []

        for row in maps:
            lObject = {}
            lObject[ u"id" ] = row[ 0 ]
            lObject[ u"gid" ] = groupID
            lObject[ u"iid"] = row[ 2 ]
            lObject[ u"siid" ] = row[ 3 ]
            lObject[ u"oid" ] = row[ 4 ]
            lObject[ u"soid"] = row[ 5 ]
            output.append( lObject )


        return output


    def deleteMapping( self , mapID ):
        """
        Deletes a row of mapping

        :param mapID: Mapping identifier.
        :type mapID: Integer
        :returns: Id of last deleted row.
        :rtype: Integer.
        """
        deleteQ = "DELETE FROM mappings WHERE map_id = ?"
        self.instCursor.execute( deleteQ , ( mapID , ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def deleteMappingOfGroup( self , groupID ):
        """
        Deletes mapping of a group

        :param groupID: Mapping identifier.
        :type groupID: Integer
        :returns: Id of deleted rows.
        :rtype: Integer.
        """
        deleteQ = "DELETE FROM mappings WHERE groups = ?"
        self.instCursor.execute( deleteQ , ( groupID , ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editGroupOfMap( self , mapID , newGroupID ):
        """
        Edits group reference of map

        :param mapID: Mapping identifier.
        :type mapID: Integer
        :param newGroupID: Group identifier.
        :type newGroupID: Integer
        :returns: Id of edited row.
        :rtype: Integer.
        """

        editGroupQ = "UPDATE maps SET groups = ? WHERE map_id = ?"

        self.instCursor.execute( editGroupQ , ( newGroupID , mapID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editInputOfMap( self , mapID , newInputID ):
        """
        Edits input reference of map

        :param mapID: Mapping identifier.
        :type mapID: Integer
        :param newInputID: Input identifier.
        :type newInputID: Integer
        :returns: Id of edited row.
        :rtype: Integer.
        """
        editInputQ = "UPDATE maps SET input = ? WHERE map_id = ?"

        self.instCursor.execute( editInputQ , ( newInputID , mapID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editOutputOfMap( self , mapID , newOutputID ):
        """
        Edits output reference of map

        :param mapID: Mapping identifier.
        :type mapID: Integer
        :param newOutputID: Input identifier.
        :type newOutputID: Integer
        :returns: Id of edited row.
        :rtype: Integer.

        """
        editOutputQ = "UPDATE maps SET output = ? WHERE map_id = ?"

        self.instCursor.execute( editOutputQ , ( newOutputID , mapID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editInputServiceOfMap( self , mapID , newInputServiceID ):
        """
        Edits input's service reference of map

        :param mapID: Mapping identifier.
        :type mapID: Integer
        :param newInputServiceID: Input's Service identifier.
        :type newInputServiceID: Integer
        :returns: Id of edited row.
        :rtype: Integer.
        """
        editInputServiceQ = "UPDATE maps SET serviceOfinput = ? WHERE map_id = ?"

        self.instCursor.execute( editInputServiceQ , ( newInputServiceID , mapID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editOutputServiceOfMap( self , mapID , newOutputServiceID ):
        """
        Edits output's service reference of map

        :param mapID: Mapping identifier.
        :type mapID: Integer
        :param newOutputServiceID: Input's Service identifier.
        :type newOutputServiceID: Integer
        :returns: Id of edited row.
        :rtype: Integer.
        """
        editOutputServiceQ = """UPDATE maps SET serviceOfoutput = ? WHERE map_id = ?"""

        self.instCursor.execute( editOutputServiceQ , ( newOutputServiceID , mapID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


###################################################
###                                                ###
###               INPUT SECTION                    ###
###                                                ###
###################################################


    #returns ID of inserted Input
    def createInput( self , serviceID , varName , initialVal ):
        """
        Creates input as an entry in database

        :param serviceID: Service identifier.
        :type serviceID: integer
        :param varName: Name of input.
        :type varName: string
        :param initialVal: The initial value of the input
        :type initialVal: float
        :returns: Id of created row
        :rtype: integer
        """
        insertIn = "INSERT INTO inputs ( variable_name , service , initial_Value ) VALUES ( ? , ? , ? )"
        vals = ( varName , serviceID , initialVal )
        self.instCursor.execute( insertIn , vals )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def retrieveInput( self , inputID ):
        """
        Retrieves input

        :param inputID: Input identifier
        :type inputID: integer
        :returns: input as a dict object
        :rtype: dict
        :Example:

        .. code-block:: python

            { "id"             : id_of_service ,
              "inputName"      : name_of_input ,
              "serviceOfinput" : id_of_service ,
              "initial_value"  : float_value
            }
        """
        getInputQ = "SELECT * FROM inputs WHERE input_id = ?"
        self.instCursor.execute( getInputQ , ( inputID , ) )
        inputRow = self.instCursor.fetchone()

        """
         ##### CODE IF NAME OF SERVICE IS WANTED INSTEAD OF ID #####

         getServiceQ = "SELECT * FROM services WHERE service_id = ?"
         self.instCursor.execute( getServiceQ , ( inputRow[ 2 ] , ) )
         service = self.instCursor.fetchone()
         nameOfservice = service[ 1 ]

        """

        output = {}
        output[ u"id" ] = inputRow[ 0 ]
        output[ u"name" ] = inputRow[ 1 ]
        output[ u"sid" ] = inputRow[ 2 ]
        output[ u"initialValue" ] = inputRow[ 3 ]

        return output


    def retrieveInputs( self ):
        """
        Retrieves inputs

        
        :returns: inputs as a list object
        :rtype: list
        :Example:

        .. code-block:: python

           [ { "id"              : id_of_input ,
              "name"      : name_of_input ,
              "sid" : id_of_service ,
              "initialValue"   : float_value
            }, { another input } , ... 
            ]
        """
        getInputQ = "SELECT * FROM inputs"
        self.instCursor.execute( getInputQ )
        inputRows = self.instCursor.fetchall()

        inputs = []
        
        for row in inputRows:
            inputObj = {}
            inputObj[ u"id" ] = row[ 0 ]
            inputObj[ u"name" ] = row[ 1 ]
            inputObj[ u"sid" ] = row[ 2 ] 
            inputObj[ u"initialValue" ] = row[ 3 ]
            inputs.append(inputObj)

        return inputs

    def deleteInput( self , inputID ):
        """
        Deletes input.

        :param inputID: Input identifier.
        :type inputID: integer
        :returns: Id of deleted row.
        :rtype: integer

        """
        deleteQ = "DELETE FROM mappings WHERE input = ?"
        self.instCursor.execute( deleteQ , ( inputID , ) )

        deleteQ = "DELETE FROM inputs WHERE input_id = ?"
        self.instCursor.execute( deleteQ , ( inputID , ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editNameOfInput( self , inputID , newName ):
        """
        Edits name of input

        :param inputID: Input identifier
        :type inputID: integer
        :param newName: New name of input
        :type newName: string
        :returns: Id of row edited
        :rtype: integer
        """

        editNameQ = "UPDATE inputs SET variable_name = ? WHERE input_id = ?"

        self.instCursor.execute( editNameQ , ( newName , inputID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editServiceOfInput( self , inputID , newServiceID ):
        """
        Edits service reference of input

        :param inputID: Input identifier
        :type inputID: integer
        :param newServiceID: New service reference of input
        :type newServiceID: integer
        :returns: Id of row edited
        :rtype: integer
        """

        editServiceQ = "UPDATE inputs SET service = ? WHERE input_id = ?"

        self.instCursor.execute( editServiceQ , ( newServiceID , inputID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editInitValueOfInput( self , inputID , newVal ):
        """
        Edits initial value of input

        :param inputID: Input identifier
        :type inputID: integer
        :param newVal: New initial value of input
        :type newVal: float
        :returns: Id of row edited
        :rtype: integer
        """

        editQ = "UPDATE inputs SET initial_value = ? WHERE input_id = ?"

        self.instCursor.execute( editQ , ( newVal , inputID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


###################################################
###                                                ###
###               OUTPUT SECTION                    ###
###                                                ###
###################################################


    #returns ID of inserted Output
    def createOutput( self , serviceID , varName , initialVal ):
        """
        Creates output as an entry in database

        :param serviceID: Service identifier.
        :type serviceID: integer
        :param varName: Name of output.
        :type varName: string
        :param initialVal: The initial value of the output
        :type initialVal: float
        :returns: Id of created row
        :rtype: integer
        """
        insertOut = "INSERT INTO outputs ( variable_name , service , initial_Value ) VALUES ( ? , ? , ? )"
        vals = ( varName , serviceID , initialVal )
        self.instCursor.execute( insertOut , vals )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def retrieveOutput( self , outputID ):
        """
        Retrieves output

        :param outputID: Output identifier
        :type outputID: integer
        :returns: output as a dict object
        :rtype: dict
        :Example:

        .. code-block:: python

            { "id"              : id_of_service ,
              "outputName"      : name_of_output ,
              "serviceOfoutput" : id_of_service ,
              "initial_value"   : float_value
            }
        """
        getOutputQ = "SELECT * FROM outputs WHERE output_id = ?"
        self.instCursor.execute( getOutputQ , ( outputID , ) )
        outputRow = self.instCursor.fetchone()


        ##### CODE IF NAME OF SERVICE IS WANTED INSTEAD OF ID #####

        #getServiceQ = "SELECT * FROM services WHERE service_id = ?"
        #self.instCursor.execute( getServiceQ , ( inputRow[ 2 ] , ) )
        #service = self.instCursor.fetchone()
        #nameOfservice = service[ 1 ]


        output = {}
        output[ u"id" ] = outputRow[ 0 ]
        output[ u"name" ] = outputRow[ 1 ]
        output[ u"sid" ] = outputRow[ 2 ] # CHANGE outputRow[ 2 ] to nameOfservice
        output[ u"initialValue" ] = outputRow[ 3 ]

        return output


    def retrieveOutputs( self ):
        """
        Retrieves outputs

        
        :returns: output as a list object
        :rtype: list
        :Example:

        .. code-block:: python

           [ { "id"              : id_of_service ,
              "name"      : name_of_output ,
              "sid" : id_of_service ,
              "initialValue"   : float_value
            }, { another Output } , ... 
            ]
        """
        getOutputQ = "SELECT * FROM outputs"
        self.instCursor.execute( getOutputQ )
        outputRows = self.instCursor.fetchall()

        outputs = []
        
        for row in outputRows:
            output = {}
            output[ u"id" ] = row[ 0 ]
            output[ u"name" ] = row[ 1 ]
            output[ u"sid" ] = row[ 2 ] 
            output[ u"initialValue" ] = row[ 3 ]
            outputs.append(output)

        return outputs

    def deleteOutput( self , outputID ):
        """
        Deletes output.

        :param outputID: Output identifier.
        :type outputID: integer
        :returns: Id of deleted row.
        :rtype: integer
        """
        deleteQ = "DELETE FROM mappings WHERE output = ?"
        self.instCursor.execute( deleteQ , ( outputID , ) )
        deleteQ = "DELETE FROM outputs WHERE output_id = ?"
        self.instCursor.execute( deleteQ , ( outputID , ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editNameOfOutput( self , outputID , newName ):
        """
        Edits name of output

        :param outputID: Output identifier
        :type outputID: integer
        :param newName: New name of output
        :type newName: string
        :returns: Id of row edited
        :rtype: integer

        """

        editNameQ = "UPDATE outputs SET variable_name = ? WHERE output_id = ?"

        self.instCursor.execute( editNameQ , ( newName , outputID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid


    def editServiceOfOutput( self , outputID , newServiceID ):
        """
        Edits service reference of output

        :param outputID: Output identifier
        :type outputID: integer
        :param newServiceID: New service reference of output
        :type newServiceID: integer
        :returns: Id of row edited
        :rtype: integer
        """

        editServiceQ = """UPDATE outputs SET service = ? WHERE output_id = ?"""

        self.instCursor.execute( editServiceQ , ( newServiceID , outputID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid

    def editInitValueOfOutput( self , outputID , newVal ):
        """
        Edits initial value of output

        :param outputID: Output identifier
        :type outputID: integer
        :param newVal: New initial value of output
        :type newVal: float
        :returns: Id of row edited
        :rtype: integer
        """

        editQ = "UPDATE outputs SET initial_value = ? WHERE output_id = ?"

        self.instCursor.execute( editQ , ( newVal , outputID ) )
        self.__inst_db.commit()
        return self.instCursor.lastrowid