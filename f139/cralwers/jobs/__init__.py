from .f139_chongqingfeilv import F139CqFl  # 重庆废铝
from .f139_guangdongfeilv import F139GdFl  # 广东废铝
from .f139_hebeifeilv import F139HbFl  # 河北废铝
from .f139_shandongfeilv import F139SdFl  # 山东废铝
from .f139_zhejiangfeilv import F139ZjFl  # 浙江废铝
from .f139_shanghaifeilv import F139ShFl  # 上海废铝
from .f139_hebeifeitong import F139HbFt  # 河北废铜
from .f139_jiangsufeitong import F139JsFt  # 江苏废铜
from .f139_shanghaifeitong import F139ShFt  # 上海废铜
from .f139_shandongfeitong import F139SdFt  # 山东废铜
from .f139_shandongfeixi import F139SdFx  # 山东废锡
from .f139_guangdongfeixi import F139GdFx  # 广东废锡
from .f139_guangdongfeixin import F139GdFx2  # 广东废锌
from .f139_feidianping import F139Fdp  # 全国各地废电瓶
from .f139_huanyuanqian import F139Hyq  # 全国各地还原铅

# 所有的废有色抓取类
all_fys_crawlers = [F139CqFl, F139GdFl, F139HbFl, F139SdFl, F139ZjFl,F139ShFl,
                    F139HbFt, F139JsFt, F139ShFt, F139SdFt,
                    F139SdFx, F139GdFx,
                    F139GdFx2,
                    F139Fdp, F139Hyq]

