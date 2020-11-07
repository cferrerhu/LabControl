%% Sistema linealizado, LQR solo
clear all
load('parametros.mat');
load('LQR.mat')
% cis = [0 0; 0 0; 0.5 0; 0 0.5];
% stepps = [2 0; 0 2; 1 1; 1 1];


% Q = [8 0 0 0 0 0 0 0;
%     0 0.1 0 0 0 0 0 0;
%     0 0 10 0 0 0 0 0;
%     0 0 0 0.1 0 0 0 0;
%     0 0 0 0 0.1 0 0 0;
%     0 0 0 0 0 1 0 0;
%     0 0 0 0 0 0 0.1 0;
%     0 0 0 0 0 0 0 1;
%     ];
% 
% R = [1 0;
%     0 0.01];



for i = 1:length(Qs)
 
Q = Qs{i,1}
R = Rs{i,1};
[K,S,e] = lqr(A_0,B_0,Q,R);

K

ci = zeros(1,8);
ci(1) = 0.5;
ci(3) = -0.5;



sim('LQR_sim_lin.slx',60)

estados = squeeze(x.Data);
phi = squeeze(x.Data(:,1));
theta = squeeze(x.Data(:,3));
tiempo = x.Time';

u1 = squeeze(u.Data(:,1));
u2 = squeeze(u.Data(:,2));


a = sum(sum(bsxfun(@times, estados*Q, estados)));
b = sum(sum(bsxfun(@times, [u1  u2]*R, [u1  u2])));
J = a + b


lgd_fs = 24;
axis_fs = 20;

subplot(2,1,1);
plot(tiempo, phi, tiempo, theta)
set(gca,'FontSize',axis_fs)
set(gca,'ycolor','black') 
set(gca,'xcolor','black') 
xlabel('Tiempo [s]','FontSize',axis_fs)
ylabel('聲gulo [\pi rad]','FontSize',axis_fs)
lgd = legend({'\phi' '\theta'});
lgd.FontSize = lgd_fs;

Ylim =  get(gca, 'YLim');
text(50,Ylim(1)+diff(Ylim)/20,['J=' num2str(J, '%.0f')],'FontSize',30)

title('Simulaci鏮 controlador LQR linealizado','FontSize',lgd_fs)


subplot(2,1,2);
plot(tiempo, u1, tiempo, u2)


set(gca,'FontSize',axis_fs)
set(gca,'ycolor','black') 
set(gca,'xcolor','black') 
xlabel('Tiempo [s]','FontSize',axis_fs)
ylabel('Voltaje [V]','FontSize',axis_fs)
lgd = legend({'v_{\Phi}' 'v_{\theta}'});
lgd.FontSize = lgd_fs;

set(findall(gcf,'Type','line'),'LineWidth',5);

port = get(0, 'MonitorPositions');
set(gcf,'position',port(2,:))



n = ['LQR_' num2str(i)];
saveas(gcf,['C:\Users\cristobal\Desktop\U\11 semestre\Lab_Cont\LabControl\Experiencias\Exp4\fotos\OL_3_7\' n '_lin.png']);
close

end




%%
% 
% 
% 
% phi = x.Data(:,1);
% theta = x.Data(:,2);
% tiempo = x.Time;
% 
% 
% lgd_fs = 24;
% axis_fs = 20;
% plot(tiempo, phi, tiempo, theta)
% 
% xlabel('Tiempo [s]','FontSize',axis_fs)
% ylabel('聲gulo [\pi rad]','FontSize',axis_fs)
% 
% 
% set(gca,'FontSize',axis_fs)
% set(gca,'ycolor','black') 
% set(gca,'xcolor','black') 
% 
% lgd = legend({'Phi' 'Theta'});
% lgd.FontSize = lgd_fs;
% 
% 
% set(findall(gcf,'Type','line'),'LineWidth',5);
% title('Simulaci鏮 linealizada en lazo abierto')
% 
% 
% %%
% 
% 
% Q = [8 0 0 0 0 0 0 0;
%     0 0.1 0 0 0 0 0 0;
%     0 0 10 0 0 0 0 0;
%     0 0 0 0.1 0 0 0 0;
%     0 0 0 0 0.1 0 0 0;
%     0 0 0 0 0 1 0 0;
%     0 0 0 0 0 0 0.1 0;
%     0 0 0 0 0 0 0 1;
%     ];
% 
% R = [1 0;
%     0 0.01];
% 
% [K,S,e] = lqr(A_0,B_0,Q,R);
% 
% %%
% phi = x.Data(:,1);
% theta = x.Data(:,3);
% tiempo = x.Time;
% 
% 
% lgd_fs = 24;
% axis_fs = 20;
% plot(tiempo, phi, tiempo, theta)
% 
% xlabel('Tiempo [s]','FontSize',axis_fs)
% ylabel('聲gulo [\pi rad]','FontSize',axis_fs)
% 
% 
% set(gca,'FontSize',axis_fs)
% set(gca,'ycolor','black') 
% set(gca,'xcolor','black') 
% 
% lgd = legend({'Phi' 'Theta'});
% lgd.FontSize = lgd_fs;
% 
% 
% set(findall(gcf,'Type','line'),'LineWidth',5);
% title('Respuesta controlador LQR')
% 
% %%
% 
% sum(sum(x.Data*Q*x.Data'))
% sum(sum((-K*x.Data')'*R*(-K*x.Data')))
% 
% a = sum(sum(bsxfun(@times, x.Data*Q, x.Data)));
% b = sum(sum(bsxfun(@times, (-K*x.Data')'*R, (-K*x.Data')')));
% 
% 
% 
% %%
% 
% txt = '0';
% text(pi,sin(pi),txt,'FontSize',14)


%% Kalman

Ts = 0.0001;
sys = ss(A_0,B_0,C_0,D_0);
V = [[8.6 0]; [0 3.0]]*10^-4;
W = [[1.3 0]; [0 1.7]]*10^-6;

Q = cov(W);
R = cov(V);
H = eye(2);
G = zeros(8,2);
G(1,1) = 1;
G(3,2) = 1;

[kest,L,P] = kalman(ss(A_0,[B_0 G],C_0,[D_0 H]),W,V,0);





%% LQR  lineal con Kalman
clear all
load('parametros.mat');
load('LQR.mat')
Ts = 0.0001;

ci = zeros(1,8);
ci(1) = 0.2;
ci(3) = 0;


 
i = 5;

Q = Qs{i}
R = Rs{i};

[K,S,e] = lqr(A_0,B_0,Q,R);


sys = ss(A_0,B_0,C_0,D_0);
V = [[8.6 0]; [0 3.0]]*10^-4;
W = [[1.3 0]; [0 1.7]]*10^-6;
Ruido = [2 2]*10^-6;

H = eye(2);
G = zeros(8,2);
G(1,1) = 20;
G(3,2) = 20;

[kest,L,P] = kalman(ss(A_0,[B_0 G],C_0,[D_0 H]),W,V,0);


sim('LQR_sim_lin_kalman.slx',60)

estados = squeeze(x.Data);
phi = squeeze(x.Data(:,1));
theta = squeeze(x.Data(:,3));
tiempo = x.Time';

estados_kal = squeeze(x_kal.Data);
phi_kal = squeeze(x_kal.Data(:,1));
theta_kal = squeeze(x_kal.Data(:,3));

u1 = squeeze(u.Data(:,1));
u2 = squeeze(u.Data(:,2));


a = sum(sum(bsxfun(@times, estados*Q, estados)));
b = sum(sum(bsxfun(@times, [u1  u2]*R, [u1  u2])));
J = a + b;

lgd_fs = 24;
axis_fs = 20;

subplot(2,1,1);
plot(tiempo, phi, tiempo, phi_kal)
set(gca,'FontSize',axis_fs)
set(gca,'ycolor','black') 
set(gca,'xcolor','black') 
xlabel('Tiempo [s]','FontSize',axis_fs)
ylabel('聲gulo [\pi rad]','FontSize',axis_fs)
lgd = legend({'\phi' '\phi estimado'});
lgd.FontSize = lgd_fs;

Ylim =  get(gca, 'YLim');
text(50,Ylim(1)+diff(Ylim)/15,['J=' num2str(J, '%.0f')],'FontSize',30);

title('Simulaci鏮 controlador LQR linealizado','FontSize',lgd_fs)


subplot(2,1,2);
plot(tiempo, theta, tiempo, theta_kal)
set(gca,'FontSize',axis_fs)
set(gca,'ycolor','black') 
set(gca,'xcolor','black') 
xlabel('Tiempo [s]','FontSize',axis_fs)
ylabel('聲gulo [\pi rad]','FontSize',axis_fs)
lgd = legend({'\theta' '\theta estimado'});
lgd.FontSize = lgd_fs;

set(findall(gcf,'Type','line'),'LineWidth',5);

port = get(0, 'MonitorPositions');
set(gcf,'position',port(2,:))





n = ['lin_kal_' num2str(i)];
saveas(gcf,['C:\Users\cristobal\Desktop\U\11 semestre\Lab_Cont\LabControl\Experiencias\Exp4\fotos\CL_3_8\' n '.png']);

%% LQR no lineal con Kalman
clear all
load('parametros.mat');
load('LQR.mat')
Ts = 0.0001;

ci = zeros(1,8);
ci(1) = 0.2;
ci(3) = 0;


Q = Qs{5};
R = Rs{5};
[K,S,e] = lqr(A_0,B_0,Q,R);


sys = ss(A_0,B_0,C_0,D_0);
V = [[8.6 0]; [0 3.0]]*10^-4;
W = [[1.3 0]; [0 1.7]]*10^-6;


H = eye(2);
G = zeros(8,2);
G(1,1) = 1;
G(3,2) = 1;

[kest,L,P] = kalman(ss(A_0,[B_0 G],C_0,[D_0 H]),W,V,0);






