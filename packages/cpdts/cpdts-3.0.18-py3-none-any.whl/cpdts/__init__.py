

import fire 
from .fire_project.fire_create import fire_create



class ENTRY(object):
    """CLI 入口类，提供项目创建相关命令"""
    
    def fire(self) -> None:
        """快速创建 fire 项目"""
        fire_create()
    
def main() -> None:
    """CLI 主入口函数"""
    try:
        fire.Fire(ENTRY)
    except KeyboardInterrupt:
        print("\n操作已取消")
        exit(0)

