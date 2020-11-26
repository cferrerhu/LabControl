%%

s = tf('s');
H = 8/(0.01*s^3 + 0.7*s^2 + 2*s + 1);
a = [0 0 0 8]; a1 = a;
b = [0.01 0.7 2 1]; b1 = [0.01 0.7 2 1];
[A,B,C,D] = tf2ss(a, b);
sys = ss(A,B,C,D);
Ts = 0.1;
mpcobj = mpc(sys, Ts);
% specify prediction horizon
mpcobj.PredictionHorizon = 100;
% specify control horizon
mpcobj.ControlHorizon = 60;
% specify weights
mpcobj.Weights.MV = 0;
mpcobj.Weights.MVRate = 0.1;
mpcobj.Weights.OV = 5;
mpcobj.Weights.ECR = 100000;
DSP = 1e-3;
i_v = [15];
step = [17];
step_time = 50;
sim('TP3.slx', 150)
%%
tiempo = salida_controlada.Time;
sen_salida = salida_controlada.Data;
sen_entrada = referencia_controlada.Data;
Vp = Vp_controlada.Data;

% J = trapz(abs(sen_entrada(step_time/Ts:end,:) - sen_salida(step_time/Ts:end,:))*Ts);
figure;
plot(tiempo, sen_salida, ':.', 'LineWidth', 2)
hold on;
plot(referencia_controlada.Time, sen_entrada, ':.',  'LineWidth', 2)
xlabel('[s]')
legend('Respuesta', 'Entrada')
title(sprintf('PH = %d, CH = %d, Modelo Preciso + Ruido',mpcobj.PredictionHorizon, mpcobj.ControlHorizon))
ylim([14.5 17.5])