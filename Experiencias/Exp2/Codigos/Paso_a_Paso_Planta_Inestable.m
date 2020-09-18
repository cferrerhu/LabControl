%% PRBS
n = 12;
N = 2^n-1;
prbs = zeros(1, N);
estadoN = randi([0 1], 1, 15);
% estadoN = [1 0 1 0 0 0 1 1 0 0 0 0 1 0 0];
for i=1:N
    prbs(i) = xor(estadoN(1), estadoN(15));
    estadoN = circshift(estadoN, 1);
    estadoN(1) = prbs(i);


end
prbs = prbs*2-1;
mean(prbs)

M = 20;
PRBS = repmat(prbs, [1, M])';
Ts = 0.5/1000;
t = [(0:1:length(PRBS)-1)*Ts]';

%%
Pz = 0;
Zz = 0;
KI = 1e-16;
Cs = 1.28;
u1 = [t, ones(length(t),1), PRBS];             
[t1aux,x,yaux] = sim('loopshape',t(end),[],u1);        
t1 = t1aux;
y1 = yaux(:, 1); % Decimation
y2 = yaux(:, 2);

%%

figure;
subplot(1, 2, 1)

grid on
plot(t1,y2)
title('Respuesta a y1')
grid on
xlabel('t')
ylabel('Magnitud')
subplot(1, 2, 2)

plot(t1,y2)
title('Respuesta a y2')
grid on
xlabel('t')
ylabel('Magnitud')

%% Remove Drift

T1 = detrend(y1, 1);
T2 = detrend(y2, 1);

% figure;
% subplot(1, 2, 1)
% 
% grid on
% plot(t1,T1)
% title('Respuesta a y1')
% xlabel('t')
% ylabel('Magnitud')
% subplot(1, 2, 2)

% plot(t1,T2)
% title('Respuesta a y2')
% grid on
% xlabel('t')
% ylabel('Magnitud')

%% Remove the first segment
new_T1 = T1(N+1:end);
new_T2 = T2(N+1:end);
new_t1 = t1(N+1:end);

%% Remove noise by averaging


matrix_T1 = reshape(new_T1, [N M-1]); output1 = mean(matrix_T1, 2);
matrix_T2 = reshape(new_T2, [N M-1]); output2 = mean(matrix_T2, 2);
% figure;
% 
% plot(t1(1:N), output2)
% hold on;
% plot(t1(1:N), prbs)
% legend('y', 'u')

%% Correlation Y1 - Y2

Ry1 = conv(output1, output1(end:-1:1), 'same'); 
% Ru2(Ru2 < max(Ru2)) = 0;
Ry1 = Ry1./max(Ry1); %figure; plot(Ry1); title('R_y_1')

Ry2 = conv(output2, output2(end:-1:1), 'same'); 
% Ru2(Ru2 < max(Ru2)) = 0;
Ry2 = Ry2./max(Ry2); %figure; plot(Ry2); title('R_y_2')
% Ryu
Ry12 = conv(output2, output1(end:-1:1), 'same'); 
% Ru2(Ru2 < max(Ru2)) = 0;
Ry12 = Ry12./max(Ry12); %figure; plot(Ry12); title('R_y_2_1')

%% FFT

% [dft_matrix] = dft_campeny(length(Ry1));
hamming_window = hamming(length(Ry1), 0.5); 

Phiy1 = dft_matrix*(Ry1.*hamming_window'); %Phiu = abs(Phiu); 
Phiy2 = dft_matrix*(Ry2.*hamming_window'); %Phiy = abs(Phiy);
Phiy12 = dft_matrix*(Ry12.*hamming_window');
disp('ARCA finish')

%% Plot Fourier Spectrum Magnitud
U = 1/(length(Ry1)*Ts);
vec_u = -length(Phiy1)/2:1:(length(Phiy1)/2-1); vec_u = vec_u*U;
figure; plot(vec_u, 20*log10(abs(fftshift(Phiy1)))); 
title('$20 \cdot \log |(\Phi_{y1})|$', 'Interpreter', 'latex','FontSize', 18); xlabel('Hz',  'Interpreter', 'latex')
figure; semilogx(vec_u, 20*log10(abs(fftshift(Phiy2))));
title('$20 \cdot \log |(\Phi_{y2})|$', 'Interpreter', 'latex', 'FontSize', 18); xlabel('Hz',  'Interpreter', 'latex')
figure; semilogx(vec_u, 20*log10(abs(fftshift(Phiy12)))); 
title('$20 \cdot \log |(\Phi_{y12})|$', 'Interpreter', 'latex', 'FontSize', 18); xlabel('Hz',  'Interpreter', 'latex')

%% Correlation MAP

U = 1/(length(Ry1)*Ts);
vec_u = -length(Phiy1)/2:1:(length(Phiy1)/2-1); vec_u = vec_u*U;
Cyu = fftshift(sqrt(abs(Phiy12).^2./(abs(Phiy1).*abs(Phiy2))));

figure; 
ax = axis();
o1 = semilogx(vec_u(vec_u>0), (((Cyu(vec_u>0)/max(Cyu(vec_u>0)))))); 
hold on;
ax.XAxis.FontSize = 13;
% plot([1.5 1.5], [0 1])
title('$C_{y12}$', 'Interpreter', 'latex', 'FontSize', 18); xlabel('Hz',  'Interpreter', 'latex')



%% Transfer Funtion

Y1 =  dft_matrix*(output1.*hamming_window');
Y2 =  dft_matrix*(output2.*hamming_window');% fft(U)
H = fftshift(Y1./Y2);
U_H = 1/(length(Y1)*Ts); 
vec_H = -length(H)/2:1:(length(H)/2-1); vec_H = vec_H*U_H;
figure;  
subplot(2,1,1);

semilogx(vec_H(vec_H > 0), 20*log10(abs(H(vec_H > 0))))
hold on;


title('Magnitude'); xlabel('Hz')
subplot(2,1,2);
semilogx(vec_H(vec_H > 0), 360/2/pi*atan2(imag((H(vec_H > 0))), real((H(vec_H > 0))))); hold on;
title('Phase'); xlabel('Hz')


%% Nyquist
figure;
Y1 =  dft_matrix*(output1.*hamming_window');
Y2 =  dft_matrix*(output2.*hamming_window');% fft(U)
H = fftshift(Y1./Y2);
% Y =  dft_matrix*(output.*hamming_window');
% U_prbs =  dft_matrix*(prbs'.*hamming_window'); % fft(U)
% H = fftshift(Y./U_prbs);
plot(real(H), imag(H), ':.')
hold on;
plot(-1:0.01:1, sqrt(1 - (-1:0.01:1).^2));
plot(-1:0.01:1, -sqrt(1 - (-1:0.01:1).^2));
axis square
title('Nyquist')