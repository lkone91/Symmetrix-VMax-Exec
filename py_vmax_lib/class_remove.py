# -*- coding: utf-8 -*-

#================================================================================#
# ------------------------------- IMPORT LIBRARY ------------------------------- #
#================================================================================#

#~~~~# LOCAL LIBRARY #~~~~#

from py_vmax_lib.func_global import *
from py_vmax_lib.func_execution import *
from py_vmax_lib.func_display import *
from py_vmax_lib.func_check import *
from py_vmax_lib.func_retrieve import *

from py_vmax_lib.class_audit import AuditMode

#==============================================================================#
# ------------------------------- MODULE START ------------------------------- #
#==============================================================================#

class RemoveMode(AuditMode):
    """Remove Mode class"""
    
    def __init__(self, glob_dic, logger):
        AuditMode.__init__(self, glob_dic, logger)
        
        self.remove_mode = 'normal'
        self.remove_max_lun = 400
        
        if self.rmv_total:
            self.remove_mode = 'total'
            
    def info_retrieve(self):
        AuditMode.info_retrieve(self)
        
        if self.mode != 'select' and self.dev != 'dev_sg':
            self.sg_all_lst, self.ig_all_lst = sg_ig_lst_retrieve(self.sid)
        
    def mode_check(self):
        
        if not self.rmv_repli and not self.unbind_mode and not self.noport_mode:
            self.force_mode = True
        
        # Verification existence S.Group Temporaire ###
            
        if self.array_type is 12:
            self.sg_temp_name = 'vmax_utils_week_{0}_temp_SG'.format(time.strftime("%V"))
            
        elif self.array_type is 3:
            self.sg_temp_name = 'SG_vmax_utils_week_{0}_temp'.format(time.strftime("%V"))
        
        self.sg_temp = exist_check([self.sg_temp_name], self.sg_all_lst)
        
        # Emulation FBA Celerra #
        
        if self.lun_cls_lst:
            
            lun_bad_emul_lst = []
            
            for l in self.lun_cls_lst:
                if l.emulation != 'FBA':
                    l.remove = False
                    lun_bad_emul_lst.append(l.id)
                    
            if lun_bad_emul_lst:
                self.warning_dict[self.warning_id_incr] = "Bad Emulation Type Detected for Device [{0}]. Script Not Delete It".format(','.join(lun_bad_emul_lst))
        
        # Verification des Luns Unbind #
        
        if self.unbind_mode:
            
            lun_with_sg_lst = []
            
            for l in self.lun_cls_lst:
                if not l.error:
                    if not l.sgroup:
                        l.warning = False
                        l.remove = True
                    else:
                        lun_with_sg_lst.append(l.id)
                        
                        if self.force_mode:
                            l.remove = True
                        
            if lun_with_sg_lst:
                
                warning_msg = ''
                
                if not self.force_mode:
                    warning_msg = ' Script not Remove It (Or Use -force Flag)'
                
                self.warning_dict[self.warning_id_incr] = 'Unbind Lun(s) with S.Group [{0}]{1}'.format(','.join(lun_with_sg_lst), warning_msg)
            
        # Verification des Luns sans Port #
        
        if self.noport_mode:
            
            lun_with_sg_lst = []
            lun_with_repli_lst = []
            lun_aclx_flag = []
            
            warning_msg = ''
            
            if not self.force_mode:
                warning_msg = ' Script not Remove It (Or Use -force Flag)'
            
            for l in self.lun_cls_lst:
                if not l.error:
                    l.warning = False
                    
                    if l.clone or l.bcv or l.srdf:
                        lun_with_repli_lst.append(l.id)
                        l.warning = True
                        
                    if l.aclx:
                        lun_aclx_flag.append(l.id)
                        l.warning = True
                        
                    if l.sgroup:
                        lun_with_sg_lst.append(l.id)
                        l.warning = True
                    
                    if not l.warning:
                        l.remove = True
                        
                    if l.warning and self.force_mode:
                        l.remove = True
                   
            
                   
            if lun_with_sg_lst:
                self.warning_dict[self.warning_id_incr] = 'Lun(s) with S.Group [{0}]{1}'.format(','.join(lun_with_sg_lst), warning_msg)
                
            if lun_aclx_flag:
                self.warning_dict[self.warning_id_incr] = 'Lun(s) ACLX [{0}]{1}'.format(','.join(lun_aclx_flag), warning_msg)
                
            if lun_with_repli_lst:
                self.warning_dict[self.warning_id_incr] = 'Lun(s) with Replication [{0}]{1}'.format(','.join(lun_with_repli_lst), warning_msg)
            
        if self.unbind_mode or self.noport_mode:
            
            if not [l for l in self.lun_cls_lst if l.remove]:
                self.error_dict[self.error_id_incr] = 'No Lun(s) to Delete'
            
        # Verification Device #
            
        if self.force_mode:
            
            sg_to_remove = []
            
            if self.dev == 'dev_lun':
                
                # Verification Multi S.Group (-lun) #
                
                sgroups_list = rtr_dict_list(self.lun_cls_lst, 'sgroup_list_fmt', True, join=True)
                
                if sgroups_list:
                    
                    lun_sg_dic_list = []
                    
                    for sgroups in sgroups_list:
                        
                        sgroup_lst = sgroups.split(',')
                        
                        debug_fmt(self.debug_mode, sgroup_lst)
                        
                        lun_sg_list = []
                        lun_sg_dic = {}
                        
                        for l in self.lun_cls_lst:
                            if not l.error and l.sgroup:
                                if sorted(l.sgroup_list_fmt) == sorted(sgroup_lst):
                                    lun_sg_list.append(l.id)
                        
                        if lun_sg_list:
                            
                            sgroups_fmt = []
                            
                            for s in sgroup_lst:
                                if 'P:' in s:
                                    sgroups_fmt.append(s.split('[')[0])
                                else:
                                    sgroups_fmt.append(s)
                            
                            lun_sg_dic['sgroup_list'] = sgroups_fmt
                            lun_sg_dic['lun_list'] = lun_sg_list
                            lun_sg_dic_list.append(lun_sg_dic)
                            
                    if lun_sg_dic_list:
                        
                        debug_fmt(self.debug_mode, lun_sg_dic_list)
                        
                        for lun_sg_dic in lun_sg_dic_list:
                            
                            if len(lun_sg_dic['sgroup_list']) > 1:
                                sgroup_list_choice = list(lun_sg_dic['sgroup_list'])
                                sgroup_list_choice.append('Remove All')
                                choice = select_choice(sgroup_list_choice, title = color_str(' <!> Lun(s) {0} have {1} S.Groups. Select One [or All] to Remove :'.format(lun_sg_dic['lun_list'], len(lun_sg_dic['sgroup_list'])), 'yel'))
                                
                            else:
                                choice = 'Remove All'
                            
                            if choice == 'Remove All':
                                rmv_sg = lun_sg_dic['sgroup_list']
                            else:
                                rmv_sg = [choice]
                            
                            for l in self.lun_cls_lst:
                                if not l.error and l.id in lun_sg_dic['lun_list']:
                                    
                                    if choice != 'Remove All':
                                        self.warning_dict[self.warning_id_incr] = 'Shared Lun(s) {0} not Delete'.format(lun_sg_dic['lun_list'])
                                    else:
                                        l.remove = True
                                        
                            for sgroup in self.sgroup_cls_lst:
                                if sgroup.name in rmv_sg:
                                    sgroup.lun_to_remove(lun_sg_dic['lun_list'])
                            
                            sg_to_remove = list(set(sg_to_remove + rmv_sg))
                            
                # Autre Luns #
                
                for l in self.lun_cls_lst:
                    if not l.error:
                        if not l.sgroup:
                            l.remove = True
                    
                # Verification S.Group Vide #
                
                for sgroup in self.sgroup_cls_lst:
                    
                    debug_fmt(self.debug_mode, sgroup.name)
                    
                    if sgroup.name in sg_to_remove:
                        
                        if len(sgroup.lun_list) == len(sgroup.remove_lun):
                            self.warning_dict[self.warning_id_incr] = 'All Luns of SG "{0}" will be Remove. So SG will be Delete too'.format(sgroup.name)
                            sgroup.remove = True
                            
                # Login Info #
                
                if any([s.remove and s.view for s in self.sgroup_cls_lst]):
                    
                    self.login_lst = rtr_dict_list(self.view_cls_lst, 'login_list', uniq=True, concat=True)
                    
                    if self.login_lst:
                        self.login_cls_lst = login_info_retrieve(self.login_lst, self.sid, logger=self.logger)

            # Verification Multi S.Group (-sg) #
            
            if self.dev == 'dev_sg':
                
                sg_to_remove = self.dev_sg_arg
                
                if self.lun_cls_lst:
                    
                    shared_lun_list = []
                    no_shared_lun_list = []
                    
                    for l in self.lun_cls_lst:
                        if not l.error:
                            shared_sgroup = [s for s in l.sgroup_list_fmt if s.split('[')[0] not in self.dev_sg_arg]
                            
                            if shared_sgroup:
                                shared_lun_list.append(l.id)
                            else:
                                no_shared_lun_list.append(l.id)
                                l.remove = True
                    
                    if shared_lun_list:
                        self.warning_dict[self.warning_id_incr] = 'Shared Lun(s) {0} not Delete'.format(shared_lun_list)
                    
                for sgroup in self.sgroup_cls_lst:
                    
                    if sgroup.name in self.dev_sg_arg:
                        sgroup.remove = True
                        
                    if sgroup.lun:
                        
                        if sgroup.name in self.dev_sg_arg:
                            sgroup.remove_lun = [l for l in sgroup.lun_list]
                        
                        else:
                            for lun in sgroup.lun_list:
                                if lun in no_shared_lun_list:
                                    sgroup.remove_lun.append(lun)
            
            # Verification Cascade S.Group #
                   
            for sgroup in self.sgroup_cls_lst:
                
                if sgroup.type == 'parent':
                    
                    sg_child_to_remove = [s.name for s in self.sgroup_cls_lst if s.name in sgroup.cascad_sgroup_name and s.remove]
                    
                    if sorted(sg_child_to_remove) == sorted(sgroup.cascad_sgroup_name):
                        self.warning_dict[self.warning_id_incr] = 'All SG of Cascad SG "{0}" will be Remove. So C.SG will be Delete too'.format(sgroup.name)
                        sgroup.remove = True
                    
                    
            # Verification Multi Init #
            
            if [s for s in self.sgroup_cls_lst if s.remove and s.view]:
                
                views_list = list(set([v.name for v in self.view_cls_lst if v.sgroup in sg_to_remove]))
                
                shared_ig_list = []
                no_shared_login_list = []
                
                for view in self.view_cls_lst:
                    
                    if view.init_share:
                        
                        shared_view = [mv for mv in view.init_view_list if mv not in views_list]
                        
                        if shared_view:
                            shared_ig_list.append(view.init)
                        else:
                            view.init_remove = True
                            no_shared_login_list = no_shared_login_list + view.login_list
                        
                    else:
                        view.init_remove = True
                        no_shared_login_list = no_shared_login_list + view.login_list
                        
                    if view.init_csc:
                        
                        for init_child in view.init_child_info:
                            
                            if init_child['share']:
                            
                                shared_view = [mv for mv in init_child['view_list'] if mv not in views_list]
                                
                                if shared_view:
                                    shared_ig_list.append(init_child['name'])
                                else:
                                    init_child['remove'] = True
                                    no_shared_login_list = no_shared_login_list + init_child['login_list']
                                
                            else:
                                init_child['remove'] = True
                                no_shared_login_list = no_shared_login_list + init_child['login_list']
                            
                if shared_ig_list:
                    self.warning_dict[self.warning_id_incr] = 'Shared IG {0} not Remove'.format(list(set(shared_ig_list)))
        
                # Verification Status Logins #
                
                no_shared_login_list = list(set(no_shared_login_list))
                
                if no_shared_login_list:
                    
                    login_log_in_lst = []
                    
                    for login in no_shared_login_list:
                        login_cls = [w for w in self.login_cls_lst if w.wwn == login][0]
                        
                        if login_cls.port_count is not 0:
                            login_cls.remove = True
                        
                        if 'Y' in login_cls.status_log_in:
                            login_log_in_lst.append(login)
                            login_cls.warning = True
            
                    if login_log_in_lst:
                        self.warning_dict[self.warning_id_incr] = 'Login(s) on "Log In" Status [{0}]'.format(','.join(login_log_in_lst))
            
    def info_display(self):
        
        if self.login_cls_lst:
            login_display(self.sid, self.login_cls_lst, war_type='Login(s) on "Log In" Status', debug=self.debug_mode)
        
        if self.sgroup_cls_lst:
            sgroup_display(self.sid, self.sgroup_cls_lst, self.view_cls_lst, self.array_type, debug=self.debug_mode)
        
        if self.lun_cls_lst:
            
            warning_type = 'Unbind/Reclaim/N.Ready'
            
            if self.unbind_mode:
                warning_type = 'Lun(s) with S.Group'
                
            if self.noport_mode:
                warning_type = 'Lun(s) with S.Group/Replication'
                
            lun_display(self.sid, self.lun_cls_lst, self.array_type, wwn_type=self.dev_lwwn, war_type=warning_type, err_type='Lun(s) with Bad Emulation', size_display=self.size_display, debug=self.debug_mode, verbose=self.verbose_mode)
        
    def mode_exec(self):
        
        # Declaration des listes de commande #
        
        remove_sg_to_csg = []
        remove_ig_to_cig = []
        remove_wwn_to_ig = []
        remove_fast_to_sg = []
        remove_lun_to_sg = []
        delete_sg = []
        delete_csg = []
        delete_mv = []
        delete_cig = []
        delete_ig = []
        delete_lun = []
        delete_login = []
        reclaim_stop = []
        unbind_lun = []
        free_all_lun = []
        dissolve_meta = []
        create_sgtmp = []
        move_lun_to_sgtmp = []
        
        # Verification / Recuperation Replication #
        
        srdf_dic_lst = []
        clone_all_dic_lst = []
        clone_dic_lst = []
        bcv_all_dic_lst = []
        bcv_dic_lst = []
        openr_dic_lst = []
        
        if self.force_mode:
            srdf_dic_lst = rtr_dict_list(self.lun_cls_lst, 'srdf_list_info', concat=True)
            clone_all_dic_lst = rtr_dict_list(self.lun_cls_lst, 'clone_info_dic_lst', concat=True)
            bcv_all_dic_lst = rtr_dict_list(self.lun_cls_lst, 'bcv_info_dic_lst', concat=True)
            openr_dic_lst = rtr_dict_list(self.lun_cls_lst, 'openr_dic_lst', concat=True)
        
        if self.rmv_repli:
            if not srdf_dic_lst and not clone_all_dic_lst and not bcv_all_dic_lst:
                self.error_dict[self.error_id_incr] = 'No Repli to Remove Find'
            
        else:
            
            if srdf_dic_lst:
                self.warning_dict[self.warning_id_incr] = 'Lun(s) with SRDF, Script Delete Pair(s)'
                
                # Verification Replication SRDF #
                
                if any([s['pair_state'] == 'SyncInProg' for s in srdf_dic_lst]):
                    self.error_dict[self.error_id_incr] = "Luns Pair(s) on 'Sync In Progress' State"
                    
                if any([s['pair_state'] == 'Synchronized' for s in srdf_dic_lst]):
                    self.warning_dict[self.warning_id_incr] = "Lun Pair(s) on 'Synchronized' State"
                
            if clone_all_dic_lst:
                self.warning_dict[self.warning_id_incr] = 'Lun(s) with Clone, Script Delete Pair(s)'
                
                clone_dic_lst = []
                clone_warning = False
                
                clone_source_target_lst = [c['target_dev_name'] for c in clone_all_dic_lst if c['type'] == 'Source']
                
                for c in clone_all_dic_lst:
                    if c['type'] == 'Target':
                        
                        c['clone_count'] = 0
                        
                        for l in clone_all_dic_lst:
                            if l['type'] == 'Target' and l['source_dev_name'] == c['source_dev_name']:
                                l['clone_count'] += 1
                                
                        if c['target_dev_name'] in clone_source_target_lst:
                            clone_warning = True
                            
                        else:
                            clone_dic_lst.append(c)
                            
                    else:
                        clone_dic_lst.append(c)
                    
                if clone_warning:
                    self.warning_dict[self.warning_id_incr] = "Source and Target Clone are Present"
                
            if bcv_all_dic_lst:
                self.warning_dict[self.warning_id_incr] = 'Lun(s) with BCV, Script Delete Pair(s)'
                
                bcv_dic_lst = dict((b['target_dev_name'],b) for b in bcv_all_dic_lst).values()
                
                if len(bcv_dic_lst) != len(bcv_all_dic_lst):
                    self.warning_dict[self.warning_id_incr] = "Source and Target BCV are Present"
                
            if openr_dic_lst:
                self.warning_dict[self.warning_id_incr] = 'Lun(s) with Open Replicator, Script Delete Pair(s)'
                
            views_list = rtr_dict_list(self.view_cls_lst, 'name', uniq = True)
            
            if self.sgroup_cls_lst:
                
                for sgroup in self.sgroup_cls_lst:
                    
                    #### REMOVE LUN TO SG ####
                    
                    if sgroup.remove_lun:
                        unmap = ''
                        
                        if not sgroup.remove:
                            if sgroup.view or getattr(sgroup, 'cascad_view_name', False):
                                unmap = ' -unmap'
                        
                        if sgroup.type != 'parent':
                            remove_lun_to_sg.append('symaccess -sid {0} remove -name {1} -type storage dev {2}{3}'.format(self.sid, sgroup.name, ','.join(sgroup.remove_lun), unmap))
                    
                    #### REMOVE SG ####
                        
                    if sgroup.remove:
                        
                        if sgroup.cascad:
                            
                            if sgroup.type == 'child':
                                unmap = ''
                                if not sgroup.remove:
                                    if sgroup.cascad_view or sgroup.view:
                                        unmap = ' -unmap'
                                
                                remove_sg_to_csg.append('symaccess -sid {0} remove -name {1} -type storage -sg {2}{3}'.format(self.sid , ''.join(sgroup.cascad_sgroup_name), sgroup.name, unmap))
                                
                            elif sgroup.type == 'parent':
                                for child_sg in sgroup.cascad_sgroup_name:
                                    if [s.remove for s in self.sgroup_cls_lst if s.name == child_sg][0]:
                                        remove_sg_to_csg.append('symaccess -sid {0} remove -name {1} -type storage -sg {2}'.format(self.sid , sgroup.name, child_sg))
                                
                        if sgroup.fast and self.array_type is 12:
                            remove_fast_to_sg.append('symfast -sid {0} disassociate -fp_name {1} -sg {2}'.format(self.sid, sgroup.fast_name, sgroup.name))
                            
                        delete_sg.append('symaccess -sid {0} delete -name {1} -type storage -nop'.format(self.sid, sgroup.name))
                            
                        #### REMOVE MV ####
                                
                        if sgroup.view:
                            
                            login_log_in_check = False
                            
                            for view in self.view_cls_lst:
                                
                                if view.sgroup == sgroup.name:
                                    
                                    delete_mv.append('symaccess -sid {0} delete -name {1} view -unmap -nop'.format(self.sid, view.name, sgroup.name))
                                    
                                    if view.init_remove:
                                        
                                        if view.init_csc:
                                            
                                            for init_child in view.init_child_info:
                                                remove_ig_to_cig.append('symaccess -sid {0} remove -name {1} -type init -ig {2}'.format(self.sid, init_child['parent_ig'], init_child['name']))
                                                
                                                if init_child['remove']:
                                                    delete_ig.append('symaccess -sid {0} delete -name {1} -type init -nop'.format(self.sid, init_child['name']))
                                                    
                                                    for login in init_child['login_list']:
                                                        remove_wwn_to_ig.append('symaccess -sid {0} remove -name {1} -type init -wwn {2}'.format(self.sid, init_child['name'], login))
                                                        
                                                        if any([w for w in self.login_cls_lst if w.wwn == login and w.remove]):
                                                            delete_login.append('symaccess -sid {0} remove -login -wwn {1} -nop'.format(self.sid, login))
                                                          
                                            delete_cig.append('symaccess -sid {0} delete -name {1} -type init -nop'.format(self.sid, view.init))
                                        
                                        else:
                                            
                                            for login in view.login_list:
                                                remove_wwn_to_ig.append('symaccess -sid {0} remove -name {1} -type init -wwn {2}'.format(self.sid, view.init, login))
                                                
                                                if any([w for w in self.login_cls_lst if w.wwn == login and w.remove]):
                                                    delete_login.append('symaccess -sid {0} remove -login -wwn {1} -nop'.format(self.sid, login))
                                                    
                                            delete_ig.append('symaccess -sid {0} delete -name {1} -type init -nop'.format(self.sid, view.init))  
                                        
            if self.lun_cls_lst:
                
                tdev_lst = [lun.id for lun in self.lun_cls_lst if lun.remove and lun.tdev]
                pdev_lst = [lun.id for lun in self.lun_cls_lst if lun.remove and not lun.tdev]
                lun_lst = tdev_lst + pdev_lst
                
                if lun_lst:
                    
                    #### MOVE DEVICE TO TEMPORARY SG ####
                    
                    if self.remove_mode == 'normal':
                        
                        if not self.sg_temp:
                            if self.array_type is 12:
                                create_sgtmp.append('symaccess -sid {0} create -name {1} -type storage'.format(self.sid, self.sg_temp_name))
                            elif self.array_type is 3:
                                create_sgtmp.append('symsg -sid {0} create {1} -slo Bronze -srp SRP_1'.format(self.sid, self.sg_temp_name))
                        
                        move_lun_to_sgtmp.append('symaccess -sid {0} add -name {1} -type stor dev {2}'.format(self.sid, self.sg_temp_name, ','.join(lun_lst)))
                    
                    #### DELETE DEVICE ####
                    
                    elif self.remove_mode == 'total':
                        
                        meta_cls_lst = [l for l in self.lun_cls_lst if l.remove and l.meta]
                        
                        dev_bound_lst = [l.id for l in self.lun_cls_lst if l.remove and l.tdev and l.bound]
                        dev_unbinding_lst = [l.id for l in self.lun_cls_lst if l.remove and l.tdev and l.unbinding]
                        dev_reclaim_lst = [l.id for l in self.lun_cls_lst if l.remove and l.tdev and l.reclaim]
                        dev_bound_not_ready_lst = [l.id for l in self.lun_cls_lst if l.remove and not l.ready and l.bound]
                        
                        dev_unbinding_all_lst = dev_unbinding_lst + dev_bound_lst
                        
                        if dev_unbinding_lst:
                            self.warning_dict[self.warning_id_incr] = 'Device(s) on Unbind in Progress [{0}]. Script Wait Unbind Completed'.format(','.join(dev_unbinding_lst))
                        
                        if dev_bound_not_ready_lst:
                            self.warning_dict[self.warning_id_incr] = 'Device(s) on Not Ready State [{0}]'.format(','.join(dev_bound_not_ready_lst))
                        
                        if dev_reclaim_lst:
                            self.warning_dict[self.warning_id_incr] = 'Device(s) on Reclaim State [{0}]. Script stop it'.format(','.join(dev_reclaim_lst))
                            reclaim_stop.append('symdev -sid {0} reclaim -stop -dev {1} -nop'.format(self.sid, ','.join(dev_reclaim_lst)))
                            
                        if dev_bound_lst:
                            if self.array_type == 12:
                                unbind_lun.append('symdev -sid {0} unbind -dev {1} -nop'.format(self.sid, ','.join(dev_bound_lst)))
                            elif self.array_type == 3:
                                free_all_lun.append('symdev -sid {0} free -all -dev {1} -nop'.format(self.sid, ','.join(dev_bound_lst)))
                                
                        if meta_cls_lst:
                            meta_member_list = []
                            
                            for meta in meta_cls_lst:
                                meta_member_list = meta_member_list + meta.meta_member
                                dissolve_meta.append('dissolve meta dev {0};'.format(meta.id))
                                
                            tdev_lst = tdev_lst + meta_member_list
                            
                        lun_all_lst = tdev_lst + pdev_lst
                        
                        for l in lun_all_lst:
                            delete_lun.append('delete dev {0};'.format(l))
                            
                        if len(delete_lun) > self.remove_max_lun:
                            self.warning_dict[self.warning_id_incr] = 'Lun(s) to delete > {0}. Script Create Several Files (symconfigure)'.format(self.remove_max_lun)
        
        #### DISPLAY COMMAND ####
        
        for mode in ['display', 'exec']:
            
            cmd_display_header(mode, self.error_dict, logger=self.logger)
            
            remove_srdf_pair(srdf_dic_lst, mode, self.sid, self.tmp_file, verbose=True, logger=self.logger, export=self.export)
            remove_clone_pair(clone_dic_lst, mode, self.sid, self.tmp_file, verbose=True, logger=self.logger, export=self.export)
            remove_bcv_pair(bcv_dic_lst, mode, self.sid, self.tmp_file, verbose=True, logger=self.logger, export=self.export)
            remove_or_pair(openr_dic_lst, mode, self.sid, self.array_id, self.tmp_file, verbose=True, logger=self.logger, export=self.export)
            
            cmd_exec_mode(delete_mv, 'Delete M.View', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(remove_sg_to_csg, 'Remove S.Group to CS.Group', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(remove_ig_to_cig, 'Remove Init to C.Init', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(delete_cig, 'Delete C.Init', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(remove_wwn_to_ig, 'Remove Logins to Init', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(delete_ig, 'Delete Init', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(delete_login, 'Delete Logins', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(remove_fast_to_sg, 'Remove F.Policy to S.Group', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(remove_lun_to_sg, 'Remove Lun to S.Group', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(delete_sg, 'Delete S.Group', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(create_sgtmp, 'Create Temp. S.Group', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(move_lun_to_sgtmp, 'Move Lun to Temp. S.Group', mode, logger=self.logger, export=self.export)
            
            if self.remove_mode == 'total' and self.lun_cls_lst and lun_lst:
                
                if mode == 'display':
                    mprint('(-) Check Lun Port(s)', tac=1)
                    
                elif mode == 'exec':
                    
                    if not self.noport_mode:
                        
                        lun_port_lst = check_lun_port(self.sid, lun_lst)
                        
                        if lun_port_lst:
                            
                            lun_port_ready_lst = list(set(lun_port_lst).difference([l.id for l in self.lun_cls_lst if l.remove and not l.ready]))
                            
                            if lun_port_ready_lst:
                                cmd_exec_mode(['symdev -sid {0} not_ready -dev {1} -nop'.format(self.sid, ','.join(lun_port_ready_lst))], 'Change Lun(s) State to Not Ready', mode, logger=self.logger, export=self.export)
                                
                            symconf_exec(
                                ['unmap dev {0} from dir ALL:ALL;'.format(l) for l in lun_port_lst],
                                'Unmap Lun(s)',
                                mode,
                                'Lun(s) to Unmap [{0} Dev] (Syntax : unmap dev <Dev> from dir ALL:ALL)'.format(len(lun_port_lst)),
                                self.sid,
                                self.tmp_file,
                                verbose=self.verbose_mode,
                                logger=self.logger,
                                export=self.export
                            )
                    
                cmd_exec_mode(reclaim_stop, 'Reclaim Stop', mode, logger=self.logger, export=self.export)
                cmd_exec_mode(unbind_lun, 'Unbind Lun(s)', mode, logger=self.logger, export=self.export)
                cmd_exec_mode(free_all_lun, 'Free Lun(s)', mode, logger=self.logger, export=self.export)
                
                if mode == 'exec' and dev_unbinding_all_lst:
                    if self.array_type == 12:
                        wait_free_unbind_lun(self.sid, dev_unbinding_all_lst, 'unbind', logger=False)
                    
                    elif self.array_type == 3:
                        wait_free_unbind_lun(self.sid, dev_unbinding_all_lst, 'free', logger=False)
                        
                symconf_exec(
                    dissolve_meta,
                    'Dissolve Meta(s)',
                    mode,
                    'Meta(s) to Dissolve [{0} Dev] (Syntax : dissolve meta dev <Dev>)'.format(len(dissolve_meta)),
                    self.sid,
                    self.tmp_file,
                    verbose=self.verbose_mode,
                    logger=self.logger,
                    export=self.export
                )
                
                delete_lun_lst = lst_splt(delete_lun, self.remove_max_lun)
                
                for y, dl in enumerate(delete_lun_lst):
                    
                    del_title = ''
                    
                    if y is 0:
                        del_title = 'Delete Lun(s)'
                        
                    if len(delete_lun_lst) > 1:
                        del_file_title = 'Lun(s) to Delete [File {0} : {1} Dev] (Syntax : delete dev <Dev>)'.format(y+1, len(dl))
                        
                    else:
                        del_file_title = 'Lun(s) to Delete [{0} Dev] (Syntax : delete dev <Dev>)'.format(len(dl))
                        
                    symconf_exec(dl, del_title, mode, del_file_title, self.sid, self.tmp_file, verbose=self.verbose_mode, logger=self.logger, export=self.export)
                    
            cmd_display_footer(mode, self.warning_dict, self.mode, logger=self.logger, start_time=self.script_start_time, nop=self.no_prompt)
            
            
            
            
