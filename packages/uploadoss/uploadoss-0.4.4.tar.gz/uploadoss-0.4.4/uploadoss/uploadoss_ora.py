# -*- coding: utf-8 -*-
import oss2
import pandas as pd
from configparser import ConfigParser
import os
import oracledb
import csv
import gzip

"""  
    数据库批量操作,内部对CSV进行GZIP压缩处理，将多个表的数据导出并上传到Ali OSS 指定目录
    :param conf_path: config file full path
    :local_path: 本地文件位置,用于存放数据库导出的数据
    :table_list_conf: config file full path，每个表和sql文本使用固定的分隔符\001 
    :start_time,end_time,dir_time 分别应对自定义sql里面的开始和结束时间，以及oss目录日期
"""
def oracle_to_oss_list_incremental(conf_path,local_path,table_list_conf,start_time,end_time,dir_time):


    config = ConfigParser() 
    config.read(conf_path)  
    # OSS config
    OSS_ACCESS_KEY_ID = config['oss']['OSS_ACCESS_KEY_ID']
    OSS_ACCESS_KEY_SECRET = config['oss']['OSS_ACCESS_KEY_SECRET']
    bucket = config.get('oss', 'bucket')
    endpoint = config.get('oss', 'endpoint')

    # oracle config 
    batch_size = config['oracle']['batch_size']

    local_path = config['dir']['local_path']

    # 建立连接
    conn = getoracleconn(conf_path)
    # 创建游标（用于执行SQL）
    cursor = conn.cursor()

    auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    
    bucket = oss2.Bucket(auth, endpoint, bucket)

    local_file = "" 

    if not os.path.exists(local_path):
        os.mkdir(local_path) 

    with open (table_list_conf,'r') as f:

        data  = f.readlines()
    processed = 0
    for line in data:

        try:  
            table_name,sql_text,oss_path = line.strip().split("\\001")
            if len(sql_text) <3 :
                
                print("当前行不符合规范，请检查：" + line)
            else:
                sql_text = sql_text.format(start_time,end_time)
                oss_path = oss_path.format(table_name,dir_time)
            file_name = table_name + ".csv.gz"
            local_file = local_path+file_name
            #批次读取
            print(f"执行SQL: {sql_text} ")
            cursor.execute(sql_text)
            
            with gzip.open(local_file, 'wt', encoding='utf-8', newline='') as f:
                writer = csv.writer(f,lineterminator='\n')
                writer.writerow([col[0].strip() for col in cursor.description])
                while True:
                    rows = cursor.fetchmany(int(batch_size))
                    if not rows:
                        break
                    writer.writerows(rows)
                    processed += len(rows)
                    print(f"已处理 {processed} 条记录")

            # Create OSS 
            bucket.put_object(oss_path, '') 

            result = oss_upload_file(local_file,oss_path,file_name,bucket)

            print(sql_text)
            # HTTP返回码。
            print('http status: {0}'.format(result.status))
            # 请求ID。请求ID是本次请求的唯一标识，强烈建议在程序日志中添加此参数。
            print('request_id: {0}'.format(result.request_id))
            # ETag是put_object方法返回值特有的属性，用于标识一个Object的内容。
            print('ETag: {0}'.format(result.etag))
            # HTTP响应头部。
            print('date: {0}'.format(result.headers['date']))

            # 删除本地文件
            delete_file(local_file)
            processed = 0
        except Exception as e:  
            print("An error occurred:", e)  
            continue  
        finally:  
            pass
    conn.close()   


def oss_upload_file(local_file,oss_path,file_name,bucket):
    
    with open(local_file,'rb') as file_obj:
        result = bucket.put_object(oss_path+file_name, file_obj)
    return result

"""  
    上传单个文件到Ali OSS 指定目录  
    :param bucket: Ali bucket,getossbucket() 返回值
    :local_path: 本地文件位置
    :file_name: 本地文件名称，同时也作为OSS端文件名称
    :oss_path: 文件需要上传到的目录  
"""
def file_to_oss(bucket,local_path,file_name,oss_path):

    local_file = local_path + file_name
    # Create OSS directory
    bucket.put_object(oss_path, '') 

    result = oss_upload_file(local_file,oss_path,file_name,bucket)
    return result 


"""  
    返回 OSS Bucket  
    :param conf_path: config file full path 
"""
def getossbucket(conf_path):

    config = ConfigParser()  
    config.read(conf_path)  
    # OSS config
    OSS_ACCESS_KEY_ID = config['oss']['OSS_ACCESS_KEY_ID']
    OSS_ACCESS_KEY_SECRET = config['oss']['OSS_ACCESS_KEY_SECRET']
    bucket = config.get('oss', 'bucket')
    endpoint = config.get('oss', 'endpoint')

    auth = oss2.Auth(OSS_ACCESS_KEY_ID, OSS_ACCESS_KEY_SECRET)
    
    bucket = oss2.Bucket(auth, endpoint, bucket)

    return bucket
"""  
    返回 pymysql conn  
    :param conf_path: config file full path
"""
def getoracleconn(conf_path):
    config = ConfigParser()  
    config.read(conf_path) 
    # oracle config 
    host = config['oracle']['host']
    user = config['oracle']['user']
    password = config['oracle']['password']
    port = int(config['oracle']['port'])
    database = config['oracle']['database']
    #charset = config['oracle']['charset']

    instant_client_path = config['oracle']['instant_client_path']

    dsn = "{}:{}/{}".format(host,port,database)
    print("dsn:" + dsn)
    # 针对oracle早期版本,采取厚模式.
    try:
        # 初始化厚模式，显式指定lib_dir
        oracledb.init_oracle_client(lib_dir=instant_client_path)
        print("厚模式初始化成功（未配置全局环境变量）")
    except oracledb.Error as e:
        print(f"初始化失败：{e}")

    config = {
        "user": user,       # 如：scott
        "password": password,     # 如：tiger
        "dsn": dsn,  # DSN格式：主机:端口/服务名（或SID）
    }
    # 建立连接
    conn = oracledb.connect(**config)

    return conn


def delete_file(path):
    os.remove(path)

if __name__ == '__main__':

    from datetime import datetime, timedelta
    today = datetime.today()
    yesterday = today - timedelta(days=1)
    # 日分区表目录
    dir_name = 'dt=' + yesterday.strftime('%Y%m%d') + '/' 

    print(dir_name)


    conf_path = r'C:\python_prj\tooss\uploadoss\conf.ini'
    local_path = r'C:\\demo\\data\\'

    config = ConfigParser() 
    config.read(conf_path)  

    # 配置多个表及SQL语句,分隔符要求 \001

    table_conf_list=r'C:\\demo\\oss\\table_config.txt' 

    oracle_to_oss_list_incremental(conf_path,local_path,table_conf_list,"'2025-01-01'","'2025-02-02'",'20250202')  






