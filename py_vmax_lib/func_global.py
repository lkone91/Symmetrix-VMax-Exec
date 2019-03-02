# -*- coding: utf-8 -*-

#================================================================================#
# ------------------------------- IMPORT LIBRARY ------------------------------- #
#================================================================================#

#~~~~# PYTHON LIBRARY #~~~~#

from __future__ import division

import os
import re
import sys
import random
import json
import datetime
import time
import functools
import subprocess
import xml.etree.ElementTree as xmltree

from pprint import pprint, pformat
from operator import attrgetter, itemgetter

#========================================================================#
# ------------------------------- CONFIG ------------------------------- #
#========================================================================#

def config_exec(config_path):
    """ Fonction : Recuperation du fichier de configuration au format JSON """
    
    conf_file = config_path + '/conf_vmax_exec.json'
    
    try:
        with open(conf_file, 'r') as json_f:
            conf_json = json.load(json_f)
    
    except IOError:
        mprint('Config File [IO Error] : <{0}> not Find'.format(conf_file), 'cri', no_end=True)
    
    except ValueError:
        mprint('Config File [Value Error] : Config File <{0}> Read Problem [JSON Bad Syntax]'.format(conf_file), 'cri', no_end=True)
    
    except:
        mprint('Config File [Problem] : Load conf file problem', 'cri', no_end=True)
    
    return conf_json
    
    
def list_array_file(config_path):
    """ Fonction : Recuperation du fichier avec la liste des baies au format JSON """
    
    array_list_file = config_path + '/vmax_list_array.json'
    
    try:
        with open(array_list_file, 'r') as json_f:
            array_dic_lst = json.load(json_f)
    
    except:
        mprint('Bay Config File <{0}> [Problem] : Load File Error'.format(array_list_file), 'cri', no_end=True)
    
    return array_dic_lst
    
#========================================================================#
# ------------------------------- LOGGER ------------------------------- #
#========================================================================#

# @function_check
def logger_exec(user, sid, mode, session_id, debug_mode=False, log_path='.', dev_mode=False):
    """ Fonction : Initialisation du Logger """
    
    import logging
    from logging.handlers import RotatingFileHandler
    
    log_path = log_path + '/log_vmax_exec.d' 
    
    if not os.path.isdir(log_path):
        try:
            os.mkdir(log_path)
        except OSError:
            mprint('Log Dir Creation Error', 'cri', no_end=True)
    
    log_file = '{0}/log_vmax_exec.log'.format(log_path)
    
    def mode_retrieve_case(m):
        return {'remove': 'RMV', 'audit': 'AUD', 'create': 'CRT', 'modify': 'MDF', 'select':'SLC', 'migrate':'MIG'}[m]
    
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter('%(asctime)s {0} {1} {2} {3} %(levelname)s > %(message)s'.format(user, session_id, mode_retrieve_case(mode), sid), "%Y/%m/%d %H:%M:%S")
    
    if debug_mode:
        steam_handler = logging.StreamHandler()
        steam_handler.setLevel(logging.DEBUG)
        steam_handler.setFormatter(formatter)
        logger.addHandler(steam_handler)
        
    else:
        file_handler = RotatingFileHandler(log_file, 'a', 1000000, 100)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


#===========================================================================#
# ------------------------------- DECORATORS ------------------------------ #
#===========================================================================#

def function_check(func):
    """ Decorator (Fonction) : Test si la fonction en argument s'execute correctement et retourne le type d'erreur si une erreur survient """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as ex:
            mprint('function [{0}] return error type [{1}], message [{2}]'.format(func.__name__, type(ex).__name__, ex), 'cri')
        
    return wrapper

    
def benchmark(func):
    """ Decorator (Fonction) : Temps d'execution de la fonction en argument (Benchmark) """
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t = time.clock()
        res = func(*args, **kwargs)
        mprint(func.__name__, time.clock()-t)
        return res
        
    return wrapper
    
#=============================================================================#
# ------------------------------- GLOBAL FUNC ------------------------------- #
#=============================================================================#

def sc_exit(return_code, no_end=False, logger=False, mode='', start_time=''):
    """ Fonction : Quitte le script """
    
    mprint()
    
    if return_code:
        if return_code is 86:
            if not no_end:
                mprint('End', 's1', tac=1)
                
                if logger:
                    logger.info('[SCRIPT_END] ')
                    
        else:
            if not no_end:
                mprint('Stop [Return Error Code {0}]'.format(return_code), 's1', tac=1)
                
                if logger:
                    logger.error('[SCRIPT_STOP] : ERROR CODE : {0}'.format(return_code))
        
    else:
        if not no_end:
            mprint('{0} Mode - End [Time {1}]'.format(mode.capitalize(), time.strftime("%H:%M:%S", time.gmtime((time.time() - start_time)))), 's1', tac=1, logger=logger)
            
            if logger:
                logger.info('[SCRIPT_END] {0} MODE [TIME {1}]'.format(mode.upper(), time.strftime("%H:%M:%S", time.gmtime((time.time() - start_time)))))
            
    sys.exit(0)

def mprint(
        text='',
        mode='n',
        mrg = '.',
        mrg2=' ',
        end='\n',
        sep=' ',
        line='',
        exit=True,
        no_end=False,
        print_return=True,
        logger=False,
        tbc=False,
        tac=False,
    ):
    
    """ Fonction : Affiche le texte au format souhaite """
    
    marge = '{0}{1}'.format(mrg, mrg2)
    
    d = time.strftime("%y/%m/%d")
    t = time.strftime("%H:%M:%S")
    
    t2_l = '-'
    t3_l = '~'
    
    if line:
        t2_l = line
        t3_l = line
    
    if mode == 'n': result = '{0}{1}'.format(marge, text)
    elif mode == 'n2': result = '{0} \033[7m {1} \033[0m'.format(marge, text)
    elif mode == 's1': result = '{0} o-> Vmax.Exec {1} [{2}][{3}] <-o'.format(marge, text, d, t)
    elif mode == 'd1': result = '{0}[{1}] {2}'.format(marge, t, text)
    elif mode == 'd2': result = '{0}[{1}][{2}] {3}'.format(marge, d, t, text)
    elif mode == 't1': result = '{0}{1}\n{2}{3}'.format(marge, text, mrg, '.'*40) 
    elif mode == 't2': result = '{0}{1}\n{2}{3}'.format(marge, text, marge, t2_l*len(text)) 
    elif mode == 't3': result = '{0} o-> {1}\n{2}     {3}'.format(marge, text, marge, t3_l*len(text))
    elif mode == 'cri': result = '{0}\033[30m\033[41m <!> [Critical] {1} \033[0m'.format(marge, text)
    elif mode == 'err': result = '{0}\033[30m\033[41m <!> [Error] {1} \033[0m'.format(marge, text)
    elif mode == 'war': result = '{0}\033[30m\033[43m <!> [Warning] {1} \033[0m'.format(marge, text) 
    elif mode == 'inf': result = '{0}\033[44m <> [Info] {1} \033[0m'.format(marge, text) 
    elif mode == 'arg_err':
        result = '{0}\n{1}\033[30m\033[41m <!> [Agument Error] {2} \033[0m [-h|-help for Help]'.format(marge, marge, text)
        no_end=True
        
    if tbc is False and re.search('cri|err|war|inf', mode):
        tbc = 1
        
    if logger:
        if mode == 'cri': logger.critical(text)
        elif mode == 'err': logger.error(text)
        elif mode == 'war': logger.warning(text)
        elif mode == 'inf': logger.info(text)
    
    tab_before = ['']
    tab_after = ['']
    
    if tbc:
        tab_before = ['{0}\n'.format(mrg) for x in range(tbc)]
        
    if tac:
        tab_after = ['\n{0}'.format(mrg) for x in range(tac)]
        
    result = '{0}{1}{2}'.format(''.join(tab_before), result, ''.join(tab_after))
        
    if print_return:
        
        sys.stdout.write('{0}{1}'.format(result, end))
        sys.stdout.flush()
        
        if mode == 'err' and exit:
            sc_exit(86, no_end=no_end, logger=logger)
        elif mode == 'cri' and exit:
            sc_exit(16, no_end=no_end, logger=logger)
        elif mode == 'arg_err':
            sc_exit(0, no_end=no_end)
            
    else:
        return result[(len(mrg)+len(mrg2)):]
        
def color_str(text, color):
    """ Fonction : Colore l'input """
    
    if color == 'red': result = '\033[30m\033[41m{0}\033[0m'.format(text)
    elif color == 'yel': result = '\033[30m\033[43m{0}\033[0m'.format(text)
    elif color == 'blu': result = '\033[44m{0}\033[0m'.format(text)
    elif color == 'rev': result = '\033[7m{0}\033[0m'.format(text)
    
    return result
    
def debug_fmt(debug_mode, dic):
    """ Fonction : Affiche l'input si le mode debug est active """
    
    if debug_mode:
        result = color_str(pformat(dic), 'blu')
        
        mprint(result)
    
def empty_result_fmt(text, result_fmt = '-'):
    """ Fonction : Retourne des tirets si l'input est vide """
    
    if not text:
        text = result_fmt
    return text
    
def rtr_dict_list(cls_lst, key, uniq=False, join=False, concat=False, filter=False, mode_cls=True):
    """ Fonction : Retourne une liste formatee selon les arguments """
    
    result = []
    
    for cls in cls_lst:
        
        if mode_cls:
            dic = cls.__dict__
        else:
            dic = cls
            
        if dic.get(key, False):
            
            if join:
                result.append(','.join(dic[key]))
                
            elif concat:
                if filter and dic[filter.split(':')[0]] == filter.split(':')[1]:
                    result = result + dic[key]
                    
                elif not filter:
                    result = result + dic[key]
            else:
                result.append(dic[key])
                
    if uniq:
        result = list(set(result))
        
    return result
    
def select_choice(choice_list, choice_list_display = [], type=False, title=False, multi=False, mode=False, default='', display_orginal_lst=False):
    """ Fonction : liste de choix """
    
    if len(choice_list) > 1:
        check = 1
        choice_list = [False] + choice_list
        
        def_fmt = ''
        
        if choice_list_display:
            choice_list_display = [False] + choice_list_display
        
        else:
            choice_list_display = list(choice_list)
        
        if multi:
            msg = 'Enter your Choice(s)'
        else:
            msg = 'Enter your Choice'
        
        if mode: msg = '{0} [0 to Return]'.format(msg)
        
        while check is not 0:
            
            mprint()
            
            if title:
                mprint(title)
                mprint()
            elif type:
                mprint('(-) Select {0} (-)'.format(type), 't1')
                mprint()
            
            msg_err = ''
            check_c = 1
            
            if default:
                def_fmt = '[Default : {0}]'.format(default)
            
            for y, choice in enumerate(choice_list_display[1:]):
                mprint('{0:>6} -> {1:<12}'.format('[{0}]'.format(y+1), choice))
                    
            mprint()
            
            while check_c is not 0:
                result = []
                result_display = []
                choice_id_lst = raw_input(". o-> {0} {1} {2} : ".format(msg, def_fmt, color_str(msg_err, 'red'))).split(',')
                
                if choice_id_lst == [''] and default:
                    result.append(default)
                    result_display.append(default)
                    check_c = 0
                
                else:
                    for choice_id in choice_id_lst:
                        
                        if not multi:
                            if len(choice_id_lst) > 1:
                                break
                        
                        if re.search('^[0-9]+$', choice_id):
                            choice_id = int(choice_id)
                            
                            if mode and choice_id == 0:
                                return 0
                                
                            elif choice_id > len(choice_list_display)-1 or choice_id == 0:
                                break
                                
                            else:
                                result.append(choice_list[choice_id])
                                result_display.append(choice_list_display[choice_id])
                                check_c = 0
                                
                        else:
                            
                            break
                
                if check_c is 0:
                    check = 0
                else:
                    msg_err = '[!Bad Choice]'
                    
    else:
        result_display = choice_list_display
        result = choice_list       
           
    if display_orginal_lst:
        display_result = ','.join(result)
    else:
        display_result = ','.join(result_display)
    
    if not multi:
        result = ''.join(result)
    
    if not mode:
        mprint() 
        mprint('{0} Selected : {1}'.format(type, display_result), 'n2')
    
    return result
  

def text_input(title, syntax='', out_type='', lst_sep=',', regex=False, lst=False, multi=False, default=False, type=''):
    """ Fonction : input de texte avec un retour different selon l'option (bool|text|list) """
    
    check = 1
    msg_err = ''
     
    if lst: syntax = "['List' to Full Display]"
    
    while check is not 0:
        choice = raw_input(". o-> {0} {1} \033[33m\033[41m{2}\033[0m : ".format(title, syntax, msg_err))
        
        if not choice and default:
            choice = default
        
        if choice:
            
            if out_type == 'lst':
                result = choice.split(lst_sep)
                check = 0
                
            elif out_type == 'int':
                if re.search('^[0-9]+$', choice):
                    result = int(choice)
                    check = 0
                    
            elif out_type == 'bool':
                
                if re.search('^(y|yes|n|no)$', choice.lower()):
                    if re.search('^(y|yes)$', choice.lower()):
                        result = True
                    else : 
                        result = False
                    check = 0
                    
            elif out_type == 'rgx':
                if re.search(regex, choice.lower()):
                    result = choice
                    check = 0
                 
            elif out_type == 'choice':
                
                msg_err = ''
                
                new_lst = [l for l in lst if choice.lower() in l.lower()]
                  
                if choice == 'List':
                    result = select_choice(lst, multi=multi, mode=1)
                    if result is not 0:
                        check = 0
                    else:
                        mprint()
                    
                elif not new_lst:
                    msg_err = '[!{0} Not Find]'.format(choice)
                    
                elif len(new_lst) > 1:
                    result = select_choice(new_lst, multi=multi, mode=1)
                    if result is not 0:
                        check = 0
                    else:
                        mprint()
                    
                else:
                    result = ','.join(new_lst)
                    check = 0
                    
                if check is 0:
                    mprint()
                    mprint('{0} Selected : {1}'.format(type, result), 'n2')
                    
            else:
                result = choice
                check = 0
                
    return result

def write_file(line_lst, file_name, mode, file_title, logger=False, verbose=False):
    """ Fonction : Ecriture d'une liste dans un fichier texte """
    
    if mode == 'display':
        mprint('(-) {0}'.format(file_title))
        if verbose:
            mprint()
            for line in line_lst:
                mprint('  + {0}'.format(line))
        
    elif mode == 'exec':
        mprint('(-) {0}'.format(file_title), 'd1', end=' ')
        
        if logger:
            logger.info('[FILE] {0} ({1})'.format(file_title, file_name))
        
        with open(file_name, 'w') as f:
            for line in line_lst:
                f.write('{0}\n'.format(line))
        
        print '[Done]'
        
    mprint()
    
    
    
def remove_file(file_name):
    """ Fonction : Suppression d'un fichier texte si il existe """
    
    if os.path.isfile(file_name):
        
        try:
            os.remove(file_name)
        except:
            mprint('Remove File Problem [{0}]'.format(file_name), 'err')
        else:
            return 0

def size_conv(size, type, rd=False, rd_dcm=1):
    """ Fonction : Convertisseur de valeur """
    
    if type == 'KB': 
        if size > 1024: size = size/1024; type = 'MB'
    if type == 'MB':
        if size > 1024: size = size/1024; type = 'GB'     
    if type == 'GB':
        if size > 1024: size = size/1024; type = 'TB'
        
    if rd:
        result = '{0} {1}'.format(round(size, rd_dcm), type)
    else:
        result = '{0} {1}'.format(int(size), type)
        
    return result
    
def percent_fmt(value, total_value):
    """ Fonction : Formatage du pourcentage """
     
    result = value*100/total_value
    result = round(result, 1)
    
    if '100.0' in str(result):
        result = int(result)
    
    return result
    
    
def line_create(list, char='-', x=1):
    """ Fonction : Createur de ligne avec list en input """
    
    result = []
    for l in list:
        if isinstance(l, int): result.append((l-x)*char)
        else: result.append(len(l)*char)
    return result


def key_check(cls, key, cls_mode=True):
    """ Fonction : Verification de la presence d'une clef dans une classe """
    
    if cls_mode:
        result = getattr(cls, key, 'No')
    else:
        result = cls.get(key, 'No')
    
    if isinstance(result, int):
        result = str(result)
    elif isinstance(result, list):
        if result:
            result = ','.join(result)
        else:
            result = 'No'
            
    return result
    
def table_display(cls_lst, keys, row_title, marge=2, cls_mode=True, reverse=False, color_stx=True, sort_key=False):
    """ Fonction : Affichage d'un tableau avec une classe en input """
    
    max_list = []
    
    for x, k in enumerate(keys):
        c_list = [len(key_check(cls, k, cls_mode)) for cls in cls_lst]
        c_list.append(len(row_title[x]))
        max_list.append(max(c_list) + marge)
        
    raw = ' {0}'.format(''.join(['{0}{1}{2}{3}{4}'.format('{', y, ':<', m, '}') for y, m in enumerate(max_list)]))
    
    mprint(raw.format(*row_title))
    mprint(raw.format(*(line_create(max_list))))
    
    if sort_key:
        sort_key = sort_key.split(',')
    else:
        sort_key = [keys[0]]
    
    if cls_mode:
        # sort_key = ['error', 'warning', 'display'] + sort_key
        sort_get = attrgetter(*sort_key)
    else:
        sort_get = itemgetter(*sort_key)
        
    for cls in sorted(cls_lst, key=sort_get, reverse=reverse):
        
        raw_fmt = raw
        
        if cls_mode and color_stx:
            if cls.display:
                raw_fmt = color_str(raw, 'blu')     
            elif cls.error:
                raw_fmt = color_str(raw, 'red')
            elif cls.warning:
                raw_fmt = color_str(raw, 'yel')
            elif cls.info:
                raw_fmt = color_str(raw, 'rev')
            
        mprint(raw_fmt.format(*(key_check(cls, k, cls_mode) for k in keys)))
            
def cmd_wait(cmd, t=.15, m=' '):
    """ Fonction : Affichage d'un widget de chargement pendant l'xecution des commandes en mode execution """
    
    for i in ['o--', '-o-', '--o', '-o-']:
        mprint("{0}{1}[{2}]{3}".format(cmd, m, i, ' '*2), end='\r')
        time.sleep(t)
    
def progress_wait(d_display, d_count, t_count, r_count, s_time):
    
    if d_count != t_count:
        
        while r_count is not 0:
            
            progress = progressbar(
                d_count,
                t_count,
                '[R:{0}]'.format(str(r_count).zfill(3)),
                msg_b='',
                sep=' ',
                display=False
            )
            
            mprint(d_display.format(str(d_count).zfill(3), str(t_count).zfill(3), progress), end='\r')
            r_count -= 1
            time.sleep(1)
            
    else:
        
        progress = progressbar(
            d_count,
            t_count,
            '[Time {0}]'.format(time.strftime("%H:%M:%S", time.gmtime((time.time() - s_time)))),
            msg_b='',
            sep=' ',
            msg_marg=False,
            display=False
        )
        
        mprint(d_display.format(str(d_count).zfill(3), str(t_count).zfill(3), progress), 'd1', tac=1)

def user_check(auth_user_lst):
    current_user = os.environ['USER']
    
    if current_user not in auth_user_lst:
        mprint('<!> [{0}] Bad User for Script Execution, Authorized Users : {1}'.format(
            current_user,
            ','.join(auth_user_lst)
        ))
        sys.exit(1)
        
def user_retrieve():
    """ Fonction : Recuperation de l'utilisateur courant """
    
    current_user = os.popen('logname').read().replace('\n', '')
    
    return current_user
    
def rows_colums_retrieve():
    """ Fonction : Recuperation de la taille de la fenetre [rows et colums] """
    
    rows, columns = os.popen('stty size', 'r').read().split()
    return rows, columns
    

def progressbar(c, t, msg, b_sz=15, msg_b='[R]', f='[]', f_load='o', e_load='-', sep=' | ', msg_marg=True, display=True ):
    """ Fonction : Barre de progression """
    
    end = '\r'
    percent = (" {0:>3}%".format(int(c*100/t)))
    b_pr = int(c*b_sz/t)
    
    if msg:
        if c == t:
            end = '\n'
            
            if msg_marg:
                msg = '{0:<20} [Done]'.format(msg)
            else:
                msg = '{0} [Done]'.format(msg)
                
        msg = '{0}{1}{2}'.format(sep, msg, ' '*5)
        
    bar = msg_b + ' ' + f[0] + f_load*b_pr + e_load*(b_sz-b_pr) + f[1] + percent + msg
    
    if display:
        mprint('{0}{1}'.format(bar, ' '*5), end=end)
    else:
        return bar
    
  
def bool_check(var, bool_mode=True):
    """ Fonction : Check de l'input et transformation en booleen [True|False] """ 
    
    if re.search('^(n/a|no|none|false|null)$', var.lower()):
        result = False
    else:
        if bool_mode: result = True
        else: result = var
        
    return result
  
# @function_check
def login_stat(status):
    """ Fonction : Check de l'etat des Logins (VMAX) """
    
    status_count = sorted([{cnt : status.count(cnt)} for cnt in set(status)])
    
    if len(status_count) != 1:
        result = 'Y({0})/N({1})'.format(status_count[1]['Yes'], status_count[0]['No'])
    else:
        result = '{0}({1})'.format(''.join(set(status)), len(status))
    
    return result

# @function_check
def dev_range_retrieve(dev_range):
    """ Fonction : Convertit un range de Luns VMAX Hexa (Exemple 0025E:0026A) en liste (VMAX) """
    
    dec_first = int(dev_range.split(':')[0], 16)
    dec_last = int(dev_range.split(':')[1], 16)
    result = [hex(dec).replace('0x', '0').rjust(5, '0').upper() for dec in range(dec_first, dec_last+1)]
    
    return result

def lst_splt(lst, cnt):
    return [lst[i:i + cnt] for i in xrange(0, len(lst), cnt)]

def sg_type_case(status):
    """ Fonction : Case avec le type de SG [normal|child|parent] (VMAX)"""
    
    return {'N/A': 'normal', 'IsParent': 'parent', 'IsChild': 'child'}.get(status, '-')

def synchro_type_case(x):
    """ Fonction : Case avec le type de Synchro SRDF (VMAX) """
    
    return {
        'Split'         :   'Splt',
        'Synchronized'  :   'Sync',
        'Synchronous'   :   'Sync',
        'Partitioned'   :   'Part',
        'Suspended'     :   'Susp',
        'Failed Over'   :   'F.Ov',
        'Invalid'       :   'Invd',
        'SyncInProg'    :   'SynP',
        'CopyInProg'    :   'CinP',
        'Copied'        :   'Copd',
        'Copy'          :   'Copy',
        'PreCopy'       :   'P.Cp',
        'Restored'      :   'Rest',
        'ActiveActive'  :   'AcAc',
        'ActiveBias'    :   'AcBi',
    }.get(x, 'Unkn')


    
