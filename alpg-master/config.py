#!/usr/bin/python3    

# Artifical load profile generator v1.0, generation of artificial load profiles to benchmark demand side management approaches
# Copyright (C) 2016 Gerwin Hoogsteen

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.




# This is an example configuration file!

import random, csv, io, os, numpy, datetime, math
import dateutil.parser as parser
# For this dependency: run "sudo pip install astral"
from astral import Astral
import pandas as pd
import mysql
import DB_config

import profilegentools

## Please select your output writer of preference
import writer as writer

# import trianawriter as writer

# Random seed
seed = 42;
random.seed(seed)

# In- and out files:
# Folder to write the output to
folder = 'out'

# input files:
weather_irradiation = 'solarirradiation.csv'
weather_timebaseDataset = 3600  # in seconds per interval

# Simulation:



# number of days to simulate and skipping of initial days. Simulation starts at Sunday January 1.
numDays = 365  # number of days
startDay = 0  # Initial day

device_id = 0
# time series for 2015, sampling interval: 60 seconds
time_index = pd.date_range('1/1/2015', periods=numDays * 24 * 60, freq='60S')

# Select the geographic location. Refer to the Astral plugin to see available locations (or give a lon+lat)
city_name = 'Copenhagen'
a = Astral()
a.solar_depression = 'civil'
city = a[city_name]

# Select the devices in the neighbourhood

# Devices
# Scale overall consumption:
consumptionFactor = 1.0  # consumption was a bit too high

# Penetration of emerging technology in percentages
# all values must be between 0-100
penetrationEV = 13
penetrationPHEV = 32
penetrationPV = 50
penetrationBattery = 10  # Note only houses with PV will receive a battery!
penetrationInductioncooking = 25

# Device parameters:
# EV
capacityEV = 42000  # Wh
powerEV = 7400  # W
capacityPHEV = 12000  # Wh
powerPHEV = 3700  # W

# PV
PVProductionPerYear = 220  # kWh
PVAngleMean = 35  # degrees
PVAngleSigma = 10  # degrees
PVSouthAzimuthSigma = 90  # degrees
PVEfficiencyMin = 15  # % of theoretical max
PVEfficiencyMax = 20  # % of theoretical max

# Driving distances
commuteDistanceMean = 25  # km
commuteDistanceSigma = 10  # km

# Battery
capacityBatteryLarge = 12000  # Wh
capacityBatteryMedium = 5000  # Wh
capacityBatterySmall = 2000  # Wh
powerBatteryLarge = 3700  # W
powerBatteryMedium = 3700  # W
powerBatterySmall = 3700  # W

# Kitchen
# Consumption of devices
ConsumptionOven = 2000  # W
ConsumptionMicroWave = 800  # W
ConsumptionStoveVentilation = 120  # W #But this is maximum, usually set lower!
ConsumptionInductionStove = 2200  # W #http://homeguides.sfgate.com/many-watts-induction-stove-85380.html

ConsumptionFridgeBigMin = 80  # W
ConsumptionFridgeBigMax = 120  # W
ConsumptionFridgeSmallMin = 50  # W
ConsumptionFridgeSmallMax = 80  # W

ConsumptionKettle = 2000  # W

# White goods
ConsumptionIron = 2000  # W
ConsumptionVacuumcleaner = 1500  # W

# House
ConsumptionHouseVentilation = 50  # W

# Household randomization
# all values must be between 0-1000
familyOutingChanceMin = 10  # percentage
familyOutingChanceMax = 20  # percentage
personWeekdayActivityChanceMin = 20  # percentage
personWeekdayActivityChanceMax = 30  # percentage
personWeekendActivityChanceMin = 20  # percentage
personWeekendActivityChanceMax = 30  # percentage

# Select the types of households
import households

householdList = []

for i in range(0, 5):
    householdList.append(households.HouseholdSingleWorker())

for i in range(0, 5):
    householdList.append(households.HouseholdSingleRetired())

for i in range(0, 5):
    householdList.append(households.HouseholdDualWorker(True))

for i in range(0, 5):
    householdList.append(households.HouseholdDualWorker(False))

for i in range(0, 5):
    householdList.append(households.HouseholdDualRetired())

for i in range(0, 5):
    householdList.append(households.HouseholdFamilyDualWorker(True))

for i in range(0, 5):
    householdList.append(households.HouseholdFamilyDualWorker(False))

for i in range(0, 5):
    householdList.append(households.HouseholdFamilySingleWorker(True))

numHouses = len(householdList)


def cleanup_db():
    db_con_string = mysql.connector.connect(host=DB_config.host, database=DB_config.database, user=DB_config.user,
                                            password=DB_config.password)
    cursor = db_con_string.cursor()
    query = "truncate table LogWatt"
    cursor.execute(query)
    db_con_string.commit()

    query = "truncate table PCBoks"
    cursor.execute(query)
    db_con_string.commit()

    query = "truncate table PCBoksUnits"
    cursor.execute(query)
    db_con_string.commit()

    query = "truncate table Unit"
    cursor.execute(query)
    db_con_string.commit()

    db_con_string.close()


### DO NOT EDIT BEYOND THIS LINE ###
# WARNING: The following option is untested:
# Output timebase in seconds
timeBase = 60  # must be a multiple of 60

# Do no touch this:
intervalLength = int(timeBase / 60)  # set the rate in minutes, normal in minute intervals

# TRIANA SPECIFIC SETTINGS
# Control
# TODO MAKE USE OF IT
TrianaPlanning_LocalFlat = True
TrianaPlanning_ReplanningInterval = 96
TrianaPlanning_Horizon = 192
TrianaPlanning_MaximumIterations = 5
TrianaPlanning_MinImprovenemt = 10
trianaModelPath = 'models/newr/'
