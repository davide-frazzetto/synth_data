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



import random, math, copy, datetime, os

import profilegentools
import config
import mysql.connector

import config



CHUNK_SIZE = 1000

def insert_many(load, time_index, device_id):
    index = 0
    while True:

        if index >= len(load):
            break

        values_str = ", ".join(
            "('{0}', '{1}', '{2}')".format(time_index[i], load[i], device_id)
            for i in range(index, min(index + CHUNK_SIZE, len(load)))
        )

        sql = "INSERT INTO LogWatt (date, watt, unitID) VALUES {0}".format(values_str)

        db_con_string = mysql.connector.connect(host='localhost', database='genetx', user='root',
                                               password='gattovolante666')
        cursor = db_con_string.cursor()
        cursor.execute(sql)
        db_con_string.commit()

        index += CHUNK_SIZE
    db_con_string.close()



def write_house(house):
    db_con_string = mysql.connector.connect(host='localhost', database='genetx', user='root',
                                            password='gattovolante666')
    cursor = db_con_string.cursor()
    query = "INSERT INTO PCBoks(pcBoksID) VALUES(" + str(house) + ")"
    cursor.execute(query, house)
    db_con_string.commit()
    db_con_string.close()


def write_device(device_name, house, load, time_index):
    db_con_string = mysql.connector.connect(host='localhost', database='genetx', user='root',
                                                   password='gattovolante666')
    cursor = db_con_string.cursor(prepared=True)
    if len(load) != len(time_index):
        raise Exception

    # insert device
    query = "INSERT INTO Unit(unitID, ApparatType) VALUES (%s, %s)"
    cursor.execute(query, (config.device_id, device_name,))
    db_con_string.commit()

    query = "INSERT INTO PCBoksUnits(unitID, PCBoksID) VALUES(%s, %s)"
    cursor.execute(query, (config.device_id, house,))
    db_con_string.commit()

    insert_many(load, time_index, config.device_id)


    config.device_id += 1


def device_time_series_generator(times, profile):
    column = [0] * (config.numDays * 24 * 60)
    for activation_second in times:
        starting_index = int(activation_second) / 60
        for i in range(len(profile)):
            # profile--index 0: active power, index 1: reactive power
            column[starting_index + i] = float(profile[i].split(',')[0])

    return column


def writeCsvLine(fname, hnum, line):
    if not os.path.exists(config.folder + '/' + fname):
        # overwrite
        f = open(config.folder + '/' + fname, 'w')
    else:
        # append
        f = open(config.folder + '/' + fname, 'a')
    f.write(line + '\n')
    f.close()


def writeCsvRow(fname, hnum, data):
    if hnum == 0:
        with open(config.folder + '/' + fname, 'w') as f:
            for l in range(0, len(data)):
                f.write(str(round(data[l])) + '\n')
    else:
        with open(config.folder + '/' + fname, 'r+') as f:
            lines = f.readlines()
            f.seek(0)
            f.truncate()
            j = 0
            for line in lines:
                line = line.rstrip()
                line = line + ';' + str(round(data[j])) + '\n'
                f.write(line)
                j = j + 1


def writeNeighbourhood(num):
    pass


# Write specific neighbourhood data if required, see the Triana example:
# configFile = []
# configFile.append('\tif houseNum == '+str(num)+':')
# configFile.append('\t\timport out.House'+str(num))
# configFile.append('\t\tout.House'+str(num)+'.addHouse(node, coordx, coordy, phase, houseNum, control, masterController, cfg)')

# if num == 0:
##overwrite
# f = open(config.folder+'/neighbourhood.py', 'w')
# else:
##append
# f = open(config.folder+'/neighbourhood.py', 'a')
# for line in range(0, len(configFile)):
# f.write(configFile[line] + '\n')
# f.close()

# def write_non_flex_dev_to_db(device_name, house_num, load):
#     db_con_string = mysql.connector.connect(host='localhost', database='genetx', user='root',
#                                             password='gattovolante666')
#
#     time_index = config.time_index
#     cursor = db_con_string.cursor(prepared=True)
#     if len(load) != len(time_index):
#         raise Exception
#
#     # insert device
#     query = "INSERT INTO Unit(unitID, ApparatType) VALUES (%s, %s)"
#     cursor.execute(query, (config.device_id, device_name,))
#     db_con_string.commit()
#
#     query = "INSERT INTO PCBoksUnits(unitID, PCBoksID) VALUES(%s, %s)"
#     cursor.execute(query, (config.device_id, house_num,))
#     db_con_string.commit()
#
#     query = "INSERT INTO LogWatt(date, watt, unitID) VALUES"
#     # combine time index and load
#     for i in range(len(time_index)):
#         query += "('" + str(time_index[i]) + "'," + str(load[i]) + "," + str(config.device_id) + ")"
#         if i < len(time_index) -1:
#             query += ",\n"
#
#     query += ";\n"
#
#     if not os.path.exists(config.folder + '/' + "insert"):
#         # overwrite
#         f = open(config.folder + '/' + "insert", 'w')
#     else:
#         # append
#         f = open(config.folder + '/' + "insert", 'a')
#     f.write(query)
#     f.close()
#
#     config.device_id += 1


def writeHousehold(house, num):
    #write house

    write_house(num)


    # Save the profile:
    # writeCsvRow('Electricity_Profile.csv', num, house.Consumption['Total'])
    # writeCsvRow('Electricity_Profile_Groupother.csv', num, house.Consumption['Other'])
    # writeCsvRow('Electricity_Profile_GroupInductive.csv', num, house.Consumption['Inductive'])
    # writeCsvRow('Electricity_Profile_GroupFridges.csv', num, house.Consumption['Fridges'])
    # writeCsvRow('Electricity_Profile_GroupElectronics.csv', num, house.Consumption['Electronics'])
    # writeCsvRow('Electricity_Profile_GroupLighting.csv', num, house.Consumption['Lighting'])
    # writeCsvRow('Electricity_Profile_GroupStandby.csv', num, house.Consumption['Standby'])

    # write to DB
    write_device('utility-primary-meter', num, house.Consumption['Total'], config.time_index)
    write_device('kitchen-appliances', num, house.Consumption['Other'], config.time_index)
    write_device('refrigerator', num, house.Consumption['Fridges'], config.time_index)
    write_device('electronics', num, house.Consumption['Electronics'], config.time_index)
    write_device('lighting', num, house.Consumption['Lighting'], config.time_index)



    # writeCsvRow('Reactive_Electricity_Profile.csv', num, house.ReactiveConsumption['Total'])
    # writeCsvRow('Reactive_Electricity_Profile_Groupother.csv', num, house.ReactiveConsumption['Other'])
    # writeCsvRow('Reactive_Electricity_Profile_GroupInductive.csv', num, house.ReactiveConsumption['Inductive'])
    # writeCsvRow('Reactive_Electricity_Profile_GroupFridges.csv', num, house.ReactiveConsumption['Fridges'])
    # writeCsvRow('Reactive_Electricity_Profile_GroupElectronics.csv', num, house.ReactiveConsumption['Electronics'])
    # writeCsvRow('Reactive_Electricity_Profile_GroupLighting.csv', num, house.ReactiveConsumption['Lighting'])
    # writeCsvRow('Reactive_Electricity_Profile_GroupStandby.csv', num, house.ReactiveConsumption['Standby'])

    # Write all devices:
    for k, v, in house.Devices.items():
        house.Devices[k].writeDevice(num)

    # House specific devices
    # if house.House.hasPV:
    #     text = str(num) + ':'
    #     text += str(house.House.pvElevation) + ',' + str(house.House.pvAzimuth) + ',' + str(
    #         house.House.pvEfficiency) + ',' + str(house.House.pvArea)
    #     writeCsvLine('PhotovoltaicSettings.txt', num, text)
    #
    # writeCsvRow('Electricity_Profile_PVProduction.csv', num, house.PVProfile)
    #
    # if house.House.hasBattery:
    #     text = str(num) + ':'
    #     text += str(house.House.batteryPower) + ',' + str(house.House.batteryCapacity) + ',' + str(
    #         round(house.House.batteryCapacity / 2))
    #     writeCsvLine('BatterySettings.txt', num, text)


def writeDeviceBufferTimeshiftable(machine, hnum):
    if machine.BufferCapacity > 0 and len(machine.StartTimes) > 0:
        text = str(hnum) + ':'
        text += profilegentools.createStringList(machine.StartTimes, None, 60)
        writeCsvLine('ElectricVehicle_Starttimes.txt', hnum, text)

        text = str(hnum) + ':'
        text += profilegentools.createStringList(machine.EndTimes, None, 60)
        writeCsvLine('ElectricVehicle_Endtimes.txt', hnum, text)

        text = str(hnum) + ':'
        text += profilegentools.createStringList(machine.EnergyLoss, None, 1, False)
        writeCsvLine('ElectricVehicle_RequiredCharge.txt', hnum, text)

        text = str(hnum) + ':'
        text += str(machine.BufferCapacity) + ',' + str(machine.Consumption)
        writeCsvLine('ElectricVehicle_Specs.txt', hnum, text)

def writeDeviceTimeshiftable(machine, hnum):
    if (machine.name == "WashingMachine" or machine.name == "Dishwasher") and len(machine.StartTimes) > 0:
        text = str(hnum) + ':'
        text += profilegentools.createStringList(machine.StartTimes, None, 60)
        # writeCsvLine('WashingMachine_Starttimes.txt', hnum, text)
        starting_times = text.split(":")[1].split(",")

        # text = str(hnum) + ':'
        # text += profilegentools.createStringList(machine.EndTimes, None, 60)
        # # writeCsvLine('WashingMachine_Endtimes.txt', hnum, text)

        text = str(hnum) + ':'
        text += machine.LongProfile
        # writeCsvLine('WashingMachine_Profile.txt', hnum, text)
        load_series = device_time_series_generator(starting_times, machine.LongProfile.replace("complex","").replace("(","").split("),"))
        write_device(machine.name, hnum, load_series, config.time_index)



