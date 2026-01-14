function oufile=filone2netcdf_02_create_v2(oufile, Xp, Yp)
% xyz in mm
%  FUNCTION (oufile, Lp, Mp, )
%
%    Create an empty netcdf for stereo data.
%
%    Arguments:
%          oufile = name of the nc file
%          Xp     = number of  points in X direction
%          Yp     = number of  points in Y direction

%


% --------------------------------------------------------------------
%  Create  NetCDF
% --------------------------------------------------------------------
% nc_create_empty(oufile,'netcdf4-classic')
nc_create_empty(oufile)
% --------------------------------------------------------------------
%  Add dimensions
% --------------------------------------------------------------------

nc_add_dimension(oufile,'X',Xp)
nc_add_dimension(oufile,'Y',Yp)
nc_add_dimension(oufile,'pointdim',3)
nc_add_dimension(oufile,'count',0)
nc_add_dimension(oufile,'dummy',1)
% --------------------------------------------------------------------
%  Add variable --> count
% --------------------------------------------------------------------
varstruct.Name = 'count';
varstruct.Nctype = 'double';
varstruct.Dimension = {'count'};
nc_addvar(oufile,varstruct)
nc_attput(oufile,'count','long_name','count')
nc_attput(oufile,'count','units','steps')
nc_attput(oufile,'count','field','time, scalar, series')
clear varstruct

% --------------------------------------------------------------------
%  Add variable --> time
% --------------------------------------------------------------------
varstruct.Name = 'time';
varstruct.Nctype = 'double';
varstruct.Dimension = {'count','dummy'};
nc_addvar(oufile,varstruct)
nc_attput(oufile,'time','long_name','time')
nc_attput(oufile,'time','units','seconds')
nc_attput(oufile,'time','field','time, scalar, series')
clear varstruct

%------------------------------------------------------------
% Add variable --> X_grid
% ------------------------------------------------------------
varstruct.Name = 'X_grid';
varstruct.Nctype = 'double';
varstruct.Dimension = {'X','Y'};
nc_addvar(oufile,varstruct)
nc_attput(oufile,'X_grid','long_name','X axis grid')
nc_attput(oufile,'X_grid','units','millimeter')
nc_attput(oufile,'X_grid','field','X_grid, scalar, series')
clear varstruct

%------------------------------------------------------------
% Add variable --> Y_grid
% ------------------------------------------------------------
varstruct.Name = 'Y_grid';
varstruct.Nctype = 'double';
varstruct.Dimension = {'X','Y'};
nc_addvar(oufile,varstruct)
nc_attput(oufile,'Y_grid','long_name','Y axis grid')
nc_attput(oufile,'Y_grid','units','millimeter')
nc_attput(oufile,'Y_grid','field','Y_grid, scalar, series')

%------------------------------------------------------------
% Add variable --> MASK Z
% ------------------------------------------------------------
varstruct.Name = 'mask_Z';
varstruct.Nctype = 'double';
varstruct.Dimension = {'X','Y'};
nc_addvar(oufile,varstruct)
nc_attput(oufile,'mask_Z','long_name','mask')
nc_attput(oufile,'mask_Z','units','0 and 1')
nc_attput(oufile,'mask_Z','field','mask_Z, scalar, series')

%------------------------------------------------------------
% Add variable --> Z
% ------------------------------------------------------------
varstruct.Name = 'Z';
varstruct.Nctype = 'int16';
varstruct.Dimension = {'count','X','Y'};
% varstruct.Deflate = 0;
varstruct.Attribute.Name = '_FillValue';
varstruct.Attribute.Value = NaN;
% varstruct.Attribute.Name = 'scale_factor';
% varstruct.Attribute.Value = 1/1000;
nc_addvar(oufile,varstruct)
nc_attput(oufile,'Z','long_name','Z data on time over the XY grid')
nc_attput(oufile,'Z','units','millimeter')
nc_attput(oufile,'Z','field','Z, scalar, series')

%------------------------------------------------------------
% Add variable --> fps
% ------------------------------------------------------------
varstruct.Name = 'fps';
varstruct.Nctype = 'double';
varstruct.Dimension = {'dummy'};
nc_addvar(oufile,varstruct)
nc_attput(oufile,'fps','long_name','frame rate')
nc_attput(oufile,'fps','units','Hz')

%------------------------------------------------------------
% Add variable --> date
% ------------------------------------------------------------
varstruct.Name = 'datenum';
varstruct.Nctype = 'double';
varstruct.Dimension = {'dummy'};
nc_addvar(oufile,varstruct)
nc_attput(oufile,'datenum','long_name','Init acq date since 00/00/00 00:00:00 UTC')
nc_attput(oufile,'datenum','units','seconds')

%------------------------------------------------------------
% Add variable --> dxy
% ------------------------------------------------------------
varstruct.Name = 'dxy';
varstruct.Nctype = 'double';
varstruct.Dimension = {'dummy'};
nc_addvar(oufile,varstruct)
nc_attput(oufile,'dxy','long_name','grid size')
nc_attput(oufile,'dxy','units','mm')

%------------------------------------------------------------
% Add variable --> scale
% ------------------------------------------------------------
varstruct.Name = 'scale';
varstruct.Nctype = 'double';
varstruct.Dimension = {'dummy'};
nc_addvar(oufile,varstruct)
nc_attput(oufile,'scale','long_name','Stereo baseline')
nc_attput(oufile,'scale','units','m')

%%
% --------------------------------------------------------------------
%  Add global attributes
% --------------------------------------------------------------------
nc_attput(oufile,nc_global,'type','WASS file')
nc_attput(oufile,nc_global,'title',oufile)
nc_attput(oufile,nc_global,'source','WASS')
