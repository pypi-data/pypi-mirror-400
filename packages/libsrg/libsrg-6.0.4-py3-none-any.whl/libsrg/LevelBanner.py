#!/usr/bin/env  python3
# libsrg (Code and Documentation) is published under an MIT License
# Copyright (c) 2023,2024 Steven Goncalo
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

# 2024 Steven Goncalo

import logging

from libsrg.LoggingUtils import level2int
from libsrg.Runner import Runner

banner_DEBUG = """

######   #######  ######   #     #   #####   
#     #  #        #     #  #     #  #     #  
#     #  #        #     #  #     #  #        
#     #  #####    ######   #     #  #  ####  
#     #  #        #     #  #     #  #     #  
#     #  #        #     #  #     #  #     #  
######   #######  ######    #####    #####   

"""

banner_INFO = """

###  #     #  #######  #######  
 #   ##    #  #        #     #  
 #   # #   #  #        #     #  
 #   #  #  #  #####    #     #  
 #   #   # #  #        #     #  
 #   #    ##  #        #     #  
###  #     #  #        #######  

"""

banner_WARNING = """

#     #     #     ######   #     #  ###  #     #   #####   
#  #  #    # #    #     #  ##    #   #   ##    #  #     #  
#  #  #   #   #   #     #  # #   #   #   # #   #  #        
#  #  #  #     #  ######   #  #  #   #   #  #  #  #  ####  
#  #  #  #######  #   #    #   # #   #   #   # #  #     #  
#  #  #  #     #  #    #   #    ##   #   #    ##  #     #  
 ## ##   #     #  #     #  #     #  ###  #     #   #####   

"""

banner_ERROR = """

#######  ######   ######   #######  ######   
#        #     #  #     #  #     #  #     #  
#        #     #  #     #  #     #  #     #  
#####    ######   ######   #     #  ######   
#        #   #    #   #    #     #  #   #    
#        #    #   #    #   #     #  #    #   
#######  #     #  #     #  #######  #     #  

"""

banner_CRITICAL = """

 #####   ######   ###  #######  ###   #####      #     #        
#     #  #     #   #      #      #   #     #    # #    #        
#        #     #   #      #      #   #         #   #   #        
#        ######    #      #      #   #        #     #  #        
#        #   #     #      #      #   #        #######  #        
#     #  #    #    #      #      #   #     #  #     #  #        
 #####   #     #  ###     #     ###   #####   #     #  #######  

"""

banners: dict[str, str] = {
    'DEBUG': banner_DEBUG,
    'INFO': banner_INFO,
    'WARNING': banner_WARNING,
    'ERROR': banner_ERROR,
    'CRITICAL': banner_CRITICAL,
}


class LevelBanner:
    """
    The LevelBanner class maintains a set of large print banners listing the python logging levels.
    """
    levs = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    levmap = {'CRITICAL': 50, 'FATAL': 50, 'ERROR': 40, 'WARN': 30, 'WARNING': 30, 'INFO': 20, 'DEBUG': 10, 'NOTSET': 0}

    # logging.getLevelNamesMapping()  # levmap[int]->str
    # {'CRITICAL': 50, 'FATAL': 50, 'ERROR': 40, 'WARN': 30, 'WARNING': 30, 'INFO': 20, 'DEBUG': 10, 'NOTSET': 0}

    @classmethod
    def find(cls, name: str, threshold=None) -> str:
        """
        Find a LevelBanner instance by name.
        :param name: Uppercase ascii name of logging level
        :param threshold: return empty string for levels below threshold
        :return: block character string
        """
        iname = level2int(name)
        if not threshold:
            threshold = logging.WARNING
        if iname < threshold:
            return ""  # f"All logging below {threshold=}"
        if name in banners:
            return banners[name]
        else:
            return f"Unknown level {name}"

    @classmethod
    def generate(cls) ->None:
        """
        This method runs the system banner utility to generate the text arrays pasted above.

        It is not needed at run time, just preserves how the banners were generated.
        """
        for lev in cls.levs:
            print(f'banner_{lev}="""')
            r = Runner(["banner", lev])
            print("\n".join(r.so_lines))
            print('"""')
            print()
        print("banners:dict[str,str]={")
        for lev in cls.levs:
            print(f"   '{lev}':banner_{lev},")
        print("}")

        for lev in cls.levs:
            s = cls.find(lev)
            print(lev, s)


if __name__ == '__main__':
    LevelBanner.generate()
