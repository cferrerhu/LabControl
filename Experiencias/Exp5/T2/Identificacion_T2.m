
clear all
clc
TANK_CONFIGURATION = 2;
tanque_n = num2str(TANK_CONFIGURATION);
setup_lab_tanks;

tiempo = 25*60; % tiempo a simular (sin transiente inicial)
Ts = 0.01; % frec sampleo
cant_escalones = 10; % cantidad de pert en el tiempo
DC = 15; % Valor de la entrada a la que se suman las pert
pert = 5; % ancho de las perturbaciones ej. randi([-pert pert])
trans_inicial = 200; % transiente inicial en segundos


largo = tiempo/Ts;
entrada = DC*ones(largo, 1);
cada = largo/cant_escalones;

cont = 1;
pert_ant = 0;
for c = 1:length(entrada)
    
    if cont > cada
        pert_ant = randi([-pert pert]);
        cont = 1;
    else
        cont = cont + 1;
    end
    entrada(c)  = entrada(c) + pert_ant;
   
end

largo_trans = trans_inicial/Ts;
entrada =  [DC*ones(largo_trans, 1); entrada];

%%
sim('s_tanks_2_LA.slx', length(entrada)*Ts)

%%
entr = entrada(largo_trans+1:end);
resp = salida.Data(largo_trans+1:end-1,:);


%%
T1 = 0:Ts:tiempo;
T1 = T1(2:end);
lgd_fs = 24;
axis_fs = 20;

yyaxis left
plot(T1,entr);
ylabel('Voltaje [V]','FontSize',axis_fs)

yyaxis right
plot(T1,resp);
ylabel('Altura [cm]','FontSize',axis_fs)

grid on


title(['Identificación Tanque ' tanque_n],'FontSize',lgd_fs)

set(gca,'FontSize',axis_fs)
set(gca,'ycolor','black') 
set(gca,'xcolor','black') 
xlabel('Tiempo [s]','FontSize',axis_fs)

lgd = legend({'Entrada ' 'Respuesta '});
lgd.FontSize = lgd_fs;

set(findall(gcf,'Type','line'),'LineWidth',3);

port = get(0, 'MonitorPositions');
set(gcf,'position',port(2,:))


saveas(gcf,['C:\Users\cristobal\Desktop\U\11 semestre\Lab_Cont\LabControl\Experiencias\Exp5\T' tanque_n '\fotos\Iden_T' tanque_n '.png']);
% close

%%
data = iddata(resp,entr,Ts);

%%
sys = n4sid(data, 4);
save('sys2','sys')
%%
load('sys2')
%%
MPC2;

%% Sin ruido

step = [20 20];
step_time = 100;
ic = 39.4;
N_power = [0 0];
%%
sim('s_tanks_2_CL.slx',400)

%%
tiempo = salida_controlada.Time;
sen_salida = salida_controlada.Data;
sen_entrada = referencia_controlada.Data;
Vp = Vp_controlada.Data;

J = trapz(abs(sen_entrada(step_time/Ts:end,:) - sen_salida(step_time/Ts:end,:))*Ts);

%% Sin ruido
lgd_fs = 24;
axis_fs = 20;






lgd_fs = 24;
axis_fs = 20;



subplot(2,1,1);

hold on
plot(tiempo, sen_entrada, tiempo, sen_salida)
title(['Simulación MPC Tanque ' tanque_n ' sin ruido'],'FontSize',lgd_fs)



set(gca,'FontSize',axis_fs)
set(gca,'ycolor','black') 
set(gca,'xcolor','black') 
xlabel('Tiempo [s]','FontSize',axis_fs)
ylabel('Altura [cm]','FontSize',axis_fs)
lgd = legend({'Referencia T1' 'Referencia T2' 'Respuesta T1' 'Respuesta T2'});
lgd.FontSize = lgd_fs;

set(findall(gcf,'Type','line'),'LineWidth',3);

set(gca,'YLim',[0 25])
Ylim =  get(gca, 'YLim');
Xlim =  get(gca, 'XLim');
text(step_time+10,Ylim(1)+diff(Ylim)/15,['J=' num2str(J(2), '%.1f') 'V*s'],'FontSize',30)
plot([step_time step_time],Ylim, 'color', 'black')
hold off


subplot(2,1,2); 
plot(tiempo, Vp,'LineWidth',3)
set(gca,'FontSize',axis_fs)
set(gca,'ycolor','black') 
set(gca,'xcolor','black') 
xlabel('Tiempo [s]','FontSize',axis_fs)
ylabel('Voltaje [V]','FontSize',axis_fs)
lgd = legend({'Vp'});
lgd.FontSize = lgd_fs;



port = get(0, 'MonitorPositions');
set(gcf,'position',port(2,:))


saveas(gcf,['C:\Users\cristobal\Desktop\U\11 semestre\Lab_Cont\LabControl\Experiencias\Exp5\T' tanque_n '\fotos\CL_T' tanque_n '.png']);



%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%Con ruido

step = [20 20];
step_time = 100;
ic = 39.4;
N_power = [0.5 0.5];
%%
sim('s_tanks_2_CL.slx', 400)

%%
tiempo = salida_controlada.Time;
sen_salida = salida_controlada.Data;
sen_entrada = referencia_controlada.Data;
Vp = Vp_controlada.Data;

J = trapz(abs(sen_entrada(step_time/Ts:end,:) - sen_salida(step_time/Ts:end,:))*Ts);

%% Con ruido
 
lgd_fs = 24;
axis_fs = 20;



subplot(2,1,1);

hold on
plot(tiempo, sen_entrada, tiempo, sen_salida)
title(['Simulación MPC Tanque ' tanque_n ' con ruido'],'FontSize',lgd_fs)



set(gca,'FontSize',axis_fs)
set(gca,'ycolor','black') 
set(gca,'xcolor','black') 
xlabel('Tiempo [s]','FontSize',axis_fs)
ylabel('Altura [cm]','FontSize',axis_fs)
lgd = legend({'Referencia T1' 'Referencia T2' 'Respuesta T1' 'Respuesta T2'});
lgd.FontSize = lgd_fs;

set(findall(gcf,'Type','line'),'LineWidth',3);

set(gca, 'YLim', [0 25]);
Ylim =  get(gca, 'YLim');
Xlim =  get(gca, 'XLim');
text(step_time+10,Ylim(1)+diff(Ylim)/15,['J=' num2str(J(2), '%.1f') 'V*s'],'FontSize',30)
plot([step_time step_time],Ylim, 'color', 'black')
hold off


subplot(2,1,2); 
plot(tiempo, Vp,'LineWidth',3)
set(gca,'FontSize',axis_fs)
set(gca,'ycolor','black') 
set(gca,'xcolor','black') 
xlabel('Tiempo [s]','FontSize',axis_fs)
ylabel('Voltaje [V]','FontSize',axis_fs)
lgd = legend({'Vp'});
lgd.FontSize = lgd_fs;



port = get(0, 'MonitorPositions');
set(gcf,'position',port(2,:))


saveas(gcf,['C:\Users\cristobal\Desktop\U\11 semestre\Lab_Cont\LabControl\Experiencias\Exp5\T' tanque_n '\fotos\CLN_T' tanque_n '.png']);

