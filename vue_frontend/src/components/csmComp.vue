<template>
    <div id="csmComp">
        <div class="container">
            <div class="row justify-content-md-center">
                <div class ="col-lg-auto form-group">                
                    THIS WILL BE PLOT<br /> 
                    THIS WILL BE PLOT<br /> 
                    THIS WILL BE PLOT<br /> 
                    THIS WILL BE PLOT<br /> 
                    THIS WILL BE PLOT<br /> 
                    THIS WILL BE PLOT<br /> 
                    THIS WILL BE PLOT<br /> 
                    THIS WILL BE PLOT<br /> 
                    THIS WILL BE PLOT<br /> 
                    THIS WILL BE PLOT<br /> 
                    THIS WILL BE PLOT<br /> 
                    THIS WILL BE PLOT<br /> 
                    THIS WILL BE PLOT<br /> 
                </div>
                <div class ="col-lg-auto form-group">                
                    THIS WILL BE TABLE<br />
                    THIS WILL BE TABLE<br />
                    THIS WILL BE TABLE<br />
                    THIS WILL BE TABLE<br />
                    THIS WILL BE TABLE<br />
                    THIS WILL BE TABLE<br />
                    THIS WILL BE TABLE<br />
                    THIS WILL BE TABLE<br />
                    THIS WILL BE TABLE<br /> 
                    THIS WILL BE TABLE<br /> 
                </div>
            </div>
            <div class="row justify-content-lg-center form-group">
                <div class="w-100 d-none d-md-block"></div>
                <div class="form-check form-check-inline">                   
                    <div class="col-md-auto" v-for="(coloumn, index) in tableColoumns" v-bind:key="index">
                        <input class="form-check-input" type="checkbox" v-bind:id="coloumn" v-bind:value="coloumn" v-model="checkedVars">
                        <label class="form-check-label" v-bind:for="coloumn">{{coloumn}}</label>
                    </div>
                    <br/>
                    <span>Checked Variables: {{ checkedVars }}</span>
                </div>
            </div>
            <div class="row justify-content-lg-center form-group">
                <div class="col-md-auto">
                    STATUS MESSAGE
                </div>
                <div class="col-md-auto">
                    BUTTONS
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

    name: "csmComp",
    props: {
        ip: String,
        port: String
    },
   
    data() {

        return {
            csmSettings: {
                gid: 0,
                rid: 0
            },
            tableName: '',
            checkedVars: [],
            tableColoumns: [],
            tableColoumnsAll:[],
            values: [],
            csmStateRunning: false,
            csmSuccessful: false,
            csmInitiateStatus: 'not initiated',
            tempConfig: {}
        }
    },


    created(){

        EventBus.$on( 'run-selected' , payLoad => {
            this.csmSettings.gid = payLoad.gid
            this.csmSettings.rid = payLoad.id
            this.tableName = payLoad.tableName
            this.getTableKeys()
            this.getValues()
        }),

        EventBus.$on( 'config-selected' , payLoad => {
            this.tempConfig = payLoad
        })
    },
    mounted(){},

    methods: {

        initiateCSM: function(){
            var url = "http://" + this.ip + ":" + this.port + "/cso/initiateCSM?gid=" + String(this.csmSettings.gid) + "&rid=" + String( this.csmSettings.rid);

            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                if(result.status == 200){
                    this.csmInitiateStatus = 'initiated';
                }
                }, error => {
                    console.error(error);
                } )
        },

        runCSM: function(){
            var url = "http://" + this.ip + ":" + this.port + "/cso/runCSM";

            this.csmStateRunning = true;
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                if(result.status == 200){
                    this.csmStateRunning = false;
                    this.csmSuccessful = true;
                }
                }, error => {
                    console.error(error);
                } )
        },

        getTableKeys: function(){

            var url = "http://" + this.ip + ":" + this.port + "/cso/tableKeys?tname=" + this.tableName;
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */

            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                for( var i = 0; i < result.data.length; i++ ){
                    if( i > 2){
                        this.tableColoumns.push(result.data[i])
                    }
                    this.tableColoumnsAll.push(result.data[i])
                }
                }, error => {
                    console.error(error);
                } )


        },
        getValues: function(){

            var url = "http://" + this.ip + ":" + this.port + "/cso/values?rid=" + String(this.csmSetting.rid);
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                for( var i = 0; i < result.length; i++ ){
                    this.values.push(result[i])
                }
                }, error => {
                    console.error(error);
                } )
        }
    }
}
</script>

<style>

</style>
