% clear all;
% 
% load('parametros.mat');
% ci_modelo_la = x0;
% step = u0;
% 
% 
% %%
% 
% clear all
% ci_mod = [0 0]
% stepp = [2 0]
% 
% ci = zeros(1,8);
% ci(1) = ci_mod(1);
% ci(3) = ci_mod(2);
% 
% s = [ 'Escal�n [\phi \theta]: [' num2str(stepp) ']' newline 'Condiciones iniciales [\phi \theta]: [' num2str(ci_mod) ']']
% 
% %% 3.2.2
% lgd_fs = 24;
% axis_fs = 20;
% 
% xlabel('Tiempo [s]','FontSize',axis_fs)
% ylabel('�ngulo [\pi rad]','FontSize',axis_fs)
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
% title('Simulaci�n en lazo abierto')
% 
% 
% 
% %%
% 
% Ylim =  get(gca, 'YLim');
% text(0.1,Ylim(2)-diff(Ylim)/20, s,'FontSize',lgd_fs, 'Color','black') % xy




%% Modelo no lineal
clear all
cis = [0 0; 0 0; 0.5 0; 0 0.5];
stepps = [2 0; 0 2; 1 1; 1 1];

for i = 1:length(cis)
   
    

ci_mod = cis(i,:);
stepp = stepps(i,:);

ci = zeros(1,8);
ci(1) = ci_mod(1);
ci(3) = ci_mod(2);

s = [ 'Escal�n [\phi \theta]: [' num2str(stepp) ']' newline 'Condiciones iniciales [\phi \theta]: [' num2str(ci_mod) ']'];

sim('modelo.slx',10)


phi = x.Data(:,1);
theta = x.Data(:,3);
tiempo = x.Time;

u1 = squeeze(u.Data(1,1,:));
u2 = squeeze(u.Data(1,2,:));


lgd_fs = 24;
axis_fs = 20;

subplot(2,1,1);
plot(tiempo, phi, tiempo, theta)
set(gca,'FontSize',axis_fs)
set(gca,'ycolor','black') 
set(gca,'xcolor','black') 
xlabel('Tiempo [s]','FontSize',axis_fs)
ylabel('�ngulo [\pi rad]','FontSize',axis_fs)
lgd = legend({'\phi' '\theta'});
lgd.FontSize = lgd_fs;


title('Simulaci�n en lazo abierto','FontSize',lgd_fs)


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

n = ['OL_' num2str(ci_mod,  '%.0f') num2str(stepp,  '%.0f')];
saveas(gcf,['C:\Users\cristobal\Desktop\U\11 semestre\Lab_Cont\LabControl\Experiencias\Exp4\fotos\OL_3_2\' n '.png']);
close

end


%% observabilidad y controlabilidad

clear all;

load('parametros.mat');
Co = ctrb(A_0,B_0);
Ob = obsv(A_0,C_0);

rank(Co) == rank(A_0)
rank(Ob) == rank(A_0)

%% Sistema linealizado
clear all
load('parametros.mat');
cis = [0 0; 0 0; 0.5 0; 0 0.5];
stepps = [2 0; 0 2; 1 1; 1 1];

for i = 1:length(cis)
   
    

ci_mod = cis(i,:);
stepp = stepps(i,:);

ci = zeros(1,8);
ci(1) = ci_mod(1);
ci(3) = ci_mod(2);


s = [ 'Escal�n [\phi \theta]: [' num2str(stepp) ']' newline 'Condiciones iniciales [\phi \theta]: [' num2str(ci_mod) ']'];

sim('modelo_lin.slx',10)


phi = squeeze(x.Data(1,1,:));
theta = squeeze(x.Data(3,1,:));
tiempo = x.Time';


u1 = squeeze(u.Data(1,1,:));
u2 = squeeze(u.Data(2,1,:));


lgd_fs = 24;
axis_fs = 20;

subplot(2,1,1);
plot(tiempo, phi, tiempo, theta)
set(gca,'FontSize',axis_fs)
set(gca,'ycolor','black') 
set(gca,'xcolor','black') 
xlabel('Tiempo [s]','FontSize',axis_fs)
ylabel('�ngulo [\pi rad]','FontSize',axis_fs)
lgd = legend({'\phi' '\theta'});
lgd.FontSize = lgd_fs;


title('Simulaci�n en lazo abierto sistema linealizado','FontSize',lgd_fs)


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

n = ['OL_' num2str(ci_mod,  '%.0f') num2str(stepp,  '%.0f')];
saveas(gcf,['C:\Users\cristobal\Desktop\U\11 semestre\Lab_Cont\LabControl\Experiencias\Exp4\fotos\OL_3_6\' n '_lin.png']);
close

end
