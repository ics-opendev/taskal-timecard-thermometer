from owlifttypeh import OwhMeta

# metaデータからイベントタイプを生成
def get_event_type(meta):
    if meta == None:
        return OwhMeta.EV_NONE
    
    event_type = meta.event_type
    if (event_type & OwhMeta.EV_BODY_TEMP) != 0:
        return OwhMeta.EV_BODY_TEMP
    elif (event_type & OwhMeta.EV_CORRECT) != 0:
        return OwhMeta.EV_CORRECT
    elif (event_type & OwhMeta.EV_DIST_INVALID) != 0:
        return OwhMeta.EV_DIST_INVALID
    elif (event_type & OwhMeta.EV_LOST) != 0:
        return OwhMeta.EV_LOST
    else:
        return OwhMeta.EV_NONE