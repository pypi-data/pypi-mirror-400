%%
clc; clear; close all;
initwafo

%%
RENDER_DEBUG_FRAMES = 1;

Nu = 1024; 
du = 0.115; 
fps = 5.0;
%Nt = fps*60*5; % Number of frames in each scenario
Nt = 20; % Number of frames in each scenario
SCENARIOS = 1;  % Number of simulation instances

Hm0_min = 5.0;
Hm0_max = 8.0;
Tp_min = 7.2;
Tp_max = 8.8;

Sp_min = 15.0;
Sp_max = 22.0;

OUT_FILE = sprintf('waves_%dx%d_%dfps_single_scenario.h5',Nu,Nu,fps);

%%

delete(OUT_FILE);

for scn=0:(SCENARIOS-1)
    dataset = sprintf('/%04d/',scn);
    h5create( OUT_FILE, [dataset,'fps'], [ 1 ], 'Datatype', 'single' );
    h5create( OUT_FILE, [dataset,'dt'], [ 1 ], 'Datatype', 'single' );
    h5create( OUT_FILE, [dataset,'KxKy'], [ 2,Nu,Nu ], 'Datatype', 'double' );
    h5create( OUT_FILE, [dataset,'ZminZmax'], [ 2 ], 'Datatype', 'single' );
    h5create( OUT_FILE, [dataset,'waveangle'], [ 1 ], 'Datatype', 'single' );
    h5disp( OUT_FILE )
    
    
    h5writepermuted(OUT_FILE, [dataset,'fps'], [fps]);
    h5writepermuted(OUT_FILE, [dataset,'dt'], [1.0/fps]);
    

    Hm0 = (Hm0_max-Hm0_min).*rand()+Hm0_min; 
    Tp = (Tp_max-Tp_min).*rand()+Tp_min; 
    th0 = rand()*2.0*pi;%scn*0.5*pi;%pi*0.5;%
    Sp = (Sp_max-Sp_min).*rand()+Sp_min; 

    h5writepermuted(OUT_FILE, [dataset,'waveangle'], [th0]);
    
    fprintf('## Scenario %4d\n',scn);
    fprintf(' Hm0: %3.2f\n',Hm0);
    fprintf('  Tp: %3.2f\n',Tp);
    fprintf(' th0: %3.2f\n',th0);
    fprintf('  Sp: %3.2f\n',Sp);

    [W,S] = wafo_generate_sequence( Hm0, Tp, th0, Sp, Nu, Nu, du, du, Nt, fps );
    close all;

    kx_ab = (-Nu/2:Nu/2-1)./(Nu).*(2*pi/du);
    ky_ab = (-Nu/2:Nu/2-1)./(Nu).*(2*pi/du);
    [Kx, Ky] = meshgrid( kx_ab, ky_ab);
    KxKy(:,:,1) = Kx;
    KxKy(:,:,2) = Ky;
    
    h5writepermuted(OUT_FILE, [dataset,'KxKy'], KxKy );

    ZZ = single( permute( W.Z, [3,1,2]) );
    
%%
    zmin = min(min(min(ZZ)));
    zmax = max(max(max(ZZ)));
    
    h5writepermuted(OUT_FILE, [dataset,'ZminZmax'], [zmin, zmax]);
    clear('Zd');
    Zd = zeros( Nt-3,Nu,Nu,3);
    
    for curridx=2:(size(ZZ,1)-2)
        fprintf('%d/%d\n',curridx,(size(ZZ,1)-2));
        Zcurr = ZZ(curridx,:,:);
        Zprev = ZZ(curridx-1,:,:);
        Znext = ZZ(curridx+1,:,:);
        
        %% debug
        if RENDER_DEBUG_FRAMES
            zimg = uint8( ((squeeze(Zcurr)-zmin) ./ (zmax-zmin))*255 );
            imwrite(zimg,sprintf('fig/scn_%03d_%06d.png',scn,curridx));
        end
    
        Zd(curridx-1,:,:,1)=Zprev;
        Zd(curridx-1,:,:,2)=Zcurr;
        Zd(curridx-1,:,:,3)=Znext;
        
    end
    
    h5create( OUT_FILE, [dataset,'data'], [ 3, Nu, Nu, size(Zd,1) ], 'Chunksize', [3,Nu,Nu,8], 'Datatype', 'single' );
    h5writepermuted(OUT_FILE, [dataset,'data'], Zd );

end

%%
fprintf('Generated dataset:\n');
h5disp( OUT_FILE );
fprintf('All done!\n');


