function dummy=cal2caacal_rjump;
% Converts a fgmcal format calibration file created at the range jump calibration step into caa named fgmcal file
% Modified 01/09/2010 LNA to check archive for final range jump calibration
% files if not found in current work directory.

% Load directory information
load config_cal

% Orbit selection
orbitSel=input('Enter orbit numbers which are to be considered in calibration analysis: (eg [93 98 99]) ');
firstorbit = orbitSel(1);
lastorbit = orbitSel(end);

version=input('Enter calibration file version number: ');

% Spacecraft selection
scSel=[1 2 3 4];

% Read in information from orbit timing information file
fprintf('Importing orbit data...\n');
fid_orbit_info=fopen('Orbit_info.txt','r');
[orbit_data,orbit_data_i]=fscanf(fid_orbit_info,'%4d %4d-%2d-%2dT%2d:%2d:%fZ %4d-%2d-%2dT%2d:%2d:%fZ %4s',[17 inf]);
orbit_data=orbit_data';

for orbit_i=1:length(orbitSel);
    orbit=orbitSel(orbit_i);
    
    % Loop through spacecraft
    for sc_i=1:length(scSel);
        sc=scSel(sc_i);
        
        % Check for existence of calibration file to be converted
        cal_in_name=['c',int2str(sc),'_cal_rj_final_corr_',int2str(orbit),'.fgmcal'];
        if exist([WORK_DIR,cal_in_name])
            fprintf('Loading calibration file for spacecraft %g orbit %g from current work directory\n',sc,orbit);
            cal_dir_file=[WORK_DIR,cal_in_name];
            cal_in_fid=fopen(cal_dir_file,'r');
            cal_in=fscanf(cal_in_fid,'%c');
            fclose(cal_in_fid);
        elseif exist([CAL_RESULTS_RJ,'Range jump_orbits_',int2str(firstorbit),'_',int2str(lastorbit),'\',cal_in_name])
            fprintf('Cannot find calibration file for spacecraft %g orbit %g in current work directory. Loading from archive\n',sc,orbit);
            cal_dir_file=[CAL_RESULTS_RJ,'Range jump_orbits_',int2str(firstorbit),'_',int2str(lastorbit),'\',cal_in_name];
            cal_in_fid=fopen(cal_dir_file,'r');
            cal_in=fscanf(cal_in_fid,'%c');
            fclose(cal_in_fid);
        else
            fprintf('No calibration file available for spacecraft %g orbit %g .  Skipping to next spacecraft.\n',sc,orbit);
            sc_i = sc_i + 1;
        end;
        % Check if calibration file is empty
%         if exist(cal_in_name) == 1
%         h_test=fopen(cal_in_name);
%         if h_test==-1
%             error(['Can''t open data file ',cal_in_name])
%         end
%         [d_test,c_test]=fscanf(h_test,'%s',[10 12]);
%         fclose(h_test);
% 	
%         if isempty(d_test)==1;
%             fprintf('The following data file is empty: %s',cal_in_name);
%         elseif isempty(d_test)==0;
%             
%             cal_in_fid=fopen(cal_in_name,'r');
%             cal_in=fscanf(cal_in_fid,'%c');
%             fclose(cal_in_fid);
        
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
            
            %Save cal file
            cal_out_fid=fopen(caa_cal_name,'w');
			
            fprintf(cal_out_fid,'%c',cal_in);
%         end; %end conditional parsing data file
%         end; % end conditional checking existence of calibration file
        
    end; % end loop over spacecraft
    
end; % end loop over orbits
fclose all