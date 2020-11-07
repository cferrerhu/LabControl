Step_initial_value = [0 0];
Step_final_value = [3 2];

initial_condition = [9 0 0 0 0 0 0 0];

%%

% states.data

figure;
ax = axes(); hold on;
title('Estados a entrada nula V con referencia de [3 2] V y condiciones iniciales no nulas', 'Interpreter', 'latex', 'FontSize', 18)
for i = 1:8
    o(i) = plot(states.Time, states.data(:, i), ':.', 'DisplayName', sprintf('Estado %d', i), 'MarkerSize', 10);
end
leg = legend('location', 'best');
leg.Interpreter= 'latex';
leg.FontSize = 14;

%% Parameters

mer = 0.288;
me = 0.0145;
mtr = 0.206;
mt = 0.0155;
mm = 0.068;
mb = 0.022;
mes = 0.255;
mts = 0.165;
Le = 0.45;
Lt = 0.25;
Lb = 0.26;
Lm = 0.26;
res = 0.155;
rts = 0.1;
d = 0.05;
g = 9.81;
zeta_phi = 2e-4;
zeta_theta = 1e-4;
K_phi = 6.08e-5;
K_theta = 3.6e-5;

Jm = 1.272e-4;
La = 0.86;
Ra = 8;
G = 0.0202;
B_theta = 2.3e-5;
B_phi =4.5e-5;


%%

syms phi_0 theta_0 i_phi i_theta w_phi w_theta v_phi v_theta real

eq5 = G*i_phi == B_phi*w_phi;
eq6 = G*i_theta == B_theta*w_theta;
eq7 = v_phi == Ra*i_phi + G*w_phi;
eq8 = v_theta == Ra*i_theta + G*w_theta;
% eq2 = (mt/2 + mtr + mts)*g*Lt*cos(phi_0) - (me/2 + mer + mes)*g*Le*cos(phi_0) - ...
%     (mb/2 + mm)*g*Lb*sin(phi_0) + Le*K_phi*sign(w_phi)*w_phi^2 == 0;
eq2 = (mt/2 + mtr + mts)*g*Lt*cos(phi_0) - (me/2 + mer + mes)*g*Le*cos(phi_0) - ...
    (mb/2 + mm)*g*Lb*sin(phi_0) + Le*K_phi*w_phi^2 == 0;
% eq4 = Lt*K_theta*sign(w_theta)*w_theta^2 == d*K_phi*sign(w_phi)*w_phi^2;
eq4 = Lt*K_theta*w_theta^2 == d*K_phi*w_phi^2;
%%

S = solve([eq2, eq4, eq5, eq6, eq7, eq8], [i_phi, i_theta, w_phi, w_theta, v_phi, v_theta]);

%%
Msolution = zeros(4, 6);
Msolution(:, 1) = eval(subs(S.i_phi, [phi_0, theta_0], [0, 0]));
Msolution(:, 2)= eval(subs(S.i_theta, [phi_0, theta_0], [0, 0]));
Msolution(:, 3) = eval(subs(S.w_phi, [phi_0, theta_0], [0, 0]));
Msolution(:, 4) = eval(subs(S.w_theta, [phi_0, theta_0], [0, 0]));
Msolution(:, 5) = eval(subs(S.v_phi, [phi_0, theta_0], [0, 0]));
Msolution(:, 6)= eval(subs(S.v_theta, [phi_0, theta_0], [0, 0]));
% solution [i_phi i_theta w_phi w_theta v_phi v_theta]
Msolution(4, :)

 vpa(S.i_theta(4), 4)
%%
syms dphi dtheta phi theta Iyy Iyz Iyz Izz Izx Ixy real

%Calculamos los momentos de inercia principales de cada elemento
I_xx = [0 mts*rts^2/2 0 mb*Lb^2/12 0 0 0 mes*res^2/2];
I_yy = [0 mts*rts^2 mt*Lt^2/12 mb*Lb^2/12 0 me*Le^2/12 0 mes*res^2/2];
I_zz = [0 mts*rts^2/2 mt*Lt^2/12 0 0 me*Le^2/12 0 mes*res^2];
M = [mtr mts mt mb mm me mer mes];
Pr = [-Lt -Lt -Lt/2 0 0 Le/2 Le Le;
    -d -d -d -d -d -d -d -d; 
    0 0 0 -Lb/2 -Lm 0 0 0];
Ixy = sum(M.*Pr(1, :).*Pr(2, :));
Iyz = sum(M.*Pr(2, :).*Pr(3, :));
Izx = sum(M.*Pr(3, :).*Pr(2, :));
Ixx = sum(I_xx + M.*(Pr(2, :).^2 + Pr(3, :).^2));
Iyy = sum(I_yy + M.*(Pr(1, :).^2 + Pr(3, :).^2));
Izz = sum(I_zz + M.*(Pr(1, :).^2 + Pr(2, :).^2));
%%
f1 = dphi;
f3 = dtheta;
J = [Iyy -Iyz; -Iyz Izz];
Tc =[0 -Izx 0; Ixy 0 2*Izx];
Tg = (mt/2 + mtr + mts)*g*Lt*cos(phi) - (me/2 + mer + mes)*g*Le*cos(phi) - ...
    (mb/2 + mm)*g*Lb*sin(phi);
Mg = [Tg; 0];
zeta = [zeta_phi, zeta_theta];
% Mp = [Le*K_phi*sign(w_theta)*w_phi^2; Lt*K_theta*sign(w_theta)*w_theta^2 - d*K_phi*sign(w_phi)*w_phi^2];
Mp = [Le*K_phi*w_phi^2; Lt*K_theta*w_theta^2 - d*K_phi*w_phi^2];
faux = inv(J)*(Tc*[dphi^2; dtheta^2; dtheta*dphi] + Mg - zeta*[dphi; dtheta] + Mp);
f2 = faux(1); f4 = faux(2);
f5 = (G*i_phi - B_phi*w_phi)/Jm;
f6 = ( G*i_theta - B_theta*w_theta)/Jm;
f7 = (-v_phi + Ra*i_phi + G*w_phi)/Jm;
f8 = (-v_theta + Ra*i_theta + G*w_theta)/Jm;
F = [f1; f2; f3; f4; f5; f6; f7; f8];

%%
x = [phi dphi theta dtheta w_phi w_theta i_phi i_theta];
x_0 = [phi_0 0 theta_0 0 S.w_phi(4) S.w_theta(4) S.i_phi(4) S.i_theta(4)];
u = [v_theta v_phi];
u_0 = [S.v_theta(4) S.v_phi(4)];

dFdx = jacobian(F, x);
dFdu = jacobian(F, u);

deltau = u - u_0;
deltax = x - x_0;
ddeltaxdt = subs(dFdx, x, x_0)*deltax' + subs(dFdu, u, u_0)*deltau';
%%

%%

vpa((ddeltaxdt(4)) , 4)

%%

