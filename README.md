# EMC Vmax Utils

## Information

The vmax_utils.py script is coded in `python 2.6` and runs on Linux. It requires the `SYMAPI API` in version `V8.*` Minimum.

The script works on Symmetrix `VMAX1`, `VMAX2 (20K,..)` and `VMAX3(200K,..)`.

All array must be declare on Json file `vmax_list_array.json` :

```javascript
[
    {
        "id": "000295700001",   // Symmetrix Array ID
        "export": "Local",      // Name of Remote SE server (symfg list --services) or Local
        "type": 12,             // Array Type 12:Vmax1&2 3:Vmax3
        "one_view": true,       // Logins on one IG and MV or Not
        "loc": "PARIS"          // Array Location
    }
]
```

Script provide following features :
 * Audit (By `Login`, `Storage Group`, `Volume`, `Unmap or Unbind Volume`)
 * Deletion (By `Storage Group`, `Volume`)
 * Creation (`Storage Group`, `Masking`, `Volume`)
 * Migration/Replication (`VLUN`, `SRDF`)

## Options

You can get all command and few examples, with `-help` or `-h` option.

```
. || OPTIONS ||
.........................................
.
. General Options
. ---------------
. -help, -h            : Help
. -debug               : Debug Mode
. -verbose, -v         : Verbose Mode
. -nop                 : No Prompt
. -ulun                : Unbind Lun
. -nplun               : No Port Lun
. -force               : Force Flag
. -sid      [Arg]      : Bay SID
. -lun, -l  [Arg]      : Lun ID
. -luid     [Arg]      : Lun Unique ID
. -sg, -s   [Arg]      : S.Group
. -wwn, -w  [Arg]      : Login (WWN)
. -tmpsg    [Arg]      : Remove Tmp S.Group (Total)
. -name     [Arg]      : New Name
.
. Mode Selection
. --------------
. select, -x           : Select Mode
. info, -i             : Audit Mode
. remove, -r           : Remove Mode
. create, -c           : Create Mode
. modify, -m           : Modify Mode
. migrate, -mig        : Migrate Mode
.
. Audit Options
. -------------
. -only, -o            : Display Only Device Info
.
. Create Options
. --------------
. -nsg                 : New S.Group
. -nlun     [Arg]      : New Lun
. -nview    [Arg]      : New M.View
. -node     [Arg]      : Node Count (Df:1)
.
. Remove Options
. --------------
. -total, -t           : Total Remove
. -repli, -rep         : Only Replication Remove
.
. Migrate Options
. ---------------
. -rnsg                : Remote New S.Group
. -mtype    [Arg]      : Migration Type [VLUN|SRDF]
. -rsid     [Arg]      : Remote SID
. -rsg      [Arg]      : Remote S.Group
. -rlun     [Arg]      : Remote Lun
.
. Modify Options
. --------------
. -flag, -f [Arg]      : Flag to Modify [BCV|SRDF]
.
.
. || EXAMPLES ||
.........................................
.
. Audit Mode
. ----------
. vmax_utils.py -sid <SID> info -lun <L.ID>
. vmax_utils.py -sid <SID> info -sg <SG>
. vmax_utils.py -sid <SID> info -wwn <WWN>
. vmax_utils.py -sid <SID> info -luid <L.UID>
. vmax_utils.py -sid <SID> info -lun <L.ID> -o
.
. Create Mode
. -----------
. vmax_utils.py -sid <SID> create -nlun <N.LUN> -sg <SG>
. vmax_utils.py -sid <SID> create -nsg -name <SRV.N> -nlun <N.LUN>
. vmax_utils.py -sid <SID> create -nview <WWN> -nsg -name <SRV.N> -nlun <N.LUN>
. vmax_utils.py -sid <SID> create -nview [<NODE.N>]<WWN>-[<NODE.N>]<WWN> -sg <SG> -name <SRV.N>
.
. <-nlun> Syntax Example : 1x54,5x108:2
.
. Remove Mode
. -----------
. vmax_utils.py -sid <SID> remove -lun <L.ID>
. vmax_utils.py -sid <SID> remove -sg <SG>
. vmax_utils.py -sid <SID> remove -sg <SG> -total
.
. Migrate Mode
. ------------
. vmax_utils.py -sid <SID> migrate -mtype SRDF -lun <L.ID> -rsid <R.SID> -rsg <RN.NAME>
. vmax_utils.py -sid <SID> migrate -mtype SRDF -sg <SG> -rsid <R.SID> -rnsg -name <RN.NAME>
. vmax_utils.py -sid <SID> migrate -mtype SRDF -lun <L.ID> -rsid <R.SID> -rlun <RL.ID>
. vmax_utils.py -sid <SID> migrate -mtype VLUN -sg <SG>
.
. Modify Mode
. -----------
. vmax_utils.py -sid <SID> modify -flag BCV -lun <L.ID>
. vmax_utils.py -sid <SID> modify -flag SRDF -sg <SG>
.
```


## Operation

Here are some examples of use in situation.

By default all mode except info work on `dry-run`. That is, the user must validate to execute the commands (Yes/No).

However it is possible to add `-nop` option for skip that.

### Audit

Example of an audit on a `storage group` with a `cascaded initiator group` (CIG).

```
$ python vmax_utils.py -sid 0001 info -sg server01-02_SG
.
.  o-> Vmax.Utils Audit Mode - Start [17/07/18][14:20:01] <-o
.
. [C:0001] [ooooooooooooooo] 100% | (Check) S.Group(s)   [Done]
. [I:0001] [ooooooooooooooo] 100% | (Infos) S.Gr[Lun(s)] [Done]
. [I:0001] [ooooooooooooooo] 100% | (Infos) Device(s)    [Done]
. [I:0001] [ooooooooooooooo] 100% | (Infos) S.Group(s)   [Done]
. [I:0001] [ooooooooooooooo] 100% | (Infos) M.View(s)    [Done]
. [I:0001] [ooooooooooooooo] 100% | (Infos) Login(s)     [Done]
.
.
. [0001] Login(s) Information
.........................................
.
.  Name              P  Port Name     Log.In  On.Fab  Fcid    Port              IG[Nb]  MV[Nb]  CIG
.  ----------------- -- ------------- ------- ------- ------- ----------------- ------- ------- ----
.  1000000000012301  2  server01/fc1  Yes(2)  Yes(2)  b00006  FA-5H:0,FA-12H:0  Yes[1]  Yes[1]  Yes
.  1000000000012303  2  server02/fc1  Yes(2)  Yes(2)  b0000e  FA-6H:1,FA-11H:1  Yes[1]  Yes[2]  Yes
.  1000000000012302  2  server01/fc2  Yes(2)  Yes(2)  b0000f  FA-6H:1,FA-11H:1  Yes[1]  Yes[1]  Yes
.  1000000000012304  2  server02/fc2  Yes(2)  Yes(2)  b00002  FA-5H:0,FA-12H:0  Yes[1]  Yes[2]  Yes
[...]
.
.
. [0001] S.Group(s) Information
.........................................
.
.  <> Storage Group      : server01_SG
.     ~~~~~~~~~~~~~
.   Lun T.Size [T.Cnt]   : 2.8 TB [27]
.   Fast Policy          : Fast_1
.   Masking View [PG]    : server01-02_MV [FA_PG_1]
.    Casc. Init. Gr.     : server01-02_CIG
.     IG Child [WWN]     : server01_IG [1000000000012301|1000000000012302]
.     IG Child [WWN]     : server02_IG [1000000000012303|1000000000012304]
[...]
.
.     : S.Group(s) as Argument
.
.
. [0001] Device(s) Information
.........................................
.
. Total Size [T.Nb]  : 2.8 TB [27]
. Total Allocate     : 2.2 TB (79.1%)
. Total Written      : 2.2 TB (79.1%)
. Lun By Type        : 10x108:2, 16x108, 1x0
.
.  ID     Type     Size    Pool     S.Group         Clone  SRDF   BCV
.  ------ -------- ------- -------- --------------- ------ ------ ----
.  025FF  TDev     108 GB  Pool_02  server01-02_SG  No     No[C]  No
.  05395  Meta[2]  108 GB  Pool_02  server01-02_SG  No     No[C]  No
.  05397  Meta[2]  108 GB  Pool_02  server01-02_SG  No     No[C]  No
[...]
.
.  o-> Vmax.Utils Audit Mode - End [Time 00:00:12] [17/07/18][14:20:13] <-o
.
```


### Creation

Example of a creation of new `storage group` with his `masking view` + `volumes`.

```
$ python vmax_utils.py -sid 0001 create -nlun 12x108 -nsg -name server01 -nview 1000000000012301,1000000000012302
.
.  o-> Vmax.Utils Create Mode - Start [17/08/28][17:21:35] <-o
.
. [C:0001] [ooooooooooooooo] 100% | (Check) S.Group(s)   [Done]
. [I:0001] [ooooooooooooooo] 100% | (Infos) Login(s)     [Done]
. [C:0001] [ooooooooooooooo] 100% | (Check) M.View(s)    [Done]
. [C:0001] [ooooooooooooooo] 100% | (Infos) Login(s)     [Done]
. [I:0001] [ooooooooooooooo] 100% | (Infos) P.Group(s)   [Done]
. [I:0001] [ooooooooooooooo] 100% | (Infos) Fast.P(s)    [Done]
. [I:0001] [ooooooooooooooo] 100% | (Infos) Pool(s)      [Done]
.
.
. [0001] Login(s) Information
.........................................
.
.  Name              P  P.Name         Log In  On Fab  Fcid    Port              IG[Nb]  MV[Nb]  CIG
.  ----------------- -- -------------- ------- ------- ------- ----------------- ------- ------- ----
.  1000000000012301  2  server01/even  Yes(2)  Yes(2)  14f4c0  FA-8F:0,FA-10F:0  Yes[1]  No      No
.  1000000000012302  2  server01/odd   Yes(2)  Yes(2)  15f4c0  FA-7F:1,FA-9F:1   Yes[1]  No      No
.
.     Warning
.
.
. [0001] Pool(s) Information
.........................................
.
.  Name    Size     Us       Us%  Ov%  Ov%[+1.3 TB]  Silo      S.Us%  S.Ov%
.  ------- -------- -------- ---- ---- ------------- --------- ------ ------
.  Pool_1  40.4 TB  34.9 TB  86   96   99  [+3.1%]   01[Pl:2]  81     174
.  Pool_2  49.8 TB  38.5 TB  77   252  254 [+2.5%]   01[Pl:2]  81     174
.
.   Pool Selected : Pool_1
.
. (-) Select F.Policy (-)
.........................................
.
.    [1] -> Fast_Policy_1
.    [2] -> Fast_Policy_2
.    [3] -> Fast_Policy_3
.
. o-> Enter your Choice [Default : Fast_Policy_1]  :
.
.   F.Policy Selected : Fast_Policy_1
.
.
. Command(s) To Execute
.........................................
.
.  o-> Create New S.Group
.      ~~~~~~~~~~~~~~~~~~
. symaccess -sid 0001 create -name server01_SG -type storage
.
.  o-> Create Lun
.      ~~~~~~~~~~
. (-) Create File With Lun to Create
.
.   + create dev count=12, size=118976, emulation=fba, dynamic_capability=DYN_RDF, config=TDEV, binding to pool=Pool_1;
.
. symconfigure -sid 0001 -f ./file_temp_vmax_py_22954.tmp prepare -nop
. symconfigure -sid 0001 -f ./file_temp_vmax_py_22954.tmp commit -nop
.
.  o-> Add Lun(s) to S.Group
.      ~~~~~~~~~~~~~~~~~~~~~
. symaccess -sid 0001 add -name server01_SG -type storage dev [New Device]
.
.  o-> Add F.Policy to S.Group
.      ~~~~~~~~~~~~~~~~~~~~~~~
. symfast -sid 0001 associate -fp_name Fast_Policy_1 -sg server01_SG
.
.  o-> Rename Logins
.      ~~~~~~~~~~~~~
. symaccess -sid 0001 rename -wwn 1000000000012301 -alias server01/even
. symaccess -sid 0001 rename -wwn 1000000000012302 -alias server01/odd
.
.  o-> Create Init
.      ~~~~~~~~~~~
. symaccess -sid 0001 create -name server01_IG -type init
.
.  o-> Add init to C.Init
.      ~~~~~~~~~~~~~~~~~~
. symaccess -sid 0001 add -name server01_IG -type init -wwn 1000000000012301
. symaccess -sid 0001 add -name server01_IG -type init -wwn 1000000000012302
.
.  o-> Create M.View
.      ~~~~~~~~~~~~~
. symaccess -sid 0001 create view -name server01_MV -ig server01_IG -sg server01_SG -pg FA_PG_2
.
. o-> Do you Want Execute Command(s) ? [Yes|No]  :
[...]
```

### SRDF Migration

Example of a SRDF migration of 3 `volumes` to a remote `storage group`.

```
$ python vmax_utils.py -sid 0001 migrate -mtype srdf -lun 01ED8,01ED9,01EDA -rsid 0002 -rsg server01_target_SG
.
.  o-> Vmax.Utils Migrate Mode - Start [17/07/18][12:44:12] <-o
.
. [C:0001] [ooooooooooooooo] 100% | (Check) Device(s)    [Done]
. [I:0001] [ooooooooooooooo] 100% | (Infos) Device(s)    [Done]
. [I:0001] [ooooooooooooooo] 100% | (Infos) RA.Group(s)  [Done]
. [C:0002] [ooooooooooooooo] 100% | (Check) S.Group(s)   [Done]
. [I:0002] [ooooooooooooooo] 100% | (Infos) S.Group(s)   [Done]
. [I:0002] [ooooooooooooooo] 100% | (Infos) Fast.P(s)    [Done]
. [I:0002] [ooooooooooooooo] 100% | (Infos) Pool(s)      [Done]
.
.
. [0002] Pool(s) Information
.........................................
.
.  Name    Size     Us       Us%  Ov%  Ov%[+162.0 GB]  Silo      S.Us%  S.Ov%
.  ------- -------- -------- ---- ---- --------------- --------- ------ ------
.  Pool_1  36.0 TB  22.8 TB  63   112  112 [+0.4%]     03[Pl:2]  73     140
.  Pool_2  87.1 TB  74.0 TB  84   168  168 [+0.2%]     03[Pl:2]  73     140
.
.     Warn. Limit  : Pool_2:Ov>150%
.
. (-) Select Pool (-)
.........................................
.
.    [1] -> Pool_1
.    [2] ->  <!> Pool_2
.
. o-> Enter your Choice [Default : Pool_1]  :
.
.   Pool Selected : Pool_1
.
.
. [0001] RA.Group Information
.........................................
.
.  RA.ID(Local)  RA.ID(Remote)  Sym.ID(Remote)  FA.Port          FA.Cnt  Label
.  ------------- -------------- --------------- ---------------- ------- ----------
.  10            10             000295700002    RF-8H:0,RF-9H:0  2       0002_0001
.
.
. [0001] Device(s) Information [Local]
.........................................
.
. Total Size [T.Nb]  : 163.4 GB [3]
. Total Allocate     : 0.0 MB (0%)
. Total Written      : 3.0 MB (0%)
. Lun By Type        : 3x54
.
.  ID     Type  Size   Pool    S.Group      Clone  SRDF   BCV
.  ------ ----- ------ ------- ------------ ------ ------ ----
.  01ED8  TDev  54 GB  Pool_8  server01_SG  No     No[C]  No
.  01ED9  TDev  54 GB  Pool_8  server01_SG  No     No[C]  No
.  01EDA  TDev  54 GB  Pool_8  server01_SG  No     No[C]  No
.
.
. Command(s) To Execute
.........................................
.
.  o-> [Remote] Create Lun
.      ~~~~~~~~~~~~~~~~~~~
. Create File With Lun to Create [./vmax_py_57378.tmp]
.
.   + create dev count=3, size=59488, emulation=fba, dynamic_capability=DYN_RDF, config=TDEV, binding to pool=PL_SAS_03;
.
. symconfigure -sid 0002 -f ./vmax_py_57378.tmp prepare -nop
. symconfigure -sid 0002 -f ./vmax_py_57378.tmp commit -nop
.
.  o-> [Remote] Add Lun(s) to S.Group
.      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
. symaccess -sid 0002 add -name server01_target_SG -type storage dev [New Device]
.
.  o-> [Local] Create SRDF Replication
.      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
. Create File With Lun to Paired [RA:10, 0001(L):0002(R)][./vmax_py_57378.tmp] :
.
.   + 01ED8 [New Dev 001]
.   + 01ED9 [New Dev 002]
.   + 01EDA [New Dev 003]
.
. symrdf -sid 0001 -f ./vmax_py_57378.tmp -rdfg 10 createpair -establish -type rdf1 -rdf_mode acp_disk -nop
.
.
. o-> Do you Want Execute Command(s) ? [Yes|No]  : y
.
.
. Command(s) Execution Start
.........................................
.
.  o-> [Remote] Create Lun
.      ~~~~~~~~~~~~~~~~~~~
. Create File With Lun to Create [./vmax_py_57378.tmp]
.
. [13:39:53] symconfigure -sid 0002 -f ./vmax_py_57378.tmp prepare -nop [cmd OK]
. [13:40:34] symconfigure -sid 0002 -f ./vmax_py_57378.tmp commit -nop [cmd OK]
.
.  o-> [Remote] Add Lun(s) to S.Group
.      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
. [13:42:55] symaccess -sid 0002 add -name server01_target_SG -type storage dev 01674,01673,01672 [cmd OK]
.
. [I:0002] [ooooooooooooooo] 100% | (Infos) Device(s)    [Done]
.
.
. [0002] Device(s) Information [Remote]
.........................................
.
. Total Size [T.Nb]  : 163.4 GB [3]
. Total Allocate     : 0.0 MB (0%)
. Total Written      : 3.0 MB (0%)
. Lun By Type        : 3x54
.
.  ID     Type  Size   Pool    S.Group             Clone  SRDF   BCV
.  ------ ----- ------ ------- ------------------  ------ ------ ----
.  01674  TDev  54 GB  Pool_1  server01_target_SG  No     No[C]  No
.  01673  TDev  54 GB  Pool_1  server01_target_SG  No     No[C]  No
.  01672  TDev  54 GB  Pool_1  server01_target_SG  No     No[C]  No
.
.  o-> [Local] Create SRDF Replication
.      ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
. Create File With Lun to Paired [RA:10, 0001(L):0002(R)][./vmax_py_57378.tmp] :
.
. [13:43:23] symrdf -sid 0001 -f ./vmax_py_57378.tmp -rdfg 10 createpair -establish -type rdf1 -rdf_mode acp_disk -nop [cmd OK]
.
. [I:0001] [ooooooooooooooo] 100% | (Infos) Device(s)    [Done]
.
.
. [0001] Device(s) Information
.........................................
.
. Total Size [T.Nb]  : 163.4 GB [3]
. Total Allocate     : 0.0 MB (0%)
. Total Written      : 3.0 MB (0%)
. Lun By Type        : 3x54
.
.  ID     Type  Size   Pool    S.Group      Clone  SRDF                        BCV
.  ------ ----- ------ ------- ------------ ------ --------------------------- ----
.  01ED8  TDev  54 GB  Pool_8  server01_SG  No     R1:10[R2:0002:01674(Sync)]  No
.  01ED9  TDev  54 GB  Pool_8  server01_SG  No     R1:10[R2:0002:01673(Sync)]  No
.  01EDA  TDev  54 GB  Pool_8  server01_SG  No     R1:10[R2:0002:01672(Sync)]  No
.
.  o-> Vmax.Utils Migrate Mode - End [Time 00:03:36] [17/07/18][12:47:48] <-o
```
