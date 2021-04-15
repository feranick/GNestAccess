#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
***********************************************************
* Google Nest Device Access GNestAccess
* version: 20210414a
* By: Nicola Ferralis <feranick@hotmail.com>
***********************************************************
'''
print(__doc__)

import requests, sys, os.path, time, configparser, logging
from datetime import datetime
from pathlib import Path

def main():
    g = GoogleNest()
    g.getToken()
    #g.refreshToken()
    g.getStructures()
    g.getDevices()
    g.getDeviceStats(g.device_0_name)
    g.getDeviceStats(g.device_1_name)
    #g.setDeviceTemperature(g.device_1_name, 18)
    #g.setFanON(g.device_1_name)

####################################################################
# Class GoogleNest
####################################################################
        
class GoogleNest:
    def __init__(self):
        self.conf = GNestConfig()
        self.url = 'https://nestservices.google.com/partnerconnections/'+self.conf.project_id+'/auth?redirect_uri='+self.conf.redirect_uri+'&access_type=offline&prompt=consent&client_id='+self.conf.client_id+'&response_type=code&scope=https://www.googleapis.com/auth/sdm.service'
        
        print(self.url)
        self.code = input("\nType code: ")
        
        self.params = (
            ('client_id', self.conf.client_id),
            ('client_secret', self.conf.client_secret),
            ('code', self.code),
            ('grant_type', 'authorization_code'),
            ('redirect_uri', self.conf.redirect_uri),
        )
    
    # Get tokens
    def getToken(self):

        response = requests.post('https://www.googleapis.com/oauth2/v4/token', params=self.params)

        response_json = response.json()
        print(response_json)
        self.access_token = response_json['token_type'] + ' ' + str(response_json['access_token'])
        print('Access token: ' + self.access_token)
        self.refresh_token = response_json['refresh_token']
        print('Refresh token: ' + self.refresh_token)

    # Refresh token
    def refreshToken(self):
        response = requests.post('https://www.googleapis.com/oauth2/v4/token', params=self.params)

        response_json = response.json()
        self.access_token = response_json['token_type'] + ' ' + response_json['access_token']
        print('Access token: ' + self.access_token)
        
    # Get structures
    def getStructures(self):
        url_structures = 'https://smartdevicemanagement.googleapis.com/v1/enterprises/' + self.conf.project_id + '/structures'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.access_token,
            }

        response = requests.get(url_structures, headers=headers)
        print(response.json())
        
    # Get devices
    def getDevices(self):
        url_get_devices = 'https://smartdevicemanagement.googleapis.com/v1/enterprises/' + self.conf.project_id + '/devices'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.access_token,
            }

        response = requests.get(url_get_devices, headers=headers)
        print(response.json())

        response_json = response.json()
        self.device_0_name = response_json['devices'][0]['name']
        self.device_1_name = response_json['devices'][1]['name']
        print(self.device_0_name)
        print(self.device_1_name)

    # Get Device Stats
    def getDeviceStats(self, device):
        url_get_device = 'https://smartdevicemanagement.googleapis.com/v1/' + device

        headers = {
        'Content-Type': 'application/json',
        'Authorization': self.access_token,
        }

        response = requests.get(url_get_device, headers=headers)

        response_json = response.json()
        humidity = response_json['traits']['sdm.devices.traits.Humidity']['ambientHumidityPercent']
        print('Humidity:', humidity)
        temperature = response_json['traits']['sdm.devices.traits.Temperature']['ambientTemperatureCelsius']
        print('Temperature:', temperature)
        
    
    def sendCmdDevice(self, device, data):
        url_set_mode = 'https://smartdevicemanagement.googleapis.com/v1/' + device + ':executeCommand'

        headers = {
        'Content-Type': 'application/json',
        'Authorization': self.access_token,
        }
        
        response = requests.post(url_set_mode, headers=headers, data=data)
        print(response.json())
        
    def setDeviceHeat(self, device):
        data = '{ "command" : "sdm.devices.commands.ThermostatMode.SetMode", "params" : { "mode" : "HEAT" } }'
        self.sendCmdDevice(device, data)
        
    def setDeviceTemperature(self, device, T):
        data = '{"command" : "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat", "params" : {"heatCelsius" : ' + str(T) + '} }'
        self.sendCmdDevice(device, data)
    
    def setFanON(self, device):
        print(mode)
        data = '{"command" : "sdm.devices.commands.Fan.SetTimer", "params" : {"timerMode" : "ON"} }'
        self.sendCmdDevice(device, data)
        
    def setFanOFF(self, device):
        print(mode)
        data = '{"command" : "sdm.devices.commands.Fan.SetTimer", "params" : {"timerMode" : "OFF"} }'
        self.sendCmdDevice(device, data)
        
####################################################################
# Configuration
####################################################################
class GNestConfig():
    def __init__(self):
        self.home = str(Path.home())+"/"
        #self.home = str(Path.cwd())+"/"
        self.configFile = self.home+"GNestAccess.ini"
        self.generalFolder = self.home+"GNestAccess/"
        #Path(self.generalFolder).mkdir(parents=True, exist_ok=True)
        self.logFile = self.generalFolder+"GNestAccess.log"
        self.conf = configparser.ConfigParser()
        self.conf.optionxform = str
        if os.path.isfile(self.configFile) is False:
            print("Configuration file does not exist: Creating one.")
            self.createConfig()
        self.readConfig(self.configFile)
    
    # Create configuration file
    def createConfig(self):
        try:
            self.defineSystem()
            with open(self.configFile, 'w') as configfile:
                self.conf.write(configfile)
        except:
            print("Error in creating configuration file")

    # Hardcoded default definitions for the configuration file
    def defineSystem(self):
        self.conf['System'] = {
            'appVersion' : 0,
            'loggingLevel' : logging.INFO,
            'loggingFilename' : self.logFile,
            'dataFolder' : '.',
            'verbose' : True,
            'project_id' : "xxx",
            'client_id' : "xxx",
            'client_secret' : "xxx",
            'redirect_uri' : "urn:ietf:wg:oauth:2.0:oob",
            }
    
    # Read configuration file into usable variables
    def readConfig(self, configFile):
        self.conf.read(configFile)
        self.sysConfig = self.conf['System']
        self.appVersion = self.sysConfig['appVersion']
        try:
            self.loggingLevel = self.sysConfig['loggingLevel']
            self.loggingFilename = self.sysConfig['loggingFilename']
            self.dataFolder = self.sysConfig['dataFolder']
            self.verbose = self.conf.getboolean('System','verbose')
            self.project_id = self.sysConfig['project_id']
            self.client_id = self.sysConfig['client_id']
            self.client_secret = self.sysConfig['client_secret']
            self.redirect_uri = self.sysConfig['redirect_uri']
        
        except:
            print("Configuration file is for an earlier version of the software")
            oldConfigFile = str(os.path.splitext(configFile)[0] + "_" +\
                    str(datetime.now().strftime('%Y%m%d-%H%M%S'))+".ini")
            print("Old config file backup: ",oldConfigFile)
            os.rename(configFile, oldConfigFile )
            print("Creating a new config file.")
            self.createConfig()
            self.readConfig(configFile)

    # Save current parameters in configuration file
    def saveConfig(self, configFile):
        try:
            with open(configFile, 'w') as configfile:
                self.conf.write(configfile)
        except:
            print("Error in saving parameters")
        

#************************************
''' Main initialization routine '''
#************************************
if __name__ == "__main__":
    sys.exit(main())
