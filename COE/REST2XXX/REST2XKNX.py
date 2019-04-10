# -*- coding: utf-8 -*-
"""
Created on Fri Aug  3 13:02:08 2018

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
from xknx import XKNX # version 0.8.5
from aiohttp import web #version 3.3.2
import asyncio #version 3.4.3
from xknx.devices import Light

light = None
my_loop = asyncio.get_event_loop()
xknx = None
#http://127.0.0.1:8082/api/v1.0/XKNX/initializeXKNX
async def initializeXKNX(request):
    #xknx = XKNX()
    #await xknx.start()
    print('XKNX device successfully started.')
    return web.json_response({'Status':'OK'}, status = 200)

#http://127.0.0.1:8082/api/v1.0/XKNX/addLightDevice?name='TestLight'&gas='1/0/9'    
async def addLightDevice(request):
    light_name = request.rel_url.query['name']
    light_gas = request.rel_url.query['gas']
    
    #light = Light(xknx,
    #              name = light_name,
    #              group_address_switch = light_gas)
    
    return web.json_response({'Status':'Light added.', 'Light Name' : light_name, 'Group Address Switch' : light_gas}, status = 200)

#http://127.0.0.1:8082/api/v1.0/XKNX/switchLightOn
async def switchLightOn(request):
    #await light.set_on()
    return web.json_response({'Status':'Light turned on.'}, status = 200)

#http://127.0.0.1:8082/api/v1.0/XKNX/switchLightOff
async def switchLightOff(request):
    #await light.set_off()
    return web.json_response({'Status':'Light turned off.'}, status = 200)
    
#http://127.0.0.1:8082/api/v1.0/XKNX/shutdownXKNX
async def shutdownXKNX(request):
    #await xknx.stop()
    return web.json_response({'Status':'XKNX device stopped.'}, status = 200)
    
app_xknx= web.Application() 
app_xknx.add_routes([web.get('/api/v1.0/XKNX/initializeXKNX', initializeXKNX)])
app_xknx.add_routes([web.get('/api/v1.0/XKNX/addLightDevice', addLightDevice)])
app_xknx.add_routes([web.get('/api/v1.0/XKNX/switchLightOn', switchLightOn)])
app_xknx.add_routes([web.get('/api/v1.0/XKNX/switchLightOff', switchLightOff)])
app_xknx.add_routes([web.get('/api/v1.0/XKNX/shutdownXKNX', shutdownXKNX)])


web.run_app(app_xknx, port = 8080)