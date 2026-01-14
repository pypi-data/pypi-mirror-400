%%
clc; clear; close all;
initwafo

%%

OUT_FILE = 'waves_256x256_test.h5';

Nu = 256; 
du = 0.46; 
fps = 1.0;
Nt = fps * 10; % Number of frames per random batch
BATCHES = 100;  % Number of batches


Hm0_min = 5.0;
Hm0_max = 8.0;
Tp_min = 7.2;
Tp_max = 8.8;

Sp_min = 15.0;
Sp_max = 22.0;

%%
h5create( OUT_FILE, '/data', [ Inf, Nu, Nu, 1 ], 'Chunksize', [8,Nu,Nu,1], 'Datatype', 'single' );
h5disp( OUT_FILE )


for ii=1:BATCHES
    fprintf('%d/%d',ii,BATCHES);
    Hm0 = (Hm0_max-Hm0_min).*rand()+Hm0_min; 
    Tp = (Tp_max-Tp_min).*rand()+Tp_min; 
    th0 = rand()*2.0*pi;
    Sp = (Sp_max-Sp_min).*rand()+Sp_min; 

    fprintf('## Batch %4d\n',ii);
    fprintf(' Hm0: %3.2f\n',Hm0);
    fprintf('  Tp: %3.2f\n',Tp);
    fprintf(' th0: %3.2f\n',th0);
    fprintf('  Sp: %3.2f\n',Sp);

    [W,S] = wafo_generate_sequence( Hm0, Tp, th0, Sp, Nu, Nu, du, du, Nt, fps );
    close all;
    ZZ = single( permute( W.Z, [3,1,2]) );
    zmin = min(min(min(ZZ)));
    zmax = max(max(max(ZZ)));

    %f = figure;
    %imagesc(  squeeze(ZZ(1,:,:)) );
    %caxis( [-Hm0 Hm0] );
    %axis equal;
    %colorbar;
    %title( sprintf('%06d',ii) );
    %drawnow;
    %saveas( f, sprintf('fig/%06d.png',ii ) );
    %close all;
    
    % Append to H5
    kk = h5info(OUT_FILE);
    last_idx = kk.Datasets(1).Dataspace(1).Size(1) + 1;
    h5write(OUT_FILE, '/data', (ZZ-zmin)./(zmax-zmin), [last_idx,1,1,1], [size(ZZ),1]);
    %h5disp( OUT_FILE )

end

%%
fprintf('Generated dataset:\n');
h5disp( OUT_FILE );


