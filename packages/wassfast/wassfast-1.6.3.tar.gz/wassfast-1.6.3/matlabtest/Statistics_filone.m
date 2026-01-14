clear
close all
clc

set(0,'defaultAxesFontName', 'Arial')
set(0,'defaultTextFontName', 'Arial')
set(0,'DefaultAxesFontSize',18)
set(0,'DefaultTextFontSize',18)

%% nc file

%javaaddpath(['C:\MWASS_analysis\mwass' '/netcdfAll-4.2.jar']);
%javaaddpath (['C:\MWASS_analysis\mwass' '/mexcdf/snctools/classes']);

%addpath (['C:\MWASS_analysis\mwass\mexcdf.r4033\' '/mexcdf/mexnc']);
%addpath (['C:\MWASS_analysis\mwass\mexcdf.r4033\' '/mexcdf/snctools']);

%% WASS data

%%%   -----   STATION Papa -----

% % % % SP1
% cd('/Volumes/Data/StationPapaStereoData/StereoXYZResults_FullCapture_WindDirection_BestQC/28Dec2014/1929UTC/XYZResults')
% nc_file='SP_2014_12_28_1929_LONG_smoothTS_lowess06_fil_1.0Hz.nc'
% quante=15600;

% % % % % SP2
% cd('/Volumes/Data/StationPapaStereoData/StereoXYZResults_FullCapture_WindDirection_BestQC/05Jan2015/2030UTC')
% nc_file='SP_2015_01_05_2030_LONG_smoothTS_lowess06_fil_1.0Hz.nc'
% quante=13050;

%%%   -----   CRIMEA -----

% cd('/Volumes/Data/2016_Stereo_IFREMER_Pedro/2013_Crimea_data/run_2013-09-26_11h45m02.045sZ_12Hz/3D')
% nc_file='Surfaces_interp_smoothTS_lowess06_fil_2.0Hz.nc'
% quante=21578

%%%   -----   Acqua Alta -----

% cd('/Users/alvise/Desktop/2.CNR/2_WASS/4_WASS_PTF/W2014_07___2014_03_27_0910_Bora_WC_radar_CROSS_SEA/3D')
% nc_file='wass__20140327_091000_step03_smoothTS_lowess08.nc'
% quante=20000


% cd '/Users/alvise/Desktop/2.CNR/2_WASS/4_WASS_PTF/W2018_04_09_Scirocco_0e94_breaking_polarim/3D/'
% nc_file='PTF__20180409_130727_sirocco.nc'
% quante=7000


% % % cd('/Users/alvise/Desktop/2.CNR/2_WASS/4_WASS_PTF/W2014_04___2014_03_10_0940UTC_Bora_BRICCONE/PP')
% % % nc_file='wass__20140310_094000_step03_smoothTS_lowess08.nc'
% % % quante=20000


%%%%  ------ ORS ----
%cd '/Users/alvise/Desktop/2.CNR/2_WASS/2018_WASS_Kiost_Gageo/3Ds/20170915_14/'
nc_file='../out.nc';
quante=numel(nc_varget(nc_file,'count'));


%%%% FIO
% dir_nc='/Users/alvise/Desktop/2.CNR/2_WASS/16_WASS_FIO/1_wass/2_wind/10ms/'
% cd(dir_nc)
% nc_file='wass__20171008_000000_step03.nc'
% quante=2254
% %%

%-----------------------------
%%%%% subsapling in time
%-----------------------------
div=3; %susampling in time
var_dummy=round(quante/div);

%-----------------------------
%%%%% subsapling in space
%-----------------------------
sub=5; %every sub points SP1, SP2

Xg=nc_varget(nc_file,'X_grid'); % in  m
mask = nc_varget(nc_file,'maskZ') < 0.99;

limi=1:sub:size(Xg,1); %>1 se voglio togliere i pti pi? lontani
limj=1:sub:size(Xg,2); 

% variable to be filled
dummy=zeros(numel(limi),numel(limj),var_dummy)*nan;

% cycle
conta=0;
for ii=1:div:quante
    conta=conta+1;
    ii
    ZI1=nc_varget(nc_file,'Z',[ii-1 0 0],[1 inf inf]);
    ZI1(mask) = nan;
    ZI1=ZI1(limi,limj);
    
    dummy(:,:,conta)=ZI1;
%     mino(conta)=min(ZI1(:));
end

E_3d   =nanmean(dummy(:))
std_3d =nanstd(dummy(:))
sk_3d  =skewness(dummy(:))
ku_3d  =kurtosis(dummy(:))
Hs    =4*std_3d

% return
%% pdf

% nell'immagine 629*15 e dintorni c'? un po' do rumore in un cavo
% dummy(dummy<-16000)=nan;

std_data=std_3d;
sk_data=sk_3d;
kurt_data=ku_3d;


dato=(dummy(:)-nanmean(dummy(:)))/(std_data);
dato=dato(isnan(dato)==0);

[pdf_y pdf_x]=hist(dato,[-6.4:0.4:6.4]); % on Hs

dpdfx=pdf_x(2)-pdf_x(1);

pdf_xx=[-7:0.2:7]; % on std
% GAUSS
pdf_gauss = pdf('Normal',pdf_xx,mean(dato),1);
pdf_gauss=1/sqrt(2*pi)*exp(-0.5*pdf_xx.^2);
% G-C3
GC3_pdf=pdf_gauss.*(1+sk_data/6*(pdf_xx.^3-3*pdf_xx));
% G-C4
GC4_pdf=pdf_gauss.*(1+sk_data/6*(pdf_xx.^3-3*pdf_xx)+...
    (kurt_data-3)/24*(pdf_xx.^4-6*pdf_xx.^2+3));
%% plot
figure
semilogy(pdf_x,pdf_y/numel(dato)/dpdfx,'sb','MarkerFaceColor','b','MarkerSize',7)
hold on
semilogy(pdf_xx,pdf_gauss,'--k','LineWidth',2)
semilogy(pdf_xx,GC3_pdf,':k','LineWidth',2)
semilogy(pdf_xx,GC4_pdf,'k','LineWidth',2)
legend('OBS','G','G-C3','G-C4')
grid on
xlabel 'z / \sigma (-)'
ylabel 'Histogram, pdf'
xlim([min(pdf_xx) max(pdf_xx)])

% some data

str={sprintf('\\sigma = %1.2f m',std_3d/1000),...
    sprintf('m_3 = %1.2f',sk_data),sprintf('m_4 = %1.2f',kurt_data)}
text(-1,10^-4,str)
