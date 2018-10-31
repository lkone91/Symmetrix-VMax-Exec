# -*- coding: utf-8 -*-

#================================================================================#
# ------------------------------- IMPORT LIBRARY ------------------------------- #
#================================================================================#

#~~~~# LOCAL LIBRARY #~~~~#

from py_vmax_lib.func_global import *
from py_vmax_lib.func_retrieve import *
from py_vmax_lib.func_display import *
from py_vmax_lib.func_check import *

#==============================================================================#
# ------------------------------- MODULE START ------------------------------- #
#==============================================================================#

class AuditMode(object):
    """ Classe : Classe du Mode Audit """
    
    def __init__(self, glob_dic, logger):
        
        for key, value in glob_dic.items():
            setattr(self, key, value)
        
        self.logger = logger
        
    def info_retrieve(self):
        """ Récupération des informations sur les Devices """
        
        self.lun_cls_lst = []
        self.sgroup_cls_lst = []
        self.view_cls_lst = []
        self.login_cls_lst = []
           
        def sgroup_phase(sgroup_list):
            self.sgroup_cls_lst = sgroup_info_retrieve(sgroup_list, self.sid, self.array_type, logger=self.logger, export=self.export)
            self.view_list = rtr_dict_list(self.sgroup_cls_lst, 'view_list', uniq=True, concat=True)
                
            if self.view_list:
                self.view_cls_lst = view_info_retrieve(self.view_list, self.sid, logger=self.logger, export=self.export)
            
        if self.select:
            dev_type = ['dev_lun', 'dev_lwwn', 'dev_sg', 'dev_wwn']
            dev_type_display = ['Lun', 'Lun UID', 'S.Group', 'Login']
            
            if self.mode is not 'audit':
                dev_type.remove('dev_wwn')
                dev_type_display.remove('Login')
            
            self.dev = select_choice(dev_type, dev_type_display, type='Device Type')
            mprint()  
            
        if self.unbind_mode:
            self.dev = 'dev_lun'
            
            self.dev_lun_arg =  [l['id'] for l in lun_lst_retrieve(self.sid, lun_type='unbound', display=True, logger=self.logger, export=self.export) if l['meta'] != 'Member']
            
            if not self.dev_lun_arg:
                mprint('No Unbind Lun on VMAX {0}'.format(self.array_id), 'err', logger=self.logger)
            
        if self.noport_mode:
            self.dev = 'dev_lun'
            
            self.dev_lun_arg =  [l['id'] for l in lun_lst_retrieve(self.sid, lun_type='noport', display=True, logger=self.logger, export=self.export) if l['meta'] != 'Member']
            
            if not self.dev_lun_arg:
                mprint('No Lun with No Port on VMAX {0}'.format(self.array_id), 'err', logger=self.logger)
            
        # Retrieve S.Group Temporary #
            
        if self.tmpsg_mode:
            
            self.logger.info('[TEMPORARY SG] WEEK > {0}'.format(self.tmpsg_mode_arg))
            
            self.dev = 'dev_sg'
            self.dev_sg = True
            self.dev_sg_arg, self.sg_all_lst, self.ig_all_lst = sgroup_tmp_retrieve(self.sid, self.array_type, self.tmpsg_mode_arg, logger=self.logger, export=self.export)
            
            if self.dev_sg_arg is 1:
                mprint('No Temporary S.Group Find Older Than {0} Week(s)'.format(self.tmpsg_mode_arg), 'inf', logger=self.logger)
                sc_exit(0, mode=self.mode, start_time=self.script_start_time, logger=self.logger)
        
        if self.dev == 'dev_lun' or self.dev == 'dev_lwwn':
            
            if self.dev == 'dev_lun':
                if self.select:
                    self.dev_lun_arg = False
                    
                if not self.unbind_mode and not self.noport_mode:
                    self.dev_lun_arg, self.lun_all_lst = lun_argument_check(self.sid, self.dev_lun_arg, logger=self.logger, export=self.export)
            
            elif self.dev == 'dev_lwwn':
                if self.select:
                    self.dev_lwwn_arg = False
                    
                self.dev_lun = True
                self.dev = 'dev_lun'
                self.dev_lun_arg, self.lun_all_lst = lun_argument_check(self.sid, self.dev_lwwn_arg, lun_type='wwn', logger=self.logger, export=self.export)
            
            if self.logger:
                self.logger.info('[LUN] Lun(s) to {0} : {1}'.format(self.mode.capitalize(), self.dev_lun_arg))
            
            self.lun_cls_lst = lun_info_retrieve(self.dev_lun_arg, self.sid, self.array_type, logger=self.logger, export=self.export)
            
            if not self.only_mode:
                
                self.sgroup_lst = rtr_dict_list(self.lun_cls_lst, 'sgroup_list', uniq=True, concat=True)
                sgroup_phase(self.sgroup_lst)
            
        elif self.dev == 'dev_sg':
            
            if self.select:
                self.dev_sg_arg = False
            
            if not self.tmpsg_mode:
                self.dev_sg_arg, self.sg_all_lst, self.ig_all_lst = sgroup_argument_check(self.sid, self.dev_sg_arg, logger=self.logger, export=self.export)
                
            self.lun_lst = sgroup_lun_lst_retrieve(self.sid, self.dev_sg_arg, export=self.export)
             
            if self.logger:
                self.logger.info('[SG] : S.Group(s) to {0} : {1} / Lun(s) : {2}'.format(self.mode.capitalize(), self.dev_sg_arg, self.lun_lst))
            
            if self.lun_lst and not self.only_mode:
                self.lun_cls_lst = lun_info_retrieve(self.lun_lst, self.sid, self.array_type, export=self.export)
                
                self.sgroup_lst = list(set(rtr_dict_list(self.lun_cls_lst, 'sgroup_list', uniq=True, concat=True) + self.dev_sg_arg))
                
                sgroup_child_list = rtr_dict_list(self.lun_cls_lst, 'sgroup_child_list', uniq=True, concat=True) 
                
                if sgroup_child_list:
                    self.dev_sg_arg = self.dev_sg_arg + sgroup_child_list
                
                sgroup_phase(self.sgroup_lst)
                    
                for s in self.sgroup_cls_lst:
                    if s.name in self.dev_sg_arg:
                        s.argument = True
                    
                self.login_lst = rtr_dict_list(self.view_cls_lst, 'login_list', uniq=True, concat=True)
                
                if self.login_lst:
                    self.login_cls_lst = login_info_retrieve(self.login_lst, self.sid, logger=self.logger, export=self.export)
            
            else:
                sgroup_phase(self.dev_sg_arg)
            
        elif self.dev == 'dev_wwn':
            
            if self.select:
                self.dev_wwn_arg = False
                
            self.dev_wwn_arg, self.login_lst = login_argument_check(self.sid, self.dev_wwn_arg, logger=self.logger, export=self.export)
            self.login_cls_lst = login_info_retrieve(self.dev_wwn_arg, self.sid, logger=self.logger, export=self.export)
            
            self.view_lst = rtr_dict_list(self.login_cls_lst, 'view_list', uniq=True, concat=True)
            
            if self.view_lst:
                self.view_cls_lst = view_info_retrieve(self.view_lst, self.sid, logger=self.logger, export=self.export)
                self.lun_lst = rtr_dict_list(self.view_cls_lst, 'lun_list', uniq=True, concat=True)
                self.lun_cls_lst = lun_info_retrieve(self.lun_lst, self.sid, self.array_type, logger=self.logger)
                self.sgroup_lst = rtr_dict_list(self.lun_cls_lst, 'sgroup_list', uniq=True, concat=True)
                self.sgroup_cls_lst = sgroup_info_retrieve(self.sgroup_lst, self.sid, self.array_type, logger=self.logger, export=self.export)
            
    def info_display(self):
        
        if self.login_cls_lst:
            login_display(self.sid, self.login_cls_lst, debug=self.debug_mode)
        
        if self.sgroup_cls_lst:
            sgroup_display(self.sid, self.sgroup_cls_lst, self.view_cls_lst, self.array_type, debug=self.debug_mode)
        
        if self.lun_cls_lst:
            lun_display(self.sid, self.lun_cls_lst, self.array_type, wwn_type=self.dev_lwwn, war_type='Unbind/Reclaim/N.Ready', size_display=self.size_display, debug=self.debug_mode, verbose=self.verbose_mode)
    
    @property
    def warning_id_incr(self):
        self.warning_id += 1
        return self.warning_id
        
    @property
    def error_id_incr(self):
        self.error_id += 1
        return self.error_id
