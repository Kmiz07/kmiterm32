from machine import Pin
import onewire, ubinascii, asyncio, confjson,ds18x20, ventilador,utime,valvula

ow = onewire.OneWire(Pin(14))
ds = ds18x20.DS18X20(ow)
flash = Pin(0,Pin.IN)
quemador = Pin(12,Pin.OUT)
pulsa_flash = 1
procesa = 1
Error = 0
nom_sondas = ['tmp_rad','tmp_acs','tmp_amb']
pulsa_flash=1
anteriores=[0,0,0]
blue_activo = False
actual={
    'tmp_acs':0,#temperatura liquido ACS
    'tmp_rad':0,#temperatura liquido RAD
    'tmp_amb':0,#temperatura ambiente
    'th_ok':20,#temperatura ambiente deseada
    'est_rad':0,#estado modo calefaccion (0= negro, 1= rojo, 2= verde)
    'est_acs':0,#estado modo ACS (0=negro, 1= rojo, 2= verde)
    'est_fire':0,#estado icono quemador(0= apagado, 1= encendido)
    'vent':0, #estado del ventilador. 0 es automatico manejado por soft 1-100 velocidad fija manual
    'programa' :0, # segundo en utime.time() en que se debe cambiar el estado de la calefaccion. 0 es no programado.
    'est_bypass' : 'acs' # puede ser 'acs' o 'rad'
    }
async def escanea(a_cadena=False):
#     print('escanea')
    global ds
    hex_roms=[]
    roms =ds.scan()
    for rom in roms:
        if a_cadena:
            xr=ubinascii.hexlify(rom).decode('UTF-8')
        else:
            xr=ubinascii.hexlify(rom)
        hex_roms.append(xr)
    return hex_roms


async def lee_sensores(objeto):#retorna un diccionario con los ID hexadecimales de los sensores existentes y sus valores de temperatura
#     print('lee sensores')
    global ds, anteriores, actual
    sensores={}
    sensdat= confjson.recupera()['sondas']
    roms = ds.scan()
    try:
        ds.convert_temp()
        await asyncio.sleep_ms(750)
        n=0
        for rom in roms:
            rm_hex = ubinascii.hexlify(rom).decode('UTF-8')
            valor_tmp=round(ds.read_temp(rom),1)
            sensores[sensdat[rm_hex]]=valor_tmp
            
            if anteriores[n] != valor_tmp:
                actual[sensdat[rm_hex]] = valor_tmp
                print(f'{sensdat[rm_hex]} : {valor_tmp}')
                print(f'{anteriores[n]}>>>>{valor_tmp}')
                if blue_activo: asyncio.create_task(objeto.send(f'{sensdat[rm_hex]}#{round(ds.read_temp(rom),1)}\n'))
                anteriores[n] = valor_tmp
            n+=1
        return (sensores)
    except:
        pass
    
    
async def empareja_sensores(objeto):
#     print('empareja sensores')
    global procesa, nom_sondas, Error
    sondas={}
    procesa=0
    Error=0
    for n in nom_sondas:
        print(f'inserta sensor de {n} y pulsa flash')
        if blue_activo: await objeto.send(f'conf_{str.split(n,'_')[1]}\n')
        await espera_flash()
        broms=await escanea()
        if broms:
            diferencia= set(broms)-set(sondas.keys())
            fff=list(diferencia)
            print(fff)
            if diferencia:
                sondas[list(diferencia)[0]]=n
            else:
                print(f'sonda {n} no detectada')
                Error+=1
        else:
            print('no se detectan sondas')
            Error+=2
        print(sondas)
    if Error == 0:
        confjson.entra('sondas',sondas)
    procesa = 1
    return Error


def fuerza_flash():#fuerza flash desde el exterior
    global pulsa_flash
    pulsa_flash=0
    
    
async def espera_flash():#Espera que se pulse flash asincronamente
#     print('espera_flash')
    global pulsa_flash
    while pulsa_flash:
        pulsa_flash = flash.value()
        await asyncio.sleep(0)
    await asyncio.sleep(0.5)
    pulsa_flash = 1
    
    
async def comprueba_sensores():
#     print('comprobando sensores')
    global procesa
    sensores = await escanea(True)
    if len(sensores)!= 3: return True
    val=confjson.recupera()
    if not 'sondas' in val.keys():
        confjson.entra('sondas',{'fallo':'error'})
        return True
    valsens=val['sondas'].keys()
    if list(set(sensores).difference(valsens)) != []:
        return True
    else:
        return False

            
            
    
async def inicia(periodo, objeto, evento):
    global procesa, actual
    ventilador.arranca()
    ventilador.regula(0)
    
    while True:
        if procesa:
            # control de programacion de encendido o apagado
            if actual['programa'] <=  utime.time() and actual['programa'] != 0:
                actual['programa'] = 0
                asyncio.create_task(objeto.send('programado#0\n'))
                if actual['est_rad'] != 0 or actual['est_acs'] != 0:
                    actual['est_rad'] = 0
                    await objeto.send('calefaccion_0\n')
                    actual['est_acs'] = 0
                    await objeto.send('acs_0\n')
                    
                else:
                    actual['est_rad'] = 1
                    await objeto.send('calefaccion_1\n')

                    
                    
            #control de temperaturas en sensores de radiador y acs
            if actual['est_rad'] == 1:
                if actual['tmp_rad'] >= int(confjson.lee('T_RAD_MIN')):
                    actual['est_rad'] =2
                    asyncio.create_task(objeto.send('calefaccion_2\n'))
            if actual['est_acs'] ==1:
                if actual['tmp_acs'] >= int(confjson.lee('T_ACS_MIN')):
                    actual['est_acs'] = 2
                    asyncio.create_task(objeto.send('acs_2\n'))
            if actual['est_rad'] == 2:
                if actual['tmp_rad'] < int(confjson.lee('T_RAD_MIN')):
                    actual['est_rad'] =1
                    asyncio.create_task(objeto.send('calefaccion_1\n'))
            if actual['est_acs'] ==2:
                if actual['tmp_acs'] < int(confjson.lee('T_ACS_MIN')):
                    actual['est_acs'] = 1
                    asyncio.create_task(objeto.send('acs_1\n'))
            #aqui control de termostato ambiente
            if actual['est_rad'] != 0:
                if actual['est_fire'] == 1: #temperatura ascendente
                    if actual['tmp_amb'] >= actual['th_ok']:
                        actual['est_fire'] = 0
                    else:
                        actual['est_fire'] = 1
                else:#temperatura descendente
                    if actual['tmp_amb'] <= actual['th_ok'] - int(confjson.lee('HISTERESIS')):
                        actual['est_fire'] = 1
                    else:
                        actual['est_fire'] = 0
            else:
                actual['est_fire'] = 0
                        
                        
            if actual['est_fire'] == 1:
                if actual['est_bypass']== 'acs':
                    actual['est_bypass'] = 'rad'
                    asyncio.create_task(valvula.valvula_RAD())
            else:
                if actual['est_bypass'] == 'rad':
                    actual['est_bypass'] = 'acs'
                    asyncio.create_task(valvula.valvula_ACS())
                
            #si esta activada acs se fuerza quemador
            if actual['est_acs'] != 0 :
                actual['est_fire'] = 1
            
            if quemador.value() != int(actual['est_fire']):
                quemador.value(int(actual['est_fire']))
                asyncio.create_task( objeto.send(f'quemador_{actual['est_fire']}\n'))    
                

            
            
            
                #aqui configura bypass para radiador si es necesario
                
                

                
                
            #aqui configura ventilador si es necesario
            if not actual['vent'] and actual['est_rad'] ==2:#si ventilador es automatico y radiador esta caliente
                ventilador.configura(actual['tmp_amb'], actual['tmp_rad'], actual['th_ok'], actual['tmp_rad'], 0)
                
                
            
            
            # lecturas de temperaturas y comprobacion de sensores
            error= 0
            x = await comprueba_sensores()
            if x:
                print('Error de sensores')
                error=await empareja_sensores(objeto)
            if error==0:
                sens = await lee_sensores(objeto)
                await asyncio.sleep(periodo)
            #print(actual)
            
                
                