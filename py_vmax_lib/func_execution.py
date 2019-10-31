# -*- coding: utf-8 -*-
#
#================================================================================#
# ------------------------------- IMPORT LIBRARY ------------------------------- #
#================================================================================#

#~~~~# LOCAL LIBRARY #~~~~#

from py_vmax_lib.func_global import *

#==============================================================================#
# ------------------------------- MODULE START ------------------------------- #
#==============================================================================#

# @function_check
def cmd_exec(cmd, mode='X', display='', cmd_pass=False, logger=False, tmp_file=False, export='Local'):  
    """ Fonction pour l'exution des commandes """
    
    if export != 'Local':
        os.environ["SYMCLI_CONNECT"] = export
    
    retry_time = 60
    retry_max_count = 10
    
    retry_count = 0
    
    while True:
        
        if logger:
            logger.info('[CMD:{0}|{1}] {2}'.format(mode, export, cmd))
        
        cmd_pipe = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
        if display:
            command = display
        elif display == 'no':
            command = ''
        else:
            command = mprint(cmd, 'd1', print_return=False)
        
        if mode == 'X':
            rows, columns = rows_colums_retrieve()
            
            col_limit = int(columns)-15
            
            if len(command) > col_limit:
                cmd_display = '{0}..'.format(command[:col_limit])
            else:
                cmd_display = command
            
            while cmd_pipe.poll() == None:
                cmd_wait(cmd_display)
        
        output, err = cmd_pipe.communicate()
        
        if cmd_pipe.wait() != 0:
            
            if cmd_pass:    
                return 1
            else:
                
                already = 0
                bind_err = 0
                
                # Check return command #
                
                output_return = [o for o in output.decode("utf-8").split('\n') if o != '']
                error_return = [e for e in err.decode("utf-8").split('\n') if e != '']
                
                return_cmd = output_return + error_return 
                
                for rtr in return_cmd:
                    
                    # Command Lock Check #
                    
                    if 'locked by another process' in rtr or 'exclusive lock on the local Symmetrix' in rtr:
                        
                        if retry_count <= retry_max_count:
                            
                            if logger:
                                logger.error('{0} [LOCKED!][RETRY:{1}][TIME:{2}s]'.format(cmd, retry_count, retry_time))
                                
                            r_count = int(retry_time)
                            
                            while r_count is not 0:
                                mprint("{0} [Lock!][R{1}:T{2}]".format(cmd_display, str(retry_count).zfill(2), str(r_count).zfill(2)), end='\r')
                                r_count -= 1
                                time.sleep(1)
                                
                            mprint("{0} [Lock!][R{1}:T{2}][Retry]".format(command, str(retry_count).zfill(2), str(r_count).zfill(2)))
                            retry_count += 1
                            break
                            
                        else:
                            if logger:
                                logger.error('{0} [CMD FAIL!][RETRY FAIL AFTER {1} TIMES]'.format(cmd, retry_max_count))
                                
                            mprint("{0} [cmd fail!][Retry Fail After {1} times!]".format(command, retry_max_count), tac=1)
                            
                            if tmp_file:
                                remove_file(tmp_file)
                                
                            sc_exit(1, logger=logger)
                    
                    # Device Already Unbind or Free Check #
                    
                    if re.search('unbind|free|ready', cmd):
                        
                        if 'The device is already in the requested state' in rtr:
                            
                            if logger:
                                logger.warning('{0} [CMD PASS][ALREADY IN THE REQUESTED STATE]'.format(cmd))
                                
                            mprint("{0} [cmd pass][Already in the Requested State]".format(command), tac=1)
                            already = 1
                            break
                        
                    # Commit Binding Problem #
                        
                    if 'commit' in cmd and "Bind failed can't match new devices" in rtr:
                        
                        if logger:
                            logger.warning('{0} [BINDING ERROR WITH COMMIT]'.format(cmd))
                    
                        mprint("{0} [Bind Error]".format(command), tac=1)
                        bind_err = 1
                        break
                        
                if retry_count is not 0:
                    continue
                
                if already is 1:
                    break
                    
                if bind_err is 1:
                    return 2
                    
                # Command Fail #
                
                if logger:
                    logger.error('{0} [CMD FAIL!]'.format(cmd))
                    logger.error('CMD RETURN [OUT.ERR] : ' + re.sub(r'\.\.+', ':', ','.join(output_return)))
                    logger.error('CMD RETURN [OUT.STD] : ' + re.sub(r'\.\.+', ':', ','.join(error_return)))
                    
                mprint("{0} [cmd fail!]".format(command), tac=1)
                
                if tmp_file:
                    remove_file(tmp_file)
                    
                sc_exit(1, logger=logger)
                
        else:
            
            # Command OK #
            if mode != 'A':
                if not display:
                    mprint("{0} [cmd OK]".format(command))
            
            result = output.decode("utf-8")
            
            if tmp_file and not re.search('prepare|precopy|validate', cmd):
                remove_file(tmp_file)
            
            return result

# @function_check
def cmd_retrieve(cmd, c, t, type='xml', msg_b ='[I]', display=True, logger=False, export='Local'):
    """ 
    Fonction : 
    Execution des commandes d'informations [XML ou Stantard] 
    Retour avec l'output au format standard ou XML
    """
    
    if display:
        progressbar(c, t, 'cmd({0})'.format(cmd.split()[0]), msg_b=msg_b)
        command = cmd_exec(cmd, 'R', progressbar(c, t, 'cmd({0})'.format(cmd.split()[0]), msg_b=msg_b, display=False), cmd_pass=True, logger=logger, export=export)
    
    else:
        command = cmd_exec(cmd, 'R', display='no', cmd_pass=True, logger=logger, export=export)
    
    if command != 1:
        if type == 'xml':
            result = xmltree.fromstring(command)
        else:
            result = command
        
        return result
        
    else:
        return 1

# @function_check
def cmd_exec_mode(cmd_list, title='', mode='display', logger=False, tmp_file=False, cmd_sort=True, export='Local'):
    if cmd_list:
        
        if cmd_sort:
            cmd_list = list(set(sorted(cmd_list)))
        
        if title:
            mprint(title, 't3')
        for cmd in cmd_list:
            if mode == 'display':
                mprint(cmd)
            elif mode == 'exec':
                cmd_exec(cmd, logger=logger, tmp_file=tmp_file, export=export)
        mprint()

# @function_check                    
def symconf_exec(cmd_list, title, mode, file_t, sid, tmp_file, verbose=False, logger=False, export='Local'):
    if cmd_list:
        if title:
            mprint(title, 't3')
            
        write_file(cmd_list, tmp_file, mode, 'Create File With {0}'.format(file_t), logger, verbose)
        
        m_list = ['prepare', 'commit']
        
        if re.search(r'^(0716|0923)$', sid):
            m_list.remove('prepare')
            
        for m in m_list:
            if mode == 'display':
                mprint('symconfigure -sid {0} -f {1} {2} -nop'.format(sid, tmp_file, m))
                
            elif mode == 'exec':
                
                try:
                    return_cmd_lst = cmd_exec('symconfigure -sid {0} -f {1} {2} -nop'.format(sid, tmp_file, m), logger=logger, tmp_file=tmp_file, export=export).split('\n')
                except AttributeError:
                    return_cmd_lst = 2
                    
                # Recuperation des Nouveaux Luns crees dans un dict #
                
                if 'Create Lun' in title:
                    
                    if return_cmd_lst is not 2:
                    
                        new_device_dic_lst = []
                        
                        for return_cmd in return_cmd_lst:
                            
                            new_device_dic = {}
                            
                            if re.search(r'New symdevs?', return_cmd):
                                
                                if re.search(r'\[TDEV\]', return_cmd):
                                    new_device_dic['type'] = 'dev'
                                    new_device_dic['dev_list'] = [re.split('\W+', return_cmd)[3]]
                                    
                                elif re.search(r'\[TDEVs\]', return_cmd):
                                    new_device_dic['type'] = 'range'
                                    new_device_dic['dev_range'] = re.search(r'\w+:\w+', return_cmd).group(0)
                                    new_device_dic['dev_list'] = dev_range_retrieve(new_device_dic['dev_range'])
                                    
                                elif re.search(r'Thin Striped meta', return_cmd):
                                    new_device_dic['type'] = 'meta'
                                    new_device_dic['meta_range'] = re.search(r'\w+:\w+', return_cmd).group(0)
                                    new_device_dic['dev_list'] = [re.search(r'(?<=head.)\w+', return_cmd).group(0)]
                                    new_device_dic['meta_size'] = re.search(r'(?<=member_size.)\w+', return_cmd).group(0)
                                    
                                new_device_dic_lst.append(new_device_dic)
                        
                        lun_lst = rtr_dict_list(new_device_dic_lst, 'dev_list', uniq=True, concat=True, mode_cls=False)
                        
                        if logger:
                            logger.info('[{0}] New Device(s) : {1}'.format(m, lun_lst))
                        
                        if m == 'commit':
                            mprint()
                            return (True, lun_lst)
                        else:
                            lun_prepare_lst = list(lun_lst)
                            
                    else:
                        return (False, lun_prepare_lst)
                        
        mprint()

# @function_check
def remove_srdf_pair(dic_lst, mode, sid, tmp_file, verbose=False, logger=False, export='Local'):
    if dic_lst:
        mprint('Remove SRDF Pair', 't3')
        ra_lst = set(dic['ra_group_num'] for dic in dic_lst)
        
        for ra in ra_lst:
            type_lst = set(dic['local_type'] for dic in dic_lst if dic['ra_group_num'] == ra)
            
            for type in type_lst:
                state_lst = set(dic['pair_state'] for dic in dic_lst if dic['ra_group_num'] == ra and dic['local_type'] == type)
                
                for state in state_lst:
                    
                    if state == 'Synchronized':
                        device_list = ['{0} {1}'.format(dic['local_dev_name'], dic['remote_dev_name']) for dic in dic_lst if dic['ra_group_num'] == ra and dic['local_type'] == type and dic['pair_state'] == state]
                        write_file(device_list, tmp_file, mode, 'Create File With Pair(s) to Split [{0}, {1}, {2}]'.format(ra, type, synchro_type_case(state)), logger, verbose)
                        
                        cmd_exec_mode(['symrdf -sid {0} -f {1} -rdfg {2} split -force -nop'.format(sid, tmp_file, ra)], mode=mode, logger=logger, tmp_file=tmp_file, export=export)
                    
                    elif re.search('ActiveBias|ActiveActive', state):
                        device_list = ['{0} {1}'.format(dic['local_dev_name'], dic['remote_dev_name']) for dic in dic_lst if dic['ra_group_num'] == ra and dic['local_type'] == type and dic['pair_state'] == state]
                        write_file(device_list, tmp_file, mode, 'Create File With Pair(s) to Suspend [{0}, {1}, {2}]'.format(ra, type, synchro_type_case(state)), logger, verbose)
                        
                        cmd_exec_mode(['symrdf -sid {0} -f {1} -rdfg {2} suspend -force -nop'.format(sid, tmp_file, ra)], mode=mode, logger=logger, tmp_file=tmp_file, export=export)
                        
                device_list = ['{0} {1}'.format(dic['local_dev_name'], dic['remote_dev_name']) for dic in dic_lst if dic['ra_group_num'] == ra and dic['local_type'] == type]
                write_file(device_list, tmp_file, mode, 'Create File With Pair(s) to Delete [{0}, {1}, {2}]'.format(ra, type, synchro_type_case(state)), logger, verbose)
                
                cmd_exec_mode(['symrdf -sid {0} -f {1} -rdfg {2} deletepair -force -nop'.format(sid, tmp_file, ra)], mode=mode, logger=logger, tmp_file=tmp_file, export=export)
                    
             
# @function_check
def remove_clone_pair(dic_lst, mode, sid, tmp_file, verbose=False, logger=False, export='Local'):
    
    if dic_lst:
        mprint('Remove Clone Pair', 't3')
        clone_cnt = int(max(set(dic['clone_count'] for dic in dic_lst)))
        
        for c in range(clone_cnt):
            type_lst = set(dic['type'] for dic in dic_lst if dic['clone_count'] is c+1)
            
            for type in type_lst:
                
                device_list = ['{0} {1}'.format(dic['source_dev_name'], dic['target_dev_name']) for dic in dic_lst if dic['clone_count'] is c+1 and dic['type'] == type]
                write_file(device_list, tmp_file, mode, 'Create File With Pair(s) to Terminated [{0}, {1}]'.format(c+1, type), logger, verbose)
                
                cmd_exec_mode(['symclone -sid {0} -f {1} terminate -force -nop'.format(sid, tmp_file)], mode=mode, logger=logger, tmp_file=tmp_file, export=export)
    
# @function_check
def remove_bcv_pair(dic_lst, mode, sid, tmp_file, verbose=False, logger=False, export='Local'):
    
    if dic_lst:
        mprint('Remove BCV Pair', 't3')
        bcv_cnt = int(max(set(dic['bcv_count'] for dic in dic_lst)))
        
        for c in range(bcv_cnt):
            type_lst = set(dic['type'] for dic in dic_lst if dic['bcv_count'] is c+1)  
            
            for type in type_lst:
                state_lst = set(dic['state'] for dic in dic_lst if dic['bcv_count'] is c+1 and dic['type'] == type)
                
                for state in state_lst:
                    
                    if state == 'Synchronized':
                        device_list = ['{0} {1}'.format(dic['source_dev_name'], dic['target_dev_name']) for dic in dic_lst if dic['bcv_count'] is c+1 and dic['type'] == type and dic['state'] == state]
                        write_file(device_list, tmp_file, mode, 'Create File With Pai(s) to Splited [{0}, {1}, {2}]'.format(c+1, type, synchro_type_case(state)), logger, verbose)
                        
                        cmd_exec_mode(['symmir -sid {0} -f {1} split -nop'.format(sid, tmp_file)], mode=mode, logger=logger, tmp_file=tmp_file, export=export)
                    
                    device_list = ['{0} {1}'.format(dic['source_dev_name'], dic['target_dev_name']) for dic in dic_lst if dic['bcv_count'] is c+1 and dic['type'] == type]
                    write_file(device_list, tmp_file, mode, 'Create File With Pair(s) to Deleted [{0}, {1}, {2}]'.format(c+1, type, synchro_type_case(state)), logger, verbose)
                    
                    cmd_exec_mode(['symmir -sid {0} -f {1} cancel -nop'.format(sid, tmp_file)], mode=mode, logger=logger, tmp_file=tmp_file, export=export)

# @function_check
def remove_or_pair(dic_lst, mode, sid, array_id, tmp_file, verbose=False, logger=False, export='Local'):
    if dic_lst:
        mprint('Remove Open Rep. Pair', 't3')
        
        session_lst = set(dic['session_name'] for dic in dic_lst)
        
        for session in session_lst:
            device_list = ['symdev={0}:{1} wwn={2}'.format(array_id, dic['local_dev'], dic['remote_wwn']) for dic in dic_lst if dic['session_name'] == session]
            
            write_file(device_list, tmp_file, mode, 'Create File With Pair(s) to Terminate [S:{0}]'.format(session), logger, verbose)
            
            cmd_exec_mode(['symrcopy -sid {0} -f {1} terminate -force -nop'.format(sid, tmp_file)], mode=mode, logger=logger, tmp_file=tmp_file, export=export)
             
# @function_check
def create_srdf_pair(dev_lst, mode, sid, tmp_file, rmt_sid, ra_group, rdf_mode='acp_disk', rdf_type='rdf1', verbose=False, logger=False, export='Local'):
    
    if dev_lst:
        mprint('[Local] Create SRDF Replication', 't3')
        
        write_file(dev_lst, tmp_file, mode, 'Create File With Lun to Paired [RA:{0}, {1}(L):{2}(R)]'.format(ra_group, sid, rmt_sid), logger, verbose)
        
        cmd_exec_mode(['symrdf -sid {0} -f {1} -rdfg {2} createpair -establish -type {3} -rdf_mode {4} -nop'.format(sid, tmp_file, ra_group, rdf_type, rdf_mode)], mode=mode, logger=logger, tmp_file=tmp_file, export=export)
    
# @function_check
def create_clone_pair(dev_lst, mode, sid, tmp_file, verbose=False, logger=False, export='Local'):
    
    if dev_lst:
        mprint('[Local] Create Clone Replication', 't3')
        
        write_file(dev_lst, tmp_file, mode, 'Create File With Lun to Paired [Dev:{0}]'.format(len(dev_lst)), logger, verbose)
        
        cmd_exec_mode([
            'symclone -sid {0} -f {1} create -precopy -differential -nop'.format(sid, tmp_file),
            'symclone -sid {0} -f {1} activate -nop'.format(sid, tmp_file),
        ], mode=mode, logger=logger, tmp_file=tmp_file, cmd_sort=False, export=export)
        
        
# @function_check
def create_vlun_migrate_pair(dev_lst, mode, sid, pool_name, vlun_session_name, tmp_file, verbose=False, logger=False, export='Local'):
    
    if dev_lst:
        mprint('Create VLUN Migration', 't3')
        
        write_file(dev_lst, tmp_file, mode, 'Create File With Lun to Migrated [Dev:{0}]'.format(len(dev_lst)), logger, verbose)
        
        cmd_exec_mode([
            'symmigrate -sid {0} -f {1} -tgt_pool -pool {2} -name {3} validate -nop'.format(sid, tmp_file, pool_name, vlun_session_name),
            'symmigrate -sid {0} -f {1} -tgt_pool -pool {2} -name {3} establish -nop'.format(sid, tmp_file, pool_name, vlun_session_name)
        ], mode=mode, logger=logger, tmp_file=tmp_file, cmd_sort=False, export=export)
        
    