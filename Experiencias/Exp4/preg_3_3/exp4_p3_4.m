Step_initial_value = [0 0];
Step_final_value = [3 2];
% x = [phi dphi theta dtheta w_phi w_theta i_phi i_theta];
initial_condition = [0 0 0 0 0 0 0 0];


%%

figure;
ax = axes(); hold on;
% title('Estados a entrada nula V con referencia de [3 2] V y condiciones iniciales no nulas', 'Interpreter', 'latex', 'FontSize', 18)
for i = 1:8
    o(i) = plot(kstates.Time, kstates.data(:, i), ':.', 'DisplayName', sprintf('Estado %d', i), 'MarkerSize', 12);
end
% plot(states.Time, x0(1)*ones(size(states.Time)), 'r--');
leg = legend('location', 'best');
leg.Interpreter= 'latex';
leg.FontSize = 18;
title('Estados $\phi$ y $\theta$', 'Interpreter', 'latex', 'FontSize', 18)
xlabel('Time [s]', 'Interpreter', 'latex', 'FontSize', 14)
ylabel('phase [rad]', 'Interpreter', 'latex', 'FontSize', 14)
% xlim([0 10])
%%

% x_0 = [0 0 0 0 0 0 0 0];
% u_0 = [0 0 0 0 0 0 0 0];
% vpa(x_0, 4);
% vpa(u_0, 4);

% phi0 = 0;
% theta0 = 0;
% 
y0 = [x0(1) x0(3)];
initial_condition = [pi/20 0 0 0 0 0 0 0];
k_initial_condition = [pi/20 0 0 0 0 0 0 0];
Ts = 0.0001;
% x0pe = eval(subs(x_0, [phi_0 theta_0], [phi0 theta0]));
% u0pe = eval(subs(u_0, [phi_0 theta_0], [phi0 theta0]));
% 
% A = eval(subs(dFdx, x, x0pe));
% B = eval(subs(dFdu, u, u0pe));
q = [10 500 2 400 0 0 0 0];
Q = diag(q);
R = diag(70*ones(1, 2));


[K,S,E]=lqr(A_0,B_0,Q,R,0);

sys = ss(A_0,B_0,C_0,D_0);
V = [[8.6 0]; [0 3.0]]*10^-6;
W = [[1.3 0]; [0 1.7]]*10^-3;


H = eye(2);
H(1) = 1;
H(2) = 10;
G = zeros(8,2);
G(1,1) = 1;
G(2,1) = 1;
G(3,2) = 10;
G(4,2) = 1;
[kest,L,P] = kalman(ss(A_0,[B_0 G],C_0,[D_0 H]),W,V,0);

% sim('function_dxdt.slx',50)
sim('sim_LQG.slx',200)

u1 = squeeze(u.Data(:,1));
u2 = squeeze(u.Data(:,2));

a1 = sum(sum(bsxfun(@times, states.Data*Q, states.Data)));
b1 = sum(sum(bsxfun(@times, [u1  u2]*R, [u1  u2])));
J = a1 + b1


%%

figure;
ax = axes(); hold on;
plot(states.Time, states.data(:, 1), ':.', 'DisplayName', sprintf('Estado %d', i), 'MarkerSize', 12);
plot(kstates.Time, kstates.data(:, 1), ':.', 'DisplayName', sprintf('Estado %d', i), 'MarkerSize', 12);
leg = legend({'$\phi$', '$\phi_K$'}, 'location', 'best');
leg.Interpreter= 'latex';
leg.FontSize = 18;
title('Estado $\phi$', 'Interpreter', 'latex', 'FontSize', 18)
xlabel('Time [s]', 'Interpreter', 'latex', 'FontSize', 14)
ylabel('phase [rad]', 'Interpreter', 'latex', 'FontSize', 14)
Ylim =  get(gca, 'YLim');
text(80,Ylim(1)+diff(Ylim)/15,['J=' num2str(J, '%.2f')],'FontSize',20);
xlim([0 150])
%%

figure;
ax = axes(); hold on;
plot(states.Time, states.data(:, 3), ':.', 'DisplayName', sprintf('Estado %d', i), 'MarkerSize', 12);
plot(kstates.Time, kstates.data(:, 3), ':.', 'DisplayName', sprintf('Estado %d', i), 'MarkerSize', 12);
leg = legend({'$\theta$', '$\theta_K$'}, 'location', 'best');
leg.Interpreter= 'latex';
leg.FontSize = 18;
title('Estado $\theta$', 'Interpreter', 'latex', 'FontSize', 18)
xlabel('Time [s]', 'Interpreter', 'latex', 'FontSize', 14)
ylabel('phase [rad]', 'Interpreter', 'latex', 'FontSize', 14)
Ylim =  get(gca, 'YLim');
text(80,Ylim(1)+diff(Ylim)/15,['J=' num2str(J, '%.2f')],'FontSize',20);
xlim([0 150])