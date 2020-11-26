%% create MPC controller object with sample time
mpcobj = mpc(sys, Ts);
%% specify prediction horizon
mpcobj.PredictionHorizon = 100;
%% specify control horizon
mpcobj.ControlHorizon = 50;
%% specify nominal values for inputs and outputs
mpcobj.Model.Nominal.U = 0;
mpcobj.Model.Nominal.Y = [0;0];
%% specify constraints for MV and MV Rate
mpcobj.MV(1).Min = 0;
mpcobj.MV(1).Max = VMAX_AMP;
%% specify overall adjustment factor applied to weights
beta = 0.61878;
%% specify weights
mpcobj.Weights.MV = 0*beta;
mpcobj.Weights.MVRate = 0.738905609893065/beta;
mpcobj.Weights.OV = [0 0.1]*beta;
mpcobj.Weights.ECR = 100000;
% %% specify overall adjustment factor applied to estimation model gains
% alpha = 3.1623;
% %% adjust custom output disturbance model gains
% setoutdist(mpcobj, 'model', mpcobj_ModelOD*alpha);
% %% adjust custom measurement noise model gains
% mpcobj.Model.Noise = mpcobj.Model.Noise/alpha;
% %% specify simulation options
% options = mpcsimopt();
% options.RefLookAhead = 'off';
% options.MDLookAhead = 'off';
% options.Constraints = 'on';
% options.OpenLoop = 'off';
% %% run simulation
% sim(mpcobj, 1001, mpcobj_RefSignal, mpcobj_MDSignal, options);
