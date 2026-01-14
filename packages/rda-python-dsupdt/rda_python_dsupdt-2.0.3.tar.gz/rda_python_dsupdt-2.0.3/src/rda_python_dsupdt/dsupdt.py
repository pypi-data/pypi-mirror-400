#!/usr/bin/env python3
##################################################################################
#     Title: dsupdt
#    Author: Zaihua Ji, zji@ucar.edu
#      Date: 10/10/2020
#            2025-02-05 transferred to package rda_python_dsupdt from
#            https://github.com/NCAR/rda-utility-programs.git
#            2025-12-08 convert to class DsUpdt
#   Purpose: python utility program to download remote files,
#            process downloaded files and create local file, and
#            archive local files onto RDA Server
#            save information of web online data files or Saved files into RDADB
#    Github: https://github.com/NCAR/rda-python-dsupdt.git
##################################################################################

import sys
import os
import re
from os import path as op
from .pg_updt import PgUpdt
from rda_python_common.pg_split import PgSplit

class DsUpdt(PgUpdt, PgSplit):
   def __init__(self):
      super().__init__()  # initialize parent class
      self.TEMPINFO = {}
      self.TOPMSG = self.SUBJECT = self.ACTSTR = None
      self.ALLCNT = 0
      self.DEFTYPES = {'WT': 'D', 'ST': 'P', 'QT': 'B'}

   # main function to run dsupdt
   def read_parameters(self):
         self.set_help_path(__file__)
         aname = 'dsupdt'
         self.parsing_input(aname)
         self.check_enough_options(self.PGOPT['CACT'], self.PGOPT['ACTS'])

   # start actions of dsupdt
   def start_actions(self):
      if self.PGOPT['ACTS']&self.OPTS['CU'][0]:
         if 'CI' in self.params:
            if self.cache_update_control(self.params['CI'][0], 1):
                self.check_dataset_status()
         else:
            self.ALLCNT = self.get_option_count(["ED", "EH"])
            self.check_dataset_status(0)
      elif self.PGOPT['ACTS'] == self.OPTS['DL'][0]:
         if 'CI' in self.params:
            self.ALLCNT = len(self.params['CI'])
            self.delete_control_info()
         elif 'RF' in self.params:
            self.ALLCNT = len(self.params['RF'])
            self.delete_remote_info()
         else:
            self.ALLCNT = len(self.params['LI'])
            self.delete_local_info()
      elif self.OPTS[self.PGOPT['CACT']][0]&self.OPTS['GA'][0]:
         self.get_update_info()
      elif self.PGOPT['CACT'] == 'PC':
         self.process_update_controls()
      elif self.PGOPT['ACTS'] == self.OPTS['SA'][0]:
         if 'IF' not in self.params:
            self.action_error("Missing input file via Option -IF")
         if self.get_input_info(self.params['IF'], 'DCUPDT'):
            self.check_enough_options('SC', self.OPTS['SC'][0])
            self.ALLCNT = len(self.params['CI'])
            self.set_control_info()
         if self.get_input_info(self.params['IF'], 'DLUPDT'):
            self.check_enough_options('SL', self.OPTS['SL'][0])
            self.ALLCNT = len(self.params['LI'])
            self.set_local_info()
         if self.get_input_info(self.params['IF'], 'DRUPDT') and self.params['RF']:
            self.check_enough_options('SR', self.OPTS['SR'][0])
            self.ALLCNT = len(self.params['RF']) if 'RF' in self.params else 0
            self.set_remote_info()
      elif self.PGOPT['ACTS'] == self.OPTS['SC'][0]:
         self.ALLCNT = len(self.params['CI'])
         self.set_control_info()
      elif self.PGOPT['ACTS'] == self.OPTS['SL'][0]:
         self.ALLCNT = len(self.params['LI'])
         self.set_local_info()
      elif self.PGOPT['ACTS'] == self.OPTS['SR'][0]:
         self.ALLCNT = len(self.params['RF'])
         self.set_remote_info()
      elif self.PGOPT['ACTS']&self.OPTS['UF'][0]:
         if 'CI' in self.params:
            if self.cache_update_control(self.params['CI'][0], 1): self.dataset_update()
         else:
            self.ALLCNT = self.get_option_count(["ED", "EH"])
            self.dataset_update()
      elif self.PGOPT['ACTS'] == self.OPTS['UL'][0]:
         if 'CI' in self.params:
            self.ALLCNT = len(self.params['CI'])
            self.unlock_control_info()
         if 'LI' in self.params:
            self.ALLCNT = len(self.params['LI'])
            self.unlock_update_info()
      if self.SUBJECT and 'NE' not in self.params and (self.PGLOG['ERRCNT'] or 'EE' not in self.params):
         self.SUBJECT += " on " + self.PGLOG['HOSTNAME']
         self.set_email("{}: {}".format(self.SUBJECT, self.TOPMSG), self.EMLTOP)
         if self.ACTSTR: self.SUBJECT = "{} for {}".format(self.ACTSTR, self.SUBJECT)
         if self.PGSIG['PPID'] > 1: self.SUBJECT += " in CPID {}".format(self.PGSIG['PID'])
         if self.PGLOG['ERRCNT'] > 0: self.SUBJECT += " With Error"
         if self.PGLOG['DSCHECK']:
            self.build_customized_email("dscheck", "einfo", "cindex = {}".format(self.PGLOG['DSCHECK']['cindex']),
                                         self.SUBJECT, self.PGOPT['wrnlog'])
         elif self.PGOPT['UCNTL']:
            self.build_customized_email("dcupdt", "einfo", "cindex = {}".format(self.PGOPT['UCNTL']['cindex']),
                                         self.SUBJECT, self.PGOPT['wrnlog'])
         else:
            self.pglog(self.SUBJECT, self.PGOPT['wrnlog']|self.SNDEML)
      if self.PGLOG['DSCHECK']:
         if self.PGLOG['ERRMSG']:
            self.record_dscheck_error(self.PGLOG['ERRMSG'])
         else:
            self.record_dscheck_status("D")
      if self.OPTS[self.PGOPT['CACT']][2]: self.cmdlog()   # log end time if not getting only action

   # delete update control records for given dsid and control indices
   def delete_control_info(self):
      s = 's' if self.ALLCNT > 1 else ''
      self.pglog("Delete {} update control record{} ...".format(self.ALLCNT, s), self.WARNLG)
      delcnt = modcnt = 0
      for i in range(self.ALLCNT):
         cidx = self.lock_update_control(self.params['CI'][i], 2, self.PGOPT['extlog'])
         if cidx <= 0: continue
         ccnd = "cindex = {}".format(cidx)
         delcnt += self.pgdel("dcupdt", ccnd, self.PGOPT['extlog'])
         modcnt += self.pgexec("UPDATE dlupdt SET cindex = 0 WHERE " + ccnd, self.PGOPT['extlog'])
      self.pglog("{} of {} update control record{} deleted".format(delcnt, self.ALLCNT, s), self.PGOPT['wrnlog'])
      if modcnt > 0:
         s = 's' if modcnt > 1 else ''
         self.pglog("{} associated local file record{} modified".format(modcnt, s), self.PGOPT['wrnlog'])

   # delete local files for given dsid and locfile indices
   def delete_local_info(self):
      s = 's' if self.ALLCNT > 1 else ''
      self.pglog("Delete {} Locfile record{} ...".format(self.ALLCNT, s), self.WARNLG)
      dcnt = delcnt = 0
      for i in range(self.ALLCNT):
         lidx = self.params['LI'][i]
         lcnd = "lindex = {}".format(lidx)
         if self.lock_update(lidx, None, 2, self.PGOPT['errlog']) <= 0: continue
         cnt = self.pgget("drupdt", "", lcnd, self.PGOPT['extlog'])
         if cnt > 0:
            ss = 's' if cnt > 1 else ''
            self.pglog("Delete {} associated remote file record{} for Locfile index {} ...".format(cnt, ss, lidx), self.WARNLG)
            dcnt += self.pgdel("drupdt", lcnd, self.PGOPT['extlog'])
         delcnt += self.pgdel("dlupdt", lcnd, self.PGOPT['extlog'])
      self.pglog("{} of {} Locfile record{} deleted".format(delcnt, self.ALLCNT, s), self.PGOPT['wrnlog'])
      if dcnt > 0:
         s = "s" if (dcnt > 1) else ""
         self.pglog("{} associated Remote file record{} deleted too".format(dcnt, s), self.PGOPT['wrnlog'])

   # delete update remote files for given dsid and remote files/locfile indices
   def delete_remote_info(self):
      s = 's' if self.ALLCNT > 1 else ''
      self.pglog("Delete {} remote file record{} ...".format(self.ALLCNT, s), self.WARNLG)
      self.validate_multiple_options(self.ALLCNT, ["LI", "DO"])
      delcnt = 0
      for i in range(self.ALLCNT):
         lcnd = "lindex = {} AND remotefile = '{}'".format(self.params['LI'][i], self.params['RF'][i])
         if 'DO' in self.params: lcnd += " AND dindex = {}".format(self.params['DO'][i])
         delcnt += self.pgdel("drupdt", lcnd, self.PGOPT['extlog'])
      self.pglog("{} of {} remote file record{} deleted".format(delcnt, self.ALLCNT, s), self.PGOPT['wrnlog'])

   # get update control information
   def get_control_info(self):
      tname = "dcupdt"
      hash = self.TBLHASH[tname]
      self.pglog("Get update control info of {} from RDADB ...".format(self.params['DS']), self.WARNLG)
      lens = fnames = None
      if 'FN' in self.params: fnames = self.params['FN']
      fnames = self.fieldname_string(fnames, self.PGOPT[tname], self.PGOPT['dcall'])
      onames = self.params['ON'] if 'ON' in self.params else "C"
      condition = self.file_condition(tname) + self.get_order_string(onames, tname)
      pgrecs = self.pgmget(tname, "*", condition, self.PGOPT['extlog'])
      if pgrecs and 'FO' in self.params: lens = self.all_column_widths(pgrecs, fnames, hash)
      self.OUTPUT.write("{}{}{}\n".format(self.OPTS['DS'][1], self.params['ES'], self.params['DS']))
      if self.PGOPT['CACT'] == "GA": self.OUTPUT.write("[{}]\n".format(tname.upper()))
      self.OUTPUT.write(self.get_string_titles(fnames, hash, lens) + "\n")
      if pgrecs:
         cnt = self.print_column_format(pgrecs, fnames, hash, lens)
         s = 's' if cnt > 1 else ''
         self.pglog("{} update control record{} retrieved".format(cnt, s), self.PGOPT['wrnlog'])
      else:
         self.pglog("no update control record retrieved", self.PGOPT['wrnlog'])

   # get local file update information
   def get_local_info(self):
      tname = "dlupdt"
      hash = self.TBLHASH[tname]
      self.pglog("Get local file update info of {} from RDADB ...".format(self.params['DS']), self.WARNLG)
      lens = fnames = None
      if 'FN' in self.params: fnames = self.params['FN']
      fnames = self.fieldname_string(fnames, self.PGOPT[tname], self.PGOPT['dlall'])
      onames = self.params['ON'] if 'ON' in self.params else "XL"
      condition = self.file_condition(tname) + self.get_order_string(onames, tname)
      pgrecs = self.pgmget(tname, "*", condition, self.PGOPT['extlog'])
      if pgrecs and 'FO' in self.params: lens = self.all_column_widths(pgrecs, fnames, hash)
      if self.PGOPT['CACT'] == "GL":
         self.OUTPUT.write("{}{}{}\n".format(self.OPTS['DS'][1], self.params['ES'], self.params['DS']))
      else:
         self.OUTPUT.write("[{}]\n".format(tname.upper()))
      self.OUTPUT.write(self.get_string_titles(fnames, hash, lens) + "\n")
      if pgrecs:
         cnt = self.print_column_format(pgrecs, fnames, hash, lens)
         s = 's' if cnt > 1 else ''
         self.pglog("{} locfile record{} retrieved".format(cnt, s), self.PGOPT['wrnlog'])
      else:
         self.pglog("no locfile record retrieved", self.PGOPT['wrnlog'])

   # get remote file update information
   def get_remote_info(self):
      tname = "drupdt"
      hash = self.TBLHASH[tname]
      self.pglog("Get remote file update info of {} from RDADB ...".format(self.params['DS']), self.WARNLG)
      lens = fnames = None
      if 'FN' in self.params: fnames = self.params['FN']
      fnames = self.fieldname_string(fnames, self.PGOPT[tname], self.PGOPT['drall'])
      onames = self.params['ON'] if 'ON' in self.params else "LDF"
      condition = self.file_condition(tname) + self.get_order_string(onames, tname)
      pgrecs = self.pgmget(tname, "*", condition, self.PGOPT['extlog'])
      if pgrecs and 'FO' in self.params: lens = self.all_column_widths(pgrecs, fnames, hash)
      if self.PGOPT['CACT'] == "GR":
         self.OUTPUT.write("{}{}{}\n".format(self.OPTS['DS'][1], self.params['ES'], self.params['DS']))
      else:
         self.OUTPUT.write("[{}]\n".format(tname.upper()))
      self.OUTPUT.write(self.get_string_titles(fnames, hash, lens) + "\n")
      if pgrecs:
         cnt = self.print_column_format(pgrecs, fnames, hash, lens)
         s = 's' if cnt > 1 else ''
         self.pglog("{} remote file record{} retrieved".format(cnt, s), self.PGOPT['wrnlog'])
      else:
         self.pglog("no remote file record retrieved", self.PGOPT['wrnlog'])

   # add or modify update control information
   def set_control_info(self):
      tname = 'dcupdt'
      s = 's' if self.ALLCNT > 1 else ''
      self.pglog("Set {} update control record{} ...".format(self.ALLCNT, s), self.WARNLG)
      addcnt = modcnt = 0
      flds = self.get_field_keys(tname, None, 'C')
      if not flds: return self.pglog("Nothing to set for update control!", self.PGOPT['errlog'])
      self.validate_multiple_values(tname, self.ALLCNT, flds)
      fields = self.get_string_fields(flds, tname)
      for i in range(self.ALLCNT):
         cidx = self.params['CI'][i]
         if cidx > 0:
            if self.lock_update_control(cidx, 2, self.PGOPT['errlog']) <= 0: continue
            cnd = "cindex = {}".format(cidx)
            pgrec = self.pgget(tname, fields, cnd, self.PGOPT['errlog'])
            if not pgrec: self.action_error("Error get update control record for " + cnd)
         else:
            pgrec = None
         record = self.build_record(flds, pgrec, tname, i)
         if record:
            if 'pindex' in record and record['pindex'] and not self.pgget("dcupdt", "", "cindex = {}".format(record['pindex'])):
               self.action_error("Parent control Index {} is not in RDADB".format(record['pindex']))
            if 'action' in record and not re.match(r'^({})$'.format(self.PGOPT['UPDTACTS']), record['action']):
               self.action_error("Action Name '{}' must be one of dsupdt Actions ({})".format(record['action'], self.PGOPT['UPDTACTS']))
            if pgrec:
               record['pid'] = 0
               record['lockhost'] = ''
               modcnt += self.pgupdt(tname, record, cnd, self.PGOPT['errlog']|self.DODFLT)
            else:
               record['dsid'] = self.params['DS']
               if 'specialist' not in record: record['specialist'] = self.params['LN']
               addcnt += self.pgadd(tname, record, self.PGOPT['errlog']|self.DODFLT)
         elif cidx: # unlock
            self.lock_update_control(cidx, 0, self.PGOPT['errlog'])
      self.pglog("{}/{} of {} control record{} added/modified".format(addcnt, modcnt, self.ALLCNT, s), self.PGOPT['wrnlog'])

   # add or modify local file update information
   def set_local_info(self):
      tname = 'dlupdt'
      s = 's' if self.ALLCNT > 1 else ''
      self.pglog("Set {} local file record{} ...".format(self.ALLCNT, s), self.WARNLG)
      addcnt = modcnt = 0
      flds = self.get_field_keys(tname, None, 'L')
      if 'RO' in self.params and 'XO' not in self.params: flds += 'X'   
      if not flds: return self.pglog("Nothing to set for update local file!", self.PGOPT['errlog'])
      self.validate_multiple_values(tname, self.ALLCNT, flds)
      fields = self.get_string_fields(flds, tname)
      for i in range(self.ALLCNT):
         lidx = self.params['LI'][i]
         if lidx > 0:
            if self.lock_update(lidx, None, 2, self.PGOPT['errlog']) <= 0: continue
            cnd = "lindex = {}".format(lidx)
            pgrec = self.pgget(tname, fields, cnd, self.PGOPT['errlog'])
            if not pgrec: self.action_error("Error get Local file record for " + cnd)
         else:
            pgrec = None
         if 'RO' in self.params: self.params['XO'][i] = self.get_next_exec_order(self.params['DS'], 0)
         record = self.build_record(flds, pgrec, tname, i)
         if record:
            if 'cindex' in record and record['cindex'] and not self.pgget("dcupdt", "", "cindex = {}".format(record['cindex'])):
               self.action_error("Update control Index {} is not in RDADB".format(record['cindex']))
            if 'action' in record and not re.match(r'^({})$'.format(self.PGOPT['ARCHACTS']), record['action']):
               self.action_error("Action Name '{}' must be one of dsarch Actions ({})".format(record['action'], self.PGOPT['ARCHACTS']))
            if pgrec:
               if 'VI' in record and not record['VI'] and pgrec['missdate']: record['missdate'] = record['misshour'] = None
               record['pid'] = 0
               record['hostname'] = 0
               modcnt += self.pgupdt(tname, record, cnd, self.PGOPT['errlog']|self.DODFLT)
            else:
               record['dsid'] = self.params['DS']
               if 'specialist' not in record: record['specialist'] = self.params['LN']
               if 'execorder' not in record: record['execorder'] = self.get_next_exec_order(self.params['DS'], 1)
               addcnt += self.pgadd(tname, record, self.PGOPT['errlog']|self.DODFLT)
         elif lidx: # unlock
            self.lock_update(lidx, None, 0, self.PGOPT['errlog'])
      self.pglog("{}/{} of {} Locfile record{} added/modified".format(addcnt, modcnt, self.ALLCNT, s), self.PGOPT['wrnlog'])

   # add or modify remote file update information
   def set_remote_info(self):
      tname = 'drupdt'
      s = 's' if self.ALLCNT > 1 else ''
      self.pglog("Set {} update remote file{} ...".format(self.ALLCNT, s), self.WARNLG)
      addcnt = modcnt = 0
      flds = self.get_field_keys(tname)
      if not flds: return self.pglog("Nothing to set for update remote file!", self.PGOPT['errlog'])
      self.validate_multiple_values(tname, self.ALLCNT, flds)
      fields = self.get_string_fields(flds, tname)
      for i in range(self.ALLCNT):
         lidx = self.params['LI'][i]
         didx = self.params['DO'][i] if 'DO' in self.params else 0
         cnd = "lindex = {} AND remotefile = '{}' AND dindex = {}".format(lidx, self.params['RF'][i], didx)
         pgrec = self.pgget("drupdt", fields, cnd, self.PGOPT['errlog'])
         record = self.build_record(flds, pgrec, tname, i)
         if record:
            if 'lindex' in record and record['lindex'] and not self.pgget("dlupdt", "", "lindex = {}".format(record['lindex'])):
               self.action_error("Local file Index {} is not in RDADB".format(record['lindex']))
            if pgrec:
               modcnt += self.pgupdt("drupdt", record, cnd, self.PGOPT['errlog']|self.DODFLT)
            else:
               record['lindex'] = lidx
               record['dsid'] = self.params['DS']
               addcnt += self.pgadd("drupdt", record, self.PGOPT['errlog']|self.DODFLT)
      self.pglog("{}/{} of {} remote file record{} added/modified".format(addcnt, modcnt, self.ALLCNT, s), self.PGOPT['wrnlog'])

   # unlock update records for given locfile indices
   def unlock_update_info(self):
      s = 's' if self.ALLCNT > 1 else ''
      self.pglog("Unlock {} update locfile{} ...".format(self.ALLCNT, s), self.WARNLG)
      modcnt = 0
      for lidx in self.params['LI']:
         cnd = "lindex = {}".format(lidx)
         pgrec = self.pgget("dlupdt", "pid, hostname", cnd, self.PGOPT['extlog'])
         if not pgrec:
            self.pglog("{}: Local File Not exists".format(lidx), self.PGOPT['errlog'])
         elif not pgrec['pid']:
            self.pglog("{}: Local File Not locked".format(lidx), self.PGOPT['wrnlog'])
         elif self.lock_update(lidx, None, -1, self.PGOPT['errlog']) > 0:
            modcnt += 1
            self.pglog("{}: Local File Unlocked {}/{}".format(lidx, pgrec['pid'], pgrec['hostname']), self.PGOPT['wrnlog'])
         elif (self.check_host_down(None, pgrec['hostname']) and
               self.lock_update(lidx, None, -2, self.PGOPT['errlog']) > 0):
            modcnt += 1
            self.pglog("{}: Local File Force unlocked {}/{}".format(lidx, pgrec['pid'], pgrec['hostname']), self.PGOPT['wrnlog'])
         else:
            self.pglog("{}: Local File Unable to unlock {}/{}".format(lidx, pgrec['pid'], pgrec['hostname']), self.PGOPT['wrnlog'])
      self.pglog("{} of {} local file record{} unlocked from RDADB".format(modcnt, self.ALLCNT, s), self.LOGWRN)

   # unlock update control records for given locfile indices
   def unlock_control_info(self):
      s = 's' if self.ALLCNT > 1 else ''
      self.pglog("Unlock {} update control{} ...".format(self.ALLCNT, s), self.WARNLG)
      modcnt = 0
      for cidx in self.params['CI']:
         pgrec = self.pgget("dcupdt", "pid, lockhost", "cindex = {}".format(cidx), self.PGOPT['extlog'])
         if not pgrec:
            self.pglog("{}: Update Control Not exists".format(cidx), self.PGOPT['errlog'])
         elif not pgrec['pid']:
            self.pglog("{}: Update Control Not locked".format(cidx), self.PGOPT['wrnlog'])
         elif self.lock_update_control(cidx, -1, self.PGOPT['extlog']) > 0:
            modcnt += 1
            self.pglog("{}: Update Control Unlocked {}/{}".format(cidx, pgrec['pid'], pgrec['lockhost']), self.PGOPT['wrnlog'])
         elif (self.check_host_down(None, pgrec['lockhost']) and
               self.lock_update_control(cidx, -2, self.PGOPT['extlog']) > 0):
            modcnt += 1
            self.pglog("{}: Update Control Force unlocked {}/{}".format(cidx, pgrec['pid'], pgrec['lockhost']), self.PGOPT['wrnlog'])
         else:
            self.pglog("{}: Undate Control Unable to unlock {}/{}".format(cidx, pgrec['pid'], pgrec['lockhost']), self.PGOPT['wrnlog'])
      self.pglog("{} of {} update control record{} unlocked from RDADB".format(modcnt, self.ALLCNT, s), self.LOGWRN)

   # get update info of local and remote files owned by login name
   def get_update_info(self):
      if 'DS' in self.params:
         dsids = {'dsid': [self.params['DS']]}
         dscnt = 1
      else:
         tname = "dlupdt"
         cnd = self.file_condition(tname, None, None, 1)
         if not cnd:
            self.set_default_value("SN", self.params['LN'])
            cnd = self.file_condition(tname, None, None, 1)
         dsids = self.pgmget(tname, "DISTINCT dsid",  cnd, self.PGOPT['extlog'])
         dscnt = len(dsids['dsid']) if dsids else 0
         if dscnt == 0:
            return self.pglog("NO dataset identified for giving condition", self.PGOPT['wrnlog'])
         elif dscnt > 1:
            self.pglog("Get Update Info for {} datasets".format(dscnt), self.PGOPT['wrnlog'])
         self.PGOPT['AUTODS'] = dscnt
      for i in range(dscnt):
         self.params['DS'] = dsids['dsid'][i]
         if self.PGOPT['ACTS'] == self.OPTS['GC'][0]:
            self.get_control_info()
         elif self.PGOPT['ACTS'] == self.OPTS['GL'][0]:
            self.get_local_info()
         elif self.PGOPT['ACTS'] == self.OPTS['GR'][0]:
            self.get_remote_info()
         else:
            if 'ON' in self.params: del self.params['ON']   # use default order string
            if 'FN' not in self.params: self.params['FN'] = 'ALL'
            if self.PGOPT['ACTS']&self.OPTS['GC'][0]: self.get_control_info()
            if self.PGOPT['ACTS']&self.OPTS['GL'][0]: self.get_local_info()
            if self.PGOPT['ACTS']&self.OPTS['GR'][0]: self.get_remote_info()
      if dscnt > 1: self.pglog("Update Info of {} datasets retrieved".format(dscnt), self.PGOPT['wrnlog'])

   # gather due datasets for data update
   def dataset_update(self):
      actcnd = "specialist = '{}'".format(self.params['LN'])
      if self.PGOPT['ACTS']&self.OPTS['AF'][0]: actcnd += " AND action IN ('AW', 'AS', 'AQ')"
      (self.PGOPT['CURDATE'], self.PGOPT['CURHOUR']) = self.curdatehour()
      if 'CD' not in self.params: self.params['CD'] = self.PGOPT['CURDATE']   # default to current date
      if 'CH' not in self.params: self.params['CH'] = self.PGOPT['CURHOUR']   # default to current hour
      if self.ALLCNT > 1 and self.params['MU']: del self.params['MU']
      if 'CN' in self.params and 'RD' in self.params: del self.params['CN']
      if 'CN' in self.params or 'RD' in self.params or 'RA' in self.params:
         if 'MO' in self.params: del self.params['MO']
      elif 'MO' not in self.params and self.PGOPT['CACT'] == "UF":
         self.params['MO'] = -1
      if 'DS' in self.params:
         dsids = [self.params['DS']]
         dscnt = 1
      else:
         if 'CI' not in self.params: actcnd += " AND cindex = 0"
         loccnd = self.file_condition('dlupdt', "LQFIXA", None, 1)
         dscnd = actcnd
         if loccnd: dscnd += " AND " + loccnd
         pgrecs = self.pgmget("dlupdt", "DISTINCT dsid", dscnd, self.PGOPT['extlog'])
         dsids = pgrecs['dsid'] if pgrecs else []
         dscnt = len(dsids)
         if not dscnt: return self.pglog("NO dataset is due for update on {} for {}".format(self.params['CD'], self.params['LN']), self.PGOPT['wrnlog'])
         self.PGOPT['AUTODS'] = dscnt
      actcnd += " ORDER BY execorder, lindex"
      if self.PGLOG['DSCHECK']:
         fcnt = 0
         for i in range(dscnt):
            self.params['DS'] = dsids[i]
            loccnd = self.file_condition('dlupdt', "LQFIXA")
            locrecs = self.pgmget("dlupdt", "*", "{} AND {}".format(loccnd, actcnd), self.PGOPT['extlog'])
            loccnt = len(locrecs['locfile']) if locrecs else 0
            if loccnt == 0: continue
            for j in range(loccnt):
               locrec = self.onerecord(locrecs, j)
               if (loccnt == 1 and 'LI' in self.params and 'LF' in self.params and
                   len(self.params['LF']) == 1 and self.params['LF'][0] != locrec['locfile']):
                  locrec['locfile'] = self.params['LF'][0]
               fcnt += self.file_update(locrec, self.LOGWRN, 1)
         self.set_dscheck_fcount(fcnt, self.LOGERR)
      # check and update data for each dataset
      logact = self.PGOPT['emllog']
      acnt = ucnt = 0
      for i in range(dscnt):
         self.params['DS'] = dsids[i]
         loccnd = self.file_condition('dlupdt', "LQFIXA")
         locrecs = self.pgmget("dlupdt", "*", "{} AND {}".format(loccnd, actcnd), self.PGOPT['extlog'])
         loccnt = len(locrecs['locfile']) if locrecs else 0
         if loccnt == 0:
            s = "-UC{}".format(self.params['CI'][0]) if ('CI' in self.params and len(self.params['CI']) == 1) else ""
            self.pglog("{}{}: no config record of local file found to update for '{}'".format(self.params['DS'], s, self.params['LN']), self.PGOPT['wrnlog'])
            continue
         s = 's' if loccnt > 1 else ''
         self.pglog("{}: {} for {} update record{}".format(self.params['DS'], self.PGOPT['CACT'], loccnt, s), logact)
         logact = self.PGOPT['emlsep']
         for j in range(loccnt):
            locrec = self.onerecord(locrecs, j)
            if (loccnt == 1 and 'LI' in self.params and 'LF' in self.params and
                len(self.params['LF']) == 1 and self.params['LF'][0] != locrec['locfile']):
               locrec['locfile'] = self.params['LF'][0]
            if locrec['cindex']:
               if 'CI' not in self.params:
                  self.params['CI'] = [locrec['cindex']]
                  self.cache_update_control(locrec['cindex'], 0)
                  if 'CN' in self.params and 'RD' in self.params: del self.params['CN']
                  if 'CN' in self.params or 'RD' in self.params or 'RA' in self.params:
                     if 'MO' in self.params: del self.params['MO']
                  elif 'MO' not in self.params and self.PGOPT['CACT'] == "UF":
                     self.params['MO'] = -1
               elif locrec['cindex'] != self.params['CI'][0]:
                  self.pglog("{}-{}: Skipped due to control index {} mismatches {}".format(self.params['DS'], locrec['lindex'], locrec['cindex'], self.params['CI'][0]), self.PGOPT['emlerr'])
                  continue
            self.PGOPT['rstat'] = 1   # reset remote download status for each local file
            if self.PGSIG['MPROC'] > 1: acnt += 1
            fcnt = self.file_update(locrec, logact)
            if self.PGSIG['PPID'] > 1:
               if self.PGOPT['AUTODS'] > 1: self.PGOPT['AUTODS'] = dscnt = 1
               acnt = ucnt = 0   # reinitialize counts for child process
               break   # stop loop in child
            if self.PGSIG['MPROC'] > 1:
               if fcnt == 0:
                  break   # quit
               else:
                  if fcnt > 0: ucnt += 1   # record update count, s is either -1 or 1
                  continue   # non-daemon parent
            if 'QE' in self.params and fcnt <= 0: break
         if self.PGOPT['vcnt'] > 0:
            self.renew_internal_version(self.params['DS'], self.PGOPT['vcnt'])
            self.PGOPT['vcnt'] = 0
         if self.PGSIG['MPROC'] > 1:
            if not self.PGSIG['QUIT'] and j == loccnt: continue
            break
         if self.PGOPT['rcnt']:
            if self.PGOPT['CACT'] == "DR":
               acnt += self.PGOPT['rcnt']
               ucnt += self.PGOPT['dcnt']
            s = 's' if self.PGOPT['rcnt'] > 1 else ''
            if loccnt > 1:
               self.pglog("{}: {} of {} rfile{} gotten!".format(self.params['DS'], self.PGOPT['dcnt'], self.PGOPT['rcnt'], s), self.PGOPT['emllog'])
            self.PGOPT['rcnt'] = self.PGOPT['dcnt'] = 0
         if self.PGOPT['lcnt']:
            if self.PGOPT['CACT'] == "BL" or self.PGOPT['CACT'] == "PB":
               acnt += self.PGOPT['lcnt']
               ucnt += self.PGOPT['bcnt']
            s = 's' if self.PGOPT['lcnt'] > 1 else ''
            if loccnt > 1 and self.PGOPT['bcnt'] > 0:
               self.pglog("{}: {} of {} lfile{} built!".format(self.params['DS'], self.PGOPT['bcnt'], self.PGOPT['lcnt'], s), self.PGOPT['emllog'])
            self.PGOPT['lcnt'] = self.PGOPT['bcnt'] = 0
         if self.PGOPT['acnt']:
            acnt += self.PGOPT['acnt']
            ucnt += self.PGOPT['ucnt']
            s = 's' if self.PGOPT['acnt'] > 1 else ''
            self.pglog("{}: {} of {} local file{} archived!".format(self.params['DS'], self.PGOPT['ucnt'], self.PGOPT['acnt'], s),
                        (self.PGOPT['emlsum'] if dscnt > 1 else self.PGOPT['emllog']))
            self.PGOPT['acnt'] = self.PGOPT['ucnt'] = 0
         if self.PGSIG['PPID'] > 1: break   # stop loop child
      if acnt > 0:
         self.TOPMSG = detail = ""
         if self.PGSIG['MPROC'] > 1:
            s = 's' if acnt > 1 else ''
            self.ACTSTR = "{} of {} CPIDs{} for 'dsupdt {}' started".format(ucnt, acnt, s, self.PGOPT['CACT'])
         else:
            s = 's' if ucnt > 1 else ''
            self.TOPMSG = ""
            if self.PGOPT['CACT'] == "DR":
               atype = "remote file{} gotten".format(s)
            elif self.PGOPT['CACT'] == "BL" or self.PGOPT['CACT'] == "PB":
               atype = "local file{} built".format(s)
            else:
               atype = "local file{} archived".format(s)
               if self.PGOPT['rdcnt'] > 0:
                  s = 's' if self.PGOPT['rdcnt'] > 1 else ''
                  self.TOPMSG = "{} remote server file{} downloaded and ".format(self.PGOPT['rdcnt'], s)
               if self.PGOPT['udcnt'] > 0:
                  if detail: detail += " & "
                  detail += "{} Web Online".format(self.PGOPT['udcnt'])
               if self.PGOPT['uncnt'] > 0:
                  if detail: detail += " & "
                  detail += "{} Glade Only".format(self.PGOPT['uncnt'])
               if self.PGOPT['uwcnt'] > 0:
                  if detail: detail += " & "
                  detail += "{} Web".format(self.PGOPT['uwcnt'])
               if self.PGOPT['uscnt'] > 0:
                  if detail: detail += " & "
                  detail += "{} Saved".format(self.PGOPT['uscnt'])
               if self.PGOPT['qbcnt'] > 0:
                  if detail: detail += " & "
                  detail += "{} Quasar Backup".format(self.PGOPT['qbcnt'])
               if self.PGOPT['qdcnt'] > 0:
                  if detail: detail += " & "
                  detail += "{} Quasar Drdata".format(self.PGOPT['qdcnt'])
            self.ACTSTR = "{} {}".format(ucnt, atype)
         self.TOPMSG += self.ACTSTR
         if detail: self.TOPMSG += " ({})".format(detail)
         if dscnt > 1:
            self.pglog("{} datasets: {}".format(dscnt, self.TOPMSG), self.PGOPT['emlsum'])
         self.SUBJECT = "DSUPDT of "
         if self.PGOPT['AUTODS'] < 2:
            self.SUBJECT += self.params['DS'].upper()
         else:
            self.SUBJECT += "{} Datasets".format(self.PGOPT['AUTODS'])
      if self.PGOPT['UCNTL']:
         self.reset_control_time()
         if self.SUBJECT: self.SUBJECT += "-C{}".format(self.PGOPT['UCNTL']['cindex'])

   # renew internal version number for given dataset
   def renew_internal_version(self, dsid, vcnt):
      s = 's' if vcnt > 1 else ''
      cmd = "dsarch {} SV -NV -DE '{} Data file{} rearchived'".format(dsid, vcnt, s)
      if self.pgsystem(cmd, self.PGOPT['emerol'], 5):  # 1 + 4
         pgrec = self.pgget('dsvrsn', '*', "dsid = '{}' and status = 'A'".format(dsid), self.PGOPT['emerol'])
         if pgrec:
            vmsg = "set to {} for DOI {}".format(pgrec['iversion'], pgrec['doi'])
         else:
            vmsg = 'renewed'
         self.pglog("{}: {} Data file{} rearchived, Internal version number {}".format(dsid, vcnt, s, vmsg), self.PGOPT['emlsum'])

   # cach the total count of files to be archived
   def count_caching(self, locrec, locinfo):
      files = self.expand_serial_pattern(locrec['locfile'])
      scnt = len(files) if files else 1
      if self.ALLCNT > 1:
         ecnt = self.ALLCNT
      else:
         tinfo = self.TEMPINFO[locrec['lindex']] = self.get_tempinfo(locrec, locinfo, 0)
         ecnt = len(tinfo['ED']) if tinfo else 1
      return ecnt * scnt

   # gather/archive due data file for update of each local file
   def file_update(self, locrec, logact, caching = 0):
      lfile = locrec['locfile']
      endonly = retcnt = 0
      lindex = locrec['lindex']
      loccnd = "lindex = {}".format(lindex)
      locinfo = "{}-L{}".format(locrec['dsid'], lindex)
      if not lfile:
         if caching:
            return None
         else:
            return self.pglog(locinfo + ": local file name NOT specified", self.PGOPT['emlerr'])
      locinfo += "-" + lfile
      if locrec['specialist'] != self.params['LN']:
         if caching:
            return None
         else:
            return self.pglog("{}: owner '{}', NOT '{}'".format(locinfo, locrec['specialist'], self.params['LN']), self.PGOPT['emlerr'])
      if caching: return self.count_caching(locrec, locinfo)
      tempinfo = self.TEMPINFO[lindex] if lindex in self.TEMPINFO else self.get_tempinfo(locrec, locinfo, 0)
      if not tempinfo: return 0  # simply return if miss temporal info for update
      rmtcnd = loccnd
      rcnd = self.file_condition('drupdt', ('D' if 'DO' in self.params else "RS"), None, 1)
      if rcnd: rmtcnd += " AND " + rcnd
      rmtrecs = self.pgmget("drupdt", "*", rmtcnd + " ORDER BY dindex, remotefile", self.PGOPT['extlog'])
      rcnt = len(rmtrecs['remotefile']) if rmtrecs else 0
      if rcnt == 0:
         if rcnd and self.pgget("drupdt", "", loccnd):
            return self.pglog("{}: NO remote file record matched for {}".format(locinfo, rcnd), self.PGOPT['emlerr'])
         # create a empty record remote file
         rcnt = 1
         rmtrecs = {'lindex': [lindex], 'dindex': [0]}
         rflds = ['remotefile', 'serverfile', 'download', 'begintime', 'endtime', 'tinterval']
         for rfld in rflds: rmtrecs[rfld] = [None]
      if rcnt == 1:
         if 'RF' in self.params and len(self.params['RF']) == 1 and not (rmtrecs['remotefile'][0] and self.params['RF'][0] == rmtrecs['remotefile'][0]):
             rmtrecs['remotefile'][0] = self.params['RF'][0]
         if 'SF' in self.params and len(self.params['SF']) == 1 and not (rmtrecs['serverfile'][0] and self.params['SF'][0] == rmtrecs['serverfile'][0]):
             rmtrecs['serverfile'][0] = self.params['SF'][0]
      ecnt = self.ALLCNT if self.ALLCNT > 1 else len(tempinfo['ED'])   # should be at least one
      if self.PGSIG['MPROC'] > 1:
         pname = "updt{}".format(lindex)
         pid = self.start_child(pname, self.PGOPT['wrnlog'], 1)   # try to start a child process
         if pid <= 0: return pid   # failed to start a child process
         if self.PGSIG['PPID'] > 1:
            self.set_email()   # empty email in child process
            self.PGOPT['acnt'] = self.PGOPT['ucnt'] = 0
         else:
            edate = tempinfo['ED'][0]
            ehour = tempinfo['EH'][0]
            lfile = self.replace_pattern(locrec['locfile'], edate, ehour, tempinfo['FQ'])
            locinfo = "{}-L{}-{}".format(locrec['dsid'], lindex, lfile)
            if ecnt > 1: locinfo += ", {} Update Periods".format(ecnt)
            self.pglog("CPID {} for 'dsupdt {}' of {}".format(self.pname2cpid(pname), self.PGOPT['CACT'], locinfo), self.PGOPT['emllog'])
            return 1   # no further action in non-daemon program
      if self.lock_update(lindex, locinfo, 1, self.PGOPT['emllog']) <= 0: return 0
      self.PGOPT['lindex'] = lindex
      tempinfo['prcmd'] = self.params['PR'][0] if 'PR' in self.params else locrec['processremote']
      tempinfo['blcmd'] = self.params['BC'][0] if 'BC' in self.params else locrec['buildcmd']
      postcnt = -1
      if self.PGOPT['UCNTL'] and self.PGOPT['CACT'] == self.PGOPT['UCNTL']['action']:
         tempinfo['postcmd'] = self.params['XC'][0] if 'XC' in self.params else self.PGOPT['UCNTL']['execcmd']
         if tempinfo['postcmd']: postcnt = 0
      setmiss = 1 if tempinfo['VD'] else 0
      ufile = uinfo = None
      rscnt = ucnt = lcnt = 0
      for i in range(ecnt):
         if self.ALLCNT > 1 and i > 0:
            tempinfo = self.get_tempinfo(locrec, locinfo, i)
            if not tempinfo: break
            edate = tempinfo['ED'][0]
            ehour = tempinfo['EH'][0]
         else:
            edate = tempinfo['ED'][i]
            ehour = tempinfo['EH'][i]
            if 'RE' in self.params and i and self.diffdatehour(edate, ehour, tempinfo['edate'], tempinfo['ehour']) <= 0:
               continue
         if ucnt and tempinfo['RS'] == 1 and i%20 == 0: self.refresh_metadata(locrec['dsid'])
         tempinfo['edate'] = edate
         if ehour != None:
            tempinfo['einfo'] = "end data date:hour {}:{:02}".format(edate, ehour)
            tempinfo['ehour'] = ehour
         else:
            tempinfo['einfo'] = "end data date {}".format(edate)
            tempinfo['ehour'] = None
         if 'GZ' in self.params: tempinfo['einfo'] += "(UTC)"
         locfiles = self.get_local_names(locrec['locfile'], tempinfo)
         lcnt = len(locfiles) if locfiles else 0
         if not lcnt: break
         rmtcnt = acnt = ccnt = ut = 0
         rfiles = rfile = None
         if tempinfo['RS'] == 0 and lcnt > 2: tempinfo['RS'] = 1
         for l in range(lcnt):
            if self.PGLOG['DSCHECK'] and ((l+1)%20) == 0:
               self.add_dscheck_dcount(20, 0, self.PGOPT['extlog'])
            lfile = locfiles[l]
            locinfo = "{}-L{}-{}".format(locrec['dsid'], lindex, lfile)
            tempinfo['gotnew'] = tempinfo['archived'] = 0
            tempinfo['ainfo'] = None
            tempinfo['ainfo'] = self.file_archive_info(lfile, locrec, tempinfo)
            if not tempinfo['ainfo']: continue
            if tempinfo['ainfo']['archived'] == tempinfo['ainfo']['archcnt']:
               ufile = "{} at {} {}".format(lfile, tempinfo['ainfo']['adate'], tempinfo['ainfo']['atime'])
               tempinfo['archived'] = 1
               if 'MO' in self.params:
                  if self.params['MO'] < 0:
                     self.pglog("{}: {} already for {}".format(locinfo, self.PGOPT['CACT'], tempinfo['einfo']), self.PGOPT['emlsum'])
                     if i == 0: self.pglog("Add Mode option -RA if you want to re-archive", self.PGOPT['wrnlog'])
                     if 'UT' in self.params or 'ED' not in self.params: ut = 1
                  retcnt += 1
                  continue
            else:
               if self.PGOPT['ACTS']&self.OPTS['AF'][0]: uinfo = locinfo
            self.pglog("{}: {} for {}".format(locinfo, self.PGOPT['CACT'], tempinfo['einfo']), logact)
            if not self.change_workdir(locrec['workdir'], locinfo, tempinfo['edate'], tempinfo['ehour'], tempinfo['FQ']):
               break
            if self.PGOPT['ACTS']&self.OPTS['AF'][0]: self.PGOPT['acnt'] += 1
            if self.PGOPT['ACTS']&self.OPTS['BL'][0]: self.PGOPT['lcnt'] += 1
            opt = 1 if tempinfo['AQ'] else 65  # 1+64(remove small file)
            linfo = self.check_local_file(lfile, opt, self.PGOPT['emerol'])
            cnt = -1
            if rmtcnt > 0:
               cnt = rmtcnt
               rfile = rfiles[l]
            else:
               dr = 1 if self.PGOPT['ACTS']&self.OPTS['PB'][0] else 0
               if linfo and self.PGOPT['CACT'] == "BL" and not tempinfo['prcmd']: dr = 0 # skip download for BL only
               if dr:
                  dfiles = None
                  for j in range(rcnt):   # processs each remote record
                     pgrec = self.onerecord(rmtrecs, j)
                     if dfiles and pgrec['remotefile'] == rfile and not self.PGOPT['mcnt']:
                        continue  # skip
                     rfile = pgrec['remotefile']
                     act = 0 if locrec['action'] == 'AQ' else self.PGOPT['ACTS']&self.OPTS['DR'][0]
                     dfiles = self.download_remote_files(pgrec, lfile, linfo, locrec, locinfo, tempinfo, act)
                     if self.PGOPT['rstat'] < 0:
                        i = ecnt
                        break
                     if dfiles: rfiles = self.joinarray(rfiles, dfiles)
                  rmtcnt = len(rfiles) if rfiles else 0
                  if rmtcnt > 0:
                     if lcnt > 1 and rmtcnt != lcnt:
                        self.pglog("{}: {} files found for {} local files".format(locrec['locinfo'], rmtcnt, lcnt), self.PGOPT['emlerr'])
                        i = ecnt
                        break
                     cnt = rmtcnt
                     rfile = rfiles[l] if lcnt > 1 else rfiles[rmtcnt-1]   # record the break remote file name
                  else:
                     rfile = None
                     if linfo and self.PGOPT['rstat'] == 0: self.PGOPT['rstat'] = 1
            if cnt != 0 and self.PGOPT['rstat'] > 0:
               if self.PGOPT['ACTS']&(self.OPTS['BL'][0]|self.OPTS['AF'][0]):
                  if cnt < 0 and linfo:
                     if tempinfo['archived'] and self.PGOPT['CACT'] == "UF" and not tempinfo['gotnew']:
                        if self.PGOPT['ACTS']&self.OPTS['AF'][0] and 'RA' not in self.params:
                           self.pglog(lfile + ": local file archived already", self.PGOPT['emllog'])
                           cnt = 0
                     else:
                        if self.PGOPT['ACTS']&self.OPTS['BL'][0]:
                           self.pglog(lfile + ": local file exists already", self.PGOPT['emllog'])
                        cnt = 1
                  elif rmtcnt == lcnt and lfile == rfile:
                      if self.PGOPT['ACTS']&self.OPTS['BL'][0]:
                         self.pglog(lfile + ": local file same as remote file", self.PGOPT['emllog'])
                  elif not (self.PGOPT['ACTS']&self.OPTS['BL'][0]):
                     self.pglog(lfile + ": local file not built yet", self.PGOPT['emlerr'])
                     cnt = 0
                  else:
                     cnt = self.build_local_file(rfiles, lfile, linfo, locrec, tempinfo, lcnt, l)
                     if cnt and 'lfile' in tempinfo:
                        lfile = tempinfo['lfile']
                        del tempinfo['lfile']
               if cnt != 0 and (self.PGOPT['ACTS']&self.OPTS['AF'][0]):
                  self.file_status_info(lfile, rfile, tempinfo)
                  cnt = self.archive_data_file(lfile, locrec, tempinfo, i)
                  if cnt > 0:
                     ucnt += 1
                     if tempinfo['RS'] == 1: rscnt += 1
                     if postcnt > -1: postcnt += 1
            elif cnt > 0:
               cnt = 0
            if cnt > 0 and self.PGOPT['rstat'] > 0:
               ccnt += 1
            elif 'UT' in self.params or tempinfo['archived']:
               ut = 1
               if cnt > 0: acnt += 1
         if self.PGLOG['DSCHECK']:
            self.add_dscheck_dcount(lcnt%20, 0, self.PGOPT['extlog'])
         if ccnt == lcnt and (self.PGOPT['ACTS']&self.OPTS['CF'][0]) and locrec['cleancmd']:
            if tempinfo['CVD'] and self.diffdate(edate, tempinfo['CVD']) > 0:
               self.clean_older_files(locrec['cleancmd'], locrec['workdir'], locinfo, tempinfo['CVD'], locrec['locfile'], rmtrecs, rcnt, tempinfo)
            else:
               if not rfiles and rcnt and locrec['cleancmd'].find(' -RF') > -1:
                  rfiles = self.get_all_remote_files(rmtrecs, rcnt, tempinfo, edate)
               self.clean_files(locrec['cleancmd'], edate, ehour, locfiles, rfiles, tempinfo['FQ'])
         if self.PGOPT['ACTS']&self.OPTS['AF'][0] or self.PGOPT['UCNTL'] and self.PGOPT['CACT'] == self.PGOPT['UCNTL']['action']:
            rmonly = 1 if self.PGOPT['rstat'] > 0 else 0
            if ccnt == lcnt:
               self.reset_update_time(locinfo, locrec, tempinfo, ccnt, endonly)
            elif ut:
               self.reset_update_time(locinfo, locrec, tempinfo, acnt, endonly)
            else:
               if self.PGOPT['rstat'] == 0:
                  if tempinfo['VD'] and self.diffdatehour(edate, ehour, tempinfo['VD'], tempinfo['VH']) < 0:
                     self.reset_update_time(locinfo, locrec, tempinfo, 0, endonly)   # skip update
                     self.PGOPT['rstat'] = 1   # reset remote download status
                  elif 'IE' in self.params:
                     if tempinfo['VD'] and self.diffdatehour(edate, ehour, tempinfo['VD'], tempinfo['VH']) >= 0:
                        endonly = 1
                     self.reset_update_time(locinfo, locrec, tempinfo, 0, endonly)   # skip update
                     self.PGOPT['rstat'] = 1   # reset remote download status
            if setmiss: setmiss = self.set_miss_time(lfile, locrec, tempinfo, rmonly)
         if postcnt > 0:
            postcmd = self.executable_command(self.replace_pattern(tempinfo['postcmd'], edate, ehour, tempinfo['FQ']),
                                                lfile, self.params['DS'], edate, ehour)
            self.pgsystem(postcmd, self.PGOPT['emllog'], 5)
            postcnt = 0
         if rscnt >= self.PGOPT['RSMAX']:
            self.refresh_metadata(locrec['dsid'])
            rscnt = 0
         if self.PGOPT['rstat'] < -1 or self.PGOPT['rstat'] < 0 and 'QE' in self.params: break  # unrecoverable errors
      if rscnt > 0: self.refresh_metadata(locrec['dsid'])
      if ufile and uinfo and ucnt == 0:
         self.pglog("{}: Last successful update - {}".format(uinfo, ufile), self.PGOPT['emlsum'])
      self.lock_update(lindex, locinfo, 0, self.PGOPT['errlog'])
      self.PGOPT['lindex'] = 0
      return retcnt

   # refresh the gathered metadata with speed up option -R and -S
   def refresh_metadata(self, dsid):
      sx = "{} -d {} -r".format(self.PGOPT['scm'], dsid)
      if self.PGOPT['wtidx']:
         if 0 in self.PGOPT['wtidx']:
            self.pgsystem(sx + 'w all', self.PGOPT['emllog'], 5)
         else:
            for tidx in self.PGOPT['wtidx']:
               self.pgsystem("{}w {}".format(sx, tidx), self.PGOPT['emllog'], 5)
         self.PGOPT['wtidx'] = {}

   # retrieve remote files# act: > 0 - create filenames and get data files physically; 0 - create filenames only
   def download_remote_files(self, rmtrec, lfile, linfo, locrec, locinfo, tempinfo, act = 0):
      emlsum = self.PGOPT['emlsum'] if self.PGOPT['CACT'] == "DR" else self.PGOPT['emllog']
      rfile = rmtrec['remotefile']
      rmtinfo = locinfo
      dfiles = []
      if not rfile:
         rfile = lfile
         rcnt = 1
      if rfile != locrec['locfile']: rmtinfo += "-" + rfile
      if act:
         tempinfo['DC'] = (self.params['DC'][0] if 'DC' in self.params and self.params['DC'][0] else
                           (rmtrec['download'] if rmtrec['download'] else locrec['download']))
      rfiles = self.get_remote_names(rfile, rmtrec, rmtinfo, tempinfo)
      rcnt = len(rfiles) if rfiles else 0
      if rcnt == 0:
         self.PGOPT['rstat'] = -2
         return self.pglog(rmtinfo + ": NO remote file name identified", self.PGOPT['emlerr'])
      self.PGOPT['rcnt'] += rcnt   # accumulate remote file counts
      if tempinfo['DC']: tempinfo['DC'] = None
      if act: # get file names on remote server and create download command
         sfile = rmtrec['serverfile']
         if sfile and sfile != rfile:
            sfiles = self.get_remote_names(sfile, rmtrec, rmtinfo, tempinfo)
            scnt = len(sfiles) if sfiles else 0
            if scnt != rcnt:
               self.PGOPT['rstat'] = -2
               return self.pglog("{}/{}: {}/{} MISS match file counts".format(rmtinfo, sfile, rcnt, scnt), self.PGOPT['emlerr'])
         else:
            sfiles = rfiles
            scnt = rcnt
      if tempinfo['AQ']:
         tstr = tempinfo['AQ']
         if tstr == 'Web':
            rpath = "{}/{}/".format(self.PGLOG['DSDHOME'], self.params['DS'])
         else:
            rpath = "{}/{}/{}/".format(self.PGLOG['DECSHOME'], self.params['DS'], tempinfo['ST'])
      else:
         tstr = 'Remote'
         rpath = ''
      ks = 1 if 'KS' in self.params else 0
      self.PGOPT['mcnt'] = ocnt = ecnt = scnt = dcnt = ncnt = 0
      omsize = self.PGLOG['MINSIZE']
      if 'VS' in tempinfo and 'VS' not in self.params: self.PGLOG['MINSIZE'] = tempinfo['VS']
      for i in range(rcnt):
         rfile = rfiles[i]
         rname = rfile['fname']
         rcmd = rfile['rcmd']
         rinfo = self.check_local_file(rpath + rname, 65, self.PGOPT['emerol'])   # 65 = 1 + 64
         gotnew = 0
         if not act:
            if rinfo:
               dfiles.append(rname)
               dcnt += 1
            else:
               ecnt += 1
               if rfile['amiss']:
                  self.pglog(rname + ": SKIP for NOT gotten {} file yet".format(tstr), self.PGOPT['emlerr'])
                  self.PGOPT['mcnt'] += 1
               elif 'IE' in self.params:
                  self.pglog(rname + ": NOT gotten {} file yet".format(tstr), self.PGOPT['emlerr'])
                  self.PGOPT['rstat'] = -1
               else:
                  self.pglog(rname + ": ERROR for NOT gotten {} file yet".format(tstr), self.PGOPT['emlerr'])
                  self.PGOPT['rstat'] = -2
                  break
            continue
         elif rinfo and 'RD' not in self.params:
            if not rcmd:
               dfiles.append(rname)
               dcnt += 1
               if tempinfo['archived']:
                  if 'CN' not in self.params:
                     ocnt += 1
                  elif self.cmptime(rinfo['date_modified'], rinfo['time_modified'], tempinfo['ainfo']['adate'], tempinfo['ainfo']['atime']) < 1:
                     ocnt += 1
                     self.pglog("{}: ARCHIVED, NO newer remote file {} found".format(lfile, rname), self.PGOPT['emllog'])
               continue
            elif 'CN' in self.params:
               if rfile['ready'] == -1:   # out of check new period already
                  dfiles.append(rname)
                  dcnt += 1
                  if tempinfo['archived']: ocnt += 1
                  continue
            elif self.cmptime(rinfo['date_modified'], rinfo['time_modified'], rfile['date'], rfile['time']) >= 0:
               dfiles.append(rname)
               dcnt += 1
               if tempinfo['archived']:
                  ocnt += 1
               else:
                  self.pglog(rname + ": IS local already", self.PGOPT['emllog'])
               continue
         sfile = sfiles[i]
         sname = sfile['fname']
         sinfo = rinfo if sname == rname else self.check_local_file(sname, 65, self.PGOPT['emerol'])
         dact = self.get_download_action(rcmd)
         rdcnt = 1 if re.search(r'(ncftpget|wget) ', dact) else 0
         dcmd = derr = ""
         info0 = cfile = pcmd = bname = None
         ftype = "remote" if sname == rname else "server"
         if sinfo:
            if rcmd:
               if 'RD' in self.params:
                  self.pglog(sname + ": ftype file is local, Try dact again", self.PGOPT['emllog'])
               elif ('CN' not in self.params and
                     self.cmptime(sinfo['date_modified'],  sinfo['time_modified'], sfile['date'], sfile['time']) >= 0):
                  rcmd = None   # do not need download again
            else:
               self.pglog("{}: USE the local copy of {} file for NO download command".format(sname, ftype), self.PGOPT['emllog'])
         elif not rcmd:
            if tempinfo['archived']:
               ocnt += 1
               self.pglog("{}: ARCHIVED, NO need get {} file {} again for NO download command".format(lfile, ftype, sname), emlsum)
            else:
               ecnt += 1
               if rfile['amiss']:
                  self.pglog(rname + ": SKIP missing remote file for NO download command", self.PGOPT['emlerr'])
                  self.PGOPT['mcnt'] += 1
               elif 'IE' in self.params:
                  self.pglog(rname + ": MISS remote file for NO download command", self.PGOPT['emlerr'])
                  self.PGOPT['rstat'] = -1
               else:
                  self.pglog(rname + ": ERROR missing remote file for NO download command", self.PGOPT['emlerr'])
                  self.PGOPT['rstat'] = -2
                  break
            continue
         if rcmd:  # try to download now
            if not sfile['ready']:
               self.PGOPT['rstat'] = 0
               self.pglog("{}: {} file NOT Ready yet".format(sname, ftype), self.PGOPT['emllog'])
               ecnt += 1
               break
            if 'CN' in self.params:
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
            dcmd = self.executable_command(rcmd, sname, self.params['DS'], sfile['date'], sfile['hour'])
            if tempinfo['AT']:
               stat = self.check_agetime(dcmd, sname, tempinfo['AT'])
               if stat <= 0:
                  self.PGOPT['rstat'] = stat
                  ecnt += 1
                  break
            if cfile != None:
               stat = self.check_newer_file(dcmd, cfile, tempinfo['ainfo'])
               if stat > 0:
                  if cfile != sname:
                      if stat < 3: self.pglog("{}: Found newer {} file {}".format(cfile, ftype, sname), emlsum)
                  else:
                      if stat < 3: self.pglog("{}: Found newer {} file".format(cfile, ftype), emlsum)
                  if stat == 2:   # file redlownloaded, reget file info
                     sinfo = self.check_local_file(sname, 64, self.PGOPT['emerol'])
                  else:           # force download file
                     cfile = None
               else:
                  if stat < 0:
                     if self.PGOPT['STATUS']:
                        if cfile != sname:
                           self.pglog("{}: Error check newer {} file {}\n{}".format(cfile, ftype, sname, self.PGOPT['STATUS']), self.PGOPT['emlerr'])
                        else:
                           self.pglog("{}: Error check newer {} file\n{}".format(cfile, ftype, self.PGOPT['STATUS']), self.PGOPT['emlerr'])
                     else:
                        if cfile != sname:
                           self.pglog("{}: Cannot check newer {} file {} via {}".format(cfile, ftype, sname, dcmd), self.PGOPT['emlsum'])
                        else:
                           self.pglog("{}: Cannot check newer {} file via {}".format(cfile, ftype, dcmd), self.PGOPT['emlsum'])
                     if stat < -1:   # uncrecoverable error
                        self.PGOPT['rstat'] = stat
                        ecnt += 1
                        break
                  elif cfile and cfile != sname:
                     self.pglog("{}: NO newer {} file {} found\n{}".format(cfile, ftype, sname, self.PGOPT['STATUS']), emlsum)
                  else:
                     self.pglog("{}: NO newer {} file found\n{}".format(sname, ftype, self.PGOPT['STATUS']), emlsum)
                  if tempinfo['archived']:
                     ncnt += 1
                     if rcnt == 1: continue
                  if not info0: info0 = sinfo
                  sinfo = None
            if not cfile:
               if op.isfile(sname) and self.pgsystem("mv -f {} {}.rd".format(sname, sname), self.PGOPT['emerol'], 4):
                  bname = sname + ".rd"
                  if not info0: info0 = self.check_local_file(bname, 64, self.PGOPT['emerol'])
               if dcmd.find('wget ') > -1: self.slow_web_access(dcmd)
               self.pgsystem(dcmd, self.PGOPT['wrnlog'], 257)   # 1 + 256
               derr = self.PGLOG['SYSERR']
               sinfo = self.check_local_file(sname, 70, self.PGOPT['emerol'])
               if sinfo:
                  mode = 0o664 if sinfo['isfile'] else 0o775
                  if mode != sinfo['mode']: self.set_local_mode(sname, sinfo['isfile'], mode, sinfo['mode'], sinfo['logname'], self.PGOPT['emerol'])
               (stat, derr) = self.parse_download_error(derr, dact, sinfo)
               if stat < -1: # uncrecoverable error
                  self.pglog("{}: error {}\n{}".format(sname, dcmd, derr), self.PGOPT['emlerr'])
                  self.PGOPT['rstat'] = stat
                  ecnt += 1
                  break
               elif stat > 0 and self.PGLOG['DSCHECK'] and sinfo:
                  self.add_dscheck_dcount(0, sinfo['data_size'], self.PGOPT['extlog'])
         if sinfo:
            if info0:
               if info0['data_size'] == sinfo['data_size'] and bname:
                  if self.compare_md5sum(bname, sname, self.PGOPT['emlsum']):
                     self.pglog("{}: GOT same size, but different content, {} file via {}".format(sname, ftype, dact), self.PGOPT['emlsum'])
                     tempinfo['gotnew'] = gotnew = 1
                     self.PGOPT['rdcnt'] += rdcnt
                     scnt += 1
                  else:
                     self.pglog("{}: GOT same {} file via {}".format(sname, ftype, dact), emlsum)
                     if rinfo and rname != sname and 'KS' not in self.params:
                        self.pgsystem("rm -f " + sname, self.PGOPT['emllog'], 5)
                        sinfo = None
                     if tempinfo['archived']:
                        ncnt += 1
               else:
                  self.pglog("{}: GOT different {} file via {}".format(sname, ftype, dact), self.PGOPT['emlsum'])
                  tempinfo['gotnew'] = gotnew = 1
                  self.PGOPT['rdcnt'] += rdcnt
                  scnt += 1
               if bname: self.pgsystem("rm -rf " + bname, self.PGOPT['emerol'], 4)
            elif rcmd:
               self.pglog("{}: GOT {} file via {}".format(sname, ftype, dact), emlsum)
               self.PGOPT['rdcnt'] += rdcnt
               scnt += 1
            self.PGOPT['dcnt'] += 1
            if tempinfo['prcmd']: pcmd = tempinfo['prcmd']
         elif info0:
            if bname:
               self.pglog("{}: RETAIN the older {} file".format(sname, ftype), emlsum)
               self.pgsystem("mv -f {} {}".format(bname, sname), self.PGOPT['emerol'], 4)
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
               self.pglog("{}: SKIP {} file for FAIL {}\n{}".format(sname, ftype, dact, derr), self.PGOPT['emlsum'])
               self.PGOPT['mcnt'] += 1
            else:
               self.PGOPT['rstat'] = 0 if 'IE' in self.params else -1
               if not derr or derr and derr.find(self.PGLOG['MISSFILE']) > -1:
                  msg = "{}: NOT Available for {}\n".format(sname, dact)
                  self.set_email(msg, self.PGOPT['emlsum'])
                  if derr: self.pglog(derr, self.PGOPT['emllog'])
               else:
                  self.pglog("{}: ERROR {}\n{}".format(sname, dact, derr), self.PGOPT['emlerr'])
               if self.PGOPT['rstat'] < 0: break
            continue
         else:
            ecnt += 1
            if sfile['amiss']: self.PGOPT['mcnt'] += 1
            continue
         if sinfo:
            if rname == sname:
               rinfo = sinfo
            elif not rinfo or gotnew:
               if rinfo: self.pgsystem("rm -f " + rname, self.PGOPT['emerol'], 5)
               if self.convert_files(rname, sname, ks, self.PGOPT['emerol']):
                  rinfo = self.check_local_file(rname, 64, self.PGOPT['emerol'])
               else:
                  self.PGOPT['rstat'] = -1
                  ecnt += 1
                  break
         if not rinfo:
            ecnt += 1
            if sfile['amiss']:
               self.pglog(rname + ": SKIP missing remote file", self.PGOPT['emlsum'])
               self.PGOPT['mcnt'] += 1
            elif 'IE' in self.params:
               self.pglog(rname + ": MISS remote file", self.PGOPT['emlerr'])
               self.PGOPT['rstat'] = -1
            else:
               self.pglog(rname + ": ERROR missing remote file", self.PGOPT['emlerr'])
               self.PGOPT['rstat'] = -2
               break
            continue
         if pcmd:
            pcmd = self.executable_command(self.replace_pattern(pcmd, rfile['date'], rfile['hour'], tempinfo['FQ']),
                                             rname, self.params['DS'], rfile['date'], rfile['hour'])
            if not self.pgsystem(pcmd, self.PGOPT['emllog'], 259):
               if self.PGLOG['SYSERR']: self.pglog(self.PGLOG['SYSERR'], self.PGOPT['emlerr'])
               self.PGOPT['rstat'] = -1
               ecnt += 1
               break
         dfiles.append(rname)
         dcnt += 1
      self.PGLOG['MINSIZE'] = omsize
      if ncnt == rcnt:
         self.PGOPT['rstat'] = 0
         if dcnt > 0: dcnt = 0
      elif ecnt > 0:
         s = 's' if rcnt > 1 else ''
         if dcnt > scnt:
            self.pglog("{}/{} of {} rfile{} obtained/at local".format(scnt, dcnt, rcnt, s), self.PGOPT['emllog'])
         else:
            self.pglog("{} of {} rfile{} obtained".format(scnt, rcnt, s), self.PGOPT['emllog'])
         if dcnt > 0 and ocnt > 0: dcnt = 0
      elif ocnt == rcnt:
         self.PGOPT['rstat'] = 0
      return dfiles if self.PGOPT['rstat'] == 1 and dcnt > 0 else None

   # build up local files
   def build_local_file(self, rfiles, lfile, linfo, locrec, tempinfo, lcnt, l):
      emlsum = self.PGOPT['emlsum'] if (self.PGOPT['ACTS'] == self.OPTS['BL'][0]) else self.PGOPT['emllog']
      if lcnt > 1:
         rcnt = 1
         rmax = l + 1
      else:
         rmax = rcnt = len(rfiles) if rfiles else 0
      rbfile = None
      if linfo:
         if rcnt == 1 and lfile == rfiles[l]: return 1
         if self.pgsystem("mv -f {} {}".format(lfile, rbfile), self.PGOPT['emerol'], 4):
            rbfile = lfile + '.rb'
      else:
         s = op.dirname(lfile)
         if s and not op.isdir(s): self.make_local_directory(s, self.PGOPT['emllog']|self.EXITLG)
      cext = None
      if locrec['options']:
         ms = re.search(r'-AF\s+([\w\.]+)', locrec['options'], re.I)
         if ms:
            fmt = ms.group(1)
            ms = re.search(r'(\w+)\.TAR(\.|$)', fmt, re.I)
            if ms:   # check compression before tarring
               fmt = ms.group(1)
               ms = re.match(r'^({})$'.format(self.CMPSTR), fmt, re.I)
               if ms: cext = '.' + fmt
      if tempinfo['blcmd']:
         blcmd = self.executable_command(self.replace_pattern(tempinfo['blcmd'], tempinfo['edate'], tempinfo['ehour'], tempinfo['FQ']),
                                         lfile, self.params['DS'], tempinfo['edate'], tempinfo['ehour'])
         if not self.pgsystem(blcmd, self.PGOPT['emllog']) or self.local_file_size(lfile, 2, self.PGOPT['emerol']) <= 0:
            ret = self.pglog("{}: error build {}".format(blcmd, lfile), self.PGOPT['emlerr'])
         else:
            self.PGOPT['bcnt'] += 1
            ret = 1
         if rbfile:
            if ret:
               self.pgsystem("rm -rf " + rbfile, self.PGOPT['emerol'], 4)
            else:
               self.pglog(lfile + ": RETAIN the older local file", emlsum)
               self.pgsystem("mv -f {} {}".format(rbfile, lfile), self.PGOPT['emerol'], 4)
         return ret
      if lfile[0] == '!':  # executable for build up local file name
         blcmd = self.executable_command(lfile[1:], None, self.params['DS'], tempinfo['edate'], tempinfo['ehour'])
         lfile = self.pgsystem(blcmd, self.PGOPT['emllog'], 21)
         if lfile and self.local_file_size(lfile, 2, self.PGOPT['emerol']) > 0:
            tempinfo['lfile'] = lfile
            return 1
         else:
            return self.pglog("{}: error build {}".format(blcmd, lfile), self.PGOPT['emlerr']) 
      if rcnt == 0 and not linfo: return 0   # no remote file found to build local file
      ret = 1
      kr = 1 if 'KR' in self.params else 0
      if rcnt == 1 and not op.isdir(rfiles[l]):
         rfile = rfiles[l]
      else:
         ms = re.match(r'^(.+)\.({})$'.format(self.CMPSTR), lfile, re.I)
         rfile = ms.group(1) if ms else lfile
         fd = None
         if tempinfo['AQ']:
            if not self.validate_one_infile(rfile, self.params['DS']): return 0
            fd = open(rfile, 'w')
            fd.write(tempinfo['AQ'] + "File\n")
         for i in range(rmax):
            tfile = rfiles[i]
            if fd:
               fd.write(tfile + "\n")
               continue
            if op.isfile(tfile) and cext and not re.search(r'{}$'.format(cext), tfile, re.I):
               ms = re.match(r'^(.+)\.({})$'.format(self.CMPSTR), tfile, re.I)
               if ms: tfile = ms.group(1)
               tfile += cext
               if not self.convert_files(tfile, rfiles[i], kr, self.PGOPT['emllog']):
                  if op.exists(rfile): self.pgsystem("rm -f " + rfile, self.PGOPT['emllog'])
                  ret = self.pglog("{}: QUIT converting file from {}".format(rfile, tfile), self.PGOPT['emllog'])
                  break
            cmd = "tar -{}vf {} {}".format('u' if i else 'c', rfile, tfile)
            ret = self.pgsystem(cmd, self.PGOPT['emllog'])
            if not ret: break
         if fd:
            ret = -1
            fd.close()
         if op.exists(rfile):
            s = "s" if rcnt > 1 else ""
            if tempinfo['AQ']:
               self.pglog("{}: input file CREATED for backing up {} {} file{}".format(rfile, rcnt, tempinfo['AQ'], s), emlsum)
            else:
               self.pglog("{}: tar file CREATED from {} file{}".format(rfile, rcnt, s), emlsum)
         else:
            ret = self.pglog(rfile + ": ERROR creating tar file", self.PGOPT['emlerr'])
      if ret > 0:
         if lfile != rfile:
            ret = self.convert_files(lfile, rfile, kr, self.PGOPT['emllog'])
            if ret: self.pglog("{}: BUILT from {}".format(lfile, rfile), emlsum)
         if ret:
           fsize = self.local_file_size(lfile, 3, self.PGOPT['emerol'])
           if fsize > 0:
               self.PGOPT['bcnt'] += 1
               if self.PGLOG['DSCHECK']: self.add_dscheck_dcount(0, fsize, self.PGOPT['extlog'])
           else:
              ret = 0
      if rbfile:
         if ret:
            self.pgsystem("rm -rf " + rbfile, self.PGOPT['emerol'], 4)
         else:
            self.pglog(lfile + ": RETAIN the older local file", emlsum)
            self.pgsystem("mv -f {} {}".format(rbfile, lfile), self.PGOPT['emerol'], 4)
      return 1 if ret else 0

   # append data type to options for given type name if not in options
   def append_data_type(self, tname, options):
      mp = r'(^|\s)-{}(\s|$)'.format(tname)
      if not re.search(mp, options, re.I): options += " -{} {}".format(tname, self.DEFTYPES[tname])
      return options

   # get data type from options for given type name, and default one if not in options
   def get_data_type(self, tname, options):
      mp = r'(^|\s)-{}\s+(\w)(\s|$)'.format(tname)
      ms = re.search(mp, options, re.I)
      return ms.group(2) if ms else self.DEFTYPES[tname]

   # archive a data file
   def archive_data_file(self, lfile, locrec, tempinfo, eidx):
      growing = -1
      if tempinfo['ainfo']:
         ainfo = tempinfo['ainfo']
         if ainfo['vindex']: growing = self.is_growing_file(locrec['locfile'], tempinfo['FQ'])
         tempinfo['ainfo'] = None   # clean the archive info recorded earlier
      else:
         ainfo = {'archived': 0, 'note': None}   # reference to empty hash
      self.pglog("{}: start {} for {}".format(lfile, locrec['action'], tempinfo['einfo']), self.PGOPT['emllog'])
      options = locrec['options'] if locrec['options'] else ""
      act = locrec['action']
      archfile = None
      if locrec['archfile']: archfile = self.replace_pattern(locrec['archfile'], tempinfo['edate'], tempinfo['ehour'], tempinfo['FQ'])
      if act == 'AW':
         if archfile and 'wfile' not in ainfo: ainfo['wfile'] = archfile
         options = self.append_data_type('WT', options)
      elif act == 'AS':
         if archfile and 'sfile' not in ainfo: ainfo['sfile'] = archfile
         options = self.append_data_type('ST', options)
      elif act == 'AQ':
         if archfile and 'bfile' not in ainfo: ainfo['bfile'] = archfile
         options = self.append_data_type('QT', options)
      if tempinfo['archived'] and not ('RA' in self.params and growing > 0):
         if (ainfo['chksm'] and ainfo['chksm'] == self.PGOPT['chksm'] or
               ainfo['asize'] and ainfo['asize'] == self.PGOPT['fsize'] and
               self.cmptime(self.PGOPT['fdate'], self.PGOPT['ftime'], ainfo['adate'], ainfo['atime']) >= 0):
            if 'RA' not in self.params:
               amsg = "{}: ARCHIVED by {}".format(lfile, ainfo['adate'])
               if tempinfo['ehour'] != None: amsg += ":{:02}".format(ainfo['ahour'])
               self.pglog(amsg, self.PGOPT['emllog'])
               if eidx == 0: self.pglog("Add Mode option -RA if you want to re-archive", self.PGOPT['emllog'])
               return -1
            elif growing == 0:
               growing = -1
      if growing == 0: tempinfo['archived'] = self.move_archived_file(ainfo, tempinfo['archived'])
      if tempinfo['AQ']:
         ifopt = 'IF'
      else:
         ifopt = 'LF'
      acmd = "dsarch {} {} -{} {}".format(self.params['DS'], act, ifopt, lfile)
      if 'wfile' in ainfo: acmd += " -WF " + ainfo['wfile']
      if 'sfile' in ainfo: acmd += " -SF " + ainfo['sfile']
      if 'bfile' in ainfo: acmd += " -QF " + ainfo['bfile']
      if self.PGOPT['chksm']: acmd += " -MC " + self.PGOPT['chksm']
      if growing > 0 and not re.search(r'(^|\s)-GF(\s|$)', options, re.I): acmd += " -GF"
      if 'MD' in self.params and not re.search(r'(^|\s)-MD(\s|$)', options, re.I): acmd += " -MD"
      if not re.search(r'(^|\s)-NE(\s|$)', options, re.I): acmd += " -NE"    # no email in dsarch
      if tempinfo['gotnew'] and not re.search(r'(^|\s)-OE(\s|$)', options, re.I): acmd += " -OE"
      if 'VS' in self.params:
         acmd += " -VS {}".format(self.params['VS'])
         if 'VS' in tempinfo: options = re.sub(r'-VS\s+\d+(\s+|$)', '', options, flags=re.I)
      if tempinfo['RS'] == 1: acmd += " -RS"
      fnote = None
      if locrec['note'] and not re.search(r'(^|\s)-DE(\s|$)', options, re.I):
         note = self.build_data_note(ainfo['note'], lfile, locrec, tempinfo)
         if note:
            if re.search(r'(\n|\"|\')', note):  # if found \n or ' or ", create temporary input file
               fnote = self.params['DS'] + ".note"
               nd = open(fnote, 'w')
               nd.write("DE<:>\n{}<:>\n".format(note))
               nd.close()
               acmd += " -IF " + fnote
            else:
               acmd += " -DE '{}'".format(note)
      if options:
         if locrec['cleancmd']: options = re.sub(r'(^-NW\s+|\s+-NW$)', '', options, 1, re.I)
         acmd += " " + self.replace_pattern(options, tempinfo['edate'], tempinfo['ehour'], tempinfo['FQ'])
      ret = self.pgsystem(acmd, self.PGOPT['emerol'], 69)   # 1 + 4 + 64
      if fnote: self.pgsystem("rm -f " + fnote, self.PGOPT['emerol'], 4)
      tempinfo['ainfo'] = self.file_archive_info(lfile, locrec, tempinfo)
      note = self.count_update_files(ainfo, tempinfo['ainfo'], ret, tempinfo['RS'])
      self.pglog("{}: UPDATED({}) for {}".format(lfile, locrec['action'], tempinfo['einfo']), self.PGOPT['emlsum'])
      return ret

   # count files updated
   def count_update_files(self, oinfo, ninfo, success, rsopt):
      nrecs = ninfo['types'] if ninfo else {}
      orecs = oinfo['types'] if oinfo else {}
      astrs = []
      astr = ""
      for type in nrecs:
         nrec = nrecs[type]
         orec = orecs[type] if type in orecs else None
         if 'sfile' in nrec:
            atype = "Saved {} File".format(self.STYPE[type])
         elif 'bfile' in nrec:
            atype = "Quasar backup {} File".format(self.BTYPE[type])
         else:
            atype = "RDA {} File".format(self.WTYPE[type])
            if rsopt == 1:
               tidx = nrec['tindex'] if nrec['tindex'] else 0
               self.PGOPT['wtidx'][tidx] = 1
         if (not orec or
             nrec['data_size'] != orec['data_size'] or
             self.cmptime(orec['date_modified'], orec['time_modified'], nrec['date_modified'], nrec['time_modified']) or
             not (nrec['checksum'] and orec['checksum'] and nrec['checksum'] == orec['checksum'])):
            if 'sfile' in nrec:
               self.PGOPT['uscnt'] += 1
            elif 'bfile' in nrec:
               if type == 'D': self.PGOPT['qdcnt'] += 1
               self.PGOPT['qbcnt'] += 1
            elif type == 'D':
               self.PGOPT['udcnt'] += 1
            elif type == 'N':
               self.PGOPT['uncnt'] += 1
            else:
               self.PGOPT['uwcnt'] += 1
            astrs.append("{} {}rchived".format(atype, "Re-a" if orec else "A"))
            if self.PGLOG['DSCHECK']:
               self.add_dscheck_dcount(0, nrec['data_size'], self.PGOPT['extlog'])
      if astrs:
         self.PGOPT['ucnt'] += 1
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

   # get the temporal info in local and remote file names and the possible values# between the break update and the current date
   # BTW, change to working directory
   def get_tempinfo(self, locrec, locinfo, eidx = 0):
      # get data end date for update action
      edate = self.params['ED'][eidx] if ('ED' in self.params and self.params['ED'][eidx]) else locrec['enddate']
      if not edate: return self.pglog(locinfo + ": MISS End Data Date for local update", self.PGOPT['emlerr'])
      ehour = self.params['EH'][eidx] if ('EH' in self.params and self.params['EH'][eidx] != None) else locrec['endhour']
      if not isinstance(edate, str): edate = str(edate)
      if ehour is None and self.pgget('drupdt', '', "lindex = {} and tinterval like '%H'".format(locrec['lindex'])):
         return self.pglog(locinfo + ": MISS End Data Hour for hourly remote update", self.PGOPT['emlerr'])
      if locrec['validint']:
         val = locrec['validint']
      elif self.PGOPT['UCNTL'] and self.PGOPT['UCNTL']['validint']:
         val = self.PGOPT['UCNTL']['validint']
      else:
         val = None
      tempinfo = {'AT': None, 'DC': None, 'ED': [], 'EH': [], 'VI': None,
                  'VD': None, 'VH': None, 'CVD': None, 'NX': None, 'FQ': None,
                  'QU': None, 'EP': 0, 'RS': -1, 'AQ': None}
      if val: val = self.get_control_time(val, "Valid Internal")
      if val:
         tempinfo['VI'] = val
         if ehour is None and val[3]: ehour = 0
      val = self.get_control_time(locrec['agetime'], "File Age Time")
      if val:
         tempinfo['AT'] = val
         if ehour is None and val[3]: ehour = 0
      frequency = self.params['FQ'][0] if 'FQ' in self.params else locrec['frequency']
      if frequency:  # get data update frequency info
         (val, unit) = self.get_control_frequency(frequency)
         if val:
            tempinfo['FQ'] = val
            tempinfo['QU'] = unit   # update frequency unit of meassure
         else:
            locinfo = self.replace_pattern(locinfo, edate, ehour)
            return self.pglog("{}: {}".format(locinfo, unit), self.PGOPT['emlerr'])
         if locrec['endperiod']: tempinfo['EP'] = locrec['endperiod']
         if val[3] and ehour is None: ehour = 0
         edate = self.enddate(edate, tempinfo['EP'], unit, tempinfo['FQ'][6])
      elif 'MU' in self.params or 'CP' in self.params:
         locinfo = self.replace_pattern(locinfo, edate, ehour)
         return self.pglog(locinfo + ": MISS frequency for Update", self.PGOPT['emlerr'])
      val = self.get_control_time(locrec['nextdue'], "Due Internval")
      if val:
         tempinfo['NX'] = val
         if ehour is None and val[3]: ehour = 0
      # check if allow missing remote file
      if 'MR' in self.params and self.params['MR'][0]:
         tempinfo['amiss'] = self.params['MR'][0]
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
               return self.pglog("{}: MISS -ST or -WT to backup {}".format(options, locinfo), self.PGOPT['emlerr'])
         else:
            return self.pglog("Set -ST or -WT in Options to backup {}".format(locinfo), self.PGOPT['emlerr'])
      if (options and re.search(r'(^|\s)-GX(\s|$)', options, re.I) and
          not re.search(r'(^|\s)-RS(\s|$)', options, re.I)):
         tempinfo['RS'] = 0   # set to 1 if need pass -RS to dsarch 
         ddate = edate
         dhour = ehour
         dcnt = 0
         self.PGOPT['wtidx'] = {}
      if options:
         ms = re.search(r'-VS\s+(\d+)', options, re.I)
         if ms: tempinfo['VS'] = int(ms.group(1))
      if tempinfo['VI']:
         if tempinfo['VI'][3]:
            (vdate, vhour) = self.adddatehour(self.PGOPT['CURDATE'], self.PGOPT['CURHOUR'], -tempinfo['VI'][0],
                                                -tempinfo['VI'][1], -tempinfo['VI'][2], -tempinfo['VI'][3])
         else:
            vdate = self.adddate(self.PGOPT['CURDATE'], -tempinfo['VI'][0], -tempinfo['VI'][1], -tempinfo['VI'][2])
            vhour = self.PGOPT['CURHOUR']
         if 'CN' in self.params and locrec['cleancmd']:
            tempinfo['CVD'] = self.adddate(self.PGOPT['CURDATE'], -tempinfo['VI'][0], -tempinfo['VI'][1], -(1+tempinfo['VI'][2]))
         tempinfo['setmiss'] = 1
         if self.diffdatehour(edate, ehour, vdate, vhour) < 0:
            vdate = edate
            vhour = ehour
         if tempinfo['amiss'] == 'N' and locrec['missdate']:
            dhour = self.diffdatehour(vdate, vhour, locrec['missdate'], locrec['misshour'])
            if dhour > 0:
               if dhour > 240:
                  record = {'missdate': None, 'misshour': None}
                  self.pgupdt("dlupdt", record, "lindex = {}".format(locrec['lindex']))
               else:
                  vdate = locrec['missdate']
                  vhour = locrec['misshour']
         if vdate and not isinstance(vdate, str): vdate = str(vdate)
         tempinfo['VD'] = vdate
         tempinfo['VH'] = vhour
         if 'ED' not in self.params and self.diffdatehour(edate, ehour, vdate, vhour) > 0:
            edate = vdate
            if tempinfo['FQ']:
               if tempinfo['EP'] or tempinfo['QU'] == 'M':
                  edate = self.enddate(edate, tempinfo['EP'], tempinfo['QU'], tempinfo['FQ'][6])
               while True:
                  (udate, uhour) = self.addfrequency(edate, ehour, tempinfo['FQ'], -1)
                  if self.diffdatehour(udate, uhour, vdate, vhour) < 0: break
                  edate = udate
                  ehour = uhour
                  if tempinfo['EP'] or tempinfo['QU'] == 'M':
                     edate = self.enddate(edate, tempinfo['EP'], tempinfo['QU'], tempinfo['FQ'][6])
      vdate = self.params['CD']
      vhour = self.params['CH']
      if tempinfo['NX']:
         if tempinfo['NX'][3]:
            (udate, uhour) = self.adddatehour(self.PGOPT['CURDATE'], vhour, -tempinfo['NX'][0],
                                                -tempinfo['NX'][1], -tempinfo['NX'][2], -tempinfo['NX'][3])
         else:
            udate = self.adddate(self.PGOPT['CURDATE'], -tempinfo['NX'][0], -tempinfo['NX'][1], -tempinfo['NX'][2])
            uhour = vhour
         if self.diffdatehour(udate, uhour, vdate, vhour) <= 0:
            vdate = udate
            vhour = uhour
      if 'CP' in self.params: (vdate, vhour) = self.addfrequency(vdate, vhour, tempinfo['FQ'], 1)
      fupdate = 1 if 'FU' in self.params else 0
      while fupdate or self.diffdatehour(edate, ehour, vdate, vhour) <= 0:
         tempinfo['ED'].append(edate)
         if ehour != None and tempinfo['QU'] != 'H':
            tempinfo['EH'].append(23)
         else:
            tempinfo['EH'].append(ehour)
         if 'MU' not in self.params: break
         if tempinfo['RS'] == 0 and dcnt < 3:
            if self.diffdatehour(edate, ehour, ddate, dhour) >= 0: dcnt += 1
         (edate, ehour) = self.addfrequency(edate, ehour, tempinfo['FQ'], 1)
         edate = self.enddate(edate, tempinfo['EP'], tempinfo['QU'], tempinfo['FQ'][6])
         fupdate = 0
      if tempinfo['RS'] == 0 and dcnt > 2: tempinfo['RS'] = 1
      if not tempinfo['ED']: # no end time found, update not due yet
         if tempinfo['NX']:
            (udate, uhour) = self.adddatehour(edate, ehour, tempinfo['NX'][0], tempinfo['NX'][1], tempinfo['NX'][2], tempinfo['NX'][3])
         else:
            udate = edate
            uhour = ehour
         locinfo = self.replace_pattern(locinfo, edate, ehour, tempinfo['FQ'])
         vdate = self.params['CD']
         val = "Update data"
         if tempinfo['NX']: val += " due"
         if uhour is None:
            locinfo += ": {} on {}".format(val, udate)
         else:
            locinfo += ": {} at {}:{:02}".format(val, udate, uhour)
            vdate += ":{:02}".format(self.params['CH'])
         return self.pglog("{} NOT due yet by {}".format(locinfo, vdate), self.PGOPT['emllog'])
      return tempinfo

   # get archived file info
   def file_archive_info(self, lfile, locrec, tempinfo):
      if tempinfo['ainfo'] != None: return tempinfo['ainfo']
      edate = tempinfo['edate']
      ehour = tempinfo['ehour']
      ainfo = {'archcnt': 0, 'archived': 0, 'present': 0, 'vindex': 0, 'types': {}, 'note': None}
      growing = self.is_growing_file(locrec['locfile'], tempinfo['FQ'])
      if growing:
         if tempinfo['NX']:
            (udate, uhour) = self.adddatehour(edate, ehour, tempinfo['NX'][0], tempinfo['NX'][1], tempinfo['NX'][2], tempinfo['NX'][3])
         else:
            udate = edate
            uhour = ehour
         if self.PGLOG['GMTZ'] and uhour != None: # convert to local times
            (udate, uhour) = self.adddatehour(udate, uhour, 0, 0, 0, -self.PGLOG['GMTZ'])
      options = locrec['options'] if locrec['options'] else ""
      act = locrec['action']
      locrec['gindex'] = self.get_group_index(options, edate, ehour, tempinfo['FQ'])
      dsid = self.params['DS']
      gcnd = "gindex = {}".format(locrec['gindex'])
      cnd = "dsid = '{}' AND {}".format(dsid, gcnd)
      mmiss = 0
      if re.match(r'^A(B|W)$', act):   # check existing web files
         ainfo['archcnt'] = 1
         ms = re.search(r'(^|\s)-WT\s+(\w)(\s|$)', options, re.I)
         type = self.get_data_type('WT', options)
         if locrec['archfile']:
            afile = self.replace_pattern(locrec['archfile'], edate, ehour, tempinfo['FQ'])
         else:
            afile = lfile if re.search(r'(^|\s)-KP(\s|$)', lfile, re.I) else op.basename(lfile)
            ms =re.search(r'(^|\s)-WP\s+(\S+)', options, re.I)
            if ms:
               path = self.replace_pattern(ms.group(2), edate, ehour, tempinfo['FQ'])
            else:
               path = self.get_group_field_path(locrec['gindex'], dsid, 'webpath')
            if path: afile = self.join_paths(path, afile)
         wrec = self.pgget_wfile(dsid, "*", "{} AND type = '{}' AND wfile = '{}'".format(gcnd, type, afile), self.PGOPT['extlog'])
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
            if not growing or self.diffdatehour(udate, uhour, adate, ahour) <= 0: ainfo['archived'] += 1
            if wrec['vindex']: ainfo['vindex'] = wrec['vindex']
            ainfo['present'] += 1
      if act == 'AS':   # check existing save files
         ainfo['archcnt'] = 1
         type = self.get_data_type('ST', options)
         if locrec['archfile']:
            afile = self.replace_pattern(locrec['archfile'], edate, ehour, tempinfo['FQ'])
         else:
            afile = lfile if re.search(r'(^|\s)-KP(\s|$)', options, re.I) else op.basename(lfile)
            ms = re.search(r'(^|\s)-SP\s+(\S+)', options, re.I)
            if ms:
               path = self.replace_pattern(ms.group(2), edate, ehour, tempinfo['FQ'])
            else:
               path = self.get_group_field_path(locrec['gindex'], self.params['DS'], 'savedpath')
            if path: afile = self.join_paths(path, afile)
         srec = self.pgget("sfile", "*", "{} AND type = '{}' AND sfile = '{}'".format(cnd, type, afile), self.PGOPT['extlog'])
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
            if not growing or self.diffdatehour(udate, uhour, adate, ahour) <= 0: ainfo['archived'] += 1
            if srec['vindex']: ainfo['vindex'] = srec['vindex']
            ainfo['present'] += 1
      if act == 'AQ':   # check existing quasar backup files
         ainfo['archcnt'] = 1
         type = self.get_data_type('QT', options)
         if locrec['archfile']:
            afile = self.replace_pattern(locrec['archfile'], edate, ehour, tempinfo['FQ'])
         else:
            return self.pglog(lfile + ": Miss Backup file name via (FA|FileArchived)", self.PGOPT['emlerr'])
         brec = self.pgget("bfile", "*", "dsid = '{}' AND type = '{}' AND bfile = '{}'".format(self.params['DS'], type, afile), self.PGOPT['extlog'])
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
            if not growing or self.diffdatehour(udate, uhour, adate, ahour) <= 0: ainfo['archived'] += 1
            ainfo['present'] += 1
      if ainfo['archcnt'] == 0:
         self.pglog("{}: unknown archive action {}".format(lfile, act), self.PGOPT['extlog'])
      return ainfo   # always returns a hash reference for archiving info

   # build up data note based on temporal info, keep the begin timestamp# for existing record; change end timestamp only if new data added
   # return None if no change for existing note
   def build_data_note(self, onote, lfile, locrec, tempinfo):
      note = locrec['note']
      if not note: return onote
      seps = self.params['PD']
      match = "[^{}]+".format(seps[1])
      edate = tempinfo['edate']
      ehour = tempinfo['ehour']
      if note[0] == '!':  # executable for build up data note
         cmd = self.executable_command(1, None, None, edate)
         if not cmd: return 0
         return self.pgsystem(cmd, self.PGOPT['emllog'], 21)
      # repalce generic patterns first
      note = self.replace_pattern(note, None)   # replace generic patterns first
      # get temporal patterns
      patterns = re.findall(r'{}({}){}'.format(seps[0], match, seps[1]), note)
      pcnt = len(patterns)
      if pcnt == 0: return note   # no pattern temporal matches
      if pcnt > 2:
         self.pglog("{}-{}: TOO many ({}) temporal patterns".format(lfile, note, pcnt), self.PGOPT['emllog'])
         return onote
      if pcnt == 2:   # replace start time
         if onote:   # get start time from existing note
            replace = r"{}{}{}".format(seps[0], patterns[0], seps[1])
            ms = re.match(r'^(.*){}(.*){}'.format(replace, self.params['PD'][0]), note)
            if ms:
               init = ms.group(1)
               sp = ms.group(2)
               ms = re.search(r'{}(.+){}'.format(init, sp), onote)
               if ms:
                  sdate = ms.group(1)
                  note = re.sub(replace, sdate, note, 1)
         elif tempinfo['FQ']: # get start time
            (sdate, shour) = self.addfrequency(edate, ehour, tempinfo['FQ'], 0)
            note = self.replace_pattern(note, sdate, shour, None, 1)
      return self.replace_pattern(note, edate, ehour)   # repalce end time now

   # get data file status info
   def file_status_info(self, lfile, rfile, tempinfo):
      # check and cache new data info
      finfo = self.check_local_file(lfile, 33, self.PGOPT['wrnlog'])   # 33 = 1 + 32
      if not finfo:
         self.PGOPT['chksm'] = ''
         self.PGOPT['fsize'] = 0
         return
      fdate = finfo['date_modified']
      ftime = finfo['time_modified']
      fhour = None
      ms = re.match(r'^(\d+):', ftime)
      if ms: four = int(ms.group(1))
      self.PGOPT['fsize'] = finfo['data_size']
      self.PGOPT['chksm'] = finfo['checksum']
      if rfile and lfile != rfile:
         finfo = self.check_local_file(rfile, 1, self.PGOPT['wrnlog'])
         if finfo and self.cmptime(finfo['date_modified'], finfo['time_modified'], fdate, ftime) < 0:
            fdate = finfo['date_modified']
            ftime = finfo['time_modified']
            ms = re.match(r'^(\d+):', ftime)
            if ms: four = int(ms.group(1))
      self.PGOPT['fdate'] = fdate
      self.PGOPT['ftime'] = ftime
      self.PGOPT['fhour'] = fhour
      if 'RE' in self.params:   # reset end data/time/hour
         if tempinfo['NX']:
            if tempinfo['NX'][3]:
               (fdate, fhour) = self.adddatehour(fdate, fhour, -tempinfo['NX'][0], -tempinfo['NX'][1],
                                                   -tempinfo['NX'][2], -tempinfo['NX'][3])
            else:
               fdate = self.adddate(fdate, -tempinfo['NX'][0], -tempinfo['NX'][1], -tempinfo['NX'][2])
         while True:
            (edate, ehour) = self.addfrequency(tempinfo['edate'], tempinfo['ehour'], tempinfo['FQ'], 1)
            edate = self.enddate(edate, tempinfo['EP'], tempinfo['QU'], tempinfo['FQ'][6])
            if self.diffdatehour(edate, ehour, fdate, fhour) > 0: break
            tempinfo['edate'] = edate
            tempinfo['ehour'] = ehour

   # check if a Server file is aged enough for download# return 1 if valid, 0 if not aged enough, -1 if cannot check
   def check_agetime(self, dcmd, sfile, atime):
      info = self.check_server_file(dcmd, 1)
      if not info:
         sact = self.get_download_action(dcmd)
         (stat, derr) = self.parse_download_error(self.PGOPT['STATUS'], sact)
         self.PGOPT['STATUS'] = derr
         self.pglog("{}: cannot check file age\n{}".format(sfile, self.PGOPT['STATUS']), self.PGOPT['emlerr'])
         return stat
      ahour = None
      if atime[3]:
         ms = re.match(r'^(\d+):', info['time_modified'])
         if ms: ahour = int(ms.group(1))
      (adate, ahour) = self.adddatehour(info['date_modified'], ahour, atime[0], atime[1], atime[2], atime[3])
      if self.diffdatehour(self.params['CD'], self.params['CH'], adate, ahour) >= 0:
         return 1
      if ahour is None:
         self.pglog(("{}: original {} file ready by {}\n".format(sfile, info['ftype'], info['date_modified']) +
                      "but NOT aged enough for retrieving yet by " + self.params['CD']), self.PGOPT['emllog'])
      else:
         self.pglog(("{}: original {} file ready by {}:{:02}\n".format(sfile, info['ftype'], info['date_modified'], ahour) +
                      "but NOT aged enough for retrieving yet by {}:{:02}".format(self.params['CD'], self.params['CH'])), self.PGOPT['emllog'])
      return 0   # otherwise server file is not aged enough

   # check if a Server file is changed with different size# return 1 - file changed, 2 - new file retrieved, 3 - force redlownload,
   #        0 - no change , -1 - error check, -2 - cannot check
   def check_newer_file(self, dcmd, cfile, ainfo):
      if cfile:
         finfo = self.check_local_file(cfile, 33, self.PGOPT['wrnlog'])
         if not finfo: return 3   # download if can not check newer
      else:
         finfo = {'isfile': 0, 'checksum': ainfo['chksm'], 'data_size': ainfo['asize'],
                  'date_modified': ainfo['adate'], 'time_modified': ainfo['atime']}
      cinfo = self.check_server_file(dcmd, 33, cfile)
      if not cinfo:
         sact = self.get_download_action(dcmd)
         (stat, derr) = self.parse_download_error(self.PGOPT['STATUS'], sact)
         self.PGOPT['STATUS'] = derr
         return stat
      stat = 2 if cinfo['ftype'] == "WGET" else 1
      if finfo['isfile'] and cfile == cinfo['fname'] and finfo['data_size'] and cinfo['data_size'] and cinfo['data_size'] != finfo['data_size']:
         return stat
      self.PGOPT['STATUS'] = ''
      if (finfo['data_size'] != cinfo['data_size'] or 'checksum' not in cinfo or
          'checksum' not in finfo or finfo['checksum'] != cinfo['checksum']):
         if 'HO' in self.params and cinfo['ftype'] == "FTP":
            (cdate, ctime) = self.addhour(cinfo['date_modified'], cinfo['time_modified'], -self.params['HO'][0])
         else:
            cdate = cinfo['date_modified']
            ctime = cinfo['time_modified']
         if self.cmptime(cdate, ctime, finfo['date_modified'], finfo['time_modified']) > 0:
            msg = "{} Newer {} {}: {} {} {}".format(self.params['DS'], cinfo['ftype'], cinfo['fname'], cdate, ctime, cinfo['data_size'])
            if 'checksum' in cinfo: msg += " " + cinfo['checksum']
            msg += "; {}: ".format(cfile if cfile else "archived")
            msg += "{} {} {}".format(finfo['date_modified'], finfo['time_modified'], finfo['data_size'])
            if 'checksum' in finfo: msg += " " + finfo['checksum']
            self.pglog(msg, self.PGOPT['wrnlog'])
            return stat
      if 'adate' in ainfo:
         self.PGOPT['STATUS'] = "archived: {} {}".format(ainfo['adate'], ainfo['atime'])
      elif cfile:
         self.PGOPT['STATUS'] += "local copy timestamp: {} {}".format(finfo['date_modified'], finfo['time_modified'])
      if 'note' in cinfo:
         self.PGOPT['STATUS'] += "\n" + cinfo['note']
      return 0

   # get download action name
   def get_download_action(self, dcmd):
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

   # change to working directory if not there yet
   def change_workdir(self, wdir, locinfo, edate, ehour, FQ):
      if 'WD' in self.params and self.params['WD'][0]: wdir = self.params['WD'][0]
      if not wdir:
         return self.pglog(locinfo + ": MISS working directory", self.PGOPT['emlerr'])
      else:
         wdir = self.replace_environments(wdir)
         wdir = self.replace_pattern(wdir, edate, ehour, FQ)
         if not self.change_local_directory(wdir, self.PGOPT['emllog']): return 0
         return 1

   # clean the working copies of remote and local files/directories
   def clean_files(self, cleancmd, edate, ehour, lfiles, rfiles, freq):
      lfile = ' '.join(lfiles) if lfiles else ''
      cleancmd = self.replace_pattern(cleancmd, edate, ehour, freq)
      cleancmd = self.executable_command(cleancmd, lfile, None, None, None, rfiles)
      self.PGLOG['ERR2STD'] = [self.PGLOG['MISSFILE']]
      self.pgsystem(cleancmd, self.PGOPT['emllog'], 5)
      self.PGLOG['ERR2STD'] = []

   # clean files rematching pattern on given date/hour
   def clean_older_files(self, cleancmd, workdir, locinfo, edate, locfile, rmtrecs, rcnt, tempinfo):
      rfiles = None
      lfiles = self.get_local_names(locfile, tempinfo, edate)
      self.change_workdir(workdir, locinfo, edate, tempinfo['ehour'], tempinfo['FQ'])
      if rcnt and cleancmd.find(' -RF') > 0:
         rfiles = self.get_all_remote_files(rmtrecs, rcnt, tempinfo, edate)
      self.clean_files(cleancmd, edate, tempinfo['ehour'], lfiles, rfiles, tempinfo['FQ'])

   # get all remote file names for one update period
   def get_all_remote_files(self, rmtrecs, rcnt, tempinfo, edate):
      rfiles = []
      for i in range(rcnt): # processs each remote record
         rmtrec = self.onerecord(rmtrecs, i)
         file = rmtrec['remotefile']
         if not file: continue
         files = self.get_remote_names(file, rmtrec, file, tempinfo, edate)
         if files: rfiles.extend(files)
      return rfiles

   # check remote file status and sed email to specialist for irregular update cases
   def check_dataset_status(self):
      if 'CD' in self.params:
         self.params['CD'] = self.format_date(self.params['CD'])   # standard format in case not yet
      else:
         self.params['CD'] = self.curdate()   # default to current date
      condition = "specialist = '{}'".format(self.params['LN'])
      if 'ED' not in self.params: condition += " AND enddate < '{}'".format(self.params['CD'])
      if 'DS' in self.params: condition += " AND dsid = '{}'".format(self.params['DS'])
      s = self.file_condition('dlupdt', ('L' if 'LI' in self.params else "FIXA"), None, 1)
      if s: condition += " AND " + s
      condition += " ORDER BY dsid, execorder, lindex"
      locrecs = self.pgmget("dlupdt", "*", condition, self.PGOPT['extlog'])
      loccnt = len(locrecs['locfile']) if locrecs else 0
      if not loccnt: return self.pglog("No Update record found for checking update status on {} for '{}'".format(self.params['CD'], self.params['LN']), self.PGOPT['wrnlog'])
      s = "s" if loccnt > 1 else ""
      self.pglog("Check {} record{} for update status...".format(loccnt, s), self.PGOPT['wrnlog'])
      for i in range(loccnt):
         locrec = self.onerecord(locrecs, i)
         if loccnt == 1 and 'LI' in self.params and 'LF' in self.params and len(self.params['LF']) == 1 and self.params['LF'][0] != locrec['locfile']:
            locrec['locfile'] = self.params['LF'][0]
         self.check_locfile_status(locrec)
      if self.PGOPT['lcnt'] or self.PGLOG['ERRMSG']:
         if self.PGOPT['lcnt']:
            loccnt = self.PGOPT['lcnt']
            s = "s" if (loccnt > 1) else ""
         self.SUBJECT = "DSUPDT Status of {} update record{}".format(loccnt, s)
         if 'DS' in self.params: self.SUBJECT += " for {}".format(self.params['DS'])
         self.TOPMSG = " ready for update of {} local file{}".format(loccnt, s)
         s = "s" if (self.PGOPT['rcnt'] > 1) else ""
         self.TOPMSG = "{}/{} remote{}{}".format(self.PGOPT['ucnt'], self.PGOPT['rcnt'], s, self.TOPMSG)
      else:
         self.pglog("No local file ready for checking {} on {} for {}".format(self.SUBJECT, self.params['CD'], self.params['LN']), self.PGOPT['wrnlog'])
         self.SUBJECT = self.TOPMSG = None
      if self.PGOPT['UCNTL']:
         self.reset_control_time()
         if self.SUBJECT: self.SUBJECT += "-C{}".format(self.PGOPT['UCNTL']['cindex'])

   # check update status for a given local file
   def check_locfile_status(self, locrec):
      loccnd = "lindex = {}".format(locrec['lindex'])
      lfile = locrec['locfile']
      locinfo = "{}-L{}".format(locrec['dsid'], locrec['lindex'])
      if not lfile: return self.pglog(locinfo + ": local file name NOT specified", self.PGOPT['emlerr'])
      locinfo += "-" + lfile
      tempinfo = self.get_tempinfo(locrec, locinfo, 0)
      if not tempinfo: return 0   # simply return if miss temporal info for update
      rmtcnd = loccnd
      rcnd = self.file_condition('drupdt', ('D' if 'DO' in self.params else "RS"), None, 1)
      if rcnd: rmtcnd += " AND " + rcnd
      rmtrecs = self.pgmget("drupdt", "*", rmtcnd + " ORDER BY dindex, remotefile", self.PGOPT['extlog'])
      rcnt = len(rmtrecs['remotefile']) if rmtrecs else 0
      if rcnt == 0:
         if rcnd and self.pgget("drupdt", "", loccnd):
            return self.pglog("{}: NO remote file record matched for {}".format(locinfo, rcnd), self.PGOPT['emlerr'])
         rcnt = 1   # create a empty record remote file
         rmtrecs = {'lindex': locrec['lindex'], 'remotefile': None, 'serverfile': None}
      if rcnt == 1:
         if 'RF' in self.params and len(self.params['RF']) == 1 and not (rmtrecs['remotefile'][0] and self.params['RF'][0] == rmtrecs['remotefile'][0]):
            rmtrecs['remotefile'][0] = self.params['RF'][0]
         if 'SF' in self.params and len(self.params['SF']) == 1 and not (rmtrecs['serverfile'][0] and self.params['SF'][0] == rmtrecs['serverfile'][0]):
            rmtrecs['serverfile'][0] = self.params['SF'][0]
      ecnt = len(tempinfo['ED'])
      self.PGOPT['lindex'] = locrec['lindex']
      logact = self.PGOPT['emllog']
      retcnt = 0
      for i in range(ecnt):
         if self.ALLCNT > 1 and i > 0:
            tempinfo = self.get_tempinfo(locrec, locinfo, i)
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
         if 'GZ' in self.params: tempinfo['einfo'] += "(UTC)"
         lfile = self.replace_pattern(locrec['locfile'], edate, ehour, tempinfo['FQ'])
         locinfo = "{}-L{}-{}".format(locrec['dsid'], locrec['lindex'], lfile)
         self.pglog("{}: Check Update Status for {}".format(locinfo, tempinfo['einfo']), logact)
         logact = self.PGOPT['emlsep']
         self.PGOPT['lcnt'] += 1
         j = 0
         while j < rcnt:   # check each remote record, stop checking if error
            pgrec = self.onerecord(rmtrecs, j)
            if not self.check_remote_status(pgrec, lfile, locrec, locinfo, tempinfo) and 'CA' not in self.params:
               break
            j += 1
         if j == 0: break
      self.PGOPT['lindex'] = 0
      return (1 if retcnt > 0 else 0)

   # check update status for given remote file
   def check_remote_status(self, rmtrec, lfile, locrec, locinfo, tempinfo):
      rfile = rmtrec['remotefile']
      rmtinfo = locinfo
      if not rfile:
         rfile = lfile
         rcnt = 1
      if rfile != locrec['locfile']: rmtinfo += "-" + rfile
      tempinfo['DC'] = (self.params['DC'][0] if ('DC' in self.params and self.params['DC'][0]) else
                        (rmtrec['download'] if rmtrec['download'] else locrec['download']))
      rfiles = self.get_remote_names(rfile, rmtrec, rmtinfo, tempinfo)
      rcnt = len(rfiles) if rfiles else 0
      if not rcnt: return self.pglog(rmtinfo + ": NO remote file name identified", self.PGOPT['emlerr'])
      self.PGOPT['rcnt'] += rcnt   # accumulate remote file counts
      if tempinfo['DC']:
         self.PGOPT['PCNT'] = self.count_pattern_path(tempinfo['DC'])
         tempinfo['DC'] = None
      sfile = rmtrec['serverfile']
      if sfile and sfile != rfile:
         sfiles = self.get_remote_names(sfile, rmtrec, rmtinfo, tempinfo)
         scnt = len(sfiles) if sfiles else 0
         if scnt != rcnt:
            self.PGOPT['rstat'] = -2
            return self.pglog("{}/{}: {}/{} MISS match file counts".format(rmtinfo, sfile, rcnt, scnt), self.PGOPT['emlerr'])
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
            return self.pglog(rmtinfo + ": Missing download command", self.PGOPT['emlerr'])
         elif not sfile['ready']:
            self.pglog(rmtinfo + ": NOT Ready yet for update", self.PGOPT['emllog'])
            break
         dcnt += 1
      return 1 if dcnt else 0

   # process the update control records
   def process_update_controls(self):
      ctime = self.curtime(1)
      if not ('CI' in self.params or 'DS' in self.params):
         self.set_default_value("SN", self.params['LN'])
      condition = ("(pid = 0 OR lockhost = '{}') AND cntltime <= '{}'".format(self.PGLOG['HOSTNAME'], ctime) +
                   self.self.get_hash_condition('dcupdt') + " ORDER BY hostname DESC, cntltime")
      pgrecs = self.pgmget("dcupdt", "*", condition, self.PGOPT['extlog'])
      self.ALLCNT = len(pgrecs['cindex']) if pgrecs else 0
      if self.ALLCNT == 0:
         return self.pglog("No update control record idetified due for process", self.LOGWRN)
      s = 's' if self.ALLCNT > 1 else ''
      self.pglog("Process {} update control record{} ...".format(self.ALLCNT, s), self.WARNLG)
      pcnt = 0
      for i in range(self.ALLCNT):
         pcnt += self.process_one_control(self.onerecord(pgrecs, i))
         if pcnt > 1 and not ('CI' in self.params or 'DS' in self.params): break
      rmsg = "{} of {} update control{} reprocessed by {}".format(pcnt, self.ALLCNT, s, self.PGLOG['CURUID'])
      if self.PGLOG['CURUID'] != self.params['LN']: rmsg += " for " + self.params['LN']
      self.pglog(rmsg, self.PGOPT['wrnlog'])

   # process one update control
   def process_one_control(self, pgrec):
      cidx = pgrec['cindex']
      cstr = "Control Index {}".format(cidx)
      if not pgrec['action']: return self.pglog(cstr + ": Miss update action", self.PGOPT['errlog'])
      if not (self.OPTS[pgrec['action']][0]&self.PGOPT['CNTLACTS']):
         return self.pglog("{}: Invalid dsupdt action '{}'".format(cstr, pgrec['action']), self.PGOPT['errlog'])
      if not pgrec['frequency']: return self.pglog(cstr + ": Miss update Frequency", self.PGOPT['errlog'])
      if pgrec['pid'] > 0 and self.check_process(pgrec['pid']):
         if 'CI' in self.params: self.pglog("{}: Under processing {}/{}".format(cstr, pgrec['pid'], self.PGLOG['HOSTNAME']), self.PGOPT['wrnlog'])
         return 0
      if pgrec['specialist'] != self.params['LN']:
         return self.pglog("{}: must be specialist '{}' to process".format(cstr, pgrec['specialist']), self.PGOPT['errlog'])
      if not ('ED' in self.params or self.valid_data_time(pgrec, cstr, self.PGOPT['wrnlog'])):
         return 0
      cmd = "dsupdt "
      if pgrec['dsid']: cmd += pgrec['dsid'] + ' '
      cmd += "{} -CI {} ".format(pgrec['action'], cidx)
      if self.PGLOG['CURUID'] != self.params['LN']: cmd += "-LN " + self.params['LN']
      cmd += "-d -b"
      # make sure it is not locked
      if self.lock_update_control(cidx, 0, self.PGOPT['errlog']) <= 0: return 0
      self.pglog("{}-{}{}: {}".format(self.PGLOG['HOSTNAME'], pgrec['specialist'], self.current_datetime(), cmd), self.LOGWRN|self.FRCLOG)
      os.system(cmd + " &")
      return 1

   # move the previous archived version controlled files
   def move_archived_file(self, ainfo, archived):
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
               if not self.pgget("sfile", "", "dsid = '{}' AND sfile = '{}'".format(self.params['DS'], tofile), self.PGOPT['extlog']):
                  break
               i += 1
            stat = self.pgsystem("dsarch {} MV -WF {} -WT {} -SF {} -ST V -KM -TS".format(self.params['DS'], fromfile, type, tofile), self.PGOPT['emerol'], 5)
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
               if not self.pgget("sfile", "", "dsid = '{}' AND sfile = '{}'".format(self.params['DS'], tofile), self.PGOPT['extlog']):
                  break
               i += 1
            stat = self.pgsystem("dsarch {} MV -RF {} -OT {} -SF {} -ST V".format(self.params['DS'], fromfile, type, tofile), self.PGOPT['emerol'], 5)
      if stat:
         self.PGOPT['vcnt'] += 1
         if 'NE' in self.params or 'EE' in self.params:
            if 'NE' in self.params: del self.params['NE']
            if 'EE' in self.params: del self.params['EE']
            self.params['SE'] = 1   # email summary at least
            self.PGOPT['emllog'] |= self.EMEROL
         self.pglog("{}-{}-{}: Found newer version-conrolled {} file; move to{} type V {}".format(self.params['DS'], type, fromfile, ftype, ttype, tofile), self.PGOPT['emlsum'])
         archived = 0
      return archived

# main function to excecute this script
def main():
   object = DsUpdt()
   object.read_parameters()
   object.start_actions()
   object.pgexit(0)

# call main() to start program
if __name__ == "__main__": main()
