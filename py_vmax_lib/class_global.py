#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

#================================================================================#
# ------------------------------- IMPORT LIBRARY ------------------------------- #
#================================================================================#

#~~~~# PYTHON LIBRARY #~~~~#

#~~~~# LOCAL LIBRARY #~~~~#

from py_vmax_lib.func_global import *
from py_vmax_lib.func_check import *
from py_vmax_lib.func_display import opts_dic_lst, help_display

#==============================================================================#
# ------------------------------- MODULE START ------------------------------- #
#==============================================================================#


class GlobalMode(object):
    """Global Mode class"""
    
    def __init__(self, tmp_path, conf_path):
        
        self.script_start_time = time.time()
        self.tmp_path = tmp_path
        self.conf_path = conf_path
        
        self.warning_dict = {}
        self.error_dict = {}
        self.warning_id = 0
        self.error_id = 0
        
        self.array_type = False
        
        opt_dic_lst = opt_treat(opts_dic_lst)
        
        for sc_opt in opt_dic_lst:
            exec("self.{0} = False".format(sc_opt['type']))
            if sc_opt['cat']:
                exec("self.{0} = False".format(sc_opt['cat']))
        
        for sc_opt in opt_dic_lst:
            if sc_opt['default']:
                exec("self.{0}_arg = {1}".format(sc_opt['name'], sc_opt['default'],))
            else:
                exec("self.{0} = False".format(sc_opt['name']))
            
            if sc_opt['actv']:
                exec("self.{0} = True".format(sc_opt['type']))
                exec("self.{0} = True".format(sc_opt['name']))
                
                if sc_opt['arg']:
                    if sc_opt['a_sep']:
                        exec("self.{0}_arg = {1}".format(sc_opt['name'], sc_opt['args'].split(sc_opt['a_sep'])))
                    else:
                        exec("self.{0}_arg = '{1}'".format(sc_opt['name'], sc_opt['args']))
                    
                if sc_opt['cat']:
                    if not eval('self.{0}'.format(sc_opt['cat'])):
                        exec("self.{0} = '{1}'".format(sc_opt['cat'], sc_opt['name']))
                    else:
                        mprint('Bad Options. Only 1 [{0}]'.format(sc_opt['cat'].upper()), 'arg_err')
                        
        if self.sid:
            self.sid = self.sid_arg
            del self.sid_arg
            
    def argument_check(self):
        
        self.array_type = False
        self.size_display = self.size_display_arg.lower()
        
        ### Récupération Information Baies (JSON) ###
                
        self.array_dic_lst = list_array_file(self.conf_path)        
        
        ### Affichage de l'Aide (-h) ###
        
        if self.hp:
            if self.cr or self.mi or self.rm: mprint('Help Option must be Witout Anoher Argument', 'arg_err')
            
            help_display(opts_dic_lst, self.array_dic_lst, self.verbose_mode)
            sc_exit(0, no_end=True)
            
        ### Selection du Mode (Mode Select) ###
        
        if self.sl:
            if self.gl or self.cr or self.mi or self.rm: mprint('Select must be Witout Anoher Argument', 'arg_err')
            
            mprint('{0} Mode - Start'.format('Select'), 's1', tac=1, tbc=1)
            
            self.mode = select_choice(['audit', 'create', 'remove', 'modify', 'migrate'], ['Audit Mode', 'Create Mode', 'Remove Mode', 'Modify Mode', 'Migrate Mode'], type='Mode')
            
        ### Selection de la Baie (Mode Select) ###
        
        if self.sl:
            self.sid, self.array_id, self.array_type, self.one_view, self.export = array_id_check(self.array_dic_lst)
            
        ### Vérification des Arguments ###
        
        if not self.sid:
            mprint('SID Array Needed', 'arg_err')
            
        if len(self.sid) < 3:
            mprint('3 Digit Min for SID Array', 'arg_err')
            
        if not self.sl:
            self.sid, self.array_id, self.array_type, self.one_view, self.export = array_id_check(self.array_dic_lst, self.sid)
            
        if not self.mode:
            mprint('Mode Needed [Audit|Create|Remove|Modify]', 'arg_err')
        
        try:
            self.node = int(self.node_arg)
        except:
            mprint('Bad Value for [-node] Option (int)', 'arg_err')
        
        if not self.sl:
            
            if self.mode == 'audit':
                
                if not self.dev:
                    mprint('Device to Audit Necessary [Lun|L.UID|SG|Login|Unb.Lun]', 'arg_err')
                    
                if self.rm or self.mi or self.cr:
                    mprint('Bad Options', 'arg_err')
                
            elif self.mode == 'remove':
                
                if not self.dev:
                    mprint('Device to Remove Necessary [Lun|L.UID|SG|Unb.Lun]', 'arg_err')
                    
                if self.dev == 'dev_wwn':
                    mprint('Remove by Logins not available', 'arg_err')
                    
                if self.rmv_repli and self.rmv_total:
                    mprint('Total and Repli Option can\'t work Together', 'arg_err')
                    
                if self.ad or self.cr:
                    mprint('Bad Options', 'arg_err')
                    
                if self.unbind_mode or self.noport_mode:
                    self.rmv_total = True
                
                if self.tmpsg_mode:
                
                    if self.rmv_repli:
                        mprint('Bad Options [-repli]', 'arg_err')
                        
                    self.rmv_total = True
                    
            elif self.mode == 'modify':
                if not self.dev:
                    mprint('Device to Modify Necessary [Lun|SG]', 'arg_err')
                    
                if self.dev == 'dev_wwn':
                    mprint('Modify by Logins not available', 'arg_err')
                    
                if self.ad or self.cr or self.mi or self.rm:
                    mprint('Bad Options', 'arg_err')
            
                if not self.flag_mode and not self.rename_mode:
                    mprint('Choose Modes (Flag|Rename)', 'arg_err')
                    
                if self.flag_mode:
                    
                    if not re.search('^(BCV|SRDF)$', self.flag_mode_arg.upper()):
                        mprint('Bad Flag to Modify [BCV|SRDF]', 'arg_err')
                
            elif self.mode == 'create':
                if self.rm or self.ad or self.mi or not self.cr:
                    mprint('Bad Options', 'arg_err')
                    
                if not self.new_name:
                    if self.new_sg or self.new_view:
                        mprint('Enter a New Name [-name] with New MV or/and New SG', 'arg_err')
                        
                if self.new_sg and self.dev_sg:
                    mprint('You can create a New SG or a Existing SG. Not both', 'arg_err')
                    
                if not self.new_sg and not self.dev_sg:
                    mprint('Enter Existing or New SG with Create Mode', 'arg_err')
                    
                if self.node > 1 and not self.new_view:
                    mprint('New Cluster Option available only with New MV Option', 'arg_err')
                    
                if not self.new_lun:
                    
                    if self.new_sg:
                        mprint('Script create SG with Lun(s)', 'arg_err')
                        
                    if not self.new_view and self.dev_sg:
                        mprint('Script create SG with Lun(s)', 'arg_err')
                        
                if self.new_view and len(self.new_view_arg) != self.node:
                    mprint('Bad Number of Node ({0}). Please Change Number of Node with -node Option'.format(self.node), 'arg_err')
               
            elif self.mode == 'migrate':
                
                if self.rm or self.ad or self.cr:
                    mprint('Bad Options', 'arg_err')
                    
                if not self.mig_type:
                    mprint('Type of Migration Necessary [VLUN|SRDF|CLONE]', 'arg_err')
                
                self.mig_type = self.mig_type_arg.upper()
                
                if self.mig_type == 'VLUN':
                    
                    if self.array_type is 3:
                        mprint('VLUN Migration not Available with VMAX-3', 'arg_err')
                        
                    # if self.dev != 'dev_sg':
                        # mprint('VLUN Migration Available only with S.Group', 'arg_err')
                    
                    if self.dev_sg and len(self.dev_sg_arg) > 1:
                        mprint('VLUN Migration Available only with One S.Group', 'arg_err')
                    
                else:
                    
                    if not self.dev:
                        mprint('Device to Migrate Necessary [Lun|S.Group]', 'arg_err')
                        
                    if self.dev == 'dev_wwn':
                        mprint('Migrate by Logins not available', 'arg_err')
                    
                    if not self.rmt_new_sg and not self.rmt_lun and not self.rmt_sg:
                        mprint('Select Remote Lun(s) [-rlun], Remote S.Group [-rsg] or a New Remote SG Name [-rnsg]', 'arg_err')
                        
                    if self.rmt_new_sg and not self.new_name:
                        mprint('Enter a New Name [-name] with New Remote SG', 'arg_err')
                        
                    if self.rmt_new_sg and self.rmt_sg:
                        mprint('Select a Remote S.Group or a New Remote SG Name, not both', 'arg_err')
                        
                    if self.rmt_sg and self.rmt_lun:
                        mprint('Select Remote Lun(s) or a Remote S.Group, not both', 'arg_err')
                        
                    if self.rmt_new_sg and self.rmt_lun:
                        mprint('Select Remote Lun(s) or a New Remote SG Name, not both', 'arg_err')
                
                    if self.mig_type == 'SRDF':
                        
                        if not self.rmt_sid:
                            mprint('Remote SID Bay Necessary for SRDF Migration', 'arg_err')
                            
                        self.rmt_sid, self.rmt_array_id, self.rmt_array_type, self.rmt_one_view, self.rmt_export = array_id_check(self.array_dic_lst, self.rmt_sid_arg, mode='Remote ')
                    
                    elif self.mig_type == 'CLONE':
                        
                        if self.rmt_sid:
                            mprint('Remote SID Not Available for Clone Migration', 'arg_err')
                            
                        self.rmt_sid, self.rmt_array_id, self.rmt_array_type, self.rmt_one_view, self.rmt_export = array_id_check(self.array_dic_lst, self.sid)
                
            if not re.search('^(mb|cyl|auto)$', self.size_display):
                mprint('Bad Size with -size Option', 'arg_err')
                
        self.pid = os.getpid()
        self.user = user_retrieve()
        
        self.tmp_file = '{0}/file_temp_vmax_py_{1}.tmp'.format(self.tmp_path, self.pid)
        
        for a in ['hp', 'sl', 'rm', 'cr', 'md', 'gl', 'ad', 'node_arg', 'size_display_arg']:
            exec('del self.{0}'.format(a))

