%--------------------------------------------------------------
%     IEE2683 Laboratorio de Control Automático
%     Archivo Prueba Caja Negra
%
%     Prof. Felipe Nunez
%
%--------------------------------------------------------------

clear all
close all
clc;
echo on
% Se deben hacer pruebas con diferentes entradas.
echo off
disp('Push any key to begin the identification routine'); pause
tic
echo on
 
% Parametros para la identifiación:
echo off
Ts = 0.005           
tfinal = 2
Cs = 0.3;
t = (0:Ts:tfinal)';
npts = length(t)
echo on
 
% El modelo Simulink será simulado a continuación. Primero se construye la
% entrada del sistema y luego se usa la función sim para simular y capturar
% los valores de la salida.
echo off

u1 = [t, 2*ones(npts,1), zeros(npts,1)];     
u2 = [t, -2*ones(npts,1), zeros(npts,1)];         
[t1,x,y1] = sim('loopshape',tfinal,[],u1);        
[t2,x,y2] = sim('loopshape',tfinal,[],u2);
toc
echo on
% Se presentan gráficos de las respuestas
echo off
disp('Push any key to begin the plotting section'); pause
figure
grid on
plot(t1,y1(:,1))
title('Respuesta a u1')
grid on
xlabel('t')
ylabel('Magnitud')
disp('paused: push any key to continue'); pause
figure
plot(t2,y2(:,1))
grid on
title('Respuesta a u2')
xlabel('t')
ylabel('Magnitud')