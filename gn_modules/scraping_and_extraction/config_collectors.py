"""
This config file defines the collectors array.
At the processing step, only the processings present in this array will be computed.
"""

from gn_modules.scraping_and_extraction.collectors.la_croix import LaCroix
from gn_modules.scraping_and_extraction.collectors.le_figaro import LeFigaro
from gn_modules.scraping_and_extraction.collectors.le_monde import LeMonde
from gn_modules.scraping_and_extraction.collectors.liberation import Liberation
from gn_modules.scraping_and_extraction.collectors.mediapart import Mediapart
from gn_modules.scraping_and_extraction.collectors.huffington_post import HuffingtonPost
from gn_modules.scraping_and_extraction.collectors.le_parisien import LeParisien
from gn_modules.scraping_and_extraction.collectors.l_equipe import LEquipe
from gn_modules.scraping_and_extraction.collectors.les_echos import LesEchos

collectors = {
    LaCroix.NAME: LaCroix,
    LeFigaro.NAME: LeFigaro,
    LeMonde.NAME: LeMonde,
    Liberation.NAME: Liberation,
    LeParisien.NAME: LeParisien,
    LEquipe.NAME: LEquipe,
    LesEchos.NAME: LesEchos,
    Mediapart.NAME: Mediapart,
    HuffingtonPost.NAME: HuffingtonPost,
}
