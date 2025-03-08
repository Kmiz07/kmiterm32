# kmiterm32
Software y hardware para control de un sistema de calefacción para autocaravana/camper.
![image](https://github.com/user-attachments/assets/5d72325a-72a1-46c5-8bac-9c52b57b173a)

Descripción del Hardware.

Se trata de un sistema de control para un dispositivo de calefacción y ACS, compuesto por un quemador de gasoil, y un doble circuito para radiador e intercambiador ACS controlado por una válvula bypass para el control de los fluidos y un ventilador con velocidad regulable por PWM.
El corazón del sistema es un esp32S, que dispone de conectividad tanto wifi como Bluetooth.
El diseño de la pcb ha sido realizado pensando en posibles futuras ampliaciones dando salida a la mayoría de los pines disponibles en el chip.
No se ha tenido en cuenta el aislamiento mediante opto acopladores. En posibles ampliaciones, si las entradas/salidas lo requieren deberá tenerse en cuenta.
El circuito consta de salida por doble relé para la válvula bypass de 12v(Fig. 1)
![image](https://github.com/user-attachments/assets/a1593144-c1db-4b91-bf6f-7ba533bd6b1f)
fig. 1

Dicha válvula tiene doble circuito con final de carrera. Para optimizar el consumo y desgaste de materiales, se ha optado por temporizar la acción de cada circuito en un tiempo de 8 segundos configurable desde la app móvil.

Consta de otra salida por relé simple para la linea de maniobra del quemador. La corriente de potencia del quemador tiene conexión directa a batería y no es controlada por el circuito.

La salida para control de velocidad del ventilador dispone de un transistor mosfet de potencia y baja entrada y produce una salida pwm adecuada para un grupo de 4 ventiladores con un consumo maximo total de 2A.

Toma los datos de temperatura ambiente, y temperaturas de fluidos mediante tres sensores ds18b20, encapsulados en un paquete de acero inoxidable impermeable. Estos sensores funcionan mediante el protocolo onewire y con un solo pin de datos se pueden muestrear las tres temperaturas.(fig.2)
![image](https://github.com/user-attachments/assets/eec37993-0454-4b55-9f88-e3056e983b31)
fig. 2

La alimentacion del chip, se obtiene a partir de los 12V mediante un sistema dc-dc del tipo MINI 560 (Fig.3)
![image](https://github.com/user-attachments/assets/77006aa3-844e-4db5-9ef2-30d3f0f2510f)
fig. 3

Se ha elegido este tipo de dispositivo pero en el pcb esta disponible tambien la posibilidad de montar un LF33cv.


![image](https://github.com/user-attachments/assets/28e9574b-473e-42fc-8266-3a432e29568f)
circuito electrico

Descripción del software.

El software esta realizado en Micropython (v1.24.1  2024-11-29 ). La estructura del código trabaja en modo asincrónico, por lo que se ha utilizado la librería aible en lugar de la ble tradicional para no interferir en el bucle de programa asincrónico.
En el inicio, el programa se pone a la espera para recibir una petición de conexión por Bluetooth y no hará nada mas mientras no reciba esa primera conexión.
Una vez recibe la primera petición, envía los datos configurables por usuario a la app y acto seguido comprueba la comunicación de las sondas de temperatura. Si estas no existen o no comunican se pone en marcha una rutina de configuración de las sondas mediante peticiones de modo que se pueda diferenciar el id de cada sonda y pueda ser memorizado en el archivo de configuración para próximos arranques.
Esta integridad de los ids de cada sonda se comprueba a cada bucle de programa. Si esta falla, se detiene la calefacción y se retorna a la rutina de configuración.
A cada vuelta del loop de programa, se comprueban las opciones requeridas por la app,(temperatura deseada, programación, velocidad de ventilador…..) y se toman las decisiones pertinentes.

