#
###############################################################################
#
#     Title: pg_updt.py
#    Author: Zaihua Ji,  zji@ucar.edu
#      Date: 09/23/2020
#             2025-02-07 transferred to package rda_python_dsupdt from
#             https://github.com/NCAR/rda-shared-libraries.git
#             2025-12-08 transfer to class PgUpdt
#   Purpose: python library module to help rountinely updates of new data 
#             for one or multiple datasets
#
#    Github: https://github.com/NCAR/rda-python-dsupdt.git
#
###############################################################################
#
import os
import re
import time
from os import path as op
from rda_python_common.pg_cmd import PgCMD
from rda_python_common.pg_opt import PgOPT

class PgUpdt(PgOPT, PgCMD):

   def __init__(self):
      super().__init__()  # initialize parent class
      self.CORDERS = {}
      self.OPTS.update({
         'DR': [0x00010, 'DownloadRemote',2],
         'BL': [0x00020, 'BuildLocal',    2],
         'PB': [0x00030, 'ProcessBoth',   2], # DR & BL
         'AF': [0x00040, 'ArchiveFile',   2],
         'CF': [0x00080, 'CleanFile',     2],
         'UF': [0x000F0, 'UpdateFile',    2], # DR & BL & AF & CF
         'CU': [0x00200, 'CheckUpdate',   0],
         'GC': [0x00400, 'GetControl',    0],
         'GL': [0x00800, 'GetLocalFile',  0],
         'GR': [0x01000, 'GetRemoteFile', 0],
         'GA': [0x01C00, 'GetALL',        0], # GC & GL & GR
         'SC': [0x02000, 'SetControl',    1],
         'SL': [0x04000, 'SetLocalFile',  1],
         'SR': [0x08000, 'SetRemoteFile', 1],
         'SA': [0x0E000, 'SetALL',        4], # SC & SL & SR
         'DL': [0x20000, 'Delete',        1],
         'UL': [0x40000, 'UnLock',        1],
         'AW': [0, 'AnyWhere'],
         'BG': [0, 'BackGround'],
         'CA': [0, 'CheckAll'],
         'CN': [0, 'CheckNew'],
         'CP': [0, 'CurrrentPeriod'],
         'EE': [0, 'ErrorEmail'],   # send email when error happens only
         'FO': [0, 'FormatOutput'],
         'FU': [0, 'FutureUpdate'],
         'GZ': [0, 'GMTZone'],
         'HU': [0, 'HourlyUpdate'],
         'IE': [0, 'IgnoreError'],
         'KR': [0, 'KeepRemote'],
         'KS': [0, 'KeepServer'],
         'LO': [0, 'LogOn'],
         'MD': [0, 'PgDataset'],
         'MO': [0, 'MissedOnly'],
         'MU': [0, 'MultipleUpdate'],
         'NC': [0, 'NewControl'],
         'NE': [0, 'NoEmail'],
         'NL': [0, 'NewLocfile'],
         'NY': [0, 'NoLeapYear'],
         'QE': [0, 'QuitError'],
         'RA': [0, 'RetryArchive'],
         'RD': [0, 'RetryDownload'],
         'RE': [0, 'ResetEndTime'],
         'RO': [0, 'ResetOrder'],
         'SE': [0, 'SummaryEmail'],   # send summary email only
         'UB': [0, 'UseBeginTime'],
         'UT': [0, 'UpdateTime'],
         'AO': [1, 'ActOption',     1],  # default to <!>
         'CD': [1, 'CurrentDate', 256],  # used this instead of curdate()
         'CH': [1, 'CurrentHour',  16],  # used this instead of (localtime)[2]
         'DS': [1, 'Dataset',       0],
         'DV': [1, 'Divider',       1],  # default to <:>
         'ES': [1, 'EqualSign',     1],  # default to <=>
         'FN': [1, 'FieldNames',    0],
         'LN': [1, 'LoginName',     1],
         'OF': [1, 'OutputFile',    0],
         'ON': [1, 'OrderNames',    0],
         'PL': [1, 'ProcessLimit', 17],
         'VS': [1, 'ValidSize',    17],  # default to self.PGLOG['MINSIZE']
         'AN': [2, 'ActionName',      1],
         'AT': [2, 'AgeTime',         1],
         'BC': [2, 'BuildCommand',    1],
         'BP': [2, 'BatchProcess',    0, ''],
         'BT': [2, 'BeginTime',       1],
         'CC': [2, 'CarbonCopy',      0],
         'CI': [2, 'ControlIndex',   16],
         'CL': [2, 'CleanCommand',    1],
         'CO': [2, "ControlOffset",   1],
         'CT': [2, 'ControlTime',     32+356],
         'DB': [2, 'Debug',           0],
         'DC': [2, 'DownloadCommand', 1],
         'DE': [2, 'Description',    64],
         'DO': [2, 'DownloadOrder',  16],
         'DT': [2, 'DataTime',       1+32+256],
         'EC': [2, 'ErrorControl',    1, "NIQ"],
         'ED': [2, 'EndDate',       257],
         'EH': [2, 'EndHour',        33],
         'EP': [2, 'EndPeriod',       1],
         'ET': [2, 'EndTime',        33],
         'FA': [2, 'FileArchived',    0],
         'FQ': [2, 'Frequency',       1],
         'GP': [2, 'GenericPattern',  0],
         'HN': [2, "HostName",        1],
         'HO': [2, 'HourOffset',     17],
         'ID': [2, 'ControlID',       0],
         'IF': [2, 'InputFile',       0],
         'KF': [2, 'KeepFile',        1, "NRSB"],
         'LF': [2, 'LocalFile',       0],
         'LI': [2, 'LocalIndex',     17],
         'MC': [2, 'EMailControl',    1, "ASNEB"],
         'MR': [2, 'MissRemote',    128, "NY"],
         'DI': [2, 'DueInterval',     1],
         'OP': [2, 'Options',         1],
         'PD': [2, 'PatternDelimiter', 2], # pattern delimiters, default to ["<", ">"]
         'PI': [2, 'ParentIndex',    17],
         'PR': [2, 'ProcessRemote',   1],
         'QS': [2, 'QSubOptions',     0],
         'RF': [2, 'RemoteFile',      0],
         'RI': [2, 'RetryInterval',   1],
         'SF': [2, 'ServerFile',      0],
         'SN': [2, 'Specialist',      1],
         'TI': [2, 'TimeInterval',    1],
         'UC': [2, 'UpdateControl',   1],
         'VI': [2, 'ValidInterval',   1],
         'WD': [2, 'WorkDir',         1],
         'XC': [2, 'ExecuteCommand',  1],
         'XO': [2, 'ExecOrder',      16],
      })
      self.ALIAS.update({
         'AN': ['Action', "AC"],
         'AT': ['FileAge', "FileAgeTime"],
         'BC': ['BuildCmd'],
         'BG': ['b'],
         'BL': ['BuildLocalfile'],
         'BP': ['d', 'DelayedMode'],
         'BT': ['IT', 'InitialTime'],
         'CI': ['UpdateControlIndex'],
         'CL': ['CleanFile'],
         'CN': ['CheckNewFile'],
         'DC': ['Command', 'Download'],
         'DE': ['Desc', 'Note', 'FileDesc', 'FileDescription'],
         'DI': ['NextDue'],
         'DL': ['RM', 'Remove'],
         'DR': ['DownloadRemoteFile'],
         'DS': ['Dsid', 'DatasetID'],
         'DV': ['Delimiter', 'Separator'],
         'ED': ['UpdateEndDate'],
         'EH': ['UpdateEndHour'],
         'EP': ['EndPeriodDay'],
         'FA': ['SF', 'WF', 'QF'],
         'FQ': ['UpdateFrequency'],
         'FU': ["ForceUpdate"],
         'GC': ['GetUpdateControl'],
         'GL': ['GetLocal'],
         'GN': ['GroupID'],
         'GP': ['GeneralPattern'],
         'GR': ['GetRemote'],
         'GZ': ['GMT', 'GreenwichZone', 'UTC'],
         'HN': ['HostMachine'],
         'KR': ['KeepRemoteFile'],
         'KS': ['KeepServerFile'],
         'LF': ['LocalFileIndex'],
         'LI': ['LocIndex', "UpdateIndex"],
         'LO': ['LoggingOn'],
         'OP': ['DsarchOption'],
         'NC': ['NewUpdateControl'],
         'NL': ['NewLocalFile'],
         'PD': ['TD', 'TemporalDelimiter'],
         'QE': ['QuitOnError'],
         'QS': ['PBSOptions'],
         'RD': ['Redownlaod'],
         'RO': ['Reorder'],
         'SC': ['SetUpdateControl'],
         'SL': ['SetLocal'],
         'SN': ['SpecialistName'],
         'SR': ['SetRemote'],
         'TI': ['Interval'],
         'UL': ["UnLockUpdate"],
         'XC': ['ExecCmd'],
         'XO': ['ExecuteOrder']
      })
      # single letter short names for option 'FN' (Field Names) to retrieve info
      # from RDADB; only the fields can be manipulated by this application are listed
      #  SHORTNM KEYS(self.OPTS) DBFIELD
      self.TBLHASH['dlupdt'] = {      # condition flag, 0-int, 1-string, -1-exclude
         'L': ['LI', "lindex",        0],
         'F': ['LF', "locfile",       1],
         'A': ['AN', "action",        1],     # dsarch action
         'I': ['CI', "cindex",        0],
         'U': ['FA', "archfile",      1],
         'X': ['XO', "execorder",     1],
         'S': ['SN', "specialist",    1],
         'M': ['MR', "missremote",    1],
         'W': ['WD', "workdir",       1],
         'O': ['OP', "options",       1],
         'C': ['DC', "download",      1],
         'Q': ['FQ', "frequency",     1],
         'E': ['EP', "endperiod",     0],
         'J': ['ED', "enddate",       1],
         'K': ['EH', "endhour",       0],
         'N': ['DI', "nextdue",       1],
         'V': ['VI', "validint",      1],
         'T': ['AT', "agetime",       1],
         'R': ['PR', "processremote", 1],
         'B': ['BC', "buildcmd",      1],
         'Z': ['CL', "cleancmd",      1],
         'D': ['DE', "note",          1],
      }
      self.TBLHASH['drupdt'] = {
         'L': ['LI', "lindex",      0],   # same as dlupdt.lindex
         'F': ['RF', "remotefile",  1],
         'D': ['DO', "dindex",      0],
         'S': ['SF', "serverfile",  1],
         'C': ['DC', "download",    1],
         'B': ['BT', "begintime",   1],
         'E': ['ET', "endtime",     1],
         'T': ['TI', "tinterval",   1],
      }
      self.TBLHASH['dcupdt'] = {
         'C': ['CI', "cindex",     0],
         'L': ['ID', "cntlid",     1],
         'N': ['SN', "specialist", 1],
         'P': ['PI', "pindex",     0],   # if not 0, refer to another dcupdt.cindex
         'A': ['AN', "action",     1],   # dsupdt action
         'F': ['FQ', "frequency",  1],
         'O': ['CO', "cntloffset", 1],
         'T': ['CT', "cntltime",   1],
         'R': ['RI', "retryint",   1],
         'V': ['VI', "validint",   1],
         'U': ['UC', "updtcntl",   1],
         'J': ['MC', "emailcntl",  1],
         'E': ['EC', "errorcntl",  1],
         'K': ['KF', "keepfile",   1],
         'Z': ['HO', "houroffset", 1],
         'D': ['DT', "datatime",   1],
         'H': ['HN', "hostname",   1],
         'Q': ['QS', "qoptions",   1],
         'Y': ['CC', "emails",     1],
         'X': ['XC', "execcmd",    1],
      }
      # global info to be used by the whole application
      self.PGOPT['updated'] = 0
      self.PGOPT['AUTODS'] = 0
      self.PGOPT['CNTLACTS'] = self.OPTS['UF'][0]|self.OPTS['CU'][0]
      self.PGOPT['UPDTACTS'] = "AF|BL|CF|CU|DR|PB|UF"
      self.PGOPT['ARCHACTS'] = "AW|AS|AQ"
      self.PGOPT['DTIMES'] = {}
      self.PGOPT['UCNTL'] = {}
      #default fields for getting info
      self.PGOPT['dlupdt'] = "LFAXIUCOQJNVWRZ"
      self.PGOPT['drupdt'] = "LFDSCBET"
      self.PGOPT['dcupdt'] = "CLNPAFOTRVUJEKZ"
      #all fields for getting info
      self.PGOPT['dlall'] = "LFAXIUCOQEJKNVTWMRBZSD"
      self.PGOPT['drall'] = self.PGOPT['drupdt']
      self.PGOPT['dcall'] = "CLNPAFOTRVUJEKZDHSQYX"
      # remote file download status
      # 0 error download, but continue for further download
      # 1 successful full/partial download, continue for build local files
      # < 0 error download, stop
      self.PGOPT['rstat'] = 1   # default to successful download
      # counts
      self.PGOPT['PCNT'] = 1
      self.PGOPT['vcnt'] = self.PGOPT['rcnt'] = self.PGOPT['dcnt'] = self.PGOPT['lcnt'] = 0
      self.PGOPT['bcnt'] = self.PGOPT['acnt'] = self.PGOPT['mcnt'] = 0
      self.PGOPT['ucnt'] = self.PGOPT['upcnt'] = self.PGOPT['ubcnt'] = self.PGOPT['uhcnt'] = 0
      self.PGOPT['uscnt'] = self.PGOPT['qbcnt'] = self.PGOPT['qdcnt'] = 0
      self.PGOPT['uwcnt'] = self.PGOPT['udcnt'] = self.PGOPT['uncnt'] = self.PGOPT['rdcnt'] = 0
      self.PGOPT['lindex'] = 0   # the current lindex is under updating
      self.WSLOWS = {
         'nomads.ncep.noaa.gov': 8
      }
       # set default parameters
      self.params['PD'] = ["<" , ">"]   # temporal pattern delimiters
      self.params['PL'] = 1   # max number of child processes allowed

   # get file contion
   def file_condition(self, tname, include = None, exclude = None, nodsid = 0):
      condition = ""
      hash = self.TBLHASH[tname]
      noand = 1 if nodsid else 0
      if not hash: self.pglog(tname + ": not defined in self.TBLHASH", self.PGOPT['extlog'])
      for key in hash:
         if include and include.find(key) < 0: continue
         if exclude and exclude.find(key) > -1: continue
         type = hash[key][2]
         if type < 0: continue   # exclude
         opt = hash[key][0]
         if opt not in self.params: continue
         fld = hash[key][1]
         condition += self.get_field_condition(fld, self.params[opt], type, noand)
         noand = 0
      if not nodsid:
         condition =  "dsid = '{}'{}".format(self.params['DS'], condition)
      return condition

   # check if enough information entered on command line and/or input file
   # for given action(s)
   def check_enough_options(self, cact, acts):
      errmsg = [
         "Miss dataset number per -DS(-Dataset)",
         "Miss local file names per -LF(-LocalFile)",
         "Miss remote file names per -RF(-RemoteFile)",
         "Miss local Index per -LI(-LocalIndex)",
         "Miss Control Index per -CI(-ControlIndex)",
         "Process one Update Control Index at a time",
      ]
      erridx = -1
      lcnt = ccnt = 0
      if 'LI' in self.params: lcnt = self.validate_lindices(cact)
      if 'CI' in self.params or 'ID' in self.params: ccnt = self.validate_cindices(cact)
      if self.OPTS[cact][2] == 1:
         if acts&self.OPTS['SC'][0]:
            if 'CI' not in self.params: erridx = 4
         elif cact == 'DL' or cact == 'UL':
            if not ('LI' in self.params or 'CI' in self.params): erridx = 3
         elif 'LI' not in self.params:
            erridx = 3
         elif acts&self.OPTS['SR'][0] and 'RF' not in self.params:
            erridx = 2
         if erridx < 0:
            if (lcnt + ccnt) > 0:
               if 'DS' not in self.params:
                  erridx = 0
               elif lcnt > 0 and cact == 'SL' and 'LF' not in self.params:
                  erridx = 1
      elif self.OPTS[cact][2] == 2:
         if 'CI' in self.params and len(self.params['CI']) > 1:
            erridx = 5
      if erridx >= 0: self.action_error(errmsg[erridx], cact)
      self.set_uid("dsupdt")   # set uid before any action
      if 'VS' in self.params:   # minimal size for a file to be valid for archive
         self.PGLOG['MINSIZE'] = int(self.params['VS'])
      if 'BP' in self.params:
         if 'PL' in self.params: self.params['PL'] = 1
         if 'CI' in self.params:
            oidx = self.params['CI'][0]
            otype = 'C'
         elif 'LI' in self.params:
            oidx = self.params['LI'][0]
            otype = 'L'
         else:
            oidx = 0
            otype = ''
         # set command line Batch options
         self.set_batch_options(self.params, 2, 1)
         self.init_dscheck(oidx, otype, "dsupdt", self.get_dsupdt_dataset(),
                            cact, "" if 'AW' in self.params else self.PGLOG['CURDIR'], self.params['LN'],
                            self.params['BP'], self.PGOPT['extlog'])
      if 'NY' in self.params: self.PGLOG['NOLEAP'] = 1
      if 'NE' in self.params:
         self.PGLOG['LOGMASK'] &= ~self.EMLALL   # turn off all email acts
      else:
         if 'SE' in self.params: self.PGOPT['emllog'] |= self.EMEROL
         if 'CC' in self.params and (self.PGOPT['ACTS']&self.OPTS['SC'][2]) == 2: self.add_carbon_copy(self.params['CC'])
      if self.PGOPT['ACTS']&self.OPTS['UF'][0]:
         plimit = self.params['PL'] if 'PL' in self.params else 1
         logon = self.params['LO'] if 'LO' in self.params else 1
         self.start_none_daemon('dsupdt', self.PGOPT['CACT'], self.params['LN'], plimit, 120, logon)
      else:
         self.start_none_daemon('dsupdt', self.PGOPT['CACT'], self.params['LN'], 1, 120, 1)
      if self.PGSIG['MPROC'] > 1:
         self.PGOPT['emllog'] |= self.FRCLOG
         self.PGOPT['wrnlog'] |= self.FRCLOG

   # get the associated dataset id
   def get_dsupdt_dataset(self):
      if 'DS' in self.params: return self.params['DS']
      if 'CI' in self.params and self.params['CI'][0]:
         pgrec = self.pgget("dcupdt", "dsid", "cindex = {}".format(self.params['CI'][0]), self.PGOPT['extlog'])
         if pgrec: return pgrec['dsid']
      if 'LI' in self.params and self.params['LI'][0]:
         pgrec = self.pgget("dlupdt", "dsid", "lindex = {}".format(self.params['LI'][0]), self.PGOPT['extlog'])
         if pgrec: return pgrec['dsid']
      return None

   # replace the temoral patterns in given fname with date/hour
   # return pattern array only if not date
   def replace_pattern(self, fname, date, hour = None, intv = None, limit = 0, bdate = None, bhour = None):
      if not fname: return None
      if date and not isinstance(date, str): date = str(date)
      if bdate and not isinstance(bdate, str): bdate = str(bdate)
      seps = self.params['PD']
      match = r"[^{}]+".format(seps[1])
      patterns = re.findall(r'{}([^{}]+){}'.format(seps[0], seps[1], seps[1]), fname)
      pcnt = len(patterns)
      if pcnt == 0: return fname   # return original name if no pattern
      if limit and pcnt > limit: pcnt = limit
      mps = {'b': r'^B(.+)B$', 'c': r'^C(.+)C$', 'd': r'(\d+)$', 'm': r'^M([NC])M$',
             'n': r'^N(H+|D+)N$', 'p': r'^P(\d+)$', 's': r'^S[\d:]+S$', 'w': r'^W(.+)W$'}
      for i in range(pcnt):
         pattern = patterns[i]
         replace = "{}{}{}".format(seps[0], pattern, seps[1])
         d = None
         domatch = 1
         ms = re.match(mps['p'], pattern, re.I)
         if ms:    # generic pattern matches
            pidx = int(ms.group(1))
            pattern = self.params['GP'][pidx] if 'GP' in self.params else None
            if not pattern: self.pglog("{}: MISS value per option -GP for matching general pattern '{}'".format(fname, replace), self.PGOPT['extlog'])
            domatch = 1
         if domatch:
            ms = re.match(mps['c'], pattern, re.I)  # current date
            if ms:
               pattern = ms.group(1)
               d = self.params['CD']
               h = self.params['CH']
               domatch = 0
         if domatch and (not date or re.match(mps['s'], pattern, re.I)): continue
         if domatch:
            ms = re.match(mps['m'], pattern, re.I)
            if ms:
               pattern = ms.group(1)
               if intv and len(intv) == 7 and intv[6] and re.search(mps['d'], date):
                  ms = re.search(mps['d'], date)
                  d = ms.group(1)
                  d = (intv[6] - 1) if d >= 28 else int(d*intv/30)
                  if pattern == "C":
                     pattern = chr(65 + d)   # upper case, chr(65) is A
                  elif pattern == "c":
                     pattern = chr(97 + d)   # lower case, chr(97) is a
                  else:
                     pattern = d + 1   # numeric, start from 1
                  d = None
                  domatch = 0
               else:
                  self.pglog("{}: MISS month fraction for '{}'".format(fname, replace), self.PGOPT['emllog'])
         if domatch:
            ms = re.match(mps['n'], pattern, re.I)
            if ms:
               pattern = ms.group(1)
               if not bdate: (bdate, bhour) = self.addfrequency(date, hour, intv, 0)
               plen = len(pattern)
               if re.match(r'^D', pattern):
                  diff = self.diffdate(date, bdate)
               else:
                  diff = self.diffdatehour(date, hour, bdate, bhour)
               pattern = "{:0{}}".format(diff, plen)
               domatch = 0
         if domatch:
            ms = re.match(mps['b'], pattern, re.I)
            if ms:
               pattern = ms.group(1)
               d = date
            elif 'UB' in self.params:
               d = date
            if d and intv:    # beginning time of update period
               if bdate:
                  d = bdate
                  h = bhour
               else:
                  (d, h) = self.addfrequency(d, hour, intv, 0)
            else:
               ms = re.match(mps['w'], pattern, re.I)
               if ms:   # back to the nearest Wed
                  pattern = ms.group(1)
                  wd = self.get_weekday(date)
                  if wd < 3:
                     wd += 4
                  else:
                     wd -= 3
                  d = self.adddate(date, 0, 0, -wd) if (wd > 0) else date
               else:
                  d = date
               h = hour
         if d: pattern = self.format_datehour(d, h, pattern)
         fname = re.sub(replace, pattern, fname, 1)
      return fname

   # get next display order of an archived data file of given dataset (and group)
   def get_next_exec_order(self, dsid, next):
      if not dsid:
         self.CORDERS = {}   # reinitial lize cached display orders
         return
      if dsid not in self.CORDERS:
         if next:
            pgrec = self.pgget("dlupdt", "max(execorder) max_order", "dsid = '{}'".format(dsid), self.PGOPT['extlog'])
            self.CORDERS[dsid] = pgrec['max_order'] if pgrec else 0
      self.CORDERS[dsid] += 1
      return self.CORDERS[dsid]

   # execute specialist specified command
   def executable_command(self, cmd, file, dsid, edate, ehour, rfiles = None):
      if not cmd or re.match(r'^#', cmd): return None
      if re.search(r'\$', cmd): cmd = self.replace_environments(cmd, None, self.PGOPT['emlerr'])
      if file:
         ms = re.search(r'__(FN|FNAME|FILENAME)__', cmd)
         if ms:
            cmd = re.sub(r'__{}__'.format(ms.group(1)), file, cmd)
         elif re.search(r'(-LF|-RF|-SF)', cmd):
            ms = re.search(r'(-LF|-RF|-SF)', cmd)
            cmd = re.sub(ms.group(1), file, cmd)
         elif re.search(r'/$', cmd):
            cmd += file
            if re.search(r'(^|\s|\||\S/)msrcp\s', cmd):
               cmd += " file"
            elif re.search(r'(^|\s|\||\S/)(cp|mv)\s', cmd):
               cmd += " ."
         elif cmd.find(file) < 0 and re.search(r'(^|\s|\||\S/)(rm\s|tar\s.+\.tar$)', cmd):
            cmd += " file"
      if re.search(r'-RF', cmd):
         names = []
         if rfiles:
            for rfile in rfiles:
               if isinstance(rfile, dict):
                  names.append(rfile['fname'])
               else:
                  names.append(rfile)
         name = ' '.join(names)
         cmd = re.sub(r'-RF', name, cmd, 1)
      if re.search(r'-DS', cmd):
         name = dsid if dsid else ""
         cmd = re.sub(r'-DS', name, cmd, 1)
      if edate and re.search(r'-ED', cmd):
         name = str(edate) if edate else ""
         cmd = re.sub('-ED', name, cmd, 1)
      if re.search(r'-EH', cmd):
         name = str(ehour) if ehour != None else ''
         cmd = re.sub(r'-EH', name, cmd, 1)
      ms = re.search(r'(-SN|-LN)', cmd)
      if ms:
         cmd = re.sub(ms.group(1), self.params['LN'], cmd, 1)
      if re.search(r'-LI', cmd):
         name = str(self.PGOPT['lindex']) if self.PGOPT['lindex'] else ''
         cmd = re.sub(r'-LI', name, cmd, 1)
      return cmd

   # get the local file names
   def get_local_names(self, lfile, tempinfo, edate = None):
      locfiles = []
      ehour = tempinfo['ehour']
      if not edate: edate = tempinfo['edate']
      if lfile[0] == '!':   # executable for build up local file names
         cmd = self.executable_command(lfile[1:], None, self.params['DS'], edate, ehour)
         if not cmd: return 0
         buf = self.pgsystem(cmd, self.PGOPT['wrnlog'], 21)
         if not buf: return self.pglog(lfile + ": NO local filename returned", self.PGOPT['emlerr'])
         locfiles = re.split('::', buf)
      else:
         lfiles = self.expand_serial_pattern(lfile)
         lcnt = len(lfiles)
         for i in range(lcnt):
            locfiles.append(self.replace_pattern(lfiles[i], edate, ehour, tempinfo['FQ']))
      return locfiles if locfiles else None

   # expend serial pattern
   def expand_serial_pattern(self, fname):
      if not fname: return None
      seps = self.params['PD']
      ms = re.search(r'{}S(\d[\d:]+\d)S{}'.format(seps[0], seps[1]), fname)
      if not ms: return [fname]
      rep = "{}S{}S{}".format(seps[0], ms.group(1), seps[1])
      mcs = re.split(':', ms.group(1))
      tlen = len(mcs[0])
      idx = [0]*3
      idx[0] = int(mcs[0])
      idx[1] = int(mcs[1])
      idx[2] = int(mcs[2]) if len(mcs) > 2 else 1
      fns = []
      i = idx[0]
      while i <= idx[1]:
         val = "{:0{}}".format(i, tlen)
         fn = re.sub(rep, val, fname, 1)
         fns.append(fn)
         i += idx[2]
      return fns

   # get the remote file names
   def get_remote_names(self, rfile, rmtrec, rmtinfo, tempinfo, edate = None):
      rmtfiles = []
      if not edate: edate = tempinfo['edate']
      if rfile[0] == '!':   # executable for build up remote file names
         cmd = self.executable_command(rfile[1:], None, self.params['DS'], edate, tempinfo['ehour'])
         if not cmd: return None
         rfile = self.pgsystem(cmd, self.PGOPT['wrnlog'], 21)
         if not rfile: return self.pglog(rmtinfo + ": NO remote filename returned", self.PGOPT['emlerr'])
         rmtfiles = re.split('::', rfile)
      else:
         rfiles = self.expand_serial_pattern(rfile)
         rcnt = len(rfiles)
         for i in range(rcnt):
            rmtfiles.extend(self.replace_remote_pattern_times(rfiles[i], rmtrec, rmtinfo, tempinfo, edate))
      return rmtfiles if rmtfiles else None

   # get and replace pattern dates/hours for remote files
   def replace_remote_pattern_times(self, rfile, rmtrec, rmtinfo, tempinfo, edate = None):
      rfiles = []
      if not edate: edate = tempinfo['edate']
      ehour = tempinfo['ehour']
      freq = tempinfo['FQ']
      (bdate, bhour) = self.addfrequency(edate, ehour, freq, 0)
      funit = tempinfo['QU'] if tempinfo['QU'] else None
      tintv = rmtrec['tinterval'] if rmtrec['tinterval'] else None
      if not tintv:
         if rmtrec['dindex'] and funit:
            if self.need_time_interval(rfile, freq): return []
         rfiles = [self.one_remote_filename(rfile, edate, ehour, tempinfo, None, bdate, bhour)]
         return rfiles
      elif not funit:
         self.pglog("{}: MISS Update Frequency for given time interval '{}'".format(rmtinfo, tintv), self.PGOPT['emlerr'])
         return []
      ms = re.match(r'^(\d*)([YMWDH])$', tintv)
      if ms:
         val = int(ms.group(1)) if len(ms.group(1)) > 0  else 1
         unit = ms.group(2)
         if unit == 'W': val *= 7
      else:
         self.pglog("{}: time interval '{}' NOT in (Y,M,W,D,H)".format(rmtinfo, tintv), self.PGOPT['emlerr'])
         return []
      # check if multiple data periods
      i = 0   # not single period
      if unit == 'H':
         if freq[3] and freq[3] <= val: i = 1
      elif unit == 'D' or unit == 'W':
         if freq[3] or freq[2] and freq[2] <= val: i = 1
      elif unit == 'M':
         if freq[3] or freq[2] or freq[1] and freq[1] <= val: i = 1
      elif unit == 'Y':
         if not freq[0] or freq[0] <= val: i = 1
      if i == 1:
         rfiles = [self.one_remote_filename(rfile, edate, ehour, tempinfo, None, bdate, bhour)]
         return rfiles
      date = edate
      hour = ehour
      # set ending date/hour for multiple data periods
      max = self.replace_pattern(rmtrec['endtime'], date, 0) if rmtrec['endtime'] else 0
      if max:
         ms = re.match(r'^(\d+-\d+-\d+)', max)
         if ms:
            edate = ms.group(1)
            ms = re.search(r':(\d+)', max)
            if ms: ehour = int(ms.group(1))
            max = 0
         else:
            if freq[1] and max.find(':') > -1:
               maxs = re.split(':', max)
               if len(maxs) == 12:
                  mn = 1
                  ms = re.match(r'^(\d+)-(\d+)', bdate)
                  if ms: mn = int(ms.group(2))
                  max = int(maxs[mn - 1])
               else: # use the first one
                  max = int(maxs[0])
            if max:
               if unit == 'H':
                  (edate, ehour) = self.adddatehour(bdate, bhour, 0, 0, 0, max)
               elif unit == 'Y':
                  edate = self.adddate(bdate, max, 0, 0)
               elif unit == 'M':
                  edate = self.adddate(bdate, 0, max, 0)
               elif unit == 'W' or unit == 'D':
                  edate = self.adddate(bdate, 0, 0, max)
      # set beginning date/hour for multiple data periods
      min = self.replace_pattern(rmtrec['begintime'], date, 0) if rmtrec['begintime'] else 0
      if min:
         ms = re.match(r'^(\d+-\d+-\d+)', min)
         if ms:
            date = ms.group(1)
            ms = re.search(r':(\d+)', min)
            if ms:
               hour = int(ms.group(1))
            else:
               hour = 0
            min = 0
         else:
            date = bdate
            hour = bhour
            if freq[1] and min.find(':') > -1:
               mins = re.split(':', min)
               if len(mins) == 12:
                  mn = 1
                  ms = re.match(r'^(\d+)-(\d+)', date)
                  if ms: mn = int(ms.group(2))
                  min = int(mins[mn-1])
               else: # use the first one
                  min = int(mins[0])
      else:
         date = bdate
         hour = bhour
   
      if min and not isinstance(min, int): min = int(min)
      gotintv = 0
      intv = [0]*4
      if unit == 'Y':
         intv[0] = val
         gotintv += 1
         if min: date = self.adddate(date, min, 0, 0)
      elif unit == 'M':
         intv[1] = val
         gotintv += 1
         if min:
            date = self.adddate(date, 0, min, 0)
         else:
            date = self.enddate(date, 0, 'M')
      elif unit == 'W' or unit == 'D':
         intv[2] = val
         gotintv += 1
         if min: date = self.adddate(date, 0, 0, min)
      elif unit == 'H':
         intv[3] = val
         gotintv += 1
         if hour is None or not freq[3]:
            ehour = 23
            hour = 0
         if min: (date, hour)  = self.adddatehour(date, hour, 0, 0, 0, min)
      if not gotintv:
         self.pglog("{}: error process time internal '{}'".format(rmtinfo, tintv), self.PGOPT['emlerr'])
         return []
      rfiles = []
      i = 0
      while self.diffdatehour(date, hour, edate, ehour) <= 0:
         rfiles.append(self.one_remote_filename(rfile, date, hour, tempinfo, intv, bdate, bhour))
         (date, hour) = self.adddatehour(date, hour, intv[0], intv[1], intv[2], intv[3])
      return rfiles

   # get one hash array for a single remote file name
   def one_remote_filename(self, fname, date, hour, tempinfo, intv, bdate, bhour):
      if tempinfo['NX']:
         (udate, uhour) = self.adddatehour(date, hour, tempinfo['NX'][0], tempinfo['NX'][1], tempinfo['NX'][2], tempinfo['NX'][3])
      else:
         udate = date,
         uhour = hour
      if 'CP' in self.params:
         (vdate, vhour) = self.addfrequency(self.PGOPT['CURDATE'], self.PGOPT['CURHOUR'], tempinfo['FQ'], 1)
      else:
         vdate = self.PGOPT['CURDATE']
         vhour = self.PGOPT['CURHOUR']
      rfile = {}
      if intv is None: intv = tempinfo['FQ']
      rfile['fname'] = self.replace_pattern(fname, date, hour, intv, 0, bdate, bhour)
      if 'FU' in self.params or self.diffdatehour(udate, uhour, vdate, vhour) <= 0:
         if tempinfo['VD'] and self.diffdatehour(date, hour, tempinfo['VD'], tempinfo['VH']) < 0:
            rfile['ready'] = -1
         else:
            rfile['ready'] = 1
      else:
         rfile['ready'] = 0
      rfile['amiss'] = 1 if (tempinfo['amiss'] == 'Y') else 0
      rfile['date'] = date
      rfile['hour'] = hour
      if hour is None:
         rfile['time'] = "23:59:59"
      else:
         rfile['time'] = "{:02}:00:00".format(hour)
      if tempinfo['DC']:
         rfile['rcmd'] = self.replace_pattern(tempinfo['DC'], date, hour, intv, 0, bdate, bhour)
      else:
         rfile['rcmd'] = None
      return rfile

   # record the date/hour for missing data
   def set_miss_time(self, lfile, locrec, tempinfo, rmonly = 0):
      setmiss = 1
      mdate = mhour = None
      pgrec = {}
      if rmonly:
         if(not locrec['missdate'] or 
            self.diffdatehour(tempinfo['edate'], tempinfo['ehour'], locrec['missdate'], locrec['misshour'])):
            return setmiss   # do not remove if miss times not match
      elif self.diffdatehour(tempinfo['edate'], tempinfo['ehour'], tempinfo['VD'], tempinfo['VH']) >= 0:
         mdate = tempinfo['edate']
         if tempinfo['ehour'] is not None: mhour = tempinfo['ehour']
         setmiss = 0
      if locrec['missdate']:
         if not mdate:
            pgrec['missdate'] = pgrec['misshour'] = None
         elif (self.diffdatehour(mdate, mhour, locrec['missdate'], locrec['misshour']) and
               self.diffdatehour(locrec['missdate'], locrec['misshour'], tempinfo['VD'], tempinfo['VH']) < 0):
            pgrec['missdate'] = mdate
            pgrec['misshour'] = mhour
      elif mdate:
         pgrec['missdate'] = mdate
         pgrec['misshour'] = mhour
      if not pgrec:
         if locrec['misshour']:
            if mhour is None or mhour != locrec['misshour']:
               pgrec['misshour'] = mhour
         elif mhour is not None:
            pgrec['misshour'] = mhour
      if pgrec: self.pgupdt("dlupdt", pgrec, "lindex = {}".format(locrec['lindex']), self.PGOPT['extlog'])
      return setmiss

   # reset next data end/update times
   def reset_update_time(self, locinfo, locrec, tempinfo, arccnt, endonly):
      gx = 1 if re.search(r'(^|\s)-GX(\s|$)', locrec['options'], re.I) else 0
      date = tempinfo['edate']
      hour = tempinfo['ehour']
      if not gx and ('UT' in self.params or arccnt > 0):
         pgrec = self.get_period_record(locrec['gindex'], self.params['DS'], locinfo)
         if pgrec:
            ehour = None
            if hour != None:
                ms = re.match(r'^(\d+):', str(pgrec['time_end']))
                if ms: ehour = int(ms.group(1))
            diff = self.diffdatehour(date, hour, pgrec['date_end'], ehour)
            if 'UT' in self.params or diff > 0:
               sdpcmd = "sdp -d {} -g {} -ed {}".format(self.params['DS'][2:], pgrec['gindex'], date)
               if hour != None: sdpcmd += " -et {:02}:59:59".format(hour)
               if self.pgsystem(sdpcmd, self.MSGLOG, 32):
                  einfo = "{}".format(date)
                  if hour != None: einfo += ":{:02}".format(hour)
                  self.pglog("{}: data archive period {} to {}".format(locinfo, ("EXTENDED" if diff > 0 else "CHANGED"), einfo), self.PGOPT['emllog'])
      if not tempinfo['FQ'] or endonly and arccnt < 1: return
      if self.diffdatehour(date, hour, self.params['CD'], self.params['CH']) <= 0:
         (date, hour) = self.addfrequency(date, hour, tempinfo['FQ'], 1)
         date = self.enddate(date, tempinfo['EP'], tempinfo['QU'], tempinfo['FQ'][6])
      if 'UT' in self.params or not locrec['enddate'] or self.diffdatehour(date, hour, locrec['enddate'], locrec['endhour']) > 0:
         record = {'enddate': date}
         if hour != None:
            record['endhour'] = hour
            einfo = "end data date:hour {}:{:02}".format(date, hour)
         else:
            einfo = "end data date {}".format(date)
         if 'GZ' in self.params: einfo += "(UTC)"
         if tempinfo['NX']:
            (date, hour) = self.adddatehour(date, hour, tempinfo['NX'][0], tempinfo['NX'][1], tempinfo['NX'][2], tempinfo['NX'][3])
         if(locrec['enddate'] and
            self.pgupdt("dlupdt", record, "lindex = {}".format(locrec['lindex']), self.PGOPT['extlog'])):
            self.pglog("{}: {} {} for NEXT update".format(locinfo, ("set" if arccnt > 0 else "SKIP to"), einfo), self.PGOPT['emllog'])
            if self.PGOPT['UCNTL']: self.reset_data_time(tempinfo['QU'], tempinfo['edate'], tempinfo['ehour'], locrec['lindex'])
         else:
            self.pglog("{}: {} for NEXT update".format(locinfo, einfo), self.PGOPT['emllog'])
      else:
         if locrec['endhour'] != None:
            einfo = "end data date:hour {}:{:02}".format(locrec['enddate'], locrec['endhour'])
         else:
            einfo = "end data date {}".format(locrec['enddate'])
         if 'GZ' in self.params: einfo += "(UTC)"
         self.pglog("{}: ALREADY set {} for NEXT update".format(locinfo, einfo), self.PGOPT['emllog'])
         if self.PGOPT['UCNTL']: self.reset_data_time(tempinfo['QU'], tempinfo['edate'], tempinfo['ehour'], locrec['lindex'])

   # get period record for sub group
   def get_period_record(self, gindex, dsid, locinfo):
      pgrec = self.pgget("dsperiod", "gindex, date_end, time_end, dorder",
                          "dsid = '{}' AND gindex = {} ORDER BY dorder".format(dsid, gindex), self.PGOPT['extlog'])
      if not pgrec and gindex:
         pgrec = self.pgget("dsgroup", "pindex", "dsid = '{}' AND gindex = {}".format(dsid, gindex), self.PGOPT['extlog'])
         if pgrec: pgrec = self.get_period_record(pgrec['pindex'], dsid, locinfo)
      if pgrec and pgrec['date_end'] and pgrec['date_end'] == "0000-00-00":
         self.pglog(locinfo + ": dsperiod.date_end set as '0000-00-00' by 'gatherxml'", self.PGOPT['emlerr'])
         pgrec = None
      return pgrec

   # check if need time interval for remote/server file
   def need_time_interval(self, fname, freq):
      units = self.temporal_pattern_units(fname, self.params['PD'])
      if not units: return 0   # no temporal pattern found in file name    
      funit = punit = None
      if freq[2] > 0:
         if 'H' in units:
            punit = "Hourly"
            funit = "Daily"
      elif freq[1] > 0:
         if 'H' in units:
            punit = "Hourly"
         elif 'D' in units:
            punit = "Daily"
         if punit: funit = "Monthly"
      elif freq[0] > 0:
         if 'H' in units:
            punit = "Hourly"
         elif 'D' in units:
            punit = "Daily"
         elif 'M' in units:
            punit = "Monthly"
         if punit: funit = "Yearly"
      if punit:
         self.pglog("{}: Remote File Name seems defined at {} Time Interval for {} Update, ".format(fname, punit, funit) +
                     "specify the Time Interval in remote file record to continue", self.PGOPT['emllog'])
         return 1
      else:
         return 0

   # check if local file is a growing one
   def is_growing_file(self, fname, freq):
      units = self.temporal_pattern_units(fname, self.params['PD'])
      if not units: return 1   # no temporal pattern found in file name    
      if freq[3] > 0:
         if 'H' in units: return 0
      elif freq[2] > 0:
         if 'H' in units or 'D' in units: return 0
      elif freq[1] > 0:
         if 'H' in units or 'D' in units or 'M' in units and not freq[6]: return 0
      elif freq[0] > 0:
         return 0
      return 1

   # add update frequency to date/hour
   # opt = -1 - minus, 0 - begin time, 1 - add (default)
   def addfrequency(self, date, hour, intv, opt = 1):
      if date and not isinstance(date, str): date = str(date)
      if not intv: return (date, hour)
      freq = intv.copy()
      if opt == 0: # get begin time of next period
         if freq[3]:
            if freq[3] == 1: return (date, hour)
            (date, hour) = self.adddatehour(date, hour, 0, 0, 0, 1)   # add one hour
         else:
            if freq[2] == 1: return (date, hour)
            date = self.adddate(date, 0, 0, 1)   # add one day
      if opt < 1: # negative frequency for minus
         flen = len(freq)
         for i in range(flen):
            if freq[i]: freq[i] = -freq[i]
      if freq[6]:    # add fraction month
         date = self.addmonth(date, freq[1], freq[6])
      elif hour != None:  # add date/hour
         (date, hour) = self.adddatehour(date, hour, freq[0], freq[1], freq[2], freq[3])
      else:  # add date only
         date = self.adddate(date, freq[0], freq[1], freq[2])
      return (date, hour)

   #  send a cumtomized email if built during specialist's process
   def send_updated_email(self, lindex, locinfo):
      pgrec = self.pgget("dlupdt", "emnote", "lindex = {}".format(lindex), self.LOGERR)
      if not (pgrec and pgrec['emnote']): return   # no customized email info to send   
      if not self.send_customized_email(locinfo, pgrec['emnote'], self.PGOPT['emllog']): return
      self.pgexec("update dlupdt set emnote = null where lindex = {}".format(lindex), self.LOGERR)   # empty email after sent

   # validate given local indices
   def validate_lindices(self, cact):
      if (self.OPTS['LI'][2]&8) == 8: return 0  # already validated
      zcnt = 0
      lcnt = len(self.params['LI'])
      i = 0
      while i < lcnt:
         val = self.params['LI'][i]
         if val:
            if isinstance(val, int):
               self.params['LI'][i] = val
            else:
               if re.match(r'^(!|<|>|<>)$', val): break
               self.params['LI'][i] = int(val)
         else:
            self.params['LI'][i] = 0
         i += 1
      if i >= lcnt:   # normal locfile index given
         for i in range(lcnt):
            val = self.params['LI'][i]
            if not val:
               if cact == "SL":
                  if 'NL' not in self.params: self.action_error("Mode option -NL to add new local file record")
                  zcnt += 1
               elif cact == "SR":
                  self.action_error("Local File Index 0 is not allowed/n" +
                               "Use Action SL with Mode option -NL to add new record")
               continue
            if i > 0 and val == self.params['LI'][i-1]: continue
            pgrec = self.pgget("dlupdt", "dsid, specialist", "lindex = {}".format(val), self.PGOPT['extlog'])
            if not pgrec:
               self.action_error("Locfile Index {} is not in RDADB".format(val))
            elif self.OPTS[self.PGOPT['CACT']][2] > 0:
               if pgrec['specialist'] == self.PGLOG['CURUID']:
                  self.params['MD'] = 1
               else:
                  self.validate_dsowner("dsupdt", pgrec['dsid'])
      else: # found none-equal condition sign
         pgrec = self.pgmget("dlupdt", "DISTINCT lindex", self.get_field_condition("lindex", self.params['LI'], 0, 1), self.PGOPT['extlog'])
         if not pgrec: self.action_error("No update record matches given Locfile Index condition")
         self.params['LI'] = pgrec['lindex']
      self.OPTS['LI'][2] |= 8   # set validated flag
      return zcnt

   # validate given control indices
   def validate_cindices(self, cact):
      if (self.OPTS['CI'][2] & 8) == 8: return 0   # already validated
      zcnt = 0
      if 'CI' in self.params:
         ccnt = len(self.params['CI'])
         i = 0
         while i < ccnt:
            val = self.params['CI'][i]
            if val:
               if isinstance(val, int):
                  self.params['CI'][i] = val
               else:
                  if re.match(r'^(!|<|>|<>)$', val): break
                  self.params['CI'][i] = int(val)
            else:
               self.params['CI'][i] = 0
            i += 1
         if i >= ccnt:   # normal locfile index given
            for i in range(ccnt):
               val = self.params['CI'][i]
               if not val:
                  if cact == 'SC':
                     if 'NC' in self.params:
                        self.params['CI'][i] = 0
                        zcnt += 1
                     else:
                        self.action_error("Mode option -NC to add new update control record")
                  continue
               if i > 0 and val == self.params['CI'][i-1]: continue
               pgrec = self.pgget("dcupdt", "dsid, specialist", "cindex = {}".format(val), self.PGOPT['extlog'])
               if not pgrec:
                  self.action_error("Control Index {} is not in RDADB".format(val))
               elif self.OPTS[self.PGOPT['CACT']][2] > 0:
                  if pgrec['specialist'] == self.PGLOG['CURUID']:
                     self.params['MD'] = 1
                  else:
                     self.validate_dsowner("dsupdt", pgrec['dsid'])
         else: # found none-equal condition sign
            pgrec = self.pgmget("dcupdt", "DISTINCT cindex", self.get_field_condition("cindex", self.params['CI'], 0, 1), self.PGOPT['extlog'])
            if not pgrec: self.action_error("No update control record matches given Index condition")
            self.params['CI'] = pgrec['cindex']   
         if len(self.params['CI']) > 1 and self.PGOPT['ACTS']&self.PGOPT['CNTLACTS']:
            self.action_error("Process one Update Control each time")
      elif 'ID' in self.params:
         self.params['CI'] = self.cid2cindex(cact, self.params['ID'], zcnt)
      self.OPTS['CI'][2] |= 8   # set validated flag
      return zcnt

   # get control index array from given control IDs
   def cid2cindex(self, cact, cntlids, zcnt):
      count = len(cntlids) if cntlids else 0
      if count == 0: return None
      i = 0
      while i < count:
         val = cntlids[i]
         if val and (re.match(r'^(!|<|>|<>)$', val) or val.find('%') > -1): break
         i += 1
      if i >= count: # normal control id given
         indices = [0]*count
         for i in range(count):
            val = cntlids[i]
            if not val:
               continue
            elif i and (val == cntlids[i-1]):
               indices[i] = indices[i-1]
               continue
            else:
               pgrec = self.pgget("dcupdt", "cindex", "cntlid = '{}'".format(val), self.PGOPT['extlog'])
               if pgrec: indices[i] = pgrec['cindex']
            if not indices[i]:
               if cact == "SC":
                  if 'NC' in self.params:
                     indices[i] = 0
                     zcnt += 1
                  else:
                     self.action_error("Control ID {} is not in RDADB,\n".format(val) +
                                       "Use Mode Option -NC (-NewControl) to add new Control", cact)
               else:
                  self.action_error("Control ID '{}' is not in RDADB".format(val), cact)
         return indices
      else:  # found wildcard and/or none-equal condition sign
         pgrec = self.pgmget("dcupdt", "DISTINCT cindex",  self.get_field_condition("cntlid", cntlids, 1, 1), self.PGOPT['extlog'])
         if not pgrec: self.action_error("No Control matches given Control ID condition")
         return pgrec['cindex']

   # check remote server file information
   def check_server_file(self, dcmd, opt, cfile):
      sfile = info = type = None
      self.PGLOG['SYSERR'] = self.PGOPT['STATUS'] = ''
      docheck = 1
      copt = opt|256
      ms = re.search(r'(^|\s|\||\S/)rdacp\s+(.+)$', dcmd)
      if ms:
         buf = ms.group(2)
         type = "RDACP"
         docheck = 0
         ms = re.match(r'^(-\w+)', buf)
         while ms:
            flg = ms.group(1)
            buf = re.sub(r'^-\w+\s+'.format(flg), '', buf, 1)   # remove options
            if flg != "-r":   # no option value
               m = re.match(r'^(\S+)\s', buf)
               if not m: break
               if flg == "-f":
                  sfile = ms.group(1)
               elif flg == "-fh":
                  target = ms.group(1)
               buf = re.sub(r'^\S\s+', '', buf, 1)   # remove values
            ms = re.match(r'^(-\w+)', buf)
         if not sfile:
             ms = re.match(r'^(\S+)', buf)
             if ms: sfile = ms.group(1)
         info = self.check_rda_file(sfile, target, copt)
      if docheck:
         ms = re.search(r'(^|\s|\||\S/)(mv|cp)\s+(.+)$', dcmd)
         if ms:
            sfile = ms.group(3)
            type = "COPY" if ms.group(2) == "cp" else "MOVE"
            docheck = 0
            ms = re.match(r'^(-\w+\s+)', sfile)
            while ms:
               sfile = re.sub(r'^-\w+\s+', '', sfile, 1)   # remove options
               ms = re.match(r'^(-\w+\s+)', sfile)
            ms = re.match(r'^(\S+)\s', sfile)
            if ms: sfile = ms.group(1)
            info = self.check_local_file(sfile, copt)
      if docheck:
         ms = re.search(r'(^|\s|\||\S/)tar\s+(-\w+)\s+(\S+\.tar)\s+(\S+)$', dcmd)
         if ms:
            sfile = ms.group(4)
            target = ms.group(3)
            type = "UNTAR" if ms.group(2).find('x') > -1 else "TAR"
            docheck = 0
            info = self.check_tar_file(sfile, target, copt)
      if docheck:
         ms = re.search(r'(^|\s|\||\S/)ncftpget\s(.*)(ftp://\S+)', dcmd, re.I)
         if ms:
            sfile = ms.group(3)
            buf = ms.group(2)
            type = "FTP"
            docheck = 0
            user = pswd = None
            if buf:
               ms = re.search(r'(-u\s+|--user=)(\S+)', buf)
               if ms: user = ms.group(2)
               ms = re.search(r'(-p\s+|--password=)(\S+)', buf)
               if ms: pswd = ms.group(2)
            info = self.check_ftp_file(sfile, copt, user, pswd)
      if docheck:
         ms = re.search(r'(^|\s|\||\S/)wget(\s.*)https{0,1}://(\S+)', dcmd, re.I)
         if ms:
            obuf = ms.group(2)
            wbuf = ms.group(3)
            sfile = op.basename(wbuf)
            self.slow_web_access(wbuf)
            type = "WGET"
            docheck = 0
            if not obuf or not re.search(r'\s-N\s', obuf): dcmd = re.sub(r'wget', 'wget -N', dcmd, 1)
            flg = 0
            if cfile and sfile != cfile:
               if self.pgsystem("cp -p {} {}".format(cfile, sfile), self.PGOPT['emerol'], 4): flg = 1
            buf = self.pgsystem(dcmd, self.PGOPT['wrnlog'], 16+32)
            info = self.check_local_file(sfile, opt, self.PGOPT['wrnlog'])
            if buf:
               if not info: self.PGOPT['STATUS'] = buf
               if re.search(r'Saving to:\s', buf):
                  flg = 0
               elif not re.search(r'(Server file no newer|not modified on server)', buf):
                  if info: info['note'] = "{}:\n{}".format(dcmd, buf)
            else:
               if info: info['note'] = dcmd + ": Failed checking new file"   
            if flg: self.pgsystem("rm -rf " + sfile, self.PGOPT['emerol'], 4)
      if docheck:
         ms = re.match(r'^(\S+)\s+(.+)$', dcmd)
         if ms:
            buf = ms.group(2)
            type = op.basename(ms.group(1)).upper()
            files = re.split(' ', buf)
            for file in files:
               if re.match(r'^-\w+', file) or not op.exists(file) or cfile and file == cfile: continue
               info = self.check_local_file(file, copt)
               if info:
                  info['data_size'] = 0
                  break   
               sfile = file
      if info:
         info['ftype'] = type
      else:
         if not self.PGOPT['STATUS']: self.PGOPT['STATUS'] = self.PGLOG['SYSERR']
         if not sfile: self.pglog(dcmd + ": NO enough information in command to check file info", self.PGOPT['errlog'])
      return info

   # check and sleep if given web site need to be slowdown for accessing
   def slow_web_access(self, wbuf):
      for wsite in self.WSLOWS:
         if wbuf.find(wsite) > -1:
            time.sleep(self.WSLOWS[wsite])

   # check remote server/file status information
   # return 1 if exists; 0 missed, -1 with error, -2 comand not surported yet
   # an error message is stored in self.PGOPT['STATUS'] if not success
   def check_server_status(self, dcmd):
      self.PGOPT['STATUS'] = ''
      target = None
      ms = re.search(r'(^|\s|\||\S/)rdacp\s+(.+)$', dcmd)
      if ms:
         buf = ms.group(2)
         ms = re.search(r'-fh\s+(\S+)', buf)
         if ms: target = ms.group(1)
         ms = re.search(r'-f\s+(\S+)', buf)
         if ms:
            fname = ms.group(1)
         else:
            ms = re.match(r'^(-\w+)', buf)
            while ms:
               flg = ms.group(1)
               buf = re.sub(r'^-\w+\s+', '', buf, 1)   # remove options
               if flg != "-r":   # no option value
                  if not re.match(r'^\S+\s', buf): break
                  buf = re.sub(r'^\S+\s+', '', buf, 1)   # remove values
               ms = re.match(r'^(-\w+)', buf)
            ms = re.match(r'^(\S+)', buf)
            if ms: fname = ms.group(1)
            if not fname:
               self.PGOPT['STATUS'] = dcmd + ": MISS from-file per option -f"
               return -1
         if not target:
            return self.check_local_status(fname)
         else:
            return self.check_remote_status(target, fname)
      ms = re.search(r'(^|\s|\||\S/)(mv|cp|tar|cnvgrib|grabbufr|pb2nc)\s+(.+)$', dcmd)
      if ms:
         buf = ms.group(2)
         fname = ms.group(3)
         ms = re.match(r'^(-\w+\s+)', fname)
         while ms:
            fname = re.sub(r'^-\w+\s+', '', fname, 1)   # remove options
            ms = re.match(r'^(-\w+\s+)', fname)
         ms = re.match(r'^(\S+)\s+(\S*)', fname)
         if ms:
            fname = ms.group(1)
            if buf == 'tar': target = ms.group(2)
         if target:
            return self.check_tar_status(fname, target)
         else:
            return self.check_local_status(fname)
      ms = re.search(r'(^|\s|\||\S/)ncftpget\s(.*)(ftp://[^/]+)(/\S+)', dcmd, re.I)
      if ms:
         buf = ms.group(2)
         target = ms.group(3)
         fname = ms.group(4)
         user = pswd = None
         if buf:
            ms = re.search(r'(-u\s+|--user=)(\S+)', buf)
            if ms: user = ms.group(2)
            ms = re.search(r'(-p\s+|--password=)(\S+)', buf)
            if ms: pswd = ms.group(2)
         return self.check_ftp_status(target, fname, user, pswd)
      ms = re.search(r'(^|\s|\||\S/)wget\s(.*)(https{0,1}://[^/]+)(/\S+)', dcmd, re.I)
      if ms:
         buf = ms.group(2)
         target = ms.group(3)
         fname = ms.group(4)
         user = pswd = None
         if buf:
            ms = re.search(r'(-u\s+|--user=|--http-user=)(\S+)', buf)
            if ms: user = ms.group(2)
            ms = re.search(r'(-p\s+|--password=|--http-passwd=)(\S+)', buf)
            if ms: pswd = ms.group(2)
         return self.check_wget_status(target, fname, user, pswd)
      ms = re.match(r'^\s*(\S+)', dcmd)
      if ms and self.valid_command(ms.group(1)):
         return 0
      else:
         self.PGOPT['STATUS'] = dcmd + ": Invalid command"
      return -2

   # check status for remote server/file via wget
   # return self.SUCCESS if file exist and self.FAILURE otherwise. 
   # file status message is returned via reference string of $status
   def check_wget_status(self, server, fname, user, pswd):
      cmd = "wget --spider --no-check-certificate "
      if user or pswd:
         self.PGOPT['STATUS'] = "{}{}: {}".format(server, fname, self.PGLOG['MISSFILE'])
         return -1
      if user: cmd += "--user={} ".format(user)
      if pswd: cmd += "--password={} ".format(pswd)
      cmd += server
      pname = None
      i = 0
      while True:
         msg = self.pgsystem(cmd + fname, self.LOGWRN, 48)   # 16+32
         if msg:
            if msg.find('Remote file exists') > -1:
               if pname:
                  self.PGOPT['STATUS'] = "{}{}: {}".format(server, pname, self.PGLOG['MISSFILE'])
                  return (-1 if i > self.PGOPT['PCNT'] else 0)
               else:
                  return 1
            elif msg.find('unable to resolve host address') > -1:
               self.PGOPT['STATUS'] = server + ": Server Un-accessible"
               return -2
            elif msg.find('Remote file does not exist') < 0:
               self.PGOPT['STATUS'] = "{}{}: Error check status:\n{}".format(cmd, fname, msg)
               return -2
         pname = fname
         fname = op.dirname(pname)
         if not fname or fname == "/":
            self.PGOPT['STATUS'] = "{}{}: {}".format(server, pname, self.PGLOG['MISSFILE'])
            return -1
         fname += "/"
         i += 1

   # check status for remote server/file via check_ftp_file()
   # return self.SUCCESS if file exist and self.FAILURE otherwise. 
   # file status message is returned via reference string of $status
   def check_ftp_status(self, server, fname, user, pswd):
      cmd = "ncftpls "
      if user: cmd += "-u {} ".format(user)
      if pswd: cmd += "-p {} ".format(pswd)
      cmd += server
      pname = None
      i = 0
      while True:
         msg = self.pgsystem(cmd + fname, self.LOGWRN, 272)   # 16+256
         if self.PGLOG['SYSERR']:
            if self.PGLOG['SYSERR'].find('unknown host') > -1:
               self.PGOPT['STATUS'] = server + ": Server Un-accessible"
               return -2
            elif self.PGLOG['SYSERR'].find('Failed to change directory') < 0:
               self.PGOPT['STATUS'] = "{}{}: Error check status:\n{}".format(server, fname, self.PGLOG['SYSERR'])
               return -2
         elif not msg:
            self.PGOPT['STATUS'] = "{}{}: {}".format(server, fname, self.PGLOG['MISSFILE'])
            return -1 if i >= self.PGOPT['PCNT'] else 0
         elif pname:
            self.PGOPT['STATUS'] = "{}{}: {}".format(server, pname, self.PGLOG['MISSFILE'])
            return -1 if i > self.PGOPT['PCNT'] else 0
         else:
            return 1
         pname = fname
         fname = op.dirname(pname)
         if not fname or fname == "/":
            self.PGOPT['STATUS'] = "{}{}: {}".format(server, pname, self.PGLOG['MISSFILE'])
            return -1
         i += 1

   # check remote server status
   def check_remote_status(self, host, fname):
      pname = None
      i = 0
      while True:
         msg = self.pgsystem("{}-sync {}".format(host, fname), self.LOGWRN, 272)   # 16+256
         if msg:
            for line in re.split('\n', msg):
               info = self.remote_file_stat(line, 0)
               if info:
                  if pname:
                     self.PGOPT['STATUS'] = "{}-{}: {}".format(host, pname. self.PGLOG['MISSFILE'])
                     return -1 if i > self.PGOPT['PCNT'] else 0
                  else:
                     return 1
         if self.PGLOG['SYSERR'] and self.PGLOG['SYSERR'].find(self.PGLOG['MISSFILE']) < 0:
            self.PGOPT['STATUS'] = "{}-sync {}: Error check status:\n{}".format(host, fname, self.PGLOG['SYSERR'])
            return -2
         pname = fname
         fname = op.dirname(pname)
         if not fname or fname == "/":
            self.PGOPT['STATUS'] = "{}-{}: {}".format(host, pname, self.PGLOG['MISSFILE'])
            return -1
         i += 1

   # check local disk status
   def check_local_status(self, fname):
      pname = None
      i = 0
      while True:
         if op.exists(fname):
            if pname:
               self.PGOPT['STATUS'] = "{}: {}".format(pname, self.PGLOG['MISSFILE'])
               return -1 if i > self.PGOPT['PCNT'] else 0
            else:
               return 1
         if self.PGLOG['SYSERR'] and self.PGLOG['SYSERR'].find(self.PGLOG['MISSFILE']) < 0:
            self.PGOPT['STATUS'] = "{}: Error check status:\n{}".format(fname, self.PGLOG['SYSERR'])
            return -2
         pname = fname
         fname = op.dirname(pname)
         if not fname or fname == "/":
            self.PGOPT['STATUS'] = "{}: {}".format(pname, self.PGLOG['MISSFILE'])
            return -1
         i += 1

   # check tar file status
   def check_tar_status(self, fname, target):
      stat = self.check_local_status(fname)
      if stat < 1: return stat
      msg = self.pgsystem("tar -tvf {} {}".format(fname, target), self.LOGWRN, 272)   # 16+256
      if msg:
         for line in re.split('\n', msg):
            if self.tar_file_stat(line, 0): return 1
      if not self.PGLOG['SYSERR'] or self.PGLOG['SYSERR'].find('Not found in archive') > -1:
         self.PGOPT['STATUS'] = "{}: Not found in tar file {}".format(target, fname)
         return 0
      else:
         self.PGOPT['STATUS'] = "{}: Error check tar file {}:\n{}".format(target, fname, self.PGLOG['SYSERR'])
         return -1

   # count directories with temoral patterns in given path
   def count_pattern_path(self, dcmd):
      getpath = 1
      ms = re.search(r'(^|\s|\||\S/)rdacp\s+(.+)$', dcmd)
      if ms:
         path = ms.group(2)
         getpath = 0
         ms = re.search(r'-f\s+(\S+)', path)
         if ms:
            path = ms.group(1)
         else:
            ms = re.match(r'^(-\w+)', path)
            while ms:
               flg = ms.group(1)
               path = re.sub(r'^-\w+\s+', '', path, 1)   # remove options
               if flg != "-r":    # no option value
                  ms = re.match(r'^(\S+)\s', path)
                  if not ms: break
                  path = re.sub(r'^\S+\s+', '', path, 1)    # remove values
               ms = re.match(r'^(-\w+)', path)
            ms = re.match(r'^(\S+)', path)
            if ms: path = ms.group(1)
            if not path: return self.pglog(dcmd + ": MISS from-file per option -f", self.PGOPT['emlerr'])
      if getpath:
         ms = re.search(r'(^|\s|\||\S/)(mv|cp|tar|cnvgrib|grabbufr|pb2nc)\s+(.+)$', dcmd)
         if ms:
            path = ms.group(3)
            getpath = 0
            ms = re.match(r'^-\w+\s', path)
            while ms:
               path = re.sub(r'^-\w+\s+', '', path, 1)   # remove options
               ms = re.match(r'^-\w+\s', path)
            ms = re.match(r'^(\S+)\s+(\S*)', path)
            if ms: path = ms.group(1)
      if getpath:
         ms = re.search(r'(^|\s|\||\S/)(ncftpget|wget)\s(.*)(ftp|http|https)://[^/]+(/\S+)', dcmd, re.I)
         if ms: path = ms.group(5)
      if not path: return self.pglog(dcmd + ": Unkown command to count pattern path", self.PGOPT['emlerr'])
      pcnt = path.find(self.params['PD'][0])
      if pcnt > 0:
         path = path[pcnt:]
         p = re.findall(r'/', path)
         pcnt = len(p) + 1
      else:
         pcnt = 1
      return pcnt

   # check error message for download action
   def parse_download_error(self, err, act, sinfo = None):
      derr = ''
      stat = 0
      if sinfo:
         if sinfo['data_size'] == 0:
            derr = ", empty file"
            if err: derr += ' ' + err
         elif sinfo['data_size'] < self.PGLOG['MINSIZE']:
            derr = ", small file({}B)".format(sinfo['data_size'])
            if err: derr += ' ' + err
         else:
            stat = 1
      elif err:
         derr = err
         if (err.find('command not found') > -1 or
             err.find('403 Forbidden') > -1):
            stat = -2
         elif (act == "wget" and err.find('404 Not Found') > -1 or
             act == "UNTAR" and err.find('Not found in archive') > -1 or
             act == "ncftpget" and err.find('Failed to open file') > -1 or
             err.find(self.PGLOG['MISSFILE']) > -1):
            derr = self.PGLOG['MISSFILE']
         else:
            stat = -1
      return (stat, derr)

   # cache update control information
   def cache_update_control(self, cidx, dolock = 0):
      cstr = "C{}".format(cidx)
      pgrec = self.pgget("dcupdt", "*", "cindex = {}".format(cidx), self.PGOPT['emlerr'])
      if not pgrec: return self.pglog(cstr + ": update control record NOT in RDADB", self.PGOPT['errlog'])
      if pgrec['dsid']:
         if 'DS' not in self.params: self.params['DS'] = pgrec['dsid']
         cstr = "{}-{}".format(self.params['DS'], cstr)
         if self.params['DS'] != pgrec['dsid']:
            return self.pglog("{}: Control dataset {} NOT match".format(cstr, pgrec['dsid']), self.PGOPT['emlerr'])
      if pgrec['hostname'] and not self.valid_control_host(cstr, pgrec['hostname'], self.PGOPT['emlerr']): return self.FAILURE
      if not ('ED' in self.params or self.valid_data_time(pgrec, cstr, self.PGOPT['emlerr'])): return self.FAILURE
      if dolock and self.lock_update_control(cidx, 1, self.PGOPT['emlerr']) <= 0: return self.FAILURE
      if self.PGLOG['DSCHECK']: self.set_dscheck_attribute("oindex", cidx)
      if pgrec['updtcntl']:
         if pgrec['updtcntl'].find('A') > -1: self.params['CA'] = 1
         if pgrec['updtcntl'].find('B') > -1: self.params['UB'] = 1
         if pgrec['updtcntl'].find('C') > -1: self.params['CP'] = 1
         if pgrec['updtcntl'].find('E') > -1: self.params['RE'] = 1
         if pgrec['updtcntl'].find('F') > -1: self.params['FU'] = 1
         if pgrec['updtcntl'].find('G') > -1:
            self.params['GZ'] = 1
            self.PGLOG['GMTZ'] = self.diffgmthour()
         if pgrec['updtcntl'].find('M') > -1: self.params['MU'] = 1
         if pgrec['updtcntl'].find('N') > -1: self.params['CN'] = 1
         if pgrec['updtcntl'].find('O') > -1: self.params['MO'] = 1
         if pgrec['updtcntl'].find('Y') > -1: self.PGLOG['NOLEAP'] = self.params['NY'] = 1
         if pgrec['updtcntl'].find('Z') > -1 and 'VS' not in self.params:
            self.PGLOG['MINSIZE'] = self.params['VS'] = 0
      if pgrec['emailcntl'] != 'A':
         if pgrec['emailcntl'] == "N":
            self.params['NE'] = 1
            self.PGLOG['LOGMASK'] &= ~self.EMLALL   # turn off all email acts
         elif pgrec['emailcntl'] == "S":
            self.params['SE'] = 1
            self.PGOPT['emllog'] |= self.EMEROL
         elif pgrec['emailcntl'] == "E":
            self.params['EE'] = 1
         elif pgrec['emailcntl'] == "B":
            self.params['SE'] = 1
            self.params['EE'] = 1
            self.PGOPT['emllog'] |= self.EMEROL
      if pgrec['errorcntl'] != 'N':
         if pgrec['errorcntl'] == "I":
            self.params['IE'] = 1
         elif pgrec['errorcntl'] == "Q":
            self.params['QE'] = 1
      if pgrec['keepfile'] != 'N':
         if pgrec['keepfile'] == "S":
            self.params['KS'] = 1
         elif pgrec['keepfile'] == "R":
            self.params['KR'] = 1
         elif pgrec['keepfile'] == "B":
            self.params['KR'] = 1
            self.params['KS'] = 1
      if pgrec['houroffset'] and 'HO' not in self.params: self.params['HO'] = [pgrec['houroffset']]
      if pgrec['emails'] and 'CC' not in self.params: self.add_carbon_copy(pgrec['emails'], 1)
      self.cache_data_time(cidx)
      self.PGOPT['UCNTL'] = pgrec
      return self.SUCCESS

   # cache date time info
   def cache_data_time(self, cidx):
      pgrecs = self.pgmget("dlupdt", "lindex, enddate, endhour", "cindex = {}".format(cidx), self.PGOPT['emlerr'])
      cnt =  len(pgrecs['lindex']) if pgrecs else 0
      for i in range(cnt):
         if not pgrecs['enddate'][i]: continue
         dhour = pgrecs['endhour'][i] if (pgrecs['endhour'][i] is not None) else 23
         self.PGOPT['DTIMES'][pgrecs['lindex'][i]] = "{} {:02}:59:59".format(pgrecs['enddate'][i], dhour)

   #  check if valid host to process update control
   def valid_control_host(self, cstr, hosts, logact):
      host = self.get_host(1)
      if hosts:
         if re.search(host, hosts, re.I):
            if hosts[0] == '!':
               return self.pglog("{}: CANNOT be processed on {}".format(cstr, hosts[1:]), logact)
         elif not re.match(r'^!', hosts):
            return self.pglog("{}-{}: MUST be processed on {}".format(host, cstr, hosts), logact)
      return self.SUCCESS

   # reset updated data time
   def reset_data_time(self, qu, ddate, dhour, lidx):
      pgrec = self.PGOPT['UCNTL']
      record = {'chktime': int(time.time())}
      if ddate:
         if dhour is None: dhour = 0 if qu == 'H' else 23
         dtime = "{} {:02}:59:59".format(ddate, dhour)
         if lidx not in self.PGOPT['DTIMES'] or self.pgcmp(self.PGOPT['DTIMES'][lidx], dtime) < 0:
            self.PGOPT['DTIMES'][lidx] = dtime
         # get earliest data time
         for ltime in self.PGOPT['DTIMES'].values():
            if self.pgcmp(ltime, dtime) < 0: dtime = ltime
         if not pgrec['datatime'] or self.pgcmp(pgrec['datatime'], dtime) < 0:
            self.PGOPT['UCNTL']['datatime'] = record['datatime'] = dtime
      if self.pgupdt("dcupdt", record, "cindex = {}".format(pgrec['cindex']), self.PGOPT['extlog']) and 'datatime' in record:
          self.pglog("{}-C{}: Data time updated to {}".format(self.params['DS'], pgrec['cindex'], dtime),  self.PGOPT['emllog'])

   # adjust control time according to the control offset
   def adjust_control_time(self, cntltime, freq, unit, offset, curtime):
      if offset:
         ofreq = self.get_control_time(offset, "Control Offset")
         if ofreq:   # remove control offset
            nfreq = ofreq.copy()
            for i in range(6):
               if nfreq[i]: nfreq[i] = -nfreq[i]
            cntltime = self.adddatetime(cntltime, nfreq[0], nfreq[1], nfreq[2], nfreq[3], nfreq[4], nfreq[5], nfreq[6])
      else:
         ofreq = None
      (cdate, ctime) = re.split(' ', cntltime)
      if unit == "H":
         hr = 0
         if ctime:
            ms = re.match(r'^(\d+)', ctime)
            if ms: hr = int(int(ms.group(1))/freq[3])*freq[3]
         else:
            i = 0
         cntltime = "{} {:02}:00:00".format(cdate, hr)
      else:
         cdate = self.enddate(cdate, (0 if unit == "W" else 1), unit, freq[6])
         cntltime = "{} 00:00:00".format(cdate)
      if ofreq: cntltime = self.adddatetime(cntltime, ofreq[0], ofreq[1], ofreq[2], ofreq[3], ofreq[4], ofreq[5], ofreq[6])   # add control offset
      while self.pgcmp(cntltime, curtime) <= 0:
         cntltime = self.adddatetime(cntltime, freq[0], freq[1], freq[2], freq[3], freq[4], freq[5], freq[6])
      return cntltime

   #  reset control time
   def reset_control_time(self):   
      pgrec = self.PGOPT['UCNTL']
      cstr = "{}-C{}".format(self.params['DS'], pgrec['cindex'])
      gmt = self.PGLOG['GMTZ']
      self.PGLOG['GMTZ'] = 0
      curtime = self.curtime(1)
      self.PGLOG['GMTZ'] = gmt
      (freq, unit) = self.get_control_frequency(pgrec['frequency'])
      if not freq: return self.pglog("{}: {}".format(cstr, unit), self.PGOPT['emlerr'])
      cntltime = self.check_datetime(pgrec['cntltime'], curtime)
      nexttime = self.adjust_control_time(cntltime, freq, unit, pgrec['cntloffset'], curtime)
      if self.PGLOG['ERRCNT']:
         cfreq = self.get_control_time(pgrec['retryint'], "Retry Interval")
         if cfreq:
            while self.pgcmp(cntltime, curtime) <= 0:
               cntltime = self.adddatetime(cntltime, cfreq[0], cfreq[1], cfreq[2], cfreq[3], cfreq[4], cfreq[5], cfreq[6])
            if self.pgcmp(cntltime, nexttime) < 0: nexttime = cntltime
      record = {}
      cstr += ": Next Control Time "
      if not pgrec['cntltime'] or self.pgcmp(nexttime, pgrec['cntltime']) > 0:
         record['cntltime'] = nexttime
         cstr += "set to {}".format(nexttime)
         if self.PGLOG['ERRCNT']: cstr += " to retry"
      else:
         cstr += "already set to {}".format(pgrec['cntltime'])
      cstr += " for Action {}({})".format(self.PGOPT['CACT'], self.OPTS[self.PGOPT['CACT']][1])
      record['pid'] = 0
      if self.pgupdt("dcupdt", record, "cindex = {}".format(pgrec['cindex']), self.PGOPT['extlog']):
         self.pglog(cstr, self.PGOPT['emllog'])

   # get array information of individual controlling time
   def get_control_time(self, val, type):
      if not val or val == '0': return 0
      if re.search(r'/(\d+)$', val):
         return self.pglog("{}: '{}' NOT support Fraction".format(val, type), self.PGOPT['emlerr'])
      ctimes = [0]*7   # initialize control times
      ms = re.search(r'(\d+)Y', val, re.I)
      if ms: ctimes[0] = int(ms.group(1))
      ms = re.search(r'(\d+)M', val, re.I)
      if ms: ctimes[1] = int(ms.group(1))
      ms = re.search(r'(\d+)D', val, re.I)
      if ms: ctimes[2] = int(ms.group(1))
      ms = re.search(r'(\d+)W', val, re.I)
      if ms: ctimes[2] += 7*int(ms.group(1))
      ms = re.search(r'(\d+)H', val, re.I)
      if ms: ctimes[3] = int(ms.group(1))
      ms = re.search(r'(\d+)N', val, re.I)
      if ms: ctimes[4] = int(ms.group(1))
      ms = re.search(r'(\d+)S', val, re.I)
      if ms: ctimes[5] = int(ms.group(1))
      for ctime in ctimes:
         if ctime > 0: return ctimes
      return self.pglog("{}: invalid '{}', must be (Y,M,W,D,H,N,S)".format(val, type), self.PGOPT['emlerr'])

   #  get group index from given option string
   def get_group_index(self, option, edate, ehour, freq):
      ms = re.search(r'-GI\s+(\S+)', option, re.I)
      if ms: return int(self.replace_pattern(ms.group(1), edate, ehour, freq))
      ms = re.search(r'-GN\s+(.*)$', option, re.I)
      if ms:
         grp = ms.group(1)
         if grp[0] == "'":
            grp = grp[1:]
            idx = grp.find("'")
            grp = grp[:idx]
         else:
            ms = re.match(r'^(\S+)', grp)
            if ms: grp = ms.group(1)
         pgrec = self.pgget("dsgroup", "gindex", "dsid = '{}' AND grpid = '{}'".format(self.params['DS'], self.replace_pattern(grp, edate, ehour, freq)), self.PGOPT['extlog'])
         if pgrec: return pgrec['gindex']
      return 0
