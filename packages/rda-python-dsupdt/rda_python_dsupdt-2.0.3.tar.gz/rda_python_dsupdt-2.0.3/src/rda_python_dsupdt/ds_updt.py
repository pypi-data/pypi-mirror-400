#!/usr/bin/env python3
#
##################################################################################
#
#     Title: dsupdt
#    Author: Zaihua Ji, zji@ucar.edu
#      Date: 10/10/2020
#            2025-02-05 transferred to package rda_python_dsupdt from
#            https://github.com/NCAR/rda-utility-programs.git
#   Purpose: python utility program to download remote files,
#            process downloaded files and create local file, and
#            archive local files onto RDA Server
#            save information of web online data files or Saved files into RDADB
#
#    Github: https://github.com/NCAR/rda-python-dsupdt.git
#
##################################################################################
#
import sys
import os
import re
from os import path as op
from rda_python_common import PgLOG
from rda_python_common import PgSIG
from rda_python_common import PgLock
from rda_python_common import PgCMD
from rda_python_common import PgFile
from rda_python_common import PgUtil
from rda_python_common import PgOPT
from rda_python_common import PgDBI
from rda_python_common import PgSplit
from . import PgUpdt

TEMPINFO = {}
TOPMSG = SUBJECT = ACTSTR = None
ALLCNT = 0
DEFTYPES = {'WT' : 'D', 'ST' : 'P', 'QT' : 'B'}

#
# main function to run dsupdt
#
def main():

   global SUBJECT
   PgOPT.parsing_input('dsupdt')
   PgUpdt.check_enough_options(PgOPT.PGOPT['CACT'], PgOPT.PGOPT['ACTS'])
   start_action()

   if SUBJECT and 'NE' not in PgOPT.params and (PgLOG.PGLOG['ERRCNT'] or 'EE' not in PgOPT.params):
      SUBJECT += " on " + PgLOG.PGLOG['HOSTNAME']
      PgLOG.set_email("{}: {}".format(SUBJECT, TOPMSG), PgLOG.EMLTOP)
      if ACTSTR: SUBJECT = "{} for {}".format(ACTSTR, SUBJECT)
      if PgSIG.PGSIG['PPID'] > 1: SUBJECT += " in CPID {}".format(PgSIG.PGSIG['PID'])
      if PgLOG.PGLOG['ERRCNT'] > 0: SUBJECT += " With Error"
      if PgLOG.PGLOG['DSCHECK']:
         PgDBI.build_customized_email("dscheck", "einfo", "cindex = {}".format(PgLOG.PGLOG['DSCHECK']['cindex']),
                                      SUBJECT, PgOPT.PGOPT['wrnlog'])
      elif PgOPT.PGOPT['UCNTL']:
         PgDBI.build_customized_email("dcupdt", "einfo", "cindex = {}".format(PgOPT.PGOPT['UCNTL']['cindex']),
                                      SUBJECT, PgOPT.PGOPT['wrnlog'])
      else:
         PgLOG.pglog(SUBJECT, PgOPT.PGOPT['wrnlog']|PgLOG.SNDEML)
   
   if PgLOG.PGLOG['DSCHECK']:
      if PgLOG.PGLOG['ERRMSG']:
         PgDBI.record_dscheck_error(PgLOG.PGLOG['ERRMSG'])
      else:
         PgCMD.record_dscheck_status("D")
   
   if PgOPT.OPTS[PgOPT.PGOPT['CACT']][2]: PgLOG.cmdlog()   # log end time if not getting only action
   
   PgLOG.pgexit(0)

#
# start action of dsupdt
#
def start_action():

   global ALLCNT
   
   if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['CU'][0]:
      if 'CI' in PgOPT.params:
         if PgUpdt.cache_update_control(PgOPT.params['CI'][0], 1):
             check_dataset_status()
      else:
         ALLCNT = PgOPT.get_option_count(["ED", "EH"])
         check_dataset_status(0)
   elif PgOPT.PGOPT['ACTS'] == PgOPT.OPTS['DL'][0]:
      if 'CI' in PgOPT.params:
         ALLCNT = len(PgOPT.params['CI'])
         delete_control_info()
      elif 'RF' in PgOPT.params:
         ALLCNT = len(PgOPT.params['RF'])
         delete_remote_info()
      else:
         ALLCNT = len(PgOPT.params['LI'])
         delete_local_info()
   elif PgOPT.OPTS[PgOPT.PGOPT['CACT']][0]&PgOPT.OPTS['GA'][0]:
      get_update_info()
   elif PgOPT.PGOPT['CACT'] == 'PC':
      process_update_controls()
   elif PgOPT.PGOPT['ACTS'] == PgOPT.OPTS['SA'][0]:
      if 'IF' not in PgOPT.params:
         PgOPT.action_error("Missing input file via Option -IF")
      if PgOPT.get_input_info(PgOPT.params['IF'], 'DCUPDT'):
         PgUpdt.check_enough_options('SC', PgOPT.OPTS['SC'][0])
         ALLCNT = len(PgOPT.params['CI'])
         set_control_info()
      if PgOPT.get_input_info(PgOPT.params['IF'], 'DLUPDT'):
         PgUpdt.check_enough_options('SL', PgOPT.OPTS['SL'][0])
         ALLCNT = len(PgOPT.params['LI'])
         set_local_info()
      if PgOPT.get_input_info(PgOPT.params['IF'], 'DRUPDT') and PgOPT.params['RF']:
         PgUpdt.check_enough_options('SR', PgOPT.OPTS['SR'][0])
         ALLCNT = len(PgOPT.params['RF']) if 'RF' in PgOPT.params else 0
         set_remote_info()
   elif PgOPT.PGOPT['ACTS'] == PgOPT.OPTS['SC'][0]:
      ALLCNT = len(PgOPT.params['CI'])
      set_control_info()
   elif PgOPT.PGOPT['ACTS'] == PgOPT.OPTS['SL'][0]:
      ALLCNT = len(PgOPT.params['LI'])
      set_local_info()
   elif PgOPT.PGOPT['ACTS'] == PgOPT.OPTS['SR'][0]:
      ALLCNT = len(PgOPT.params['RF'])
      set_remote_info()
   elif PgOPT.PGOPT['ACTS']&PgOPT.OPTS['UF'][0]:
      if 'CI' in PgOPT.params:
         if PgUpdt.cache_update_control(PgOPT.params['CI'][0], 1): dataset_update()
      else:
         ALLCNT = PgOPT.get_option_count(["ED", "EH"])
         dataset_update()
   elif PgOPT.PGOPT['ACTS'] == PgOPT.OPTS['UL'][0]:
      if 'CI' in PgOPT.params:
         ALLCNT = len(PgOPT.params['CI'])
         unlock_control_info()
      if 'LI' in PgOPT.params:
         ALLCNT = len(PgOPT.params['LI'])
         unlock_update_info()

#
# delete update control records for given dsid and control indices
#
def delete_control_info():

   s = 's' if ALLCNT > 1 else ''
   PgLOG.pglog("Delete {} update control record{} ...".format(ALLCNT, s), PgLOG.WARNLG)

   delcnt = modcnt = 0
   for i in range(ALLCNT):
      cidx = PgLock.lock_update_control(PgOPT.params['CI'][i], 2, PgOPT.PGOPT['extlog'])
      if cidx <= 0: continue
      ccnd = "cindex = {}".format(cidx)
      delcnt += PgDBI.pgdel("dcupdt", ccnd, PgOPT.PGOPT['extlog'])
      modcnt += PgDBI.pgexec("UPDATE dlupdt SET cindex = 0 WHERE " + ccnd, PgOPT.PGOPT['extlog'])

   PgLOG.pglog("{} of {} update control record{} deleted".format(delcnt, ALLCNT, s), PgOPT.PGOPT['wrnlog'])
   if modcnt > 0:
      s = 's' if modcnt > 1 else ''
      PgLOG.pglog("{} associated local file record{} modified".format(modcnt, s), PgOPT.PGOPT['wrnlog'])

#
# delete local files for given dsid and locfile indices
#
def delete_local_info():

   s = 's' if ALLCNT > 1 else ''
   PgLOG.pglog("Delete {} Locfile record{} ...".format(ALLCNT, s), PgLOG.WARNLG)

   dcnt = delcnt = 0
   for i in range(ALLCNT):
      lidx = PgOPT.params['LI'][i]
      lcnd = "lindex = {}".format(lidx)
      if PgLock.lock_update(lidx, None, 2, PgOPT.PGOPT['errlog']) <= 0: continue
      cnt = PgDBI.pgget("drupdt", "", lcnd, PgOPT.PGOPT['extlog'])
      if cnt > 0:
         ss = 's' if cnt > 1 else ''
         PgLOG.pglog("Delete {} associated remote file record{} for Locfile index {} ...".format(cnt, ss, lidx), PgLOG.WARNLG)
         dcnt += PgDBI.pgdel("drupdt", lcnd, PgOPT.PGOPT['extlog'])
      delcnt += PgDBI.pgdel("dlupdt", lcnd, PgOPT.PGOPT['extlog'])

   PgLOG.pglog("{} of {} Locfile record{} deleted".format(delcnt, ALLCNT, s), PgOPT.PGOPT['wrnlog'])
   if dcnt > 0:
      s = "s" if (dcnt > 1) else ""
      PgLOG.pglog("{} associated Remote file record{} deleted too".format(dcnt, s), PgOPT.PGOPT['wrnlog'])

#
# delete update remote files for given dsid and remote files/locfile indices
#
def delete_remote_info():

   s = 's' if ALLCNT > 1 else ''
   PgLOG.pglog("Delete {} remote file record{} ...".format(ALLCNT, s), PgLOG.WARNLG)

   PgOPT.validate_multiple_options(ALLCNT, ["LI", "DO"])
   delcnt = 0
   for i in range(ALLCNT):
      lcnd = "lindex = {} AND remotefile = '{}'".format(PgOPT.params['LI'][i], PgOPT.params['RF'][i])
      if 'DO' in PgOPT.params: lcnd += " AND dindex = {}".format(PgOPT.params['DO'][i])
      delcnt += PgDBI.pgdel("drupdt", lcnd, PgOPT.PGOPT['extlog'])

   PgLOG.pglog("{} of {} remote file record{} deleted".format(delcnt, ALLCNT, s), PgOPT.PGOPT['wrnlog'])

#
# get update control information
#
def get_control_info():

   tname = "dcupdt"
   hash = PgOPT.TBLHASH[tname]
   PgLOG.pglog("Get update control info of {} from RDADB ...".format(PgOPT.params['DS']), PgLOG.WARNLG)

   lens = fnames = None
   if 'FN' in PgOPT.params: fnames = PgOPT.params['FN']
   fnames = PgDBI.fieldname_string(fnames, PgOPT.PGOPT[tname], PgOPT.PGOPT['dcall'])
   onames = PgOPT.params['ON'] if 'ON' in PgOPT.params else "C"
   condition = PgUpdt.file_condition(tname) + PgOPT.get_order_string(onames, tname)
   pgrecs = PgDBI.pgmget(tname, "*", condition, PgOPT.PGOPT['extlog'])
   if pgrecs and 'FO' in PgOPT.params: lens = PgUtil.all_column_widths(pgrecs, fnames, hash)
   PgOPT.OUTPUT.write("{}{}{}\n".format(PgOPT.OPTS['DS'][1], PgOPT.params['ES'], PgOPT.params['DS']))
   if PgOPT.PGOPT['CACT'] == "GA": PgOPT.OUTPUT.write("[{}]\n".format(tname.upper()))
   PgOPT.OUTPUT.write(PgOPT.get_string_titles(fnames, hash, lens) + "\n")
   if pgrecs:
      cnt = PgOPT.print_column_format(pgrecs, fnames, hash, lens)
      s = 's' if cnt > 1 else ''
      PgLOG.pglog("{} update control record{} retrieved".format(cnt, s), PgOPT.PGOPT['wrnlog'])
   else:
      PgLOG.pglog("no update control record retrieved", PgOPT.PGOPT['wrnlog'])

#
# get local file update information
#
def get_local_info():

   tname = "dlupdt"
   hash = PgOPT.TBLHASH[tname]
   PgLOG.pglog("Get local file update info of {} from RDADB ...".format(PgOPT.params['DS']), PgLOG.WARNLG)

   lens = fnames = None
   if 'FN' in PgOPT.params: fnames = PgOPT.params['FN']
   fnames = PgDBI.fieldname_string(fnames, PgOPT.PGOPT[tname], PgOPT.PGOPT['dlall'])
   onames = PgOPT.params['ON'] if 'ON' in PgOPT.params else "XL"
   condition = PgUpdt.file_condition(tname) + PgOPT.get_order_string(onames, tname)
   pgrecs = PgDBI.pgmget(tname, "*", condition, PgOPT.PGOPT['extlog'])
   if pgrecs and 'FO' in PgOPT.params: lens = PgUtil.all_column_widths(pgrecs, fnames, hash)
   if PgOPT.PGOPT['CACT'] == "GL":
      PgOPT.OUTPUT.write("{}{}{}\n".format(PgOPT.OPTS['DS'][1], PgOPT.params['ES'], PgOPT.params['DS']))
   else:
      PgOPT.OUTPUT.write("[{}]\n".format(tname.upper()))
   PgOPT.OUTPUT.write(PgOPT.get_string_titles(fnames, hash, lens) + "\n")
   if pgrecs:
      cnt = PgOPT.print_column_format(pgrecs, fnames, hash, lens)
      s = 's' if cnt > 1 else ''
      PgLOG.pglog("{} locfile record{} retrieved".format(cnt, s), PgOPT.PGOPT['wrnlog'])
   else:
      PgLOG.pglog("no locfile record retrieved", PgOPT.PGOPT['wrnlog'])

#
# get remote file update information
#
def get_remote_info():

   tname = "drupdt"
   hash = PgOPT.TBLHASH[tname]
   PgLOG.pglog("Get remote file update info of {} from RDADB ...".format(PgOPT.params['DS']), PgLOG.WARNLG)

   lens = fnames = None
   if 'FN' in PgOPT.params: fnames = PgOPT.params['FN']
   fnames = PgDBI.fieldname_string(fnames, PgOPT.PGOPT[tname], PgOPT.PGOPT['drall'])
   onames = PgOPT.params['ON'] if 'ON' in PgOPT.params else "LDF"
   condition = PgUpdt.file_condition(tname) + PgOPT.get_order_string(onames, tname)
   pgrecs = PgDBI.pgmget(tname, "*", condition, PgOPT.PGOPT['extlog'])
   if pgrecs and 'FO' in PgOPT.params: lens = PgUtil.all_column_widths(pgrecs, fnames, hash)
   if PgOPT.PGOPT['CACT'] == "GR":
      PgOPT.OUTPUT.write("{}{}{}\n".format(PgOPT.OPTS['DS'][1], PgOPT.params['ES'], PgOPT.params['DS']))
   else:
      PgOPT.OUTPUT.write("[{}]\n".format(tname.upper()))
   PgOPT.OUTPUT.write(PgOPT.get_string_titles(fnames, hash, lens) + "\n")
   if pgrecs:
      cnt = PgOPT.print_column_format(pgrecs, fnames, hash, lens)
      s = 's' if cnt > 1 else ''
      PgLOG.pglog("{} remote file record{} retrieved".format(cnt, s), PgOPT.PGOPT['wrnlog'])
   else:
      PgLOG.pglog("no remote file record retrieved", PgOPT.PGOPT['wrnlog'])

#
# add or modify update control information
#
def set_control_info():

   tname = 'dcupdt'
   s = 's' if ALLCNT > 1 else ''
   PgLOG.pglog("Set {} update control record{} ...".format(ALLCNT, s), PgLOG.WARNLG)

   addcnt = modcnt = 0
   flds = PgOPT.get_field_keys(tname, None, 'C')
   if not flds: return PgLOG.pglog("Nothing to set for update control!", PgOPT.PGOPT['errlog'])
   PgOPT.validate_multiple_values(tname, ALLCNT, flds)
   fields = PgOPT.get_string_fields(flds, tname)
   
   for i in range(ALLCNT):
      cidx = PgOPT.params['CI'][i]
      if cidx > 0:
         if PgLock.lock_update_control(cidx, 2, PgOPT.PGOPT['errlog']) <= 0: continue
         cnd = "cindex = {}".format(cidx)
         pgrec = PgDBI.pgget(tname, fields, cnd, PgOPT.PGOPT['errlog'])
         if not pgrec: PgOPT.action_error("Error get update control record for " + cnd)
      else:
         pgrec = None

      record = PgOPT.build_record(flds, pgrec, tname, i)
      if record:
         if 'pindex' in record and record['pindex'] and not PgDBI.pgget("dcupdt", "", "cindex = {}".format(record['pindex'])):
            PgOPT.action_error("Parent control Index {} is not in RDADB".format(record['pindex']))
         if 'action' in record and not re.match(r'^({})$'.format(PgOPT.PGOPT['UPDTACTS']), record['action']):
            PgOPT.action_error("Action Name '{}' must be one of dsupdt Actions ({})".format(record['action'], PgOPT.PGOPT['UPDTACTS']))
         if pgrec:
            record['pid'] = 0
            record['lockhost'] = ''
            modcnt += PgDBI.pgupdt(tname, record, cnd, PgOPT.PGOPT['errlog']|PgLOG.DODFLT)
         else:
            record['dsid'] = PgOPT.params['DS']
            if 'specialist' not in record: record['specialist'] = PgOPT.params['LN']
            addcnt += PgDBI.pgadd(tname, record, PgOPT.PGOPT['errlog']|PgLOG.DODFLT)
      elif cidx: # unlock
         PgLock.lock_update_control(cidx, 0, PgOPT.PGOPT['errlog'])

   PgLOG.pglog("{}/{} of {} control record{} added/modified".format(addcnt, modcnt, ALLCNT, s), PgOPT.PGOPT['wrnlog'])

#
# add or modify local file update information
#
def set_local_info():

   tname = 'dlupdt'
   s = 's' if ALLCNT > 1 else ''
   PgLOG.pglog("Set {} local file record{} ...".format(ALLCNT, s), PgLOG.WARNLG)

   addcnt = modcnt = 0
   flds = PgOPT.get_field_keys(tname, None, 'L')
   if 'RO' in PgOPT.params and 'XO' not in PgOPT.params: flds += 'X'   
   if not flds: return PgLOG.pglog("Nothing to set for update local file!", PgOPT.PGOPT['errlog'])
   PgOPT.validate_multiple_values(tname, ALLCNT, flds)
   fields = PgOPT.get_string_fields(flds, tname)

   for i in range(ALLCNT):
      lidx = PgOPT.params['LI'][i]
      if lidx > 0:
         if PgLock.lock_update(lidx, None, 2, PgOPT.PGOPT['errlog']) <= 0: continue
         cnd = "lindex = {}".format(lidx)
         pgrec = PgDBI.pgget(tname, fields, cnd, PgOPT.PGOPT['errlog'])
         if not pgrec: PgOPT.action_error("Error get Local file record for " + cnd)
      else:
         pgrec = None

      if 'RO' in PgOPT.params: PgOPT.params['XO'][i] = PgUpdt.get_next_exec_order(PgOPT.params['DS'], 0)
      record = PgOPT.build_record(flds, pgrec, tname, i)
      if record:
         if 'cindex' in record and record['cindex'] and not PgDBI.pgget("dcupdt", "", "cindex = {}".format(record['cindex'])):
            PgOPT.action_error("Update control Index {} is not in RDADB".format(record['cindex']))
         if 'action' in record and not re.match(r'^({})$'.format(PgOPT.PGOPT['ARCHACTS']), record['action']):
            PgOPT.action_error("Action Name '{}' must be one of dsarch Actions ({})".format(record['action'], PgOPT.PGOPT['ARCHACTS']))

         if pgrec:
            if 'VI' in record and not record['VI'] and pgrec['missdate']: record['missdate'] = record['misshour'] = None
            record['pid'] = 0
            record['hostname'] = 0
            modcnt += PgDBI.pgupdt(tname, record, cnd, PgOPT.PGOPT['errlog']|PgLOG.DODFLT)
         else:
            record['dsid'] = PgOPT.params['DS']
            if 'specialist' not in record: record['specialist'] = PgOPT.params['LN']
            if 'execorder' not in record: record['execorder'] = PgUpdt.get_next_exec_order(PgOPT.params['DS'], 1)
            addcnt += PgDBI.pgadd(tname, record, PgOPT.PGOPT['errlog']|PgLOG.DODFLT)
      elif lidx: # unlock
         PgLock.lock_update(lidx, None, 0, PgOPT.PGOPT['errlog'])

   PgLOG.pglog("{}/{} of {} Locfile record{} added/modified".format(addcnt, modcnt, ALLCNT, s), PgOPT.PGOPT['wrnlog'])

#
# add or modify remote file update information
#
def set_remote_info():

   tname = 'drupdt'
   s = 's' if ALLCNT > 1 else ''
   PgLOG.pglog("Set {} update remote file{} ...".format(ALLCNT, s), PgLOG.WARNLG)

   addcnt = modcnt = 0
   flds = PgOPT.get_field_keys(tname)
   if not flds: return PgLOG.pglog("Nothing to set for update remote file!", PgOPT.PGOPT['errlog'])
   PgOPT.validate_multiple_values(tname, ALLCNT, flds)
   fields = PgOPT.get_string_fields(flds, tname)
   
   for i in range(ALLCNT):
      lidx = PgOPT.params['LI'][i]
      didx = PgOPT.params['DO'][i] if 'DO' in PgOPT.params else 0
      cnd = "lindex = {} AND remotefile = '{}' AND dindex = {}".format(lidx, PgOPT.params['RF'][i], didx)
      pgrec = PgDBI.pgget("drupdt", fields, cnd, PgOPT.PGOPT['errlog'])
      record = PgOPT.build_record(flds, pgrec, tname, i)
      if record:
         if 'lindex' in record and record['lindex'] and not PgDBI.pgget("dlupdt", "", "lindex = {}".format(record['lindex'])):
            PgOPT.action_error("Local file Index {} is not in RDADB".format(record['lindex']))

         if pgrec:
            modcnt += PgDBI.pgupdt("drupdt", record, cnd, PgOPT.PGOPT['errlog']|PgLOG.DODFLT)
         else:
            record['lindex'] = lidx
            record['dsid'] = PgOPT.params['DS']
            addcnt += PgDBI.pgadd("drupdt", record, PgOPT.PGOPT['errlog']|PgLOG.DODFLT)

   PgLOG.pglog("{}/{} of {} remote file record{} added/modified".format(addcnt, modcnt, ALLCNT, s), PgOPT.PGOPT['wrnlog'])

#
# unlock update records for given locfile indices
#
def unlock_update_info():

   s = 's' if ALLCNT > 1 else ''
   PgLOG.pglog("Unlock {} update locfile{} ...".format(ALLCNT, s), PgLOG.WARNLG)

   modcnt = 0
   for lidx in PgOPT.params['LI']:
      cnd = "lindex = {}".format(lidx)
      pgrec = PgDBI.pgget("dlupdt", "pid, hostname", cnd, PgOPT.PGOPT['extlog'])
      if not pgrec:
         PgLOG.pglog("{}: Local File Not exists".format(lidx), PgOPT.PGOPT['errlog'])
      elif not pgrec['pid']:
         PgLOG.pglog("{}: Local File Not locked".format(lidx), PgOPT.PGOPT['wrnlog'])
      elif PgLock.lock_update(lidx, None, -1, PgOPT.PGOPT['errlog']) > 0:
         modcnt += 1
         PgLOG.pglog("{}: Local File Unlocked {}/{}".format(lidx, pgrec['pid'], pgrec['hostname']), PgOPT.PGOPT['wrnlog'])
      elif (PgFile.check_host_down(None, pgrec['hostname']) and
            PgLock.lock_update(lidx, None, -2, PgOPT.PGOPT['errlog']) > 0):
         modcnt += 1
         PgLOG.pglog("{}: Local File Force unlocked {}/{}".format(lidx, pgrec['pid'], pgrec['hostname']), PgOPT.PGOPT['wrnlog'])
      else:
         PgLOG.pglog("{}: Local File Unable to unlock {}/{}".format(lidx, pgrec['pid'], pgrec['hostname']), PgOPT.PGOPT['wrnlog'])

   PgLOG.pglog("{} of {} local file record{} unlocked from RDADB".format(modcnt, ALLCNT, s), PgLOG.LOGWRN)

#
# unlock update control records for given locfile indices
#
def unlock_control_info():

   s = 's' if ALLCNT > 1 else ''
   PgLOG.pglog("Unlock {} update control{} ...".format(ALLCNT, s), PgLOG.WARNLG)

   modcnt = 0
   for cidx in PgOPT.params['CI']:
      pgrec = PgDBI.pgget("dcupdt", "pid, lockhost", "cindex = {}".format(cidx), PgOPT.PGOPT['extlog'])
      if not pgrec:
         PgLOG.pglog("{}: Update Control Not exists".format(cidx), PgOPT.PGOPT['errlog'])
      elif not pgrec['pid']:
         PgLOG.pglog("{}: Update Control Not locked".format(cidx), PgOPT.PGOPT['wrnlog'])
      elif PgLock.lock_update_control(cidx, -1, PgOPT.PGOPT['extlog']) > 0:
         modcnt += 1
         PgLOG.pglog("{}: Update Control Unlocked {}/{}".format(cidx, pgrec['pid'], pgrec['lockhost']), PgOPT.PGOPT['wrnlog'])
      elif (PgFile.check_host_down(None, pgrec['lockhost']) and
            PgLock.lock_update_control(cidx, -2, PgOPT.PGOPT['extlog']) > 0):
         modcnt += 1
         PgLOG.pglog("{}: Update Control Force unlocked {}/{}".format(cidx, pgrec['pid'], pgrec['lockhost']), PgOPT.PGOPT['wrnlog'])
      else:
         PgLOG.pglog("{}: Undate Control Unable to unlock {}/{}".format(cidx, pgrec['pid'], pgrec['lockhost']), PgOPT.PGOPT['wrnlog'])

   PgLOG.pglog("{} of {} update control record{} unlocked from RDADB".format(modcnt, ALLCNT, s), PgLOG.LOGWRN)

#
# get update info of local and remote files owned by login name
#
def get_update_info():
   
   if 'DS' in PgOPT.params:
      dsids = {'dsid' : [PgOPT.params['DS']]}
      dscnt = 1
   else:
      tname = "dlupdt"
      cnd = PgUpdt.file_condition(tname, None, None, 1)
      if not cnd:
         PgOPT.set_default_value("SN", PgOPT.params['LN'])
         cnd = PgUpdt.file_condition(tname, None, None, 1)
      dsids = PgDBI.pgmget(tname, "DISTINCT dsid",  cnd, PgOPT.PGOPT['extlog'])
      dscnt = len(dsids['dsid']) if dsids else 0
      if dscnt == 0:
         return PgLOG.pglog("NO dataset identified for giving condition", PgOPT.PGOPT['wrnlog'])
      elif dscnt > 1:
         PgLOG.pglog("Get Update Info for {} datasets".format(dscnt), PgOPT.PGOPT['wrnlog'])

      PgOPT.PGOPT['AUTODS'] = dscnt

   for i in range(dscnt):
      PgOPT.params['DS'] = dsids['dsid'][i]
      if PgOPT.PGOPT['ACTS'] == PgOPT.OPTS['GC'][0]:
         get_control_info()
      elif PgOPT.PGOPT['ACTS'] == PgOPT.OPTS['GL'][0]:
         get_local_info()
      elif PgOPT.PGOPT['ACTS'] == PgOPT.OPTS['GR'][0]:
         get_remote_info()
      else:
         if 'ON' in PgOPT.params: del PgOPT.params['ON']   # use default order string
         if 'FN' not in PgOPT.params: PgOPT.params['FN'] = 'ALL'
         if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['GC'][0]: get_control_info()
         if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['GL'][0]: get_local_info()
         if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['GR'][0]: get_remote_info()

   if dscnt > 1: PgLOG.pglog("Update Info of {} datasets retrieved".format(dscnt), PgOPT.PGOPT['wrnlog'])

#
# gather due datasets for data update
#
def dataset_update():

   global SUBJECT, TOPMSG, ACTSTR

   actcnd = "specialist = '{}'".format(PgOPT.params['LN'])
   if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['AF'][0]: actcnd += " AND action IN ('AW', 'AS', 'AQ')"
   (PgOPT.PGOPT['CURDATE'], PgOPT.PGOPT['CURHOUR']) = PgUtil.curdatehour()
   if 'CD' not in PgOPT.params: PgOPT.params['CD'] = PgOPT.PGOPT['CURDATE']   # default to current date
   if 'CH' not in PgOPT.params: PgOPT.params['CH'] = PgOPT.PGOPT['CURHOUR']   # default to current hour
   if ALLCNT > 1 and PgOPT.params['MU']: del PgOPT.params['MU']
   if 'CN' in PgOPT.params and 'RD' in PgOPT.params: del PgOPT.params['CN']
   if 'CN' in PgOPT.params or 'RD' in PgOPT.params or 'RA' in PgOPT.params:
      if 'MO' in PgOPT.params: del PgOPT.params['MO']
   elif 'MO' not in PgOPT.params and PgOPT.PGOPT['CACT'] == "UF":
      PgOPT.params['MO'] = -1

   if 'DS' in PgOPT.params:
      dsids = [PgOPT.params['DS']]
      dscnt = 1
   else:
      if 'CI' not in PgOPT.params: actcnd += " AND cindex = 0"
      loccnd = PgUpdt.file_condition('dlupdt', "LQFIXA", None, 1)
      dscnd = actcnd
      if loccnd: dscnd += " AND " + loccnd
      pgrecs = PgDBI.pgmget("dlupdt", "DISTINCT dsid", dscnd, PgOPT.PGOPT['extlog'])
      dsids = pgrecs['dsid'] if pgrecs else []
      dscnt = len(dsids)
      if not dscnt: return PgLOG.pglog("NO dataset is due for update on {} for {}".format(PgOPT.params['CD'], PgOPT.params['LN']), PgOPT.PGOPT['wrnlog'])
      PgOPT.PGOPT['AUTODS'] = dscnt
   actcnd += " ORDER BY execorder, lindex"

   if PgLOG.PGLOG['DSCHECK']:
      fcnt = 0
      for i in range(dscnt):
         PgOPT.params['DS'] = dsids[i]
         loccnd = PgUpdt.file_condition('dlupdt', "LQFIXA")
         locrecs = PgDBI.pgmget("dlupdt", "*", "{} AND {}".format(loccnd, actcnd), PgOPT.PGOPT['extlog'])
         loccnt = len(locrecs['locfile']) if locrecs else 0
         if loccnt == 0: continue
         for j in range(loccnt):
            locrec = PgUtil.onerecord(locrecs, j)
            if (loccnt == 1 and 'LI' in PgOPT.params and 'LF' in PgOPT.params and
                len(PgOPT.params['LF']) == 1 and PgOPT.params['LF'][0] != locrec['locfile']):
               locrec['locfile'] = PgOPT.params['LF'][0]
            fcnt += file_update(locrec, PgLOG.LOGWRN, 1)
      PgCMD.set_dscheck_fcount(fcnt, PgLOG.LOGERR)

   # check and update data for each dataset
   logact = PgOPT.PGOPT['emllog']
   acnt = ucnt = 0
   for i in range(dscnt):
      PgOPT.params['DS'] = dsids[i]
      loccnd = PgUpdt.file_condition('dlupdt', "LQFIXA")
      locrecs = PgDBI.pgmget("dlupdt", "*", "{} AND {}".format(loccnd, actcnd), PgOPT.PGOPT['extlog'])
      loccnt = len(locrecs['locfile']) if locrecs else 0
      if loccnt == 0:
         s = "-UC{}".format(PgOPT.params['CI'][0]) if ('CI' in PgOPT.params and len(PgOPT.params['CI']) == 1) else ""
         PgLOG.pglog("{}{}: no config record of local file found to update for '{}'".format(PgOPT.params['DS'], s, PgOPT.params['LN']), PgOPT.PGOPT['wrnlog'])
         continue
      s = 's' if loccnt > 1 else ''
      PgLOG.pglog("{}: {} for {} update record{}".format(PgOPT.params['DS'], PgOPT.PGOPT['CACT'], loccnt, s), logact)
      logact = PgOPT.PGOPT['emlsep']
      for j in range(loccnt):
         locrec = PgUtil.onerecord(locrecs, j)
         if (loccnt == 1 and 'LI' in PgOPT.params and 'LF' in PgOPT.params and
             len(PgOPT.params['LF']) == 1 and PgOPT.params['LF'][0] != locrec['locfile']):
            locrec['locfile'] = PgOPT.params['LF'][0]
         if locrec['cindex']:
            if 'CI' not in PgOPT.params:
               PgOPT.params['CI'] = [locrec['cindex']]
               PgUpdt.cache_update_control(locrec['cindex'], 0)
               if 'CN' in PgOPT.params and 'RD' in PgOPT.params: del PgOPT.params['CN']
               if 'CN' in PgOPT.params or 'RD' in PgOPT.params or 'RA' in PgOPT.params:
                  if 'MO' in PgOPT.params: del PgOPT.params['MO']
               elif 'MO' not in PgOPT.params and PgOPT.PGOPT['CACT'] == "UF":
                  PgOPT.params['MO'] = -1
            elif locrec['cindex'] != PgOPT.params['CI'][0]:
               PgLOG.pglog("{}-{}: Skipped due to control index {} mismatches {}".format(PgOPT.params['DS'], locrec['lindex'], locrec['cindex'], PgOPT.params['CI'][0]), PgOPT.PGOPT['emlerr'])
               continue

         PgOPT.PGOPT['rstat'] = 1   # reset remote download status for each local file
         if PgSIG.PGSIG['MPROC'] > 1: acnt += 1
         fcnt = file_update(locrec, logact)
         if PgSIG.PGSIG['PPID'] > 1:
            if PgOPT.PGOPT['AUTODS'] > 1: PgOPT.PGOPT['AUTODS'] = dscnt = 1
            acnt = ucnt = 0   # reinitialize counts for child process
            break   # stop loop in child
         if PgSIG.PGSIG['MPROC'] > 1:
            if fcnt == 0:
               break   # quit
            else:
               if fcnt > 0: ucnt += 1   # record update count, s is either -1 or 1
               continue   # non-daemon parent
         if 'QE' in PgOPT.params and fcnt <= 0: break

      if PgOPT.PGOPT['vcnt'] > 0:
         renew_internal_version(PgOPT.params['DS'], PgOPT.PGOPT['vcnt'])
         PgOPT.PGOPT['vcnt'] = 0
      if PgSIG.PGSIG['MPROC'] > 1:
         if not PgSIG.PGSIG['QUIT'] and j == loccnt: continue
         break
      if PgOPT.PGOPT['rcnt']:
         if PgOPT.PGOPT['CACT'] == "DR":
            acnt += PgOPT.PGOPT['rcnt']
            ucnt += PgOPT.PGOPT['dcnt']
         s = 's' if PgOPT.PGOPT['rcnt'] > 1 else ''
         if loccnt > 1:
            PgLOG.pglog("{}: {} of {} rfile{} gotten!".format(PgOPT.params['DS'], PgOPT.PGOPT['dcnt'], PgOPT.PGOPT['rcnt'], s), PgOPT.PGOPT['emllog'])
         PgOPT.PGOPT['rcnt'] = PgOPT.PGOPT['dcnt'] = 0
      if PgOPT.PGOPT['lcnt']:
         if PgOPT.PGOPT['CACT'] == "BL" or PgOPT.PGOPT['CACT'] == "PB":
            acnt += PgOPT.PGOPT['lcnt']
            ucnt += PgOPT.PGOPT['bcnt']
         s = 's' if PgOPT.PGOPT['lcnt'] > 1 else ''
         if loccnt > 1 and PgOPT.PGOPT['bcnt'] > 0:
            PgLOG.pglog("{}: {} of {} lfile{} built!".format(PgOPT.params['DS'], PgOPT.PGOPT['bcnt'], PgOPT.PGOPT['lcnt'], s), PgOPT.PGOPT['emllog'])
         PgOPT.PGOPT['lcnt'] = PgOPT.PGOPT['bcnt'] = 0
      if PgOPT.PGOPT['acnt']:
         acnt += PgOPT.PGOPT['acnt']
         ucnt += PgOPT.PGOPT['ucnt']
         s = 's' if PgOPT.PGOPT['acnt'] > 1 else ''
         PgLOG.pglog("{}: {} of {} local file{} archived!".format(PgOPT.params['DS'], PgOPT.PGOPT['ucnt'], PgOPT.PGOPT['acnt'], s),
                     (PgOPT.PGOPT['emlsum'] if dscnt > 1 else PgOPT.PGOPT['emllog']))
         PgOPT.PGOPT['acnt'] = PgOPT.PGOPT['ucnt'] = 0

      if PgSIG.PGSIG['PPID'] > 1: break   # stop loop child

   if acnt > 0:
      TOPMSG = detail = ""
      if PgSIG.PGSIG['MPROC'] > 1:
         s = 's' if acnt > 1 else ''
         ACTSTR = "{} of {} CPIDs{} for 'dsupdt {}' started".format(ucnt, acnt, s, PgOPT.PGOPT['CACT'])
      else:
         s = 's' if ucnt > 1 else ''
         TOPMSG = ""
         if PgOPT.PGOPT['CACT'] == "DR":
            atype = "remote file{} gotten".format(s)
         elif PgOPT.PGOPT['CACT'] == "BL" or PgOPT.PGOPT['CACT'] == "PB":
            atype = "local file{} built".format(s)
         else:
            atype = "local file{} archived".format(s)
            if PgOPT.PGOPT['rdcnt'] > 0:
               s = 's' if PgOPT.PGOPT['rdcnt'] > 1 else ''
               TOPMSG = "{} remote server file{} downloaded and ".format(PgOPT.PGOPT['rdcnt'], s)
            if PgOPT.PGOPT['udcnt'] > 0:
               if detail: detail += " & "
               detail += "{} Web Online".format(PgOPT.PGOPT['udcnt'])
            if PgOPT.PGOPT['uncnt'] > 0:
               if detail: detail += " & "
               detail += "{} Glade Only".format(PgOPT.PGOPT['uncnt'])
            if PgOPT.PGOPT['uwcnt'] > 0:
               if detail: detail += " & "
               detail += "{} Web".format(PgOPT.PGOPT['uwcnt'])
            if PgOPT.PGOPT['uscnt'] > 0:
               if detail: detail += " & "
               detail += "{} Saved".format(PgOPT.PGOPT['uscnt'])
            if PgOPT.PGOPT['qbcnt'] > 0:
               if detail: detail += " & "
               detail += "{} Quasar Backup".format(PgOPT.PGOPT['qbcnt'])
            if PgOPT.PGOPT['qdcnt'] > 0:
               if detail: detail += " & "
               detail += "{} Quasar Drdata".format(PgOPT.PGOPT['qdcnt'])
         ACTSTR = "{} {}".format(ucnt, atype)

      TOPMSG += ACTSTR
      if detail: TOPMSG += " ({})".format(detail)
      if dscnt > 1:
         PgLOG.pglog("{} datasets: {}".format(dscnt, TOPMSG), PgOPT.PGOPT['emlsum'])
      SUBJECT = "DSUPDT of "
      if PgOPT.PGOPT['AUTODS'] < 2:
         SUBJECT += PgOPT.params['DS'].upper()
      else:
         SUBJECT += "{} Datasets".format(PgOPT.PGOPT['AUTODS'])

   if PgOPT.PGOPT['UCNTL']:
      PgUpdt.reset_control_time()
      if SUBJECT: SUBJECT += "-C{}".format(PgOPT.PGOPT['UCNTL']['cindex'])

# renew internal version number for given dataset
def renew_internal_version(dsid, vcnt):

   s = 's' if vcnt > 1 else ''
   cmd = "dsarch {} SV -NV -DE '{} Data file{} rearchived'".format(dsid, vcnt, s)
   if PgLOG.pgsystem(cmd, PgOPT.PGOPT['emerol'], 5):  # 1 + 4
      pgrec = PgDBI.pgget('dsvrsn', '*', "dsid = '{}' and status = 'A'".format(dsid), PgOPT.PGOPT['emerol'])
      if pgrec:
         vmsg = "set to {} for DOI {}".format(pgrec['iversion'], pgrec['doi'])
      else:
         vmsg = 'renewed'

      PgLOG.pglog("{}: {} Data file{} rearchived, Internal version number {}".format(dsid, vcnt, s, vmsg), PgOPT.PGOPT['emlsum'])

#
# cach the total count of files to be archived
#
def count_caching(locrec, locinfo):

   files = PgUpdt.expand_serial_pattern(locrec['locfile'])
   scnt = len(files) if files else 1

   if ALLCNT > 1:
      ecnt = ALLCNT
   else:
      tinfo = TEMPINFO[locrec['lindex']] = get_tempinfo(locrec, locinfo, 0)
      ecnt = len(tinfo['ED']) if tinfo else 1

   return ecnt * scnt

#
# gather/archive due data file for update of each local file
#
def file_update(locrec, logact, caching = 0):

   lfile = locrec['locfile']
   endonly = retcnt = 0
   lindex = locrec['lindex']
   loccnd = "lindex = {}".format(lindex)
   locinfo = "{}-L{}".format(locrec['dsid'], lindex)
   if not lfile:
      if caching:
         return None
      else:
         return PgLOG.pglog(locinfo + ": local file name NOT specified", PgOPT.PGOPT['emlerr'])
   locinfo += "-" + lfile
   if locrec['specialist'] != PgOPT.params['LN']:
      if caching:
         return None
      else:
         return PgLOG.pglog("{}: owner '{}', NOT '{}'".format(locinfo, locrec['specialist'], PgOPT.params['LN']), PgOPT.PGOPT['emlerr'])

   if caching: return count_caching(locrec, locinfo)
   tempinfo = TEMPINFO[lindex] if lindex in TEMPINFO else get_tempinfo(locrec, locinfo, 0)
   if not tempinfo: return 0  # simply return if miss temporal info for update

   rmtcnd = loccnd
   rcnd = PgUpdt.file_condition('drupdt', ('D' if 'DO' in PgOPT.params else "RS"), None, 1)
   if rcnd: rmtcnd += " AND " + rcnd
   rmtrecs = PgDBI.pgmget("drupdt", "*", rmtcnd + " ORDER BY dindex, remotefile", PgOPT.PGOPT['extlog'])
   rcnt = len(rmtrecs['remotefile']) if rmtrecs else 0
   if rcnt == 0:
      if rcnd and PgDBI.pgget("drupdt", "", loccnd):
         return PgLOG.pglog("{}: NO remote file record matched for {}".format(locinfo, rcnd), PgOPT.PGOPT['emlerr'])
      # create a empty record remote file
      rcnt = 1
      
      rmtrecs = {'lindex' : [lindex], 'dindex' : [0]}
      rflds = ['remotefile', 'serverfile', 'download', 'begintime', 'endtime', 'tinterval']
      for rfld in rflds: rmtrecs[rfld] = [None]
   if rcnt == 1:
      if 'RF' in PgOPT.params and len(PgOPT.params['RF']) == 1 and not (rmtrecs['remotefile'][0] and PgOPT.params['RF'][0] == rmtrecs['remotefile'][0]):
          rmtrecs['remotefile'][0] = PgOPT.params['RF'][0]
      if 'SF' in PgOPT.params and len(PgOPT.params['SF']) == 1 and not (rmtrecs['serverfile'][0] and PgOPT.params['SF'][0] == rmtrecs['serverfile'][0]):
          rmtrecs['serverfile'][0] = PgOPT.params['SF'][0]
   ecnt = ALLCNT if ALLCNT > 1 else len(tempinfo['ED'])   # should be at least one

   if PgSIG.PGSIG['MPROC'] > 1:
      pname = "updt{}".format(lindex)
      pid = PgSIG.start_child(pname, PgOPT.PGOPT['wrnlog'], 1)   # try to start a child process
      if pid <= 0: return pid   # failed to start a child process
      if PgSIG.PGSIG['PPID'] > 1:
         PgLOG.set_email()   # empty email in child process
         PgOPT.PGOPT['acnt'] = PgOPT.PGOPT['ucnt'] = 0
      else:
         edate = tempinfo['ED'][0]
         ehour = tempinfo['EH'][0]
         lfile = PgUpdt.replace_pattern(locrec['locfile'], edate, ehour, tempinfo['FQ'])
         locinfo = "{}-L{}-{}".format(locrec['dsid'], lindex, lfile)
         if ecnt > 1: locinfo += ", {} Update Periods".format(ecnt)
         PgLOG.pglog("CPID {} for 'dsupdt {}' of {}".format(PgSIG.pname2cpid(pname), PgOPT.PGOPT['CACT'], locinfo), PgOPT.PGOPT['emllog'])
         return 1   # no further action in non-daemon program

   if PgLock.lock_update(lindex, locinfo, 1, PgOPT.PGOPT['emllog']) <= 0: return 0
   PgOPT.PGOPT['lindex'] = lindex
   tempinfo['prcmd'] = PgOPT.params['PR'][0] if 'PR' in PgOPT.params else locrec['processremote']
   tempinfo['blcmd'] = PgOPT.params['BC'][0] if 'BC' in PgOPT.params else locrec['buildcmd']
   postcnt = -1
   if PgOPT.PGOPT['UCNTL'] and PgOPT.PGOPT['CACT'] == PgOPT.PGOPT['UCNTL']['action']:
      tempinfo['postcmd'] = PgOPT.params['XC'][0] if 'XC' in PgOPT.params else PgOPT.PGOPT['UCNTL']['execcmd']
      if tempinfo['postcmd']: postcnt = 0

   setmiss = 1 if tempinfo['VD'] else 0
   ufile = uinfo = None
   rscnt = ucnt = lcnt = 0

   for i in range(ecnt):
      if ALLCNT > 1 and i > 0:
         tempinfo = get_tempinfo(locrec, locinfo, i)
         if not tempinfo: break
         edate = tempinfo['ED'][0]
         ehour = tempinfo['EH'][0]
      else:
         edate = tempinfo['ED'][i]
         ehour = tempinfo['EH'][i]
         if 'RE' in PgOPT.params and i and PgUtil.diffdatehour(edate, ehour, tempinfo['edate'], tempinfo['ehour']) <= 0:
            continue
      if ucnt and tempinfo['RS'] == 1 and i%20 == 0: refresh_metadata(locrec['dsid'])
      tempinfo['edate'] = edate
      if ehour != None:
         tempinfo['einfo'] = "end data date:hour {}:{:02}".format(edate, ehour)
         tempinfo['ehour'] = ehour
      else:
         tempinfo['einfo'] = "end data date {}".format(edate)
         tempinfo['ehour'] = None
      if 'GZ' in PgOPT.params: tempinfo['einfo'] += "(UTC)"

      locfiles = PgUpdt.get_local_names(locrec['locfile'], tempinfo)
      lcnt = len(locfiles) if locfiles else 0
      if not lcnt: break
      rmtcnt = acnt = ccnt = ut = 0
      rfiles = rfile = None
      if tempinfo['RS'] == 0 and lcnt > 2: tempinfo['RS'] = 1

      for l in range(lcnt):
         if PgLOG.PGLOG['DSCHECK'] and ((l+1)%20) == 0:
            PgCMD.add_dscheck_dcount(20, 0, PgOPT.PGOPT['extlog'])
         lfile = locfiles[l]
         locinfo = "{}-L{}-{}".format(locrec['dsid'], lindex, lfile)
         tempinfo['gotnew'] = tempinfo['archived'] = 0
         tempinfo['ainfo'] = None
         tempinfo['ainfo'] = file_archive_info(lfile, locrec, tempinfo)
         if not tempinfo['ainfo']: continue
         if tempinfo['ainfo']['archived'] == tempinfo['ainfo']['archcnt']:
            ufile = "{} at {} {}".format(lfile, tempinfo['ainfo']['adate'], tempinfo['ainfo']['atime'])
            tempinfo['archived'] = 1
            if 'MO' in PgOPT.params:
               if PgOPT.params['MO'] < 0:
                  PgLOG.pglog("{}: {} already for {}".format(locinfo, PgOPT.PGOPT['CACT'], tempinfo['einfo']), PgOPT.PGOPT['emlsum'])
                  if i == 0: PgLOG.pglog("Add Mode option -RA if you want to re-archive", PgOPT.PGOPT['wrnlog'])
                  if 'UT' in PgOPT.params or 'ED' not in PgOPT.params: ut = 1
               retcnt += 1
               continue
         else:
            if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['AF'][0]: uinfo = locinfo
         PgLOG.pglog("{}: {} for {}".format(locinfo, PgOPT.PGOPT['CACT'], tempinfo['einfo']), logact)
         if not change_workdir(locrec['workdir'], locinfo, tempinfo['edate'], tempinfo['ehour'], tempinfo['FQ']):
            break
         if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['AF'][0]: PgOPT.PGOPT['acnt'] += 1
         if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['BL'][0]: PgOPT.PGOPT['lcnt'] += 1
         opt = 1 if tempinfo['AQ'] else 65  # 1+64(remove small file)
         linfo = PgFile.check_local_file(lfile, opt, PgOPT.PGOPT['emerol'])
         cnt = -1
         if rmtcnt > 0:
            cnt = rmtcnt
            rfile = rfiles[l]
         else:
            dr = 1 if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['PB'][0] else 0
            if linfo and PgOPT.PGOPT['CACT'] == "BL" and not tempinfo['prcmd']: dr = 0 # skip download for BL only
            if dr:
               dfiles = None
               for j in range(rcnt):   # processs each remote record
                  pgrec = PgUtil.onerecord(rmtrecs, j)
                  if dfiles and pgrec['remotefile'] == rfile and not PgOPT.PGOPT['mcnt']:
                     continue  # skip
                  rfile = pgrec['remotefile']
                  act = 0 if locrec['action'] == 'AQ' else PgOPT.PGOPT['ACTS']&PgOPT.OPTS['DR'][0]
                  dfiles = download_remote_files(pgrec, lfile, linfo, locrec, locinfo, tempinfo, act)
                  if PgOPT.PGOPT['rstat'] < 0:
                     i = ecnt
                     break
                  if dfiles: rfiles = PgUtil.joinarray(rfiles, dfiles)

               rmtcnt = len(rfiles) if rfiles else 0
               if rmtcnt > 0:
                  if lcnt > 1 and rmtcnt != lcnt:
                     PgLOG.pglog("{}: {} files found for {} local files".format(locrec['locinfo'], rmtcnt, lcnt), PgOPT.PGOPT['emlerr'])
                     i = ecnt
                     break
                  cnt = rmtcnt
                  rfile = rfiles[l] if lcnt > 1 else rfiles[rmtcnt-1]   # record the break remote file name
               else:
                  rfile = None
                  if linfo and PgOPT.PGOPT['rstat'] == 0: PgOPT.PGOPT['rstat'] = 1

         if cnt != 0 and PgOPT.PGOPT['rstat'] > 0:
            if PgOPT.PGOPT['ACTS']&(PgOPT.OPTS['BL'][0]|PgOPT.OPTS['AF'][0]):
               if cnt < 0 and linfo:
                  if tempinfo['archived'] and PgOPT.PGOPT['CACT'] == "UF" and not tempinfo['gotnew']:
                     if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['AF'][0] and 'RA' not in PgOPT.params:
                        PgLOG.pglog(lfile + ": local file archived already", PgOPT.PGOPT['emllog'])
                        cnt = 0
                  else:
                     if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['BL'][0]:
                        PgLOG.pglog(lfile + ": local file exists already", PgOPT.PGOPT['emllog'])
                     cnt = 1
               elif rmtcnt == lcnt and lfile == rfile:
                   if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['BL'][0]:
                      PgLOG.pglog(lfile + ": local file same as remote file", PgOPT.PGOPT['emllog'])
               elif not (PgOPT.PGOPT['ACTS']&PgOPT.OPTS['BL'][0]):
                  PgLOG.pglog(lfile + ": local file not built yet", PgOPT.PGOPT['emlerr'])
                  cnt = 0
               else:
                  cnt = build_local_file(rfiles, lfile, linfo, locrec, tempinfo, lcnt, l)
                  if cnt and 'lfile' in tempinfo:
                     lfile = tempinfo['lfile']
                     del tempinfo['lfile']

            if cnt != 0 and (PgOPT.PGOPT['ACTS']&PgOPT.OPTS['AF'][0]):
               file_status_info(lfile, rfile, tempinfo)
               cnt = archive_data_file(lfile, locrec, tempinfo, i)
               if cnt > 0:
                  ucnt += 1
                  if tempinfo['RS'] == 1: rscnt += 1
                  if postcnt > -1: postcnt += 1
         elif cnt > 0:
            cnt = 0

         if cnt > 0 and PgOPT.PGOPT['rstat'] > 0:
            ccnt += 1
         elif 'UT' in PgOPT.params or tempinfo['archived']:
            ut = 1
            if cnt > 0: acnt += 1

      if PgLOG.PGLOG['DSCHECK']:
         PgCMD.add_dscheck_dcount(lcnt%20, 0, PgOPT.PGOPT['extlog'])
      if ccnt == lcnt and (PgOPT.PGOPT['ACTS']&PgOPT.OPTS['CF'][0]) and locrec['cleancmd']:
         if tempinfo['CVD'] and PgUtil.diffdate(edate, tempinfo['CVD']) > 0:
            clean_older_files(locrec['cleancmd'], locrec['workdir'], locinfo, tempinfo['CVD'], locrec['locfile'], rmtrecs, rcnt, tempinfo)
         else:
            if not rfiles and rcnt and locrec['cleancmd'].find(' -RF') > -1:
               rfiles = get_all_remote_files(rmtrecs, rcnt, tempinfo, edate)
            clean_files(locrec['cleancmd'], edate, ehour, locfiles, rfiles, tempinfo['FQ'])
      if PgOPT.PGOPT['ACTS']&PgOPT.OPTS['AF'][0] or PgOPT.PGOPT['UCNTL'] and PgOPT.PGOPT['CACT'] == PgOPT.PGOPT['UCNTL']['action']:
         rmonly = 1 if PgOPT.PGOPT['rstat'] > 0 else 0
         if ccnt == lcnt:
            PgUpdt.reset_update_time(locinfo, locrec, tempinfo, ccnt, endonly)
         elif ut:
            PgUpdt.reset_update_time(locinfo, locrec, tempinfo, acnt, endonly)
         else:
            if PgOPT.PGOPT['rstat'] == 0:
               if tempinfo['VD'] and PgUtil.diffdatehour(edate, ehour, tempinfo['VD'], tempinfo['VH']) < 0:
                  PgUpdt.reset_update_time(locinfo, locrec, tempinfo, 0, endonly)   # skip update
                  PgOPT.PGOPT['rstat'] = 1   # reset remote download status
               elif 'IE' in PgOPT.params:
                  if tempinfo['VD'] and PgUtil.diffdatehour(edate, ehour, tempinfo['VD'], tempinfo['VH']) >= 0:
                     endonly = 1
                  PgUpdt.reset_update_time(locinfo, locrec, tempinfo, 0, endonly)   # skip update
                  PgOPT.PGOPT['rstat'] = 1   # reset remote download status
         if setmiss: setmiss = PgUpdt.set_miss_time(lfile, locrec, tempinfo, rmonly)

      if postcnt > 0:
         postcmd = PgUpdt.executable_command(PgUpdt.replace_pattern(tempinfo['postcmd'], edate, ehour, tempinfo['FQ']),
                                             lfile, PgOPT.params['DS'], edate, ehour)
         PgLOG.pgsystem(postcmd, PgOPT.PGOPT['emllog'], 5)
         postcnt = 0
      if rscnt >= PgOPT.PGOPT['RSMAX']:
         refresh_metadata(locrec['dsid'])
         rscnt = 0
      if PgOPT.PGOPT['rstat'] < -1 or PgOPT.PGOPT['rstat'] < 0 and 'QE' in PgOPT.params: break  # unrecoverable errors

   if rscnt > 0: refresh_metadata(locrec['dsid'])
   if ufile and uinfo and ucnt == 0:
      PgLOG.pglog("{}: Last successful update - {}".format(uinfo, ufile), PgOPT.PGOPT['emlsum'])
   PgLock.lock_update(lindex, locinfo, 0, PgOPT.PGOPT['errlog'])
   PgOPT.PGOPT['lindex'] = 0

   return retcnt

#
# refresh the gathered metadata with speed up option -R and -S
#
def refresh_metadata(dsid):

   sx = "{} -d {} -r".format(PgOPT.PGOPT['scm'], dsid)
   if PgOPT.PGOPT['wtidx']:
      if 0 in PgOPT.PGOPT['wtidx']:
         PgLOG.pgsystem(sx + 'w all', PgOPT.PGOPT['emllog'], 5)
      else:
         for tidx in PgOPT.PGOPT['wtidx']:
            PgLOG.pgsystem("{}w {}".format(sx, tidx), PgOPT.PGOPT['emllog'], 5)
      PgOPT.PGOPT['wtidx'] = {}

#
# retrieve remote files
# act: > 0 - create filenames and get data files physically; 0 - create filenames only
#
def download_remote_files(rmtrec, lfile, linfo, locrec, locinfo, tempinfo, act = 0):

   emlsum = PgOPT.PGOPT['emlsum'] if PgOPT.PGOPT['CACT'] == "DR" else PgOPT.PGOPT['emllog']
   rfile = rmtrec['remotefile']
   rmtinfo = locinfo
   dfiles = []
   if not rfile:
      rfile = lfile
      rcnt = 1
   if rfile != locrec['locfile']: rmtinfo += "-" + rfile
   if act:
      tempinfo['DC'] = (PgOPT.params['DC'][0] if 'DC' in PgOPT.params and PgOPT.params['DC'][0] else
                        (rmtrec['download'] if rmtrec['download'] else locrec['download']))

   rfiles = PgUpdt.get_remote_names(rfile, rmtrec, rmtinfo, tempinfo)
   rcnt = len(rfiles) if rfiles else 0
   if rcnt == 0:
      PgOPT.PGOPT['rstat'] = -2
      return PgLOG.pglog(rmtinfo + ": NO remote file name identified", PgOPT.PGOPT['emlerr'])

   PgOPT.PGOPT['rcnt'] += rcnt   # accumulate remote file counts
   if tempinfo['DC']: tempinfo['DC'] = None

   if act: # get file names on remote server and create download command
      sfile = rmtrec['serverfile']
      if sfile and sfile != rfile:
         sfiles = PgUpdt.get_remote_names(sfile, rmtrec, rmtinfo, tempinfo)
         scnt = len(sfiles) if sfiles else 0
         if scnt != rcnt:
            PgOPT.PGOPT['rstat'] = -2
            return PgLOG.pglog("{}/{}: {}/{} MISS match file counts".format(rmtinfo, sfile, rcnt, scnt), PgOPT.PGOPT['emlerr'])
      else:
         sfiles = rfiles
         scnt = rcnt

   if tempinfo['AQ']:
      tstr = tempinfo['AQ']
      if tstr == 'Web':
         rpath = "{}/{}/".format(PgLOG.PGLOG['DSDHOME'], PgOPT.params['DS'])
      else:
         rpath = "{}/{}/{}/".format(PgLOG.PGLOG['DECSHOME'], PgOPT.params['DS'], tempinfo['ST'])
   else:
      tstr = 'Remote'
      rpath = ''

   ks = 1 if 'KS' in PgOPT.params else 0
   PgOPT.PGOPT['mcnt'] = ocnt = ecnt = scnt = dcnt = ncnt = 0
   omsize = PgLOG.PGLOG['MINSIZE']
   if 'VS' in tempinfo and 'VS' not in PgOPT.params: PgLOG.PGLOG['MINSIZE'] = tempinfo['VS']
   for i in range(rcnt):
      rfile = rfiles[i]
      rname = rfile['fname']
      rcmd = rfile['rcmd']
      rinfo = PgFile.check_local_file(rpath + rname, 65, PgOPT.PGOPT['emerol'])   # 65 = 1 + 64
      gotnew = 0
      if not act:
         if rinfo:
            dfiles.append(rname)
            dcnt += 1
         else:
            ecnt += 1
            if rfile['amiss']:
               PgLOG.pglog(rname + ": SKIP for NOT gotten {} file yet".format(tstr), PgOPT.PGOPT['emlerr'])
               PgOPT.PGOPT['mcnt'] += 1
            elif 'IE' in PgOPT.params:
               PgLOG.pglog(rname + ": NOT gotten {} file yet".format(tstr), PgOPT.PGOPT['emlerr'])
               PgOPT.PGOPT['rstat'] = -1
            else:
               PgLOG.pglog(rname + ": ERROR for NOT gotten {} file yet".format(tstr), PgOPT.PGOPT['emlerr'])
               PgOPT.PGOPT['rstat'] = -2
               break
         continue
      elif rinfo and 'RD' not in PgOPT.params:
         if not rcmd:
            dfiles.append(rname)
            dcnt += 1
            if tempinfo['archived']:
               if 'CN' not in PgOPT.params:
                  ocnt += 1
               elif PgUtil.cmptime(rinfo['date_modified'], rinfo['time_modified'], tempinfo['ainfo']['adate'], tempinfo['ainfo']['atime']) < 1:
                  ocnt += 1
                  PgLOG.pglog("{}: ARCHIVED, NO newer remote file {} found".format(lfile, rname), PgOPT.PGOPT['emllog'])
            continue
         elif 'CN' in PgOPT.params:
            if rfile['ready'] == -1:   # out of check new period already
               dfiles.append(rname)
               dcnt += 1
               if tempinfo['archived']: ocnt += 1
               continue
         elif PgUtil.cmptime(rinfo['date_modified'], rinfo['time_modified'], rfile['date'], rfile['time']) >= 0:
            dfiles.append(rname)
            dcnt += 1
            if tempinfo['archived']:
               ocnt += 1
            else:
               PgLOG.pglog(rname + ": IS local already", PgOPT.PGOPT['emllog'])
            continue

      sfile = sfiles[i]
      sname = sfile['fname']
      sinfo = rinfo if sname == rname else PgFile.check_local_file(sname, 65, PgOPT.PGOPT['emerol'])
      dact = get_download_action(rcmd)
      rdcnt = 1 if re.search(r'(ncftpget|wget) ', dact) else 0
      dcmd = derr = ""
      info0 = cfile = pcmd = bname = None
      ftype = "remote" if sname == rname else "server"
      if sinfo:
         if rcmd:
            if 'RD' in PgOPT.params:
               PgLOG.pglog(sname + ": ftype file is local, Try dact again", PgOPT.PGOPT['emllog'])
            elif ('CN' not in PgOPT.params and
                  PgUtil.cmptime(sinfo['date_modified'],  sinfo['time_modified'], sfile['date'], sfile['time']) >= 0):
               rcmd = None   # do not need download again
         else:
            PgLOG.pglog("{}: USE the local copy of {} file for NO download command".format(sname, ftype), PgOPT.PGOPT['emllog'])
      elif not rcmd:
         if tempinfo['archived']:
            ocnt += 1
            PgLOG.pglog("{}: ARCHIVED, NO need get {} file {} again for NO download command".format(lfile, ftype, sname), emlsum)
         else:
            ecnt += 1
            if rfile['amiss']:
               PgLOG.pglog(rname + ": SKIP missing remote file for NO download command", PgOPT.PGOPT['emlerr'])
               PgOPT.PGOPT['mcnt'] += 1
            elif 'IE' in PgOPT.params:
               PgLOG.pglog(rname + ": MISS remote file for NO download command", PgOPT.PGOPT['emlerr'])
               PgOPT.PGOPT['rstat'] = -1
            else:
               PgLOG.pglog(rname + ": ERROR missing remote file for NO download command", PgOPT.PGOPT['emlerr'])
               PgOPT.PGOPT['rstat'] = -2
               break
         continue

      if rcmd:  # try to download now
         if not sfile['ready']:
            PgOPT.PGOPT['rstat'] = 0
            PgLOG.pglog("{}: {} file NOT Ready yet".format(sname, ftype), PgOPT.PGOPT['emllog'])
            ecnt += 1
            break
         if 'CN' in PgOPT.params:
            if sinfo:
               cfile = sname
            elif rinfo:
               cfile = rname
               info0 = rinfo
            elif rcnt == 1 and linfo:
               cfile = lfile
               info0 = linfo
            elif tempinfo['archived']:
               cfile = ''

         dcmd = PgUpdt.executable_command(rcmd, sname, PgOPT.params['DS'], sfile['date'], sfile['hour'])
         if tempinfo['AT']:
            stat = check_agetime(dcmd, sname, tempinfo['AT'])
            if stat <= 0:
               PgOPT.PGOPT['rstat'] = stat
               ecnt += 1
               break
         if cfile != None:
            stat = check_newer_file(dcmd, cfile, tempinfo['ainfo'])
            if stat > 0:
               if cfile != sname:
                   if stat < 3: PgLOG.pglog("{}: Found newer {} file {}".format(cfile, ftype, sname), emlsum)
               else:
                   if stat < 3: PgLOG.pglog("{}: Found newer {} file".format(cfile, ftype), emlsum)
               if stat == 2:   # file redlownloaded, reget file info
                  sinfo = PgFile.check_local_file(sname, 64, PgOPT.PGOPT['emerol'])
               else:           # force download file
                  cfile = None
            else:
               if stat < 0:
                  if PgOPT.PGOPT['STATUS']:
                     if cfile != sname:
                        PgLOG.pglog("{}: Error check newer {} file {}\n{}".format(cfile, ftype, sname, PgOPT.PGOPT['STATUS']), PgOPT.PGOPT['emlerr'])
                     else:
                        PgLOG.pglog("{}: Error check newer {} file\n{}".format(cfile, ftype, PgOPT.PGOPT['STATUS']), PgOPT.PGOPT['emlerr'])
                  else:
                     if cfile != sname:
                        PgLOG.pglog("{}: Cannot check newer {} file {} via {}".format(cfile, ftype, sname, dcmd), PgOPT.PGOPT['emlsum'])
                     else:
                        PgLOG.pglog("{}: Cannot check newer {} file via {}".format(cfile, ftype, dcmd), PgOPT.PGOPT['emlsum'])

                  if stat < -1:   # uncrecoverable error
                     PgOPT.PGOPT['rstat'] = stat
                     ecnt += 1
                     break
               elif cfile and cfile != sname:
                  PgLOG.pglog("{}: NO newer {} file {} found\n{}".format(cfile, ftype, sname, PgOPT.PGOPT['STATUS']), emlsum)
               else:
                  PgLOG.pglog("{}: NO newer {} file found\n{}".format(sname, ftype, PgOPT.PGOPT['STATUS']), emlsum)

               if tempinfo['archived']:
                  ncnt += 1
                  if rcnt == 1: continue
               if not info0: info0 = sinfo
               sinfo = None

         if not cfile:
            if op.isfile(sname) and PgLOG.pgsystem("mv -f {} {}.rd".format(sname, sname), PgOPT.PGOPT['emerol'], 4):
               bname = sname + ".rd"
               if not info0: info0 = PgFile.check_local_file(bname, 64, PgOPT.PGOPT['emerol'])
            if dcmd.find('wget ') > -1: PgUpdt.slow_web_access(dcmd)
            PgLOG.pgsystem(dcmd, PgOPT.PGOPT['wrnlog'], 257)   # 1 + 256
            derr = PgLOG.PGLOG['SYSERR']
            sinfo = PgFile.check_local_file(sname, 70, PgOPT.PGOPT['emerol'])
            if sinfo:
               mode = 0o664 if sinfo['isfile'] else 0o775
               if mode != sinfo['mode']: PgFile.set_local_mode(sname, sinfo['isfile'], mode, sinfo['mode'], sinfo['logname'], PgOPT.PGOPT['emerol'])

            (stat, derr) = PgUpdt.parse_download_error(derr, dact, sinfo)
            if stat < -1: # uncrecoverable error
               PgLOG.pglog("{}: error {}\n{}".format(sname, dcmd, derr), PgOPT.PGOPT['emlerr'])
               PgOPT.PGOPT['rstat'] = stat
               ecnt += 1
               break
            elif stat > 0 and PgLOG.PGLOG['DSCHECK'] and sinfo:
               PgCMD.add_dscheck_dcount(0, sinfo['data_size'], PgOPT.PGOPT['extlog'])

      if sinfo:
         if info0:
            if info0['data_size'] == sinfo['data_size'] and bname:
               if PgFile.compare_md5sum(bname, sname, PgOPT.PGOPT['emlsum']):
                  PgLOG.pglog("{}: GOT same size, but different content, {} file via {}".format(sname, ftype, dact), PgOPT.PGOPT['emlsum'])
                  tempinfo['gotnew'] = gotnew = 1
                  PgOPT.PGOPT['rdcnt'] += rdcnt
                  scnt += 1
               else:
                  PgLOG.pglog("{}: GOT same {} file via {}".format(sname, ftype, dact), emlsum)
                  if rinfo and rname != sname and 'KS' not in PgOPT.params:
                     PgLOG.pgsystem("rm -f " + sname, PgOPT.PGOPT['emllog'], 5)
                     sinfo = None
                  if tempinfo['archived']:
                     ncnt += 1
            else:
               PgLOG.pglog("{}: GOT different {} file via {}".format(sname, ftype, dact), PgOPT.PGOPT['emlsum'])
               tempinfo['gotnew'] = gotnew = 1
               PgOPT.PGOPT['rdcnt'] += rdcnt
               scnt += 1
            if bname: PgLOG.pgsystem("rm -rf " + bname, PgOPT.PGOPT['emerol'], 4)
         elif rcmd:
            PgLOG.pglog("{}: GOT {} file via {}".format(sname, ftype, dact), emlsum)
            PgOPT.PGOPT['rdcnt'] += rdcnt
            scnt += 1

         PgOPT.PGOPT['dcnt'] += 1
         if tempinfo['prcmd']: pcmd = tempinfo['prcmd']
      elif info0:
         if bname:
            PgLOG.pglog("{}: RETAIN the older {} file".format(sname, ftype), emlsum)
            PgLOG.pgsystem("mv -f {} {}".format(bname, sname), PgOPT.PGOPT['emerol'], 4)
            if tempinfo['prcmd']: pcmd = tempinfo['prcmd']
            sinfo = info0
         elif cfile:
            if tempinfo['archived']:
               ocnt += 1
            elif rcnt == 1:
               if tempinfo['prcmd']: pcmd = tempinfo['prcmd']
            if cfile == sname:
               sinfo = info0
            elif not rinfo and cfile == lfile:
               continue
      elif not cfile:
         ecnt += 1
         if sfile['amiss']:
            PgLOG.pglog("{}: SKIP {} file for FAIL {}\n{}".format(sname, ftype, dact, derr), PgOPT.PGOPT['emlsum'])
            PgOPT.PGOPT['mcnt'] += 1
         else:
            PgOPT.PGOPT['rstat'] = 0 if 'IE' in PgOPT.params else -1
            if not derr or derr and derr.find(PgLOG.PGLOG['MISSFILE']) > -1:
               msg = "{}: NOT Available for {}\n".format(sname, dact)
               PgLOG.set_email(msg, PgOPT.PGOPT['emlsum'])
               if derr: PgLOG.pglog(derr, PgOPT.PGOPT['emllog'])
            else:
               PgLOG.pglog("{}: ERROR {}\n{}".format(sname, dact, derr), PgOPT.PGOPT['emlerr'])
            if PgOPT.PGOPT['rstat'] < 0: break
         continue
      else:
         ecnt += 1
         if sfile['amiss']: PgOPT.PGOPT['mcnt'] += 1
         continue

      if sinfo:
         if rname == sname:
            rinfo = sinfo
         elif not rinfo or gotnew:
            if rinfo: PgLOG.pgsystem("rm -f " + rname, PgOPT.PGOPT['emerol'], 5)
            if PgFile.convert_files(rname, sname, ks, PgOPT.PGOPT['emerol']):
               rinfo = PgFile.check_local_file(rname, 64, PgOPT.PGOPT['emerol'])
            else:
               PgOPT.PGOPT['rstat'] = -1
               ecnt += 1
               break

      if not rinfo:
         ecnt += 1
         if sfile['amiss']:
            PgLOG.pglog(rname + ": SKIP missing remote file", PgOPT.PGOPT['emlsum'])
            PgOPT.PGOPT['mcnt'] += 1
         elif 'IE' in PgOPT.params:
            PgLOG.pglog(rname + ": MISS remote file", PgOPT.PGOPT['emlerr'])
            PgOPT.PGOPT['rstat'] = -1
         else:
            PgLOG.pglog(rname + ": ERROR missing remote file", PgOPT.PGOPT['emlerr'])
            PgOPT.PGOPT['rstat'] = -2
            break
         continue

      if pcmd:
         pcmd = PgUpdt.executable_command(PgUpdt.replace_pattern(pcmd, rfile['date'], rfile['hour'], tempinfo['FQ']),
                                          rname, PgOPT.params['DS'], rfile['date'], rfile['hour'])
         if not PgLOG.pgsystem(pcmd, PgOPT.PGOPT['emllog'], 259):
            if PgLOG.PGLOG['SYSERR']: PgLOG.pglog(PgLOG.PGLOG['SYSERR'], PgOPT.PGOPT['emlerr'])
            PgOPT.PGOPT['rstat'] = -1
            ecnt += 1
            break
      dfiles.append(rname)
      dcnt += 1

   PgLOG.PGLOG['MINSIZE'] = omsize
   if ncnt == rcnt:
      PgOPT.PGOPT['rstat'] = 0
      if dcnt > 0: dcnt = 0
   elif ecnt > 0:
      s = 's' if rcnt > 1 else ''
      if dcnt > scnt:
         PgLOG.pglog("{}/{} of {} rfile{} obtained/at local".format(scnt, dcnt, rcnt, s), PgOPT.PGOPT['emllog'])
      else:
         PgLOG.pglog("{} of {} rfile{} obtained".format(scnt, rcnt, s), PgOPT.PGOPT['emllog'])
      if dcnt > 0 and ocnt > 0: dcnt = 0
   elif ocnt == rcnt:
      PgOPT.PGOPT['rstat'] = 0

   return dfiles if PgOPT.PGOPT['rstat'] == 1 and dcnt > 0 else None

#
# build up local files
#
def build_local_file(rfiles, lfile, linfo, locrec, tempinfo, lcnt, l):

   emlsum = PgOPT.PGOPT['emlsum'] if (PgOPT.PGOPT['ACTS'] == PgOPT.OPTS['BL'][0]) else PgOPT.PGOPT['emllog']

   if lcnt > 1:
      rcnt = 1
      rmax = l + 1
   else:
      rmax = rcnt = len(rfiles) if rfiles else 0

   rbfile = None
   if linfo:
      if rcnt == 1 and lfile == rfiles[l]: return 1
      if PgLOG.pgsystem("mv -f {} {}".format(lfile, rbfile), PgOPT.PGOPT['emerol'], 4):
         rbfile = lfile + '.rb'
   else:
      s = op.dirname(lfile)
      if s and not op.isdir(s): PgFile.make_local_directory(s, PgOPT.PGOPT['emllog']|PgLOG.EXITLG)

   cext = None
   if locrec['options']:
      ms = re.search(r'-AF\s+([\w\.]+)', locrec['options'], re.I)
      if ms:
         fmt = ms.group(1)
         ms = re.search(r'(\w+)\.TAR(\.|$)', fmt, re.I)
         if ms:   # check compression before tarring
            fmt = ms.group(1)
            ms = re.match(r'^({})$'.format(PgFile.CMPSTR), fmt, re.I)
            if ms: cext = '.' + fmt

   if tempinfo['blcmd']:
      blcmd = PgUpdt.executable_command(PgUpdt.replace_pattern(tempinfo['blcmd'], tempinfo['edate'], tempinfo['ehour'], tempinfo['FQ']),
                                        lfile, PgOPT.params['DS'], tempinfo['edate'], tempinfo['ehour'])
      if not PgLOG.pgsystem(blcmd, PgOPT.PGOPT['emllog']) or PgFile.local_file_size(lfile, 2, PgOPT.PGOPT['emerol']) <= 0:
         ret = PgLOG.pglog("{}: error build {}".format(blcmd, lfile), PgOPT.PGOPT['emlerr'])
      else:
         PgOPT.PGOPT['bcnt'] += 1
         ret = 1

      if rbfile:
         if ret:
            PgLOG.pgsystem("rm -rf " + rbfile, PgOPT.PGOPT['emerol'], 4)
         else:
            PgLOG.pglog(lfile + ": RETAIN the older local file", emlsum)
            PgLOG.pgsystem("mv -f {} {}".format(rbfile, lfile), PgOPT.PGOPT['emerol'], 4)
      return ret

   if lfile[0] == '!':  # executable for build up local file name
      blcmd = PgUpdt.executable_command(lfile[1:], None, PgOPT.params['DS'], tempinfo['edate'], tempinfo['ehour'])
      lfile = PgLOG.pgsystem(blcmd, PgOPT.PGOPT['emllog'], 21)
      if lfile and PgFile.local_file_size(lfile, 2, PgOPT.PGOPT['emerol']) > 0:
         tempinfo['lfile'] = lfile
         return 1
      else:
         return PgLOG.pglog("{}: error build {}".format(blcmd, lfile), PgOPT.PGOPT['emlerr']) 

   if rcnt == 0 and not linfo: return 0   # no remote file found to build local file

   ret = 1
   kr = 1 if 'KR' in PgOPT.params else 0
   if rcnt == 1 and not op.isdir(rfiles[l]):
      rfile = rfiles[l]
   else:
      ms = re.match(r'^(.+)\.({})$'.format(PgFile.CMPSTR), lfile, re.I)
      rfile = ms.group(1) if ms else lfile
      fd = None
      if tempinfo['AQ']:
         if not PgOPT.validate_one_infile(rfile, PgOPT.params['DS']): return 0
         fd = open(rfile, 'w')
         fd.write(tempinfo['AQ'] + "File\n")

      for i in range(rmax):
         tfile = rfiles[i]
         if fd:
            fd.write(tfile + "\n")
            continue

         if op.isfile(tfile) and cext and not re.search(r'{}$'.format(cext), tfile, re.I):
            ms = re.match(r'^(.+)\.({})$'.format(PgFile.CMPSTR), tfile, re.I)
            if ms: tfile = ms.group(1)
            tfile += cext
            if not PgFile.convert_files(tfile, rfiles[i], kr, PgOPT.PGOPT['emllog']):
               if op.exists(rfile): PgLOG.pgsystem("rm -f " + rfile, PgOPT.PGOPT['emllog'])
               ret = PgLOG.pglog("{}: QUIT converting file from {}".format(rfile, tfile), PgOPT.PGOPT['emllog'])
               break
         cmd = "tar -{}vf {} {}".format('u' if i else 'c', rfile, tfile)
         ret = PgLOG.pgsystem(cmd, PgOPT.PGOPT['emllog'])
         if not ret: break

      if fd:
         ret = -1
         fd.close()

      if op.exists(rfile):
         s = "s" if rcnt > 1 else ""
         if tempinfo['AQ']:
            PgLOG.pglog("{}: input file CREATED for backing up {} {} file{}".format(rfile, rcnt, tempinfo['AQ'], s), emlsum)
         else:
            PgLOG.pglog("{}: tar file CREATED from {} file{}".format(rfile, rcnt, s), emlsum)
      else:
         ret = PgLOG.pglog(rfile + ": ERROR creating tar file", PgOPT.PGOPT['emlerr'])

   if ret > 0:
      if lfile != rfile:
         ret = PgFile.convert_files(lfile, rfile, kr, PgOPT.PGOPT['emllog'])
         if ret: PgLOG.pglog("{}: BUILT from {}".format(lfile, rfile), emlsum)
      if ret:
        fsize = PgFile.local_file_size(lfile, 3, PgOPT.PGOPT['emerol'])
        if fsize > 0:
            PgOPT.PGOPT['bcnt'] += 1
            if PgLOG.PGLOG['DSCHECK']: PgCMD.add_dscheck_dcount(0, fsize, PgOPT.PGOPT['extlog'])
        else:
           ret = 0

   if rbfile:
      if ret:
         PgLOG.pgsystem("rm -rf " + rbfile, PgOPT.PGOPT['emerol'], 4)
      else:
         PgLOG.pglog(lfile + ": RETAIN the older local file", emlsum)
         PgLOG.pgsystem("mv -f {} {}".format(rbfile, lfile), PgOPT.PGOPT['emerol'], 4)

   return 1 if ret else 0


#
# append data type to options for given type name if not in options
#
def append_data_type(tname, options):

   mp = r'(^|\s)-{}(\s|$)'.format(tname)
   if not re.search(mp, options, re.I): options += " -{} {}".format(tname, DEFTYPES[tname])
   return options

#
# get data type from options for given type name, and default one if not in options
#
def get_data_type(tname, options):

   mp = r'(^|\s)-{}\s+(\w)(\s|$)'.format(tname)
   ms = re.search(mp, options, re.I)
   return ms.group(2) if ms else DEFTYPES[tname]

#
# archive a data file
#
def archive_data_file(lfile, locrec, tempinfo, eidx):

   growing = -1
   if tempinfo['ainfo']:
      ainfo = tempinfo['ainfo']
      if ainfo['vindex']: growing = PgUpdt.is_growing_file(locrec['locfile'], tempinfo['FQ'])
      tempinfo['ainfo'] = None   # clean the archive info recorded earlier
   else:
      ainfo = {'archived' : 0, 'note' : None}   # reference to empty hash

   PgLOG.pglog("{}: start {} for {}".format(lfile, locrec['action'], tempinfo['einfo']), PgOPT.PGOPT['emllog'])

   options = locrec['options'] if locrec['options'] else ""
   act = locrec['action']
   archfile = None
   if locrec['archfile']: archfile = PgUpdt.replace_pattern(locrec['archfile'], tempinfo['edate'], tempinfo['ehour'], tempinfo['FQ'])
   if act == 'AW':
      if archfile and 'wfile' not in ainfo: ainfo['wfile'] = archfile
      options = append_data_type('WT', options)
   elif act == 'AS':
      if archfile and 'sfile' not in ainfo: ainfo['sfile'] = archfile
      options = append_data_type('ST', options)
   elif act == 'AQ':
      if archfile and 'bfile' not in ainfo: ainfo['bfile'] = archfile
      options = append_data_type('QT', options)

   if tempinfo['archived'] and not ('RA' in PgOPT.params and growing > 0):
      if (ainfo['chksm'] and ainfo['chksm'] == PgOPT.PGOPT['chksm'] or
            ainfo['asize'] and ainfo['asize'] == PgOPT.PGOPT['fsize'] and
            PgUtil.cmptime(PgOPT.PGOPT['fdate'], PgOPT.PGOPT['ftime'], ainfo['adate'], ainfo['atime']) >= 0):
         if 'RA' not in PgOPT.params:
            amsg = "{}: ARCHIVED by {}".format(lfile, ainfo['adate'])
            if tempinfo['ehour'] != None: amsg += ":{:02}".format(ainfo['ahour'])
            PgLOG.pglog(amsg, PgOPT.PGOPT['emllog'])
            if eidx == 0: PgLOG.pglog("Add Mode option -RA if you want to re-archive", PgOPT.PGOPT['emllog'])
            return -1
         elif growing == 0:
            growing = -1

   if growing == 0: tempinfo['archived'] = move_archived_file(ainfo, tempinfo['archived'])

   if tempinfo['AQ']:
      ifopt = 'IF'
   else:
      ifopt = 'LF'
   acmd = "dsarch {} {} -{} {}".format(PgOPT.params['DS'], act, ifopt, lfile)
   if 'wfile' in ainfo: acmd += " -WF " + ainfo['wfile']
   if 'sfile' in ainfo: acmd += " -SF " + ainfo['sfile']
   if 'bfile' in ainfo: acmd += " -QF " + ainfo['bfile']
   if PgOPT.PGOPT['chksm']: acmd += " -MC " + PgOPT.PGOPT['chksm']

   if growing > 0 and not re.search(r'(^|\s)-GF(\s|$)', options, re.I): acmd += " -GF"
   if 'MD' in PgOPT.params and not re.search(r'(^|\s)-MD(\s|$)', options, re.I): acmd += " -MD"
   if not re.search(r'(^|\s)-NE(\s|$)', options, re.I): acmd += " -NE"    # no email in dsarch
   if tempinfo['gotnew'] and not re.search(r'(^|\s)-OE(\s|$)', options, re.I): acmd += " -OE"
   if 'VS' in PgOPT.params:
      acmd += " -VS {}".format(PgOPT.params['VS'])
      if 'VS' in tempinfo: options = re.sub('-VS\s+\d+(\s+|$)', '', options, flags=re.I)
   if tempinfo['RS'] == 1: acmd += " -RS"

   fnote = None
   if locrec['note'] and not re.search(r'(^|\s)-DE(\s|$)', options, re.I):
      note = build_data_note(ainfo['note'], lfile, locrec, tempinfo)
      if note:
         if re.search(r'(\n|\"|\')', note):  # if found \n or ' or ", create temporary input file
            fnote = PgOPT.params['DS'] + ".note"
            nd = open(fnote, 'w')
            nd.write("DE<:>\n{}<:>\n".format(note))
            nd.close()
            acmd += " -IF " + fnote
         else:
            acmd += " -DE '{}'".format(note)

   if options:
      if locrec['cleancmd']: options = re.sub(r'(^-NW\s+|\s+-NW$)', '', options, 1, re.I)
      acmd += " " + PgUpdt.replace_pattern(options, tempinfo['edate'], tempinfo['ehour'], tempinfo['FQ'])

   ret = PgLOG.pgsystem(acmd, PgOPT.PGOPT['emerol'], 69)   # 1 + 4 + 64
   if fnote: PgLOG.pgsystem("rm -f " + fnote, PgOPT.PGOPT['emerol'], 4)

   tempinfo['ainfo'] = file_archive_info(lfile, locrec, tempinfo)
   note = count_update_files(ainfo, tempinfo['ainfo'], ret, tempinfo['RS'])
   PgLOG.pglog("{}: UPDATED({}) for {}".format(lfile, locrec['action'], tempinfo['einfo']), PgOPT.PGOPT['emlsum'])

   return ret

#
# count files updated
#
def count_update_files(oinfo, ninfo, success, rsopt):

   nrecs = ninfo['types'] if ninfo else {}
   orecs = oinfo['types'] if oinfo else {}
   astrs = []
   astr = ""

   for type in nrecs:
      nrec = nrecs[type]
      orec = orecs[type] if type in orecs else None

      if 'sfile' in nrec:
         atype = "Saved {} File".format(PgOPT.STYPE[type])
      elif 'bfile' in nrec:
         atype = "Quasar backup {} File".format(PgOPT.BTYPE[type])
      else:
         atype = "RDA {} File".format(PgOPT.WTYPE[type])
         if rsopt == 1:
            tidx = nrec['tindex'] if nrec['tindex'] else 0
            PgOPT.PGOPT['wtidx'][tidx] = 1

      if (not orec or
          nrec['data_size'] != orec['data_size'] or
          PgUtil.cmptime(orec['date_modified'], orec['time_modified'], nrec['date_modified'], nrec['time_modified']) or
          not (nrec['checksum'] and orec['checksum'] and nrec['checksum'] == orec['checksum'])):
         if 'sfile' in nrec:
            PgOPT.PGOPT['uscnt'] += 1
         elif 'bfile' in nrec:
            if type == 'D': PgOPT.PGOPT['qdcnt'] += 1
            PgOPT.PGOPT['qbcnt'] += 1
         elif type == 'D':
            PgOPT.PGOPT['udcnt'] += 1
         elif type == 'N':
            PgOPT.PGOPT['uncnt'] += 1
         else:
            PgOPT.PGOPT['uwcnt'] += 1

         astrs.append("{} {}rchived".format(atype, "Re-a" if orec else "A"))
         if PgLOG.PGLOG['DSCHECK']:
            PgCMD.add_dscheck_dcount(0, nrec['data_size'], PgOPT.PGOPT['extlog'])

   if astrs:
      PgOPT.PGOPT['ucnt'] += 1
      if len(astrs)  < ninfo['archcnt']:
         if success:
            astr = " Successful, but only "
         else:
            astr = " Partially finished, "
         astr += ', '.join(astrs)
   else:
      if success:
         astr = " Successful, but NO file Re-archived"
      else:
         astr = " Failed, NO file {}rchived".format('Re-a' if oinfo['present'] == ninfo['archcnt'] else "A")

   if astr:
      s = "s" if ninfo['archcnt'] > 1 else ""
      astr += " of {} archfile{}".format(ninfo['archcnt'], s)

   return astr

#
# get the temporal info in local and remote file names and the possible values
# between the break update and the current date
# BTW, change to working directory
#
def get_tempinfo(locrec, locinfo, eidx = 0):

   # get data end date for update action
   edate = PgOPT.params['ED'][eidx] if ('ED' in PgOPT.params and PgOPT.params['ED'][eidx]) else locrec['enddate']
   if not edate: return PgLOG.pglog(locinfo + ": MISS End Data Date for local update", PgOPT.PGOPT['emlerr'])
   ehour = PgOPT.params['EH'][eidx] if ('EH' in PgOPT.params and PgOPT.params['EH'][eidx] != None) else locrec['endhour']
   if not isinstance(edate, str): edate = str(edate)

   if ehour is None and PgDBI.pgget('drupdt', '', "lindex = {} and tinterval like '%H'".format(locrec['lindex'])):
      return PgLOG.pglog(locinfo + ": MISS End Data Hour for hourly remote update", PgOPT.PGOPT['emlerr'])

   if locrec['validint']:
      val = locrec['validint']
   elif PgOPT.PGOPT['UCNTL'] and PgOPT.PGOPT['UCNTL']['validint']:
      val = PgOPT.PGOPT['UCNTL']['validint']
   else:
      val = None

   tempinfo = {'AT' : None, 'DC' : None, 'ED' : [], 'EH' : [], 'VI' : None,
               'VD' : None, 'VH' : None, 'CVD' : None, 'NX' : None, 'FQ' : None,
               'QU' : None, 'EP' : 0, 'RS' : -1, 'AQ' : None}

   if val: val = PgUpdt.get_control_time(val, "Valid Internal")
   if val:
      tempinfo['VI'] = val
      if ehour is None and val[3]: ehour = 0

   val = PgUpdt.get_control_time(locrec['agetime'], "File Age Time")
   if val:
      tempinfo['AT'] = val
      if ehour is None and val[3]: ehour = 0

   frequency = PgOPT.params['FQ'][0] if 'FQ' in PgOPT.params else locrec['frequency']
   if frequency:  # get data update frequency info
      (val, unit) = PgOPT.get_control_frequency(frequency)
      if val:
         tempinfo['FQ'] = val
         tempinfo['QU'] = unit   # update frequency unit of meassure
      else:
         locinfo = PgUpdt.replace_pattern(locinfo, edate, ehour)
         return PgLOG.pglog("{}: {}".format(locinfo, unit), PgOPT.PGOPT['emlerr'])
      if locrec['endperiod']: tempinfo['EP'] = locrec['endperiod']
      if val[3] and ehour is None: ehour = 0
      edate = PgUtil.enddate(edate, tempinfo['EP'], unit, tempinfo['FQ'][6])
   elif 'MU' in PgOPT.params or 'CP' in PgOPT.params:
      locinfo = PgUpdt.replace_pattern(locinfo, edate, ehour)
      return PgLOG.pglog(locinfo + ": MISS frequency for Update", PgOPT.PGOPT['emlerr'])

   val = PgUpdt.get_control_time(locrec['nextdue'], "Due Internval")
   if val:
      tempinfo['NX'] = val
      if ehour is None and val[3]: ehour = 0

   # check if allow missing remote file
   if 'MR' in PgOPT.params and PgOPT.params['MR'][0]:
      tempinfo['amiss'] = PgOPT.params['MR'][0]
   elif locrec['missremote']:
      tempinfo['amiss'] = locrec['missremote']
   else:
      tempinfo['amiss'] = 'N'

   options = locrec['options']
   if locrec['action'] == 'AQ':
      if options:
         ms = re.search(r'-(ST|WT)\s+(\w)', options)
         if ms:
            if ms.group(1) == 'ST':
               tempinfo['AQ'] = 'Saved'
               tempinfo['ST'] = ms.group(2)
            else:
               tempinfo['AQ'] = 'Web'
         else:
            return PgLOG.pglog("{}: MISS -ST or -WT to backup {}".format(options, locinfo), PgOPT.PGOPT['emlerr'])
      else:
         return PgLOG.pglog("Set -ST or -WT in Options to backup {}".format(locinfo), PgOPT.PGOPT['emlerr'])
   if (options and re.search(r'(^|\s)-GX(\s|$)', options, re.I) and
       not re.search(r'(^|\s)-RS(\s|$)', options, re.I)):
      tempinfo['RS'] = 0   # set to 1 if need pass -RS to dsarch 
      ddate = edate
      dhour = ehour
      dcnt = 0
      PgOPT.PGOPT['wtidx'] = {}

   if options:
      ms = re.search(r'-VS\s+(\d+)', options, re.I)
      if ms: tempinfo['VS'] = int(ms.group(1))

   if tempinfo['VI']:
      if tempinfo['VI'][3]:
         (vdate, vhour) = PgUtil.adddatehour(PgOPT.PGOPT['CURDATE'], PgOPT.PGOPT['CURHOUR'], -tempinfo['VI'][0],
                                             -tempinfo['VI'][1], -tempinfo['VI'][2], -tempinfo['VI'][3])
      else:
         vdate = PgUtil.adddate(PgOPT.PGOPT['CURDATE'], -tempinfo['VI'][0], -tempinfo['VI'][1], -tempinfo['VI'][2])
         vhour = PgOPT.PGOPT['CURHOUR']

      if 'CN' in PgOPT.params and locrec['cleancmd']:
         tempinfo['CVD'] = PgUtil.adddate(PgOPT.PGOPT['CURDATE'], -tempinfo['VI'][0], -tempinfo['VI'][1], -(1+tempinfo['VI'][2]))
      tempinfo['setmiss'] = 1
      if PgUtil.diffdatehour(edate, ehour, vdate, vhour) < 0:
         vdate = edate
         vhour = ehour
      if tempinfo['amiss'] == 'N' and locrec['missdate']:
         dhour = PgUtil.diffdatehour(vdate, vhour, locrec['missdate'], locrec['misshour'])
         if dhour > 0:
            if dhour > 240:
               record = {'missdate' : None, 'misshour' : None}
               PgDBI.pgupdt("dlupdt", record, "lindex = {}".format(locrec['lindex']))
            else:
               vdate = locrec['missdate']
               vhour = locrec['misshour']

      if vdate and not isinstance(vdate, str): vdate = str(vdate)
      tempinfo['VD'] = vdate
      tempinfo['VH'] = vhour
      if 'ED' not in PgOPT.params and PgUtil.diffdatehour(edate, ehour, vdate, vhour) > 0:
         edate = vdate
         if tempinfo['FQ']:
            if tempinfo['EP'] or tempinfo['QU'] == 'M':
               edate = PgUtil.enddate(edate, tempinfo['EP'], tempinfo['QU'], tempinfo['FQ'][6])
            while True:
               (udate, uhour) = PgUpdt.addfrequency(edate, ehour, tempinfo['FQ'], -1)
               if PgUtil.diffdatehour(udate, uhour, vdate, vhour) < 0: break
               edate = udate
               ehour = uhour
               if tempinfo['EP'] or tempinfo['QU'] == 'M':
                  edate = PgUtil.enddate(edate, tempinfo['EP'], tempinfo['QU'], tempinfo['FQ'][6])

   vdate = PgOPT.params['CD']
   vhour = PgOPT.params['CH']
   if tempinfo['NX']:
      if tempinfo['NX'][3]:
         (udate, uhour) = PgUtil.adddatehour(PgOPT.PGOPT['CURDATE'], vhour, -tempinfo['NX'][0],
                                             -tempinfo['NX'][1], -tempinfo['NX'][2], -tempinfo['NX'][3])
      else:
         udate = PgUtil.adddate(PgOPT.PGOPT['CURDATE'], -tempinfo['NX'][0], -tempinfo['NX'][1], -tempinfo['NX'][2])
         uhour = vhour
      if PgUtil.diffdatehour(udate, uhour, vdate, vhour) <= 0:
         vdate = udate
         vhour = uhour

   if 'CP' in PgOPT.params: (vdate, vhour) = PgUpdt.addfrequency(vdate, vhour, tempinfo['FQ'], 1)

   fupdate = 1 if 'FU' in PgOPT.params else 0
   while fupdate or PgUtil.diffdatehour(edate, ehour, vdate, vhour) <= 0:
      tempinfo['ED'].append(edate)
      if ehour != None and tempinfo['QU'] != 'H':
         tempinfo['EH'].append(23)
      else:
         tempinfo['EH'].append(ehour)
      if 'MU' not in PgOPT.params: break
      if tempinfo['RS'] == 0 and dcnt < 3:
         if PgUtil.diffdatehour(edate, ehour, ddate, dhour) >= 0: dcnt += 1
      (edate, ehour) = PgUpdt.addfrequency(edate, ehour, tempinfo['FQ'], 1)
      edate = PgUtil.enddate(edate, tempinfo['EP'], tempinfo['QU'], tempinfo['FQ'][6])
      fupdate = 0

   if tempinfo['RS'] == 0 and dcnt > 2: tempinfo['RS'] = 1
   if not tempinfo['ED']: # no end time found, update not due yet
      if tempinfo['NX']:
         (udate, uhour) = PgUtil.adddatehour(edate, ehour, tempinfo['NX'][0], tempinfo['NX'][1], tempinfo['NX'][2], tempinfo['NX'][3])
      else:
         udate = edate
         uhour = ehour
      locinfo = PgUpdt.replace_pattern(locinfo, edate, ehour, tempinfo['FQ'])
      vdate = PgOPT.params['CD']
      val = "Update data"
      if tempinfo['NX']: val += " due"
      if uhour is None:
         locinfo += ": {} on {}".format(val, udate)
      else:
         locinfo += ": {} at {}:{:02}".format(val, udate, uhour)
         vdate += ":{:02}".format(PgOPT.params['CH'])

      return PgLOG.pglog("{} NOT due yet by {}".format(locinfo, vdate), PgOPT.PGOPT['emllog'])
   
   return tempinfo

#
# get archived file info
#
def file_archive_info(lfile, locrec, tempinfo):

   if tempinfo['ainfo'] != None: return tempinfo['ainfo']

   edate = tempinfo['edate']
   ehour = tempinfo['ehour']
   ainfo = {'archcnt' : 0, 'archived' : 0, 'present' : 0, 'vindex' : 0, 'types' : {}, 'note' : None}
   growing = PgUpdt.is_growing_file(locrec['locfile'], tempinfo['FQ'])
   if growing:
      if tempinfo['NX']:
         (udate, uhour) = PgUtil.adddatehour(edate, ehour, tempinfo['NX'][0], tempinfo['NX'][1], tempinfo['NX'][2], tempinfo['NX'][3])
      else:
         udate = edate
         uhour = ehour
      if PgLOG.PGLOG['GMTZ'] and uhour != None: # convert to local times
         (udate, uhour) = PgUtil.adddatehour(udate, uhour, 0, 0, 0, -PgLOG.PGLOG['GMTZ'])

   options = locrec['options'] if locrec['options'] else ""
   act = locrec['action']
   locrec['gindex'] = PgUpdt.get_group_index(options, edate, ehour, tempinfo['FQ'])
   dsid = PgOPT.params['DS']
   gcnd = "gindex = {}".format(locrec['gindex'])
   cnd = "dsid = '{}' AND {}".format(dsid, gcnd)
   mmiss = 0
   if re.match(r'^A(B|W)$', act):   # check existing web files
      ainfo['archcnt'] = 1
      ms = re.search(r'(^|\s)-WT\s+(\w)(\s|$)', options, re.I)
      type = get_data_type('WT', options)
      if locrec['archfile']:
         afile = PgUpdt.replace_pattern(locrec['archfile'], edate, ehour, tempinfo['FQ'])
      else:
         afile = lfile if re.search(r'(^|\s)-KP(\s|$)', lfile, re.I) else op.basename(lfile)
         ms =re.search(r'(^|\s)-WP\s+(\S+)', options, re.I)
         if ms:
            path = PgUpdt.replace_pattern(ms.group(2), edate, ehour, tempinfo['FQ'])
         else:
            path = PgDBI.get_group_field_path(locrec['gindex'], dsid, 'webpath')
         if path: afile = PgLOG.join_paths(path, afile)

      wrec = PgSplit.pgget_wfile(dsid, "*", "{} AND type = '{}' AND wfile = '{}'".format(gcnd, type, afile), PgOPT.PGOPT['extlog'])
      if wrec:
         ainfo['wfile'] = wrec['wfile']
         adate = ainfo['adate'] = str(wrec['date_modified'])
         atime = ainfo['atime'] = str(wrec['time_modified'])
         ahour = None
         if atime:
            ms = re.match(r'^(\d+):', atime)
            if ms: ahour = int(ms.group(1))
         ainfo['ahour'] = ahour
         ainfo['asize'] = wrec['data_size']
         ainfo['chksm'] = wrec['checksum'] if wrec['checksum'] else ''
         ainfo['note']  = wrec['note']
         ainfo['types'][type] = wrec
         ainfo['wtype'] = type
         if not growing or PgUtil.diffdatehour(udate, uhour, adate, ahour) <= 0: ainfo['archived'] += 1
         if wrec['vindex']: ainfo['vindex'] = wrec['vindex']
         ainfo['present'] += 1

   if act == 'AS':   # check existing save files
      ainfo['archcnt'] = 1
      type = get_data_type('ST', options)
      if locrec['archfile']:
         afile = PgUpdt.replace_pattern(locrec['archfile'], edate, ehour, tempinfo['FQ'])
      else:
         afile = lfile if re.search(r'(^|\s)-KP(\s|$)', options, re.I) else op.basename(lfile)
         ms = re.search(r'(^|\s)-SP\s+(\S+)', options, re.I)
         if ms:
            path = PgUpdt.replace_pattern(ms.group(2), edate, ehour, tempinfo['FQ'])
         else:
            path = PgDBI.get_group_field_path(locrec['gindex'], PgOPT.params['DS'], 'savedpath')
         if path: afile = PgLOG.join_paths(path, afile)

      srec = PgDBI.pgget("sfile", "*", "{} AND type = '{}' AND sfile = '{}'".format(cnd, type, afile), PgOPT.PGOPT['extlog'])
      if srec:
         ainfo['sfile'] = srec['sfile']
         adate = ainfo['adate'] = str(srec['date_modified'])
         atime = ainfo['atime'] = str(srec['time_modified'])
         ahour = None
         if atime:
            ms = re.match(r'^(\d+):', atime)
            if ms: ahour = int(ms.group(1))
         ainfo['asize'] = srec['data_size']
         ainfo['chksm'] = srec['checksum'] if srec['checksum'] else ''
         ainfo['note']  = srec['note']
         ainfo['types'][type] = srec
         ainfo['stype'] = type
         if not growing or PgUtil.diffdatehour(udate, uhour, adate, ahour) <= 0: ainfo['archived'] += 1
         if srec['vindex']: ainfo['vindex'] = srec['vindex']
         ainfo['present'] += 1

   if act == 'AQ':   # check existing quasar backup files
      ainfo['archcnt'] = 1
      type = get_data_type('QT', options)
      if locrec['archfile']:
         afile = PgUpdt.replace_pattern(locrec['archfile'], edate, ehour, tempinfo['FQ'])
      else:
         return PgLOG.pglog(lfile + ": Miss Backup file name via (FA|FileArchived)", PgOPT.PGOPT['emlerr'])

      brec = PgDBI.pgget("bfile", "*", "dsid = '{}' AND type = '{}' AND bfile = '{}'".format(PgOPT.params['DS'], type, afile), PgOPT.PGOPT['extlog'])
      if brec:
         ainfo['bfile'] = brec['bfile']
         adate = ainfo['adate'] = str(brec['date_modified'])
         atime = ainfo['atime'] = str(brec['time_modified'])
         ahour = None
         if atime:
            ms = re.match(r'^(\d+):', atime)
            if ms: ahour = int(ms.group(1))
         ainfo['asize'] = brec['data_size']
         ainfo['chksm'] = brec['checksum'] if brec['checksum'] else ''
         ainfo['note']  = brec['note']
         ainfo['types'][type] = brec
         ainfo['btype'] = type
         if not growing or PgUtil.diffdatehour(udate, uhour, adate, ahour) <= 0: ainfo['archived'] += 1
         ainfo['present'] += 1

   if ainfo['archcnt'] == 0:
      PgLOG.pglog("{}: unknown archive action {}".format(lfile, act), PgOPT.PGOPT['extlog'])

   return ainfo   # always returns a hash reference for archiving info

#
# build up data note based on temporal info, keep the begin timestamp
# for existing record; change end timestamp only if new data added
# return None if no change for existing note
#
def build_data_note(onote, lfile, locrec, tempinfo):
   
   note = locrec['note']
   if not note: return onote

   seps = PgOPT.params['PD']
   match = "[^{}]+".format(seps[1])
   edate = tempinfo['edate']
   ehour = tempinfo['ehour']
   
   if note[0] == '!':  # executable for build up data note
      cmd = PgUpdt.executable_command(1, None, None, edate)
      if not cmd: return 0
      return PgLOG.pgsystem(cmd, PgOPT.PGOPT['emllog'], 21)

   # repalce generic patterns first
   note = PgUpdt.replace_pattern(note, None)   # replace generic patterns first

   # get temporal patterns
   patterns = re.findall(r'{}({}){}'.format(seps[0], match, seps[1]), note)
   pcnt = len(patterns)
   if pcnt == 0: return note   # no pattern temporal matches
   if pcnt > 2:
      PgLOG.pglog("{}-{}: TOO many ({}) temporal patterns".format(lfile, note, pcnt), PgOPT.PGOPT['emllog'])
      return onote

   if pcnt == 2:   # replace start time
      if onote:   # get start time from existing note
         replace = "{}{}{}".format(seps[0], patterns[0], seps[1])
         ms = re.match(r'^(.*){}(.*){}'.format(replace, PgOPT.params['PD'][0]), note)
         if ms:
            init = ms.group(1)
            sp = ms.group(2)
            ms = re.search(r'{}(.+){}'.format(init, sp), onote)
            if ms:
               sdate = ms.group(1)
               note = re.sub(replace, sdate, note, 1)
      elif tempinfo['FQ']: # get start time
         (sdate, shour) = PgUpdt.addfrequency(edate, ehour, tempinfo['FQ'], 0)
         note = PgUpdt.replace_pattern(note, sdate, shour, None, 1)

   return PgUpdt.replace_pattern(note, edate, ehour)   # repalce end time now

#
# get data file status info
#
def file_status_info(lfile, rfile, tempinfo):
   
   # check and cache new data info
   finfo = PgFile.check_local_file(lfile, 33, PgOPT.PGOPT['wrnlog'])   # 33 = 1 + 32
   if not finfo:
      PgOPT.PGOPT['chksm'] = ''
      PgOPT.PGOPT['fsize'] = 0
      return

   fdate = finfo['date_modified']
   ftime = finfo['time_modified']
   fhour = None
   ms = re.match(r'^(\d+):', ftime)
   if ms: four = int(ms.group(1))
   PgOPT.PGOPT['fsize'] = finfo['data_size']
   PgOPT.PGOPT['chksm'] = finfo['checksum']

   if rfile and lfile != rfile:
      finfo = PgFile.check_local_file(rfile, 1, PgOPT.PGOPT['wrnlog'])
      if finfo and PgUtil.cmptime(finfo['date_modified'], finfo['time_modified'], fdate, ftime) < 0:
         fdate = finfo['date_modified']
         ftime = finfo['time_modified']
         ms = re.match(r'^(\d+):', ftime)
         if ms: four = int(ms.group(1))

   PgOPT.PGOPT['fdate'] = fdate
   PgOPT.PGOPT['ftime'] = ftime
   PgOPT.PGOPT['fhour'] = fhour
   
   if 'RE' in PgOPT.params:   # reset end data/time/hour
      if tempinfo['NX']:
         if tempinfo['NX'][3]:
            (fdate, fhour) = PgUtil.adddatehour(fdate, fhour, -tempinfo['NX'][0], -tempinfo['NX'][1],
                                                -tempinfo['NX'][2], -tempinfo['NX'][3])
         else:
            fdate = PgUtil.adddate(fdate, -tempinfo['NX'][0], -tempinfo['NX'][1], -tempinfo['NX'][2])

      while True:
         (edate, ehour) = PgUpdt.addfrequency(tempinfo['edate'], tempinfo['ehour'], tempinfo['FQ'], 1)
         edate = PgUtil.enddate(edate, tempinfo['EP'], tempinfo['QU'], tempinfo['FQ'][6])
         if PgUtil.diffdatehour(edate, ehour, fdate, fhour) > 0: break
         tempinfo['edate'] = edate
         tempinfo['ehour'] = ehour

#
# check if a Server file is aged enough for download
# return 1 if valid, 0 if not aged enough, -1 if cannot check
#
def check_agetime(dcmd, sfile, atime):
   
   info = PgUpdt.check_server_file(dcmd, 1)
   if not info:
      sact = get_download_action(dcmd)
      (stat, derr) = PgUpdt.parse_download_error(PgOPT.PGOPT['STATUS'], sact)
      PgOPT.PGOPT['STATUS'] = derr
      PgLOG.pglog("{}: cannot check file age\n{}".format(sfile, PgOPT.PGOPT['STATUS']), PgOPT.PGOPT['emlerr'])
      return stat

   ahour = None
   if atime[3]:
      ms = re.match(r'^(\d+):', info['time_modified'])
      if ms: ahour = int(ms.group(1))
   (adate, ahour) = PgUtil.adddatehour(info['date_modified'], ahour, atime[0], atime[1], atime[2], atime[3])
   if PgUtil.diffdatehour(PgOPT.params['CD'], PgOPT.params['CH'], adate, ahour) >= 0:
      return 1

   if ahour is None:
      PgLOG.pglog(("{}: original {} file ready by {}\n".format(sfile, info['ftype'], info['date_modified']) +
                   "but NOT aged enough for retrieving yet by " + PgOPT.params['CD']), PgOPT.PGOPT['emllog'])
   else:
      PgLOG.pglog(("{}: original {} file ready by {}:{:02}\n".format(sfile, info['ftype'], info['date_modified'], ahour) +
                   "but NOT aged enough for retrieving yet by {}:{:02}".format(PgOPT.params['CD'], PgOPT.params['CH'])), PgOPT.PGOPT['emllog'])

   return 0   # otherwise server file is not aged enough

#
# check if a Server file is changed with different size
# return 1 - file changed, 2 - new file retrieved, 3 - force redlownload,
#        0 - no change , -1 - error check, -2 - cannot check
#
def check_newer_file(dcmd, cfile, ainfo):

   if cfile:
      finfo = PgFile.check_local_file(cfile, 33, PgOPT.PGOPT['wrnlog'])
      if not finfo: return 3   # download if can not check newer
   else:
      finfo = {'isfile' : 0, 'checksum' : ainfo['chksm'], 'data_size' : ainfo['asize'],
               'date_modified' : ainfo['adate'], 'time_modified' : ainfo['atime']}

   cinfo = PgUpdt.check_server_file(dcmd, 33, cfile)
   if not cinfo:
      sact = get_download_action(dcmd)
      (stat, derr) = PgUpdt.parse_download_error(PgOPT.PGOPT['STATUS'], sact)
      PgOPT.PGOPT['STATUS'] = derr
      return stat

   stat = 2 if cinfo['ftype'] == "WGET" else 1
   if finfo['isfile'] and cfile == cinfo['fname'] and finfo['data_size'] and cinfo['data_size'] and cinfo['data_size'] != finfo['data_size']:
      return stat

   PgOPT.PGOPT['STATUS'] = ''
   if (finfo['data_size'] != cinfo['data_size'] or 'checksum' not in cinfo or
       'checksum' not in finfo or finfo['checksum'] != cinfo['checksum']):
      if 'HO' in PgOPT.params and cinfo['ftype'] == "FTP":
         (cdate, ctime) = PgUtil.addhour(cinfo['date_modified'], cinfo['time_modified'], -PgOPT.params['HO'][0])
      else:
         cdate = cinfo['date_modified']
         ctime = cinfo['time_modified']

      if PgUtil.cmptime(cdate, ctime, finfo['date_modified'], finfo['time_modified']) > 0:
         msg = "{} Newer {} {}: {} {} {}".format(PgOPT.params['DS'], cinfo['ftype'], cinfo['fname'], cdate, ctime, cinfo['data_size'])
         if 'checksum' in cinfo: msg += " " + cinfo['checksum']
         msg += "; {}: ".format(cfile if cfile else "archived")
         msg += "{} {} {}".format(finfo['date_modified'], finfo['time_modified'], finfo['data_size'])
         if 'checksum' in finfo: msg += " " + finfo['checksum']
         PgLOG.pglog(msg, PgOPT.PGOPT['wrnlog'])
         return stat

   if 'adate' in ainfo:
      PgOPT.PGOPT['STATUS'] = "archived: {} {}".format(ainfo['adate'], ainfo['atime'])
   elif cfile:
      PgOPT.PGOPT['STATUS'] += "local copy timestamp: {} {}".format(finfo['date_modified'], finfo['time_modified'])

   if 'note' in cinfo:
      PgOPT.PGOPT['STATUS'] += "\n" + cinfo['note']

   return 0

#
# get download action name
#
def get_download_action(dcmd):

   if not dcmd: return "download"

   dact = "DOWNLOAD"
   ms = re.search(r'(^|\S\/)tar\s+-(\w+)\s', dcmd)
   if ms:
      taropt = ms.group(2)
      dact = "UNTAR" if taropt.find('x') > -1 else "TAR"
   else:
      ms = re.match(r'^\s*(\S+)', dcmd)
      if ms:
         dact = op.basename(ms.group(1))
         if dact == "wc":
            ms = re.search(r'\|\s*(\S+)', dcmd)
            if ms: dact = op.basename(ms.group(1))

   return dact

#
# change to working directory if not there yet
#
def change_workdir(wdir, locinfo, edate, ehour, FQ):

   if 'WD' in PgOPT.params and PgOPT.params['WD'][0]: wdir = PgOPT.params['WD'][0]
   if not wdir:
      return PgLOG.pglog(locinfo + ": MISS working directory", PgOPT.PGOPT['emlerr'])
   else:
      wdir = PgLOG.replace_environments(wdir)
      wdir = PgUpdt.replace_pattern(wdir, edate, ehour, FQ)
      if not PgFile.change_local_directory(wdir, PgOPT.PGOPT['emllog']): return 0

      return 1

#
# clean the working copies of remote and local files/directories
#
def clean_files(cleancmd, edate, ehour, lfiles, rfiles, freq):

   lfile = ' '.join(lfiles) if lfiles else ''
   cleancmd = PgUpdt.replace_pattern(cleancmd, edate, ehour, freq)
   cleancmd = PgUpdt.executable_command(cleancmd, lfile, None, None, None, rfiles)
   PgLOG.PGLOG['ERR2STD'] = [PgLOG.PGLOG['MISSFILE']]
   PgLOG.pgsystem(cleancmd, PgOPT.PGOPT['emllog'], 5)
   PgLOG.PGLOG['ERR2STD'] = []

#
# clean files rematching pattern on given date/hour
#
def clean_older_files(cleancmd, workdir, locinfo, edate, locfile, rmtrecs, rcnt, tempinfo):

   rfiles = None
   lfiles = PgUpdt.get_local_names(locfile, tempinfo, edate)
   change_workdir(workdir, locinfo, edate, tempinfo['ehour'], tempinfo['FQ'])

   if rcnt and cleancmd.find(' -RF') > 0:
      rfiles = get_all_remote_files(rmtrecs, rcnt, tempinfo, edate)
   clean_files(cleancmd, edate, tempinfo['ehour'], lfiles, rfiles, tempinfo['FQ'])

#
# get all remote file names for one update period
#
def get_all_remote_files(rmtrecs, rcnt, tempinfo, edate):

   rfiles = []
   for i in range(rcnt): # processs each remote record
      rmtrec = PgUtil.onerecord(rmtrecs, i)
      file = rmtrec['remotefile']
      if not file: continue
      files = PgUpdt.get_remote_names(file, rmtrec, file, tempinfo, edate)
      if files: rfiles.extend(files)

   return rfiles

#
# check remote file status and sed email to specialist for irregular update cases
#
def check_dataset_status():

   if 'CD' in PgOPT.params:
      PgOPT.params['CD'] = PgUtil.format_date(PgOPT.params['CD'])   # standard format in case not yet
   else:
      PgOPT.params['CD'] = PgUtil.curdate()   # default to current date

   condition = "specialist = '{}'".format(PgOPT.params['LN'])
   if 'ED' not in PgOPT.params: condition += " AND enddate < '{}'".format(PgOPT.params['CD'])
   if 'DS' in PgOPT.params: condition += " AND dsid = '{}'".format(PgOPT.params['DS'])
   s = PgUpdt.file_condition('dlupdt', ('L' if 'LI' in PgOPT.params else "FIXA"), None, 1)
   if s: condition += " AND " + s
   condition += " ORDER BY dsid, execorder, lindex"
   locrecs = PgDBI.pgmget("dlupdt", "*", condition, PgOPT.PGOPT['extlog'])
   loccnt = len(locrecs['locfile']) if locrecs else 0
   if not loccnt: return PgLOG.pglog("No Update record found for checking update status on {} for '{}'".format(PgOPT.params['CD'], PgOPT.params['LN']), PgOPT.PGOPT['wrnlog'])

   s = "s" if loccnt > 1 else ""
   PgLOG.pglog("Check {} record{} for update status...".format(loccnt, s), PgOPT.PGOPT['wrnlog'])
   for i in range(loccnt):
      locrec = PgUtil.onerecord(locrecs, i)
      if loccnt == 1 and 'LI' in PgOPT.params and 'LF' in PgOPT.params and len(PgOPT.params['LF']) == 1 and PgOPT.params['LF'][0] != locrec['locfile']:
         locrec['locfile'] = PgOPT.params['LF'][0]
      check_locfile_status(locrec)

   if PgOPT.PGOPT['lcnt'] or PgLOG.PGLOG['ERRMSG']:
      if PgOPT.PGOPT['lcnt']:
         loccnt = PgOPT.PGOPT['lcnt']
         s = "s" if (loccnt > 1) else ""
      SUBJECT = "DSUPDT Status of {} update record{}".format(loccnt, s)
      if 'DS' in PgOPT.params: SUBJECT += " for {}".format(PgOPT.params['DS'])
      TOPMSG = " ready for update of {} local file{}".format(loccnt, s)
      s = "s" if (PgOPT.PGOPT['rcnt'] > 1) else ""
      TOPMSG = "{}/{} remote{}{}".format(PgOPT.PGOPT['ucnt'], PgOPT.PGOPT['rcnt'], s, TOPMSG)
   else:
      PgLOG.pglog("No local file ready for checking {} on {} for {}".format(SUBJECT, PgOPT.params['CD'], PgOPT.params['LN']), PgOPT.PGOPT['wrnlog'])
      SUBJECT = TOPMSG = None

   if PgOPT.PGOPT['UCNTL']:
      PgUpdt.reset_control_time()
      if SUBJECT: SUBJECT += "-C{}".format(PgOPT.PGOPT['UCNTL']['cindex'])

#
# check update status for a given local file
#
def check_locfile_status(locrec):

   loccnd = "lindex = {}".format(locrec['lindex'])
   lfile = locrec['locfile']
   locinfo = "{}-L{}".format(locrec['dsid'], locrec['lindex'])
   if not lfile: return PgLOG.pglog(locinfo + ": local file name NOT specified", PgOPT.PGOPT['emlerr'])
   locinfo += "-" + lfile
   tempinfo = get_tempinfo(locrec, locinfo, 0)
   if not tempinfo: return 0   # simply return if miss temporal info for update

   rmtcnd = loccnd
   rcnd = PgUpdt.file_condition('drupdt', ('D' if 'DO' in PgOPT.params else "RS"), None, 1)
   if rcnd: rmtcnd += " AND " + rcnd
   rmtrecs = PgDBI.pgmget("drupdt", "*", rmtcnd + " ORDER BY dindex, remotefile", PgOPT.PGOPT['extlog'])
   rcnt = len(rmtrecs['remotefile']) if rmtrecs else 0
   if rcnt == 0:
      if rcnd and PgDBI.pgget("drupdt", "", loccnd):
         return PgLOG.pglog("{}: NO remote file record matched for {}".format(locinfo, rcnd), PgOPT.PGOPT['emlerr'])
      rcnt = 1   # create a empty record remote file
      rmtrecs = {'lindex' : locrec['lindex'], 'remotefile' : None, 'serverfile' : None}

   if rcnt == 1:
      if 'RF' in PgOPT.params and len(PgOPT.params['RF']) == 1 and not (rmtrecs['remotefile'][0] and PgOPT.params['RF'][0] == rmtrecs['remotefile'][0]):
         rmtrecs['remotefile'][0] = PgOPT.params['RF'][0]
      if 'SF' in PgOPT.params and len(PgOPT.params['SF']) == 1 and not (rmtrecs['serverfile'][0] and PgOPT.params['SF'][0] == rmtrecs['serverfile'][0]):
         rmtrecs['serverfile'][0] = PgOPT.params['SF'][0]

   ecnt = len(tempinfo['ED'])
   PgOPT.PGOPT['lindex'] = locrec['lindex']
   logact = PgOPT.PGOPT['emllog']

   retcnt = 0
   for i in range(ecnt):
      if ALLCNT > 1 and i > 0:
         tempinfo = get_tempinfo(locrec, locinfo, i)
         if not tempinfo: break
         edate = tempinfo['ED'][0]
         ehour = tempinfo['EH'][0]
      else:
         edate = tempinfo['ED'][i]
         ehour = tempinfo['EH'][i]
      tempinfo['edate'] = edate
      if ehour != None:
         tempinfo['einfo'] = "end data date:hour {}:{:02}".format(edate, ehour)
         tempinfo['ehour'] = ehour
      else:
         tempinfo['einfo'] = "end data date {}".format(edate)
         tempinfo['ehour'] = None

      if 'GZ' in PgOPT.params: tempinfo['einfo'] += "(UTC)"
      lfile = PgUpdt.replace_pattern(locrec['locfile'], edate, ehour, tempinfo['FQ'])
      locinfo = "{}-L{}-{}".format(locrec['dsid'], locrec['lindex'], lfile)
      PgLOG.pglog("{}: Check Update Status for {}".format(locinfo, tempinfo['einfo']), logact)
      logact = PgOPT.PGOPT['emlsep']
      PgOPT.PGOPT['lcnt'] += 1
      j = 0
      while j < rcnt:   # check each remote record, stop checking if error
         pgrec = PgUtil.onerecord(rmtrecs, j)
         if not check_remote_status(pgrec, lfile, locrec, locinfo, tempinfo) and 'CA' not in PgOPT.params:
            break
         j += 1
      if j == 0: break

   PgOPT.PGOPT['lindex'] = 0

   return (1 if retcnt > 0 else 0)

#
# check update status for given remote file
#
def check_remote_status(rmtrec, lfile, locrec, locinfo, tempinfo):

   rfile = rmtrec['remotefile']
   rmtinfo = locinfo
   if not rfile:
      rfile = lfile
      rcnt = 1

   if rfile != locrec['locfile']: rmtinfo += "-" + rfile
   tempinfo['DC'] = (PgOPT.params['DC'][0] if ('DC' in PgOPT.params and PgOPT.params['DC'][0]) else
                     (rmtrec['download'] if rmtrec['download'] else locrec['download']))
   rfiles = PgUpdt.get_remote_names(rfile, rmtrec, rmtinfo, tempinfo)
   rcnt = len(rfiles) if rfiles else 0
   if not rcnt: return PgLOG.pglog(rmtinfo + ": NO remote file name identified", PgOPT.PGOPT['emlerr'])

   PgOPT.PGOPT['rcnt'] += rcnt   # accumulate remote file counts
   if tempinfo['DC']:
      PgOPT.PGOPT['PCNT'] = PgUpdt.count_pattern_path(tempinfo['DC'])
      tempinfo['DC'] = None

   sfile = rmtrec['serverfile']
   if sfile and sfile != rfile:
      sfiles = PgUpdt.get_remote_names(sfile, rmtrec, rmtinfo, tempinfo)
      scnt = len(sfiles) if sfiles else 0
      if scnt != rcnt:
         PgOPT.PGOPT['rstat'] = -2
         return PgLOG.pglog("{}/{}: {}/{} MISS match file counts".format(rmtinfo, sfile, rcnt, scnt), PgOPT.PGOPT['emlerr'])
   else:
      sfiles = rfiles
      scnt = rcnt

   dcnt = 0
   for i in range(rcnt):
      rmtinfo = locinfo
      rfile = rfiles[i]
      if rfile['fname'] != lfile: rmtinfo += "-" + rfile['fname']     
      sfile = sfiles[i]
      if sfile['fname'] != rfile['fname']: rmtinfo += "-" + sfile['fname']
      rcmd = rfile['rcmd']
      if not rcmd:
         return PgLOG.pglog(rmtinfo + ": Missing download command", PgOPT.PGOPT['emlerr'])
      elif not sfile['ready']:
         PgLOG.pglog(rmtinfo + ": NOT Ready yet for update", PgOPT.PGOPT['emllog'])
         break
      dcnt += 1

   return 1 if dcnt else 0

#
# process the update control records
#
def process_update_controls():

   global ALLCNT
   ctime = PgUtil.curtime(1)
   if not ('CI' in PgOPT.params or 'DS' in PgOPT.params):
      PgOPT.set_default_value("SN", PgOPT.params['LN'])

   condition = ("(pid = 0 OR lockhost = '{}') AND cntltime <= '{}'".format(PgLOG.PGLOG['HOSTNAME'], ctime) +
                PgOPT.PgOPT.get_hash_condition('dcupdt') + " ORDER BY hostname DESC, cntltime")
   pgrecs = PgDBI.pgmget("dcupdt", "*", condition, PgOPT.PGOPT['extlog'])

   ALLCNT = len(pgrecs['cindex']) if pgrecs else 0
   if ALLCNT == 0:
      return PgLOG.pglog("No update control record idetified due for process", PgLOG.LOGWRN)

   s = 's' if ALLCNT > 1 else ''
   PgLOG.pglog("Process {} update control record{} ...".format(ALLCNT, s), PgLOG.WARNLG)

   pcnt = 0
   for i in range(ALLCNT):
      pcnt += process_one_control(PgUtil.onerecord(pgrecs, i))
      if pcnt > 1 and not ('CI' in PgOPT.params or 'DS' in PgOPT.params): break
   rmsg = "{} of {} update control{} reprocessed by {}".format(pcnt, ALLCNT, s, PgLOG.PGLOG['CURUID'])
   if PgLOG.PGLOG['CURUID'] != PgOPT.params['LN']: rmsg += " for " + PgOPT.params['LN']
   PgLOG.pglog(rmsg, PgOPT.PGOPT['wrnlog'])

#
# process one update control
#
def process_one_control(pgrec):

   cidx = pgrec['cindex']
   cstr = "Control Index {}".format(cidx)
   if not pgrec['action']: return PgLOG.pglog(cstr + ": Miss update action", PgOPT.PGOPT['errlog'])
   if not (PgOPT.OPTS[pgrec['action']][0]&PgOPT.PGOPT['CNTLACTS']):
      return PgLOG.pglog("{}: Invalid dsupdt action '{}'".format(cstr, pgrec['action']), PgOPT.PGOPT['errlog'])
   if not pgrec['frequency']: return PgLOG.pglog(cstr + ": Miss update Frequency", PgOPT.PGOPT['errlog'])
   if pgrec['pid'] > 0 and PgSIG.check_process(pgrec['pid']):
      if 'CI' in PgOPT.params: PgLOG.pglog("{}: Under processing {}/{}".format(cstr, pgrec['pid'], PgLOG.PGLOG['HOSTNAME']), PgOPT.PGOPT['wrnlog'])
      return 0
   if pgrec['specialist'] != PgOPT.params['LN']:
      return PgLOG.pglog("{}: must be specialist '{}' to process".format(cstr, pgrec['specialist']), PgOPT.PGOPT['errlog'])
   if not ('ED' in PgOPT.params or PgOPT.valid_data_time(pgrec, cstr, PgOPT.PGOPT['wrnlog'])):
      return 0
   cmd = "dsupdt "
   if pgrec['dsid']: cmd += pgrec['dsid'] + ' '
   cmd += "{} -CI {} ".format(pgrec['action'], cidx)
   if PgLOG.PGLOG['CURUID'] != PgOPT.params['LN']: cmd += "-LN " + PgOPT.params['LN']
   cmd += "-d -b"

   # make sure it is not locked
   if PgLock.lock_update_control(cidx, 0, PgOPT.PGOPT['errlog']) <= 0: return 0
   PgLOG.pglog("{}-{}{}: {}".format(PgLOG.PGLOG['HOSTNAME'], pgrec['specialist'], PgLOG.current_datetime(), cmd), PgLOG.LOGWRN|PgLOG.FRCLOG)
   os.system(cmd + " &")
   return 1

#
# move the previous archived version controlled files
#
def move_archived_file(ainfo, archived):

   stat = 0
   if 'wfile' in ainfo:
      type = ainfo['wtype']
      pgrec = ainfo['types'][type]
      if pgrec and pgrec['vindex']:
         tofile = fromfile = ainfo['wfile']
         ftype = "Web"
         ttype = " Saved"
         i = 0
         while True:    # create tofile name
            if i > 0: tofile = "{}.vbu{}".format(fromfile, i)
            if not PgDBI.pgget("sfile", "", "dsid = '{}' AND sfile = '{}'".format(PgOPT.params['DS'], tofile), PgOPT.PGOPT['extlog']):
               break
            i += 1
         stat = PgLOG.pgsystem("dsarch {} MV -WF {} -WT {} -SF {} -ST V -KM -TS".format(PgOPT.params['DS'], fromfile, type, tofile), PgOPT.PGOPT['emerol'], 5)

   if stat == 0 and ainfo['sfile']:
      type = ainfo['stype']
      pgrec = ainfo['types'][type]
      if pgrec and pgrec['vindex']:
         fromfile = ainfo['sfile']
         ftype = "Saved"
         ttype = ''
         i = 0
         while True:    # create tofile name
            tofile = "{}.vbu{}".format(fromfile, i)
            if not PgDBI.pgget("sfile", "", "dsid = '{}' AND sfile = '{}'".format(PgOPT.params['DS'], tofile), PgOPT.PGOPT['extlog']):
               break
            i += 1
         stat = PgLOG.pgsystem("dsarch {} MV -RF {} -OT {} -SF {} -ST V".format(PgOPT.params['DS'], fromfile, type, tofile), PgOPT.PGOPT['emerol'], 5)

   if stat:
      PgOPT.PGOPT['vcnt'] += 1
      if 'NE' in PgOPT.params or 'EE' in PgOPT.params:
         if 'NE' in PgOPT.params: del PgOPT.params['NE']
         if 'EE' in PgOPT.params: del PgOPT.params['EE']
         PgOPT.params['SE'] = 1   # email summary at least
         PgOPT.PGOPT['emllog'] |= PgLOG.EMEROL
      PgLOG.pglog("{}-{}-{}: Found newer version-conrolled {} file; move to{} type V {}".format(PgOPT.params['DS'], type, fromfile, ftype, ttype, tofile), PgOPT.PGOPT['emlsum'])
      archived = 0

   return archived

#
# call main() to start program
#
if __name__ == "__main__": main()
