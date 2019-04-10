<template>
    <div id="mappingComp">
        <div class="row">
            <div class="col-md-1">
                <table class="table table-bordered table-hover">
                    <thead>
                        <th scope="col">ID</th>
                        <!-- <th scope="col">GID</th> -->
                    </thead>
                    <tbody v-if="this.validation.valid">
                        <tr v-for="(mapping, index) in mappings" v-bind:key="index" v-bind:class="{ 'table-active' : validation.selectedIndex == index }" v-on:click="changeIndex(index)">
                            <td>{{ mapping.id }}</td>
                            <!-- <td>{{ mapping.gid }}</td> -->
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="col-md col-md-offset-3">
                <table class="table table-bordered table-hover">
                    <thead>
                        <th scope="col">Output</th>
                        <th scope="col">Service</th>
                    </thead>
                    
                    <tbody v-if="this.validation.valid">
                        <tr v-for="(mapping, index) in mappings" v-bind:key="index" v-bind:class="{ 'table-active' : validation.selectedIndex == index }" v-on:click="changeIndex(index)">
                            <td>{{ nameOfoutput(mapping.oid) }}</td>
                            <td>{{ nameOfservice(mapping.soid) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div class="col-md col-md-offset-3">
                <table class="table table-bordered table-hover">
                    <thead>
                        <th scope="col">Input</th>
                        <th scope="col">Service</th>
                    </thead>
                    <tbody v-if="this.validation.valid">
                        <tr v-for="(mapping, index) in mappings" v-bind:key="index" v-bind:class="{ 'table-active' : validation.selectedIndex == index }" v-on:click="changeIndex(index)">
                            <td>{{ nameOfinput(mapping.iid) }}</td>
                            <td>{{ nameOfservice(mapping.siid) }}</td>
                        </tr>
                    </tbody>
                </table>
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
    name: 'mappingComp',

    props: {
        ip: String,
        port: String
    },

    data() {

        return {
            services: [],
            inputs: [],
            outputs: [],
            mappings: [],
            mappingForms: {
                id: 0,
                gid: 0,
                soid: 0,
                oid: 0,
                siid: 0,
                iid: 0
            },
            validation: {
                valid: false,
                selectedIndex: Number
            },
            groupRef: Number,
            serviceRef: Number
        }
    },

    created(){
        
        //payLoad is group id
        EventBus.$on( 'group-selected', payLoad => { 
            this.groupRef = payLoad;
            this.mappingsOfgroup(payLoad);
            this.servicesOfgroup(payLoad);
            this.allInputs();
            this.allOutputs();
            this.validation.valid = true;
            } );
        
        EventBus.$on( 'delete-mapping-submitted' , payLoad => {
            this.deleteMapping(payLoad.id);
        } );

        EventBus.$on('refresh-all', this.refresh );

        EventBus.$on( 'add-mapping-submitted' , payLoad => {
            this.createMapping(payLoad)
        } )

        EventBus.$on( 'edit-mapping-submitted' , payLoad => {
            this.editMapping(payLoad)
        } )
    },

    computed: {       
        
    },
    mounted() {
        this.mappingsOfgroup();
    },

    methods: {

        refresh: function(){
            this.mappingsOfgroup(this.groupRef);
            this.servicesOfgroup(this.groupRef);
            this.allInputs();
            this.allOutputs();
            this.validation.valid = true;
        },

        createMapping: function(body){           

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "POST",
                "url" : "http://" + this.ip + ":" + this.port + "/cso/create/mapping", 
                data: body
            }).then( result => { console.log(result) } )
        },

        editMapping: function(body){           

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "PUT",
                "url" : "http://" + this.ip + ":" + this.port + "/cso/edit/mapping", 
                data: body
            }).then( result => { console.log(result) } )
        },

        mappingsOfgroup: function(id){

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : "http://" + this.ip + ":" + this.port + "/cso/mappings?group=" + String( id )
            }).then( result => { 
                this.mappings = result.data;  
                this.validation.valid = true; 
                }, error => {
                    console.error(error);
                    this.validation.valid = false;
                } )
        },

        servicesOfgroup: function(id){

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : "http://" + this.ip + ":" + this.port + "/cso/services?group=" + String( id )
            }).then( result => { 
                this.services = result.data;  
                this.validation.valid = true; 
                }, error => {
                    console.error(error);
                    this.validation.valid = false;
                } )
        },

        allOutputs: function(){

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : "http://" + this.ip + ":" + this.port + "/cso/alloutputs"
            }).then( result => { 
                this.outputs = result.data;  
                this.validation.valid = true; 
                }, error => {
                    console.error(error);
                    this.validation.valid = false;
                } )
        },

        allInputs: function(){

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : "http://" + this.ip + ":" + this.port + "/cso/allinputs"
            }).then( result => { 
                this.inputs = result.data;  
                this.validation.valid = true; 
                }, error => {
                    console.error(error);
                    this.validation.valid = false;
                } )
        },

        changeIndex: function(num){
            this.validation.selectedIndex = num;
            this.mappingForms.id = this.mappings[num].id;
            this.mappingForms.gid = this.mappings[num].gid;
            this.mappingForms.iid = this.mappings[num].iid;
            this.mappingForms.oid = this.mappings[num].oid;
            this.mappingForms.siid = this.mappings[num].siid;
            this.mappingForms.soid = this.mappings[num].soid;
            EventBus.$emit('mapping-selected', this.mappingForms)
        },

        nameOfservice: function(sid){

            for( var i = 0; i < this.services.length; i++ ){

                if( sid == this.services[i].id ){
                    return this.services[i].name
                }
            }
        },

        nameOfinput: function(iid){

            for( var i = 0; i < this.inputs.length; i++ ){

                if( iid == this.inputs[i].id ){
                    return this.inputs[i].name
                }
            }
        },

        nameOfoutput: function(oid){

            for( var i = 0; i < this.outputs.length; i++ ){

                if( oid == this.outputs[i].id ){
                    return this.outputs[i].name
                }
            }
        },

        deleteMapping: function(id){

            var url = "http://" + this.ip + ":" + this.port + "/cso/delete/mapping?id=" + String( id );
            /*eslint no-console: ["error", { allow: ["warn", "error", "log"] }] */
            axios({ 
                method: "DELETE", 
                "url": url
            }).then( result => {
                console.log( result )
            });
        }
    }
    
}
</script>

<style>

</style>
