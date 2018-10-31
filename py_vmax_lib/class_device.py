
#================================================================================#
# ------------------------------- IMPORT LIBRARY ------------------------------- #
#================================================================================#

#~~~~# PYTHON LIBRARY #~~~~#

from __future__ import division

#~~~~# LOCAL LIBRARY #~~~~#

from py_vmax_lib.func_global import *



#==============================================================================#
# ------------------------------- MODULE START ------------------------------- #
#==============================================================================#

class DeviceGlobal(object):
    def __init__(self):
        self.info = False
        self.warning = False
        self.error = False
        self.remove = False
        self.display = False
        
        self.error_msg = ''
        self.warning_msg = ''


class LunInfo(DeviceGlobal):
    """Device class"""
    def __init__(self, id, wwn_id, size, size_cyl, type, status, emulation):
        DeviceGlobal.__init__(self)
        
        self.id = id
        self.wwn_id = wwn_id
        self.size = int(size)
        self.size_cyl = int(size_cyl)
        self.type = type
        self.emulation = emulation
        self.tdev = False
        self.ready = False
        self.bound = False
        self.unbinding = False
        self.reclaim = False
        self.meta = False
        self.sgroup = False
        self.sgroup_parent = False
        self.srdf_cap = False
        self.bcv_flag = False
        self.clone = False
        self.bcv = False
        self.srdf = False
        self.openr = False
        self.gkeeper = False
        self.aclx = False
        self.pool = False
        
        self.sgroup_list = []
        self.sgroup_list_fmt = []
        self.written = 0
        self.allocate = 0
        
        self.size_fmt = size_conv(self.size, 'MB')
        
        if 'TDEV' in type:
            self.tdev = True
            self.type = "TDev"
        else:
            self.type = "PDev"
        
        if 'BCV' in type:
            self.bcv_flag = True
        
        if status.lower() != 'not ready':
            self.ready = True
        else:
            self.warning = True
        
        if self.emulation != 'FBA':
            self.error = True
        
    def gkeep(self):
        self.gkeeper = True
        self.type = "{0}[GK]".format(self.type)
        
    def aclx_flag(self):
        self.aclx = True
        self.type = "{0}[ACLX]".format(self.type)
        
    def pool_info(self, pool):
        self.pool = True
        self.pool_name = str(pool)
        
    def status_info(self, status, written, alloc):
        if status == 'Bound' or status == 'Reclaiming':
            self.bound = True
            
            if status == 'Reclaiming':
                self.reclaim = True
        
        elif status == 'Unbinding':
            self.unbinding = True
        
        self.written = int(written)
        
        try:
            self.allocate = int(alloc)
        except ValueError:
            self.allocate = 0
        
        if self.unbinding or self.reclaim and not self.bound:
            self.warning = True
        
    def storage_info(self, sg_dic_lst):
        self.sgroup = True
        
        self.sgroup_list = [s['sgroup_name'] for s in sg_dic_lst]
        self.sgroup_count = len(self.sgroup_list)
        
        self.sgroup_child_list = [s['sgroup_name'] for s in sg_dic_lst if s['status'] == 'child']
        self.sgroup_parent_list = [s['sgroup_name'] for s in sg_dic_lst if s['status'] == 'parent']
        
        for y, sg in enumerate(sg_dic_lst):
            
            if sg['status'] == 'child':
                self.sgroup_parent = True
                
                try:
                    self.sgroup_list_fmt.append('{0}[P:{1}]'.format(sg['sgroup_name'], sg_dic_lst[y+1]['sgroup_name']))
                
                except IndexError:
                    self.sgroup_list_fmt.append('{0}[P:{1}]'.format(sg['sgroup_name'], sg_dic_lst[y-1]['sgroup_name']))
                
            elif sg['status'] == 'normal':
                self.sgroup_list_fmt.append(sg['sgroup_name'])
                
    def meta_info(self, count, meta_list, meta_size):
        self.meta = True
        self.meta_count = int(count)
        self.meta_list = meta_list
        self.meta_size = int(''.join(set(meta_size)))
        self.meta_size_fmt = size_conv(self.meta_size, 'MB')
        self.meta_member = [meta for meta in meta_list if meta != self.id]
        self.type = "Meta[{0}]".format(count)
          
    def clone_info(self, clone_dic_lst):
        self.clone = True
        self.clone_info_dic_lst = clone_dic_lst
        self.source = [dic['source_dev_name'] for dic in clone_dic_lst][0]
        
        for y, dic in enumerate(clone_dic_lst):
            dic['clone_count'] = y+1
            if self.id == self.source:
                self.clone_type = 'SRC'
                dic['type'] = 'Source'
            else:
                self.clone_type = 'TGT'
                dic['type'] = 'Target'
         
    def bcv_info(self, bcv_dic_lst):
        self.bcv = True
        self.bcv_info_dic_lst = bcv_dic_lst
        self.source = [dic['source_dev_name'] for dic in bcv_dic_lst][0]
        
        for y, dic in enumerate(bcv_dic_lst):
            dic['bcv_count'] = y+1
            if self.id == self.source:
                self.bcv_type = 'SRC'
                dic['type'] = 'Source'
            else:
                self.bcv_type = 'TGT'
                dic['type'] = 'Target'
         
    def srdf_info(self, remote_list, srdf_list_info):
        self.srdf = True
        self.srdf_remote_list = list(remote_list)
        self.srdf_list_info = srdf_list_info
        
    def openrep_info(self, openr_dic_lst):
        self.openr = True
        self.openr_dic_lst = openr_dic_lst
        
        for or_dic in self.openr_dic_lst:
            
            or_dic['local_dev'] = self.id
            
            if or_dic['pull'] == 'True':
                or_dic['mode'] = 'Pull'
            else:
                or_dic['mode'] = 'Push'
                
            del or_dic['pull']
            
            
    @property
    def state_fmt(self):
        fmt = 'Ready'
        
        if self.unbinding:
            fmt = 'Unbinding'
        elif self.reclaim:
            fmt = 'Reclaim'
        elif self.tdev and not self.pool:
            fmt = 'Unbound'
        elif not self.ready:
            fmt = 'N.Ready'
            
        return fmt
        
    @property
    def allocate_written_fmt(self):
        fmt = 'A:{0:<5} W:{1}'.format(
            '{0}%'.format(percent_fmt(self.allocate, self.size)),
            '{0}%'.format(percent_fmt(self.written, self.size)),
        )
        
        return fmt
        
    @property
    def openr_display(self):
        if self.openr:
            fmt = 'Yes'
            
            for or_dic in self.openr_dic_lst:
                
                if or_dic['mode'] == 'Pull':
                    fmt = fmt + '[Pl]'
                else:
                    fmt = fmt + '[Ps]'
                
        else:
            fmt = 'No'
        
        return fmt
        
    @property
    def srdf_display(self):
        if self.srdf:
            fmt = []
            for srdf_info in self.srdf_list_info:
                if srdf_info['local_type'] == 'R1':
                    srdf_rmt_type = 'R2'
                else:
                    srdf_rmt_type = 'R1'
                    
                fmt.append('{0}:{1}[{2}:{3}:{4}({5})]'.format(
                    srdf_info['local_type'],
                    srdf_info['ra_group_num'].zfill(2),
                    srdf_rmt_type,
                    srdf_info['remote_symid'][-4:],
                    srdf_info['remote_dev_name'],
                    synchro_type_case(srdf_info['pair_state']),
                ))
        else:
            if self.srdf_cap:
                fmt = 'No[C]'
                
            else:
                fmt = 'No'
                
        return fmt
        
    @property
    def clone_display(self):
        if self.clone:
            if self.clone_type == 'SRC':
                fmt = "SRC[TGT:{0}]".format("|".join(['{0}({1})'.format(dic['target_dev_name'], synchro_type_case(dic['state'])) for dic in self.clone_info_dic_lst]))
            else:
                fmt = "TGT[SRC:{0}]".format("|".join(['{0}({1})'.format(dic['source_dev_name'], synchro_type_case(dic['state'])) for dic in self.clone_info_dic_lst]))
        
        else:
            fmt = 'No'
            
        return fmt
        
    @property
    def bcv_display(self):
        if self.bcv:
            if self.bcv_type == 'SRC':
                fmt = "SRC[TGT:{0}]".format("|".join(['{0}({1})'.format(dic['target_dev_name'], synchro_type_case(dic['state'])) for dic in self.bcv_info_dic_lst]))
            else:
                fmt = "TGT[SRC:{0}]".format("|".join(['{0}({1})'.format(dic['source_dev_name'], synchro_type_case(dic['state'])) for dic in self.bcv_info_dic_lst]))
        
        else:
            if self.bcv_flag:
                fmt = 'No[F]'
            else:
                fmt = 'No'
                
        return fmt
        
    def __radd__(self, other):
        return other + self.size


class SgroupInfo(DeviceGlobal):
    """Storage Group class"""
    
    def __init__(self, name, view, fast, type):
        DeviceGlobal.__init__(self)
        
        self.name = name
        self.view = bool(view)
        self.fast = bool(fast)
        self.type = sg_type_case(type)
        self.argument = False
        self.slo = False
        self.srp = False
        self.cascad = False
        self.lun = False
        self.lun_count = 0
        self.remove_lun = []
        
    def lun_info(self, lun_list, total_size):
        self.lun = True
        self.lun_list = lun_list
        self.total_size_mb = total_size
        self.lun_count = len(lun_list)
        
    def lun_to_remove(self, lun_list):
        self.remove_lun = self.remove_lun + lun_list
        
    def view_info(self, view):
        self.view_list = view
        self.view_count = len(view)
        
    def fast_info(self, fast, tier_list):
        self.fast_name = fast
        self.fast_tier_list = tier_list
        
    def slo_info(self, slo, srp):
        self.slo = True
        self.slo_name = slo
        self.fast_name = slo
        if srp:
            self.srp = True
            self.srp_name = srp
        
    def cascad_info(self, cascad_view, cascad_view_name, cascad_sgroup_dic_lst):
        self.cascad = True
        self.cascad_view = cascad_view
        self.cascad_view_name = cascad_view_name
        self.cascad_sgroup_name = [c['sgroup_name'] for c in cascad_sgroup_dic_lst]
        self.cascad_sgroup_type = set([c['status'] for c in cascad_sgroup_dic_lst])
        
        if len(self.cascad_sgroup_type) > 1:
            self.warning = True
        
        self.cascad_sgroup_type = ','.join(self.cascad_sgroup_type)


class ViewInfo(DeviceGlobal):
    """Masking View class"""
    def __init__(self, name, sg, ig, pg):
        DeviceGlobal.__init__(self)
        
        self.name = name
        self.sgroup = sg
        self.init = ig
        self.pgroup = pg
        self.lun = False
        self.login = False
        self.init_csc = False
        self.init_share = False
        self.init_remove = False
        
    def login_info(self, login):
        self.login = True
        self.login_list = login
        
    def init_info(self, mv_list):
        if len(mv_list) > 1:
            self.init_share = True
        self.init_view_list = mv_list
        
    def cascad_info(self, ig_list, ig_info_lst):
        self.init_csc = True
        self.init_child_list = ig_list
        self.init_child_count = len(ig_list)
        
        self.init_child_info = []
        
        for ig_info in ig_info_lst:
            ig_info['remove'] = False
            
            if len(ig_info['view_list']) > 1:
                ig_info['share'] = True
            else:
                ig_info['share'] = False
            
            self.init_child_info.append(ig_info)
            
    def lun_info(self, lun_list, total):
        self.lun = True
        self.lun_list = lun_list
        self.lun_total_size = size_conv(total, 'MB', True)
        self.lun_count = len(lun_list)


class LoginInfo(DeviceGlobal):
    """Login class"""
    def __init__(self, wwn):
        DeviceGlobal.__init__(self)
        
        self.wwn = wwn
        self.status = False
        self.port = False
        self.init = False
        self.init_share = False
        self.view_share = False
        self.port_count = 0
        
        self.status_log_in = 'No'
        self.status_on_fab = 'No'
        
    def port_info(self, port_info_dic):
        self.port = True
        self.status = True
        
        self.port_count = len(port_info_dic)
        
        self.status_log_in = login_stat([p_dic['logged_in'] for p_dic in port_info_dic])
        self.status_on_fab = login_stat([p_dic['on_fabric'] for p_dic in port_info_dic])
        self.status_fcid = ','.join(set([p_dic['fcid'] for p_dic in port_info_dic]))
        
        self.node_name = bool_check([p_dic['node_name'] for p_dic in port_info_dic][0], False)
        self.port_name = bool_check([p_dic['port_name'] for p_dic in port_info_dic][0], False)
        
        self.port_enable_dir_prt_list = []
        self.port_disable_dir_prt_list = []
        self.port_logged_dir_prt_list = []
        
        for port_dic in port_info_dic:
            if port_dic['on_fabric'] == 'Yes':
                self.port_enable_dir_prt_list.append('{0}:{1}'.format(port_dic['director'], port_dic['port']))
            else:
                self.port_disable_dir_prt_list.append('{0}:{1}'.format(port_dic['director'], port_dic['port']))
            
            if port_dic['logged_in'] == 'Yes':
                self.port_logged_dir_prt_list.append('{0}:{1}'.format(port_dic['director'], port_dic['port']))
            
        self.port_all_dir_prt_list = self.port_enable_dir_prt_list + self.port_disable_dir_prt_list
        
    def init_info(self, ig_info_lst):
        self.init = True
        self.init_cascad = False
        self.init_info_lst = ig_info_lst
        
        self.init_list = []
        self.view_list = []
        
        for ig_dic in ig_info_lst:
            self.init_list.append(ig_dic['ig_name'])
            
            for view in ig_dic['mv_list']:
                if ' *' in view:
                    self.init_cascad = True
                
                self.view_list.append(view.replace(' *', ''))
            
        self.init_count = len(self.init_list)
        self.view_count = len(self.view_list)
            
        if self.init_count > 1:
            self.init_share = True
        
        if self.view_count > 1:
            self.view_share = True
        
    @property
    def node_port_fmt(self):
        fmt = 'No'
        
        if self.node_name:
            fmt = '{0}/{1}'.format(self.node_name, self.port_name)
        
        return fmt
        
    @property
    def init_cnt_fmt(self):
        if self.init_count is not 0:
            return 'Yes[{0}]'.format(self.init_count)
        else:
            return 'No'
        
    @property
    def view_cnt_fmt(self):
        if self.view_count is not 0:
            return 'Yes[{0}]'.format(self.view_count)
        else:
            return 'No'
        
    @property
    def cig_cnt_fmt(self):
        if self.init_cascad:
            return 'Yes'
        else:
            return 'No'


class PoolInfo(DeviceGlobal):
    """Pool class"""
    def __init__(self, name, total, used, used_prc, subs_prc, lun_total_size, lun_total_consum_size):
        DeviceGlobal.__init__(self)
        
        self.name = name
        self.total_gb = int(total.split('.')[0])
        self.used_gb = int(used.split('.')[0])
        self.used_prc = int(used_prc)
        self.subs_prc = int(subs_prc)
        self.new_lun_total_size_gb = int(lun_total_size)
        self.new_lun_total_consum_size_gb = int(lun_total_consum_size)
        
        self.silo_pool_lst = []
        self.silo_count = 0
        self.silo_used_prc = 0
        self.silo_subs_prc = 0
        
        self.subs_gb = self.total_gb*self.subs_prc/100
        
        self.subs_gb_aft_lun_add = self.subs_gb + self.new_lun_total_size_gb
        self.subs_prc_aft_lun_add = self.subs_gb_aft_lun_add*100/self.total_gb
        
        self.gb_aft_lun_add = self.used_gb + self.new_lun_total_consum_size_gb
        self.prc_aft_lun_add = self.gb_aft_lun_add*100/self.total_gb 
        
        used_prc_float = self.used_gb*100/self.total_gb
        subs_prc_float = self.subs_gb*100/self.total_gb
        
        self.subs_prc_aft_lun_add_fmt = '{0:<3} [+{1}%]'.format(int(self.subs_prc_aft_lun_add), round(self.subs_prc_aft_lun_add-subs_prc_float, 1))
        self.prc_aft_lun_add_fmt = '{0:<2} [+{1}%]'.format(int(self.prc_aft_lun_add), round(self.prc_aft_lun_add-used_prc_float, 1))
        
        self.total_fmt = size_conv(self.total_gb, 'GB', rd=True)
        self.used_fmt = size_conv(self.used_gb, 'GB', rd=True)
        
        # WARNING / ERROR CHECK #
        
        error_msg_lst = []
        warning_msg_lst = []
        
        if self.used_prc >= 90:
            self.error = True
            error_msg_lst.append('Us>90%')
        elif int(self.subs_prc) >= 170:
            self.error = True
            error_msg_lst.append('Ov>170%')
        elif int(self.prc_aft_lun_add) >= 90:
            self.error = True
            error_msg_lst.append('Us+>90%')
        elif int(self.subs_prc_aft_lun_add) >= 170:
            self.error = True
            error_msg_lst.append('Ov+>170%')
        elif self.used_prc >= 85:
            self.warning = True
            warning_msg_lst.append('Us>85%')
        elif int(self.subs_prc) >= 150:
            self.warning = True
            warning_msg_lst.append('Ov>150%')
        elif int(self.subs_prc_aft_lun_add) >= 150:
            self.warning = True
            warning_msg_lst.append('Ov+>150%')
        
        if error_msg_lst:
            self.error_msg = '{0}:{1}'.format(self.name, ''.join(error_msg_lst))
        elif warning_msg_lst:
            self.warning_msg = '{0}:{1}'.format(self.name, ''.join(warning_msg_lst))
        
    def silo_info(self, pool_lst, id, count, used_prc, subs_prc):
        self.silo_pool_lst = pool_lst
        self.silo_id = id
        self.silo_count = count
        self.silo_used_prc = used_prc
        self.silo_subs_prc = subs_prc
        
    @property
    def silo_id_cnt(self):
        return '{0}[Pl:{1}]'.format(self.silo_id, self.silo_count)


class SRPInfo(DeviceGlobal):
    """SRP class"""
    def __init__(self, name, total, used, subs, lun_total_size, lun_total_consum_size):
        DeviceGlobal.__init__(self)
        self.name = name
        self.total_gb = int(total.split('.')[0])
        self.used_gb = int(used.split('.')[0])
        self.subs_gb = int(subs.split('.')[0])
        self.new_lun_total_size_gb = int(lun_total_size)
        self.new_lun_total_consum_size_gb = int(lun_total_consum_size)
        self.slo = False
        
        self.total_fmt = size_conv(self.total_gb, 'GB', rd=True)
        self.used_fmt = size_conv(self.used_gb, 'GB', rd=True)
        self.used_prc = self.used_gb/self.total_gb*100
        self.subs_prc = self.subs_gb/self.total_gb*100
        
        self.subs_gb_aft_lun_add = self.subs_gb + self.new_lun_total_size_gb
        self.subs_prc_aft_lun_add = self.subs_gb_aft_lun_add*100/self.total_gb
        
        self.gb_aft_lun_add = self.used_gb + self.new_lun_total_consum_size_gb
        self.prc_aft_lun_add = self.gb_aft_lun_add*100/self.total_gb 
        
        used_prc_float = self.used_gb*100/self.total_gb
        subs_prc_float = self.subs_gb*100/self.total_gb
        
        self.subs_prc_aft_lun_add_fmt = '{0:<3} [+{1}%]'.format(int(self.subs_prc_aft_lun_add), round(self.subs_prc_aft_lun_add-self.subs_prc, 1))
        self.prc_aft_lun_add_fmt = '{0:<2} [+{1}%]'.format(int(self.prc_aft_lun_add), round(self.prc_aft_lun_add-used_prc_float, 1))
        
        self.used_prc = int(self.used_prc)
        self.subs_prc = int(self.subs_prc)
        
        warning_msg_lst = []
        
        if self.used_prc >= 85:
            self.warning = True
            warning_msg_lst.append('Us>85%')
        elif int(self.subs_prc_aft_lun_add) >= 150:
            self.warning = True
            warning_msg_lst.append('Ov>150%')
            
        if warning_msg_lst:
            self.warning_msg = '{0}:{1}'.format(self.name, ''.join(warning_msg_lst))    
            
    def slo_info(self, slo_lst):
        self.slo = True
        self.slo_list = slo_lst


class FastInfo(DeviceGlobal):
    """Fast class"""
    def __init__(self, name, sg_count):
        DeviceGlobal.__init__(self)
        
        self.name = name
        self.sg_count = sg_count
        self.tier = False
        self.pool = False
     
    def tier_info(self, tier_list, tier_info):
        self.tier = True
        self.pool = True
        self.tier_list = tier_list
        self.tier_info = tier_info
        self.pool_list = [tier['pool_name'] for tier in tier_info]


class PortGroupInfo(DeviceGlobal):
    """SRP class"""
    def __init__(self, name, dir, port, mv):
        DeviceGlobal.__init__(self)
        
        self.name = name
        self.view_count = len(mv)
        self.dir_port = ['{0}:{1}'.format(d, p) for d, p in zip(dir, port)]

class RaGroupInfo(DeviceGlobal):
    """Ra Group class"""
        
    def __init__(self, rmt_id, ra_dic_lst):
        DeviceGlobal.__init__(self)
        
        self.rmt_id = rmt_id
        self.ra_group_label = [r['ra_group_label'] for r in ra_dic_lst][0]
        self.ra_group_num = [r['ra_group_num'] for r in ra_dic_lst][0]
        self.rmt_ra_group_num = [r['rmt_ra_group_num'] for r in ra_dic_lst][0]
        self.ra_port_id = [r['rmt_ra_port_id'] for r in ra_dic_lst]
        
        self.ra_port_id_count = len(self.ra_port_id)
        
        if self.ra_group_num != self.rmt_ra_group_num:
            self.warning = True
            self.warning_msg = 'Local RA and Remote RA is different'
        
        for r in ra_dic_lst:
            
            if r['link_sw'] == 'N/A':
                self.error = True
                self.error_msg = 'RA Link Not Available'
                
            else:
                del r['ra_group_label']
                del r['ra_group_num']
                del r['rmt_id']
                del r['rmt_ra_group_num']
            
        self.ra_port_dic_lst = ra_dic_lst
        
        