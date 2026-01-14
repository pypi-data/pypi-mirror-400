close all
clc
clear

set(0,'defaultAxesFontName', 'Arial')
set(0,'defaultTextFontName', 'Arial')
set(0,'DefaultAxesFontSize',11)
set(0,'DefaultTextFontSize',11)

% her we compute AVG spectrum at different distance from the cameras to
% look at the distribution of S(f) with the stereo range

%% WASS datum
%-----------------------------
%work_dir='/Users/alvise/Desktop/2.CNR/2_WASS/2018_WASS_Kiost_Gageo/3Ds/'
%cd([work_dir '20170915_11/'])

%nc_file='tests/out_fast1.nc';

nc_file='/media/fibe/FIO_2018/KIOST_2018_10_06_14_00/out_fft_128_farneback.nc';
mask = nc_varget(nc_file,'maskZ') < 0.99;

%----------------
% The actual NC file to analyze

%ncname = 'out_wass_128.nc';
%ncname = 'out_fft_128_farneback.nc';
ncname = 'out_fft_128.nc';


%---------------
nc_file=sprintf('/media/fibe/FIO_2018/KIOST_2018_10_06_14_00/%s',ncname);

time=nc_varget(nc_file,'time');
quante=1000;
fps=1.0/(time(3)-time(2));

%nc_file='./out_wass.nc';



%-----------------------------
%%%%% x-y grid
%-----------------------------
xx=nc_varget(nc_file,'X_grid')/1000;
yy=nc_varget(nc_file,'Y_grid')/1000;

%-----------------------------
%%%%% select strip around mid column
%-----------------------------
col_min=round(size(xx,2)/2) -1;
col_max=round(size(xx,2)/2) +1;

%-----------------------------
%%%%% param x fft
%-----------------------------
win_hann=hanning(quante);
dt=1/fps;

Nt=quante;
dur=Nt*dt; % s

df=1/dur;



try
    NCdata.info = ncreadatt(nc_file,'/','info');
    NCdata.generator = ncreadatt(nc_file,'/','generator');
    NCdata.settingsfile = ncreadatt(nc_file,'/','settingsfile');
    NCdata.sf_alpha = ncreadatt(nc_file,'meta','SpecFit.alpha');
    NCdata.sf_smooth_sigma = ncreadatt(nc_file,'meta','SpecFit.final_smooth_sigma');
    NCdata.sf_maxptdist = ncreadatt(nc_file,'meta','PointsReducer.max_pt_distance');
catch ex
    NCdata.generator = 'WASS';
end



%% cycle over different ranges
%-----------------------------

% range in m --------------------------
range=yy(:,1);


% if filter, reduce the length to account for the filter size
z=nc_varget(nc_file,'Z',[0 round(size(xx,1)/2) round(size(xx,2)/2)],[quante 1 1])/1000;
z=fillmissing(z,'nearest');

%-----------------------------
%%%%% frequency axis
%-----------------------------
freq=linspace(-0.5,0.5,Nt)*(1/dt);

%-----------------------------
%%%%% avg_spec
%-----------------------------
avg_spec=zeros(numel(range),Nt)*nan;

%-----------------------------
%%%%% avg_spec welch
%-----------------------------
n_welch=2048;
avg_spec_welch=zeros(numel(range),n_welch/2+1)*nan;

%-----------------------------
%%%%% cycle over rows
%-----------------------------
for rr=1:1:numel(range) %first row is the farthest
    
    
    dummy=      zeros(numel(freq),1); %to store all spectra
    dummy_welch=zeros(n_welch/2+1,1); %to store all spectra
    
    %-----------------------------
    %%%%% cycle over columns
    %-----------------------------
    for cc=col_min:col_max
        
        %-----------------------------
        %%%%% TS
        %-----------------------------
        z=nc_varget(nc_file,'Z',[0 rr-1 cc-1],[quante 1 1])/1000;
        z=fillmissing(z,'nearest');
        
        %-----------------------------
        %%%%% FFT
        %-----------------------------
        z_fft=fftshift(fft((z-mean(z)).*hanning(numel(z))));
        
        %normalize and scale
        z_fft=z_fft./Nt;
        z_fft=abs(z_fft).^2/df;
        
        z_fft=z_fft*sqrt(8/3);
        
        %add
        dummy=dummy+z_fft;
        
        %-----------------------------
        %%%%% welch
        %-----------------------------
        
        [S,f]=cpsd(z-mean(z),z-mean(z),[],[],n_welch,fps);
        dummy_welch=dummy_welch+S;
    
    end
    
    %-----------------------------
    %%%%% store spectra
    %-----------------------------
    avg_spec(rr,:)      =dummy      /(col_max-col_min+1);
    avg_spec_welch(rr,:)=dummy_welch/(col_max-col_min+1);
    
    clear dummy
    %     figure,loglog(freq,avg_spec(rr,:))
end

%-----------------------------
%%%%% FFT: double the energy as I show half-spec
%-----------------------------
avg_spec=avg_spec*2;

%% plot spectra
%-----------------------------
clear Hm0_fft Hm0_welch Tm02_welch Tm01_welch
close all

%-----------------------------
%%%%% select range in m
%-----------------------------
gr=find(range>=-210 & range <=-120); %index of good ranges

%-----------------------------
%%%%% select freq. range
%-----------------------------
gf=find(f >0 & f<20);

%-----------------------------
%%%%% create colomap
%-----------------------------
cmap=jet(numel(gr));

%-----------------------------
%%%%% FFT (avg over columns)
%-----------------------------
% figure,
% clear Hm0_fft
% for rr=1:numel(gr); %all rows
%     rr
%     %plot spectrum
%     loglog(freq,avg_spec(gr(rr),:),'Color',cmap(rr,:)),hold on,
%     
%     %Hm0
%     Hm0_fft(rr)=4*sqrt(   sum(avg_spec(rr,:)/2  .*df)); %/2 because I doubled the energy
%     
% end
% 
% %-----------------------------
% %%%%% Fig properties
% %-----------------------------
% ylabel('S(f) (m^2s)')
% xlabel 'f (1/s)'
% title 'FFT'
% colormap(jet) % forse non va commentato
% hcb=colorbar;
% ylabel(hcb,'Range y (m)');
% xlim([0 max(freq)])
% % ylim([10^-3 10^1])
% 
% %-----------------------------
% %%%%% set colorbar
% %-----------------------------
% delta=(min(range(gr))-max(range(gr)))/10;
% asse_cmap=[min(range(gr)):-delta:max(range(gr))];
% hcb.TickLabels=asse_cmap;
% 
% %-----------------------------
% %%%%% slopes
% %-----------------------------
% f_sl=[0.2:0.1:1];
% x_max=[1];
% y_max=[0.1];
% 
% loglog(f_sl,((f_sl/(x_max*1)).^-4)*y_max,'-k','LineWidth',2)
% loglog(f_sl,((f_sl/(x_max*1)).^-5)*y_max,'--k','LineWidth',2)

%-----------------------------
%%%%% WELCH (avg over columns)
%-----------------------------
figure
df_welch=gradient(f');
conta=0;

clear Hm0_welch Tm01_welch Tm02_welch ni_welch
for rr=gr(1):gr(end); %all rows
    rr
    conta=conta+1;
      
        %plot spectrum
    loglog(f(gf),avg_spec_welch(rr,gf),'Color',cmap(conta,:)),hold on,
    
    %-----------------------------
    %%%%% parameters in a f-range
    %-----------------------------
    
    m0=sum(           avg_spec_welch(rr,gf)             .*df_welch(gf));
    m1=sum(f(gf)'.*   avg_spec_welch(rr,gf)     .*df_welch(gf));
    m2=sum(f(gf)'.^2.*avg_spec_welch(rr,gf)  .*df_welch(gf));
    
    %Hm0
    Hm0_welch(conta)=4*sqrt(m0);
    % Tm01
    Tm01_welch(conta)=m0/m1;
    % Tm02
    Tm02_welch(conta)=sqrt(m0/m2);
    % ni
    ni_welch(conta)=sqrt(m0*m2/m1^2-1);
    
end

%-----------------------------
%%%%% plot far field minus near field
%-----------------------------
% loglog(f(gf),avg_spec_welch(gr(1),gf)-avg_spec_welch(gr(end),gf),'k','LineWidth',5)

%-----------------------------
%%%%% Fig properties
%-----------------------------
ylabel('S (m^2s)')
xlabel 'f_a (1/s)'
title(sprintf('welch %s\n%s', NCdata.generator,ncname),'interpreter', 'none' );
ylim([1E-4, 1E2])
colormap(jet(numel(gr)))
hcb=colorbar;
ylabel(hcb,'Range y-axis (m)');
box on, grid on
% ylim([10^-3 10^1])
xlim([min(f), max(f)])

%-----------------------------
%%%%% slopes
%-----------------------------
f_sl=[0.2:0.1:1.2];
x_max=[0.7];
y_max=[0.01];

loglog(f_sl,((f_sl/(x_max*1)).^-4)*y_max,'-k','LineWidth',2)
%% loglog(f_sl,((f_sl/(x_max*1)).^-5)*y_max,'--k','LineWidth',2)

%-----------------------------
%%%%% set colorbar
%-----------------------------
delta=(min(range(gr))-max(range(gr)))/10;
asse_cmap=[min(range(gr)):-delta:max(range(gr))];
hcb.TickLabels=asse_cmap;

%if strcmp( NCdata.generator, 'WASS' )
%    saveas(gcf,'figs/welch_wass.png');
%else
%    saveas(gcf,sprintf('figs/welch_wfast_%s.png',NCdata.settingsfile) );
%end
saveas(gcf,sprintf('figs/welch_%s.png',ncname) );

return;
%-----------------------------
%%%%% PLOT Hmo, Tm01, Tm02 vs. range
%-----------------------------
figure,

subplot(1,3,1)
plot(range(gr),Hm0_welch)
title 'Hm0',xlabel 'range (m)'

subplot(1,3,2)
plot(range(gr),Tm01_welch)
title 'Tm01',xlabel 'range (m)'

subplot(1,3,3)
plot(range(gr),Tm02_welch)
title 'Tm02',xlabel 'range (m)'
