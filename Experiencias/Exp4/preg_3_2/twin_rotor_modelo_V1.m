%IEE2683 Laboratorio de Control Automático
%Actualizado por Matías Troncoso Sept 2015.
%Titulo: Modelo del Twin Rotor

%Descripcion: Esta rutina utiliza el Symbolic Toolbox para encotrar el
%modelo en el espacio de estados del sistema Twin Rotor utilizando a
%partir de las ecuaciones de Lagrange y las modelos dinmicos de motores
%DC.

clc
clear all
%definicion de variables de estado del sistema como variables simbolicas
syms theta phi d_theta d_phi w_t w_p i_t i_p 
%definicion de las segundas derivadas de los estados phi y theta
syms dd_theta dd_phi
%definicion de las variable manipuladas
syms u_t u_p
%definicion de los parametros del sistema
syms d L_t L_b L_e r_ts r_es
syms m_tr m_ts m_t m_b m_m m_e m_er m_es
syms g eps_e eps_t K_p K_t ;
%definición parámetros auxiliares
syms F_phi F_t
syms Ra La Gm B_t B_p Jm_t Jm_p

%Se definen las matrices de rotacion del sistema, que permiten describir la
%posicion absoluta de cada punto respecto a sus coordenadas relativas
R1 = [ cos(phi), 0, sin(phi);
    0, 1,         0;
    -sin(phi), 0,  cos(phi)];
R2 = [  cos(theta), -sin(theta), 0;
    sin(theta), cos(theta), 0;
    0,          0, 1];
R=R2*R1;
%por ejemplo, la masa mtr esta en la posicion relativa [-L_t; -d; 0],
%entonces su posicion absoluta es R*[-L_t; -d; 0]

%Se define la posición relativa de cada masa respecto al centro de
%rotación. Las posiciones se definen dentro de una matriz de posiciones
%para realizar la transformacion una sola vez para todas las posiciones

P_r(:,1) = [-L_t; -d; 0];%masa mtr
P_r(:,2) = [-L_t; -d; 0];%masa mts
P_r(:,3) = [-L_t/2; -d; 0];%masa mt
P_r(:,4) = [0; -d; -L_b/2];%masa mb
P_r(:,5) = [0; -d; -L_b];%masa mm
P_r(:,6) = [L_e/2; -d; 0];%masa me
P_r(:,7) = [L_e; -d; 0];%masa mer
P_r(:,8) = [L_e; -d; 0];%masa mes
%La posición absoluta de cada masa respecto al centro de rotación
P = R*P_r;

%Calculamos la velocidad absoluta de cada masa en terminos de phi, theta,
%d_phi y dtheta utilizando el comando diff (derivada parcial simbolica) y
%la regla de la cadena.
v = diff(P,theta)*d_theta+diff(P,phi)*d_phi;

%Definimos el vector de masas de cada elemento (se define como matriz
%para reducir la cantidad de operaciones)

M = [m_tr m_ts m_t m_b m_m m_e m_er m_es];

%Calculamos los momentos de inercia principales de cada elemento
I_xx = [0 m_ts*r_ts^2/2 0 m_b*L_b^2/12 0 0 0 m_es*r_es^2/2];
I_yy = [0 m_ts*r_ts^2 m_t*L_t^2/12 m_b*L_b^2/12 0 m_e*L_e^2/12 0 m_es*r_es^2/2];
I_zz = [0 m_ts*r_ts^2/2 m_t*L_t^2/12 0 0 m_e*L_e^2/12 0 m_es*r_es^2];

Ep = sum(M*g.*P(3,:));
Ec = 0.5*(sum(v.^2)*transpose(M) + sum(I_yy)*d_phi^2 + sum(I_zz)*d_theta^2);
Ec = simplify(Ec);

%Finalemente el valor de L es:
L = Ec-Ep;
%Definimos el vector de grados de libertad
q = [phi; theta];
%Definimos el vector de primeras derivadas
d_q = [d_phi; d_theta];
%Definimos el vector de derivadas al cuadrado
d_q2 = [d_phi^2; d_theta^2; d_phi*d_theta];
%Definimos el vector de segundas derivadas
dd_q = [dd_phi; dd_theta];

%Se calcula las derivada parcial de cada elemento de L respecto a cada q 
%utilizando la funcion jacobian
eqs1 = jacobian(L,q);
%se calcula la derivada de L respecto a cada d_q
tmp = jacobian(L,d_q);
%Se deriva respecto al tiempo la utlima expresion mediante regla de la
%cadena
eqs2 = jacobian(tmp,[q;d_q])*[d_q; dd_q];
%utilizamos el comando simplify para hacer simplificaciones simbolicas
eqs2=simplify(eqs2);
%Finalemente la ecuación dinamica de lagrange es
eqs = eqs2-transpose(eqs1);
eqs = expand(eqs);
%es importante recoradar que estas son equaciones de Torque, no de fuerzas

%Generlamente las equaciónes de lagrange se pueden escribir como
%J(q) d2q/dt2 + M(q) g + Tc(q) (d2q/dt2)^2  = 0
%donde J(q) es una matriz relacionada a los momentos de inercia del
%sistema, M(q) se relaciona con las masas y Tc(q) se relaciona con las
%fuerzas centrifugas. Podemos encontrar cada uno de los terminos mediante
%los siguientes comandos
J = simplify(jacobian(eqs,dd_q));
eqs2 = simplify(eqs-J*dd_q);
Mg = simplify(diff(eqs,g));
eqs3 = simplify(eqs2-Mg*g);
eqs3 = expand(eqs3);

syms a b c
tmp1 = subs(eqs3,{d_phi^2,d_theta^2},{a, b});
tmp2 = subs(tmp1,{d_phi, d_theta},{sqrt(c),sqrt(c)});
tmp2 = expand(tmp2); 
Tc = simplify(jacobian(tmp2,[a;b;c]));
eqs4 = simplify(eqs3-Tc*d_q2); %eqs4 = 0

%Calculamos los Momentos externos del sistema, que en este caso son los
%roces viscosos y los momentos que ejercen los rotores
M_ext = [-eps_e*d_phi - L_e*K_p*abs(w_p)*w_p;
    -eps_t*d_theta + L_t*K_t*abs(w_t)*w_t + d*K_p*abs(w_p)*w_p*sin(phi)];

% la ecuación de lagrange equivalente es
%eqs_equiv = J*dd_q+Mg*g+Tc*d_q2;

%Una vez encontrado el modelo dinamico del sistema mecanico, nos interesa
%encontrar expresiones para las segundas derivadas de phi y theta. Para
%ello definimos d_Omega = [dd_phi; dd_theta], el cual se puede obtener
%multiplicando a ambos lados la ecuacion equivalente por la matriz inversa
%de J(q)
d_Omega = inv(J)*(M_ext - Mg*g - Tc*d_q2);

%Si observamos el valor de d_Omega en la linea de comandos, se puede
%observar porque es tan necesario utilizar Symbolica Toolbox, en vez de
%resolver las ecuaciones a mano.

%Ahora se expresaran las ecuaciones de los motores 

d_i_t   =   (-Ra/La)*i_t+(-Gm/(La))*w_t+(1/La)*u_t;
d_i_p   =   (-Ra/La)*i_p+(-Gm/(La))*w_p+(1/La)*u_p;

d_w_t   =   (Gm/Jm_t)*i_t+(-B_t/(Jm_t))*w_t;
d_w_p   =   (Gm/Jm_p)*i_p+(-B_p/(Jm_p))*w_p;

%Una vez obtenidas las 6 ecuaciones dinamicas del sistema, podemos
%describir el sistema mediante variables de estado. El vector de estados x
%esta dado por
x = [phi; d_phi; theta; d_theta; w_p; w_t; i_p; i_t];
%Definimos adicionalmente un vector u conteniendo las variables manipualdas
u = [u_p;u_t];

%La ecuacion de estado no lineal que define al sistema completo es
f_x = [d_phi;
    d_Omega(1);
    d_theta;
    d_Omega(2);
    d_w_p;
    d_w_t;
    d_i_p;
    d_i_t];

%La ecuacion de medicion es
g_x =[phi;
    theta];

%Una vez obtenidas las ecuaciones de estado, podemos reemplazar los
%parametros del sistema pos sus valores reales.

%parametros de los motores;
 Ra  =   9;%
 La  =   8.4e-4;%
 Jm_p = 0.25*m_er^2/12;
 Jm_t = 0.15*m_tr^2/12;
 Gm   =  0.0746;%Nm/A o Vs/rad.
 B_t =   4e-4; 
 B_p =   9e-4;


%paramtros del T-R
m_er    =   0.228;
m_e     =   0.0145;
m_tr    =   0.206;
m_t     =   0.0155;
m_m     =   0.068;
m_b     =   0.022;
m_es    =   0.255;
m_ts    =   0.165;
L_e     =   0.24;
L_t     =   0.25;
L_b     =   0.26;
L_m     =   0.26;
r_es    =   0.155;
r_ts    =   0.1;
d       =   0.05;
g       =   9.81;
eps_e   =   2e-3;
eps_t   =   1e-3;

K_p     =   2.2e-4;
K_t     =   3.895e-5;

%Para efectos de modelacion y simulacion es necesario encontrar el punto de
%operacion del sistema. Como queremos que el sistema se mantenga estable en
%una posicion horizontal, definimos
phi_0 = 0.0001;
theta_0 = 0.0;
d_theta_0 = 0;
d_phi_0 = 0;

%luego evaluamos las ecuaciones buscamos los valores de w_p y w_t que son
%necesarios para mantener esa poscion
d_Omega_n = eval(d_Omega);
d_Omega_n = subs(d_Omega_n,{phi,theta,d_phi,d_theta},{phi_0,theta_0,d_phi_0,d_theta_0});
sol=solve(d_Omega_n(1),d_Omega_n(2),w_p,w_t);
w_p_0 = eval(sol.w_p);
w_t_0 = eval(sol.w_t);

%luego, las corrientes en cada motor en regimen permanente son
i_p_0 = B_p*w_p_0/Gm;
i_t_0 = B_t*w_t_0/Gm;

%con lo cual podemos obtener los voltajes de entrada necesarios para
%mantener el punto de operacion.
u_t_0=Ra*i_t_0+Gm*w_t_0;
u_p_0=Ra*i_p_0+Gm*w_p_0;

%Definimos vectorialmente el punto de operacion del sistema, acorde con las
%ecuaciones de estado
x0=[phi_0; d_phi_0; theta_0; d_theta_0; w_p_0; w_t_0; i_p_0; i_t_0]
u0=[u_p_0;u_t_0]

%Para linealizar el sistema es necesario obtener las derivadas parciales de
%cada elemento de f_x y g_x respecto a cada elemento de x y u. Para ello
%utilizamos el comando jacobian.
A = jacobian(eval(f_x),x);
B = jacobian(eval(f_x),u);
C = jacobian(eval(g_x),x);
D = jacobian(eval(g_x),u);


%Las matrices evaluadas en el punto de operacion son
A_0 = subs(A,{x(1),x(2),x(3),x(4),x(5),x(6),x(7),x(8)},{x0(1),x0(2),x0(3),x0(4),x0(5),x0(6),x0(7),x0(8)});
B_0 = subs(B,{x(1),x(2),x(3),x(4),x(5),x(6),x(7),x(8)},{x0(1),x0(2),x0(3),x0(4),x0(5),x0(6),x0(7),x0(8)});
C_0 = subs(C,{x(1),x(2),x(3),x(4),x(5),x(6),x(7),x(8)},{x0(1),x0(2),x0(3),x0(4),x0(5),x0(6),x0(7),x0(8)});
D_0 = subs(D,{x(1),x(2),x(3),x(4),x(5),x(6),x(7),x(8)},{x0(1),x0(2),x0(3),x0(4),x0(5),x0(6),x0(7),x0(8)});

%En algunas versiones de matlab, al evaluar las matrices en x0, el
%resultado sigue siendo del tipo 'sym'. El comando 'eval' transforma los
%valores a tipo 'double'
if strcmp(class(A_0),'sym')
    A_0 = eval(A_0);
end

B_0 = eval(B_0);
C_0 = eval(C_0);
D_0 = eval(D_0);

%Se calcula la observabilidad y controlabilidad del sistema
[Abar,Bbar,Cbar,T,k] = ctrbf(A_0,B_0,C_0)
Estados_controlables = sum(k);
[Abar,Bbar,Cbar,T,k] = obsvf(A_0,B_0,C_0)
Estados_observables = sum(k);

%Almacenamos los parametros del sistema para su uso posterior
save('parametros.mat','A_0','B_0','C_0','D_0','x0','u0');

%Se reemplazan parametros simbolicos por valores reales

f_x = eval(f_x);
g_x = eval(g_x);
f_x = eval(f_x);
g_x = eval(g_x);

%Finalmente generamos la funcion de matlab 'func_f_x.m' que utilizaremos
%para simular el sistema no lineal en Simulink
fid=fopen('func_f_x.m','wt');
fprintf(fid,'function dxdt = func_f_x(x,u) \n');
fprintf(fid,'phi = x(1);d_phi = x(2);theta = x(3);d_theta = x(4);w_p = x(5); w_t = x(6); i_p = x(7); i_t = x(8);\n');
fprintf(fid,'u_p = u(1); u_t = u(2);\n');
fprintf(fid,'dxdt = [');
for k=1:8
    fprintf(fid,'%s;\n',char(f_x(k)));
end
fprintf(fid,'];');

fclose(fid);