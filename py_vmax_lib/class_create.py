# -*- coding: utf-8 -*-

#================================================================================#
# ------------------------------- IMPORT LIBRARY ------------------------------- #
#================================================================================#

#~~~~# LOCAL LIBRARY #~~~~#

from py_vmax_lib.class_audit import AuditMode

from py_vmax_lib.func_global import *
from py_vmax_lib.func_execution import *
from py_vmax_lib.func_display import *
from py_vmax_lib.func_retrieve import *
from py_vmax_lib.func_check import *

#==============================================================================#
# ------------------------------- MODULE START ------------------------------- #
#==============================================================================#

class CreateMode(AuditMode):
    """Create Mode class"""
    
    def __init__(self, glob_dic, logger, mig_mode=False):
        AuditMode.__init__(self, glob_dic, logger)
        
        self.mig_mode = mig_mode
        self.exist_sg = False
        
        if self.mode == 'create':
            if self.select:
                mprint()
                self.new_lun = text_input('Create New Lun ?', '[Yes|No]', out_type='bool')
                self.new_sg = text_input('Create New S.Group ?', '[Yes|No]', out_type='bool')
                self.new_view = text_input('Create New M.View ?', '[Yes|No]', out_type='bool')
                
                if not self.new_lun and not self.new_sg and not self.new_view:
                    sc_exit(0, mode=self.mode, start_time=self.script_start_time, logger=self.logger)
                
                if not self.new_lun:
                    if self.new_sg or self.new_view: mprint('Script create S.Group or M.View with Lun(s)', 'err')
                
                if not self.new_sg:
                    self.dev_sg = True
                
                mprint()
            
            self.logger.info('[NEW:DEV] [Lun : {0} / S.Group : {1} / M.View : {2}]'.format(self.new_lun, self.new_sg, self.new_view))
            
    def mode_check(self):
        
        self.login_cls_lst = []
        
        # VA(C)rification des nouveaux Luns en argument #
        
        if self.new_lun:
            
            # VA(C)rification Taille #
            
            check = 1
            
            while check is not 0:
                
                self.nlun_dct_lst = []
                lun_size_lst = []
                no_standard_meta_lst = []
                no_standard_lun_lst = []
                
                if self.select or check == 2:
                    check = 1
                    self.new_lun_arg = text_input('Enter Lun to Create', out_type='lst')
                    
                for n in self.new_lun_arg:
                    
                    n = n.lower()
                    
                    if not re.search('^[0-9]+(x|\*)([0-9]+c?(:[0-9]+)?|gk)$', n):
                        mprint('Bad Syntax [Ex : 1x108,2x216:2.. or 1x1093c]', 'err', exit=False)
                        mprint()
                        check = 2; break
                         
                    cylinder_mode = False
                    
                    lun_create_dct = {}
                    
                    lun_create_dct['size_cyl'] = False
                    lun_create_dct['meta'] = False
                    lun_create_dct['gk'] = False
                    
                    lun_create_dct['count'] = int(re.split(r'x|\*', n)[0])
                    lun_size_fmt = re.split(r'x|\*', n)[1]
                    
                    if 'c' in lun_size_fmt:
                        cylinder_mode = True
                        lun_size_fmt = lun_size_fmt.replace('c', '')
                    
                    if re.search('[0-9]+:[0-9]+$', str(lun_size_fmt)):
                        if self.array_type == 3:
                            mprint('No Meta on VMAX-3', 'err', exit=False)
                            mprint()
                            check = 2; break
                            
                        lun_create_dct['meta'] = True
                        lun_size = int(lun_size_fmt.split(':')[0])
                        meta_count = int(lun_size_fmt.split(':')[1])
                        
                        if cylinder_mode and lun_size % meta_count is not 0:
                            mprint('Problem with Cylinder Meta : ({0}) !'.format(n), 'err', exit=False)
                            mprint()
                            check = 2; break
                            
                        
                    elif str(lun_size_fmt).lower() == 'gk':
                        lun_create_dct['gk'] = True
                     
                    else:
                        lun_size = int(lun_size_fmt)
                    
                    if not lun_create_dct['gk']:
                        
                        if not cylinder_mode:
                            
                            for l in lun_size_dic_lst:
                                
                                if re.search('^{0}$'.format(l['reg']), str(lun_size)):
                                    
                                    lun_size = l['size_gb']
                                    
                                    lun_create_dct['size_cyl'] = l['cyl_12'] if self.array_type == 12 else l['cyl_3']
                                    
                                    if lun_create_dct['meta']:
                                        lun_create_dct['meta_cyl'] = int(lun_create_dct['size_cyl'] / int(meta_count))
                                        
                                        if lun_create_dct['meta_cyl'] not in [s['cyl_12'] for s in lun_size_dic_lst]:
                                            mprint('Meta Bad Value : {0} [Meta {1} GB]'.format(n, int(lun_size / int(meta_count))), 'err', exit=False)
                                            mprint()
                                            check = 2; break
                                        
                                        if lun_create_dct['meta_cyl'] != 118976:
                                            no_standard_meta_lst.append('{0}x{1}:{2} [Meta {3} GB]'.format(lun_create_dct['count'], lun_size, int(meta_count), int(lun_size / int(meta_count))))
                                        
                                    else:
                                        
                                        if self.array_type == 12 and lun_size > 108:
                                            no_standard_lun_lst.append('{0}x{1}'.format(lun_create_dct['count'], lun_size))
                                        
                                        
                            if not lun_create_dct['size_cyl']:
                                mprint('Bad Lun Size [{0} GB]'.format(lun_size), 'err', exit=False)
                                mprint()
                                check = 2; break
                            
                            lun_size_lst.append(int(lun_size)*lun_create_dct['count'])
                        
                        else:
                            lun_create_dct['size_cyl'] = lun_size
                            
                            if lun_create_dct['meta']:
                                lun_create_dct['meta_cyl'] = int(lun_create_dct['size_cyl'] / int(meta_count))
                            
                        
                    self.nlun_dct_lst.append(lun_create_dct)
                    
                if check is not 2:
                    
                    check = 0
                    
                    if not self.mig_mode:
                        self.lun_total_size_gb = sum(lun_size_lst)
                        self.lun_total_consum_size_gb = 0
                        
                    self.logger.info('[NEW:LUN] {0}'.format(self.new_lun_arg))
                    
                    if no_standard_meta_lst:
                        self.warning_dict[self.warning_id_incr] = 'Meta with Not Standard Value (108 GB) : {0}'.format(', '.join(no_standard_meta_lst))
                    
                    if no_standard_lun_lst:
                        self.warning_dict[self.warning_id_incr] = 'Lun with Size > 108 GB on not Meta : {0}'.format(', '.join(no_standard_lun_lst))
                    
        if self.select: mprint()
        
        # VA(C)rif SG Existant #
        
        if self.dev_sg:
            
            if not getattr(self, 'sg_all_lst', False):
                self.sg_all_lst, self.ig_all_lst = sg_ig_lst_retrieve(self.sid, export=self.export)
            
            self.exist_sg = True
            check = 0
            
            if self.select:
                check = 1
            
            while True:
                if check is 1:
                    mprint()
                    self.dev_sg_arg = [text_input('Enter S.Group Name', type='S.Group', out_type='choice', lst=self.sg_all_lst)]
                    
                if len(self.dev_sg_arg) > 1:
                    mprint('Only 1 S.Group to add Lun(s)', 'err', tac=1, logger=self.logger, exit=False)                 
                    check = 1
                    continue
                    
                else:
                    sg_check = exist_check(self.dev_sg_arg, self.sg_all_lst, 'S.Group', mode = 'N', logger=self.logger, exit=False)
                    
                    if sg_check is not 2:
                        self.sgroup = ','.join(self.dev_sg_arg)
                        self.logger.info('[EXIST:SG] {0}'.format(self.sgroup))
                        break
                        
                    else:
                        mprint()
                        check = 1
                        continue
                    
            if check is 1: mprint()
                    
        # VA(C)rif Nouveau SG #
        
        if self.select and self.new_view:
            cluster = text_input('Create New Cluster ?', '[Yes|No]', out_type='bool')
            mprint()
            
            if cluster:
                self.node = text_input('Enter Number of Node', out_type='int')
                mprint()
            
        if self.new_sg:
            
            title_fmt = ''
            
            if self.select:
                self.new_name_arg = False
            
            if self.mode == 'migrate':
                title_fmt = 'Remote '
                
                self.new_name_arg = getattr(self, 'new_name_arg', False)
                
            self.sgroup, self.new_name_arg, self.sg_all_lst, self.ig_all_lst = new_sgroup_argument_check(
                self.sid,
                self.new_name_arg,
                self.node,
                self.one_view,
                sg_type=title_fmt,
                no_break=self.no_break,
                logger=self.logger,
                export=self.export
            )
            
        # VA(C)rif Nouvelle MV [Select] #
        
        if self.new_view:
            check = 1
            
            if self.select:
                while check is not 0:
                    
                    check = 1
                    
                    if self.exist_sg:
                        mprint()
                        self.new_name_arg = text_input('Enter Name of New M.View')
                         
                    self.new_view_arg = []
                    node_name_lst = []
                    node_wwn_lst = []
                    
                    for n in range(self.node):
                        
                        if self.node != 1:
                            
                            check_n = 1
                            
                            while check_n is not 0:
                                node_name = text_input('Enter Name of Node {0}'.format(n+1))
                                
                                if re.search('(_sg|sg_)', node_name.lower()):
                                    mprint("Bad Name Syntax. Please enter Only Server Name", 'err', exit=False)
                                    mprint()
                                    
                                elif node_name in node_name_lst:
                                    mprint("Nodes can't Have the Same Name", 'err', exit=False)
                                    mprint()
                                
                                elif node_name.lower() == self.new_name_arg.lower():
                                    mprint("Nodes can't Have the Same Name of Cluster", 'err', exit=False)
                                    mprint()
                                
                                else:
                                    check_n = 0
                            
                            node_name_lst.append(node_name)
                            
                        check_w = 1
                        
                        while check_w is not 0:
                            
                            if self.node != 1:
                                t = 'Node'
                                c = n+1
                            else:
                                t = 'Server'
                                c = ''
                                
                            node_wwn = text_input('Enter Logins of {0} {1}'.format(t, c), out_type='lst')
                            
                            if len(node_wwn)%2 != 0:
                                mprint('2 Logins Min (Even/Odd Fabric) and Even Number Only (2/4/6..) Logins', 'err', exit=False)
                                mprint()
                            
                            else:
                                for w in node_wwn:
                                    if w in node_wwn_lst:
                                        mprint("2 Nodes can't Have the Same Logins", 'err', exit=False)
                                        mprint()
                                        check_w = 1; break
                                    else:
                                        check_w = 0
                             
                        node_wwn_lst = node_wwn_lst + node_wwn
                        
                        if self.node != 1:
                            view_arg = '[{0}]{1}'.format(node_name, ','.join(node_wwn))
                            
                        else:
                            view_arg = ','.join(node_wwn)
                            
                        self.new_view_arg.append(view_arg)
                            
                        mprint()
                    
                    check = 0
                   
            if self.no_break:
                self.nview_name = self.new_name_arg
            else:
                self.nview_name = self.new_name_arg.lower()
                
            self.nview_dic_lst = []
            
            # VA(C)rif Syntaxe/WWN #
            
            if self.node > 1:
                 
                for view_inf in self.new_view_arg:
                    nview_dic = {}
                    view_inf = view_inf.replace(':', '').lower()
                    
                    match = re.match(r'^\[(?P<server>.*)\](?P<wwn_list>.*)$', view_inf)
                    
                    if match:
                        nview_dic['name'] = match.group('server')
                        nview_dic['wwn_list'] = match.group('wwn_list').split(',')
                        
                    else:
                        mprint('Bad Syntax for nview Argument [Ex : [server1]wwn1,wwn2-[server2]wwn1,wwn2]', 'err', logger=self.logger)
                        
                    if nview_dic['name'] == self.nview_name:
                        mprint("Node and Cluster Name should be different [{0}]".format(self.nview_name), 'err', logger=self.logger)
                       
                    self.nview_dic_lst.append(nview_dic)
             
            else:
                nview_dic = {}  
                nview_dic['name'] = self.nview_name
                nview_dic['wwn_list'] = ','.join(self.new_view_arg).replace(':', '').lower().split(',')
                
                self.nview_dic_lst.append(nview_dic)
                
            bad_wwn_lst = login_syntax_check(nview_dic['wwn_list'])
            
            if bad_wwn_lst:
                mprint('Bad WWN syntax : {0}'.format(bad_wwn_lst), 'err', logger=self.logger)
                   
            self.wwn_list = []
            
            for nview_dic in self.nview_dic_lst:
                self.wwn_list = self.wwn_list + nview_dic['wwn_list']
                
            # VA(C)rif Login #
                
            self.login_cls_lst = [login for login in login_info_retrieve(self.wwn_list, self.sid, export=self.export)]
            
            if [login.wwn for login in self.login_cls_lst if not login.port]:
                login_display(self.sid, self.login_cls_lst, debug=self.debug_mode)
                mprint('Login(s) [{0}] not Find'.format(','.join([login.wwn for login in self.login_cls_lst if not login.port])), 'err')
            
            self.wwn_dic_lst = []
            
            login_alias_lst = []
            login_view_lst = []
            login_init_lst = []
            login_no_onfab_lst = []
            
            for login in self.login_cls_lst:
                
                wwn_dic = {}
                wwn_dic['name'] = login.wwn
                wwn_dic['type'] = []
                wwn_dic['exist_ig_name'] = ''
                wwn_dic['exist_node_name'] = False
                
                for dir_prt in login.port_all_dir_prt_list:
                    if int(dir_prt.split(':')[1]) % 2 == 0:
                        wwn_dic['type'].append('P')
                    else:
                        wwn_dic['type'].append('I')
                    
                wwn_dic['type'] = set(wwn_dic['type'])
                
                if len(wwn_dic['type']) > 1:
                    login_display(self.sid, self.login_cls_lst, debug=self.debug_mode)
                    mprint('Login {0} is connect to Peer and Odd Fabric. Check Zoning or Create MV manualy'.format(wwn_dic['name']), 'err')
                else:
                    wwn_dic['type'] = ','.join(wwn_dic['type'])
                    
                # Check Warning/Erreur #
                
                if getattr(login, 'view_list', False):
                    login_view_lst.append(wwn_dic['name'])
                    login.warning = True
                    
                if getattr(login, 'node_name', False):
                    login_alias_lst.append(wwn_dic['name'])
                    wwn_dic['exist_node_name'] = True
                    login.warning = True
                    
                if getattr(login, 'init_list', False):
                    wwn_dic['exist_ig_name'] = login.init_list[0]
                    login_init_lst.append((wwn_dic['name'], wwn_dic['exist_ig_name']))
                    login.warning = True
                    
                if not 'Y' in getattr(login, 'status_on_fab', []):
                    login_no_onfab_lst.append(wwn_dic['name'])
                    login.error = True
                    
                self.wwn_dic_lst.append(wwn_dic)
             
            login_type_lst = [wwn_dic['type'] for wwn_dic in self.wwn_dic_lst]
            login_type_count = sorted([{cnt : login_type_lst.count(cnt)} for cnt in set(login_type_lst)])
            
            only_one_fab = False
            
            if len(login_type_count) != 2:
                
                if self.force_mode:
                    only_one_fab = True
                    
                else:
                    login_display(self.sid, self.login_cls_lst, debug=self.debug_mode)
                    mprint('Logins are connect only on 1 fabric. Check it', 'err')
                    
                    if login_type_count[0]['I'] != login_type_count[1]['P']:
                        login_display(self.sid, self.login_cls_lst, debug=self.debug_mode)
                        mprint('There are {0} Logins on Odd Fabric and {1} on Even Fabric. Check it'.format(login_type_count[0]['I'], login_type_count[1]['P']), 'err')
            
            # if login_alias_lst:
                # self.warning_dict[self.warning_id_incr] = 'Login(s) {0} have Already a Alias [Script Rename it]'.format(','.join(login_alias_lst))
            
            if login_init_lst:
                for l in login_init_lst:
                    self.warning_dict[self.warning_id_incr] = 'Login {0} have Already a IG : {1} [Script Use It]'.format(l[0], l[1])
                
            if login_view_lst:
                self.warning_dict[self.warning_id_incr] = 'Login(s) {0} have Already a M.View'.format(','.join(login_view_lst))
                
            if login_no_onfab_lst:
                login_display(self.sid, self.login_cls_lst, debug=self.debug_mode)
                mprint('Login(s) {0} not Connected on Fabric'.format(login_no_onfab_lst), 'err') 
                
            # GenA(C)ration des IG/MV #
            
            self.mv_all_lst = view_lst_retrieve(self.sid, logger=self.logger, export=self.export)
            self.login_all_dic_lst = login_lst_retrieve(self.sid, logger=self.logger, export=self.export)
            
            generate_ig_mv_login(self.wwn_dic_lst, self.nview_dic_lst, self.login_cls_lst, self.node, self.nview_name, only_one_fab, self.one_view)
            
            # Check des IG/MV #
            
            for w in self.wwn_dic_lst:
                
                exist_check([w['mv_name']], self.mv_all_lst, type='M.View', mode='E')
                
                w['ig_exist'] = exist_check([w['ig_name']], self.ig_all_lst, type='Init')
                
                if self.node > 1:
                    w['cig_exist'] = exist_check([w['cig_name']], self.ig_all_lst, type='C.Init')
                
                w['pn_exist'] = exist_check(
                    ['{0}:{1}'.format(w['server_name'], w['port_name'])],
                    ['{0}:{1}'.format(x['node_name'], x['port_name']) for x in self.login_all_dic_lst],
                    type='Server Port Name'
                )
                
            # ig_exist_lst = set([w['ig_name'] for w in self.wwn_dic_lst if w['ig_exist']])
            # cig_exist_lst = set([w['cig_name'] for w in self.wwn_dic_lst if w.get('cig_exist', False)])
            
            # if ig_exist_lst:
                # self.warning_dict[self.warning_id_incr] = 'IG(s) {0} Already Exist [Script not Create It]'.format(','.join(ig_exist_lst))
            
            # if cig_exist_lst:
                # self.warning_dict[self.warning_id_incr] = 'CIG(s) {0} Already Exist [Script not Create It]'.format(','.join(cig_exist_lst))
            
            debug_fmt(self.debug_mode, self.wwn_dic_lst)
            
            # VA(C)rif PG #
            
            self.port_cls_lst = [p for p in port_group_retrieving(self.sid, export=self.export)]
            
            debug_fmt(self.debug_mode, [p.__dict__ for p in self.port_cls_lst])
            
            for wwn_dic in self.wwn_dic_lst:
                
                if self.one_view:
                    wwn_dic['port_all'] = rtr_dict_list(self.wwn_dic_lst, 'port', uniq=True, concat=True, mode_cls=False)
                    wwn_dic['port_logged'] = rtr_dict_list(self.wwn_dic_lst, 'port_logged', uniq=True, concat=True, mode_cls=False)
                    
                else:
                    wwn_dic['port_all'] = rtr_dict_list(self.wwn_dic_lst, 'port', uniq=True, concat=True, filter='type:{0}'.format(wwn_dic['type']), mode_cls=False)
                    wwn_dic['port_logged'] = rtr_dict_list(self.wwn_dic_lst, 'port_logged', uniq=True, concat=True, filter='type:{0}'.format(wwn_dic['type']), mode_cls=False)
                    
                wwn_dic['pg'] = [p.name for p in self.port_cls_lst if sorted(wwn_dic['port_all']) == sorted(p.dir_port)]
                
                if not wwn_dic['pg']:
                    wwn_dic['pg'] = [p.name for p in self.port_cls_lst if sorted(wwn_dic['port_logged']) == sorted(p.dir_port)]
                    
                    if not wwn_dic['pg']:
                        login_display(self.sid, self.login_cls_lst, debug=self.debug_mode)
                        mprint('No Port Group find. Check Zoning or Create MV manualy', 'err')
                    
                elif len(wwn_dic['pg']) > 1:
                    login_display(self.sid, self.login_cls_ls, debug=self.debug_modet)
                    mprint('Several Port Group find [{0}]. Create MV manualy'.format(','.join(wwn_dic['pg'])), 'err')
                    
                wwn_dic['pg'] = wwn_dic['pg'][0]
                
            self.logger.info('[NEW:VIEW] {0}'.format(self.nview_dic_lst))
               
    def info_retrieve(self):
        
        self.fast_list = []
        self.lun_by_pool_lst = []
        
        if self.exist_sg:
            self.sgroup_cls = sgroup_info_retrieve(self.dev_sg_arg, self.sid, self.array_type, logger=self.logger, export=self.export)[0]
            self.sgroup = ','.join(self.dev_sg_arg)
            
            if self.array_type == 12:
                
                if self.sgroup_cls.fast:
                    self.fast_list = [self.sgroup_cls.fast_name]
                
        if self.new_lun:
            
            if self.array_type == 12:
                self.fast_cls_lst = fast_retrieving(self.sid, self.fast_list, logger=self.logger, export=self.export)
                self.pool_list = rtr_dict_list(self.fast_cls_lst, 'pool_list', uniq=True, concat=True)
                self.pool_cls_lst = pool_retrieving(self.sid, sorted(self.pool_list), self.lun_total_size_gb, self.lun_total_consum_size_gb, logger=self.logger, export=self.export)
                
                silo_info_retrieve(self.pool_cls_lst, self.fast_cls_lst)
                
            elif self.array_type == 3:
                self.srp_cls_lst = srp_retrieving(self.sid, self.lun_total_size_gb, self.lun_total_consum_size_gb, logger=self.logger, export=self.export)
                slo_retrieving(self.srp_cls_lst, self.sid, logger=self.logger, export=self.export)
                
            if self.exist_sg:
                # Selection SG Child (si CSG) #
                
                if self.sgroup_cls.type == 'parent':
                    self.sgroup = select_choice(self.sgroup_cls.cascad_sgroup_name, type='S.Group Child')
                
                else:
                    if self.array_type == 12:
                        if self.sgroup_cls.lun_count is not 0 and not self.sgroup_cls.fast:
                            self.lun_by_pool_lst = lun_by_pool_retrieving(self.sid, self.sgroup_cls.lun_list, self.pool_cls_lst, logger=self.logger, export=self.export)   
                            
                
        if self.login_cls_lst:
            login_display(self.sid, self.login_cls_lst, debug=self.debug_mode)
        
        if self.new_lun:
            
            if self.array_type == 12:
                
                pool_display(self.sid, self.pool_cls_lst, self.lun_total_size_gb, self.lun_total_consum_size_gb, mode_migrate=self.mig_mode, debug=self.debug_mode)
                
                pool_lst = sorted([p for p in self.pool_cls_lst if not p.error], key=attrgetter('warning'))
                
                if pool_lst:
                    
                    pool_default = sorted(self.pool_cls_lst, key=attrgetter('subs_prc_aft_lun_add', 'used_prc'))[0].name
                    
                    if not self.fast_list and self.exist_sg:
                        mprint('S.Group {0} have no F.Policy. So All Pool are Available'.format(self.sgroup), 'war')
                    
                    if self.lun_by_pool_lst:
                        mprint()
                        for p in self.lun_by_pool_lst:
                            mprint(color_str(' > {0} : {1} Lun(s) '.format(p.keys()[0], p.values()[0]), 'rev'))
                        
                    pool_list = [p.name for p in pool_lst]
                    pool_list_display = []
                    
                    for p in pool_lst:
                        
                        p_fmt = p.name
                        
                        if p.warning:
                            p_fmt = color_str(' {0} '.format(p_fmt), 'yel')
                            
                        if p.info:
                            p_fmt = '{0} (*)'.format(p_fmt)    
                            
                        pool_list_display.append(p_fmt)
                    
                    if self.no_prompt:
                        self.pool_name = pool_default
                    else:
                        self.pool_name = select_choice(pool_list, pool_list_display, type='Pool', default=pool_default, display_orginal_lst=True)
                    
                    # Selection Fast New SG #
                    
                    if self.new_sg:
                        fast_lst = [f for f in self.fast_cls_lst if self.pool_name in f.pool_list]
                        
                        try:
                            fast_default = [f.name for f in fast_lst if 'Classe2' in f.name][0]
                        except IndexError:
                            fast_default = sorted(fast_lst, key=attrgetter('sg_count'), reverse=True)[0].name
                        
                        if self.no_prompt:
                            self.fast_name = fast_default
                        else:
                            self.fast_name = select_choice(sorted([f.name for f in fast_lst]), type='F.Policy', default=fast_default)
                    
                else:
                    mprint('No Pool Available for this Size : {0}'.format(size_conv(self.lun_total_size_gb, 'GB')), 'err')
                    
            elif self.array_type == 3:
                
                srp_display(self.sid, self.srp_cls_lst, self.lun_total_size_gb, self.lun_total_consum_size_gb, mode_migrate=self.mig_mode, debug=self.debug_mode)
                
                if self.new_sg:
                    
                    slo_default = 'Silver'
                    
                    self.srp = self.srp_cls_lst[0].name
                    
                    if self.no_prompt:
                        self.slo_name = slo_default
                    else:
                        self.slo_name = select_choice(sorted(self.srp_cls_lst[0].slo_list), type='Slo', default=slo_default)
        
        if self.new_view:
            
            if self.wwn_dic_lst:
                
                for wwn_dic in self.wwn_dic_lst:
                    
                    if wwn_dic['exist_node_name']:
                        mprint()
                        choice = text_input(color_str(' <!> Login {0} Have Already Alias ! Do You Want rename It ? '.format(wwn_dic['name']), 'yel'), '[Y|N] (N)', out_type='bool', default='No')
                        
                        if choice:
                            wwn_dic['exist_node_name'] = False
                        
        
    def mode_exec(self, mode_type = ['display', 'exec']):
        
        title_rmt = ''
        
        if self.mode == 'migrate':
            
            if self.mig_type == 'SRDF':
                title_rmt = '[Remote] '
            else:
                title_rmt = '[Local] '
                
        create_lun = []
        add_lun_to_sg = []
        rename_login = []
        create_sg = []
        create_cig = []
        create_ig = []
        create_mv = []
        add_ig_to_cig = []
        add_wwn_to_ig = []
        add_fast_to_sg = []
        
        # CrA(C)ation MV #
        
        cons_lun = ''
        
        if self.array_type == 3:
            cons_lun = ' -consistent_lun'
        
        if self.new_view: 
            
            for wwn_dic in self.wwn_dic_lst:
                
                if not wwn_dic['exist_node_name']:
                    rename_login.append('symaccess -sid {0} rename -wwn {1} -alias {2}/{3}'.format(self.sid, wwn_dic['name'], wwn_dic['server_name'], wwn_dic['port_name']))
                
                if not wwn_dic['ig_exist']:
                    create_ig.append('symaccess -sid {0} create -name {1} -type init{2}'.format(self.sid, wwn_dic['ig_name'], cons_lun))
                    add_wwn_to_ig.append('symaccess -sid {0} add -name {1} -type init -wwn {2}'.format(self.sid, wwn_dic['ig_name'], wwn_dic['name']))
                
                if self.node > 1:
                    create_mv.append('symaccess -sid {0} create view -name {1} -ig {2} -sg {3} -pg {4}'.format(self.sid, wwn_dic['mv_name'], wwn_dic['cig_name'], self.sgroup, wwn_dic['pg']))
                    
                    if not wwn_dic['cig_exist']:
                        create_cig.append('symaccess -sid {0} create -name {1} -type init{2}'.format(self.sid, wwn_dic['cig_name'], cons_lun))
                        add_ig_to_cig.append('symaccess -sid {0} add -name {1} -type init -ig {2}'.format(self.sid, wwn_dic['cig_name'], wwn_dic['ig_name']))
                    
                else:
                    create_mv.append('symaccess -sid {0} create view -name {1} -ig {2} -sg {3} -pg {4}'.format(self.sid, wwn_dic['mv_name'], wwn_dic['ig_name'], self.sgroup, wwn_dic['pg']))
                
        # CrA(C)ation Lun #
        
        if self.new_lun:
            
            for nlun_dct in self.nlun_dct_lst:
                
                binding_pool = ''
                dynamic_cap = ''
                
                if self.array_type == 12:
                    binding_pool = ', binding to pool={0}'.format(self.pool_name)
                    dynamic_cap = ', dynamic_capability=DYN_RDF'
                
                if nlun_dct['meta']:
                    create_lun.append('create dev count={0}, emulation=FBA, config=TDEV, size={1}, meta_member_size={2}, meta_config=striped{3}{4};'.format(nlun_dct['count'], nlun_dct['size_cyl'], nlun_dct['meta_cyl'], binding_pool, dynamic_cap))
                    
                elif nlun_dct['gk']:
                    create_lun.append('create gatekeeper count={0}, emulation=FBA, type=thin{1};'.format(nlun_dct['count'], binding_pool))
                    
                else:
                    create_lun.append('create dev count={0}, size={1}, emulation=FBA, config=TDEV{2}{3};'.format(nlun_dct['count'], nlun_dct['size_cyl'], binding_pool, dynamic_cap))
            
            add_lun_to_sg.append('symaccess -sid {0} add -name {1} -type storage dev {2}'.format(self.sid, self.sgroup, '[New Device]'))
        
        # CrA(C)ation SG #
        
        if self.new_sg:
            if self.array_type == 12:
                create_sg.append('symaccess -sid {0} create -name {1} -type storage'.format(self.sid, self.sgroup))
                add_fast_to_sg.append('symfast -sid {0} associate -fp_name {1} -sg {2}'.format(self.sid, self.fast_name, self.sgroup))
                
            elif self.array_type == 3:
                create_sg.append('symsg -sid {0} create {1} -slo {2} -srp {3}'.format(self.sid, self.sgroup, self.slo_name, self.srp))
        
        # Affichage/Execution Commandes #
        
        for mode in mode_type:
            
            cmd_display_header(mode, self.error_dict, logger=self.logger)
            
            cmd_exec_mode(create_sg, '{0}Create New S.Group'.format(title_rmt), mode, logger=self.logger, export=self.export)
            
            if mode == 'display':
                symconf_exec(create_lun, '{0}Create Lun'.format(title_rmt), mode, 'Lun to Create', self.sid, self.tmp_file, verbose=True, logger=self.logger, export=self.export)
                cmd_exec_mode(add_lun_to_sg, '{0}Add Lun(s) to S.Group'.format(title_rmt), mode, logger=self.logger, export=self.export)
                
            elif mode == 'exec':
                if self.new_lun:
                    create_validation_check, self.new_lun_lst = symconf_exec(create_lun, '{0}Create Lun'.format(title_rmt), mode, 'Lun to Create', self.sid, self.tmp_file, verbose=True, logger=self.logger, export=self.export)
                    
                    if not create_validation_check:
                        self.new_lun_cls_lst = lun_info_retrieve(self.new_lun_lst, self.sid, self.array_type, logger=self.logger, export=self.export)
                        
                        lun_with_no_pool_lst = [l.id for l in self.new_lun_cls_lst if not l.bound]
                        bind_lun_to_pool = ['symdev -sid {0} bind -dev {1} -pool {2} -nop'.format(self.sid, ','.join(lun_with_no_pool_lst), self.pool_name)]   
                        cmd_exec_mode(bind_lun_to_pool, '{0}Binding Lun(s) to Pool'.format(title_rmt), mode, logger=self.logger, export=self.export)
                    
                    add_lun_to_sg = ['symaccess -sid {0} add -name {1} -type storage dev {2}'.format(self.sid, self.sgroup, ','.join(self.new_lun_lst))]
                    cmd_exec_mode(add_lun_to_sg, '{0}Add Lun(s) to S.Group'.format(title_rmt), mode, logger=self.logger, export=self.export)
                
            cmd_exec_mode(add_fast_to_sg, '{0}Add F.Policy to S.Group'.format(title_rmt), mode, logger=self.logger, export=self.export)
            cmd_exec_mode(rename_login, 'Rename Logins', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(create_cig, 'Create C.Init', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(create_ig, 'Create Init', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(add_wwn_to_ig, 'Add Login to Init', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(add_ig_to_cig, 'Add init to C.Init', mode, logger=self.logger, export=self.export)
            cmd_exec_mode(create_mv, 'Create M.View', mode, logger=self.logger, export=self.export)
            
            if self.mode == 'create':
                if mode == 'exec':
                    self.new_lun_cls_lst = lun_info_retrieve(self.new_lun_lst, self.sid, self.array_type, logger=self.logger, export=self.export)
                    lun_display(self.sid, self.new_lun_cls_lst, self.array_type, size_display=self.size_display, debug=self.debug_mode)
                
                cmd_display_footer(mode, self.warning_dict, self.mode, logger=self.logger, start_time=self.script_start_time, nop=self.no_prompt)
            