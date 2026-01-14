%%
% Initializes all the settings for the WASS REALTIME pipeline
%
clc;clear;close all;

% Absoute path of an already processed sequence with the same geometrical
% configuration to be used by WASS REALTIME
DATADIR='/media/fibe/FIO_2018/KIOST_2018_10_06_14_00/output/';
FIRST_FRAME=1;

% Spectrum size 
N=256;

% Filename of the output configuration file
%
OUTFILE=sprintf('/media/fibe/FIO_2018/KIOST_2018_10_06_14_00/config_KIOST_2018_10_06_14_00_%d.mat',N);

% Plane file
%
PLANEFILE='/media/fibe/FIO_2018/KIOST_2018_10_06_14_00/output/planes.txt';

% Camera baseline in meters
%
CAM_BASELINE=5.0;

% Area center and size in meters
area_center = [0, -150];
area_size = 230;


%%
scale = CAM_BASELINE;
area_size_m = floor( area_size / 2);
xmin = area_center(1)-area_size_m;
xmax = area_center(1)+area_size_m;
ymin = area_center(2)-area_size_m;
ymax = area_center(2)+area_size_m;

%%

prev=cd(sprintf('%s/%06d_wd',DATADIR,FIRST_FRAME));

K0 = importdata('K0_small.txt');
K1 = importdata('K1_small.txt');
R = importdata('Cam0_poseR.txt');
T = importdata('Cam0_poseT.txt');
P0cam = importdata('P0cam.txt');
P1cam = importdata('P1cam.txt');
%scale = importdata('scale.txt');

plane = importdata(PLANEFILE);
if size(plane,1)>1
    plane = mean(plane,1)';
    cd(prev);
    dlmwrite('plane_avg_recomputed.txt',plane,'precision',10);
    PLANEFILE = sprintf('%s/plane_avg_recomputed.txt',pwd());
end
cd(prev);

%%

[mesh,Rpl,Tpl]=load_camera_mesh_and_align_plane(DATADIR, FIRST_FRAME, CAM_BASELINE, PLANEFILE);
mesh_subsample = 10;

zmax = quantile(mesh(:,3),0.98);
zmin = quantile(mesh(:,3),0.02);

scatter( mesh(1:mesh_subsample:end,1), mesh(1:mesh_subsample:end,2), '.k' );
axis ij;

axis equal;
grid on;
hold on;
plot( [xmin, xmax, xmax, xmin, xmin], [ymin,ymin,ymax,ymax,ymin], '-r', 'LineWidth',2);
title('Extent of the reconstructed area (m)');

%%
% P0plane
Ri = Rpl'; 
Ti = -Rpl'*Tpl; 
%Ri = Rpl;
%Ti = Tpl;
I = imread( sprintf('%s/%06d_wd/undistorted/00000000.png',DATADIR,FIRST_FRAME) );
Iw = size(I,2); 
Ih = size(I,1); 
SCALEi = 1.0./CAM_BASELINE; 
 
ToNorm = [ 2.0/Iw,  0,    -1  0; ... 
              0   2.0/Ih  -1  0; ... 
              0      0     1  0; ... 
              0      0     0  1]; 
P0plane = ToNorm*[P0cam;0 0 0 1]*[Ri,Ti;0 0 0 1]*[SCALEi,0,0,0; 0,SCALEi,0,0; 0,0,-SCALEi,0; 0,0,0,1];
P1plane = ToNorm*[P1cam;0 0 0 1]*[Ri,Ti;0 0 0 1]*[SCALEi,0,0,0; 0,SCALEi,0,0; 0,0,-SCALEi,0; 0,0,0,1];

%%
% gridding

[XX,YY] = meshgrid( linspace(xmin,xmax,N), linspace(ymin,ymax,N) );
x_spacing = XX(1,2)-XX(1,1);
y_spacing = YY(2,1)-YY(1,1);
assert( abs(x_spacing - y_spacing) < 1E-5 );

kx_ab = (-N/2:N/2-1)./(N).*(2*pi/x_spacing);
ky_ab = (-N/2:N/2-1)./(N).*(2*pi/y_spacing);
[KX_ab, KY_ab] = meshgrid( kx_ab, ky_ab);
spec_scale = 1.0/(N*N);


%%
% Export everything
save(OUTFILE, 'xmin','xmax','ymin','ymax', 'zmin', 'zmax','scale','CAM_BASELINE', ...
              'R', 'T', 'Rpl', 'Tpl', 'P0cam', 'P1cam', 'P0plane', 'P1plane', 'K0', 'K1',         ...
              'N', ...
              'XX', 'YY', 'KX_ab', 'KY_ab', 'spec_scale', 'x_spacing', 'y_spacing' ...
    );

