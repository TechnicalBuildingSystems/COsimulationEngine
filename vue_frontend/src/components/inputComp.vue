<template>
    <div id = "inputComp">      
        <table class="table table-bordered table-hover">
            <thead>
                <tr>
                    <th v-for="inputKeys in Object.keys(submitInput)" v-bind:key="inputKeys" scope="col"> {{ inputKeys.toUpperCase() }} </th>
                </tr>
            </thead>
            <tbody v-if="this.validation.valid">
                <tr v-for="(input,index) in inputs" v-bind:key="index" v-bind:class="{ 'table-active' : validation.selectedIndex == index }" v-on:click="changeIndex(index)">
                    <td>{{ input.id }}</td>
                    <td>{{ input.name }}</td>
                    <td>{{ input.sid }}</td>
                    <td>{{ input.initialValue }}</td>
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
    name: 'inputComp',

    props: {
        ip: String,
        port: String
    },
    
    data() {
        return {
            deleteId: 0,
            submitInput: { 
                id: 0, 
                name: '', 
                sid: 0, 
                initialValue: 0.0
                },
            inputs: [] ,
            validation: {
                valid: false,
                selectedIndex : Number
            },
            serviceRef: Number
        }
    },

    created(){
        //payLoad is service id
        EventBus.$on( 'service-selected', payLoad => { 
            this.serviceRef = payLoad.id;
            this.refresh();
            } );

        EventBus.$on( 'delete-input-submitted' , payLoad => {
            this.deleteInput(payLoad.id);
        } );

        EventBus.$on( 'add-input-submitted' , payLoad => {
            this.createInput(payLoad)
        } )

        EventBus.$on( 'edit-input-submitted' , payLoad => {
            this.editInput(payLoad)
        } )

        EventBus.$on('refresh-all', this.refresh );
    },
    mounted(){

        this.refresh();
        this.validation.valid = true;
    },

    methods: {

        refresh: function(){

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/inputs?service=" + String( this.serviceRef );

            axios({ 
                method: "GET", 
                "url": url 
            }).then( result => {
                this.inputs = result.data;
            }, error => {
                console.error(error);
            });
            
        }, 

        changeIndex: function(num){
            this.validation.selectedIndex = num;
            this.submitInput.id = this.inputs[num].id;
            this.submitInput.initialValue = this.inputs[num].initialValue;
            this.submitInput.name = this.inputs[num].name;
            this.submitInput.sid = this.inputs[num].sid;
            EventBus.$emit( 'input-selected' , this.submitInput )
        },

        createInput: function(body){

            var url = "http://" + this.ip + ":" + this.port + "/cso/create/input";

            
            /*eslint no-console: ["error", { allow: ["warn", "error", "log"] }] */
            axios({ 
                method : "POST", 
                "url" : url, 
                data : body 
            }).then( result => { 
                console.log(result) 
            })
            
        },

        editInput: function(body){

            var url = "http://" + this.ip + ":" + this.port + "/cso/edit/input";


            axios({ 
                method: "PUT", 
                "url": url, 
                data: body 
            }).then( result => { 
                console.log( result ) 
            });
        },

        getAnInput: function(){
            var url = "http://" + this.ip + ":" + this.port + "/cso/input?id=" + String( this.submitInput.iid );

            axios({ 
                method: "GET", 
                "url": url 
            }).then(result => {
                this.inputs = result.data;
                
            }, error => {
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
                console.error(error);
            });
            
        },

        deleteInput: function(id){

            var url = "http://" + this.ip + ":" + this.port + "/cso/delete/input?id=" + String( id );
            /*eslint no-console: ["error", { allow: ["warn", "error", "log"] }] */
            console.log(url);
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


