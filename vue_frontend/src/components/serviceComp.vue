<template>
    <div id="serviceComp">
        <!-- <div v-for="item in Object.keys( groupForms)" v-bind:key="item" > {{ item }}</div> -->
        <table class="table table-bordered table-hover">
            <thead>
                <tr>
                    <th v-for="serviceKeys in Object.keys(serviceForms)" v-bind:key="serviceKeys" scope="col"> {{ serviceKeys.toUpperCase() }} </th>
                </tr>
            </thead>
            <tbody v-if="this.validation.valid">
                <tr v-for="(service, index) in services" v-bind:key="index" v-bind:class="{ 'table-active' : validation.selectedIndex == index }" v-on:click="changeIndex(index)">
                    <td>{{ service.id }}</td>
                    <td>{{ service.name }}</td>
                    <td>{{ service.ip }}</td>
                    <td>{{ service.port }}</td>
                    <td>{{ service.target }}</td>                    
                    <td>{{ groupRef }}</td>
                </tr>
            </tbody>
        </table>
        <!-- <ul v-if="this.validation.valid">
            <li v-for="service in services" v-bind:key="service.id"> id: {{ service.id }}, name: {{ service.name }}, ip: {{ service.ip }}, port: {{ service.port }}, target: {{ service.target }} </li>
        </ul> -->
        <button v-on:click="getServicesOfGroup(groupRef)">Group: {{ groupRef }}</button>
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
    name: 'serviceComp',
    props: {
        ip: String,
        port: String
    },
    data() {
        return {
            groupRef: Number,
            services: [],
            serviceForms: { 
                id: 0, 
                name: '', 
                ip: '', 
                port: '', 
                target: '', 
                gid: 0 
            }, 
            servicesOfGroup: [],
            validation: {
                valid: false,
                selectedIndex : Number
            }
        }
    },

    mounted() {
        this.getServicesOfGroup();
        
    },

    created(){

        EventBus.$on( 'add-service-submitted' , payLoad => {
            this.createService(payLoad);
        } );

        //payLoad is group id
        EventBus.$on( 'group-selected', payLoad => { 
            this.groupRef = payLoad; 
            this.getServicesOfGroup(payLoad) 
            } );

        EventBus.$on( 'delete-service-submitted' , payLoad => {
            this.deleteService(payLoad.id);
        } )

        EventBus.$on( 'edit-service-submitted' , payLoad => {
            this.editService(payLoad)
        } )

        EventBus.$on('refresh-all', payLoad => {
            this.getServicesOfGroup(payLoad)
        } )
    },

    methods: {

        changeIndex: function(num){
            this.validation.selectedIndex = num;
            this.serviceForms.id = this.services[num].id;
            this.serviceForms.name = this.services[num].name;
            this.serviceForms.ip = this.services[num].ip;
            this.serviceForms.port = this.services[num].port;
            this.serviceForms.target = this.services[num].target;
            this.serviceForms.gid = this.services[num].gid;
            EventBus.$emit( 'service-selected' , this.serviceForms)
        },

        createService: function(body){

            var url = "http://" + this.ip + ":" + this.port + "/cso/create/service";
           

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "POST",
                "url" : url, 
                data: body
            }).then( result => { console.log(result) } )
        },

        editService: function(){

            var url = "http://" + this.ip + ":" + this.port + "/cso/edit/service"
            var body = {
                "id" : this.serviceForms.id,
                "name" : this.serviceForms.name,
                "ip" : this.serviceForms.ip,
                "port": this.serviceForms.port,
                "target": this.serviceForms.target,
                "gid" : this.serviceForms.gid 
            }

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "PUT",
                "url" : url, 
                data: body
            }).then( result => { console.log(result) } )
        },

        getService: function(){

            var url = "http://" + this.ip + ":" + this.port + "/cso/service?id=" + String( this.serviceForms.sid )

            axios({
                method: "GET",
                "url" : url
            }).then( result => {
                this.service.push( result.data );
            }, error => {
                /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
                console.error(error);
            })
        },

        getServicesOfGroup: function(id){
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/services?group=" + String( id )
            axios({
                method: "GET",
                "url" : url
            }).then( result => {
                this.services = result.data;
                this.validation.valid = true;
            }, error => {
                /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
                console.error(error);
                this.validation.valid = false;
            })
        },

        deleteService: function(id){
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/delete/service?id=" + String( id ) 

            axios({
                method: "DELETE",
                "url" : url
            }).then( result => { 
                console.log( result.data );
            }, error => {
                console.error(error);
            } )
        },

        serviceSelected: function(id){

            EventBus.$emit( 'service-selected' , id)
        }
    }
}
</script>

<style>

</style>
