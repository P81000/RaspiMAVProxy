#!/usr/bin/env python

##AERORIVER GERAL

import time, math
from pymavlink import mavutil
import multiprocessing
import socket

from MAVProxy.modules.lib import mp_module
from MAVProxy.modules.lib.mp_settings import MPSetting

#Rasp IP -- General purpouse module has to receive data from 5004 udp port
UDP_IP='127.0.0.1'
UDP_PORT=5004

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

class ARGeral(mp_module.MPModule):
    print('AeroRiver Geral LogSaver')
    def __init__(self, mpstate):
        super(ARGeral, self).__init__(mpstate, "ar", "logsaver")
        self.data_process = None
        self.collecting_data = False
        self.add_command('ar1', self.cmd_stop, 'AERORIVERGERAL')
        self.start_data_acquisition()

    def cmd_stop(self, args):
        if len(args) == 0:
            print('Missing args: (stop)')
            return
        elif args[0] == 'stop':
            if self.collecting_data:
                self.stop_data_acquisition()
            else:
                print('Data acquisition is not running.')
        else:
            print('Invalid argument. Please use "stop".')

    def start_data_acquisition(self):
        if self.data_process and self.data_process.is_alive():
            print('Data acquisition is already running.')
            return
        self.collecting_data = True
        self.data_process = multiprocessing.Process(target=self.collect_data)
        self.data_process.start()
        print('Data acquisition started')

    def stop_data_acquisition(self):
        if self.collecting_data:
            self.collecting_data = False
            self.data_process.terminate()
            self.data_process.join()
            print('Data acquisition stopped')
        else:
            print('Data acquisition is not running')
  
    def collect_data(self):
        print('Data acquisition process started')
        sock.settimeout(0.2)
        try:
            while self.collecting_data:
                #-------------------#
                try:
                    val, addr = sock.recvfrom(48)
                    val = val.decode().split(';')
                    timestamp, data1, data2 = float(val[0]), float(val[1]), float(val[2])
                except socket.timeout:
                    timestamp, data1, data2 = -1, -1, -1
                #-------------------#
                self.master.mav.geral_aeroriver_send(timestamp, data1, data2)
        except KeyboardInterrupt:
            print('Exiting')

def init(mpstate):
    '''initialize module'''
    return ARGeral(mpstate)