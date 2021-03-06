#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
***********************************************************
* Google Nest Device Access GNestAccess
* version: 20210429a
* By: Nicola Ferralis <feranick@hotmail.com>
* Google Nest API: https://tinyurl.com/673rxvmf
***********************************************************
'''
print(__doc__)

import requests, sys, os.path, time, configparser, logging
import webbrowser
from datetime import datetime
from pathlib import Path
'''
def main():
    if len(sys.argv) > 1:
        code = sys.argv[1]
    else:
        code = ""
    g = GoogleNest(code)
    g.getToken()
    #g.refreshToken()
    g.getStructures()
    dev0, tmp = g.getDevices(0)
    dev1, tmp = g.getDevices(1)
    g.getDeviceStats(dev0)
    #g.getDeviceStats(dev1)
    #g.setDeviceTemperature(g.device_1_name, 18)
    #g.setFanON(dev1)
    #g.getFanTrait(1)
    print("Fan status:", g.fanStatus)
    print("HVAC status:", g.hvacStatus)
'''

####################################################################
# Class GoogleNest
####################################################################
        
class GoogleNest:
    def __init__(self, code):
        self.conf = GNestConfig()
        print('\033[1mEnter this URL in a browser and follow the instructions to get an access code:\033[0m\n')
        self.url = 'https://nestservices.google.com/partnerconnections/'+self.conf.project_id+'/auth?redirect_uri='+self.conf.redirect_uri+'&access_type=offline&prompt=consent&client_id='+self.conf.client_id+'&response_type=code&scope=https://www.googleapis.com/auth/sdm.service'
        
        print(self.url)
        webbrowser.open(self.url,new=1,autoraise=True)
        if code == "":
            self.code = input("\n\033[1mPaste access code: \033[0m")
        else:
            self.code = code
        
        self.params = (
            ('client_id', self.conf.client_id),
            ('client_secret', self.conf.client_secret),
            ('code', self.code),
            ('grant_type', 'authorization_code'),
            ('redirect_uri', self.conf.redirect_uri),
        )
        self.time = time.time()
    
    # Get tokens
    def getToken(self):
        response = requests.post('https://www.googleapis.com/oauth2/v4/token', params=self.params)

        response_json = response.json()
        #print(response_json)
        self.access_token = response_json['token_type'] + ' ' + str(response_json['access_token'])
        print('Access token: ' + self.access_token)
        self.refresh_token = response_json['refresh_token']
        print('Refresh token: ' + self.refresh_token)
        self.time = time.time()

    # Refresh token
    def refreshToken(self):
        params = (
            ('client_id', self.conf.client_id),
            ('client_secret', self.conf.client_secret),
            ('refresh_token', self.refresh_token),
            ('grant_type', 'refresh_token'),
        )
        response = requests.post('https://www.googleapis.com/oauth2/v4/token', params=params)

        response_json = response.json()
        #print(response_json)
        self.access_token = response_json['token_type'] + ' ' + response_json['access_token']
        #print('Access token: ' + self.access_token)
        print("\n Access token refreshed")
        
    # Get structures
    def getStructures(self):
        url_structures = 'https://smartdevicemanagement.googleapis.com/v1/enterprises/' + self.conf.project_id + '/structures'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.access_token,
            }

        response = requests.get(url_structures, headers=headers)
        #print(response.json())
        
    # Get devices
    def getDevices(self, dev):
        url_get_devices = 'https://smartdevicemanagement.googleapis.com/v1/enterprises/' + self.conf.project_id + '/devices'

        headers = {
            'Content-Type': 'application/json',
            'Authorization': self.access_token,
            }

        response = requests.get(url_get_devices, headers=headers)
        #print(response.json())
        response_json = response.json()
        device_name = str(response_json['devices'][dev]['name'])
        #print(device_name)
        return device_name, response.json()

    # Get Device Stats
    def getDeviceStats(self, device):
        #print("DEVICE NAME:",device)
        url_get_device = 'https://smartdevicemanagement.googleapis.com/v1/' + device
        headers = {
        'Content-Type': 'application/json',
        'Authorization': self.access_token,
        }
        try:
            response = requests.get(url_get_device, headers=headers)
            response_json = response.json()
            self.humidity = response_json['traits']['sdm.devices.traits.Humidity']['ambientHumidityPercent']
            #print('Humidity:', self.humidity)
            self.temperature = response_json['traits']['sdm.devices.traits.Temperature']['ambientTemperatureCelsius']
            #print('Temperature:', self.temperature)
            
            '''
            tmp = response_json['traits']['sdm.devices.traits.Fan']['timerMode']
            if tmp == "ON":
                self.fanStatus = 1
            else:
                self.fanStatus = 0
            #print('Fan:', self.fanStatus)
            #print("STATUS:",response_json['traits']['sdm.devices.traits.ThermostatHvac']['status'])
            '''
            self.fanStatus = response_json['traits']['sdm.devices.traits.Fan']['timerMode']
            self.hvacStatus = response_json['traits']['sdm.devices.traits.ThermostatHvac']['status']
            

        except RuntimeError as arg:
            print("\n\n Failed to get Device Statistics\n")
            print(arg)
            self.humidity = 0
            self.temperature = 0
            self.fanStatus = "OFF"
            self.hvacStatus = "OFF"
        
    def sendCmdDevice(self, device, data):
        url_set_mode = 'https://smartdevicemanagement.googleapis.com/v1/' + device + ':executeCommand'

        headers = {
        'Content-Type': 'application/json',
        'Authorization': self.access_token,
        }
        
        response = requests.post(url_set_mode, headers=headers, data=data)
        #print(response.json())
        
    def setDeviceHeat(self, device):
        data = '{ "command" : "sdm.devices.commands.ThermostatMode.SetMode", "params" : { "mode" : "HEAT" } }'
        self.sendCmdDevice(device, data)
        
    def setDeviceTemperature(self, device, T):
        data = '{"command" : "sdm.devices.commands.ThermostatTemperatureSetpoint.SetHeat", "params" : {"heatCelsius" : ' + str(T) + '} }'
        self.sendCmdDevice(device, data)
    
    def setFanON(self, device):
        data = '{"command" : "sdm.devices.commands.Fan.SetTimer", "params" : {"timerMode" : "ON"} }'
        self.sendCmdDevice(device, data)
        
    def setFanOFF(self, device):
        data = '{"command" : "sdm.devices.commands.Fan.SetTimer", "params" : {"timerMode" : "OFF"} }'
        self.sendCmdDevice(device, data)
    
    def getFanTrait(self, dev):
        try:
            dev_name, traits = self.getDevices(dev)
            self.fanMode = traits['devices'][dev]['traits']['sdm.devices.traits.Fan']['timerMode']
            print("Fan",dev,"is:",self.fanMode)
        except RuntimeError as arg:
            print("\n\n Failed to get Fan status\n")
            print(arg)
            #self.fanMode = "OFF"
        return self.fanMode
        
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
# Main initialization routine
#************************************
if __name__ == "__main__":
    sys.exit(main())
