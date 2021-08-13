from owlifttypeh import OwhMeta

# metaデータからイベントタイプを生成
def get_event_type(meta):
    if meta is None:
        return OwhMeta.EV_NONE
    
    event_type = meta.event_type
    if (evt & OwhMeta.EV_BODY_TEMP) != 0:
        return OwhMeta.EV_BODY_TEMP
    elif (evt & OwhMeta.EV_CORRECT) != 0:
        return OwhMeta.EV_CORRECT
    elif (evt & OwhMeta.EV_DIST_INVALID) != 0:
        return OwhMeta.EV_DIST_INVALID
    elif (evt & OwhMeta.EV_LOST) != 0:
        return OwhMeta.EV_LOST
    else:
        return OwhMeta.EV_NONE