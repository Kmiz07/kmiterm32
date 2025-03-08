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
