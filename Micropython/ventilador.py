from machine import Pin,PWM
vent_pin = 27
vent_freq = 30000
vent_dut = 0
vent = PWM(Pin(vent_pin), freq=vent_freq, duty_u16=vent_dut)

def arranca():
    global vent
    vent.init()
def para():
    global vent
    vent.deinit()
para()
def regula(val_vent):
    global vent
    print(val_vent)
    fuerza = int(val_vent*65535/100)
    if fuerza > 65535: fuerza= 65535
    vent.duty_u16(fuerza)
    print(f'ventilador:{fuerza}')
    
def configura(temp_ambiente, temp_radiador, temp_deseada, rad_ok, val_vent):
    if rad_ok != 2:
        vent.duty_u16(0)
    else:
        if val_vent == 0:
            fuerza = (temp_deseada-temp_ambiente)*50
            if fuerza > 100 : fuerza = 100
            if fuerza < 0 : fuerza = 0
        else:
            fuerza = val_vent
        regula(fuerza)
