# -*- coding: utf-8 -*-

#================================================================================#
# ------------------------------- IMPORT LIBRARY ------------------------------- #
#================================================================================#

#~~~~# LOCAL LIBRARY #~~~~#

from py_vmax_lib.class_audit import AuditMode

from py_vmax_lib.func_global import *
from py_vmax_lib.func_execution import *
from py_vmax_lib.func_display import *
from py_vmax_lib.func_retrieve import sg_ig_lst_retrieve
from py_vmax_lib.func_check import exist_check

#==============================================================================#
# ------------------------------- MODULE START ------------------------------- #
#==============================================================================#

class ModifyMode(AuditMode):
    """Remove Mode class"""
    
    def __init__(self, glob_dic, logger):
        AuditMode.__init__(self, glob_dic, logger)
        
        if self.dev == 'dev_lun':
            self.only_mode = True
        
        if self.select:
            self.flag_mode = True
            
            self.flag_mode_arg = select_choice(['BCV', 'SRDF'], type='Flag to Modify')
            
    def mode_check(self):
        
        if self.flag_mode:
            
            self.flag_mode_arg = self.flag_mode_arg.upper()
            
            if not self.lun_cls_lst:
                mprint('No Lun to Modify Find', 'err', logger=self.logger)
            
            self.lun_to_modify_lst = []
            
            for lun in self.lun_cls_lst:
                
                if self.flag_mode_arg == 'BCV':
                    if not lun.bcv_flag:
                        lun.info = True
                        self.lun_to_modify_lst.append(lun.id)
                        
                elif self.flag_mode_arg == 'SRDF':
                    if not lun.srdf_cap:
                        lun.info = True
                        self.lun_to_modify_lst.append(lun.id)
            
            AuditMode.info_display(self)
            
            if not self.lun_to_modify_lst:
                mprint('All Luns have Already {0} Flag'.format(self.flag_mode_arg), 'err', logger=self.logger)
                
            else:
                mprint('{0} : {1} Lun(s) with No {2} Flag'.format(color_str('  ', 'rev'), len(self.lun_to_modify_lst), self.flag_mode_arg), tbc=1)
                
                if self.logger:
                    self.logger.info('[DEV:FLAG] {0} Lun(s) Find with No {1} Flag'.format(len(self.lun_to_modify_lst), self.flag_mode_arg))
        
        
    def mode_exec(self):
        
        if self.flag_mode:
            if self.flag_mode_arg == 'BCV':
                change_flag = ['convert dev {0} to BCV+TDEV;'.format(l) for l in self.lun_to_modify_lst]
                syntax_type = 'convert dev <Dev> to BCV+TDEV'
                
            elif self.flag_mode_arg == 'SRDF':
                change_flag = ['set dev {0} attribute=dyn_rdf;'.format(l) for l in self.lun_to_modify_lst]
                syntax_type = 'set dev <Dev> attribute=dyn_rdf'
                
        
        
        for mode in ['display', 'exec']:
            
            cmd_display_header(mode, self.error_dict, logger=self.logger)  
            
            if self.flag_mode:
                symconf_exec(
                    change_flag,
                    'Change {0} Flag'.format(self.flag_mode_arg),
                    mode,
                    'Lun(s) to Modify [{0} Dev] (Syntax : {1})'.format(len(change_flag), syntax_type),
                    self.sid,
                    self.tmp_file,
                    verbose=self.verbose_mode,
                    logger=self.logger,
                    export=self.export
                )
            
            cmd_display_footer(mode, self.warning_dict, self.mode, logger=self.logger, start_time=self.script_start_time, nop=self.no_prompt)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        