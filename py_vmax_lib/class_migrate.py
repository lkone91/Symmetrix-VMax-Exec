# -*- coding: utf-8 -*-

#================================================================================#
# ------------------------------- IMPORT LIBRARY ------------------------------- #
#================================================================================#

#~~~~# LOCAL LIBRARY #~~~~#

from py_vmax_lib.class_audit import AuditMode
from py_vmax_lib.class_create import CreateMode

from py_vmax_lib.func_global import *
from py_vmax_lib.func_execution import *
from py_vmax_lib.func_display import *
from py_vmax_lib.func_retrieve import *
from py_vmax_lib.func_check import *

#==============================================================================#
# ------------------------------- MODULE START ------------------------------- #
#==============================================================================#

class MigrateMode(AuditMode):
    """ Migrate Mode class """
    
    def __init__(self, glob_dic, logger):
        AuditMode.__init__(self, glob_dic, logger)
        
    def info_retrieve(self):
        
        # Selection des Options en Mode Select #
        
        if self.select:
            
            mig_type_choice_lst = ['CLONE', 'SRDF', 'VLUN']
            mig_type_choice_display_lst = ['Clone Migration', 'SRDF Migration', 'VLUN Migration']
            
            if self.array_type is 3:
                mig_type_choice_lst.remove('VLUN')
                mig_type_choice_display_lst.remove('VLUN Migration')
            
            self.mig_type = select_choice(mig_type_choice_lst, mig_type_choice_display_lst, type='Migration Type')
            
            if self.mig_type != 'VLUN':
                
                if self.mig_type == 'SRDF':
                    self.rmt_sid, self.rmt_array_id, self.rmt_array_type, self.rmt_one_view, self.rmt_export = array_id_check(self.array_dic_lst, mode='Remote ')
                
                elif self.mig_type == 'CLONE':
                    self.rmt_sid, self.rmt_array_id, self.rmt_array_type, self.rmt_one_view, self.rmt_export = self.sid, self.array_id, self.array_type, self.one_view, self.export
                
                self.dev = select_choice(['dev_lun', 'dev_sg'], ['Lun', 'S.Group'], type='Device Type to Migrate')
                self.rmt_mode = select_choice(
                    ['exist', 'exist_sg', 'new_sg'],
                    ['Remote Lun(s)', 'Remote S.Group [Lun(s) Creation]', 'Remote New S.Group [Lun(s) + S.Group Creation]'],
                    type='Remote Target Type'
                )
                
                if self.rmt_mode == 'exist':
                    self.rmt_lun = True
                    
                elif self.rmt_mode == 'exist_sg':
                    self.rmt_sg = True
                
                elif self.rmt_mode == 'new_sg':
                    self.rmt_new_sg = True
                
            else:
                self.dev = select_choice(['dev_lun', 'dev_sg'], ['Lun', 'S.Group'], type='Device Type to Migrate')
                
            mprint()
            
        if self.dev == 'dev_lun':
            self.lun_dic_lst = lun_lst_retrieve(self.sid, export=self.export)
            
        if self.rmt_lun:
            self.rmt_lun_dic_lst = lun_lst_retrieve(self.rmt_sid, export=self.rmt_export)
            
        if self.dev == 'dev_sg':
            
            if self.select:
                self.dev_sg_arg = False
            
            self.dev_sg_arg, self.sg_all_lst, self.ig_all_lst = sgroup_argument_check(self.sid, self.dev_sg_arg, sg_type='Local S.Group', logger=self.logger, export=self.export)
            self.lun_lst = sgroup_lun_lst_retrieve(self.sid, self.dev_sg_arg, export=self.export)
            
            if self.lun_lst:
                if self.logger:
                    self.logger.info('[SG] : S.Group(s) to {0} : {1} / Lun(s) : {2}'.format(self.mode.capitalize(), self.dev_sg_arg, self.lun_lst))
                
            else:
                mprint('S.Group {0} have No Lun'.format(self.dev_sg_arg), 'err', logger=self.logger)
            
            
        elif self.dev == 'dev_lun':
            
            if self.select:
                self.dev_lun_arg = False
                
            self.lun_lst = lun_argument_check(self.sid, self.dev_lun_arg, tit='Local Lun(s) (B:{0})'.format(self.sid), dic_lst=self.lun_dic_lst, logger=self.logger, export=self.export)
            
            if self.logger:
                self.logger.info('[LUN] Local Lun(s) to {0} : {1}'.format(self.mode.capitalize(), self.lun_lst))
                
        if self.rmt_lun:
           
            if self.select:
                self.rmt_lun_arg = False
                
            self.rmt_lun_arg = lun_argument_check(self.rmt_sid, self.rmt_lun_arg, tit='Remote Lun(s) (B:{0})'.format(self.rmt_sid), dic_lst=self.rmt_lun_dic_lst, tbc=0, logger=self.logger, export=self.rmt_export)
            
            if self.logger:
                self.logger.info('[LUN] Target Lun(s) : {0}'.format(self.rmt_lun_arg))
            
        self.lun_cls_lst = lun_info_retrieve(self.lun_lst, self.sid, self.array_type, logger=self.logger, export=self.export)
        
        if self.rmt_lun:
            self.rmt_lun_cls_lst = lun_info_retrieve(self.rmt_lun_arg, self.rmt_sid, self.rmt_array_type, logger=self.logger, export=self.rmt_export)
          
        if self.rmt_sg:
            if self.select:                                                                                                                                  
                self.rmt_sg_arg = False                                                                                                                          
            
            self.rmt_sg_arg, self.rmt_sg_all_lst, self.rmt_ig_all_lst = sgroup_argument_check(self.rmt_sid, self.rmt_sg_arg, sg_type='Remote S.Group', logger=self.logger, export=self.rmt_export)    
            
        self.lun_total_size_gb = int(sum(self.lun_cls_lst)/1024)
        self.lun_total_consum_size_gb = int(sum([l.allocate for l in self.lun_cls_lst])/1024)
            
        # Logger Information #
        
        if self.mig_type == 'SRDF':
            self.logger.info('[MIG_TYPE:SRDF] : SOURCE SID : {0} | TARGET SID : {1}'.format(self.sid, self.rmt_sid))
            
        elif self.mig_type == 'VLUN':
            
            if self.dev_sg:
                self.logger.info('[MIG_TYPE:VLUN] : SGROUP : {0}'.format(self.dev_sg_arg))
            elif self.dev_lun:
                self.logger.info('[MIG_TYPE:VLUN] : LUN(S) : {0}'.format(self.dev_lun_arg))
            
            self.sgroup_lst = rtr_dict_list(self.lun_cls_lst, 'sgroup_list', uniq=True, concat=True)
            self.sgroup_cls_lst = sgroup_info_retrieve(self.sgroup_lst, self.sid, self.array_type, logger=self.logger, export=self.export)
            
            self.fast_cls_lst = fast_retrieving(self.sid, logger=self.logger, export=self.export)
            self.pool_cls_lst = pool_retrieving(self.sid, lun_tsize=self.lun_total_size_gb, lun_consum_tsize=self.lun_total_consum_size_gb, logger=self.logger, export=self.export)
            
            silo_info_retrieve(self.pool_cls_lst, self.fast_cls_lst)
            
    def mode_check(self):
        
        if self.mig_type != 'VLUN':
            
            self.lun_by_type_lst, lun_by_type_conv_lst = lun_by_type_migrate_fmt(self.lun_cls_lst, self.array_type, self.rmt_array_type)
            
            if self.array_type is 3 and self.rmt_array_type is 12:
                mprint('Migratation to VMAX-2 from VMAX-2 not Available', 'err', logger=self.logger)
                
            # Verif Warning Existant (Source) #
            
            if any([l.warning for l in self.lun_cls_lst]):
                lun_display(self.sid, self.lun_cls_lst, self.array_type, war_type='Unbind/Reclaim/N.Ready', word=' [Local]', size_display=self.size_display, debug=self.debug_mode)
                mprint('Source Lun(s) Not Valid', 'err', logger=self.logger)
                
            # Verif GK Existant (Source) #
            
            if gate_keep_check(self.lun_cls_lst):
                self.warning_dict[self.warning_id_incr] = 'Gate Keeper Detected on Source Lun(s). Script will not Take Them'
                
            if not self.lun_by_type_lst:
                lun_display(self.sid, self.lun_cls_lst, self.array_type, err_type='Gate Keeper', word=' [Local]', size_display=self.size_display, debug=self.debug_mode)
                mprint('Source Lun(s) Not Valid', 'err', logger=self.logger)
            
            self.local_lun_id_by_size = [l.id for l in sorted(self.lun_cls_lst, key=attrgetter('size', 'type'), reverse=True) if not l.gkeeper]
            
            # Verif SRDF Existant (Source) #
            
            lun_with_srdf_lst, r1_check, r2_check = lun_with_srdf_check(self.lun_cls_lst)
            
            if lun_with_srdf_lst:
                self.warning_dict[self.warning_id_incr] = 'Source Lun(s) {0} with Already SRDF Session'.format(lun_with_srdf_lst)
                
                if r2_check and self.mig_type == 'SRDF':
                    self.error_dict[self.error_id_incr] = 'Source Lun(s) Detected on R2'
                
            if self.mig_type == 'SRDF':
                
                # Verif SRDF Capable Existant (Source) #
                
                self.lun_with_no_srdf_flag = [l.id for l in self.lun_cls_lst if not l.gkeeper and not l.srdf_cap]
                
                if self.lun_with_no_srdf_flag:
                    self.warning_dict[self.warning_id_incr] = 'Source Lun(s) {0} with No SRDF Flag. Script Add it'.format(self.lun_with_no_srdf_flag)
                   
                # Verif RA Group #
                
                self.ra_cls_lst = ra_group_retrieve(self.array_id, self.rmt_array_id, logger=self.logger, export=self.export)
                
                if self.ra_cls_lst.error:
                    sc_exit(1, logger=self.logger)
            
            
            if self.rmt_lun:
                
                self.logger.info('[LUN_TGT] : Target Lun(s) : {0}'.format(self.rmt_lun_arg))
                
                self.rmt_lun_by_type_lst, rmt_lun_by_type_conv_lst = lun_by_type_migrate_fmt(self.rmt_lun_cls_lst, self.rmt_array_type, self.array_type)
                
                # Verif Warning Existant (Cible) #
                
                if any([l.warning for l in self.rmt_lun_cls_lst]):
                    lun_display(self.sid, self.rmt_lun_cls_lst, self.rmt_array_type, war_type='Unbind/Reclaim/N.Ready', size_display=self.size_display, word=' [Remote]', debug=self.debug_mode)
                    mprint('Target Lun(s) Not Valid', 'err', logger=self.logger)
                    
                # Verif GK Existant (Cible) #
                
                if gate_keep_check(self.rmt_lun_cls_lst):
                    self.warning_dict[self.warning_id_incr] = 'Gate Keeper Detected on Target Lun(s). Script will not Take Them'
                    
                if not self.rmt_lun_by_type_lst:
                    mprint('Target Lun(s) Not Valid')
                
                self.rmt_lun_id_by_size = [l.id for l in sorted(self.rmt_lun_cls_lst, key=attrgetter('size', 'type'), reverse=True) if not l.gkeeper]
                
                # Verif correspondance entre Lun Soure et Cible
                
                if len(self.lun_by_type_lst) != len(self.rmt_lun_by_type_lst):
                    mprint('Bad Count of Lun(s) Between Source and Target', 'err')
                
                if lun_by_type_conv_lst != rmt_lun_by_type_conv_lst:
                    self.error_dict[self.error_id_incr] = 'Source and Target Lun(s) Mismatch'
                    
                # Verif SRDF Existant (Cible) #
                    
                rmt_lun_with_srdf_lst, r1_check, r2_check = lun_with_srdf_check(self.rmt_lun_cls_lst)
                    
                if rmt_lun_with_srdf_lst:    
                    self.error_dict[self.error_id_incr] = 'Target Lun(s) {0} with Already SRDF Session'.format(rmt_lun_with_srdf_lst)
                   
                if self.mig_type == 'SRDF':
                   
                    # Verif SRDF Capable Existant (Source) #
                    
                    self.rmt_lun_with_no_srdf_flag = [l.id for l in self.rmt_lun_cls_lst if not l.gkeeper and not l.srdf_cap]
                    
                    if self.rmt_lun_with_no_srdf_flag:
                        self.warning_dict[self.warning_id_incr] = 'Target Lun(s) {0} with No SRDF Flag. Script Add it'.format(self.rmt_lun_with_no_srdf_flag)
                   
                # Verif Espace Alloue sur Lun Cible #
                   
                rmt_lun_allocate_lst = [l.id for l in self.rmt_lun_cls_lst if l.allocate > 0]
                
                if rmt_lun_allocate_lst:
                    self.warning_dict[self.warning_id_incr] = 'Target Lun(s) {0} not empty'.format(rmt_lun_allocate_lst)
                
            else:
                
                # Instanciation de la Classe CreateMode avec en argument un dictionnaire comportant les nouvelles valeurs #
                
                dic_mig = dict(self.__dict__)
                
                dic_mig['select'] = False
                dic_mig['no_prompt'] = self.no_prompt
                dic_mig['export'] = self.rmt_export
                dic_mig['array_id'] = self.rmt_array_id
                dic_mig['sid'] = self.rmt_sid
                dic_mig['array_type'] = self.rmt_array_type
                dic_mig['one_view'] = self.rmt_one_view
                dic_mig['new_lun'] = True
                dic_mig['new_lun_arg'] = self.lun_by_type_lst
                dic_mig['lun_total_size_gb'] = self.lun_total_size_gb
                dic_mig['lun_total_consum_size_gb'] = self.lun_total_consum_size_gb
                
                if self.rmt_new_sg:
                    dic_mig['new_sg'] = True
                    dic_mig['dev_sg'] = False
                    
                elif self.rmt_sg:
                    dic_mig['dev_sg'] = True
                    dic_mig['dev_sg_arg'] = self.rmt_sg_arg
                    dic_mig['sg_all_lst'] = self.rmt_sg_all_lst
                    dic_mig['ig_all_lst'] = self.rmt_ig_all_lst
                    
                self.rmt_create = CreateMode(dic_mig, self.logger, mig_mode=True)
                self.rmt_create.mode_check()
                self.rmt_create.info_retrieve()
                
                
        else: # Migration VLUN #
            
            vlun_check = 0
            
            # Recuperation Session existante #
            
            vlun_session_lst, vlun_device_lst = vlun_all_vol_session_retrieve(self.sid, logger=self.logger)
            
            # Check FP (Mode SG) #
            
            if self.dev_sg:
                if any(not s.fast for s in self.sgroup_cls_lst):
                    self.warning_dict[self.warning_id_incr] = 'S.Group have No Fast Policy'
            
            # Check FP (Mode Lun) #
            
            if self.dev_lun:
                if any(s.fast for s in self.sgroup_cls_lst):
                    self.error_dict[self.error_id_incr] = 'VLUN Migration with Lun not Available on S.Group with Fast Policy. Please Remove FP and Retry'
                    vlun_check = 1
                    
            # Check Pool #
            
            if any(not l.bound for l in self.lun_cls_lst):
                self.error_dict[self.error_id_incr] = 'Lun(s) with No Pool'
                vlun_check = 1
                
            # Check Session existante #
                
            vol_with_session_check = 0
                
            for l in self.lun_cls_lst:
                if l.id in vlun_device_lst:
                    vol_with_session_check = 1
                    vlun_check = 1
                    l.error = True
                    
            if vol_with_session_check is 1: 
                self.error_dict[self.error_id_incr] = 'Lun(s) With Active Migration Session'
            
            if self.sgroup_cls_lst:
                sgroup_display(self.sid, self.sgroup_cls_lst, [], self.array_type, display_view_info=False, debug=self.debug_mode)
            
            lun_display(self.sid, self.lun_cls_lst, self.array_type, size_display=self.size_display, err_type='Lun(s) With Active VLUN Session', debug=self.debug_mode)
            
            if vlun_check is 0:
            
                # Passage du Flag Display sur les Pools Actuels et Suppression du Flag d'erreur/warning (si present) #
                
                lun_pool_lst = rtr_dict_list(self.lun_cls_lst, 'pool_name', uniq=True)
                
                for p in self.pool_cls_lst:
                    if p.name in lun_pool_lst:
                        p.display = True
                        p.error = False
                        p.warning = False
                        p.subs_prc_aft_lun_add_fmt = '---'
                        p.prc_aft_lun_add_fmt = '---'
                        
                pool_display(self.sid, self.pool_cls_lst, self.lun_total_size_gb, self.lun_total_consum_size_gb, mode_migrate=True, debug=self.debug_mode)
                
                av_pool_lst = sorted([p for p in self.pool_cls_lst if not p.error and not p.display], key=attrgetter('warning'))
            
                if av_pool_lst:
                    
                    # Selection du Nv Pool #
                    
                    pool_list = [p.name for p in av_pool_lst]
                    pool_list_display = []
                    
                    for p in av_pool_lst:
                        if p.warning:
                            pool_list_display.append(color_str(' {0} '.format(p.name), 'yel'))
                        else:
                            pool_list_display.append(p.name)
                            
                    pool_default = sorted(av_pool_lst, key=attrgetter('subs_prc_aft_lun_add', 'used_prc'))[0].name
                    self.pool_name = select_choice(pool_list, pool_list_display, type='Target Pool', default=pool_default, display_orginal_lst=True)
                    
                    # Selection de la F.Policy du Nv S.Group #
                    
                    self.fast_name = False
                    
                    if self.dev_sg:
                    
                        if not any(l.sgroup_count != 1 for l in self.lun_cls_lst):
                        
                            fast_lst = [f for f in self.fast_cls_lst if self.pool_name in f.pool_list]
                            
                            try:
                                fast_default = [f.name for f in fast_lst if 'Classe2' in f.name][0]
                            except IndexError:
                                fast_default = sorted(fast_lst, key=attrgetter('sg_count'), reverse=True)[0].name
                            
                            fast_choice = select_choice(sorted([f.name for f in fast_lst]), type='Target F.Policy', default=fast_default)
                            self.fast_name = fast_choice
                        
                        else:
                            self.warning_dict[self.warning_id_incr] = 'Lun(s) with several S.Group [No F.Policy Add After Migrate]'
                    
                else:
                    mprint('No Pool Available for this Size : {0} [Consum:{1}]'.format(size_conv(self.lun_total_size_gb, 'GB'), size_conv(self.lun_total_consum_size_gb, 'GB')), 'err')
                
                
    def info_display(self):
        
        if self.mig_type == 'SRDF':
            
            ra_group_display(self.sid, [self.ra_cls_lst], debug=self.debug_mode)
            
            lun_display(self.sid, self.lun_cls_lst, self.array_type, war_type='SRDF Session in Progress', word=' [Local]', size_display=self.size_display, debug=self.debug_mode)
            
            if self.rmt_lun:
                lun_display(self.rmt_sid, self.rmt_lun_cls_lst, self.rmt_array_type, war_type='SRDF Session in Progress', word=' [Remote]', size_display=self.size_display, debug=self.debug_mode)
                
                
        elif self.mig_type == 'CLONE':
            
            lun_display(self.sid, self.lun_cls_lst, self.array_type, war_type='SRDF Session in Progress', word=' [Local]', size_display=self.size_display, debug=self.debug_mode)
            
            if self.rmt_lun:
                lun_display(self.rmt_sid, self.rmt_lun_cls_lst, self.rmt_array_type, war_type='SRDF Session in Progress', word=' [Remote]', size_display=self.size_display, debug=self.debug_mode)
            
            
    def mode_exec(self, mode_type = ['display', 'exec']):
        
        change_flag = []
        rmt_change_flag = []
        add_fast_to_sg = []
        
        for mode in mode_type:
            
            if self.mig_type != 'VLUN':
                
                if self.rmt_new_sg or self.rmt_sg:
                    
                    self.rmt_create.mode_exec(mode_type = [mode])
                    
                    if mode == 'display':
                        migrate_lun = ['{0} [New Dev {1}]'.format(l, str(c+1).zfill(3), self.rmt_sid) for c, l in enumerate(self.local_lun_id_by_size)]
                        
                    elif mode == 'exec':
                        self.rmt_new_lun_cls_lst = lun_info_retrieve(self.rmt_create.new_lun_lst, self.rmt_sid, self.rmt_array_type, logger=self.logger, export=self.rmt_export)
                        lun_display(self.rmt_sid, self.rmt_new_lun_cls_lst, self.rmt_array_type, word=' [Remote]', size_display=self.size_display, debug=self.debug_mode)
                        
                        mprint()
                        
                        self.rmt_lun_id_by_size = [l.id for l in sorted(self.rmt_new_lun_cls_lst, key=attrgetter('size', 'type'), reverse=True)]
                        migrate_lun = ['{0} {1}'.format(l, lr) for l, lr in zip(self.local_lun_id_by_size, self.rmt_lun_id_by_size)]
                        
                    
                elif self.rmt_lun:
                    cmd_display_header(mode, self.error_dict, logger=self.logger)
                    
                    if self.mig_type == 'SRDF' and self.rmt_lun_with_no_srdf_flag:
                        rmt_change_flag = ['set dev {0} attribute=dyn_rdf;'.format(l) for l in self.rmt_lun_with_no_srdf_flag]
                        
                    migrate_lun = ['{0} {1}'.format(l, lr) for l, lr in zip(self.local_lun_id_by_size, self.rmt_lun_id_by_size)]
                
                if self.mig_type == 'SRDF':
                    if self.lun_with_no_srdf_flag:
                        change_flag = ['set dev {0} attribute=dyn_rdf;'.format(l) for l in self.lun_with_no_srdf_flag]
                    
                    symconf_exec(
                        change_flag,
                        '[Local] Change SRDF Flag',
                        mode,
                        'Lun(s) to Modify [{0} Dev] (Syntax : set dev <Dev> attribute=dyn_rdf)'.format(len(change_flag)),
                        self.sid,
                        self.tmp_file,
                        verbose=self.verbose_mode,
                        logger=self.logger,
                        export=self.export
                    )
                    
                    symconf_exec(rmt_change_flag, '[Remote] Change SRDF Flag', mode, 'Lun(s) to Modify', self.rmt_sid, self.tmp_file, verbose=self.verbose_mode, logger=self.logger, export=self.rmt_export)
                    create_srdf_pair(migrate_lun, mode, self.sid, self.tmp_file, self.rmt_sid, self.ra_cls_lst.ra_group_num, verbose=True, logger=self.logger, export=self.export)
                    
                elif self.mig_type == 'CLONE':
                    create_clone_pair(migrate_lun, mode, self.sid, self.tmp_file, verbose=True, logger=self.logger, export=self.export)
                    
            else: # Migration VLUN #
                
                cmd_display_header(mode, self.error_dict, logger=self.logger)
                
                remove_fast_to_sg = []
                
                sgroup = self.sgroup_cls_lst[0]
                self.vlun_migration_name = 'VLUN_{0}_{1}'.format(sgroup.name, self.pid)
                
                if sgroup.fast:
                    remove_fast_to_sg = ['symfast -sid {0} disassociate -fp_name {1} -sg {2}'.format(self.sid, sgroup.fast_name, sgroup.name)]
                    
                if self.dev_sg and self.fast_name:
                    add_fast_to_sg = ['symfast -sid {0} associate -fp_name {1} -sg {2}'.format(self.sid, self.fast_name, sgroup.name)]
                
                cmd_exec_mode(remove_fast_to_sg, 'Remove F.Policy to S.Group', mode, logger=self.logger, export=self.export)
                create_vlun_migrate_pair([l.id for l in self.lun_cls_lst], mode, self.sid, self.pool_name, self.vlun_migration_name, self.tmp_file, verbose=self.verbose_mode, logger=self.logger, export=self.export)
                
                if mode == 'display':
                    mprint('(-) VLUN Migration State Check', tac=1)
                
                elif mode == 'exec':
                    wait_vlun_migrate(self.sid, self.vlun_migration_name, len(self.lun_cls_lst))
                
                cmd_exec_mode(
                    ['symmigrate -sid {0} -name {1} terminate -nop'.format(self.sid, self.vlun_migration_name)],
                    'Terminate VLUN Migration',
                    mode, logger=self.logger, export=self.export
                )
                
                cmd_exec_mode(add_fast_to_sg, 'Add New F.Policy to S.Group', mode, logger=self.logger, export=self.export)
                
            cmd_display_footer(mode, self.warning_dict, self.mode, logger=self.logger, start_time=self.script_start_time, nop=self.no_prompt)
            
            if mode == 'exec':
                
                if self.mig_type != 'VLUN':
                    self.new_lun_cls_lst = lun_info_retrieve(self.local_lun_id_by_size, self.sid, self.array_type, logger=self.logger, export=self.export)
                    lun_display(self.sid, self.new_lun_cls_lst, self.array_type, size_display=self.size_display, debug=self.debug_mode)
            
