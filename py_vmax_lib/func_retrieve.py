# -*- coding: utf-8 -*-

#================================================================================#
# ------------------------------- IMPORT LIBRARY ------------------------------- #
#================================================================================#

#~~~~# LOCAL LIBRARY #~~~~#

from py_vmax_lib.func_global import *
from py_vmax_lib.func_execution import *
from py_vmax_lib.class_device import *

#==============================================================================#
# ------------------------------- MODULE START ------------------------------- #
#==============================================================================#


# @function_check
def silo_info_retrieve(pool_cls_lst, fast_cls_lst, logger=False):
    
    for pool in pool_cls_lst:
        
        silo_pool_lst = [f.pool_list for f in fast_cls_lst if pool.name in f.pool_list][0]
        
        try:
            silo_id = set([s.split('_')[2] for s in silo_pool_lst])
            
            if len(silo_id) > 1:
                silo_id = '-'
                
            else:
                silo_id = list(silo_id)[0]
            
        except IndexError:
            silo_id = '-'
        
        silo_count = len(silo_pool_lst)
        silo_used_prc = int(sum([p.used_prc for p in pool_cls_lst if p.name in silo_pool_lst])/silo_count)
        silo_subs_prc = int(sum([p.subs_prc for p in pool_cls_lst if p.name in silo_pool_lst])/silo_count)
        
        pool.silo_info(silo_pool_lst, silo_id, silo_count, silo_used_prc, silo_subs_prc)

# @function_check
def sg_ig_lst_retrieve(sid, logger=False, export='Local'):
    
    sg_list = []
    ig_list = []
    
    cmd_sgig_tree = cmd_retrieve('symaccess -sid {0} list -output xml'.format(sid), 0, 1, msg_b='[C:{0}]'.format(sid), logger=logger, export=export)
    
    if cmd_sgig_tree is not 1:
        sg_list = [sg.text for sg in cmd_sgig_tree.findall('Symmetrix/Storage_Group/Group_Info/group_name')]
        ig_list = [ig.text for ig in cmd_sgig_tree.findall('Symmetrix/Initiator_Group/Group_Info/group_name')]
    
    progressbar(1, 1, '(Check) S.Group(s)',  msg_b='[C:{0}]'.format(sid))
    
    return sg_list, ig_list

# @function_check
def vlun_all_vol_session_retrieve(sid, logger=False, export='Local'):
    
    vlun_session_lst = []
    vlun_device_lst = []
    
    cmd_vlun_tree = cmd_retrieve('symmigrate -sid {0} list -output xml'.format(sid), 0, 1, msg_b='[C:{0}]'.format(sid), logger=logger, export=export)
    
    try:
        for vlun in cmd_vlun_tree.findall('Migrate/Session'):
            vlun_session_lst.append(vlun.find('name').text)
            vlun_device_lst.append(vlun.find('src_dev_name').text)
            
    except:
        pass
        
    vlun_session_lst = list(set(vlun_session_lst))
    
    progressbar(1, 1, '(Check) VLun.Session', msg_b='[C:{0}]'.format(sid))
    
    return vlun_session_lst, vlun_device_lst
    
# @function_check
def vlun_session_retrieve(sid, vlun_name, logger=False, export='Local'):
    
    vlun_dic_lst = []
    
    cmd_vlun_tree = cmd_retrieve('symmigrate -sid {0} list -output xml'.format(sid), 0, 1, display=False, logger=logger, export=export)
    
    for vlun in cmd_vlun_tree.findall('Migrate/Session'):
        if vlun.find('name').text == vlun_name:
            
            vlun_dic = {}
            
            vlun_dic['src_dev_name'] = vlun.find('src_dev_name').text
            vlun_dic['state'] = vlun.find('state').text
            vlun_dic['percent_done'] = vlun.find('percent_done').text
            
            vlun_dic_lst.append(vlun_dic)
            
    if not vlun_dic_lst:
        mprint('VLUN Session {0} Not Find'.format(vlun_name), 'err', logger=logger)
        
    else:
        return vlun_dic_lst
    
# @function_check
def view_lst_retrieve(sid, logger=False, export='Local'):
    
    view_list = []
    
    cmd_view_tree = cmd_retrieve('symaccess -sid {0} list view -output xml'.format(sid), 0, 1, msg_b='[C:{0}]'.format(sid), logger=logger, export=export)
    
    if cmd_view_tree is not 1:
        view_list = [v.text for v in cmd_view_tree.findall('Symmetrix/Masking_View/View_Info/view_name')]
    
    progressbar(1, 1, '(Check) M.View(s)', msg_b='[C:{0}]'.format(sid))
    
    return view_list
    
# @function_check
def login_lst_retrieve(sid, logger=False, export='Local'):
    
    login_dic_lst = []
    
    cmd_login_tree = cmd_retrieve('symaccess -sid {0} list logins -output xml'.format(sid), 0, 1, msg_b='[C:{0}]'.format(sid), logger=logger, export=export)
    
    if cmd_login_tree is not 1:
        
        for login in cmd_login_tree.findall('Symmetrix/Devmask_Login_Record/Login'):
            
            login_dic = {}
            
            login_dic['login'] = login.find('originator_port_wwn').text
            login_dic['node_name'] = login.find('awwn_node_name').text
            login_dic['port_name'] = login.find('awwn_port_name').text
            
            login_dic_lst.append(login_dic)
    
    progressbar(1, 1, '(Check) Login(s)', msg_b='[C:{0}]'.format(sid))
    
    return login_dic_lst
    
# @function_check
def sgroup_lun_lst_retrieve(sid, sg_list, logger=False, export='Local'):
    
    count = 0
    t_count = len(sg_list)
    
    result = []
    
    for sg in sg_list:
        cmd_sg_tree = cmd_retrieve('symaccess -sid {0} show {1} -type storage -output xml'.format(sid, sg), count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
        
        if cmd_sg_tree is not 1:
            if cmd_sg_tree.find("Symmetrix/Storage_Group/Group_Info/Device") is not None:
                for sgroup in cmd_sg_tree.findall("Symmetrix/Storage_Group/Group_Info/Device"):
                    start_dev = sgroup.find('start_dev').text
                    end_dev = sgroup.find('end_dev').text
                    
                    if start_dev == end_dev:
                        result.append(start_dev)
                        
                    else:
                        result = result + dev_range_retrieve('{0}:{1}'.format(start_dev, end_dev))
                 
    count += 1
    progressbar(count, t_count, '(Infos) S.Gr[Lun(s)]', msg_b='[I:{0}]'.format(sid))
    
    result = list(set(result))
    
    return result
    
def sgroup_tmp_retrieve(sid, array_type, week_nb, logger=False, export='Local'):
    
    result = []
    
    sg_all_lst, ig_all_lst = sg_ig_lst_retrieve(sid, export=export)
    sgtmp_list = [s for s in sg_all_lst if re.search(r'(SG_|^)vmax_exec_week_[0-9]+_temp(_SG|$)', s)]
    
    if sgtmp_list:
        date_cur = datetime.date.today()
        date_ago = date_cur - datetime.timedelta(weeks=int(week_nb))
        
        week_cur = int(date_cur.isocalendar()[1])
        week_ago = int(date_ago.isocalendar()[1])
        
        for sgtmp in sgtmp_list:
            
            sg_wk = int(re.sub(r'_SG$|^SG_', '', sgtmp).split('_')[3])
            
            if week_cur > week_ago:
                if sg_wk > week_cur or sg_wk <= week_ago:
                    result.append(sgtmp)
                
            if week_cur > week_ago:
                if sg_wk > week_cur and sg_wk <= week_ago:
                    result.append(sgtmp)
                
        if result:  
            return result, sg_all_lst, ig_all_lst
        
    return 1, 1, 1
    
# @function_check
def lun_lst_retrieve(sid, lun_type='', display=True, dev_lst=[], logger=False, export='Local'):
    
    cmd_args = ''
    
    lun_dic_lst = []
    
    if lun_type:
        cmd_args = ' -{0}'.format(lun_type)
        
        if lun_type == 'unbound':
            cmd_args = ' -tdev{0}'.format(cmd_args)
        
    if dev_lst:
        cmd_args = '{0} -dev {1}'.format(cmd_args, ','.join(dev_lst))
        
    cmd_lun_tree = cmd_retrieve('symdev -sid {0} list{1} -output xml'.format(sid, cmd_args), 0, 1, msg_b='[C:{0}]'.format(sid), display=display, logger=logger, export=export)
        
    if cmd_lun_tree is not 1:
        for lun in cmd_lun_tree.findall("Symmetrix/Device"):
            lun_dic = {}
            
            if lun_type == 'wwn':
                lun_dic['id'] = lun.find('dev_name').text
                lun_dic['wwn_id'] = lun.find('wwn').text
                lun_dic['configuration'] = lun.find('configuration').text
                lun_dic['meta'] = bool_check(lun.find('flags/meta').text, False)
            
            else:
                lun_dic['id'] = lun.find('Dev_Info/dev_name').text
                lun_dic['configuration'] = lun.find('Dev_Info/configuration').text
                lun_dic['meta'] = bool_check(lun.find('Flags/meta').text, False)
            
            lun_dic_lst.append(lun_dic)
        
    if display:
        progressbar(1, 1, '(Check) Device(s)', msg_b = '[C:{0}]'.format(sid))
    
    return lun_dic_lst

def lun_free_lst_retrieve(sid, lun_lst, logger=False, export='Local'):
    """ Fonction : Recuperation des luns binde apres un free all """
    
    cmd_lun_tree = cmd_retrieve('symcfg -sid {0} list -tdev -dev {1} -output xml'.format(sid, ','.join(lun_lst)), 0, 1, display=False, logger=logger, export=export)
    
    bound_lst = [l.find('dev_name').text for l in cmd_lun_tree.findall('Symmetrix/ThinDevs/Device') if l.find('tdev_status').text == 'Bound']
    
    return bound_lst
    
# # @function_check
def lun_info_retrieve(lun_lst, sid, array_type, logger=False, export='Local'):
    
    result = []
    count = 0
    t_count = len(lun_lst)
    
    cmd_sg_tree = cmd_retrieve('symaccess -sid {0} list -type stor dev ,{1} -output xml'.format(sid, ','.join(lun_lst)),0, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
    cmd_lun_tree = cmd_retrieve('symdev -sid {0} list -dev {1} -v -output xml'.format(sid, ','.join(lun_lst)),0, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
    cmd_lun_status_tree = cmd_retrieve('symcfg -sid {0} list -tdev -dev {1} -output xml'.format(sid, ','.join(lun_lst)),0, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
    
    for lun in lun_lst:
        
        for device in cmd_lun_tree.findall("Symmetrix/Device"):
            
            if device.find('Dev_Info/dev_name').text == lun:
                
                lun_info = LunInfo(
                    lun,
                    device.find('Product/wwn').text,
                    device.find('Capacity/megabytes').text,
                    device.find('Capacity/cylinders').text,
                    device.find('Dev_Info/configuration').text,
                    device.find('Dev_Info/status').text,
                    device.find('Dev_Info/emulation').text,
                )
                
                if bool_check(device.find('Flags/meta').text):
                    lun_info.meta_info(
                        device.find('Meta/members').text,
                        [meta_mb.text for meta_mb in device.findall('Meta/Meta_Device/dev_name')],
                        [mem_size.text for mem_size in device.findall('Meta/Meta_Device/megabytes')],
                    )
                    
                if bool_check(device.find('Flags/gatekeeper').text):
                    lun_info.gkeep()
                    
                if bool_check(device.find('Flags/aclx').text):
                    lun_info.aclx_flag()
                    
                lun_info.srdf_cap = bool_check(device.find('Flags/dynamic_rdf_capability').text)
                
                if lun_info.tdev:
                    if array_type == 12:
                        pool = bool_check(device.find('Dev_Info/thin_pool_name').text, False)
                    elif array_type == 3:
                        pool = bool_check(device.find('Dev_Info/SRP_name').text, False)
                        
                    if pool: lun_info.pool_info(pool)
                
                if device.find('CLONE_Device') is not None:
                
                    lun_clone_dic_lst = []
                    
                    for clone_info in device.findall("CLONE_Device"):
                        lun_clone_dic = {}
                        
                        lun_clone_dic['state'] = clone_info.find('state').text
                        lun_clone_dic['last_action'] = clone_info.find('last_action').text
                        lun_clone_dic['backgrnd_copy_state'] = clone_info.find('clone_state_flags/backgrnd_copy_state').text
                        lun_clone_dic['differential_state'] = clone_info.find('clone_state_flags/differential_state').text
                        lun_clone_dic['vse'] = clone_info.find('clone_state_flags/vse').text
                        lun_clone_dic['vpsnap'] = clone_info.find('clone_state_flags/vpsnap').text
                        lun_clone_dic['percent_copied'] = clone_info.find('percent_copied').text
                        lun_clone_dic['source_dev_name'] = clone_info.find('SRC/dev_name').text
                        lun_clone_dic['target_dev_name'] = clone_info.find('TGT/dev_name').text
                        
                        lun_clone_dic_lst.append(lun_clone_dic)
                    
                    lun_info.clone_info(lun_clone_dic_lst) 
                    
                if device.find('BCV_Pair') is not None and device.find('BCV_Pair/state').text != 'NeverEstab':
                    
                    lun_bcv_dic_lst = []
                    
                    for bcv_info in device.findall("BCV_Pair"):
                        lun_bcv_dic = {}
                        
                        lun_bcv_dic['state'] = bcv_info.find('state').text
                        lun_bcv_dic['last_action'] = bcv_info.find('last_action').text
                        lun_bcv_dic['source_dev_name'] = bcv_info.find('STD/dev_name').text
                        lun_bcv_dic['target_dev_name'] = bcv_info.find('BCV/dev_name').text
                        
                        lun_bcv_dic_lst.append(lun_bcv_dic)
                    
                    lun_info.bcv_info(lun_bcv_dic_lst)
                    
                if device.find('RDF') is not None:
                    
                    lun_srdf_dic_lst = []
                    lun_srdf_remote_lst = []
                    
                    for srdf_info in device.findall("RDF"):
                        lun_srdf_dic = {}
                        
                        lun_srdf_dic['pair_state'] = srdf_info.find('RDF_Info/pair_state').text
                        lun_srdf_dic['r1_invalids'] = srdf_info.find('RDF_Info/r1_invalids').text
                        lun_srdf_dic['r2_invalids'] = srdf_info.find('RDF_Info/r2_invalids').text
                        lun_srdf_dic['pair_configuration'] = srdf_info.find('RDF_Info/pair_configuration').text
                        lun_srdf_dic['mode'] = srdf_info.find('Mode/mode').text
                        lun_srdf_dic['link'] = srdf_info.find('Status/link').text
                        lun_srdf_dic['link_status_change_time'] = srdf_info.find('Status/link_status_change_time').text
                        lun_srdf_dic['local_dev_name'] = srdf_info.find('Local/dev_name').text
                        lun_srdf_dic['local_type'] = srdf_info.find('Local/type').text
                        lun_srdf_dic['ra_group_num'] = srdf_info.find('Local/ra_group_num').text
                        lun_srdf_dic['remote_dev_name'] = srdf_info.find('Remote/dev_name').text
                        lun_srdf_dic['remote_symid'] = srdf_info.find('Remote/remote_symid').text
                        
                        try:
                            lun_srdf_dic['remote_wwn'] = srdf_info.find('Remote/wwn').text
                        except AttributeError:
                            lun_srdf_dic['remote_wwn'] = 'N/A'
                        
                        lun_srdf_remote_lst.append(lun_srdf_dic['remote_dev_name'])
                        lun_srdf_dic_lst.append(lun_srdf_dic)
                    
                    lun_info.srdf_info(lun_srdf_remote_lst, lun_srdf_dic_lst) 
                
                if device.find('RCopy_Device') is not None:
                
                    lun_openr_dic_lst = []
                    
                    for openr_info in device.findall("RCopy_Device"):
                        lun_openr_dic = {}
                        
                        lun_openr_dic['session_name'] = openr_info.find('session_name').text
                        lun_openr_dic['state'] = openr_info.find('state').text
                        lun_openr_dic['pull'] = openr_info.find('pull').text
                        lun_openr_dic['percent_copied'] = openr_info.find('percent_copied').text
                        lun_openr_dic['remote_wwn'] = openr_info.find('Remote/wwn').text
                        
                        lun_openr_dic_lst.append(lun_openr_dic)
                        
                    lun_info.openrep_info(lun_openr_dic_lst)
                
                
        if cmd_lun_status_tree is not 1:
            
            for device in cmd_lun_status_tree.findall("Symmetrix/ThinDevs/Device"):
                if device.find('dev_name').text == lun:
                    lun_info.status_info(
                        device.find('tdev_status').text,
                        device.find('alloc_tracks_mb').text,
                        device.find('written_tracks_mb').text,
                    ) 
             
        if cmd_sg_tree is not 1:
            
            sgroup_dic_lst = []
            
            for sgroup_info in cmd_sg_tree.findall("Symmetrix/Device"):
                if sgroup_info.find('dev_name').text == lun:
                    for sgroup in sgroup_info.findall('Storage_Group/Group_Info'):
                        
                        if bool_check(sgroup.find('group_name').text):
                            
                            sgroup_dic = {}
                            sgroup_dic['sgroup_name'] = sgroup.find('group_name').text
                            sgroup_dic['status'] = sg_type_case(sgroup.find('Status').text)
                            
                            sgroup_dic_lst.append(sgroup_dic)
                            
            if sgroup_dic_lst:
                lun_info.storage_info(sgroup_dic_lst) 
                    
        result.append(lun_info) 
         
        count += 1 
        progressbar(count, t_count, '(Infos) Device(s)', msg_b = '[I:{0}]'.format(sid)) 
         
    return result 
    
# @function_check
def sgroup_info_retrieve(sgroup_list, sid, array_type, logger=False, export='Local'):
    
    result = []
    count = 0
    t_count = len(sgroup_list)
    
    for sgroup in sgroup_list:
        
        view_bool = False
        
        cmd_sg_tree = cmd_retrieve('symsg -sid {0} show {1} -output xml'.format(sid, sgroup), count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
        cmd_sg_view_tree = cmd_retrieve('symaccess -sid {0} show {1} -type storage -output xml'.format(sid, sgroup), count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
        
        if cmd_sg_view_tree.find('Symmetrix/Storage_Group/Group_Info/Mask_View_Names/view_name') is not None:
            view_bool = True
            
        sgroup_info = SgroupInfo(
            sgroup,
            view_bool,
            bool_check(cmd_sg_tree.find('SG/SG_Info/FAST_Managed').text),
            cmd_sg_view_tree.find('Symmetrix/Storage_Group/Group_Info/Status').text,
        )
        
        if cmd_sg_tree.find('SG/DEVS_List') is not None:
            for device in cmd_sg_tree.findall("SG/DEVS_List"):
                sgroup_info.lun_info(
                    [lun.text for lun in device.findall('Device/dev_name')],
                    sum([int(s.text) for s in device.findall('Device/megabytes')]),
                )
        
        if sgroup_info.view:
            sgroup_info.view_info(
                [view.text for view in cmd_sg_view_tree.findall('Symmetrix/Storage_Group/Group_Info/Mask_View_Names/view_name')],
            )
            
        if sgroup_info.fast:
            if array_type == 12:
                cmd_sg_fast_tree = cmd_retrieve('symfast -sid {0} list -association -demand -sg {1} -output xml'.format(sid, sgroup), count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
                sgroup_info.fast_info(
                    cmd_sg_fast_tree.find('Symmetrix/Fast_Policy/Policy_Info/policy_name').text,
                    [tier.text for tier in cmd_sg_fast_tree.findall('Symmetrix/Fast_Policy/Tier/tier_name')],
                )
                
            elif array_type == 3:
                sgroup_info.slo_info(
                    bool_check(cmd_sg_tree.find('SG/SG_Info/SLO_name').text, False),
                    bool_check(cmd_sg_tree.find('SG/SG_Info/SRP_name').text, False),
                )
        
        if sgroup_info.type != 'normal':
            cascad_view = False
            cascad_view_name = []
            cascad_sgroup_dic_lst = []
            
            if cmd_sg_view_tree.find('Symmetrix/Storage_Group/Group_Info/Cascaded_View_Names/view_name') is not None:
                cascad_view = True
                cascad_view_name = [v.text for v in cmd_sg_view_tree.findall('Symmetrix/Storage_Group/Group_Info/Cascaded_View_Names/view_name')]
            
            for cascad_sgroup_info in cmd_sg_view_tree.findall('Symmetrix/Storage_Group/Group_Info/SG_Group_info/SG'):
                cascad_sgroup_dic = {}
                cascad_sgroup_dic['sgroup_name'] = cascad_sgroup_info.find('group_name').text
                cascad_sgroup_dic['status'] = cascad_sgroup_info.find('Status').text
                
                
                
                cascad_sgroup_dic_lst.append(cascad_sgroup_dic)
            
            sgroup_info.cascad_info(cascad_view, cascad_view_name, cascad_sgroup_dic_lst)
            
        result.append(sgroup_info)
        
        count += 1
        
        progressbar(count, t_count, '(Infos) S.Group(s)', msg_b = '[I:{0}]'.format(sid)) 
    
    return result
    
# @function_check
def view_info_retrieve(view_list, sid, logger=False, export='Local'):
    
    result = []
    count = 0
    t_count = len(view_list)
    
    for view in view_list:
        
        cmd_view_tree = cmd_retrieve('symaccess -sid {0} show {1} view -detail -output xml'.format(sid, view), count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
        
        init = cmd_view_tree.find('Symmetrix/Masking_View/View_Info/init_grpname').text
        
        view_info = ViewInfo(
            view,
            cmd_view_tree.find('Symmetrix/Masking_View/View_Info/stor_grpname').text,
            init,
            cmd_view_tree.find('Symmetrix/Masking_View/View_Info/port_grpname').text,
        ) 
        
        cmd_init_tree = cmd_retrieve('symaccess -sid {0} show {1} -type init -output xml'.format(sid, init), count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
        
        view_info.init_info([mv.text.replace(' *', '') for mv in cmd_init_tree.findall('Symmetrix/Initiator_Group/Group_Info/Mask_View_Names/view_name')])
        
        if cmd_init_tree.find('Symmetrix/Initiator_Group/Group_Info/Initiator_List/Initiator/group_name') is not None:
            ig_list = [ig.text for ig in cmd_init_tree.findall('Symmetrix/Initiator_Group/Group_Info/Initiator_List/Initiator/group_name')]
            ig_info_list = []
            
            for ig in ig_list:
                cmd_init_child_tree = cmd_retrieve('symaccess -sid {0} show {1} -type init -output xml'.format(sid, ig), count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
                
                ig_info = {}
                ig_info['name'] = ig
                ig_info['parent_ig'] = view_info.init
                ig_info['login_list'] = [login.text for login in cmd_init_child_tree.findall('Symmetrix/Initiator_Group/Group_Info/Initiator_List/Initiator/wwn')]
                ig_info['view_list'] = [mv.text.replace(' *', '') for mv in cmd_init_child_tree.findall('Symmetrix/Initiator_Group/Group_Info/Mask_View_Names/view_name')]
                
                ig_info_list.append(ig_info)
                    
            view_info.cascad_info(ig_list, ig_info_list)
        
        view_info.login_info([login.text for login in cmd_view_tree.findall('Symmetrix/Masking_View/View_Info/Initiators/wwn')])
        view_info.lun_info(
            list(set([lun.text for lun in cmd_view_tree.findall('Symmetrix/Masking_View/View_Info/Device/dev_name')])),
            int(cmd_view_tree.find('Symmetrix/Masking_View/View_Info/Totals/total_dev_cap_mb').text),
        )
        
        result.append(view_info)
        
        count += 1
        progressbar(count, t_count, '(Infos) M.View(s)', msg_b = '[I:{0}]'.format(sid)) 
        
    return result
   
# @function_check
def login_info_retrieve(login_list, sid, logger=False, export='Local'):
    
    result = []
    count = 0
    t_count = len(login_list)
    
    mode = ''
    
    for login in login_list:
        
        login_info = LoginInfo(login)
        
        cmd_login_tree = cmd_retrieve('symaccess -sid {0} list logins -wwn {1} -output xml'.format(sid, login),count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
        cmd_init_tree = cmd_retrieve('symaccess -sid {0} list -type init -wwn {1} -output xml'.format(sid, login),count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
          
        if cmd_login_tree != 1:
            
            port_dic_lst = []
            
            for port_info in cmd_login_tree.findall("Symmetrix/Devmask_Login_Record"):
                
                port_dic = {}
                
                port_dic['director'] = port_info.find('director').text
                port_dic['port'] = port_info.find('port').text
                port_dic['port_wwn'] = port_info.find('port_wwn').text
                port_dic['type'] = port_info.find('Login/type').text
                port_dic['node_name'] = port_info.find('Login/awwn_node_name').text
                port_dic['port_name'] = port_info.find('Login/awwn_port_name').text
                port_dic['fcid'] = port_info.find('Login/fcid').text
                port_dic['logged_in'] = port_info.find('Login/logged_in').text
                port_dic['on_fabric'] = port_info.find('Login/on_fabric').text
                
                port_dic_lst.append(port_dic)
                
            login_info.port_info(port_dic_lst)
        
        if cmd_init_tree != 1:
            
            ig_dic_lst = []
            
            for init_info in cmd_init_tree.findall("Symmetrix/Initiator_Group/Group_Info"):
                
                ig_dic = {}
                
                ig_dic['mv_list'] = [mv.text for mv in init_info.findall('Mask_View_Names/view_name')]
                ig_dic['ig_name'] = init_info.find('group_name').text
                ig_dic['last_update'] = init_info.find('last_updated').text
                
                ig_dic_lst.append(ig_dic)
            
            login_info.init_info(ig_dic_lst)
            
        result.append(login_info)
        
        count += 1
        progressbar(count, t_count, '(Infos) Login(s)', msg_b = '[I:{0}]'.format(sid)) 
    
    if mode == 'new_login':
        return result, view_list, node_name_list, port_port_list
        
    else:
        return result
   
def lun_by_pool_retrieving(sid, lun_lst, pool_cls_lst, logger=False, export='Local'):
    
    result = []
    count = 0
    t_count = len(lun_lst)
    
    lun_pool_lst = []
    
    cmd_lun_status_tree = cmd_retrieve('symcfg -sid {0} list -tdev -dev {1} -output xml'.format(sid, ','.join(lun_lst)),count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
    
    for lun in lun_lst:
        
        if cmd_lun_status_tree is not 1:
            
            for device in cmd_lun_status_tree.findall("Symmetrix/ThinDevs/Device"):
                
                if device.find('dev_name').text == lun:
                    lun_pool_lst.append(device.find('pool_name').text)
        
        count += 1
        progressbar(count, t_count, '(Infos) Lun(s) Pool', msg_b = '[I:{0}]'.format(sid)) 
        
    result = sorted([{cnt : lun_pool_lst.count(cnt)} for cnt in set(lun_pool_lst)])
    
    for pool in pool_cls_lst:
        
        if pool.name in lun_pool_lst and not pool.error:
            pool.info = True
    
    return result
   
# @function_check
def pool_retrieving(sid, pool_list=[], lun_tsize=0, lun_consum_tsize=0, logger=False, export='Local'):
    
    result = []
    count = 0
    t_count = 1
    
    cmd_pool_tree = cmd_retrieve('symcfg -sid {0} list -thin -pool -detail -gb -output xml'.format(sid),count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
    
    if not pool_list:
        pool_list = [pool.text for pool in cmd_pool_tree.findall('Symmetrix/DevicePool/pool_name')]
    
    t_count = len(pool_list)
    
    for pool in pool_list:
        for pool_inf in cmd_pool_tree.findall("Symmetrix/DevicePool"):
            if pool_inf.find('pool_name').text == pool:
                pool_info = PoolInfo(
                    pool,
                    pool_inf.find('total_tracks_gb').text,
                    pool_inf.find('total_used_tracks_gb').text,
                    pool_inf.find('percent_full').text,
                    pool_inf.find('subs_percent').text,
                    lun_tsize,
                    lun_consum_tsize,
                )
                
                result.append(pool_info)
            
        count += 1
        progressbar(count, t_count, '(Infos) Pool(s)', msg_b = '[I:{0}]'.format(sid)) 
        
    return result
 
# @function_check 
def srp_retrieving(sid, lun_tsize=0, lun_consum_tsize=0, logger=False, export='Local'):

    result = []
    count = 0
    t_count = 1
    
    cmd_srp_tree = cmd_retrieve('symcfg -sid {0} list -srp -detail -gb -output xml'.format(sid),count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
      
    for srp_inf in cmd_srp_tree.findall("Symmetrix/SRP/SRP_Info"):
        srp_info = SRPInfo(
            srp_inf.find('name').text,
            srp_inf.find('usable_capacity_gigabytes').text,
            srp_inf.find('allocated_capacity_gigabytes').text,
            srp_inf.find('subscribed_capacity_gigabytes').text,
            lun_tsize,
            lun_consum_tsize,
        )
        
        result.append(srp_info)
        
        count += 1
        
        progressbar(count, t_count, '(Infos) SRP(s)', msg_b = '[I:{0}]'.format(sid))
    
    return result
    
# @function_check
def fast_retrieving(sid, fast_list=[], logger=False, export='Local'):
    
    result = []
    count = 0
    t_count = 1
    
    cmd_fast_tree = cmd_retrieve('symfast -sid {0} list -fp -v -output xml'.format(sid),count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
    cmd_tier_tree = cmd_retrieve('symtier -sid {0} list -v -output xml'.format(sid),count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
    
    if not fast_list:
        fast_list = [fast.text for fast in cmd_fast_tree.findall('Symmetrix/Fast_Policy/Policy_Info/policy_name')]
    
    t_count = len(fast_list)
    
    for fast in fast_list:    
        for fast_inf in cmd_fast_tree.findall("Symmetrix/Fast_Policy"):
            if fast_inf.find('Policy_Info/policy_name').text == fast:
                
                tier_list = [tier.text for tier in fast_inf.findall('Tier/tier_name')]
                
                fast_info = FastInfo(
                    fast,
                    fast_inf.find('Policy_Info/num_of_sg').text,
                )
                
                tier_dic_lst = []
                
                for tier in tier_list:
                    for tier_inf in cmd_tier_tree.findall("Symmetrix/Storage_Tier/Tier_Info"):
                        if tier_inf.find('tier_name').text == tier:
                            tier_dic = {}
                            tier_dic['name'] = tier
                            tier_dic['type'] = tier_inf.find('tier_type').text
                            tier_dic['disk_location'] = tier_inf.find('disk_location').text
                            tier_dic['techno'] = tier_inf.find('technology').text
                            tier_dic['protection'] = tier_inf.find('target_protection').text
                            tier_dic['pool_name'] = tier_inf.find('Thin_Pool_Info/pool_name').text
                            
                            tier_dic_lst.append(tier_dic) 
                
                fast_info.tier_info(tier_list, tier_dic_lst)
                
                result.append(fast_info)
                
                count += 1
                progressbar(count, t_count, '(Infos) Fast.P(s)', msg_b = '[I:{0}]'.format(sid))
                
    return result
   
# @function_check 
def slo_retrieving(srp_cls_lst, sid, logger=False, export='Local'):

    result = []
    count = 0
    t_count = 1
    
    cmd_slo_tree = cmd_retrieve('symcfg -sid {0} list -slo -output xml'.format(sid),count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
    
    for srp in srp_cls_lst:
        srp.slo_info([slo.text for slo in cmd_slo_tree.findall('Symmetrix/SLO/SLO_Info/name')])
    
    count += 1
    progressbar(count, t_count, '(Infos) Slo(s)', msg_b = '[I:{0}]'.format(sid))
        
   
# @function_check
def port_group_retrieving(sid, logger=False, export='Local'):
    
    result = []
    count = 0
    t_count = 1
    
    cmd_pg_list_tree = cmd_retrieve('symaccess -sid {0} list -type port -output xml'.format(sid),count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
    
    pg_list = [pg.text for pg in cmd_pg_list_tree.findall('Symmetrix/Port_Group/Group_Info/group_name')]
    
    t_count = len(pg_list)
    
    for pg in pg_list:
        
        cmd_pg_tree = cmd_retrieve('symaccess -sid {0} show {1} -type port -output xml'.format(sid, pg),count, t_count, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
        
        pg_info = PortGroupInfo(
            pg,
            [dir.text for dir in cmd_pg_tree.findall('Symmetrix/Port_Group/Group_Info/Director_Identification/dir')],
            [port.text for port in cmd_pg_tree.findall('Symmetrix/Port_Group/Group_Info/Director_Identification/port')],
            [mv.text for mv in cmd_pg_tree.findall('Symmetrix/Port_Group/Group_Info/Mask_View_Names/view_name')],
        )
        
        result.append(pg_info)
        
        count += 1
        progressbar(count, t_count, '(Infos) P.Group(s)', msg_b = '[I:{0}]'.format(sid))
    
    return result
    
# @function_check
def ra_group_retrieve(array_id, rmt_id, logger=False, export='Local'):
    
    sid = array_id[-4:]
    
    cmd_ra_list_tree = cmd_retrieve('symcfg -sid {0} list -ra all -switch -output xml'.format(sid),0, 1, msg_b='[I:{0}]'.format(sid), logger=logger, export=export)
    
    ra_dic_lst = []
    
    for ragroup in cmd_ra_list_tree.findall('Symmetrix/Director/Port/RDF'):
        if ragroup.find('remote_symid').text == rmt_id:
            ra_dic = {}
            
            ra_dic['rmt_id'] = rmt_id
            
            try:
                ra_dic['rmt_ra_port_id'] = '{0}:{1}'.format(ragroup.find('remote_ra_id').text, ragroup.find('remote_port').text)
                ra_dic['ra_group_num'] = ragroup.find('ra_group_num').text
                ra_dic['ra_group_label'] = ragroup.find('ra_group_label').text
                ra_dic['rmt_ra_group_num'] = ragroup.find('remote_ra_group_num').text
                ra_dic['link_sw'] = ragroup.find('Attributes/Link/rdf_sw_comp_supported').text
                ra_dic['link_hw'] = ragroup.find('Attributes/Link/rdf_hw_comp_supported').text
            
                ra_dic_lst.append(ra_dic)
                
            except AttributeError:
                mprint()
                
                mprint('Ra Group with Remote ID {0} Not Active'.format(rmt_id), 'err', logger=logger)
            
    progressbar(1, 1, '(Infos) RA.Group(s)', msg_b = '[I:{0}]'.format(sid))
    
    if not ra_dic_lst:
        mprint('No RA Group Find Between {0} And {1}'.format(array_id, rmt_id), 'err', logger=logger)
    else:
        result = RaGroupInfo(rmt_id, ra_dic_lst)
    
    return result

# @function_check
def lun_by_type_migrate_fmt(lun_cls_lst, local_array_type, remote_array_type):
    
    dev_attr_lst = []
    dev_attr_conv_lst = []
    
    for l in lun_cls_lst:
        
        if not l.gkeeper:
            
            dev_attr = l.size_cyl
            dev_attr_conv = dev_attr
            
            if local_array_type is 3:
                dev_attr_conv = dev_attr * 2
            
            if local_array_type is 12 and remote_array_type is 3:
                
                if dev_attr % 2 is not 0:
                    dev_attr = dev_attr + 3
                
                dev_attr = dev_attr / 2
                
            if l.meta and not remote_array_type is 3:
                dev_attr = '{0}c:{1}'.format(dev_attr, l.meta_count)
            
            else:
                dev_attr = '{0}c'.format(dev_attr)
                
        dev_attr_lst.append(dev_attr)
        dev_attr_conv_lst.append(dev_attr_conv)
    
    dev_by_type_lst = sorted(['{0}x{1}'.format(dev_attr_lst.count(cnt), cnt) for cnt in set(dev_attr_lst)])
    dev_by_type_conv_lst = sorted(['{0}x{1}'.format(dev_attr_conv_lst.count(cnt), cnt) for cnt in set(dev_attr_conv_lst)])
    
    return dev_by_type_lst, dev_by_type_conv_lst

# @function_check
def lun_by_type_retrieve(lun_cls_lst, array_type=12):
    gk_lst = []
    
    lun_size_lst = [int(l.size/1024) for l in lun_cls_lst if not l.meta and not l.gkeeper]
    meta_size_lst = ['{0}:{1}'.format(int(l.size/1024), l.meta_count) for l in lun_cls_lst if l.meta]
    
    if array_type is 3 and meta_size_lst:
        meta_size_lst = [m.split(':')[0] for m in meta_size_lst]
    
    gk_lst = ['GK' for l in lun_cls_lst if l.gkeeper]
    
    all_lun_lst = lun_size_lst + meta_size_lst + gk_lst
    result = sorted(['{0}x{1}'.format(all_lun_lst.count(cnt), cnt) for cnt in set(all_lun_lst)])
    
    return result
    
    
    
    