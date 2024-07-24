function dummy=cal2caacal_Kepko;
% Converts a matlab format calibration file created at te Kepko calibration step into caa named fgmcal file

% Load calibration file to be converted
cal_in=input('Enter the name of the calibration file to be converted to caa cal file: (.mat)','s');
load(cal_in);

sc=cal_matrix.sc;

orbit=input('Enter the orbit number the calibration file is for: ');

version=input('Enter calibration file version number: ');

% Read in information from orbit timing information file
fprintf('Importing orbit data...\n');
fid_orbit_info=fopen('Orbit_info.txt','r');
[orbit_data,orbit_data_i]=fscanf(fid_orbit_info,'%4d %4d-%2d-%2dT%2d:%2d:%fZ %4d-%2d-%2dT%2d:%2d:%fZ %4s',[17 inf]);
orbit_data=orbit_data';

orbit_num_index=find(orbit==orbit_data(:,1));
startyear=orbit_data(orbit_num_index,2);
startmonth=orbit_data(orbit_num_index,3);
startday=orbit_data(orbit_num_index,4);
starthour=orbit_data(orbit_num_index,5);
startmin=orbit_data(orbit_num_index,6);
startsec=orbit_data(orbit_num_index,7);
endyear=orbit_data(orbit_num_index,8);
endmonth=orbit_data(orbit_num_index,9);
endday=orbit_data(orbit_num_index,10);
endhour=orbit_data(orbit_num_index,11);
endmin=orbit_data(orbit_num_index,12);
endsec=orbit_data(orbit_num_index,13);

%Build caa filename
caa_cal_name=sprintf('C%1.0d_CC_FGM_CALF__%04d%02d%02d_%02d%02d%02d_%04d%02d%02d_%02d%02d%02d_V%02d.fgmcal',sc,startyear,startmonth,startday,starthour,startmin,startsec,endyear,endmonth,endday,endhour,endmin,endsec,version);

% fgmcal format
StartTime=[];
EndTime=[];
range_ints_file_save=[];
cal_write_v8arch(caa_cal_name,cal_matrix,StartTime,EndTime,range_ints_file_save);