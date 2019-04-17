<template>
    <div id="runComp">
        <table class="table table-bordered table-hover">
            <thead>
                <tr>
                    <th v-for="runKeys in Object.keys(runForms)" v-bind:key="runKeys" scope="col"> {{ runKeys.toUpperCase() }} </th>
                </tr>
            </thead>
            <tbody v-if="this.validation.valid">
                <tr v-for="(run, index) in runs" v-bind:key="index" v-bind:class="{ 'table-active' : validation.selectedIndex == index }" v-on:click="changeIndex(index)">
                    <td>{{ run.id }}</td>
                    <td>{{ run.tableName }}</td>
                    <td>{{ run.gid }}</td>
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
    name: "runComp",

    props: {
        ip: String,
        port: String
    },
    
    data() {
        return {
            groupRef: Number,
            runs: [],
            runForms: {
                id: 0,
                tableName: '',
                gid: 0
            },
            tempValues: [],
            tableName: '',
            validation: {
                valid: false,
                selectedIndex: Number
            }

        }
    },

    created(){
        //payLoad is group id
        EventBus.$on( 'group-selected', payLoad => { 
            this.groupRef = payLoad ;
            this.getRuns();
            this.validation.valid = true;
            } );

        EventBus.$on( 'add-run-submitted' , payLoad => {
            this.createRun(payLoad);
        } );

        EventBus.$on( 'edit-run-submitted' , payLoad => {
            this.editTableName(payLoad);
        } );

        EventBus.$on( 'delete-run-submitted' , payLoad =>{
            this.deleteRun(payLoad.id);
        } );


        EventBus.$on('refresh-all', this.getRuns )
    },
    mounted(){},

    methods:{

        createRun: function(body){

            var url = "http://" + this.ip + ":" + this.port + "/cso/create/run";

            

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "POST",
                "url" : url, 
                data: body
            }).then( result => { console.log(result) } )

        },

        getRuns: function(){
          
            var url = "http://" + this.ip + ":" + this.port + "/cso/runs?group=" + String( this.groupRef ) ;

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.runs = result.data
                } )
        },

        getValues: function(){

            var url = "http://" + this.ip + ":" + this.port + "/cso/values?id=" + this.runForms.id;

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.tempValues = result.data
                } )
        },

        deleteValues: function(){

            var url = "http://" + this.ip + ":" + this.port + "/cso/delete/valueTable?id=" + this.runForms.id;

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "DELETE",
                "url" : url
            }).then( result => { console.log(result) } )
        },

        getTableName: function(){
            
            var url = "http://" + this.ip + ":" + this.port + "/cso/table?rid=" + this.runForms.id;

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : url
            }).then( result => { this.tableName = result.data })

        },

        deleteRun: function(id){

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/delete/run?id=" + String( id )

            axios({
                method: "DELETE",
                "url" : url
            }).then( result => { console.log(result) }, error => {
                    console.error(error);
                } )

        },
        
        changeIndex: function(num){
            this.validation.selectedIndex = num;
            this.runForms.id = this.runs[ num ].id ;
            this.runForms.tableName = this.runs[ num ].tableName ;
            this.runForms.gid = this.runs[ num ].gid ;

            EventBus.$emit( 'run-selected' , this.runForms )
        },

        editTableName: function(body){
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */

            var url = "http://" + this.ip + ":" + this.port + "/cso/edit/run"

            axios({
                method: "PUT",
                "url" : url,
                data : body
            }).then( result => { console.log(result) }, error => {
                    console.error(error);
                } )

        }
    }
}
</script>

<style>

</style>
