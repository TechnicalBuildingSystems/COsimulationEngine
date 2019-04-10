<template>
    <div id = "outputComp">
        <table class="table table-bordered table-hover">
            <thead>
                <tr>
                    <th v-for="outputKeys in Object.keys(submitOutput)" v-bind:key="outputKeys" scope="col"> {{ outputKeys.toUpperCase() }} </th>
                </tr>
            </thead>
            <tbody v-if="this.validation.valid">
                <tr v-for="(output, index) in outputs" v-bind:key="index" v-bind:class="{ 'table-active' : validation.selectedIndex == index }" v-on:click="changeIndex(index)">
                    <td>{{ output.id }}</td>
                    <td>{{ output.name }}</td>
                    <td>{{ output.sid }}</td>
                    <td>{{ output.initialValue }}</td>
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
    name: 'outputComp',

    props: {
        ip: String,
        port: String
    },

    data() {
        return {
            serviceRef: Number,
            deleteId: 0,
            submitOutput: { 
                id: 0, 
                name: '', 
                sid: 0, 
                initialValue: 0.0
                },
            outputs: [] ,
            validation: {
                valid: false,
                selectedIndex: Number
            }
        }
    },

    created(){
        //payLoad is service id
        EventBus.$on( 'service-selected', payLoad => { 
            this.serviceRef = payLoad.id;
            this.refresh();
            } );

        EventBus.$on( 'delete-output-submitted' , payLoad => {
            this.deleteOutput(payLoad.id);
        } )

        EventBus.$on('refresh-all', this.refresh );

        EventBus.$on( 'add-output-submitted' , payLoad => {
            this.createOutput(payLoad)
        } )
        
        EventBus.$on( 'edit-output-submitted' , payLoad => {
            this.editOutput(payLoad)
        } )
    },

    mounted(){

        this.refresh();
        this.validation.valid = true;

    },
    methods: {
        
        refresh: function(){
            
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/outputs?service=" + String( this.serviceRef );

            axios({ 
                method: "GET", 
                "url": url 
            }).then( result => {
                this.outputs = result.data;
                console.log( result )
            }, error => {
                console.error(error);
            });
            
        }, 

        createOutput: function(body){

            var url = "http://" + this.ip + ":" + this.port + "/cso/create/output";

            /*eslint no-console: ["error", { allow: ["warn", "error", "log"] }] */
            axios({ 
                method : "POST", 
                "url" : url, 
                data : body 
            }).then( result => { 
                console.log(result) 
            })
            
        },

        changeIndex: function(num){
            this.validation.selectedIndex = num;
            this.submitOutput.id = this.outputs[num].id;
            this.submitOutput.initialValue = this.outputs[num].initialValue;
            this.submitOutput.name = this.outputs[num].name;
            this.submitOutput.sid = this.outputs[num].sid;
            EventBus.$emit( 'output-selected' , this.submitOutput )
        },

        editOutput: function(body){

            var url = "http://" + this.ip + ":" + this.port + "/cso/edit/output";

            

            axios({ 
                method: "PUT", 
                "url": url, 
                data: body 
            }).then( result => { 
                console.log( result ) 
            });
        },
        
        getAnOutput: function(){

            var url = "http://" + this.ip + ":" + this.port + "/cso/output?id=" + String( this.submitOutput.oid );

            axios({ 
                method: "GET", 
                "url": url 
            }).then(result => {
                this.outputs = result.data;
                
            }, error => {
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
                console.error(error);
            });
            
        },

        deleteOutput: function(id){

            var url = "http://" + this.ip + ":" + this.port + "/cso/delete/output?id=" + String( id );
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
