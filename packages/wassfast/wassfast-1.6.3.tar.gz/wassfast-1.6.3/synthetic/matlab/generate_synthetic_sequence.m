%%
clc; clear; close all;
initwafo

OUT_FILE = '/media/fibe/FIO_2018/synth/synth_sequence.h5';

%%

%Hm0 = 6; 
%Tp = 8;
%th0 = -pi/2;
Hm0 = 5.5; 
Tp = 7.5;
th0 = -pi/2-0.1;
Sp = 15.02;
Nu = 256; 
du = 0.46; 
fps = 7.0;
Nt = fps * 60 * 5; 

[W,S] = wafo_generate_sequence( Hm0, Tp, th0, Sp, Nu, Nu, du, du, Nt, fps );
close all;

%%
delete(OUT_FILE);
scn=0;
dataset = sprintf('/%04d/',scn);
h5create( OUT_FILE, [dataset,'fps'], [ 1 ], 'Datatype', 'single' );
h5create( OUT_FILE, [dataset,'dt'], [ 1 ], 'Datatype', 'single' );
h5create( OUT_FILE, [dataset,'ZminZmax'], [ 2 ], 'Datatype', 'single' );
h5create( OUT_FILE, [dataset,'waveangle'], [ 1 ], 'Datatype', 'single' );
h5disp( OUT_FILE )


h5writepermuted(OUT_FILE, [dataset,'fps'], [fps]);
h5writepermuted(OUT_FILE, [dataset,'dt'], [1.0/fps]);
   
ZZ = single( permute( W.Z, [3,1,2]) );

zmin = min(min(min(ZZ)));
zmax = max(max(max(ZZ)));
    
h5writepermuted(OUT_FILE, [dataset,'ZminZmax'], [zmin, zmax]);
    

h5create( OUT_FILE, [dataset,'data'], [ Nu, Nu, size(ZZ,1) ], 'Chunksize', [Nu,Nu,8], 'Datatype', 'single' );
h5writepermuted(OUT_FILE, [dataset,'data'], ZZ );
    
h5disp( OUT_FILE )

%%


for ii=1:3
    f = figure;
    imagesc(  W.Z(:,:,ii) );
    caxis( [-Hm0 Hm0] );
    axis equal;
    colorbar;
    title( sprintf('%06d',ii) );
    drawnow;
    saveas( f, sprintf('fig/%06d.png',ii ) );
    close all;
end

%%