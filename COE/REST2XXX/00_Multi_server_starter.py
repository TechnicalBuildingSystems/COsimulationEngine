# -*- coding: utf-8 -*-
"""
Created on Mon Aug  6 12:51:03 2018

@author: viho

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

import asyncio
import sys
from REST_ADS_AIO import app_ads
from task1 import app_task1
from task2 import app_task2
#from XKNX_Rest_AIOHTTP import app_xknx
from REST2FMI_AIO import app_fmi
from rest_fmi_ahu import app_ahu
from rest_fmi_ctrl import app_ctrl

def start():
    try:
        loop = asyncio.get_event_loop()
        
        
        ### ### ### ### ### ### ### ###
        # Application "ADS" on port 8080
        # app1 = app_ads
        # handler1 = app1.make_handler()
        # coroutine1 = loop.create_server(handler1, '127.0.0.1', 8080)
        # server1 = loop.run_until_complete(coroutine1)
        # address1, port1 = server1.sockets[0].getsockname()
        # print('ADS_APP started on http://{}:{}'.format(address1, port1))
        
        ### ### ### ### ### ### ### ###
        #Application "TASK1" on port 8081
        app2 = app_ctrl
        handler2 = app2.make_handler()
        coroutine2 = loop.create_server(handler2, '127.0.0.1', 8080)
        server2 = loop.run_until_complete(coroutine2)
        address2, port2 = server2.sockets[0].getsockname()
        print('CTRL_APP started on http://{}:{}'.format(address2, port2))

        ### ### ### ### ### ### ### ###
        # Application "XKNX" on port 8082       
        # app3 = app_xknx
        # handler3 = app3.make_handler()
        # coroutine3 = loop.create_server(handler3, '127.0.0.1', 8082)
        # server3 = loop.run_until_complete(coroutine3)
        # address3, port3 = server3.sockets[0].getsockname()
        # print('XKNX_APP started on http://{}:{}'.format(address3, port3))
        
        ### ### ### ### ### ### ### ###
        # Application "FMI" on port 8083      
        # app4 = app_fmi
        # handler4 = app4.make_handler()
        # coroutine4 = loop.create_server(handler4, '127.0.0.1', 8083)
        # server4 = loop.run_until_complete(coroutine4)
        # address4, port4 = server4.sockets[0].getsockname()
        # print('FMI_APP started on http://{}:{}'.format(address4, port4))
        
		### ### ### ### ### ### ### ###
        #Application "TASK2" on port 8081
        app4 = app_ahu
        handler4 = app4.make_handler()
        coroutine4 = loop.create_server(handler4, '127.0.0.1', 8083)
        server4 = loop.run_until_complete(coroutine4)
        address4, port4 = server4.sockets[0].getsockname()
        print('AHU_APP started on http://{}:{}'.format(address4, port4))
        
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            ### ### ### ### ### ### ### ###
            # Close all apps
            # server1.close()
            # loop.run_until_complete(app1.shutdown())
            # loop.run_until_complete(handler1.shutdown(60.0))
            # loop.run_until_complete(handler1.finish_connections(1.0))
            # loop.run_until_complete(app1.cleanup())

            server2.close()
            loop.run_until_complete(app2.shutdown())
            loop.run_until_complete(handler2.shutdown(60.0))
            loop.run_until_complete(handler2.finish_connections(1.0))
            loop.run_until_complete(app2.cleanup())
                        
            # server3.close()
            # loop.run_until_complete(app3.shutdown())
            # loop.run_until_complete(handler3.shutdown(60.0))
            # loop.run_until_complete(handler3.finish_connections(1.0))
            # loop.run_until_complete(app3.cleanup())
            
            server4.close()
            loop.run_until_complete(app4.shutdown())
            loop.run_until_complete(handler4.shutdown(60.0))
            loop.run_until_complete(handler4.finish_connections(1.0))
            loop.run_until_complete(app4.cleanup())
            
        loop.close()
    except Exception as e:
        sys.stderr.write('Error: ' + format(str(e)) + "\n")
        sys.exit(1)

if __name__ == '__main__':
    start()
    

