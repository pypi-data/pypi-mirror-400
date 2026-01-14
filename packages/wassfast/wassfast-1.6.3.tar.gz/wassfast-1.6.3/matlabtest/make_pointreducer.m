mex pointreducer.cpp

% OCVRoot = '/usr/local/Cellar/opencv3/3.2.0/';
% IPath = ['-I',fullfile(OCVRoot,'include')];
% LPath = fullfile(OCVRoot, 'lib');
% lib1 = fullfile(LPath,'libopencv_core.dylib');
% lib2 = fullfile(LPath,'libopencv_highgui.dylib');
% lib3 = fullfile(LPath,'libopencv_imgcodecs.dylib');
% mex('pointreducer.cpp', IPath, lib1,lib2,lib3);

%%
% test

close all;
pts = rand(2,5500)*2 - 1;
scatter( pts(1,:), pts(2,:),'.k' );
axis equal;
axis([-0.7,0.7,-0.7,0.7]);

kpt = pointreducer( pts, 0.025);

hold on;
scatter( pts(1,kpt), pts(2,kpt),'or' );
