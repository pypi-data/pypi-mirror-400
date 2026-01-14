%%
confmat = load('/media/fibe/FIO_2018/KIOST_2018_10_06_14_00/config_KIOST_2018_10_06_14_00_256.mat');
DATADIR = '/media/fibe/FIO_2018/KIOST_2018_10_06_14_00/output/';
PLANEFILE='/media/fibe/FIO_2018/KIOST_2018_10_06_14_00/output/planes.txt';
netcdf_file = '/media/fibe/FIO_2018/KIOST_2018_10_06_14_00/out_wass_256.nc';
dt=1.0/15.0;
%%

plane = importdata(PLANEFILE);cd 

if size(plane,1)>1
    plane = mean(plane,1)';
    dlmwrite('plane_avg_recomputed.txt',plane,'precision',10);
    PLANEFILE = sprintf('%s/plane_avg_recomputed.txt',pwd());
end

%%
filone2netcdf_02_create_v2(netcdf_file,confmat.N,confmat.N)
nc_varput(netcdf_file,'X_grid', confmat.XX*1000)% in mm
nc_varput(netcdf_file,'Y_grid', confmat.YY*1000) % in mm
nc_varput(netcdf_file,'fps', 1/dt) % in hz
%nc_varput(netcdf_file,'datenum', date_acq) % matlab datenum
x_spacing = confmat.XX(1,2)-confmat.XX(1,1);
nc_varput(netcdf_file,'dxy', x_spacing*1000)% in mm
nc_varput(netcdf_file,'scale', 1.0)% in mm
clear('XX','YY','x_spacing');
%%

for idx=1:4000
    % Unzip if necessary
    workdir = sprintf('%s/%06d_wd', DATADIR, idx );
    disp(workdir);
    workdirzip = [workdir,'.zip'];
    
    was_unzipped = 0;    
    if exist(workdir','dir') ~= 7
            
        if exist(workdirzip','file')==2
            prev = cd(DATADIR);
            unzip(workdirzip);
            cd(prev);
            was_unzipped = 1;
        else
            fprintf( '%s does not exist, exiting\n', workdir);
            break;
        end
    end

    
    [mesh,Rpl,Tpl]=load_camera_mesh_and_align_plane(DATADIR, idx, confmat.CAM_BASELINE, PLANEFILE);
    
    disp('interpolating...');
    F = scatteredInterpolant(mesh(:,1),mesh(:,2),mesh(:,3),'linear','none');
    ZZ = F( confmat.XX, confmat.YY );
    
    data_frame = struct;
    %%% 3D datum
    data_frame.time = idx*dt;
    data_frame.count = idx;

    % z in mm _________________________________
    data_frame.Z = ZZ.*1000;
    nc_addnewrecs(netcdf_file, data_frame);

        
end