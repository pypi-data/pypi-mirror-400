% clear
% close all

set(0,'defaultAxesFontName', 'Arial')
set(0,'defaultTextFontName', 'Arial')
set(0,'DefaultAxesFontSize',18)
set(0,'DefaultTextFontSize',18)

scrsz = get(0,'ScreenSize');

%-----------------------------
%%%%% mexnc
%-----------------------------
%javaaddpath(['C:\MWASS_analysis\mwass' '/netcdfAll-4.2.jar']);
%javaaddpath (['C:\MWASS_analysis\mwass' '/mexcdf/snctools/classes']);
%addpath((['C:\MWASS_analysis\mwass\mexcdf.r4033\' '/mexcdf/mexnc']));
%addpath((['C:\MWASS_analysis\mwass\mexcdf.r4033\' '/mexcdf/snctools']));

%% WASS file
%-----------------------------

%-----------------------------
%%%%% work dir
%-----------------------------
%work_dir='/Users/alvise/Desktop/2.CNR/2_WASS/2018_WASS_Kiost_Gageo/3Ds'

%-----------------------------
%%%%% sequence
%-----------------------------
%cd     ([work_dir '/20170915_14/'])
nc_file='../out.nc'

%-----------------------------
%%%%% parameters
%-----------------------------
ncid_new = netcdf.open(nc_file, 'NC_WRITE');
varid_Z_new = netcdf.inqVarID(ncid_new,'Z');
xx=nc_varget(nc_file,'X_grid');
yy=nc_varget(nc_file,'Y_grid');

Times = nc_varget(nc_file,'time');
fps=1.0/(Times(3)-Times(2));%nc_varget(nc_file,'fps');

quanti=numel(nc_varget(nc_file,'count'));


%% prepare variables
steppo=10; % sub-sampling in space to speed up

map_std=xx(1:steppo:size(xx,1),1:steppo:size(xx,2))*nan;
map_mean=map_std*nan;
map_min=map_std*nan;
map_max=map_std*nan;
map_Hmax=map_std*nan;
map_skew=map_std*nan;
map_kurt=map_std*nan;
map_count_data=map_std*nan;


conta_ii=0;
for ii=1:steppo:size(xx,1)
    ii/size(xx,1)*100
    conta_ii=conta_ii+1;
    
    conta_jj=0;
    for jj=1:steppo:size(xx,2)
        conta_jj=conta_jj+1;

        tic
        % se uso nc_varget, carica i nan dove sono. mentre netcdf.getVar
        
        zz_rw=nc_varget(nc_file,'Z',[0 ii-1 jj-1],[quanti 1 1]);
        
        %         zz_rw = double(squeeze(netcdf.getVar(ncid_new,varid_Z_new,...
        %             [jj-1 ii-1 0],[1 1 quanti])));
        time_read=toc;
        
        map_count_data(ii,jj)=numel(zz_rw)-sum(isnan(zz_rw));
        
        ts_new=zz_rw;
        
        %%%% store data x ts_new (TS smooth).
        map_std (conta_ii,conta_jj)=std(ts_new);
        map_mean(conta_ii,conta_jj)=mean(ts_new);
        map_min (conta_ii,conta_jj)=min(ts_new);
        map_max (conta_ii,conta_jj)=max(ts_new);
        map_skew(conta_ii,conta_jj)=skewness(ts_new(isnan(ts_new)<1));
        map_kurt(conta_ii,conta_jj)=kurtosis(ts_new(isnan(ts_new)<1));
        
%         %Z-C
%         if sum(isnan(ts_new))==0;
%             
%             [ind,up,down,crest,trough,height,period] = ...
%                 zero_crossing_v2(ts_new-nanmean(ts_new),0,0,fps);
%             
%             
%             H=crest-trough;
%             map_Hmax(ii,jj)=max(H);
%         end
    end
end

%%
xx=nc_varget(nc_file,'X_grid');
yy=nc_varget(nc_file,'Y_grid');

xx=xx/1000;
yy=yy/1000;

%%
figure(4), clf

subplot(2,2,1)
imagesc(xx(1:steppo:size(xx,1),1:steppo:size(xx,2)),yy(1:steppo:size(xx,1),1:steppo:size(xx,2)),4*map_std)
title(sprintf('Hs = 4*STD (mean = %1.1f m)',4*nanmean(map_std(:)/1000)))
colorbar,colormap(jet)
caxis([0.8 1.2]*4*nanmean(map_std(:)))
% caxis([700 1700])

subplot(2,2,2)
imagesc(xx(1:steppo:size(xx,1),1:steppo:size(xx,2)),yy(1:steppo:size(xx,1),1:steppo:size(xx,2)),map_mean)
title 'mean',colorbar,colormap(jet)
caxis([-1 1]*150)

subplot(2,2,3)
imagesc(xx(1:steppo:size(xx,1),1:steppo:size(xx,2)),yy(1:steppo:size(xx,1),1:steppo:size(xx,2)),map_skew)
title 'skewness',colorbar,colormap(jet)
caxis([0.1 1]*0.2)

subplot(2,2,4)
imagesc(xx(1:steppo:size(xx,1),1:steppo:size(xx,2)),yy(1:steppo:size(xx,1),1:steppo:size(xx,2)),map_kurt)
title 'kurtosis',colorbar,colormap(jet)
caxis([2.5 3.5])

return
%% if the nc is small I can load it

zz=nc_varget(nc_file,'Z');
xx=nc_varget(nc_file,'X_grid');
yy=nc_varget(nc_file,'Y_grid');

%

map_mean=squeeze(nanmean(zz,1));
map_std=squeeze(nanstd(zz,1));
% map_skew=squeeze(skewness(zz,0,1));

%%
close all

figure,
subplot(1,2,1)
mesh(xx,yy,map_mean),axis xy, title 'mean',colorbar

subplot(1,2,2),
mesh(xx,yy,map_std),axis xy, title 'std',colorbar

figure
        imagesc(map_skew),caxis([0.2 1])
