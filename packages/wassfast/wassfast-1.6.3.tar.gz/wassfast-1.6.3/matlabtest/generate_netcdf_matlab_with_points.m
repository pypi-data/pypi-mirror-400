%%
clc; clear; close all;

confmat = load('/DATASCRATCH/realtime/config.mat');
DATADIR = '/DATASCRATCH/realtime/out_20180409T130727_east_break_polarim_camswap/';
PLANEFILE='/DATASCRATCH/realtime/out_20180409T130727_east_break_polarim_camswap/planes.txt';
netcdf_file = '/DATASCRATCH/realtime/out_wass_128_pts.nc';
dt=0.2;
N=4000;

%%

plane = importdata(PLANEFILE);cd 

if size(plane,1)>1
    plane = mean(plane,1)';
    dlmwrite('plane_avg_recomputed.txt',plane,'precision',10);
    PLANEFILE = sprintf('%s/plane_avg_recomputed.txt',pwd());
end

%%

oufile=filone2netcdf_02_create_v2(netcdf_file,confmat.N,confmat.N);
nc_varput(netcdf_file,'X_grid', confmat.XX*1000)% in mm
nc_varput(netcdf_file,'Y_grid', confmat.YY*1000) % in mm
nc_varput(netcdf_file,'fps', 1/dt) % in hz
%nc_varput(netcdf_file,'datenum', date_acq) % matlab datenum
x_spacing = confmat.XX(1,2)-confmat.XX(1,1);
nc_varput(netcdf_file,'dxy', x_spacing*1000)% in mm
nc_varput(netcdf_file,'scale', 1.0)% in mm
clear('XX','YY','x_spacing');

Npts = 4096;
nc_add_dimension(oufile,'Npts',Npts) % Number of points 

%------------------------------------------------------------
% Add variable --> Pts
% ------------------------------------------------------------
varstruct.Name = 'Pts';
varstruct.Nctype = 'float';
varstruct.Dimension = {'count','Npts','pointdim'};
% varstruct.Deflate = 0;
varstruct.Attribute.Name = '_FillValue';
varstruct.Attribute.Value = NaN;
% varstruct.Attribute.Name = 'scale_factor';
% varstruct.Attribute.Value = 1/1000;
nc_addvar(oufile,varstruct)
nc_attput(oufile,'Pts','long_name','3D points')
nc_attput(oufile,'Pts','units','millimeter')

mask_set=0;

%%
for idx=0:N
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
    
    %%
    scalefacx = confmat.xmax-confmat.xmin;
    scalefacy = confmat.ymax-confmat.ymin;
    pts = mesh(:,1:2)';
    pts(1,:) = (pts(1,:)-confmat.xmin) / scalefacx -0.5;
    pts(2,:) = (pts(2,:)-confmat.ymin) / scalefacy -0.5;
    
    close all;
    kpt = pointreducer( pts, 0.005);
    pts3d = [pts(1:2,kpt); mesh(kpt,3)'];
    assert(size(pts3d,2)>Npts)
    
    indices_to_keep = randperm(size(pts3d,2));
    indices_to_keep = indices_to_keep(1:Npts);
    
    pts3d = pts3d(:,indices_to_keep);
    
    %figure,scatter( pts3d(1,:), pts3d(2,:), 10, pts3d(3,:), 'filled' ); axis equal;
    %axis([-0.5, 0.5, -0.5, 0.5]); caxis([-3 3]);
    
    %figure;
    %pcolor(( confmat.XX-confmat.xmin-0) / scalefacx -0.5,...
    %       ( confmat.YY-confmat.ymin-0) / scalefacy -0.5, ZZ); axis equal; shading flat;
    %axis([-0.5, 0.5, -0.5, 0.5]);caxis([-3 3]);
    
    %%
    
    
    if mask_set==0
        %%
        mask = ~isnan(ZZ);
        mask = imgaussfilt( double(mask),7);
        mask = mask>0.99;

        mask = imgaussfilt( double(mask),3);
        
        
        mask = mask .* (tukeywin(size(mask,1),0.1)'.*tukeywin(size(mask,1),0.1));
        imagesc(ZZ.*mask)
        
        nc_varput(netcdf_file,'mask_Z', mask)
        mask_set=1;
        %%
    end
    
    %%
    data_frame = struct;
    %%% 3D datum
    data_frame.time = idx*dt;
    data_frame.count = idx;

    % z in mm _________________________________
    data_frame.Z = ZZ.*1000;
    
    % p3d
    data_frame.Pts =  pts3d';
    nc_addnewrecs(netcdf_file, data_frame);

    
        
end