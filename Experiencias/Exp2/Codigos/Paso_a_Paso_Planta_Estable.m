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

%% Repetition of prbs
M = 20;
PRBS = repmat(prbs, [1, M])';
Ts = 5/1000;
t = [(0:1:length(PRBS)-1)*Ts]';

%%

[t1aux,x,y1aux] = sim('BlackBox',t(end),[],[t, PRBS]);

y1 = [y1aux(1); y1aux(5:end)];
t1 = [t1aux(1); t1aux(5:end)];

size(y1)
size(PRBS)
%%
figure;
title(sprintf('Respuesta a prbs, n = %d, M = %d', n, M))
xlabel('t')
ylabel('Magnitud')
hold on;
grid on;
plot(t1,y1,'MarkerSize',12)



%% Remove Trend

T = detrend(y1, 1);

figure;
title(sprintf('Respuesta a prbs sin tendencia, n = %d, M = %d', n, M))
xlabel('t')
ylabel('Magnitud')
hold on;
grid on;
plot(t1, T, 'MarkerSize',12)

%% Remove the first segment

new_T = T(N+1:end);
new_t1 = t1(N+1:end);
plot(new_t1, new_T, 'MarkerSize',12)

%% Remove noise by averaging


matrix_T = reshape(new_T, [N M-1]);
figure;
output = mean(matrix_T, 2);
plot(t1(1:N), output)
hold on;
plot(t1(1:N), prbs)
legend('y', 'u')

%% Correlations

%%
% Ru
Ru = conv(prbs, prbs(end:-1:1), 'same'); 
Ru = Ru./max(Ru); figure; plot(Ru); title('R_u');
% Ry

Ry = conv(output, output(end:-1:1), 'same')'; 
Ry = Ry./max(Ry); figure; plot(Ry); title('R_y');

% Ryu
Ryu = conv(prbs, output(end:-1:1), 'same'); 
Ryu = Ryu./max(Ryu); figure; plot(Ryu); title('R_y_u');

%% figure Hanning Window
figure;

plot(hamming_window, ':.')
title('Hanning Window $\alpha = 0.5$', 'Interpreter', 'latex', 'FontSize', 14)
xlabel('Sample')
ylabel('Amplitude')
%% FFT

[dft_matrix] = dft_campeny(length(Ru));
hamming_window = hamming(length(Ru), 0.5); 

Phiu = dft_matrix*(Ru.*hamming_window)'; %Phiu = abs(Phiu); 
Phiy = dft_matrix*(Ry.*hamming_window)'; %Phiy = abs(Phiy);
Phiyu = dft_matrix*(Ryu.*hamming_window)';
disp('finish')

%% Plot Fourier Spectrum Magnitud
U = 1/(length(Ru)*Ts);
vec_u = -length(Phiu)/2:1:(length(Phiu)/2-1); vec_u = vec_u*U;
figure; plot(vec_u, 20*log10(abs(fftshift(Phiu)))); 
title('$20 \cdot \log |(\Phi_u)|$', 'Interpreter', 'latex','FontSize', 18); xlabel('Hz',  'Interpreter', 'latex')
figure; semilogx(vec_u, 20*log10(abs(fftshift(Phiy'))));
title('$20 \cdot \log |(\Phi_y)|$', 'Interpreter', 'latex', 'FontSize', 18); xlabel('Hz',  'Interpreter', 'latex')
figure; semilogx(vec_u, 20*log10(abs(fftshift(Phiyu)))); 
title('$20 \cdot \log |(\Phi_{yu})|$', 'Interpreter', 'latex', 'FontSize', 18); xlabel('Hz',  'Interpreter', 'latex')

%% Plot Fourier Spectrum Fase

figure; plot(vec_u, 360/2/pi*atan2(imag(fftshift(Phiu')), real(fftshift(Phiu')))); 
title('$\angle (\Phi_u)$', 'Interpreter', 'latex'); xlabel('Hz',  'Interpreter', 'latex')

figure; plot(vec_u, 360/2/pi*atan2(imag(fftshift(Phiy')), real(fftshift(Phiy')))); 
title('$\angle (\Phi_y)$', 'Interpreter', 'latex'); xlabel('Hz',  'Interpreter', 'latex')

figure; plot(vec_u, 360/2/pi*atan2(imag(fftshift(Phiyu')), real(fftshift(Phiyu')))); 
title('$\angle (\Phi_{yu})$', 'Interpreter', 'latex'); xlabel('Hz',  'Interpreter', 'latex')

%% Coherence Spectrum
U = 1/(length(Ru)*Ts);
vec_u = -length(Phiu)/2:1:(length(Phiu)/2-1); vec_u = vec_u*U;
Cyu = fftshift(sqrt(abs(Phiyu).^2./(abs(Phiy).*abs(Phiu))));

figure; semilogx(vec_u(vec_u>0), (((Cyu(vec_u>0)/max(Cyu))))); 
hold on;
plot([1.5 1.5], [0 1])
title('$C_{yu}$', 'Interpreter', 'latex', 'FontSize', 18); xlabel('Hz',  'Interpreter', 'latex')
leg = legend('Cyu', 'x = 1.5 Hz'); leg.FontSize = 14;
%%
figure; plot(vec_u, 360/2/pi*atan2(imag(fftshift(Cyu')), real(fftshift(Cyu')))); 
title('$\angle (C_{yu})$', 'Interpreter', 'latex'); xlabel('Hz',  'Interpreter', 'latex')

%% Bode
Y =  dft_matrix*(output.*hamming_window');
U_prbs =  dft_matrix*(prbs'.*hamming_window'); % fft(U)
H = fftshift(Y./U_prbs);
U_H = 1/(length(output)*Ts);
vec_H = -length(H)/2:1:(length(H)/2-1); vec_H = vec_H*U_H;
figure;  
subplot(2,1,1);

semilogx(vec_H(vec_H > 0), 20*log10(abs(H(vec_H > 0))))
hold on;
plot([1.50 1.5], [-50 50])
leg = legend('Magintude', 'x = 1.5 Hz'); leg.FontSize = 14;
title('Magnitude'); xlabel('Hz')
subplot(2,1,2);
semilogx(vec_H(vec_H > 0), 360/2/pi*atan2(imag((H(vec_H > 0))), real((H(vec_H > 0))))); hold on;
title('Phase'); xlabel('Hz')
plot([1.50 1.5], [-200 200])
leg = legend('Phase', 'x = 1.5 Hz'); leg.FontSize = 14;

%% Nyquist
 
figure;
Y =  dft_matrix*(output.*hamming_window');
U_prbs =  dft_matrix*(prbs'.*hamming_window'); % fft(U)
H = fftshift(Y./U_prbs);
plot(real(H), imag(H), ':.')
hold on;
plot(-1:0.01:1, sqrt(1 - (-1:0.01:1).^2));
plot(-1:0.01:1, -sqrt(1 - (-1:0.01:1).^2));
axis square
title('Nyquist')


% margen fase = 180 - atan2(0.9404, -0.34)*180/pi = 70.1226
% margen de ganancia 0.7


