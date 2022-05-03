#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# The MIT License (MIT)
#
# Grove Base Hat for the Raspberry Pi, used to connect grove sensors.
# Copyright (C) 2018  Seeed Technology Co.,Ltd.
'''
This is the code for
    - Grove - Moisture Sensor <https://www.seeedstudio.com/Grove-Moisture-Sensor-p-955.html>`_

Examples:

    .. code-block:: python

        import time
        from grove.grove_moisture_sensor import GroveMoistureSensor

        # connect to alalog pin 2(slot A2)
        PIN = 2

        sensor = GroveMoistureSensor(PIN)

        print('Detecting moisture...')
        while True:
            m = sensor.moisture
            if 0 <= m and m < 300:
                result = 'Dry'
            elif 300 <= m and m < 600:
                result = 'Moist'
            else:
                result = 'Wet'
            print('Moisture value: {0}, {1}'.format(m, result))
            time.sleep(1)
'''
import math
import sys
import time
import runPump
from grove.adc import ADC
import paho.mqtt.client as paho
from grove.gpio import GPIO

__all__ = ["GroveMoistureSensor"]

class GroveMoistureSensor:
    '''
    Grove Moisture Sensor class

    Args:
        pin(int): number of analog pin/channel the sensor connected.
    '''
    def __init__(self, channel):
        self.channel = channel
        self.adc = ADC()

    @property
    def moisture(self):
        '''
        Get the moisture strength value/voltage

        Returns:
            (int): voltage, in mV
        '''
        value = self.adc.read_voltage(self.channel)
        return value

Grove = GroveMoistureSensor



__all__ = ["GroveRelay"]

class GroveRelay(GPIO):
    '''
    Class for Grove - Relay

    Args:
        pin(int): number of digital pin the relay connected.
    '''
    def __init__(self, pin):
        super(GroveRelay, self).__init__(pin, GPIO.OUT)

    def on(self):
        '''
        enable/on the relay
        '''
        self.write(1)

    def off(self):
        '''
        disable/off the relay
        '''
        self.write(0)


Grove = GroveRelay

def runPump():
    from grove.helper import SlotHelper
    sh = SlotHelper(SlotHelper.GPIO)
    pin = 22

    relay = GroveRelay(pin)

    relay.on()
    time.sleep(5)
    relay.off()


def main():
    from grove.helper import SlotHelper
    sh = SlotHelper(SlotHelper.ADC)
    pin = 0

    # Used to connect the soil moisture data to NodeRed
    # MQTT_HOST = 'localhost'
    # MQTT_PORT = 1883
    # MQTT_CLIENT_ID = 'Python-MQTT-client'
    # MQTT_USER = 'user'
    # MQTT_PASSWORD = 'password'
    # TOPIC = 'soil moisture reading'

    # client = paho.Client(MQTT_CLIENT_ID)

    # client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    # client.connect(MQTT_HOST, MQTT_PORT)

    sensor = GroveMoistureSensor(pin)

    sensorMax = 2050 # Sitting in the air (average)
    sensorMin = 1220 # Submerged in water (average)

    dryCount = 0

    print('Detecting moisture...')
    while True:
        z = sensor.moisture

        if z > 2050:
            z = 2050
        elif z < 1220:
            z = 1220

        moisture_percentage = 1 - ((z - sensorMin) / (sensorMax - sensorMin))
        m = moisture_percentage
        if 0 <= m and m < 0.21:
            result = 'Dry'
            dryCount += 1
            if dryCount >= 5:
                runPump()
                dryCount = 0
        elif 0.21 <= m and m < 0.41:
            result = 'Damp'
            if dryCount > 0:
                dryCount -=1
            else:
                dryCount = 0
        elif 0.41 <= m and m < 0.61:
            result = 'Moist'
            if dryCount > 0:
                dryCount = 0
        elif 0.61 <= m and m < 0.81:
            result = 'Wet'
            dryCount = 0
        else:
            result = 'Water'
            dryCount = 0
        print('Soil Moisture: {0:.2%}, {1}'.format(m, result))
        test = 'Soil Moisture: {0:.2%}, {1}'.format(m, result)
        #client.publish(TOPIC, test)
        print(dryCount)
        time.sleep(5)

if __name__ == '__main__':
    main()
