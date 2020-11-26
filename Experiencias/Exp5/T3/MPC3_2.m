%% create MPC controller object with sample time
mpcobj = mpc(mpcobj_plant_C, 0.01);
%% specify prediction horizon
mpcobj.PredictionHorizon = 80;
%% specify control horizon
mpcobj.ControlHorizon = 50;
%% specify nominal values for inputs and outputs
mpcobj.Model.Nominal.U = 0;
mpcobj.Model.Nominal.Y = [0;0];
%% specify constraints for MV and MV Rate
mpcobj.MV(1).Min = 0;
mpcobj.MV(1).Max = 22;
%% specify overall adjustment factor applied to weights
beta = 1.8965;
%% specify weights
mpcobj.Weights.MV = 0*beta;
mpcobj.Weights.MVRate = 0.439294039406504/beta;
mpcobj.Weights.OV = [0.227637962343178 0.1682029674]*beta;
mpcobj.Weights.ECR = 100000;
% %% specify overall adjustment factor applied to estimation model gains
% alpha = 0.95499;
% %% adjust default output disturbance model gains
% setoutdist(mpcobj, 'model', getoutdist(mpcobj)*alpha);
% %% adjust default measurement noise model gains
% mpcobj.Model.Noise = mpcobj.Model.Noise/alpha;
% %% specify simulation options
% options = mpcsimopt();
% options.RefLookAhead = 'off';
% options.MDLookAhead = 'off';
% options.Constraints = 'on';
% options.OpenLoop = 'off';
% %% run simulation
% sim(mpcobj, 1001, mpcobj_RefSignal, mpcobj_MDSignal, options);
