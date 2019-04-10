<template>
    <div id="groupComp">
        <table class="table table-bordered table-hover">
            <thead>
                <tr>
                    <th v-for="formKeys in Object.keys(groupForms)" v-bind:key="formKeys" scope="col">{{ formKeys.toUpperCase() }}</th>
                </tr>
            </thead>
            <tbody v-if="this.validation.valid">
                <tr v-for="(group, index) in groups" v-bind:class="{'table-active': validation.selectedIndex == index }" v-bind:key="index" v-on:click="changeIndex(index); validation.groupSelected = true; setForms(group.id, group.name)">
                    <td>{{group.id}}</td>
                    <td>{{group.name}}</td>
                </tr>
            </tbody>
        </table>
        <form>
            <div class="form-row">
                <div class="col">
                <input type="text" v-model="groupForms.id" class="form-control" placeholder="Group ID" v-bind:disabled="!validation.groupSelected">
                </div>
                <div class="col">
                <input type="text" v-model="groupForms.name" class="form-control" placeholder="New groupname">
                </div>
            </div>
            <div class="form-row">
                <div class="col">
                    <button type="button" class="btn btn-success btn-sm" v-on:click="createGroup(groupForms)">Add Group</button>
                    <button type="button" class="btn btn-secondary btn-sm" v-on:click="editGroup(groupForms)" v-bind:disabled="!validation.groupSelected">Edit</button>
                    <button type="button" class="btn btn-danger btn-sm" v-bind:disabled="!validation.groupSelected" data-toggle="modal" data-target="#deleteGroupConfirm">Delete</button>
                    <button type="button" class="btn btn-link btn-sm" v-on:click="getGroups()">Refresh</button>
                </div>
            </div>
        </form>
        
        <!-- MODAL -->
        <div class="modal fade" id="deleteGroupConfirm" tabindex="-1" role="dialog" aria-labelledby="deleteConfirm" aria-hidden="true">
            <div class="modal-dialog modal-dialog-centered" role="document">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="exampleModalLongTitle">Set IP and Port of CSO</h5>
                        <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                            <span aria-hidden="true">&times;</span>
                        </button>
                    </div>
                    <div class="modal-body">
                    Are you sure of deleting following group: ID: {{ groupForms.id }}, Name: {{ groupForms.name }}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
                        <button v-on:click="deleteGroup(groupForms.id)" class="btn btn-primary" data-dismiss="modal">Submit</button>
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
    name: 'groupComp',

    props: {
        ip: String,
        port: String
    },

    data() {

        return {
            groups: [],
            groupForms: {
                id: 0, 
                name: ''
            },

            validation: {
                valid: false,
                selectedIndex : Number,
                groupSelected: false
            }
        }
    },

    components:{
    },

    created(){

        //payload is group as json body
        EventBus.$on('add-group-submitted', payLoad => {  
            this.createGroup(payLoad)
        });


        //payload is group as json body
        EventBus.$on('edit-group-submitted', payLoad => {  
            this.editGroup(payLoad)
        });

        //payload is id
        EventBus.$on('delete-group-submitted', payLoad => {  
            this.deleteGroup(payLoad)
        });
    },

    mounted() {
        this.getGroups();
        
    },

    methods: {

        changeIndex: function(num){
            this.validation.selectedIndex = num;
            this.groupSelected(this.groups[num].id);
        },

        setForms: function(gid, gname){
            
            this.groupForms.id = gid;
            this.groupForms.name = gname;
        },

        createGroup: function(body){
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/create/group"
            
            axios({
                method: "POST",
                "url" : url,
                data: body
            }).then( result => { 
                this.getGroups(); })
        },

        editGroup: function(body){

            var url = "http://" + this.ip + ":" + this.port + "/cso/edit/group"
            

            axios({
                method: "PUT",
                "url" : url,
                data: body
            }).then( result => { 
                this.getGroups(); })
        }, 

        getGroup: function(){

            var url = "http://" + this.ip + ":" + this.port + "/cso/group?id=" + String( this.groupForms.id )
            
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.groups.push( result.data );
                } )
        },
        
        getGroups: function(){
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/groups"
            console.log( url )
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.groups = result.data;  
                this.validation.valid = true; 
                }, error => {
                    console.error(error);
                    this.validation.valid = false;
                } )
        },

        deleteGroup: function(id){
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            var url = "http://" + this.ip + ":" + this.port + "/cso/delete/group?id=" + String( id )

            axios({
                method: "DELETE",
                "url" : url
            }).then( result => { 
                this.getGroups();
                } )
        },
        
        //Fires event for runComp, mappingComp, serviceComp
        groupSelected: function(id){
            
            EventBus.$emit('group-selected', id )
        }
    }
}
</script>

<style>

</style>
