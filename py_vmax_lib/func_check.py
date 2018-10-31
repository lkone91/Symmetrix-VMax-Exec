# -*- coding: utf-8 -*-

#================================================================================#
# ------------------------------- IMPORT LIBRARY ------------------------------- #
#================================================================================#

#~~~~# PYTHON LIBRARY #~~~~#

from __future__ import division

#~~~~# LOCAL LIBRARY #~~~~#

from py_vmax_lib.func_global import *
from py_vmax_lib.func_retrieve import *

#==============================================================================#
# ------------------------------- MODULE START ------------------------------- #
#==============================================================================#

# @function_check
def opt_check(script_opts, argv):
    for opt in script_opts:
        if argv in opt['opt']:
            return opt
    return False

# @function_check
def opt_treat(opts_dic_lst):
        
    if len(sys.argv) == 1:
        mprint('Argument(s) Needed', 'arg_err')
        sys.exit(1)
    
    opt_arg = False
    
    for x, argv in enumerate(sys.argv[1:]):
        if not opt_arg:
            opt_info = opt_check(opts_dic_lst, argv)
            if opt_info and opt_info['arg']:
                
                try:
                    opt_arg = sys.argv[1:][x+1]
                except:
                    mprint('Option [{0}] Need Argument'.format(argv), 'arg_err')
                    sys.exit(1)
                    
                opt_ck = opt_check(opts_dic_lst, opt_arg)
                
                if opt_ck:
                    mprint('Option [{0}] Need Argument'.format(argv), 'arg_err')
                    sys.exit(1)
                else:
                    opt_info['actv'] = True
                    opt_info['args'] = opt_arg
                        
            elif opt_info and not opt_info['arg']:
                opt_info['actv'] = True
            else:
                mprint('Option [{0}] Not Recognize'.format(argv), 'arg_err')
                sys.exit(1)
        else:
            opt_arg = False
    
    return opts_dic_lst
  

def bay_ping(array_id, symcli_export, logger):
    
    accessible = False
    
    if symcli_export != 'Local':
        os.environ["SYMCLI_CONNECT"] = symcli_export
    
    cmd_pipe = subprocess.Popen(
       'symrdf -sid {0} ping'.format(array_id),
       stdout=subprocess.PIPE,
       stderr=subprocess.PIPE,
       shell=True
    )
    
    cmd_return = cmd_pipe.communicate()[1].split('\n')
    
    for c in cmd_return:
        if re.search('successfully pinged', c.lower()):
            accessible = True

    if not accessible:
        mprint('Bay with ID {0} not Accessible [Remote Symcli Server : {1}]'.format(array_id, symcli_export), 'err', logger=logger)
    
# @function_check
def exist_check(lst, all_lst, type=False, mode=False, exit=True, err_return=2, logger=False):
    
    not_exist_list = []
    exist_list = []
    all_lst_fmt = [a.lower() for a in all_lst]
    
    for l in lst:
        if l.lower() not in all_lst_fmt:
            not_exist_list.append(l)
        else:
            exist_list.append(l)
            
    if mode == 'N' and not_exist_list:
            mprint('{0} {1} Not Exist'.format(type, not_exist_list), 'err', logger=logger, exit=exit)
            return err_return
            
    elif mode == 'E' and not not_exist_list:
            mprint('{0} {1} Already Exist'.format(type, exist_list), 'err', logger=logger, exit=exit)
            return err_return
            
    else:
        if not_exist_list:
            return False
        else:
            return True
      
# # @function_check      
def check_lun_port(sid, lun_list):
    
    mprint('(-) Check Lun Port(s) ...', end='\r')
    
    lun_no_port_lst = [l['id'] for l in lun_lst_retrieve(sid, lun_type='noport', display=False)]
    
    lun_port_lst = list(set(lun_list).difference(set(lun_no_port_lst)))
    
    if lun_port_lst: 
        mprint('(-) Lun with Port(s) Connected : {0}'.format(','.join(lun_port_lst)), 'd1', tac=1)
        
        return lun_port_lst
        
    else:
        mprint('(-) No Lun with Port(s) Connected', 'd1', tac=1)
        
# # @function_check
def wait_free_unbind_lun(sid, lun_list, type, logger=False):
    """ Fonction : Attente de l'unbind des Luns """
    
    refresh_time = 45
    lun_free_unbind_lst = []
    func_start_time = time.time()
    
    d_display = '(-) ' + type.capitalize() + ' Lun(s) : [{0}/{1}]{2}'
    
    while len(lun_free_unbind_lst) != len(lun_list):
        
        progress = progressbar(len(lun_free_unbind_lst), len(lun_list), '[R:CMD]', msg_b='', sep=' ', display=False)
        mprint(d_display.format(str(len(lun_free_unbind_lst)).zfill(3), str(len(lun_list)).zfill(3), progress), end='\r')
        
        if type == 'unbind':
            lun_free_unbind_lst = lun_lst_retrieve(sid, lun_type='unbound', display=False, dev_lst=lun_list, logger=logger)
        else:
            lun_free_unbind_lst = lun_free_lst_retrieve(sid, lun_list, logger=logger)
        
        progress_wait(d_display, len(lun_free_unbind_lst), len(lun_list), refresh_time, func_start_time)
        
    
# # @function_check
def wait_vlun_migrate(sid, vlun_name, lun_cnt, export='Local'):
    
    refresh_time = 45
    lun_mig_lst = []
    func_start_time = time.time()
    
    d_display = '(-) Migrate Lun(s) : [{0}/{1}]{2}'
    
    while len(lun_mig_lst) != lun_cnt:
        
        progress = progressbar(len(lun_mig_lst), lun_cnt, '[R:CMD]', msg_b='', sep=' ', display=False)
        mprint(d_display.format(str(len(lun_mig_lst)).zfill(3), str(lun_cnt).zfill(3), progress), end='\r')
        
        lun_mig_lst = [l['src_dev_name'] for l in vlun_session_retrieve(sid, vlun_name, export=export) if l['state'] == 'Migrated']
        
        progress_wait(d_display, len(lun_mig_lst), lun_cnt, refresh_time, func_start_time)
    
# # @function_check
def login_syntax_check(wwn_lst):
    pattern = re.compile(r'^[1-5c]0[0-9a-f]{14}$')
    result = [w for w in wwn_lst if not re.match(pattern, w)]
    
    return result
        
# @function_check
def lun_with_srdf_check(lun_cls_lst):
    
    result = []
    r1_check = False
    r2_check = False
    
    for l in lun_cls_lst:
        if l.srdf:
            l.warning = True
            result.append(l.id)
            
            for s in l.srdf_list_info:
                if s['local_type'] == 'R1':
                    r1_check = True
                else:
                    r2_check = True
                
    return result, r1_check, r2_check
    
# @function_check
def gate_keep_check(lun_cls_lst):
    
    result = []
    
    for l in lun_cls_lst:
        if l.gkeeper:
            l.error = True
            result.append(l.id)
        
    return result

# @function_check
def array_id_check(array_dic_lst, sid='', mode=''):
    
    if not sid:
        mprint()
        sid = text_input('Enter {0}SID Array'.format(mode), type='{0}SID Array'.format(mode), out_type='choice', regex=False, lst=[a['id'] for a in array_dic_lst])
    
    check = 0
    
    for a in array_dic_lst:
        if a['id'][-len(sid):] == sid:
            check = 1
            array_type = a['type']
            array_id = a['id']
            one_view = a['one_view']
            export = a['export']
            
    if check is 0:
        mprint('{0}SID Array {1} not Find'.format(mode, sid), 'arg_err')
    
    sid = array_id[-4:]
    
    return sid, array_id, array_type, one_view, export

# @function_check
def lun_argument_check(sid, dev_arg, lun_type='', tit='Lun(s)', dic_lst=False, tbc=1, logger=False, export='Local'):
    
    if not dic_lst:
        lun_dic_lst = lun_lst_retrieve(sid, lun_type=lun_type, export=export)
        
    else:
        lun_dic_lst = dic_lst
        
    lun_all_lst = [l['id'] for l in lun_dic_lst]
    
    if dev_arg:
        check = 0
    else:
        check = 1
        if tbc: mprint()
    
    while True:
        
        lun_err = []
        lun_wwn_err = []
        lun_meta_memb = []
        
        if check is 1:
            if lun_type == 'wwn':
                dev_arg = text_input('Enter WWN {0}'.format(tit), type='WWN Lun', out_type='lst')
                
            else:
                dev_arg = text_input('Enter {0}'.format(tit), type='Lun', out_type='lst')
                
        
        if lun_type == 'wwn':
            dev_arg = [x.upper() for x in dev_arg]
        else:
            
            # Convertion des Ranges de Luns #
            
            dev_lst = []
            
            for x in dev_arg:
                if ':' in x:
                    dev_lst = dev_lst + dev_range_retrieve(x)
                else:
                    dev_lst.append(x.rjust(5, '0').upper())
                    
            dev_arg = dev_lst
            
        for l in dev_arg:
            
            if lun_type == 'wwn' and l not in [x['wwn_id'] for x in lun_dic_lst]:
                lun_wwn_err.append(l)
                
            elif not lun_type and l not in [x['id'] for x in lun_dic_lst]:
                lun_err.append(l)
                
            else:
                if lun_type == 'wwn':
                    lun_meta = [x['meta'] for x in lun_dic_lst if x['wwn_id'] == l][0]
                
                else:
                    lun_meta = [x['meta'] for x in lun_dic_lst if x['id'] == l][0]
                
                if lun_meta == 'Member':
                    lun_meta_memb.append(l)
                
        if lun_err:
            mprint('{0} Not Find [{1}]'.format(tit, ','.join(lun_err)), 'err', logger=logger, exit=False, tac=1)
            check = 1
            continue
            
        elif lun_wwn_err:
            mprint('UID {0} Not Find [{1}]'.format(tit, ','.join(lun_wwn_err)), 'err', logger=logger, exit=False, tac=1)    
            check = 1    
            continue
            
        elif lun_meta_memb:
            mprint('Meta Member Detected [{0}] '.format(','.join(lun_meta_memb)), 'err', logger=logger, exit=False, tac=1)
            check = 1
            continue
            
        else:
            break
    
    dev_id_lst = []
    
    if lun_type == 'wwn':
        for x in lun_dic_lst:
            if x['wwn_id'] in dev_arg:
                dev_id_lst.append(x['id']) 
            
        dev_arg = dev_id_lst
        
    if check is 1:
        mprint()
    
    if dic_lst:
        return dev_arg
    else:
        return dev_arg, lun_all_lst
    
# @function_check
def sgroup_argument_check(sid, sg_arg, sg_type='S.Group', logger=False, export='Local'):
    
    sg_all_lst, ig_all_lst = sg_ig_lst_retrieve(sid, export=export)
    
    if sg_arg:
        check = 0
    else:
        check = 1
        mprint()
    
    while True:
        
        sg_err = []
        
        if check is 1:
            sg_arg = [text_input('Enter {0}'.format(sg_type), type='S.Group', out_type='choice', lst=sorted(sg_all_lst))]
        
        for s in sg_arg:
            if s not in sg_all_lst:
                sg_err.append(s)
        
        if sg_err:
            mprint('{0} {1} Not Find'.format(sg_type, sg_err), 'err', logger=logger, exit=False, tac=1)
            check = 1
            continue
            
        else:
            break
            
    if check is 1:
        mprint()
    
    return sg_arg, sg_all_lst, ig_all_lst
    
# @function_check
def login_argument_check(sid, login_arg, login_type='Login(s)', logger=False, export='Local'):
    
    login_lst = [l['login'] for l in login_lst_retrieve(sid, export=export)]
    
    if login_arg:
        check = 0
    else:
        check = 1
        mprint()
    
    while True:
        
        login_err = []
        
        if check is 1:
            login_arg = text_input('Enter {0}'.format(login_type), type='Login', out_type='lst')
        
        login_arg = [w.replace(':', '').lower() for w in login_arg]
        
        for w in login_arg:
            if w not in login_lst:
                login_err.append(w)
                
        if login_err:
            mprint('{0} {1} Not Find'.format(login_type, login_err), 'err', logger=logger, exit=False, tac=1)
            check = 1
            continue
            
        else:
            break
            
    if check is 1:
        mprint()
    
    return login_arg, login_lst
    
# @function_check
def new_sgroup_argument_check(sid, new_name_arg, node, one_view, sg_type='', no_break=False, logger=False, export='Local'):
    
    sg_all_lst, ig_all_lst = sg_ig_lst_retrieve(sid, export=export)
    
    if new_name_arg:
        check = 0
    else:
        check = 1
        mprint()
    
    while True:
        
        if check is 1:
            
            server_type = 'Server'
            
            if node is not 1:
                server_type = 'Cluster'
                
            server_type = '{0}{1}'.format(sg_type, server_type)
            
            new_name_arg = text_input('Enter {0} New Name'.format(server_type))
            
        if re.search('(_sg|sg_)', new_name_arg.lower()):
            mprint('[{0}] Bad Name Syntax. Please enter Only Server Name [Ex: parva784589|parva784589-90]'.format(new_name_arg), 'err', tac=1, logger=logger, exit=False)
            check = 1
            continue
            
        else:
            
            if not no_break:
                new_name_arg = new_name_arg.lower()
            
            if one_view:
                nsg_name = ['SG_{0}'.format(new_name_arg)]
                
            else:
                nsg_name = ['{0}_SG'.format(new_name_arg)]
            
            sg_check = exist_check(nsg_name, sg_all_lst, 'S.Group', mode = 'E', logger=logger, exit=False)
            
            if sg_check is not 2:
                sgroup = ','.join(nsg_name)
                if logger:
                    logger.info('[NEW:SG] {0}'.format(sgroup))
                break
                
            else:
                mprint()
                check = 1
                continue
                
    if check is 1:
        mprint()
        
    return sgroup, new_name_arg, sg_all_lst, ig_all_lst
    
    
def generate_ig_mv_login(wwn_dic_lst, nview_dic_lst, login_cls_lst, node, new_name, only_one_fab, one_view):
    
    odd_count = 0
    even_count = 0
    
    for wwn_dic in wwn_dic_lst:
        
        # Genération des IG/MV #
        
        wwn_dic['port'] = rtr_dict_list(login_cls_lst, 'port_enable_dir_prt_list', uniq=True, concat=True, filter='wwn:{0}'.format(wwn_dic['name']))    
        wwn_dic['port_logged'] = rtr_dict_list(login_cls_lst, 'port_logged_dir_prt_list', uniq=True, concat=True, filter='wwn:{0}'.format(wwn_dic['name']))    
            
        if only_one_fab:
            
            for p in wwn_dic['port']:
                
                if int(p.split('-')[1].split(':')[0].replace('F', '')) % 2 == 0:    
                    wwn_dic['type'] = 'P'
                    
                else:    
                    wwn_dic['type'] = 'I'    
            
        for nview_dic in nview_dic_lst:    
                
            if wwn_dic['name'] in nview_dic['wwn_list']:    
                wwn_dic['server_name'] = nview_dic['name']
                
                if node > 1:
                    wwn_dic['cluster_name'] = new_name
                
                if one_view:
                    wwn_dic['ig_name'] = 'IG_{0}'.format(nview_dic['name'])
                    wwn_dic['mv_name'] = 'MV_{0}'.format(new_name)
                    
                    if node > 1:
                        wwn_dic['cig_name'] = 'CIG_{0}'.format(new_name)
                        
                else:
                    wwn_dic['ig_name'] = '{0}_{1}_IG'.format(nview_dic['name'], wwn_dic['type'])
                    wwn_dic['mv_name'] = '{0}_{1}_MV'.format(new_name, wwn_dic['type'])
                    
                    if node > 1:
                        wwn_dic['cig_name'] = '{0}_{1}_CIG'.format(new_name, wwn_dic['type'])
                    
                if wwn_dic['exist_ig_name']:
                    wwn_dic['ig_name'] = wwn_dic['exist_ig_name']
                 
        # Genération de l'enregistrement des Logins #
                    
        npiv = ''            
                    
        if re.search(r'^c0', wwn_dic['name']):
            npiv = 'npiv_'
        
        if wwn_dic['type'] == 'P':
            
            even_type = '{0}even'.format(npiv)
            even_count_fmt = str(even_count)
            
            if even_count_fmt == '0':
                even_count_fmt = ''  
                
            wwn_dic['port_name'] = '{0}{1}'.format(even_type, even_count_fmt)
            
            even_count += 1
            
        elif wwn_dic['type'] == 'I':
            odd_type = '{0}odd'.format(npiv)
            odd_count_fmt = str(odd_count)
            
            if odd_count_fmt == '0':
                odd_count_fmt = ''
                
            wwn_dic['port_name'] = '{0}{1}'.format(odd_type, odd_count_fmt)
            
            odd_count += 1
            
            
            