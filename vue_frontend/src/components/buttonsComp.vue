<template>
    <div id="buttonsComp">
        <div class="btn-group btn-group-justified">
            <div class="btn-group">
                <button type="button" v-on:click="getGroups(); getServices(); getOutputs(); getInputs()" class="btn btn-success" data-toggle="modal" data-target="#addModal" v-bind:disabled="selectedComp == 'csm'">Add</button>
            </div>
            <div class="btn-group">
                <button type="button" v-on:click="getGroups(); getServices(); getOutputs(); getInputs()" class="btn btn-secondary" data-toggle="modal" data-target="#editModal" v-bind:disabled="selectedComp == 'csm'">Edit</button>
            </div>
            <div class="btn-group">
                <button type="button" class="btn btn-danger" data-toggle="modal" data-target="#deleteModal" v-bind:disabled="selectedComp == 'csm'">Delete</button>
            </div>
            <div class="btn-group">
                <button type="button" v-on:click="refreshAll()" class="btn" v-bind:disabled="selectedComp == 'csm'">Refresh</button>
            </div>
        </div>


        <!-- Add Modal -->
        <div class="modal fade" id="addModal" tabindex="-1" role="dialog" aria-labelledby="addButtonModalCenterTitle" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered" role="document" >
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Add {{ selectedComp }}</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='service'">
                        <form>
                            <div class="form-group">
                                <label for="serviceName">Name</label>
                                <input type="text" v-model="serviceForms.name" class="form-control" id="serviceName"  placeholder="name">
                            </div>
                            <div class="form-row">
                                <div class="form-group col-md-4">
                                    <label for="serviceIp">Ip</label>
                                    <input type="text" v-model="serviceForms.ip" class="form-control" id="serviceIp"  placeholder="ip">
                                </div>
                                <div class="form-group col-md-4">
                                    <label for="servicePort">Port</label>
                                    <input type="text" v-model="serviceForms.port" class="form-control" id="servicePort"  placeholder="port">
                                </div>
                                <div class="form-group col-md-4">
                                    <label for="serviceTarget">Target</label>
                                    <input type="text" v-model="serviceForms.target" class="form-control" id="serviceTarget"  placeholder="target/path">
                                </div>                                
                            </div>
                            <div class="form-group">
                                <label for="serviceGroup">Group</label>
                                <select v-model="serviceForms.gid" :options="groupsButtons" class="form-control mb-3" id="serviceGroup">
                                    <option disabled>Choose Group...</option>
                                    <option v-for="group in groupsButtons" v-bind:key="group.id" v-bind:value="group.id">ID: {{ group.id }}, Name: {{ group.name }}</option>
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='input'">
                        <form >
                            <div class="form-row">
                                <div class="form-group col-md-6">
                                    <label for="inputName">Name</label>
                                    <input type="text" v-model="inputForms.name" class="form-control" id="inputName"  placeholder=Name>
                                </div>
                                <div class="form-group col-md-6">
                                    <label for="inputInitVal">Initial Value</label>
                                    <input type="number" step="0.01" v-model="inputForms.initialValue" class="form-control" id="inputInitVal"  placeholder="initial Value">
                                </div>                                
                            </div>

                            <div class="form-group">
                                <label for="inputService">Service</label>
                                <select v-model="inputForms.sid" :options="servicesButtons" class="form-control mb-3" id="inputService">
                                    <option disabled>Choose Service...</option>
                                    <option v-for="service in servicesButtons" v-bind:key="service.id" v-bind:value="service.id">ID: {{ service.id }}, Name: {{ service.name }}</option>
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='output'">
                        <form >
                            <div class="form-row">
                                <div class="form-group col-md-6">
                                    <label for="outputName">Name</label>
                                    <input type="text" v-model="outputForms.name" class="form-control" id="outputName"  placeholder=Name>
                                </div>
                                <div class="form-group col-md-6">
                                    <label for="outputInitVal">Initial Value</label>
                                    <input type="number" step="0.01" v-model="outputForms.initialValue" class="form-control" id="outputInitVal"  placeholder="initial Value">
                                </div>                                
                            </div>
                            <div class="form-group">
                                <label for="outputService">Service</label>
                                <select v-model="outputForms.sid" :options="servicesButtons" class="form-control mb-3" id="outputService">
                                    <option disabled>Choose Service...</option>
                                    <option v-for="service in servicesButtons" v-bind:key="service.id" v-bind:value="service.id">ID: {{ service.id }}, Name: {{ service.name }}</option>
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='run'">
                        <form>
                            <div class="form-group">
                                <label for="tableName">Name</label>
                                <input type="text" v-model="runForms.tableName" class="form-control" id="tableName"  placeholder="Table name">
                            </div>
                            <div class="form-group">
                                <label for="runGroup">Group</label>
                                <select v-model="runForms.gid" :options="groupsButtons" class="form-control mb-3" id="runGroup">
                                    <option disabled>Choose Group...</option>
                                    <option v-for="group in groupsButtons" v-bind:key="group.id" v-bind:value="group.id">ID: {{ group.id }}, Name: {{ group.name }}</option>
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='mapping'">
                        <div class="form-row">
                            <label for="serviceOutput">Service(output)</label>
                            <select v-model="mappingForms.soid" :options="groupsButtons"  @change="onChangeOuts()" class="form-control mb-3" id="serviceOutput">
                                <option disabled>Choose Service of Output...</option>
                                <option v-for="service in servicesButtons" v-bind:key="service.id" v-bind:value="service.id">ID: {{ service.id }}, Name: {{ service.name }}</option>
                            </select>  
                            <label for="output">Output</label>
                            <select v-model="mappingForms.oid" :options="groupsButtons" class="form-control mb-3" id="output">
                                <option disabled>Choose Output...</option>
                                <option v-for="output in serviceOutputs"  v-bind:key="output.id" v-bind:value="output.id">ID: {{ output.id }}, Name: {{ output.name }}</option>
                            </select>
                            <label for="serviceInput">Service(input)</label>
                            <select v-model="mappingForms.siid" :options="groupsButtons" @change="onChangeIns()" class="form-control mb-3" id="serviceInput">
                                <option disabled>Choose Service of Input...</option>
                                <option v-for="service in servicesButtons" v-bind:key="service.id" v-bind:value="service.id" >ID: {{ service.id }}, Name: {{ service.name }}</option>
                            </select>  
                            <label for="input">Input</label>
                            <select v-model="mappingForms.iid" :options="groupsButtons" class="form-control mb-3" id="input">
                                <option disabled>Choose Input...</option>
                                <option v-for="input in serviceInputs" v-bind:key="input.id" v-bind:value="input.id">ID: {{ input.id }}, Name: {{ input.name }}</option>
                            </select>                                
                        </div>
                        <div class="form-group">
                            <label for="runGroup">Group</label>
                            <select v-model="mappingForms.gid" :options="groupsButtons" class="form-control mb-3" id="runGroup">
                                <option disabled>Choose Group...</option>
                                <option v-for="group in groupsButtons" v-bind:key="group.id" v-bind:value="group.id">ID: {{ group.id }}, Name: {{ group.name }}</option>
                            </select>
                        </div>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='config'">
                        <div class="form-row">
                            <div class="form-group col-md-4">
                                <label for="startTime">Start Time</label>
                                <input type="number" v-model="configForms.startTime" class="form-control" id="startTime"  placeholder="Start Time">
                            </div>
                            <div class="form-group col-md-4">
                                <label for="endTime">End Time</label>
                                <input type="number" v-model="configForms.endTime" class="form-control" id="endTime"  placeholder="End Time">
                            </div>
                            <div class="form-group col-md-4">
                                <label for="stepSize">Step Size</label>
                                <input type="number" step="0.01" v-model="configForms.stepSize" class="form-control" id="stepSize"  placeholder="Step Size">
                            </div>                                
                        </div>
                        <div class="form-group">
                            <label for="configRun">Run</label>
                            <select v-model="configForms.rid" :options="runsButtons" class="form-control mb-3" id="configRun">
                                <option disabled>Choose Run...</option>
                                <option v-for="run in runsButtons" v-bind:key="run.id" v-bind:value="run.id">ID: {{ run.id }}, Name: {{ run.tableName }}</option>
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                        <button class="btn btn-primary" v-on:click="addSubmit(selectedComp)" data-dismiss="modal">Submit</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Edit Modal -->
        <div class="modal fade" id="editModal" tabindex="-1" role="dialog" aria-labelledby="editButtonModal" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered" role="document" >
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Edit {{ selectedComp }}</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='service'">
                        <form>
                            <div class="form-row">
                                <label for="serviceId">ID</label>
                                <input type="text" v-model="serviceForms.id" class="form-control" id="serviceId" disabled>
                                <label for="serviceName">Name</label>
                                <input type="text" v-model="serviceForms.name" class="form-control" id="serviceName"  placeholder="name">
                            </div>
                            <div class="form-row">
                                <div class="form-group col-md-4">
                                    <label for="serviceIp">Ip</label>
                                    <input type="text" v-model="serviceForms.ip" class="form-control" id="serviceIp"  placeholder="ip">
                                </div>
                                <div class="form-group col-md-4">
                                    <label for="servicePort">Port</label>
                                    <input type="text" v-model="serviceForms.port" class="form-control" id="servicePort"  placeholder="port">
                                </div>
                                <div class="form-group col-md-4">
                                    <label for="serviceTarget">Target</label>
                                    <input type="text" v-model="serviceForms.target" class="form-control" id="serviceTarget"  placeholder="target/path">
                                </div>                                
                            </div>
                            <div class="form-group">
                                <label for="serviceGroup">Group</label>
                                <select v-model="serviceForms.gid" :options="groupsButtons" class="form-control mb-3" id="serviceGroup">
                                    <option disabled>Choose Group...</option>
                                    <option v-for="group in groupsButtons" v-bind:key="group.id" v-bind:value="group.id">ID: {{ group.id }}, Name: {{ group.name }}</option>
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='input'">
                        <form >
                            <div class="form-row">
                                <div class="form-group col-md-4">
                                    <label for="inputId">Id</label>
                                    <input type="text" v-model="inputForms.id" class="form-control" id="inputId"  disabled>
                                </div>
                                <div class="form-group col-md-4">
                                    <label for="inputName">Name</label>
                                    <input type="text" v-model="inputForms.name" class="form-control" id="inputName"  placeholder="Name">
                                </div>
                                <div class="form-group col-md-4">
                                    <label for="inputInitVal">Initial Value</label>
                                    <input type="number" step="0.01" v-model="inputForms.initialValue" class="form-control" id="inputInitVal"  placeholder="initial Value">
                                </div>                                
                            </div>

                            <div class="form-group">
                                <label for="inputService">Service</label>
                                <select v-model="inputForms.sid" :options="servicesButtons" class="form-control mb-3" id="inputService">
                                    <option disabled>Choose Service...</option>
                                    <option v-for="service in servicesButtons" v-bind:key="service.id" v-bind:value="service.id">ID: {{ service.id }}, Name: {{ service.name }}</option>
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='output'">
                        <form >
                            <div class="form-row">
                                <div class="form-group col-md-4">
                                    <label for="outputId">Id</label>
                                    <input type="text" v-model="outputForms.id" class="form-control" id="outputId"  disabled>
                                </div>
                                <div class="form-group col-md-4">
                                    <label for="outputName">Name</label>
                                    <input type="text" v-model="outputForms.name" class="form-control" id="outputName"  placeholder=Name>
                                </div>
                                <div class="form-group col-md-4">
                                    <label for="outputInitVal">Initial Value</label>
                                    <input type="number" step="0.01" v-model="outputForms.initialValue" class="form-control" id="outputInitVal"  placeholder="initial Value">
                                </div>                                
                            </div>
                            <div class="form-group">
                                <label for="outputService">Service</label>
                                <select v-model="outputForms.sid" :options="servicesButtons" class="form-control mb-3" id="outputService">
                                    <option disabled>Choose Service...</option>
                                    <option v-for="service in servicesButtons" v-bind:key="service.id" v-bind:value="service.id">ID: {{ service.id }}, Name: {{ service.name }}</option>
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='run'">
                        <form>
                            <div class="form-row">
                                <div class="form-group col-md-3">
                                    <label for="runId">Id</label>
                                    <input type="text" v-model="runForms.id" class="form-control" id="runId"  disabled>
                                </div>
                                <label for="tableName">Name</label>
                                <input type="text" v-model="runForms.tableName" class="form-control" id="tableName"  placeholder="Table name">
                            </div>
                            <div class="form-group">
                                <label for="runGroup">Group</label>
                                <select v-model="runForms.gid" :options="groupsButtons" class="form-control mb-3" id="runGroup">
                                    <option disabled>Choose Group...</option>
                                    <option v-for="group in groupsButtons" v-bind:key="group.id" v-bind:value="group.id">ID: {{ group.id }}, Name: {{ group.name }}</option>
                                </select>
                            </div>
                        </form>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='mapping'">
                        <div class="form-row">
                            <label for="mappingId">Id</label>
                            <input type="text" v-model="mappingForms.id" class="form-control" id="mappingId"  disabled>
                        </div>
                        <div class="form-row">
                            <div class="form-group col-md-6">
                                <label for="serviceOutput">Service(output)</label>
                                <select v-model="mappingForms.soid" :options="groupsButtons"  @change="onChangeOuts()" class="form-control mb-3" id="serviceOutput">
                                    <option disabled>Choose Service of Output...</option>
                                    <option v-for="service in servicesButtons" v-bind:key="service.id" v-bind:value="service.id">ID: {{ service.id }}, Name: {{ service.name }}</option>
                                </select> 
                            </div>         
                            <div class="form-group col-md-6">                        
                                <label for="serviceInput">Service(input)</label>
                                <select v-model="mappingForms.siid" :options="groupsButtons" @change="onChangeIns()" class="form-control mb-3" id="serviceInput">
                                    <option disabled>Choose Service of Input...</option>
                                    <option v-for="service in servicesButtons" v-bind:key="service.id" v-bind:value="service.id" >ID: {{ service.id }}, Name: {{ service.name }}</option>
                                </select> 
                            </div>
                        </div>
                        <div class="form-row">
                            <div class="form-group col-md-6">
                                <label for="output">Output</label>
                                <select v-model="mappingForms.oid" :options="groupsButtons" class="form-control mb-3" id="output">
                                    <option disabled>Choose Output...</option>
                                    <option v-for="output in serviceOutputs"  v-bind:key="output.id" v-bind:value="output.id">ID: {{ output.id }}, Name: {{ output.name }}</option>
                                </select>
                            </div>         
                            <div class="form-group col-md-6">   
                                <label for="input">Input</label>
                                <select v-model="mappingForms.iid" :options="groupsButtons" class="form-control mb-3" id="input">
                                    <option disabled>Choose Input...</option>
                                    <option v-for="input in serviceInputs" v-bind:key="input.id" v-bind:value="input.id">ID: {{ input.id }}, Name: {{ input.name }}</option>
                                </select>
                            </div> 
                        </div> 
                        <div class="form-group">
                            <label for="runGroup">Group</label>
                            <select v-model="mappingForms.gid" :options="groupsButtons" class="form-control mb-3" id="runGroup">
                                <option disabled>Choose Group...</option>
                                <option v-for="group in groupsButtons" v-bind:key="group.id" v-bind:value="group.id">ID: {{ group.id }}, Name: {{ group.name }}</option>
                            </select>
                        </div>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='config'">
                        <div class="form-row">
                            <label for="configId">Id</label>
                            <input type="text" v-model="configForms.id" class="form-control" id="configId"  disabled>
                        </div>
                        <div class="form-row">
                            <div class="form-group col-md-4">
                                <label for="startTime">Start Time</label>
                                <input type="number" v-model="configForms.startTime" class="form-control" id="startTime"  placeholder="Start Time">
                            </div>
                            <div class="form-group col-md-4">
                                <label for="endTime">End Time</label>
                                <input type="number" v-model="configForms.endTime" class="form-control" id="endTime"  placeholder="End Time">
                            </div>
                            <div class="form-group col-md-4">
                                <label for="stepSize">Step Size</label>
                                <input type="number" step="0.01" v-model="configForms.stepSize" class="form-control" id="stepSize"  placeholder="Step Size">
                            </div>                                
                        </div>
                        <div class="form-group">
                            <label for="configRun">Run</label>
                            <select v-model="configForms.rid" :options="runsButtons" class="form-control mb-3" id="configRun">
                                <option disabled>Choose Run...</option>
                                <option v-for="run in runsButtons" v-bind:key="run.id" v-bind:value="run.id">ID: {{ run.id }}, Name: {{ run.tableName }}</option>
                            </select>
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                        <button class="btn btn-primary" v-on:click="editSubmit(selectedComp)" data-dismiss="modal">Submit</button>
                    </div>
                </div>
            </div>
        </div>

        <!-- Delete Modal -->
        <div class="modal fade" id="deleteModal" tabindex="-1" role="dialog" aria-labelledby="deleteButtonModal" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered" role="document" >
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Delete-{{ selectedComp }}</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body" v-if="selectedComp=='service'">
                        Deleting following service, please submit to confirm.
                        Id: {{ serviceForms.id }},
                        Name: {{ serviceForms.name }},
                        IP: {{ serviceForms.ip }},
                        Port: {{ serviceForms.port }},
                        Target: {{ serviceForms.target }}
                        Group: {{ serviceForms.gid }}
                    </div>
                    <div class="modal-body" v-if="selectedComp=='input'">
                        Deleting following input, please submit to confirm.
                        Id: {{ inputForms.id }},
                        Name: {{ inputForms.name }},
                        Initial Value: {{ inputForms.initialValue }},
                        Service: {{ inputForms.service }}
                    </div>
                    <div class="modal-body" v-if="selectedComp=='output'">
                        Deleting following output, please submit to confirm.
                        Id: {{ outputForms.id }},
                        Name: {{ outputForms.name }},
                        Initial Value: {{ outputForms.initialValue }},
                        Service: {{ outputForms.service }}
                    </div>
                    <div class="modal-body" v-if="selectedComp=='run'">
                        Deleting following run, please submit to confirm.
                        Id: {{ runForms.id }},
                        Table Name: {{ runForms.tableName }},
                        Group: {{ runForms.gid }}
                    </div>
                    <div class="modal-body" v-if="selectedComp=='mapping'">
                        Deleting following mapping, please submit to confirm.
                        Id: {{ mappingForms.id }},
                        Service(Output): {{ mappingForms.soid }},
                        Output: {{ mappingForms.oid }},
                        Service(Input): {{ mappingForms.siid }},
                        Input: {{ mappingForms.iid }}
                    </div>
                    <div class="modal-body" v-if="selectedComp=='config'">
                        Deleting following configuration, please submit to confirm.
                        Id: {{ configForms.id }},
                        Run: {{ configForms.rid }},
                        Start Time: {{ configForms.startTime }},
                        End Time: {{ configForms.endTime }},
                        Step Size: {{ configForms.stepSize }}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                        <button class="btn btn-primary" v-on:click="deleteSubmit(selectedComp)" data-dismiss="modal">Submit</button>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<script>
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

import axios from "axios";
import { EventBus } from '../main.js';

export default {
    name: 'buttonsComp',

    props: {
        selectedComp: String,
        ip: String,
        port: String,
    },

    data(){
        return{
            groupsButtons: [],
            servicesButtons: [],
            outputsButtons: [],
            inputsButtons: [],
            runsButtons: [],
            mappingsButtons: [],
            configsButtons: [],
            
            serviceOutputs: [],
            serviceInputs: [],

            groupRef: Number,
            selectedGroup: 0,
            selectedService: 0,

            serviceForms: {
                id: 0,
                name: '',
                ip: '',
                port: '',
                target: '',
                gid: 0
            },

            runForms: {
                id: 0,
                tableName: '',
                gid: 0
            },

            mappingForms: {
                id: 0,
                gid: 0,
                soid: 0,
                oid: 0,
                siid: 0,
                iid: 0
            },

            inputForms: {
                id: 0,
                sid: 0,
                name: '',
                initialValue: 0.0
            },

            outputForms: {
                id: 0,
                sid: 0,
                name: '',
                initialValue: 0.0
            },

            configForms: {
                id : 0,
                rid : 0,
                startTime: 0,
                endTime: 0,
                stepSize: 0.0
            }
        }
    },

    created(){
        
        EventBus.$on( 'group-selected',  payLoad =>{
            this.groupRef = payLoad;
            this.getGroups();
            this.getServices();
            this.getRuns(this.groupRef);
            this.getInputs();
            this.getOutputs();
            this.getMappings();
            this.getConfigs();
        },
        
        EventBus.$on( 'service-selected',  payLoad =>{
            this.selectedService = payLoad.id;
            this.serviceForms = payLoad;
        })),

        EventBus.$on( 'mapping-selected', payLoad => {
            this.mappingForms = payLoad;
            this.onChangeOuts();
            this.onChangeIns();
        } ),

        EventBus.$on( 'input-selected' , payLoad => {
            this.inputForms = payLoad;
        } ),

        EventBus.$on( 'output-selected' , payLoad => {
            this.outputForms = payLoad;
        } ),

        EventBus.$on( 'run-selected' , payLoad => {
            this.runForms = payLoad;
        } ),

        EventBus.$on( 'config-selected' , payLoad => {
            this.configForms = payLoad;
        } )
    },
    mounted(){
    },

    methods: {

        refreshAll: function(){
            EventBus.$emit('refresh-all', this.groupRef);
        },


        getGroups: function(){
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/groups"
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.groupsButtons = result.data;
                }, error => {
                    console.error(error);
                } )
        },

        getServices: function(){
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/services?group=" + String( this.groupRef )
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.servicesButtons = result.data;
                }, error => {
                    console.error(error);
                } )
        },

        getInputs: function(){
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/allinputs"
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.inputsButtons = result.data; 
                }, error => {
                    console.error(error);
                } )
        },

        getOutputs: function(){
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/alloutputs"
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.outputsButtons = result.data; 
                }, error => {
                    console.error(error);
                } )
        },

        getRuns: function(gid){

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/runs?group=" + String( gid )
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.runsButtons = result.data; 
                }, error => {
                    console.error(error);
                } )

        },

        getMappings: function(){

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/mappings?group=" + String( this.groupRef )

            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.mappingsButtons = result.data; 
                }, error => {
                    console.error(error);
                } )

        },

        getConfigs: function(){

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/configs?group=" + String( this.groupRef )
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.configsButtons = result.data; 
                }, error => {
                    console.error(error);
                } )
        },

        addSubmit: function(comp){
            var body = {};

            if( comp == 'service' ){
                body = this.serviceForms;
            }

            else if( comp == 'output' ){
                body = this.outputForms;
            }

            else if( comp == 'input' ){
                body = this.inputForms;
            }

            else if( comp == 'run' ){
                body = this.runForms;
            }

            else if( comp == 'mapping' ){
                body = this.mappingForms;
            }

            else if( comp == 'config' ){
                body = this.configForms;
            }

            EventBus.$emit('add-' + comp + '-submitted' , body);
        },

        editSubmit: function(comp){

            var body = {};

            if( comp == 'service' ){
                body = this.serviceForms;
            }

            else if( comp == 'output' ){
                body = this.outputForms;
            }

            else if( comp == 'input' ){
                body = this.inputForms;
            }

            else if( comp == 'run' ){
                body = this.runForms;
            }

            else if( comp == 'mapping' ){
                body = this.mappingForms;
            }

            else if( comp == 'config' ){
                body = this.configForms;
            }

            EventBus.$emit('edit-' + comp + '-submitted' , body )
        },

        deleteSubmit: function(comp){
            var body = {};

            if( comp == 'service' ){
                body = this.serviceForms;
            }

            else if( comp == 'output' ){
                body = this.outputForms;
            }

            else if( comp == 'input' ){
                body = this.inputForms;
            }

            else if( comp == 'run' ){
                body = this.runForms;
            }

            else if( comp == 'mapping' ){
                body = this.mappingForms;
            }

            else if( comp == 'config' ){
                body = this.configForms;
            }

            EventBus.$emit('delete-' + comp + '-submitted' , body )
        },

        selectOption: function(x){

            this.selectedGroup = x;

        },

        onChangeOuts: function(){
            this.serviceOutputs = [];
            for( var i = 0; i < this.outputsButtons.length; i++){
                if(this.outputsButtons[i].sid == this.mappingForms.soid){
                    this.serviceOutputs.push( this.outputsButtons[i] )
                }
            }
        },

        onChangeIns: function(){
            this.serviceInputs = [];
            for( var i = 0; i < this.inputsButtons.length; i++){
                if(this.inputsButtons[i].sid == this.mappingForms.siid){
                    this.serviceInputs.push( this.inputsButtons[i] )
                }
            }
        }
    }
}
</script>

<style>

</style>


