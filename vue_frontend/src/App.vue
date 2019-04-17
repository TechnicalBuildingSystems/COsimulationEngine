<template>
  <div id="app" class="container">
    <div class="row">
      <nav class="navbar navbar-expand-sm bg-dark navbar-dark fixed-top">
        <a class="navbar-brand" href="/">VIBN</a>
        <div class="collapse navbar-collapse">        
          <span class="my-2 my-lg-0">
            <span class="btn btn-outline-light">Status: 
              <span v-if="!connectionOk" class="badge badge-danger" v-show="!connectionOk" data-toggle="modal" data-target="#exampleModalCenter">Not Connected</span>
              <span v-else-if="connectionOk" class="badge badge-success" v-show="connectionOk" data-toggle="modal" data-target="#exampleModalCenter">Connected to "{{ this.modal.ip }}"</span>
            </span>
          </span>
        </div>
      </nav>
      <!--<img alt="Vue logo" src="./assets/logo.png">-->
      <!--<HelloWorld msg="Welcome to Your Vue.js App"/>-->
      <!--  v-on:click="testConnection()" -->
  
  
      <!-- MODAL -->
      <div class="modal fade" id="exampleModalCenter" tabindex="-1" role="dialog" aria-labelledby="exampleModalCenterTitle" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered" role="document">
          <div class="modal-content">
           <div class="modal-header">
            <h5 class="modal-title" id="exampleModalLongTitle">Set IP and Port of CSO</h5>
            <button type="button" class="close" data-dismiss="modal" aria-label="Close">
              <span aria-hidden="true">&times;</span>
            </button>
          </div>
          <div class="modal-body">
            <form>
              <div class="form-group">
                <label for="csoIP">IP Address</label>
                <input v-model="modal.ip" type="text" class="form-control" id="csoIP" aria-describedby="csoHelp" placeholder="Enter CSO IP Address">
                <small id="csoHelp" class="form-text text-muted">Type in IP Address of CSO.</small>
              </div>
              <div class="form-group">
                <label for="csoPort">Port</label>
                <input v-model="modal.port" type="text" class="form-control" id="csoPort" placeholder="CSO Port">
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>
            <button v-on:click="testConnection()" class="btn btn-primary" data-dismiss="modal">Submit</button>
          </div>
        </div>
        </div>
      </div>
  
      <!-- <input v-if="connectionOk" v-model="this.groupRefe" placeholder="Group Reference">
      <outputComp v-bind:ip="this.ip" v-if="connectionOk" v-bind:serviceRef="this.service"></outputComp>
      <inputComp v-bind:ip="this.ip" v-if="connectionOk" v-bind:groupRef="this.groupRefe" v-bind:serviceRef="this.service" ></inputComp> -->
      
      <!-- NavTab content -->
      <div class="col-lg-3 align-self-start">
        <groupComp ref="groupMain" v-bind:ip="this.modal.ip" v-bind:port="this.modal.port"></groupComp>
      </div>
      <div class="col-lg-9 align-self-end">
        <ul class="nav nav-tabs" id="myTab" role="tablist">
          <li class="nav-item">
            <a class="nav-link active" id="service-tab" data-toggle="tab" href="#home" role="tab" aria-controls="service" v-on:click="selected='service'" aria-selected="true">Services</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" id="input-tab" data-toggle="tab" href="#inputs" role="tab" aria-controls="input" v-on:click="selected='input'" aria-selected="false">Inputs</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" id="output-tab" data-toggle="tab" href="#outputs" role="tab" aria-controls="output" v-on:click="selected='output'" aria-selected="false">Outputs</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" id="run-tab" data-toggle="tab" href="#runs" role="tab" aria-controls="run" v-on:click="selected='run'" aria-selected="false">Runs</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" id="mapping-tab" data-toggle="tab" href="#mappings" role="tab" aria-controls="mapping" v-on:click="selected='mapping'" aria-selected="false">Mappings</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" id="configuration-tab" data-toggle="tab" href="#configs" role="tab" aria-controls="config" v-on:click="selected='config'" aria-selected="false">Configuration</a>
          </li>
          <li class="nav-item">
            <a class="nav-link" id="csm-tab" data-toggle="tab" href="#csm" role="tab" aria-controls="csm" v-on:click="selected='csm'" aria-selected="false">CoSimulationManager</a>
          </li>
        </ul>
        <div id="myTabContent" class="tab-content">    
          <div class="tab-pane fade show active" role="tabpanel" v-bind:id="this.selected" v-bind:aria-labelledby="this.selected + '-tab' ">
            <div class = "container">
              <serviceComp v-bind:groupRef="this.groupRefe" v-bind:ip="this.modal.ip" v-bind:port="this.modal.port" v-show="selected=='service'"></serviceComp>
              <inputComp v-bind:ip="this.modal.ip" v-bind:port="this.modal.port" v-bind:serviceRef="this.service" v-show="selected=='input'"></inputComp>
              <outputComp v-bind:ip="this.modal.ip" v-bind:port="this.modal.port" v-bind:serviceRef="this.service" v-show="selected=='output'"></outputComp>
              <mappingComp v-bind:ip="this.modal.ip" v-bind:port="this.modal.port" v-bind:groupRef="this.groupRefe" v-show="selected=='mapping'"></mappingComp>
              <runComp v-bind:ip="this.modal.ip" v-bind:port="this.modal.port" v-show="selected=='run'"></runComp>
              <csmComp v-bind:ip="this.modal.ip" v-bind:port="this.modal.port" v-show="selected=='csm'"></csmComp>
              <simconfigComp v-bind:ip="this.modal.ip" v-bind:port="this.modal.port" v-bind:group="this.groupRefe" v-show="selected=='config'"></simconfigComp>
            </div>
          </div>
        </div>
        <buttonsComp v-bind:ip="this.modal.ip" v-bind:port="this.modal.port" v-bind:selectedComp="this.selected" ></buttonsComp>
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
import groupComp from './components/groupComp.vue';
import inputComp from './components/inputComp.vue';
import mappingComp from './components/mappingComp.vue';
import outputComp from './components/outputComp.vue';
import runComp from './components/runComp.vue';
import serviceComp from './components/serviceComp.vue';
import simconfigComp from './components/simconfigComp.vue';
import buttonsComp from "./components/buttonsComp.vue";
import csmComp from "./components/csmComp.vue";
import { EventBus } from './main.js';

export default {
  name: 'app',


  data() {
    return {
      run: 1,
      groupRefe: 1,
      service: 1,
      connectionOk: false,
      ip:"localhost",
      modal: {
        ip: "localhost",
        port: "3030"
      },
      selected: 'service',
      componentNames: []

    }
  },
  created(){
    //payLoad is group id
    EventBus.$on( 'group-selected', payLoad => { this.groupRefe = payLoad } );
  }, 

  mounted(){        
    this.testConnection();
  },


  components: {
    groupComp,
    inputComp,
    mappingComp,
    outputComp,
    runComp,
    serviceComp,
    simconfigComp,
    buttonsComp,
    csmComp
  },

  methods: {

    testConnection: function(){
      /*eslint no-console: ["error", { allow: ["warn", "error" , "log"] }] */
      var url = "http://" + this.modal.ip + ":" + this.modal.port + "/cso/testConnection";
      axios({
                method: "GET",
                "url": url
            }).then( result => {
                console.log( result );
                if( result.status == 200)
                  this.connectionOk = true
            }, error => {
                console.error(error);
                this.connectionOk = false;
      });
    },
     
    changeGroupRef: function(id){
      this.groupRefe = id;
    },

  }
}


</script>

<style>
@import '../node_modules/bootstrap/dist/css/bootstrap.css';

#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
.tab-pane {

    border-left: 1px solid #ddd;
    border-right: 1px solid #ddd;
    border-bottom: 1px solid #ddd;
    border-radius: 0px 0px 5px 5px;
    padding: 10px;
}

.nav-tabs {
    margin-bottom: 0;
}
</style>
