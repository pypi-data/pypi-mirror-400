function  h5writepermuted( filename,dataset,data )
% Writes h5 datasets in C style row-major format

ndim = numel(size(data));
pdata = permute(data,[ndim:-1:1]);

h5write(filename,dataset,pdata);

end

