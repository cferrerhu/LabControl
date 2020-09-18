%% PRBS
n = 12;
N = 2^n-1;

prbs = zeros(1, N);
% estadoN = randi([0 1], 1, 15);
estadoN = [1 0 1 0 0 0 1 1 0 0 0 0 1 0 0];
for i=1:N
    prbs(i) = xor(estadoN(1), estadoN(15));
    estadoN = circshift(estadoN, 1);
    estadoN(1) = prbs(i);

end
prbs = prbs*2-1;

M = 20;
PRBS = repmat(prbs, [1, M])';
Ts = 0.5/1000;
t = [(0:1:length(PRBS)-1)*Ts]';
%%
% Paramteros para respuesta estable
% Pz = 0.8;
% Zz = 0.3;
% KI = 1.5;
% Cs = 1.2;

% Parametros para tener solo controlador proporcional
Pz = 0;
Zz = 0;
KI = 1e-32;
Cs = 1.28;
Cfd = 1;
u1 = [t, PRBS.*ones(length(t),1), PRBS*0];             
[t1aux,x,yaux] = sim('loopshape',t(end),[],u1);        
t1 = t1aux;
y1 = yaux(:, 1); % Decimation
y2 = yaux(:, 2);

figure;

ax1 = subplot(1, 2, 1);
grid on
plot(t1,y1);
hold on;
title('Referencia Escalon', 'FontSize', 18)
grid on
xlabel('t')
ylabel('Magnitud')
plot(t1, ones(length(t),1));
legend('Salida', 'Entrada')
ax1.YAxis.FontSize = 13;
ax1.XAxis.FontSize = 13;
xlim([0 40])

ax2 = subplot(1, 2, 2);
plot(t1,y1)
hold on;
plot(t1, ones(length(t),1));
title('Zoom [38.1, 38.5] s', 'FontSize', 18)
grid on
xlabel('t')
ylabel('Magnitud')
xlim([38.1, 38.4])
legend('Salida', 'Entrada')
ax2.YAxis.FontSize = 13;
ax2.XAxis.FontSize = 13;

T1 = detrend(y1, 1);
T2 = detrend(y2, 1);
new_T1 = T1(N+1:end);
new_T2 = T2(N+1:end);
new_t1 = t1(N+1:end);
matrix_T1 = reshape(new_T1, [N M-1]); output1 = mean(matrix_T1, 2);
matrix_T2 = reshape(new_T2, [N M-1]); output2 = mean(matrix_T2, 2);

%% Transfer Funtion

Y1 =  dft_matrix*(output1.*hamming_window');
Y2 =  dft_matrix*(output2.*hamming_window');% fft(U)
H = fftshift(Y1./Y2);
U_H = 1/(length(Y1)*Ts); 
vec_H = -length(H)/2:1:(length(H)/2-1); vec_H = vec_H*U_H;
figure;  
ax1 = subplot(2,1,1);
grid on;
semilogx(vec_H(vec_H > 0), 20*log10(abs(H(vec_H > 0))))
xlim([0.1 400])
ax1.YAxis.FontSize = 13;
ax1.XAxis.FontSize = 13;

title(sprintf('Magnitude'), 'FontSize', 18); xlabel('Hz', 'FontSize', 14)
ax2 = subplot(2,1,2);
phase = 360/2/pi*atan2(imag((H(vec_H > 0))),real((H(vec_H > 0)))); 
grid on;
semilogx(vec_H(vec_H > 0), phase); hold on;
xlim([0.1 400])
title('Phase',  'FontSize', 18); xlabel('Hz', 'FontSize', 14)
ax2.YAxis.FontSize = 13;
ax2.XAxis.FontSize = 13;

%% Nyquist
figure;
Y1 =  dft_matrix*(output1.*hamming_window');
Y2 =  dft_matrix*(output2.*hamming_window');% fft(U)
H = fftshift(Y1./Y2);

plot(real(H), imag(H), ':.')
hold on;
plot(-1:0.01:1, sqrt(1 - (-1:0.01:1).^2));
plot(-1:0.01:1, -sqrt(1 - (-1:0.01:1).^2));
axis square
title('Nyquist')