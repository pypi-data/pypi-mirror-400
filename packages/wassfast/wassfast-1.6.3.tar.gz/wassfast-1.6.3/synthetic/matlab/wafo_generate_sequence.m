function [W, STD1] = wafo_generate_sequence( Hm0, Tp, th0, Sp, Nu, Nv, du, dv, Nt, fps )
% WAFO_GENERATE_SEQUENCE Generates a random sea surface elevation sequence
%                        using WAFO
%   
%    Hm0: Significant wave height
%     Tp: Primary peak period
%    th0: Wave direction (ie direction from which waves are coming)
%     Sp: Spreading parameter (lower this number to increase the spreading.
%                              default value: 15)
%     Nu: Number of grid points in X direction
%     Nv: Number of grid points in Y direction
%     du: Grid point spacing in X direction (m)
%     dv: Grid point spacing in Y direction (m)
%     Nt: Number of frames
%    fps: Frames per second 
%
%   Returns:
%      W: wave surface elevation struct
%   STD1: directional spectrum used
%

plotflag = 0; 
ST = torsethaugen([],[Hm0 Tp],plotflag); dt = 0.1; N = 2000;
xs = spec2sdat(ST,N,dt);
D1 = spreading(Nt,'cos',th0,Sp,[],0); %frequency independent
STD1 = mkdspec(ST,D1); 

% to plot the spectrum:
% plotspec(STD1,plotflag)

rng('default'); clf
opt = simoptset('Nt',Nt,'dt',1.0/fps,'Nu',Nu,'du',du,'Nv',Nv,'dv',dv);
W = spec2field(STD1,opt);


end

