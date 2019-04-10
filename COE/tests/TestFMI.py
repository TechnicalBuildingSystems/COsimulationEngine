# -*- coding: utf-8 -*-
"""
Created on Fri Aug 03 15:05:10 2018

@author: geos
"""

# Muss FMU fuer CoSimulation bekommen!
# !!! Aufpassen: modelIdentifier muss namen der FMU bekommen 



# Packages to import
from fmpy import *
from fmpy.fmi2 import FMU2Slave
import shutil
import os


###   ###   ###   ###   ###   ###   
# loadFMU
pathToFmu = "/home/ibp/Documents/ControlledTemperature.fmu"
print( pathToFmu )
dump( pathToFmu )

model_description = read_model_description( pathToFmu )
unzipdir = extract( pathToFmu )

# get value references

vrs = {}

for variable in model_description.modelVariables:
    vrs[ variable.name ] = variable.valueReference
    print( "Variable name \t" , variable.name , "Variable reference \t" ,  variable.valueReference )

fmu = FMU2Slave( guid            = model_description.guid ,
                 unzipDirectory  = unzipdir ,
                 modelIdentifier = model_description.coSimulation.modelIdentifier ,
                 instanceName	 = "instance1")

###   ###   ###   ###   ###   ###   
# Init FMU
start_time = 0.0
stop_time = 30.0
step_size = 1.0
time = start_time
results = [] # list to record the results

fmu.instantiate()
fmu.setupExperiment( startTime = start_time )
fmu.enterInitializationMode()
fmu.exitInitializationMode()


###   ###   ###   ###   ###   ###   

# simulation loop
while time < stop_time:

    # Set inputs
    fmu.setReal( [ vrs[ u"u" ] ] , [ 273.15 + 20 if time < 10 else 273.15 + 30 ] )
    
    # do_step
    fmu.doStep( currentCommunicationPoint = time ,
                communicationStepSize     = step_size )
    # getOutputs
    otp = fmu.getReal( [ vrs[ u"TemperatureOut" ] ] )
    print( "time:\t" , time , "result:\t" , otp )
    # Store calculated result
    results.append( ( time , otp ) )


    # advance the time
    time += step_size
    print( "Time is: " , time , "value is" , otp )

fmu.terminate()
fmu.freeInstance()

# clean up
shutil.rmtree( unzipdir )

for row in results:
   print( "time :" , row[ 0 ] , "y" , row[ 1 ] )

