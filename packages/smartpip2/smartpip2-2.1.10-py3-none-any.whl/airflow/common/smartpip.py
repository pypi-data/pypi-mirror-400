import os #line:2
import requests #line:3
import time #line:4
import json #line:5
import re #line:6
import subprocess #line:7
requests .packages .urllib3 .disable_warnings ()#line:10
from airflow .settings import ETL_FILE_PATH ,KETTLE_HOME ,HIVE_HOME ,P_URL ,DATASET_TOKEN ,REFRESH_TOKEN #line:12
from airflow .utils .email import fun_email ,list_email #line:13
from airflow .common .datax import datax_cmdStr ,flinkcdc_cmdStr #line:14
from airflow .exceptions import SmartpipException #line:15
from smart_chart .common .connect_db import DB_conn as connect_db_execute #line:16
_O0O0OO0000O0000OO =f'{P_URL}/echart/dataset_api/?token={DATASET_TOKEN}&visitor=Airflow&type='#line:19
_OOO0OO0O00OOOOOOO =f'{P_URL}/echart/refresh_ds/?token={REFRESH_TOKEN}&type='#line:20
_O0O0O0OO000O0000O =f'{P_URL}/dm/api/sync_tableQuality/?token={REFRESH_TOKEN}&project='#line:21
def smart_upload (O0OOOOO00OOOO0000 ):#line:25
    OO0OO00O0O00O0OO0 ,OO0O0OOO0OOOOOOO0 =os .path .split (O0OOOOO00OOOO0000 )#line:26
    OO0O0OOO0OOOOOOO0 =OO0O0OOO0OOOOOOO0 .split ('.')[0 ]#line:27
    O000OOO0O0000O0OO ={"title":OO0O0OOO0OOOOOOO0 ,"token":DATASET_TOKEN ,"visitor":"Airflow"}#line:32
    O00000OOO000O0000 ={'file':open (O0OOOOO00OOOO0000 ,'rb')}#line:33
    O0OO0O0OOO0O0O00O =f'''{P_URL}/echart/dataset_api/?type=uploadlog&visitor=Airflow&token={DATASET_TOKEN}&param={{"uptime":"{time.time()}","filename":"{OO0O0OOO0OOOOOOO0}"}}'''#line:34
    OO0O00O00OOOO0OO0 =60 #line:35
    O00OO000O0OOO000O =requests .post (f'{P_URL}/etl/api/upload_file_api/',files =O00000OOO000O0000 ,data =O000OOO0O0000O0OO ,verify =False )#line:37
    print (O00OO000O0OOO000O .status_code )#line:38
    if O00OO000O0OOO000O .status_code ==200 :#line:39
        O00OO000O0OOO000O =O00OO000O0OOO000O .json ()#line:40
    elif O00OO000O0OOO000O .status_code ==504 :#line:41
        print ('timeout, try waiting...')#line:42
        O00OO000O0OOO000O ={"result":"error","data":"time out"}#line:43
        for OO0000OO00000OOO0 in range (20 ):#line:44
            OOOO00OOO0O0O0OO0 =requests .get (O0OO0O0OOO0O0O00O ,verify =False ).json ()#line:45
            print (OOOO00OOO0O0O0OO0 )#line:46
            O000OOO0O0000O0OO =OOOO00OOO0O0O0OO0 ['data']#line:47
            if len (O000OOO0O0000O0OO )>1 :#line:48
                O00OO000O0OOO000O ={"result":"success","data":"uploaded"}#line:49
                break #line:50
            time .sleep (OO0O00O00OOOO0OO0 )#line:51
    else :#line:52
        O00OO000O0OOO000O ={"result":"error","data":"some thing wrong"}#line:53
    print (O00OO000O0OOO000O )#line:54
    if O00OO000O0OOO000O ['result']=='error':#line:55
        raise SmartpipException ('Upload Error')#line:56
def get_dataset (OOO000OOOO0O00000 ,param =None ):#line:59
    ""#line:65
    OOOO0OOOOOOO000OO =_O0O0OO0000O0000OO +str (OOO000OOOO0O00000 )#line:66
    if param :#line:67
        OOOO0OOOOOOO000OO =f'{OOOO0OOOOOOO000OO}&param={json.dumps(param)}'#line:68
    O0O0000O000O00O0O =requests .get (OOOO0OOOOOOO000OO ,verify =False )#line:69
    O0O0000O000O00O0O =O0O0000O000O00O0O .json ()#line:70
    return O0O0000O000O00O0O #line:71
def dataset (OOOOO00OO000O00O0 ,O0O0O00O0OOO0OOOO ,OO0O000OO00OOOOOO ,tolist =None ):#line:74
    ""#line:81
    O0O00O00O0O00O0OO =60 *15 #line:82
    O0OOOO0O0O0OOOO00 =3600 *2 #line:83
    O0000O0O00OOO00O0 =''#line:84
    try :#line:85
        while True :#line:86
            OOO0O0O00OOO0O0O0 =requests .get (_O0O0OO0000O0000OO +O0O0O00O0OOO0OOOO ,verify =False )#line:87
            OOO0O0O00OOO0O0O0 =OOO0O0O00OOO0O0O0 .json ()#line:88
            O0OO0OO0O0OO0O000 =OOO0O0O00OOO0O0O0 ['result']#line:89
            OOO0O0O00OOO0O0O0 =OOO0O0O00OOO0O0O0 ['data']#line:90
            if O0OO0OO0O0OO0O000 =='error':#line:91
                raise Exception (f'{OOO0O0O00OOO0O0O0}')#line:92
            O0000O0O00OOO00O0 =',\n'.join ([str (OOOO0O00O0OOO0O00 )for OOOO0O00O0OOO0O00 in OOO0O0O00OOO0O0O0 ])#line:93
            print (f'Dataset: {O0000O0O00OOO00O0} ')#line:94
            if OO0O000OO00OOOOOO =='e3':#line:95
                if len (OOO0O0O00OOO0O0O0 )<2 :#line:96
                    if O0OOOO0O0O0OOOO00 <=0 :#line:97
                        raise Exception ('超时且数据为空')#line:98
                    else :#line:99
                        time .sleep (O0O00O00O0O00O0OO )#line:100
                        O0OOOO0O0O0OOOO00 =O0OOOO0O0O0OOOO00 -O0O00O00O0O00O0OO #line:101
                else :#line:102
                    break #line:103
            else :#line:104
                if len (OOO0O0O00OOO0O0O0 )>1 :#line:105
                    if OO0O000OO00OOOOOO =='e1':#line:106
                        raise Exception ('有异常数据')#line:107
                    elif OO0O000OO00OOOOOO =='e2':#line:108
                        list_email (f'Info_{OOOOO00OO000O00O0}',f'{OOOOO00OO000O00O0}-Dataset Status',OOO0O0O00OOO0O0O0 ,to_list =tolist )#line:109
                else :#line:110
                    if OO0O000OO00OOOOOO not in ['info','e1']:#line:111
                        O0000O0O00OOO00O0 ='数据为空'#line:112
                        raise Exception (O0000O0O00OOO00O0 )#line:113
                break #line:114
    except Exception as OOOOO000O0O000O00 :#line:115
        fun_email (f'{OOOOO00OO000O00O0}-执行Dataset校验出错',O0000O0O00OOO00O0 ,to_list =tolist )#line:116
        raise SmartpipException (str (OOOOO000O0O000O00 .args ))#line:117
def refresh_dash (OOOOO0OO00O000O00 ,O0OO0000OO00O00O0 ):#line:120
    ""#line:123
    try :#line:124
        O000000OO00OO000O =requests .get (f'{_OOO0OO0O00OOOOOOO}{O0OO0000OO00O00O0}',verify =False )#line:125
        O000000OO00OO000O =O000000OO00OO000O .json ()#line:126
        print (O000000OO00OO000O )#line:127
        OO00O0O0O0O000OO0 =O000000OO00OO000O ['status']#line:128
        if OO00O0O0O0O000OO0 !=200 :#line:129
            raise SmartpipException ('refresh_dash')#line:130
    except Exception as OOOOOOOOO0OOOOOOO :#line:131
        fun_email (f'{OOOOO0OO00O000O00}-执行refresh出错',str (OOOOOOOOO0OOOOOOO .args ))#line:132
        raise SmartpipException (str (OOOOOOOOO0OOOOOOO .args ))#line:133
def refresh_quality (OO000OO0OO0000O0O ,OOOOO0O0O00O0OOO0 ,hours =1 ):#line:136
    ""#line:139
    try :#line:140
        O0OO0OOO00OOO0OO0 =requests .get (f'{_O0O0O0OO000O0000O}{OOOOO0O0O00O0OOO0}&hours={hours}',verify =False )#line:141
        O0OO0OOO00OOO0OO0 =O0OO0OOO00OOO0OO0 .json ()#line:142
        print (O0OO0OOO00OOO0OO0 )#line:143
        OOO00OO00000O0O00 =O0OO0OOO00OOO0OO0 ['status']#line:144
        if OOO00OO00000O0O00 !=200 :#line:145
            raise SmartpipException ('refresh_quality')#line:146
    except Exception as OO0O000O0OO0OO000 :#line:147
        fun_email (f'{OO000OO0OO0000O0O}-执行refresh_quality出错',str (OO0O000O0OO0OO000 .args ))#line:148
        raise SmartpipException (str (OO0O000O0OO0OO000 .args ))#line:149
def dash_mail (O0OO0OOO0O0OO0OO0 ,OO000O0O0O000OOO0 ,O000OO0O0000O00OO ):#line:152
    ""#line:156
    if callable (OO000O0O0O000OOO0 ):#line:157
        OOOOO0OOO0O0OO0O0 =OO000O0O0O000OOO0 ()#line:158
    else :#line:159
        OOOOO0OOO0O0OO0O0 =OO000O0O0O000OOO0 #line:160
    print (OOOOO0OOO0O0OO0O0 )#line:161
    if isinstance (OOOOO0OOO0O0OO0O0 ,str ):#line:162
        fun_email (O0OO0OOO0O0OO0OO0 ,OOOOO0OOO0O0OO0O0 ,O000OO0O0000O00OO )#line:163
    else :#line:164
        fun_email (OOOOO0OOO0O0OO0O0 [0 ],OOOOO0OOO0O0OO0O0 [1 ],O000OO0O0000O00OO )#line:165
    print ('发送邮件成功!')#line:166
def run_bash (OOOOO0000O0OO0O00 ):#line:170
    O000OO0OO00OOOOOO =''#line:171
    O0OO0OO0O000O0O00 =subprocess .Popen (OOOOO0000O0OO0O00 ,stdout =subprocess .PIPE ,stderr =subprocess .STDOUT ,shell =True ,cwd =ETL_FILE_PATH )#line:172
    print ('PID:',O0OO0OO0O000O0O00 .pid )#line:173
    for OO0O000OOO0O0OOO0 in iter (O0OO0OO0O000O0O00 .stdout .readline ,b''):#line:174
        if O0OO0OO0O000O0O00 .poll ()and OO0O000OOO0O0OOO0 ==b'':#line:175
            break #line:176
        OO0O000OOO0O0OOO0 =OO0O000OOO0O0OOO0 .decode (encoding ='utf8')#line:177
        print (OO0O000OOO0O0OOO0 .rstrip ())#line:178
        O000OO0OO00OOOOOO =O000OO0OO00OOOOOO +OO0O000OOO0O0OOO0 #line:179
    O0OO0OO0O000O0O00 .stdout .close ()#line:180
    O000O000000OOO0O0 =O0OO0OO0O000O0O00 .wait ()#line:181
    print ('result code: ',O000O000000OOO0O0 )#line:182
    return O000OO0OO00OOOOOO ,O000O000000OOO0O0 #line:183
def run_python (O0O000O00OOOO0O00 ,OO0000O0O00000O00 ,dev =''):#line:186
    O000OO000O0OO000O =O0O000O00OOOO0O00 .split ('/')#line:187
    _OOOOOOO00OO00000O ,OOOO0OO0OOOOOOOOO =run_bash ('python %s %s'%(O0O000O00OOOO0O00 ,OO0000O0O00000O00 ))#line:188
    if OOOO0OO0OOOOOOOOO !=0 :#line:189
        fun_email (f'{O000OO000O0OO000O[-2]}/{O000OO000O0OO000O[-1]}出错','python error')#line:190
        raise SmartpipException ('python error')#line:191
def run_dataxx (O0O0OOOO0OO0000OO ,OOOO0OO0OO0000O00 ,dev =''):#line:195
    if not O0O0OOOO0OO0000OO .startswith (os .path .sep ):#line:196
        O0O0OOOO0OO0000OO =os .path .join (ETL_FILE_PATH ,O0O0OOOO0OO0000OO )#line:197
    O00O0O00O00OOOOO0 =O0O0OOOO0OO0000OO .split ('/')#line:198
    if OOOO0OO0OO0000O00 :#line:199
        O0O00O0O0O0O000O0 =[f'-D{O00O0O000OOOOO0O0}:{O0OOO00OO0000OOO0}'for O00O0O000OOOOO0O0 ,O0OOO00OO0000OOO0 in OOOO0OO0OO0000O00 .items ()]#line:200
        OOO00O0OO0OOOOOO0 =' '.join (O0O00O0O0O0O000O0 )#line:201
        O0O00OO0OOO0O000O =[f'-p"{OOO00O0OO0OOOOOO0}"',O0O0OOOO0OO0000OO ]#line:202
    else :#line:203
        O0O00OO0OOO0O000O =[O0O0OOOO0OO0000OO ]#line:204
    O00O000O0O0000000 =datax_cmdStr (O0O00OO0OOO0O000O )#line:205
    _O0O00OOO0OO0O0O0O ,OOO0OOOOO0OO0O00O =run_bash (O00O000O0O0000000 )#line:206
    if OOO0OOOOO0OO0O00O !=0 :#line:207
        fun_email (f'{O00O0O00O00OOOOO0[-2]}/{O00O0O00O00OOOOO0[-1]}出错','datax error')#line:208
        raise SmartpipException ('error')#line:209
def run_datax (O000OO0O0OO0O0OO0 ,OO0OOO0O00O0OO0OO ,OO0000OO0OO0OOO0O ,O000OO00OOOO0OO0O ,dev =''):#line:212
    if not O000OO0O0OO0O0OO0 .startswith (os .path .sep ):#line:213
        O000OO0O0OO0O0OO0 =os .path .join (ETL_FILE_PATH ,O000OO0O0OO0O0OO0 +'.sql')#line:214
    with open (O000OO0O0OO0O0OO0 ,'r',encoding ='utf8')as O00OO000O0O0O00O0 :#line:215
        OOOOOO0OO0000000O =readSqlstr (O00OO000O0O0O00O0 .read ().strip (),para_dict =O000OO00OOOO0OO0O )#line:216
    OOOOOO0OO0000000O =OOOOOO0OO0000000O .split ('##')#line:217
    OOOOO0O00O0OOOO0O ={}#line:218
    for O0O00OO00OO000000 in OOOOOO0OO0000000O :#line:219
        OOOO000O00O00OOO0 =O0O00OO00OO000000 .find ('=')#line:220
        if OOOO000O00O00OOO0 >0 :#line:221
            OOOOO0O00O0OOOO0O [O0O00OO00OO000000 [:OOOO000O00O00OOO0 ].strip ()]=O0O00OO00OO000000 [OOOO000O00O00OOO0 +1 :].replace ('\n',' ').strip ()#line:222
    OO0OOOOOOO0O00OOO =OOOOO0O00O0OOOO0O .keys ()#line:223
    if 'incColumn'in OO0OOOOOOO0O00OOO :#line:224
        OOOO0OOO000OO0O0O =OOOOO0O00O0OOOO0O .pop ('incColumn')#line:225
        OO0OOO00O0OO0O00O =OOOOO0O00O0OOOO0O .pop ('incDB')if 'incDB'in OO0OOOOOOO0O00OOO else 'starrocks'#line:226
        if OOOO0OOO000OO0O0O :#line:227
            OO000000O0000O000 =_OO0OOO00OO00OO0O0 (f"select max({OOOO0OOO000OO0O0O}) from {OOOOO0O00O0OOOO0O['targetTable']}",OO0OOO0O00O0OO0OO ,db_connect =OO0OOO00O0OO0O00O ,dev =dev )#line:229
            print ('GET PARAM',OO000000O0000O000 )#line:230
            OO00O0OO000O0OO00 =0 #line:231
            if len (OO000000O0000O000 )>1 :#line:232
                if OO000000O0000O000 [1 ][0 ]is not None :#line:233
                    OO00O0OO000O0OO00 =OO000000O0000O000 [1 ][0 ]#line:234
            OOOOO0O00O0OOOO0O ['querySql']=readSqlstr (OOOOO0O00O0OOOO0O ['querySql'],para_dict ={OOOO0OOO000OO0O0O :OO00O0OO000O0OO00 })#line:235
    O00O0000O0OO00OO0 =OOOOO0O00O0OOOO0O .pop ('template')if 'template'in OO0OOOOOOO0O00OOO else 'default'#line:237
    OOO00OO0OO000OOO0 =OOOOO0O00O0OOOO0O .get ('targetColumn')#line:238
    O0000O0O000O00O0O =None #line:239
    if O00O0000O0OO00OO0 .endswith ('hdfs'):#line:240
        O0000O0O000O00O0O =OOOOO0O00O0OOOO0O .pop ('hiveSql')if 'hiveSql'in OO0OOOOOOO0O00OOO else None #line:242
        if not O0000O0O000O00O0O :#line:243
            O0000O0O000O00O0O =OOOOO0O00O0OOOO0O .pop ('postSql')if 'postSql'in OO0OOOOOOO0O00OOO else None #line:244
        if OOO00OO0OO000OOO0 :#line:246
            OOO00OO0OO000OOO0 =OOO00OO0OO000OOO0 .split (',')#line:247
            OO0OOO00OOOO00O00 =[]#line:248
            for O0O00OO00OO000000 in OOO00OO0OO000OOO0 :#line:249
                if ':'in O0O00OO00OO000000 :#line:250
                    O0O00OO00OO000000 =O0O00OO00OO000000 .split (':')#line:251
                    OO0OOO00OOOO00O00 .append ({"name":O0O00OO00OO000000 [0 ].strip (),"type":O0O00OO00OO000000 [1 ].strip ()})#line:252
                else :#line:253
                    OO0OOO00OOOO00O00 .append ({"name":O0O00OO00OO000000 .strip (),"type":"STRING"})#line:254
            OOOOO0O00O0OOOO0O ['targetColumn']=json .dumps (OO0OOO00OOOO00O00 )#line:255
    else :#line:256
        if OOO00OO0OO000OOO0 :#line:257
            OOO00OO0OO000OOO0 =[O00O0O0O00OO0O0O0 .strip ()for O00O0O0O00OO0O0O0 in OOO00OO0OO000OOO0 .split (',')]#line:258
            OOOOO0O00O0OOOO0O ['targetColumn']=json .dumps (OOO00OO0OO000OOO0 )#line:259
        else :#line:260
            OOOOO0O00O0OOOO0O ['targetColumn']='["*"]'#line:261
        if O00O0000O0OO00OO0 .endswith ('starrocks'):#line:263
            if '.'in OOOOO0O00O0OOOO0O ['targetTable']:#line:264
                OOOOO0O00O0OOOO0O ['targetDB'],OOOOO0O00O0OOOO0O ['targetTable']=OOOOO0O00O0OOOO0O ['targetTable'].split ('.')#line:265
            else :#line:266
                OOOOO0O00O0OOOO0O ['targetDB']='Test'#line:267
        else :#line:268
            if 'writeMode'not in OO0OOOOOOO0O00OOO :#line:269
                OOOOO0O00O0OOOO0O ['writeMode']='insert'#line:270
    if 'preSql'in OO0OOOOOOO0O00OOO :#line:271
        OOOOO0O00O0OOOO0O ['preSql']=json .dumps (OOOOO0O00O0OOOO0O ['preSql'].strip ().split (';'))#line:272
    else :#line:273
        OOOOO0O00O0OOOO0O ['preSql']=''#line:274
    if 'postSql'in OO0OOOOOOO0O00OOO :#line:275
        OOOOO0O00O0OOOO0O ['postSql']=json .dumps (OOOOO0O00O0OOOO0O ['postSql'].strip ().split (';'))#line:276
    else :#line:277
        OOOOO0O00O0OOOO0O ['postSql']=''#line:278
    O00000O00O0OOO0OO =O000OO0O0OO0O0OO0 .split ('/')#line:279
    OOO0OO0OO0OOOOO0O =O00000O00O0OOO0OO [-1 ].split ('.')[0 ]#line:280
    with open (os .path .join (OO0000OO0OO0OOO0O ,'datax','templates',O00O0000O0OO00OO0 ),'r')as O00OO000O0O0O00O0 :#line:281
        O0OOOO00O0OOO0O00 =O00OO000O0O0O00O0 .read ()#line:282
    O000OO0O0OO0O0OO0 =os .path .join (OO0000OO0OO0OOO0O ,'datax',OOO0OO0OO0OOOOO0O +'.json')#line:283
    with open (O000OO0O0OO0O0OO0 ,'w',encoding ='utf8')as O00OO000O0O0O00O0 :#line:284
        O00OO000O0O0O00O0 .write (readSqlstr (O0OOOO00O0OOO0O00 ,OOOOO0O00O0OOOO0O ))#line:285
    OOOO0O00OO0000O00 =datax_cmdStr ([O000OO0O0OO0O0OO0 ])#line:286
    _O0OOO0O00000OOO00 ,OO000000O0000O000 =run_bash (OOOO0O00OO0000O00 )#line:287
    if OO000000O0000O000 !=0 :#line:288
        fun_email (f'{O00000O00O0OOO0OO[-2]}/{O00000O00O0OOO0OO[-1]}出错','datax error')#line:289
        raise SmartpipException ('datax error')#line:290
    if O0000O0O000O00O0O :#line:291
        _OO0OOO00OO00OO0O0 (O0000O0O000O00O0O ,OO0OOO0O00O0OO0OO ,db_connect ='hive',dev =dev )#line:292
def run_flinkcdc (O00O000O0OOO000O0 ,O00O0OOO000O0O0OO ,O00OOOOOOO00OO0O0 ,OOOO0OO0OOO00000O ,dev =''):#line:1
    if not O00O000O0OOO000O0 .startswith (os .path .sep ):#line:2
        O00O000O0OOO000O0 =os .path .join (ETL_FILE_PATH ,O00O000O0OOO000O0 +'.sql')#line:3
    with open (O00O000O0OOO000O0 ,'r',encoding ='utf8')as OO0O00O0OOO000000 :#line:4
        O0000O0OOO000OO00 =readSqlstr (OO0O00O0OOO000000 .read ().strip (),para_dict =OOOO0OO0OOO00000O )#line:5
    O0000O0OOO000OO00 =O0000O0OOO000OO00 .split ('##')#line:6
    O0O00OO00OO000O0O ={}#line:7
    for OOO00000O00OOO00O in O0000O0OOO000OO00 :#line:8
        OOOOOO00O0OO000O0 =OOO00000O00OOO00O .find ('=')#line:9
        if OOOOOO00O0OO000O0 >0 :#line:10
            O0O00OO00OO000O0O [OOO00000O00OOO00O [:OOOOOO00O0OO000O0 ].strip ()]=OOO00000O00OOO00O [OOOOOO00O0OO000O0 +1 :].strip ()#line:11
    OO0000O000O00OOOO =O0O00OO00OO000O0O ['name']#line:12
    OO000O00O00OOOOOO =O00O0OOO000O0O0OO .get ('flink','http://localhost:8081/jobs/overview/')#line:13
    O00OOO00OO0000O0O =requests .get (OO000O00O00OOOOOO ).json ()['jobs']#line:14
    for OOO00000O00OOO00O in O00OOO00OO0000O0O :#line:15
        if OO0000O000O00OOOO ==OOO00000O00OOO00O ['name']:#line:16
            print (OOO00000O00OOO00O )#line:17
            if OOO00000O00OOO00O ['status']=='RUNNING':#line:18
                return #line:19
            elif OOO00000O00OOO00O ['status']not in ["CANCELED","FINISHED"]:#line:20
                raise SmartpipException ('flinkcdc monitor error')#line:21
    O0OOOO0O00O0000OO =O0O00OO00OO000O0O .keys ()#line:23
    OO0OOOOOO00OO0000 =O0O00OO00OO000O0O .pop ('template')if 'template'in O0OOOO0O00O0000OO else 'default'#line:24
    O0OO00O0000O0O0O0 =O00O000O0OOO000O0 .split ('/')#line:25
    OOOO00000O0OOOOO0 =O0OO00O0000O0O0O0 [-1 ].split ('.')[0 ]#line:26
    with open (os .path .join (O00OOOOOOO00OO0O0 ,'datax','templates',OO0OOOOOO00OO0000 ),'r')as OO0O00O0OOO000000 :#line:27
        OO00000O0000000O0 =OO0O00O0OOO000000 .read ()#line:28
    O00O000O0OOO000O0 =os .path .join (O00OOOOOOO00OO0O0 ,'datax',OOOO00000O0OOOOO0 +'.yaml')#line:29
    with open (O00O000O0OOO000O0 ,'w',encoding ='utf8')as OO0O00O0OOO000000 :#line:30
        OO0O00O0OOO000000 .write (readSqlstr (OO00000O0000000O0 ,O0O00OO00OO000O0O ))#line:31
    OO0O000000O0OO0OO =flinkcdc_cmdStr ([O00O000O0OOO000O0 ])#line:32
    _OO00O0OO00O0OOOO0 ,OO0O00000O00OOOO0 =run_bash (OO0O000000O0OO0OO )#line:33
    if OO0O00000O00OOOO0 !=0 :#line:34
        fun_email (f'{O0OO00O0000O0O0O0[-2]}/{O0OO00O0000O0O0O0[-1]}出错','flinkcdc error')#line:35
        raise SmartpipException ('flinkcdc error')
def readSqlFile (O0O000OOOO000O0OO ,para_dict =None ):#line:322
    if O0O000OOOO000O0OO .find ('.sql')<0 :#line:323
        return 'file type error'#line:324
    with open (O0O000OOOO000O0OO ,'r',encoding ='utf-8')as O000000000OO0000O :#line:325
        OO00OO0OO0OO0O00O =O000000000OO0000O .read ()#line:326
    OO0OO0OOO00OO000O =readSqlstr (OO00OO0OO0OO0O00O ,para_dict )#line:327
    return OO0OO0OOO00OO000O #line:328
def readSqoopFile (O0O00O00OO00O0OO0 ,para_dict =None ):#line:331
    if not O0O00O00OO00O0OO0 .endswith ('.sql'):#line:332
        return 'file type error'#line:333
    with open (O0O00O00OO00O0OO0 ,'r',encoding ='utf8')as O0OO0OOO0O00O0O0O :#line:334
        O0O0O0O0O00O00O0O =O0OO0OOO0O00O0O0O .read ().strip ()#line:335
    OO00000000OO0OO0O =re .match (r"/\*(.*?)\*/(.+)",O0O0O0O0O00O00O0O ,re .M |re .S )#line:336
    OOOO00O00OO0O0OO0 =readSqlstr (OO00000000OO0OO0O .group (1 ).strip (),para_dict )#line:337
    O0O0O00O0OO0000O0 =OO00000000OO0OO0O .group (2 ).strip ()#line:338
    return OOOO00O00OO0O0OO0 ,O0O0O00O0OO0000O0 #line:339
def readSqlstr (O00OO000OO0OOO0OO ,para_dict =None ):#line:342
    OOOO0O000OO0OO0O0 =re .sub (r"(\/\*(.|\n)*?\*\/)|--.*",'',O00OO000OO0OOO0OO .strip ())#line:343
    if para_dict :#line:344
        for O0000OO00000OOO0O ,OO000O000OO0000O0 in para_dict .items ():#line:345
            if O0000OO00000OOO0O .isnumeric ():#line:346
                OOOO000O0O0O0OO0O =get_dataset (OO000O000OO0000O0 )#line:347
                print ('dataset:',OOOO000O0O0O0OO0O )#line:348
                if OOOO000O0O0O0OO0O ['result']!='success':#line:349
                    raise SmartpipException (OOOO000O0O0O0OO0O ['data'])#line:350
                else :#line:351
                    OOOO000O0O0O0OO0O =OOOO000O0O0O0OO0O ['data']#line:352
                if len (OOOO000O0O0O0OO0O )>1 :#line:353
                    for OO000OO0OO0O00000 ,OOOOO0OO000000O00 in zip (OOOO000O0O0O0OO0O [0 ],OOOO000O0O0O0OO0O [1 ]):#line:354
                        OOOO0O000OO0OO0O0 =OOOO0O000OO0OO0O0 .replace ('$'+OO000OO0OO0O00000 ,str (OOOOO0OO000000O00 ))#line:355
            elif callable (OO000O000OO0000O0 ):#line:356
                OOO0OO0O000OO00O0 =OO000O000OO0000O0 ()#line:357
                for OO000OO0OO0O00000 ,OOOOO0OO000000O00 in OOO0OO0O000OO00O0 .items ():#line:358
                    OOOO0O000OO0OO0O0 =OOOO0O000OO0OO0O0 .replace ('$'+OO000OO0OO0O00000 ,str (OOOOO0OO000000O00 ))#line:359
            else :#line:360
                OOOO0O000OO0OO0O0 =OOOO0O000OO0OO0O0 .replace ('$'+O0000OO00000OOO0O ,str (OO000O000OO0000O0 ))#line:361
    return OOOO0O000OO0OO0O0 #line:362
def run_sql_file (O00000O0OO000O0O0 ,OOOO00000000000OO ,db_connect ='starrocks',para_dict =None ,dev =''):#line:365
    if not O00000O0OO000O0O0 .startswith (os .path .sep ):#line:366
        O00000O0OO000O0O0 =os .path .join (ETL_FILE_PATH ,O00000O0OO000O0O0 +'.sql')#line:367
    O00O0OOO00O0OOO00 =O00000O0OO000O0O0 .split ('/')#line:368
    try :#line:369
        OO000O0OOOOOO0O00 =readSqlFile (O00000O0OO000O0O0 ,para_dict ).split (';')#line:370
        O00O00000O00O0O00 =OOOO00000000000OO .get (db_connect )#line:371
        if dev :#line:372
            if f'{db_connect}{dev}'in OOOO00000000000OO .keys ():#line:373
                O00O00000O00O0O00 =OOOO00000000000OO .get (f'{db_connect}{dev}')#line:374
        O00O00000O00O0O00 ['dbtype']=db_connect #line:375
        O000OO0OOO0OO00O0 =connect_db_execute ().execute_sql_list (OO000O0OOOOOO0O00 ,connect_dict =O00O00000O00O0O00 )#line:376
        return O000OO0OOO0OO00O0 #line:377
    except Exception as OO0O0O0OO000O000O :#line:378
        fun_email ('{}/{}执行出错'.format (O00O0OOO00O0OOO00 [-2 ],O00O0OOO00O0OOO00 [-1 ]),str (OO0O0O0OO000O000O ))#line:379
        raise SmartpipException (str (OO0O0O0OO000O000O ))#line:380
def _OO0OOO00OO00OO0O0 (O000OO0O000O00000 ,OOOOO00OO0OOO0O0O ,db_connect ='starrocks',para_dict =None ,dev =''):#line:383
    try :#line:384
        if isinstance (O000OO0O000O00000 ,str ):#line:385
            O000OO0O000O00000 =readSqlstr (O000OO0O000O00000 ,para_dict ).split (';')#line:386
        O00O0OOO0OOOOOO0O =OOOOO00OO0OOO0O0O .get (db_connect )#line:387
        if dev :#line:388
            if f'{db_connect}{dev}'in OOOOO00OO0OOO0O0O .keys ():#line:389
                O00O0OOO0OOOOOO0O =OOOOO00OO0OOO0O0O .get (f'{db_connect}{dev}')#line:390
        O00O0OOO0OOOOOO0O ['dbtype']=db_connect #line:391
        O00OO0OO00OOOOO00 =connect_db_execute ().execute_sql_list (O000OO0O000O00000 ,connect_dict =O00O0OOO0OOOOOO0O )#line:392
        return O00OO0OO00OOOOO00 #line:393
    except Exception as OO00OO00O0OOOO0O0 :#line:394
        fun_email ('SQL执行出错',f'{O000OO0O000O00000}{OO00OO00O0OOOO0O0}')#line:395
        raise SmartpipException (str (OO00OO00O0OOOO0O0 ))#line:396
def run_sp (OO0O000O00O00O00O ,O0O0O0O0OO0OO0O0O ,db_connect ='oracle',sp_para =None ,dev =''):#line:399
    try :#line:400
        O00OOOO000O0O0OO0 =O0O0O0O0OO0OO0O0O .get (db_connect )#line:401
        if dev :#line:402
            if f'{db_connect}{dev}'in O0O0O0O0OO0OO0O0O .keys ():#line:403
                O00OOOO000O0O0OO0 =O0O0O0O0OO0OO0O0O .get (f'{db_connect}{dev}')#line:404
        connect_db_execute ().excute_proc (OO0O000O00O00O00O ,sp_para ,O00OOOO000O0O0OO0 )#line:405
    except Exception as O000OOO00O00O000O :#line:406
        fun_email ('{}执行出错'.format (OO0O000O00O00O00O ),str (O000OOO00O00O000O ))#line:407
        raise SmartpipException (str (O000OOO00O00O000O ))#line:408
def run_kettle (OO0O0O000OOO0OOOO ,para_str ='',dev =False ):#line:412
    ""#line:419
    if not OO0O0O000OOO0OOOO .startswith (os .path .sep ):#line:420
        OO0O0O000OOO0OOOO =os .path .join (ETL_FILE_PATH ,OO0O0O000OOO0OOOO )#line:421
    OOO000O0000O0OO00 =OO0O0O000OOO0OOOO .split ('/')#line:422
    print ('kettle job start')#line:423
    if '.ktr'in OO0O0O000OOO0OOOO :#line:425
        OOO0O00000OO00O0O =f'{KETTLE_HOME}/pan.sh -level=Basic -file={OO0O0O000OOO0OOOO}{para_str}'#line:426
    else :#line:427
        OOO0O00000OO00O0O =f'{KETTLE_HOME}/kitchen.sh -level=Basic -file={OO0O0O000OOO0OOOO}{para_str}'#line:428
    print (OOO0O00000OO00O0O )#line:429
    OOOO00O00OO0O00O0 ,OO0OO00O0O0O000O0 =run_bash (OOO0O00000OO00O0O )#line:433
    if OO0OO00O0O0O000O0 ==0 or (OOOO00O00OO0O00O0 .find ('(result=[false])')==-1 and (OOOO00O00OO0O00O0 .find ('ended successfully')>0 or OOOO00O00OO0O00O0 .find ('result=[true]')>0 )):#line:435
        print ('{} 完成数据抽取'.format (str (OO0O0O000OOO0OOOO )))#line:436
    else :#line:437
        print ('{} 执行错误'.format (OO0O0O000OOO0OOOO ))#line:438
        fun_email ('{}/{}出错'.format (OOO000O0000O0OO00 [-2 ],OOO000O0000O0OO00 [-1 ]),str (OOOO00O00OO0O00O0 ))#line:439
        raise SmartpipException ('Run Kettle Error')#line:440
def hdfsStarrocks (OOOOO00O00O000000 ,OOO00OOOO00000O0O ,para_dict =None ):#line:444
    ""#line:448
    O0OOO0OOOO0O0O00O =OOOOO00O00O000000 .split ('/')#line:449
    print ('starrocks load job start')#line:450
    OOO00O0OOOO0O0O0O ,O0OOOO00O0O0OO0OO =readSqoopFile (OOOOO00O00O000000 ,para_dict =para_dict )#line:451
    OOO00O0OOOO0O0O0O =OOO00O0OOOO0O0O0O .split ('\n')#line:452
    O00O0000OO00OOOOO ={'LABEL':f'{O0OOO0OOOO0O0O00O[-2]}{O0OOO0OOOO0O0O00O[-1][:-4]}{int(time.time())}','HDFS':HIVE_HOME }#line:453
    for OOO000000O0OO0OOO in OOO00O0OOOO0O0O0O :#line:454
        OOO00O000OO00O0O0 =OOO000000O0OO0OOO .find ('=')#line:455
        if OOO00O000OO00O0O0 >0 :#line:456
            O00O0000OO00OOOOO [OOO000000O0OO0OOO [:OOO00O000OO00O0O0 ].strip ()]=OOO000000O0OO0OOO [OOO00O000OO00O0O0 +1 :].strip ()#line:457
    O00000OO0O0OOOOO0 =O00O0000OO00OOOOO .get ('sleepTime')#line:459
    if O00000OO0O0OOOOO0 :#line:460
        O00000OO0O0OOOOO0 =int (O00000OO0O0OOOOO0 )#line:461
        if O00000OO0O0OOOOO0 <30 :#line:462
            O00000OO0O0OOOOO0 =30 #line:463
    else :#line:464
        O00000OO0O0OOOOO0 =30 #line:465
    O00O0O000OO0OO0OO =O00O0000OO00OOOOO .get ('maxTime')#line:467
    if O00O0O000OO0OO0OO :#line:468
        O00O0O000OO0OO0OO =int (O00O0O000OO0OO0OO )#line:469
        if O00O0O000OO0OO0OO >3600 :#line:470
            O00O0O000OO0OO0OO =3600 #line:471
    else :#line:472
        O00O0O000OO0OO0OO =600 #line:473
    _OO0OOO00OO00OO0O0 (O0OOOO00O0O0OO0OO ,OOO00OOOO00000O0O ,db_connect ='starrocks',para_dict =O00O0000OO00OOOOO )#line:475
    time .sleep (O00000OO0O0OOOOO0 )#line:476
    OOOO0OO0000OO0O0O =f'''show load from {O00O0000OO00OOOOO.get('targetDB')} where label = '{O00O0000OO00OOOOO['LABEL']}' order by CreateTime desc limit 1 '''#line:477
    OO0O0000O0O0000OO ='start to check label'#line:478
    try :#line:479
        while True :#line:480
            OO0O0000O0O0000OO =_OO0OOO00OO00OO0O0 ([OOOO0OO0000OO0O0O ],OOO00OOOO00000O0O ,db_connect ='starrocks')#line:481
            print (OO0O0000O0O0000OO )#line:482
            OOOOOOOOO0OO00O0O =OO0O0000O0O0000OO [1 ][2 ]#line:483
            if OOOOOOOOO0OO00O0O =='CANCELLED':#line:484
                raise Exception (f'Starrocks:{OOOOOOOOO0OO00O0O}')#line:485
            elif OOOOOOOOO0OO00O0O =='FINISHED':#line:486
                print ('Load completed')#line:487
                break #line:488
            if O00O0O000OO0OO0OO <=0 :#line:489
                raise Exception ('超时未完成')#line:490
            else :#line:491
                time .sleep (O00000OO0O0OOOOO0 )#line:492
                O00O0O000OO0OO0OO =O00O0O000OO0OO0OO -O00000OO0O0OOOOO0 #line:493
    except Exception as O00OO0OOOO0OOO00O :#line:494
        print ('{} 执行错误'.format (OOOOO00O00O000000 ))#line:495
        fun_email ('{}/{}执行出错'.format (O0OOO0OOOO0O0O00O [-2 ],O0OOO0OOOO0O0O00O [-1 ]),str (OO0O0000O0O0000OO ))#line:496
        raise SmartpipException (str (O00OO0OOOO0OOO00O .args ))#line:497
def kafkaStarrocks (O00O0O0OO0OO0O0OO ,O0OOO0O00OO00O000 ,OOO00OOOO00OO0O0O ,O0O0OO0O000O0OO0O ,O00OOO0OO0OO0O0OO ,dev =''):#line:500
    with open (O00O0O0OO0OO0O0OO ,'r',encoding ='utf8')as OOO00OO000O000OOO :#line:501
        OOOOO0O0O00OO0OOO =readSqlstr (OOO00OO000O000OOO .read ().strip (),para_dict =O00OOO0OO0OO0O0OO )#line:502
    OOOOO0O0O00OO0OOO =OOOOO0O0O00OO0OOO .split ('##')#line:503
    OO0OOO00OO000OOOO ={}#line:504
    for OOOO00000O00OOO00 in OOOOO0O0O00OO0OOO :#line:505
        OO0O00O00O0OO0OO0 =OOOO00000O00OOO00 .find ('=')#line:506
        if OO0O00O00O0OO0OO0 >0 :#line:507
            OOOOOOOO0O0O0O0O0 =OOOO00000O00OOO00 [OO0O00O00O0OO0OO0 +1 :].replace ('\n',' ').strip ()#line:508
            if OOOOOOOO0O0O0O0O0 :#line:509
                OO0OOO00OO000OOOO [OOOO00000O00OOO00 [:OO0O00O00O0OO0OO0 ].strip ()]=OOOOOOOO0O0O0O0O0 #line:510
    OOOOO0OOOO0OOOO0O =OO0OOO00OO000OOOO .pop ('topic')#line:511
    OOO000O0OO0OO000O =OO0OOO00OO000OOOO .pop ('table')#line:512
    O000OOOOOO000OOO0 =OO0OOO00OO000OOOO .keys ()#line:513
    if 'skipError'in O000OOOOOO000OOO0 :#line:514
        skipError =OO0OOO00OO000OOOO .pop ('skipError')#line:515
    else :#line:516
        skipError =None #line:517
    if 'kafkaConn'in O000OOOOOO000OOO0 :#line:518
        O000O00000OO0OO0O =OO0OOO00OO000OOOO .pop ('kafkaConn')#line:519
    else :#line:520
        O000O00000OO0OO0O ='default'#line:521
    if 'offsets'in O000OOOOOO000OOO0 :#line:522
        OO00O0OO0OO00O00O =json .loads (OO0OOO00OO000OOOO .pop ('offsets'))#line:523
    else :#line:524
        OO00O0OO0OO00O00O =None #line:525
    if 'json_root'in O000OOOOOO000OOO0 :#line:526
        OOO0O0OO00O0O0O00 =OO0OOO00OO000OOOO .pop ('json_root')#line:527
    else :#line:528
        OOO0O0OO00O0O0O00 =None #line:529
    if 'jsonpaths'in O000OOOOOO000OOO0 :#line:530
        O000O0OO00O00O0O0 =OO0OOO00OO000OOOO .get ('jsonpaths')#line:531
        if not O000O0OO00O00O0O0 .startswith ('['):#line:532
            O000O0OO00O00O0O0 =O000O0OO00O00O0O0 .split (',')#line:533
            O000O0OO00O00O0O0 =json .dumps (['$.'+OOOOOO0OOOO0O0000 .strip ()for OOOOOO0OOOO0O0000 in O000O0OO00O00O0O0 ])#line:534
            OO0OOO00OO000OOOO ['jsonpaths']=O000O0OO00O00O0O0 #line:535
    O0O0O0O0OO0000O0O =_O0OOO00OOOOOO0O00 (OOOOO0OOOO0OOOO0O ,O0OOO0O00OO00O000 [O000O00000OO0OO0O ],O0O0OO0O000O0OO0O ,OO00O0OO0OO00O00O )#line:536
    def O0O00OO0O00OO0O0O (O0000O00O00OO00O0 ):#line:538
        O000OO0OOO0O0000O =b''#line:539
        O000OO00OOOOO00O0 =None #line:540
        if 'format'in O000OOOOOO000OOO0 :#line:541
            for O000OO00OOOOO00O0 in O0000O00O00OO00O0 :#line:542
                O0O0OO0O0O0OOO00O =O000OO00OOOOO00O0 .value #line:543
                if OOO0O0OO00O0O0O00 :#line:544
                    O0O0OO0O0O0OOO00O =json .loads (O0O0OO0O0O0OOO00O .decode ('utf8'))#line:545
                    O0O0OO0O0O0OOO00O =json .dumps (O0O0OO0O0O0OOO00O [OOO0O0OO00O0O0O00 ]).encode ('utf8')#line:546
                if O0O0OO0O0O0OOO00O .startswith (b'['):#line:547
                    O000OO0OOO0O0000O =O000OO0OOO0O0000O +b','+O0O0OO0O0O0OOO00O [1 :-1 ]#line:548
                else :#line:549
                    O000OO0OOO0O0000O =O000OO0OOO0O0000O +b','+O0O0OO0O0O0OOO00O #line:550
                if len (O000OO0OOO0O0000O )>94857600 :#line:551
                    streamStarrocks (OOO000O0OO0OO000O ,OOO00OOOO00OO0O0O ,OO0OOO00OO000OOOO ,O000OO0OOO0O0000O ,skipError )#line:552
                    O0O0O0O0OO0000O0O .write_offset (O000OO00OOOOO00O0 .partition ,O000OO00OOOOO00O0 .offset +1 )#line:553
                    O000OO0OOO0O0000O =b''#line:554
                if O000OO00OOOOO00O0 .offset ==O0O0O0O0OO0000O0O .end_offset -1 :#line:555
                    break #line:556
        else :#line:557
            for O000OO00OOOOO00O0 in O0000O00O00OO00O0 :#line:558
                O0O0OO0O0O0OOO00O =O000OO00OOOOO00O0 .value #line:559
                if OOO0O0OO00O0O0O00 :#line:560
                    O0O0OO0O0O0OOO00O =json .loads (O0O0OO0O0O0OOO00O .decode ('utf8'))#line:561
                    O0O0OO0O0O0OOO00O =json .dumps (O0O0OO0O0O0OOO00O [OOO0O0OO00O0O0O00 ]).encode ('utf8')#line:562
                O000OO0OOO0O0000O =O000OO0OOO0O0000O +b'\n'+O0O0OO0O0O0OOO00O #line:563
                if len (O000OO0OOO0O0000O )>94857600 :#line:564
                    streamStarrocks (OOO000O0OO0OO000O ,OOO00OOOO00OO0O0O ,OO0OOO00OO000OOOO ,O000OO0OOO0O0000O ,skipError )#line:565
                    O0O0O0O0OO0000O0O .write_offset (O000OO00OOOOO00O0 .partition ,O000OO00OOOOO00O0 .offset +1 )#line:566
                    O000OO0OOO0O0000O =b''#line:567
                if O000OO00OOOOO00O0 .offset ==O0O0O0O0OO0000O0O .end_offset -1 :#line:568
                    break #line:569
        print (O000OO0OOO0O0000O [1 :1000 ])#line:570
        if O000OO0OOO0O0000O :#line:571
            streamStarrocks (OOO000O0OO0OO000O ,OOO00OOOO00OO0O0O ,OO0OOO00OO000OOOO ,O000OO0OOO0O0000O ,skipError )#line:572
        return O000OO00OOOOO00O0 #line:573
    O0O0O0O0OO0000O0O .consumer_topic (O0O00OO0O00OO0O0O )#line:575
def apiStarrocks (O00OO00OO00O000OO ,OOO00OOOOO00O0OO0 ,O0OOOOO0O0OO00O0O ,OO0OO0O000000O0O0 ):#line:578
    with open (O00OO00OO00O000OO ,'r',encoding ='utf8')as OOOO0OO0OO0OOOO0O :#line:579
        O0OO0O0O000OO0OO0 =readSqlstr (OOOO0OO0OO0OOOO0O .read ().strip (),para_dict =OO0OO0O000000O0O0 )#line:580
    O0OO0O0O000OO0OO0 =O0OO0O0O000OO0OO0 .split ('##')#line:581
    O0000OO0O0O0000OO ={}#line:582
    for OO00O0OO0000OOOO0 in O0OO0O0O000OO0OO0 :#line:583
        OOO00O0O00OO00O00 =OO00O0OO0000OOOO0 .find ('=')#line:584
        if OOO00O0O00OO00O00 >0 :#line:585
            OO00O0O0OO0O000O0 =OO00O0OO0000OOOO0 [OOO00O0O00OO00O00 +1 :].replace ('\n',' ').strip ()#line:586
            if OO00O0O0OO0O000O0 :#line:587
                O0000OO0O0O0000OO [OO00O0OO0000OOOO0 [:OOO00O0O00OO00O00 ].strip ()]=OO00O0O0OO0O000O0 #line:588
    OOO0OOOO00OO00OOO =O0000OO0O0O0000OO .pop ('table')#line:589
    O00OO0000O000O0O0 =O0000OO0O0O0000OO .keys ()#line:590
    if 'param'in O00OO0000O000O0O0 :#line:591
        O000O00OO0OOOOO0O =O0000OO0O0O0000OO .pop ('param')#line:592
    else :#line:593
        O000O00OO0OOOOO0O =None #line:594
    if 'apiConn'in O00OO0000O000O0O0 :#line:595
        OOO0O000O0OOOOO00 =O0000OO0O0O0000OO .pop ('apiConn')#line:596
    else :#line:597
        OOO0O000O0OOOOO00 ='default'#line:598
    if 'skipError'in O00OO0000O000O0O0 :#line:599
        skipError =O0000OO0O0O0000OO .pop ('skipError')#line:600
    else :#line:601
        skipError =None #line:602
    if 'jsonpaths'in O00OO0000O000O0O0 :#line:603
        OO00O00000OO0OOO0 =O0000OO0O0O0000OO .get ('jsonpaths')#line:604
        if not OO00O00000OO0OOO0 .startswith ('['):#line:605
            OO00O00000OO0OOO0 =OO00O00000OO0OOO0 .split (',')#line:606
            OO00O00000OO0OOO0 =json .dumps (['$.'+O0O0000OO00000OOO .strip ()for O0O0000OO00000OOO in OO00O00000OO0OOO0 ])#line:607
            O0000OO0O0O0000OO ['jsonpaths']=OO00O00000OO0OOO0 #line:608
    OOOO0OOOO0O0OOOO0 =OOO00OOOOO00O0OO0 [OOO0O000O0OOOOO00 ](O000O00OO0OOOOO0O )#line:609
    if OOOO0OOOO0O0OOOO0 :#line:610
        streamStarrocks (OOO0OOOO00OO00OOO ,O0OOOOO0O0OO00O0O ,O0000OO0O0O0000OO ,OOOO0OOOO0O0OOOO0 ,skipError )#line:611
    else :#line:612
        print ('无数据')#line:613
def streamStarrocks (OOO0OOOO00O0OO0O0 ,O000O000OO0OOO000 ,O00000OOOOOO00OOO ,O0000OO0OO00OOOO0 ,skipError =False ):#line:616
    ""#line:619
    import base64 ,uuid #line:620
    OO0OO0OOO00OOOO00 ,OOO0OOOO00O0OO0O0 =OOO0OOOO00O0OO0O0 .split ('.')#line:621
    OO00OOO0O0O0OOOO0 =str (base64 .b64encode (f'{O000O000OO0OOO000["user"]}:{O000O000OO0OOO000["password"]}'.encode ('utf-8')),'utf-8')#line:622
    O0000OO0OO00OOOO0 =O0000OO0OO00OOOO0 .strip ()#line:623
    if O0000OO0OO00OOOO0 .startswith (b','):#line:624
        O00000OOOOOO00OOO ['strip_outer_array']='true'#line:625
        O0000OO0OO00OOOO0 =b'['+O0000OO0OO00OOOO0 [1 :]+b']'#line:626
    OO0O000OO0OO0OOOO ={'Content-Type':'application/json','Authorization':f'Basic {OO00OOO0O0O0OOOO0}','label':f'{OOO0OOOO00O0OO0O0}{uuid.uuid4()}',**O00000OOOOOO00OOO }#line:632
    O0OOO000OO0000OOO =f"{O000O000OO0OOO000['url']}/api/{OO0OO0OOO00OOOO00}/{OOO0OOOO00O0OO0O0}/_stream_load"#line:633
    print ('start loading to starrocks....')#line:634
    OOOOO0O000000OO00 =requests .put (O0OOO000OO0000OOO ,headers =OO0O000OO0OO0OOOO ,data =O0000OO0OO00OOOO0 ).json ()#line:635
    print (OOOOO0O000000OO00 )#line:636
    if OOOOO0O000000OO00 ['Status']=='Fail':#line:637
        if skipError :#line:638
            print (f'Starrocks Load Error, Skip this offset')#line:639
        else :#line:640
            raise SmartpipException (f'Starrocks Load Error')#line:641
def routineStarrocks (OOOOOOO000OOOOOOO ,OOO0O00O000OOOO00 ,flag =''):#line:644
    OOO00O0000O0O0000 =_OO0OOO00OO00OO0O0 ([f'SHOW ROUTINE LOAD FOR {OOO0O00O000OOOO00}'],OOOOOOO000OOOOOOO ,db_connect ='starrocks')#line:645
    OOO00O0000O0O0000 =dict (zip (OOO00O0000O0O0000 [0 ],OOO00O0000O0O0000 [1 ]))#line:646
    print ('状态:',OOO00O0000O0O0000 ['State'])#line:647
    print ('统计:',OOO00O0000O0O0000 ['Statistic'])#line:648
    print ('进度:',OOO00O0000O0O0000 ['Progress'])#line:649
    if OOO00O0000O0O0000 ['State']!='RUNNING':#line:650
        print ('ERROR: ',OOO00O0000O0O0000 ['ReasonOfStateChanged'])#line:651
        if not flag :#line:652
            raise SmartpipException ('Starrocks Routine Load fail')#line:653
from airflow .utils .session import provide_session #line:659
@provide_session #line:662
def point_test (O00OO0OOOO00O0OOO ,sleeptime ='',maxtime ='',session =None ):#line:663
    ""#line:670
    if sleeptime :#line:671
        sleeptime =int (sleeptime )#line:672
        sleeptime =sleeptime if sleeptime >60 else 60 #line:673
    if maxtime :#line:674
        maxtime =int (maxtime )#line:675
        maxtime =maxtime if maxtime <60 *60 *2 else 60 *60 *2 #line:676
    else :#line:677
        maxtime =0 #line:678
    try :#line:679
        O000OO00O00OO00O0 =f"select start_date,state from dag_run where dag_id ='{O00OO0OOOO00O0OOO}' ORDER BY id desc LIMIT 1"#line:680
        while True :#line:681
            O0000OO0OOO0OO00O =session .execute (O000OO00O00OO00O0 ).fetchall ()#line:682
            if O0000OO0OOO0OO00O [0 ][1 ]!='success':#line:683
                if maxtime >0 and O0000OO0OOO0OO00O [0 ][1 ]!='failed':#line:684
                    print ('waiting...'+O0000OO0OOO0OO00O [0 ][1 ])#line:685
                    time .sleep (sleeptime )#line:686
                    maxtime =maxtime -sleeptime #line:687
                else :#line:688
                    O0OO000O0O00OO00O =O0000OO0OOO0OO00O [0 ][0 ].strftime ("%Y-%m-%d %H:%M:%S")#line:689
                    OOO0OO000OOO00OO0 ='所依赖的dag:'+O00OO0OOOO00O0OOO +',状态为'+O0000OO0OOO0OO00O [0 ][1 ]+'.其最新的执行时间为'+O0OO000O0O00OO00O #line:690
                    fun_email (OOO0OO000OOO00OO0 ,'前置DAG任务未成功')#line:691
                    raise SmartpipException (OOO0OO000OOO00OO0 )#line:692
            else :#line:693
                print ('success...',O0000OO0OOO0OO00O )#line:694
                break #line:695
    except Exception as O0000O0OO0000O0OO :#line:696
        raise SmartpipException (str (O0000O0OO0000O0OO .args ))#line:697
class _O0OOO00OOOOOO0O00 (object ):#line:701
    connect =None #line:702
    def __init__ (OO0O0O0000OO0O000 ,OO000OOO00O000O0O ,OOO00O0OOOO00O000 ,O00OOO00O0O00O0OO ,offsets =None ):#line:704
        OO0O0O0000OO0O000 .end_offset =None #line:705
        OO0O0O0000OO0O000 .db_err_count =0 #line:706
        OO0O0O0000OO0O000 .topic =OO000OOO00O000O0O #line:707
        OO0O0O0000OO0O000 .kafkaconfig =OOO00O0OOOO00O000 #line:708
        OO0O0O0000OO0O000 .offsetDict ={}#line:709
        OO0O0O0000OO0O000 .current_dir =O00OOO00O0O00O0OO #line:710
        OO0O0O0000OO0O000 .offsets =offsets #line:711
        try :#line:712
            OO0O0O0000OO0O000 .consumer =OO0O0O0000OO0O000 .connect_kafka_customer ()#line:713
        except Exception as O0O000OO000OOOO00 :#line:714
            O0O000OO000OOOO00 ='kafka无法连接','ErrLocation：{}\n'.format (OO000OOO00O000O0O )+str (O0O000OO000OOOO00 )+',kafka消费者无法创建'#line:715
            raise O0O000OO000OOOO00 #line:716
    def get_toggle_or_offset (OO00O0O000O0O0000 ,O00O00O0O0OO00O00 ,OO000OOOO00OO0OO0 ):#line:718
        ""#line:719
        if OO00O0O000O0O0000 .offsets :#line:720
            if isinstance (OO00O0O000O0O0000 .offsets ,int ):#line:721
                return OO00O0O000O0O0000 .offsets #line:722
            else :#line:723
                OO0O0OO0O0O00O000 =OO00O0O000O0O0000 .offsets .get (str (OO000OOOO00OO0OO0 ))#line:724
                if OO0O0OO0O0O00O000 is not None :#line:725
                    return int (OO0O0OO0O0O00O000 )#line:726
        OO0O0OO0O0O00O000 =0 #line:727
        try :#line:728
            O0O0OOO000OO0OOOO =f"{OO00O0O000O0O0000.current_dir}/kafka/{O00O00O0O0OO00O00}_offset_{OO000OOOO00OO0OO0}.txt"#line:729
            if os .path .exists (O0O0OOO000OO0OOOO ):#line:730
                OOO0OOO0O000OO0OO =open (O0O0OOO000OO0OOOO ).read ()#line:731
                if OOO0OOO0O000OO0OO :#line:732
                    OO0O0OO0O0O00O000 =int (OOO0OOO0O000OO0OO )#line:733
            else :#line:734
                with open (O0O0OOO000OO0OOOO ,encoding ='utf-8',mode ='a')as OO0OOOOOOO00O0O00 :#line:735
                    OO0OOOOOOO00O0O00 .close ()#line:736
        except Exception as OO0000O0O00OOO0O0 :#line:737
            print (f"读取失败：{OO0000O0O00OOO0O0}")#line:738
            raise OO0000O0O00OOO0O0 #line:739
        return OO0O0OO0O0O00O000 #line:740
    def write_offset (O00O0000000000OO0 ,O000OO00O0OOO000O ,offset =None ):#line:742
        ""#line:745
        if O00O0000000000OO0 .topic and offset :#line:746
            OOO00O0OO0O0OOOO0 =f"{O00O0000000000OO0.current_dir}/kafka/{O00O0000000000OO0.topic}_offset_{O000OO00O0OOO000O}.txt"#line:748
            try :#line:749
                with open (OOO00O0OO0O0OOOO0 ,'w')as O0OO0OOO000000OO0 :#line:750
                    O0OO0OOO000000OO0 .write (str (offset ))#line:751
                    O0OO0OOO000000OO0 .close ()#line:752
            except Exception as OO00O0O00OOOO00O0 :#line:753
                print (f"写入offset出错：{OO00O0O00OOOO00O0}")#line:754
                raise OO00O0O00OOOO00O0 #line:755
    def connect_kafka_customer (OO0O0OO0OOO0OOO0O ):#line:757
        ""#line:758
        OOOO00OOOOO00OO00 =KafkaConsumer (**OO0O0OO0OOO0OOO0O .kafkaconfig )#line:759
        return OOOO00OOOOO00OO00 #line:760
    def parse_data (OO0O0000OOOOOOOOO ,OOOOO000O0OO0OOO0 ):#line:762
        ""#line:767
        return dict ()#line:768
    def gen_sql (O00O0O000O00O00OO ,OO0000O00O00O000O ):#line:770
        ""#line:775
        O0OOO0O0O000O0OO0 =[]#line:776
        for OOO0O00OO0000O00O in OO0000O00O00O000O :#line:777
            O0OOO0O0O000O0OO0 .append (str (tuple (OOO0O00OO0000O00O )))#line:779
        return ','.join (O0OOO0O0O000O0OO0 )#line:780
    def dispose_kafka_data (O0O00O0OO0OO0O00O ,OO00O00O00O00000O ):#line:782
        ""#line:787
        pass #line:788
    def get_now_time (O0OO0O0OOOOOOOO00 ):#line:790
        ""#line:794
        OOOOOO0O000OOO00O =int (time .time ())#line:795
        return time .strftime ('%Y-%m-%d %H:%M:%S',time .localtime (OOOOOO0O000OOO00O ))#line:796
    def tran_data (OO00OO000O00O0OO0 ,O0O0OOO0O0000OO00 ,O00O0OOOOO00OOO00 ):#line:798
        ""#line:804
        OOO00O00OO0OOOOOO =O0O0OOO0O0000OO00 .get (O00O0OOOOO00OOO00 ,"")#line:805
        OOO00O00OO0OOOOOO =""if OOO00O00OO0OOOOOO is None else OOO00O00OO0OOOOOO #line:806
        return str (OOO00O00OO0OOOOOO )#line:807
    def consumer_data (OO00OOOOO000000O0 ,OO00OOO00O0OO0OO0 ,O000O0O0O000O0000 ,O00OO00O0OO0O0000 ):#line:809
        ""#line:816
        if OO00OOOOO000000O0 .consumer :#line:817
            OO00OOOOO000000O0 .consumer .assign ([TopicPartition (topic =OO00OOOOO000000O0 .topic ,partition =OO00OOO00O0OO0OO0 )])#line:818
            O0O00OOOO0OOO000O =TopicPartition (topic =OO00OOOOO000000O0 .topic ,partition =OO00OOO00O0OO0OO0 )#line:820
            OO00OO0OO00O000OO =OO00OOOOO000000O0 .consumer .beginning_offsets ([O0O00OOOO0OOO000O ])#line:821
            O00OO0OOO0000000O =OO00OO0OO00O000OO .get (O0O00OOOO0OOO000O )#line:822
            OO00000OOOOOOOO0O =OO00OOOOO000000O0 .consumer .end_offsets ([O0O00OOOO0OOO000O ])#line:823
            O0OO0OOO0OO0OO00O =OO00000OOOOOOOO0O .get (O0O00OOOO0OOO000O )#line:824
            print (f'建立消费者, {OO00OOO00O0OO0OO0}分区, 最小offset:{O00OO0OOO0000000O}, 最大offset:{O0OO0OOO0OO0OO00O}')#line:825
            if O000O0O0O000O0000 =='-996':#line:826
                O000O0O0O000O0000 =OO00000OOOOOOOO0O -1 #line:827
            if O000O0O0O000O0000 <O00OO0OOO0000000O :#line:828
                print (f'Warning: 消费offset：{O000O0O0O000O0000} 小于最小offset:{O00OO0OOO0000000O}')#line:829
                O000O0O0O000O0000 =O00OO0OOO0000000O #line:830
            if O000O0O0O000O0000 >=O0OO0OOO0OO0OO00O :#line:831
                print (f'消费offset：{O000O0O0O000O0000} 大于最大offset:{O0OO0OOO0OO0OO00O}, 本次不消费')#line:832
                return #line:833
            OO00OOOOO000000O0 .end_offset =O0OO0OOO0OO0OO00O #line:834
            OO00OOOOO000000O0 .consumer .seek (TopicPartition (topic =OO00OOOOO000000O0 .topic ,partition =OO00OOO00O0OO0OO0 ),offset =O000O0O0O000O0000 )#line:835
            print (f'消费{OO00OOO00O0OO0OO0}分区, 开始消费offset：{O000O0O0O000O0000}!')#line:836
            OO0OO0O0O0OOO0OOO =O00OO00O0OO0O0000 (OO00OOOOO000000O0 .consumer )#line:837
            O000O0O0O000O0000 =OO0OO0O0O0OOO0OOO .offset +1 #line:838
            OO00OOOOO000000O0 .offsetDict [OO00OOO00O0OO0OO0 ]=O000O0O0O000O0000 #line:841
            OO00OOOOO000000O0 .write_offset (OO00OOO00O0OO0OO0 ,O000O0O0O000O0000 )#line:842
            OO00OOOOO000000O0 .offsetDict [OO00OOO00O0OO0OO0 ]=O000O0O0O000O0000 #line:845
            OO00OOOOO000000O0 .write_offset (OO00OOO00O0OO0OO0 ,O000O0O0O000O0000 )#line:846
    def consumer_topic (O00O0OOOOOOO000O0 ,O000O0O000OO000O0 ):#line:848
        print (f"topic: {O00O0OOOOOOO000O0.topic}")#line:849
        print ('开始解析。')#line:850
        OOOOO000OO0OO00O0 =O00O0OOOOOOO000O0 .consumer .partitions_for_topic (topic =O00O0OOOOOOO000O0 .topic )#line:852
        for O000OO000O00O0000 in OOOOO000OO0OO00O0 :#line:853
            OOO0000OOO0O0OO0O =O00O0OOOOOOO000O0 .get_toggle_or_offset (O00O0OOOOOOO000O0 .topic ,O000OO000O00O0000 )#line:854
            O0OO0OO0OOO00OOOO =0 if OOO0000OOO0O0OO0O <0 else OOO0000OOO0O0OO0O #line:856
            O00O0OOOOOOO000O0 .consumer_data (O000OO000O00O0000 ,O0OO0OO0OOO00OOOO ,O000O0O000OO000O0 )#line:857
    def save_all_offset (O0OO0OOOOO000O000 ):#line:859
        for OO000OOO0OO0000OO ,O00O00OOO00OOOOOO in O0OO0OOOOO000O000 .offsetDict :#line:860
            O0OO0OOOOO000O000 .write_offset (OO000OOO0OO0000OO ,O00O00OOO00OOOOOO )#line:861
