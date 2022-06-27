import sys
sys.path.append('../..')
import go
import plugins.downbili.download

def downbili(meta_data):
    uid = meta_data.get('se').get('user_id')
    gid = meta_data.get('se').get('group_id')
    message = meta_data.get('message')
    
    go.send(meta_data, '下载开始...')
    # {:mark:bug_fix:}
    vl = download.VideoList(url,uid, gid, part)
    for i in vl.download():
        dl = download.Download(i, uid, gid)
        dl.download(path,type = type,codecs = codecs,byte = byte)