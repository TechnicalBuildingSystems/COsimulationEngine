<template>
    <div id="simconfigComp">
        <table class="table table-bordered table-hover">
            <thead>
                <tr>
                    <th v-for="configKey in Object.keys(simconfigForms)" v-bind:key="configKey" scope="col"> {{ configKey.toUpperCase() }} </th>
                </tr>
            </thead>
            <tbody v-if="this.validation.valid">
                <tr v-for="(config, index) in simConfigs" v-bind:key="index" v-bind:class="{ 'table-active' : validation.selectedIndex == index }" v-on:click="changeIndex(index)">
                    <td> {{ config.id }} </td>
                    <td> {{ config.rid }} </td>
                    <td> {{ config.startTime }} </td>
                    <td> {{ config.endTime }} </td>
                    <td> {{ config.stepSize }} </td>
                </tr>
            </tbody>
        </table>
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
    name: "simconfigComp",

    props: {
        ip: String,
        port: String
    },

    data() {

        return {
            group: Number,
            simConfigs: [],
            simconfigForms: {
                id: 0,
                rid: 0,
                startTime: 0,
                endTime: 0,
                stepSize : 0.0
            },
            validation: {
                valid: false,
                selectedIndex: Number
            }
        }
    },

    created(){

        EventBus.$on( 'group-selected' , payLoad => {
            this.group = payLoad;
            this.getConfigsOfGroup();
        }),


        EventBus.$on('refresh-all', this.getConfigsOfGroup );


        EventBus.$on( 'edit-config-submitted' , payLoad => {
            this.editConfig(payLoad)
        } )

        EventBus.$on( 'add-config-submitted' , payLoad => {
            this.createConfig(payLoad)
        } )


        EventBus.$on( 'delete-config-submitted' , payLoad => {
            this.deleteConfig(payLoad.id);
        })
    },
    mounted(){
    },

    methods: {

        createConfig: function(body){

            var url = "http://" + this.ip + ":" + this.port + "/cso/create/config";


            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "POST",
                "url" : url, 
                data: body
            }).then( result => { console.log(result) } )
        },

        editConfig: function(body){

            var url = "http://" + this.ip + ":" + this.port + "/cso/edit/config";

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "PUT",
                "url" : url, 
                data: body
            }).then( result => { console.log(result) } )
        },

        getConfig: function(){

            var url = "http://" + this.ip + ":" + this.port + "/cso/config?id=" + String( this.simconfigForms.id );

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "POST",
                "url" : url
            }).then( result => { 
                this.simConfigs.push(result.data)
                }, error => {
                    console.error(error);
                } )
        },

        getConfigsOfGroup: function(){

            var url = "http://" + this.ip + ":" + this.port + "/cso/configs?group=" + String( this.group );

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.simConfigs = result.data;
                this.validation.valid = true;
                }, error => {
                    console.error(error);
                    this.validation.valid = false;
                } )
        },

        deleteConfig: function(id){

            var url = "http://" + this.ip + ":" + this.port + "/cso/delete/config?id=" + String( id ) ;

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "DELETE",
                "url" : url
            }).then( result => { 
                console.log(result)
                }, error => {
                    console.error(error);
                } )
        },

        changeIndex: function(num){
            this.validation.selectedIndex = num;
            this.simconfigForms.id = this.simConfigs[ num ].id;
            this.simconfigForms.rid = this.simConfigs[ num ].rid;
            this.simconfigForms.startTime = this.simConfigs[ num ].startTime;
            this.simconfigForms.endTime = this.simConfigs[ num ].endTime;
            this.simconfigForms.stepSize = this.simConfigs[ num ].stepSize;
            EventBus.$emit('config-selected' , this.simconfigForms )
        }
        
    }

}
</script>

<style>

</style>
