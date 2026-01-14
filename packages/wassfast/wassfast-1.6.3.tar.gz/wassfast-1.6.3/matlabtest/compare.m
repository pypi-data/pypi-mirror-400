%
clc;clear;close all;

nc_wass = '/media/fibe/FIO_20181/sequence_20181006_14/wass__20181006_140000_MINE.nc';
nc_wfast = '/media/fibe/FIO_20181/sequence_20181006_14/wassfast__20181006_140000_CNN.nc';

%nc_wfast = '/media/fibe/FIO_2018/sequence_20181006_10/out_wassfast_griddata.nc';
%nc_wass = '/media/fibe/FIO_2018/sequence_20181006_10/wass__20181006_100000_step03.nc';
%nc_wfast = '/media/fibe/FIO_2018/sequence_20181006_17/wassfast__20181006_170000_0.4.nc';
%nc_wass =
%'/media/fibe/FIO_2018/sequence_20181006_17/wass__20181006_170000_step03.nc';%


zrange = [-5 5]; % in meters

%%


XX=nc_varget(nc_wfast,'X_grid')/1000;
YY=nc_varget(nc_wfast,'Y_grid')/1000;
fprintf("Data shape:\n");
disp( size(XX))

XX_gt=nc_varget(nc_wass,'X_grid')/1000;
YY_gt=nc_varget(nc_wass,'Y_grid')/1000;


try
    mask = nc_varget(nc_wfast,'maskZ') < 0.99;
catch ME
    mask = XX*0;
end

%assert( sum(sum(XX-XX_gt))<1E-8 );
%assert( sum(sum(YY-YY_gt))<1E-8 );
%%
figure; hold on;
scatter( XX(:), YY(:), 'or');
scatter( XX_gt(:), YY_gt(:), '.k');
grid on;
%close all;

%%
% Sample some timeseries and measure the error
Si = floor(size(XX,1)/2)-6:2:floor(size(XX,1)/2)+7;
Sj = floor(size(XX,2)/2)-6:2:floor(size(XX,2)/2)+7;

Z_all = [];
Zgt_all = [];
for pti=Si
    for ptj=Sj
        fprintf('Sampling timeserie at %d %d\n',pti,ptj);
        
        index = find( XX_gt==XX(pti,ptj) & YY_gt==YY(pti,ptj));
        [pti_gt, ptj_gt] = ind2sub( size(XX_gt), index);
        
        Zgt = squeeze( nc_varget( nc_wass,'Z',[0,pti_gt,ptj_gt],[inf,1,1]) )';
        Z = squeeze(  nc_varget( nc_wfast,'Z',[1,pti,ptj],[inf,1,1]) )';

        common = min( numel(Z), numel(Zgt) );
        Zgt_all= [Zgt_all, Zgt(10:common)];
        Z_all= [Z_all, Z(10:common)];
                
    end
end

diff = nanmean( abs(Zgt_all - Z_all) );
fprintf('Average diff: %f\n',diff);
fprintf('    WASS mean: %f\n',nanmean(Zgt_all));
fprintf('WASSfast mean: %f\n',nanmean(Z_all));

Zgtmean = nanmean(Zgt_all);
Zmean = nanmean(Z_all);
Zgt_all = Zgt_all - Zgtmean;
Z_all = Z_all - Zmean;
diff = nanmean( abs(Zgt_all - Z_all) );
fprintf('Average diff (after 0-mean normalization): %f\n',diff);
%%
% Timeserie
pti = floor(size(XX,1)/2);
ptj = floor(size(XX,2)/2);
index = find( XX_gt==XX(pti,ptj) & YY_gt==YY(pti,ptj));
[pti_gt, ptj_gt] = ind2sub( size(XX_gt), index);
% 

Zgt = nc_varget( nc_wass,'Z',[0,pti_gt,ptj_gt],[inf,1,1]);
Zgt = Zgt - nanmean(Zgt);
Z = nc_varget( nc_wfast,'Z',[0,pti,ptj],[inf,1,1]);
Z = Z - nanmean(Z);
common = min( numel(Z), numel(Zgt) );

diff = nanmean( abs(Zgt(1:common)-Z(1:common)) );
fprintf('Average diff: %f\n',diff);

figure;
plot( Zgt(1:common), '-k'); hold on;
plot(   Z(1:common), '.-r'); hold on;
grid minor;
xlabel('Frames')
ylabel('Elevation (mm)')
legend('WASS', 'WASSfast');

%%
% Average elevation

% Zgt = squeeze( ncread( nc_wass,'Z',[20,20,1], [128-20,128-20,4000] ) );
% Zgtmean = squeeze(nanmean( nanmean(Zgt, 1), 2));
% clear Zgt
% 
% disp(nanmean(Zgtmean))
% 
% Z = squeeze( ncread( nc_wfast,'Z',[20,20,1], [128-20,128-20,4000] ) );
% Zmean = squeeze(nanmean( nanmean(Z, 1), 2));
% clear Z
% 
% disp(nanmean(Zmean))
% 
% figure;
% plot( Zgtmean, '-k'); hold on;
% plot(   Zmean, '.-r'); hold on;
% grid on;
% legend('WASS', 'WASSfast');
% title('Average surface elevation')



return
%%
%index = find( XX_gt==XX(1,1) & YY_gt==YY(1,1));
%[topleft_i_gt, topleft_j_gt] = ind2sub( size(XX_gt), index);
%index = find( XX_gt==XX(end,end) & YY_gt==YY(end,end));
%[bottomright_i_gt, bottomright_j_gt] = ind2sub( size(XX_gt), index);

pti = floor(size(XX,1)/2);
ptj = floor(size(XX,2)/2);
index = find( XX_gt==XX(pti,ptj) & YY_gt==YY(pti,ptj));
[pti_gt, ptj_gt] = ind2sub( size(XX_gt), index);


for idx=20

    Zgt = ncread( nc_wass,'Z', [pti_gt-50,ptj_gt-50,idx], [100,100,1] )';
    %Zgt(mask) = nan;
    Z = ncread( nc_wfast,'Z', [pti-50,ptj-50,idx], [100,100,1] )';
    %Z(mask) = nan;

    %%

    figure;
    %pcolor(XX_gt/1000,YY_gt/1000,Zgt/1000);
    imagesc(Zgt)
    axis ij;
    caxis( zrange );
    axis equal;
    colorbar;
    shading flat;
    title(sprintf('WASS idx=%d',idx) );
    saveas(gcf, sprintf('figs/compare_%05d_W.png',idx));
    close all;
    
    %%
    
    figure;
    %pcolor(XX/1000,YY/1000,Z/1000);
    imagesc(Z)
    axis ij;
    caxis( zrange );
    axis equal;
    colorbar;
    shading flat;
    title(sprintf('WASSfast idx=%d',idx) );
    saveas(gcf, sprintf('figs/compare_%05d_Wf.png',idx));
    close all;
    
end