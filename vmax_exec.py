#!/usr/bin/python
# -*- coding: utf-8 -*-
#
#---------------------------------------------------------------------------
# Script    : vmax_exec.py                                                 |
# Author    : L.Koné                                                       |
# Language  : Pyhton 2                                                     |
# Lib Dir   : ./py_vmax_lib                                                |
# Version   : v1.01                                                        |
# Date      : 03/10/2017                                                   |
#---------------------------------------------------------------------------

#================================================================================#
# ------------------------------- IMPORT LIBRARY ------------------------------- #
#================================================================================#

#~~~~# PYTHON LIBRARY #~~~~#

import signal
import time
import os

#~~~~# LOCAL LIBRARY #~~~~#

try:
    from py_vmax_lib.class_global import GlobalMode
    from py_vmax_lib.class_audit import AuditMode
    from py_vmax_lib.class_create import CreateMode
    from py_vmax_lib.class_remove import RemoveMode
    from py_vmax_lib.class_modify import ModifyMode
    from py_vmax_lib.class_migrate import MigrateMode

    from py_vmax_lib.func_global import *
    from py_vmax_lib.func_check import bay_ping

except ImportError:
    print '<!> Modules import Error ! Check Lib dir [./py_vmax_lib]'
    exit(1)
    
#==============================================================================#
# ------------------------------- CONSTANT VAR ------------------------------- #
#==============================================================================#

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Variable du Mode DEV #

DEV_MODE = False

# Liste des utilisateurs authorisé à executer le script #

AUTH_USER_LST = ['root', 'admvmax']

#==============================================================================#
# ------------------------------- MODULE START ------------------------------- #
#==============================================================================#

# @function_check
def signal_close(signal, frame):
    """ Fonction : Fonction appellé en cas d'appuie sur les touches [Ctrl-C] """
    
    mprint()
    
    if TMP_FILE:
        remove_file(TMP_FILE)
        
    mprint("SIGINT Signal Received", 'err', logger=LOGGER)


def main():
    """ Fonction : Corp du script """
    
    # Déclaration des CONSTANTES #
    
    global LOGGER
    global TMP_FILE
    
    LOGGER = False
    TMP_FILE = False
    SESSION_ID = str(random.random())[2:8]
    
    # Vérification User Courant #
    
    user_check(AUTH_USER_LST)
    
    # Initialisation du Fichier de Config #
    
    CONFIG_PATH = CURRENT_DIR
    
    if DEV_MODE:
        LOG_PATH = os.path.abspath(os.path.dirname(sys.argv[0]))
        TMP_PATH = '/tmp'
        
        mprint(color_str('  --o>>>>>>>>>>>>>>>> [MODE DEV] <<<<<<<<<<<<<<<<o--  ', 'blu'), tbc=1)
        
    else:
        CONFIG = config_exec(CONFIG_PATH)
        LOG_PATH = CONFIG['LOG']['PATH']
        TMP_PATH = CONFIG['TMP']['PATH']
          
    # Initialisation du Signal Handler #
    
    signal.signal(signal.SIGINT, signal_close)
    
    # Check des arguments #
    
    glob = GlobalMode(TMP_PATH, CONFIG_PATH)
    glob.argument_check()
    
    # Génération d'un dict avec les arguments du script #
    
    glob_dic = glob.__dict__
    debug_fmt(glob.debug_mode, glob_dic)
    
    # Récupération du fichier temp [Mode Création/Suppression/Modification] #
    
    TMP_FILE = glob_dic['tmp_file']
    
    # Initialisation du LOGGER #
    
    if glob.tmpsg_mode:
        glob.user = glob.user + ':SG_Clean'
    
    LOGGER = logger_exec(glob.user, glob.sid, glob.mode, SESSION_ID, glob.debug_mode, LOG_PATH, DEV_MODE)
    
    # Démarrage des Modes ###
    
    mode_fmt = '{0} MODE'.format(glob.mode.upper())
    
    if glob.select:
        mode_fmt = '{0} [SELECTION -X]'.format(mode_fmt)
    else:
        mprint('{0} Mode (S:{1}) - Start'.format(glob.mode.capitalize(), SESSION_ID), 's1', tac=1, tbc=1, logger=LOGGER)
        
    LOGGER.info('[SCRIPT_START] {0}'.format(mode_fmt))
    
    # Test de Ping Vmax #
    
    bay_ping(glob_dic['array_id'], glob_dic['export'], LOGGER)
    
    if glob.mode == 'audit':
        audit = AuditMode(glob_dic, LOGGER)
        audit.info_retrieve()
        audit.info_display()
        
    elif glob.mode == 'remove':
        remove = RemoveMode(glob_dic, LOGGER)
        remove.info_retrieve()
        remove.mode_check()
        remove.info_display()
        remove.mode_exec()
        
    elif glob.mode == 'modify':
        modify = ModifyMode(glob_dic, LOGGER)
        modify.info_retrieve()
        modify.mode_check()
        modify.mode_exec()
        
    elif glob.mode == 'create':
        create = CreateMode(glob_dic, LOGGER)
        create.mode_check()
        create.info_retrieve()
        create.mode_exec()
        
    elif glob.mode == 'migrate':
        migrate = MigrateMode(glob_dic, LOGGER)
        migrate.info_retrieve()
        migrate.mode_check()
        migrate.info_display()
        migrate.mode_exec()
        
    sc_exit(0, mode=glob.mode, start_time=glob.script_start_time, logger=LOGGER)


if __name__ == '__main__':
    main()
    
    
    
