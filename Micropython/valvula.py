from machine import Pin
from utime import time
import asyncio
valv_acs = 17
valv_rad = 16
lapso = 8
ACS = Pin(valv_acs,Pin.OUT)
RAD = Pin(valv_rad,Pin.OUT)
instante = 0
actuando = False

async def valvula_ACS():
    global actuando, lapso, ACS
    if not actuando:
        actuando=True
        ACS.on()
        print('valvula>>>>acs')
        await asyncio.sleep(lapso)
        ACS.off()
        actuando=False
    print('valvula parada')
    
async def valvula_RAD():
    global actuando, lapso, RAD
    if not actuando:
        actuando = True
        RAD.on()
        print('valvula>>>radiador')
        await asyncio.sleep(lapso)
        RAD.off()
        actuando = False
    print('valvula parada')
