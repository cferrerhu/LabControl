%% create MPC controller object with sample time
mpcobj = mpc(sys, 0.01);
%% specify prediction horizon
mpcobj.PredictionHorizon = 200;
%% specify control horizon
mpcobj.ControlHorizon = 100;
%% specify nominal values for inputs and outputs
mpcobj.Model.Nominal.U = 0;
mpcobj.Model.Nominal.Y = 0;
%% specify constraints for MV and MV Rate
mpcobj.MV(1).Min = 0;
mpcobj.MV(1).Max = 22;
%% specify constraints for OV
mpcobj.OV(1).Min = 0;
mpcobj.OV(1).Max = 25;
%% specify overall adjustment factor applied to weights
beta = 4.7588;
%% specify weights
mpcobj.Weights.MV = 0*beta;
mpcobj.Weights.MVRate = 0.1/beta;
mpcobj.Weights.OV = 1*beta;
mpcobj.Weights.ECR = 100000;
%% specify simulation options
options = mpcsimopt();
options.RefLookAhead = 'off';
options.MDLookAhead = 'off';
options.Constraints = 'on';
options.OpenLoop = 'off';
%% run simulation
% sim(mpcobj, 20001, mpcobj_RefSignal_6, mpcobj_MDSignal_6, options);