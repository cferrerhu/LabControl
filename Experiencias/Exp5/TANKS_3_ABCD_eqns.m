% Matlab equation file: "TANKS_3_ABCD_eqns.m"
% Open-Loop State-Space Matrices: A, B, C, and D
% for the Quanser Coupled Tanks - Configuration #3 Experiment.

A( 1, 1 ) = -1/2*Ao1*2^(1/2)*g/(g*L10)^(1/2)/At1;
A( 1, 2 ) = 0;
A( 1, 3 ) = 0;
A( 2, 1 ) = 1/2*Ao1*2^(1/2)/(g*L10)^(1/2)*g/At2;
A( 2, 2 ) = -1/2*Ao2*2^(1/2)/(g*L20)^(1/2)*g/At2;
A( 2, 3 ) = 0;
A( 3, 1 ) = 0;
A( 3, 2 ) = 1;
A( 3, 3 ) = 0;

B( 1, 1 ) = -Kp*(-1+gamma)/At1;
B( 2, 1 ) = gamma*Kp/At2;
B( 3, 1 ) = 0;

C( 1, 1 ) = 0;
C( 1, 2 ) = 1;
C( 1, 3 ) = 0;

D( 1, 1 ) = 0;
