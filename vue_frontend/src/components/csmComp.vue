<template>
    <div id="csmComp">
        <div class="container">
            <div class="row justify-content-lg-center form-group">
                <div class="col-md-auto">
                    STATUS MESSAGE: {{ csmInitiateStatus }}
                </div>
            </div>
            <div class="col-md-auto" style="height:50vh; width:80vw">
                <canvas id="myChart"></canvas>
            </div>

            <div class="btn-group btn-group-justified">
                <div class="btn-group">
                    <button type="button" v-on:click="initiateCSM()" class="btn btn-primary" >Initiate CSM</button>
                </div>
                <div class="btn-group">
                    <button type="button" v-on:click="runCSM()" class="btn btn-primary" >Run CSM</button>
                </div>
                <div class="btn-group">
                    <button type="button" v-on:click="getValues()" class="btn btn-primary" >getValues</button>
                </div>                
                <div class="btn-group">
                    <button type="button" v-on:click="renderGraph('myChart')" class="btn btn-primary" >Plot</button>
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
import { Line } from 'vue-chartjs'
import Chart from 'chart.js';



export default {
    extends : Line,
    name: "csmComp",    
    props: {
        ip: String,
        port: String
    },
    
    
    data() {

        return {
            csmSettings: {
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
            tempConfig: {},
            dbdata: {},
            plotoptions: {
                responsive: true,
                lineTension: 1,
                elements: {
                    line: {
                        tension: 0
                    }
                },
                scales: {
                    yAxes: [{
                    ticks: {
                        beginAtZero: true,
                        padding: 25,
                    }
                    }]
                }
            }
            
        }
    },


    created(){

        EventBus.$on( 'run-selected' , payLoad => {
            this.csmSettings.gid = payLoad.gid
            this.csmSettings.rid = payLoad.id
            this.tableName = payLoad.tableName
            this.getValues()
        }),

        EventBus.$on( 'config-selected' , payLoad => {
            this.tempConfig = payLoad
        })

    },
    mounted(){

    },

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
            this.csmInitiateStatus = 'CSM Running...';
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                if(result.status == 200){
                    this.csmStateRunning = false;
                    this.csmSuccessful = true;
                    this.csmInitiateStatus = 'CSM Successfully run.';
                }
                }, error => {
                    console.error(error);
                } )
        },


        getRandomColor: function() {
            var letters = '0A268BCDEF134579';
            var color = '#';
            for (var i = 0; i < 6; i++) {
                color += letters[Math.floor(Math.random() * 16)];
            }
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            console.log(color)
            return color;
            },

        getValues: function(){

            var url = "http://" + this.ip + ":" + this.port + "/cso/getValues?rid=" + String(this.csmSettings.rid);
            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            axios({
                method: "GET",
                "url" : url
            }).then( result => { 
                this.tableColoumnsAll = Object.keys(result.data)

                for( var j = 0; j < this.tableColoumnsAll.length; j++){
                    
                    if( this.tableColoumnsAll[j].includes("inputs") || this.tableColoumnsAll[j].includes("outputs") ){
                        this.tableColoumns.push(this.tableColoumnsAll[j])
                    }
                }                        
                
                this.dbdata = result.data

                }, error => {
                    console.error(error);
            } )
        },


        renderGraph: function(chartId){
            
            var computedData = {}

            computedData.labels = this.dbdata.timestamp
            console.log(this.dbdata)
            computedData.datasets = []

            for( var i = 0; i < this.tableColoumns.length; i++){

                computedData.datasets[i] = {}

                computedData.datasets[i].label = this.tableColoumns[i]

                computedData.datasets[i].data = this.dbdata[this.tableColoumns[i]]

                computedData.datasets[i].fill = false
                computedData.datasets[i].borderColor = [ this.getRandomColor(), ]

                computedData.datasets[i].borderWidth = 3

            }


            /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
            console.log(computedData)

            const ctx = document.getElementById(chartId)
            const myChart = new Chart( ctx , {
                type : 'line',
                data : computedData,
                options: this.plotoptions
            })
        }
    }
}
</script>

<style>

</style>
