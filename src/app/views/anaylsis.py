from functools import reduce
from flask import jsonify, request
from flask_jwt import jwt_required, current_identity
from sqlalchemy import and_
from sqlalchemy.types import Float
from ..utils import similarty_dict
from ..visualization import HeatmapVisualization
import time
from ..app import app
from ..schemas import *
from ..models import db, User, Analysis, MetabolomicsData, Method, Dataset
from ..tasks import save_analysis
from ..base import *
from ..dpm import *
import datetime







sample_data = {'group': 'None', 'study_name': 'FatB Gene Project', 'analysis': {'LabF_115898': {'Label': 'None', 'Metabolites': {'leu_L_c': 8599.0, 'adpac_c': 1507.0, 'g6p_c': 6850.0, 'glu_L_c': 364440.0, 'dhdascb_c': 185798.0, 'amp_c': 2899.0, 'phe_L_c': 4304.0, 'thr_L_c': 44939.0, 'oxa_c': 674933.0, 'gly_c': 468690.0, 'ascb_L_c': 688.0, 'glc_D_c': 148599.0, 'citr_L_c': 3402.0, 'lnlnca_c': 3168.0, 'xylt_c': 1972.0, 'acmana_c': 9670.0, 'tre_c': 1059.0, 'ser_L_c': 375298.0, 'fum_c': 112457.0, 'tyr_L_c': 4110.0, 'tym_c': 26261.0, 'trp_L_c': 2289.0, 'hdca_c': 5896.0, 'xyl_D_c': 16849.0, 'thmpp_c': 135713.0, 'mal_L_c': 26262.0, 'lnlc_c': 519.0, 'ethamp_c': 4295.0, 'dca_c': 4593.0, 'pro_L_c': 735480.0, 'met_L_c': 4365.0, 'ddca_c': 10864.0, 'adn_c': 423.0, 'ocdca_c': 17995.0, '5oxpro_c': 577671.0, 'ttdca_c': 468.0, 'C01601_c': 14659.0, 'val_L_c': 24835.0, 'glyc_R_c': 12991.0, 'spmd_c': 373.0, 'ile_L_c': 4305.0, 'ala_B_c': 4431.0, 'glcn_c': 711.0, 'arg_L_c': 19528.0, 'orn_c': 23190.0, 'lac_L_c': 64018.0, 'cit_c': 6783.0, 'akg_c': 2789.0, 'succ_c': 23069.0}}, 'LabF_115821': {'Label': 'None', 'Metabolites': {'leu_L_c': 2701.0, 'adpac_c': 1872.0, 'g6p_c': 7981.0, 'glu_L_c': 278425.0, 'dhdascb_c': 234347.0, 'amp_c': 2878.0, 'phe_L_c': 4012.0, 'thr_L_c': 72473.0, 'oxa_c': 38192.0, 'gly_c': 534059.0, 'ascb_L_c': 851.0, 'glc_D_c': 91136.0, 'citr_L_c': 3226.0, 'lnlnca_c': 4327.0, 'xylt_c': 2981.0, 'acmana_c': 16733.0, 'tre_c': 536.0, 'ser_L_c': 558622.0, 'fum_c': 436851.0, 'tyr_L_c': 6255.0, 'tym_c': 36730.0, 'trp_L_c': 4899.0, 'hdca_c': 8151.0, 'xyl_D_c': 24757.0, 'thmpp_c': 211352.0, 'mal_L_c': 38429.0, 'lnlc_c': 627.0, 'ethamp_c': 5569.0, 'dca_c': 7949.0, 'pro_L_c': 110445.0, 'met_L_c': 4122.0, 'ddca_c': 9381.0, 'adn_c': 644.0, 'ocdca_c': 29917.0, '5oxpro_c': 858933.0, 'ttdca_c': 806.0, 'C01601_c': 45112.0, 'val_L_c': 11345.0, 'glyc_R_c': 22525.0, 'spmd_c': 816.0, 'ile_L_c': 613.0, 'ala_B_c': 4591.0, 'glcn_c': 397.0, 'arg_L_c': 37686.0, 'orn_c': 12195.0, 'lac_L_c': 65818.0, 'cit_c': 4463.0, 'akg_c': 2599.0, 'succ_c': 43483.0}}, 'LabF_115904': {'Label': 'None', 'Metabolites': {'leu_L_c': 4868.0, 'adpac_c': 2197.0, 'g6p_c': 7767.0, 'glu_L_c': 382033.0, 'dhdascb_c': 163570.0, 'amp_c': 2153.0, 'phe_L_c': 4020.0, 'thr_L_c': 52772.0, 'oxa_c': 271901.0, 'gly_c': 718653.0, 'ascb_L_c': 662.0, 'glc_D_c': 116769.0, 'citr_L_c': 2822.0, 'lnlnca_c': 4863.0, 'xylt_c': 2157.0, 'acmana_c': 10246.0, 'tre_c': 2367.0, 'ser_L_c': 644142.0, 'fum_c': 180903.0, 'tyr_L_c': 3541.0, 'tym_c': 30760.0, 'trp_L_c': 1922.0, 'hdca_c': 5563.0, 'xyl_D_c': 20923.0, 'thmpp_c': 89094.0, 'mal_L_c': 26727.0, 'lnlc_c': 449.0, 'ethamp_c': 2810.0, 'dca_c': 5273.0, 'pro_L_c': 634620.0, 'met_L_c': 4466.0, 'ddca_c': 16604.0, 'adn_c': 538.0, 'ocdca_c': 19008.0, '5oxpro_c': 630096.0, 'ttdca_c': 607.0, 'C01601_c': 26541.0, 'val_L_c': 26680.0, 'glyc_R_c': 16857.0, 'spmd_c': 545.0, 'ile_L_c': 6579.0, 'ala_B_c': 6114.0, 'glcn_c': 333.0, 'arg_L_c': 29214.0, 'orn_c': 14889.0, 'lac_L_c': 46955.0, 'cit_c': 10725.0, 'akg_c': 1743.0, 'succ_c': 76735.0}}, 'LabF_115826': {'Label': 'None', 'Metabolites': {'leu_L_c': 6891.0, 'adpac_c': 4537.0, 'g6p_c': 8596.0, 'glu_L_c': 255206.0, 'dhdascb_c': 195741.0, 'amp_c': 2264.0, 'phe_L_c': 4245.0, 'thr_L_c': 45618.0, 'oxa_c': 71978.0, 'gly_c': 238196.0, 'ascb_L_c': 884.0, 'glc_D_c': 147045.0, 'citr_L_c': 1378.0, 'lnlnca_c': 2525.0, 'xylt_c': 2095.0, 'acmana_c': 14507.0, 'tre_c': 1007.0, 'ser_L_c': 283620.0, 'fum_c': 193074.0, 'tyr_L_c': 5128.0, 'tym_c': 30171.0, 'trp_L_c': 4272.0, 'hdca_c': 5201.0, 'xyl_D_c': 24527.0, 'thmpp_c': 76869.0, 'mal_L_c': 27525.0, 'lnlc_c': 398.0, 'ethamp_c': 4320.0, 'dca_c': 5546.0, 'pro_L_c': 617786.0, 'met_L_c': 2349.0, 'ddca_c': 8543.0, 'adn_c': 588.0, 'ocdca_c': 19787.0, '5oxpro_c': 1011677.0, 'ttdca_c': 766.0, 'C01601_c': 13861.0, 'val_L_c': 27101.0, 'glyc_R_c': 7896.0, 'spmd_c': 411.0, 'ile_L_c': 5321.0, 'ala_B_c': 5658.0, 'glcn_c': 439.0, 'arg_L_c': 15180.0, 'orn_c': 3168.0, 'lac_L_c': 163642.0, 'cit_c': 6047.0, 'akg_c': 2276.0, 'succ_c': 83729.0}}, 'LabF_115873': {'Label': 'None', 'Metabolites': {'leu_L_c': 9373.0, 'adpac_c': 2338.0, 'g6p_c': 6826.0, 'glu_L_c': 250433.0, 'dhdascb_c': 174461.0, 'amp_c': 2314.0, 'phe_L_c': 4712.0, 'thr_L_c': 40889.0, 'oxa_c': 680528.0, 'gly_c': 231965.0, 'ascb_L_c': 683.0, 'glc_D_c': 84624.0, 'citr_L_c': 2349.0, 'lnlnca_c': 2223.0, 'xylt_c': 2024.0, 'acmana_c': 9612.0, 'tre_c': 661.0, 'ser_L_c': 545280.0, 'fum_c': 188815.0, 'tyr_L_c': 4353.0, 'tym_c': 37325.0, 'trp_L_c': 2823.0, 'hdca_c': 4414.0, 'xyl_D_c': 19287.0, 'thmpp_c': 86975.0, 'mal_L_c': 29501.0, 'lnlc_c': 259.0, 'ethamp_c': 3307.0, 'dca_c': 6833.0, 'pro_L_c': 689869.0, 'met_L_c': 4743.0, 'ddca_c': 23058.0, 'adn_c': 579.0, 'ocdca_c': 18516.0, '5oxpro_c': 759993.0, 'ttdca_c': 676.0, 'C01601_c': 14585.0, 'val_L_c': 24285.0, 'glyc_R_c': 10516.0, 'spmd_c': 632.0, 'ile_L_c': 4651.0, 'ala_B_c': 6061.0, 'glcn_c': 301.0, 'arg_L_c': 16177.0, 'orn_c': 7906.0, 'lac_L_c': 88333.0, 'cit_c': 7725.0, 'akg_c': 2120.0, 'succ_c': 13879.0}}, 'LabF_115893': {'Label': 'None', 'Metabolites': {'leu_L_c': 8781.0, 'adpac_c': 3536.0, 'g6p_c': 7714.0, 'glu_L_c': 284022.0, 'dhdascb_c': 133263.0, 'amp_c': 1678.0, 'phe_L_c': 3618.0, 'thr_L_c': 26770.0, 'oxa_c': 973531.0, 'gly_c': 331879.0, 'ascb_L_c': 387.0, 'glc_D_c': 109888.0, 'citr_L_c': 3277.0, 'lnlnca_c': 5935.0, 'xylt_c': 1915.0, 'acmana_c': 7834.0, 'tre_c': 755.0, 'ser_L_c': 375771.0, 'fum_c': 89512.0, 'tyr_L_c': 3709.0, 'tym_c': 24990.0, 'trp_L_c': 1581.0, 'hdca_c': 7422.0, 'xyl_D_c': 15731.0, 'thmpp_c': 62711.0, 'mal_L_c': 19686.0, 'lnlc_c': 576.0, 'ethamp_c': 1780.0, 'dca_c': 6027.0, 'pro_L_c': 632790.0, 'met_L_c': 3662.0, 'ddca_c': 10012.0, 'adn_c': 303.0, 'ocdca_c': 25586.0, '5oxpro_c': 603169.0, 'ttdca_c': 825.0, 'C01601_c': 17109.0, 'val_L_c': 48098.0, 'glyc_R_c': 5116.0, 'spmd_c': 520.0, 'ile_L_c': 12732.0, 'ala_B_c': 2600.0, 'glcn_c': 221.0, 'arg_L_c': 23398.0, 'orn_c': 22134.0, 'lac_L_c': 95616.0, 'cit_c': 10321.0, 'akg_c': 1764.0, 'succ_c': 51367.0}}, 'LabF_115914': {'Label': 'None', 'Metabolites': {'leu_L_c': 4826.0, 'adpac_c': 2149.0, 'g6p_c': 6073.0, 'glu_L_c': 374337.0, 'dhdascb_c': 174967.0, 'amp_c': 2204.0, 'phe_L_c': 3964.0, 'thr_L_c': 63729.0, 'oxa_c': 274058.0, 'gly_c': 635325.0, 'ascb_L_c': 487.0, 'glc_D_c': 142576.0, 'citr_L_c': 3014.0, 'lnlnca_c': 5217.0, 'xylt_c': 2368.0, 'acmana_c': 8893.0, 'tre_c': 380.0, 'ser_L_c': 718520.0, 'fum_c': 184596.0, 'tyr_L_c': 3641.0, 'tym_c': 29692.0, 'trp_L_c': 1668.0, 'hdca_c': 5962.0, 'xyl_D_c': 19778.0, 'thmpp_c': 100027.0, 'mal_L_c': 23031.0, 'lnlc_c': 706.0, 'ethamp_c': 2719.0, 'dca_c': 4901.0, 'pro_L_c': 614460.0, 'met_L_c': 4296.0, 'ddca_c': 7524.0, 'adn_c': 575.0, 'ocdca_c': 20073.0, '5oxpro_c': 623933.0, 'ttdca_c': 550.0, 'C01601_c': 22707.0, 'val_L_c': 28678.0, 'glyc_R_c': 18593.0, 'spmd_c': 644.0, 'ile_L_c': 5807.0, 'ala_B_c': 5716.0, 'glcn_c': 270.0, 'arg_L_c': 24339.0, 'orn_c': 18675.0, 'lac_L_c': 23815.0, 'cit_c': 5743.0, 'akg_c': 1881.0, 'succ_c': 58216.0}}, 'LabF_115878': {'Label': 'None', 'Metabolites': {'leu_L_c': 2866.0, 'adpac_c': 2046.0, 'g6p_c': 7291.0, 'glu_L_c': 242858.0, 'dhdascb_c': 206360.0, 'amp_c': 2236.0, 'phe_L_c': 3604.0, 'thr_L_c': 73167.0, 'oxa_c': 721940.0, 'gly_c': 594793.0, 'ascb_L_c': 1047.0, 'glc_D_c': 66700.0, 'citr_L_c': 2986.0, 'lnlnca_c': 2559.0, 'xylt_c': 2296.0, 'acmana_c': 11870.0, 'tre_c': 310.0, 'ser_L_c': 926506.0, 'fum_c': 500610.0, 'tyr_L_c': 4024.0, 'tym_c': 28514.0, 'trp_L_c': 2712.0, 'hdca_c': 4010.0, 'xyl_D_c': 20273.0, 'thmpp_c': 60620.0, 'mal_L_c': 40602.0, 'lnlc_c': 237.0, 'ethamp_c': 3090.0, 'dca_c': 4854.0, 'pro_L_c': 40136.0, 'met_L_c': 3073.0, 'ddca_c': 8393.0, 'adn_c': 370.0, 'ocdca_c': 16132.0, '5oxpro_c': 888501.0, 'ttdca_c': 636.0, 'C01601_c': 30651.0, 'val_L_c': 11073.0, 'glyc_R_c': 18710.0, 'spmd_c': 460.0, 'ile_L_c': 1148.0, 'ala_B_c': 6383.0, 'glcn_c': 329.0, 'arg_L_c': 24611.0, 'orn_c': 4845.0, 'lac_L_c': 44010.0, 'cit_c': 5312.0, 'akg_c': 1680.0, 'succ_c': 23526.0}}, 'LabF_115811': {'Label': 'None', 'Metabolites': {'leu_L_c': 8338.0, 'adpac_c': 2418.0, 'g6p_c': 7104.0, 'glu_L_c': 431890.0, 'dhdascb_c': 217051.0, 'amp_c': 2434.0, 'phe_L_c': 6150.0, 'thr_L_c': 50225.0, 'oxa_c': 71021.0, 'gly_c': 278803.0, 'ascb_L_c': 610.0, 'glc_D_c': 115681.0, 'citr_L_c': 2693.0, 'lnlnca_c': 4085.0, 'xylt_c': 2579.0, 'acmana_c': 12707.0, 'tre_c': 1568.0, 'ser_L_c': 465113.0, 'fum_c': 110148.0, 'tyr_L_c': 5941.0, 'tym_c': 29378.0, 'trp_L_c': 4130.0, 'hdca_c': 6542.0, 'xyl_D_c': 19115.0, 'thmpp_c': 135122.0, 'mal_L_c': 31796.0, 'lnlc_c': 601.0, 'ethamp_c': 4261.0, 'dca_c': 5194.0, 'pro_L_c': 697857.0, 'met_L_c': 5649.0, 'ddca_c': 23806.0, 'adn_c': 590.0, 'ocdca_c': 22315.0, '5oxpro_c': 739682.0, 'ttdca_c': 904.0, 'C01601_c': 12992.0, 'val_L_c': 26157.0, 'glyc_R_c': 7769.0, 'spmd_c': 522.0, 'ile_L_c': 6040.0, 'ala_B_c': 5625.0, 'glcn_c': 371.0, 'arg_L_c': 22417.0, 'orn_c': 16679.0, 'lac_L_c': 58535.0, 'cit_c': 7069.0, 'akg_c': 2284.0, 'succ_c': 34014.0}}, 'LabF_115883': {'Label': 'None', 'Metabolites': {'leu_L_c': 13918.0, 'adpac_c': 1306.0, 'g6p_c': 3991.0, 'glu_L_c': 349891.0, 'dhdascb_c': 178303.0, 'amp_c': 2106.0, 'phe_L_c': 5805.0, 'thr_L_c': 57130.0, 'oxa_c': 168441.0, 'gly_c': 652762.0, 'ascb_L_c': 734.0, 'glc_D_c': 100977.0, 'citr_L_c': 3621.0, 'lnlnca_c': 2352.0, 'xylt_c': 1765.0, 'acmana_c': 13643.0, 'tre_c': 847.0, 'ser_L_c': 674347.0, 'fum_c': 158461.0, 'tyr_L_c': 7245.0, 'tym_c': 17348.0, 'trp_L_c': 4033.0, 'hdca_c': 3880.0, 'xyl_D_c': 15664.0, 'thmpp_c': 129478.0, 'mal_L_c': 23053.0, 'lnlc_c': 231.0, 'ethamp_c': 4620.0, 'dca_c': 3298.0, 'pro_L_c': 508665.0, 'met_L_c': 3366.0, 'ddca_c': 7642.0, 'adn_c': 479.0, 'ocdca_c': 15169.0, '5oxpro_c': 871614.0, 'ttdca_c': 513.0, 'C01601_c': 16961.0, 'val_L_c': 28215.0, 'glyc_R_c': 7727.0, 'spmd_c': 1343.0, 'ile_L_c': 6480.0, 'ala_B_c': 5422.0, 'glcn_c': 250.0, 'arg_L_c': 23768.0, 'orn_c': 17253.0, 'lac_L_c': 51704.0, 'cit_c': 2832.0, 'akg_c': 1003.0, 'succ_c': 19171.0}}, 'LabF_115924': {'Label': 'None', 'Metabolites': {'leu_L_c': 9093.0, 'adpac_c': 2375.0, 'g6p_c': 6173.0, 'glu_L_c': 290242.0, 'dhdascb_c': 148727.0, 'amp_c': 2927.0, 'phe_L_c': 4678.0, 'thr_L_c': 41211.0, 'oxa_c': 72728.0, 'gly_c': 425955.0, 'ascb_L_c': 604.0, 'glc_D_c': 144382.0, 'citr_L_c': 1790.0, 'lnlnca_c': 1589.0, 'xylt_c': 2009.0, 'acmana_c': 9162.0, 'tre_c': 1266.0, 'ser_L_c': 427588.0, 'fum_c': 132217.0, 'tyr_L_c': 4907.0, 'tym_c': 25663.0, 'trp_L_c': 2660.0, 'hdca_c': 3631.0, 'xyl_D_c': 17589.0, 'thmpp_c': 59530.0, 'mal_L_c': 24816.0, 'lnlc_c': 216.0, 'ethamp_c': 3871.0, 'dca_c': 5971.0, 'pro_L_c': 616372.0, 'met_L_c': 3919.0, 'ddca_c': 24186.0, 'adn_c': 971.0, 'ocdca_c': 19975.0, '5oxpro_c': 918287.0, 'ttdca_c': 631.0, 'C01601_c': 13759.0, 'val_L_c': 22212.0, 'glyc_R_c': 12929.0, 'spmd_c': 522.0, 'ile_L_c': 2819.0, 'ala_B_c': 4699.0, 'glcn_c': 419.0, 'arg_L_c': 16368.0, 'orn_c': 4829.0, 'lac_L_c': 100337.0, 'cit_c': 5398.0, 'akg_c': 2649.0, 'succ_c': 74984.0}}, 'LabF_115842': {'Label': 'None', 'Metabolites': {'leu_L_c': 7991.0, 'adpac_c': 8451.0, 'g6p_c': 8445.0, 'glu_L_c': 261095.0, 'dhdascb_c': 182455.0, 'amp_c': 2386.0, 'phe_L_c': 5365.0, 'thr_L_c': 78700.0, 'oxa_c': 49907.0, 'gly_c': 648700.0, 'ascb_L_c': 905.0, 'glc_D_c': 92079.0, 'citr_L_c': 3565.0, 'lnlnca_c': 2355.0, 'xylt_c': 2236.0, 'acmana_c': 9875.0, 'tre_c': 446.0, 'ser_L_c': 816033.0, 'fum_c': 175204.0, 'tyr_L_c': 4608.0, 'tym_c': 25149.0, 'trp_L_c': 3507.0, 'hdca_c': 4676.0, 'xyl_D_c': 14826.0, 'thmpp_c': 52857.0, 'mal_L_c': 27956.0, 'lnlc_c': 228.0, 'ethamp_c': 3709.0, 'dca_c': 3709.0, 'pro_L_c': 303440.0, 'met_L_c': 3818.0, 'ddca_c': 4576.0, 'adn_c': 132.0, 'ocdca_c': 21463.0, '5oxpro_c': 791296.0, 'ttdca_c': 642.0, 'C01601_c': 15370.0, 'val_L_c': 47124.0, 'glyc_R_c': 18720.0, 'spmd_c': 376.0, 'ile_L_c': 8209.0, 'ala_B_c': 8823.0, 'glcn_c': 222.0, 'arg_L_c': 27827.0, 'orn_c': 11339.0, 'lac_L_c': 96975.0, 'cit_c': 4078.0, 'akg_c': 1752.0, 'succ_c': 62656.0}}, 'LabF_115909': {'Label': 'None', 'Metabolites': {'leu_L_c': 5624.0, 'adpac_c': 8148.0, 'g6p_c': 6826.0, 'glu_L_c': 365318.0, 'dhdascb_c': 163491.0, 'amp_c': 1650.0, 'phe_L_c': 4165.0, 'thr_L_c': 47266.0, 'oxa_c': 415520.0, 'gly_c': 784923.0, 'ascb_L_c': 759.0, 'glc_D_c': 121027.0, 'citr_L_c': 2444.0, 'lnlnca_c': 1844.0, 'xylt_c': 2148.0, 'acmana_c': 10403.0, 'tre_c': 531.0, 'ser_L_c': 688606.0, 'fum_c': 184728.0, 'tyr_L_c': 2811.0, 'tym_c': 29092.0, 'trp_L_c': 1649.0, 'hdca_c': 4482.0, 'xyl_D_c': 19019.0, 'thmpp_c': 67792.0, 'mal_L_c': 27875.0, 'lnlc_c': 276.0, 'ethamp_c': 2123.0, 'dca_c': 6204.0, 'pro_L_c': 626729.0, 'met_L_c': 3740.0, 'ddca_c': 11080.0, 'adn_c': 407.0, 'ocdca_c': 16439.0, '5oxpro_c': 905941.0, 'ttdca_c': 769.0, 'C01601_c': 20855.0, 'val_L_c': 25444.0, 'glyc_R_c': 15850.0, 'spmd_c': 488.0, 'ile_L_c': 4686.0, 'ala_B_c': 5185.0, 'glcn_c': 324.0, 'arg_L_c': 23914.0, 'orn_c': 4015.0, 'lac_L_c': 88356.0, 'cit_c': 8376.0, 'akg_c': 1705.0, 'succ_c': 36752.0}}, 'LabF_115929': {'Label': 'None', 'Metabolites': {'leu_L_c': 8626.0, 'adpac_c': 2368.0, 'g6p_c': 8279.0, 'glu_L_c': 240590.0, 'dhdascb_c': 192104.0, 'amp_c': 3657.0, 'phe_L_c': 4293.0, 'thr_L_c': 39036.0, 'oxa_c': 117162.0, 'gly_c': 266472.0, 'ascb_L_c': 510.0, 'glc_D_c': 258037.0, 'citr_L_c': 3062.0, 'lnlnca_c': 2827.0, 'xylt_c': 2047.0, 'acmana_c': 9919.0, 'tre_c': 1286.0, 'ser_L_c': 512823.0, 'fum_c': 144991.0, 'tyr_L_c': 3879.0, 'tym_c': 35481.0, 'trp_L_c': 2603.0, 'hdca_c': 5304.0, 'xyl_D_c': 20297.0, 'thmpp_c': 77524.0, 'mal_L_c': 26583.0, 'lnlc_c': 593.0, 'ethamp_c': 3392.0, 'dca_c': 6826.0, 'pro_L_c': 558396.0, 'met_L_c': 5493.0, 'ddca_c': 21115.0, 'adn_c': 582.0, 'ocdca_c': 24793.0, '5oxpro_c': 839227.0, 'ttdca_c': 672.0, 'C01601_c': 23200.0, 'val_L_c': 26852.0, 'glyc_R_c': 12192.0, 'spmd_c': 518.0, 'ile_L_c': 4928.0, 'ala_B_c': 5249.0, 'glcn_c': 391.0, 'arg_L_c': 38112.0, 'orn_c': 13195.0, 'lac_L_c': 143155.0, 'cit_c': 6015.0, 'akg_c': 3516.0, 'succ_c': 14067.0}}, 'LabF_115816': {'Label': 'None', 'Metabolites': {'leu_L_c': 7767.0, 'adpac_c': 2380.0, 'g6p_c': 5588.0, 'glu_L_c': 405053.0, 'dhdascb_c': 242998.0, 'amp_c': 2732.0, 'phe_L_c': 6371.0, 'thr_L_c': 57689.0, 'oxa_c': 79621.0, 'gly_c': 181015.0, 'ascb_L_c': 1113.0, 'glc_D_c': 108577.0, 'citr_L_c': 3129.0, 'lnlnca_c': 3361.0, 'xylt_c': 2759.0, 'acmana_c': 14185.0, 'tre_c': 993.0, 'ser_L_c': 470295.0, 'fum_c': 178780.0, 'tyr_L_c': 5143.0, 'tym_c': 32269.0, 'trp_L_c': 4985.0, 'hdca_c': 6372.0, 'xyl_D_c': 24288.0, 'thmpp_c': 119269.0, 'mal_L_c': 37006.0, 'lnlc_c': 607.0, 'ethamp_c': 3769.0, 'dca_c': 5444.0, 'pro_L_c': 532747.0, 'met_L_c': 6204.0, 'ddca_c': 7801.0, 'adn_c': 745.0, 'ocdca_c': 23408.0, '5oxpro_c': 782510.0, 'ttdca_c': 662.0, 'C01601_c': 20343.0, 'val_L_c': 24596.0, 'glyc_R_c': 10492.0, 'spmd_c': 745.0, 'ile_L_c': 5158.0, 'ala_B_c': 5964.0, 'glcn_c': 495.0, 'arg_L_c': 32062.0, 'orn_c': 12493.0, 'lac_L_c': 100045.0, 'cit_c': 8227.0, 'akg_c': 3182.0, 'succ_c': 35576.0}}, 'LabF_115847': {'Label': 'None', 'Metabolites': {'leu_L_c': 25723.0, 'adpac_c': 2612.0, 'g6p_c': 7871.0, 'glu_L_c': 230805.0, 'dhdascb_c': 155475.0, 'amp_c': 2418.0, 'phe_L_c': 6196.0, 'thr_L_c': 65136.0, 'oxa_c': 53545.0, 'gly_c': 692392.0, 'ascb_L_c': 1240.0, 'glc_D_c': 95939.0, 'citr_L_c': 3558.0, 'lnlnca_c': 3128.0, 'xylt_c': 1384.0, 'acmana_c': 8621.0, 'tre_c': 505.0, 'ser_L_c': 769579.0, 'fum_c': 271269.0, 'tyr_L_c': 5932.0, 'tym_c': 25950.0, 'trp_L_c': 5148.0, 'hdca_c': 5208.0, 'xyl_D_c': 5655.0, 'thmpp_c': 48402.0, 'mal_L_c': 28323.0, 'lnlc_c': 335.0, 'ethamp_c': 4176.0, 'dca_c': 3089.0, 'pro_L_c': 113179.0, 'met_L_c': 3462.0, 'ddca_c': 3973.0, 'adn_c': 133.0, 'ocdca_c': 22911.0, '5oxpro_c': 895021.0, 'ttdca_c': 515.0, 'C01601_c': 32043.0, 'val_L_c': 35787.0, 'glyc_R_c': 19913.0, 'spmd_c': 480.0, 'ile_L_c': 6224.0, 'ala_B_c': 40246.0, 'glcn_c': 396.0, 'arg_L_c': 25459.0, 'orn_c': 17873.0, 'lac_L_c': 106792.0, 'cit_c': 5188.0, 'akg_c': 1875.0, 'succ_c': 39767.0}}, 'LabF_115867': {'Label': 'None', 'Metabolites': {'leu_L_c': 8408.0, 'adpac_c': 2894.0, 'g6p_c': 7566.0, 'glu_L_c': 241988.0, 'dhdascb_c': 215698.0, 'amp_c': 2347.0, 'phe_L_c': 5337.0, 'thr_L_c': 89417.0, 'oxa_c': 58690.0, 'gly_c': 527648.0, 'ascb_L_c': 1043.0, 'glc_D_c': 66419.0, 'citr_L_c': 3483.0, 'lnlnca_c': 2853.0, 'xylt_c': 2051.0, 'acmana_c': 8871.0, 'tre_c': 553.0, 'ser_L_c': 908471.0, 'fum_c': 239205.0, 'tyr_L_c': 4504.0, 'tym_c': 32271.0, 'trp_L_c': 4415.0, 'hdca_c': 4951.0, 'xyl_D_c': 5634.0, 'thmpp_c': 69736.0, 'mal_L_c': 27643.0, 'lnlc_c': 434.0, 'ethamp_c': 4752.0, 'dca_c': 2685.0, 'pro_L_c': 467792.0, 'met_L_c': 3848.0, 'ddca_c': 3704.0, 'adn_c': 118.0, 'ocdca_c': 19541.0, '5oxpro_c': 827264.0, 'ttdca_c': 902.0, 'C01601_c': 12548.0, 'val_L_c': 38790.0, 'glyc_R_c': 12734.0, 'spmd_c': 510.0, 'ile_L_c': 8133.0, 'ala_B_c': 6983.0, 'glcn_c': 509.0, 'arg_L_c': 24915.0, 'orn_c': 12014.0, 'lac_L_c': 40463.0, 'cit_c': 4555.0, 'akg_c': 1433.0, 'succ_c': 37686.0}}, 'LabF_115852': {'Label': 'None', 'Metabolites': {'leu_L_c': 7452.0, 'adpac_c': 2786.0, 'g6p_c': 7236.0, 'glu_L_c': 190516.0, 'dhdascb_c': 211644.0, 'amp_c': 2160.0, 'phe_L_c': 7044.0, 'thr_L_c': 73347.0, 'oxa_c': 37942.0, 'gly_c': 798504.0, 'ascb_L_c': 1012.0, 'glc_D_c': 57378.0, 'citr_L_c': 2986.0, 'lnlnca_c': 1008.0, 'xylt_c': 1960.0, 'acmana_c': 11477.0, 'tre_c': 600.0, 'ser_L_c': 893830.0, 'fum_c': 220884.0, 'tyr_L_c': 5030.0, 'tym_c': 33297.0, 'trp_L_c': 4913.0, 'hdca_c': 6782.0, 'xyl_D_c': 16090.0, 'thmpp_c': 114719.0, 'mal_L_c': 28101.0, 'lnlc_c': 428.0, 'ethamp_c': 4823.0, 'dca_c': 2897.0, 'pro_L_c': 181588.0, 'met_L_c': 3648.0, 'ddca_c': 3857.0, 'adn_c': 79.0, 'ocdca_c': 41983.0, '5oxpro_c': 818768.0, 'ttdca_c': 651.0, 'C01601_c': 28704.0, 'val_L_c': 42002.0, 'glyc_R_c': 16046.0, 'spmd_c': 898.0, 'ile_L_c': 6464.0, 'ala_B_c': 8547.0, 'glcn_c': 343.0, 'arg_L_c': 26485.0, 'orn_c': 16990.0, 'lac_L_c': 80325.0, 'cit_c': 6140.0, 'akg_c': 1548.0, 'succ_c': 29414.0}}, 'LabF_115888': {'Label': 'None', 'Metabolites': {'leu_L_c': 3365.0, 'adpac_c': 1200.0, 'g6p_c': 4484.0, 'glu_L_c': 340639.0, 'dhdascb_c': 178766.0, 'amp_c': 2518.0, 'phe_L_c': 4362.0, 'thr_L_c': 72739.0, 'oxa_c': 737457.0, 'gly_c': 700994.0, 'ascb_L_c': 586.0, 'glc_D_c': 79389.0, 'citr_L_c': 3047.0, 'lnlnca_c': 3225.0, 'xylt_c': 1871.0, 'acmana_c': 11833.0, 'tre_c': 470.0, 'ser_L_c': 749637.0, 'fum_c': 579266.0, 'tyr_L_c': 4325.0, 'tym_c': 18077.0, 'trp_L_c': 2668.0, 'hdca_c': 5268.0, 'xyl_D_c': 20996.0, 'thmpp_c': 84727.0, 'mal_L_c': 31273.0, 'lnlc_c': 374.0, 'ethamp_c': 3175.0, 'dca_c': 3723.0, 'pro_L_c': 311821.0, 'met_L_c': 3447.0, 'ddca_c': 6233.0, 'adn_c': 435.0, 'ocdca_c': 15178.0, '5oxpro_c': 574950.0, 'ttdca_c': 479.0, 'C01601_c': 26450.0, 'val_L_c': 22162.0, 'glyc_R_c': 19606.0, 'spmd_c': 428.0, 'ile_L_c': 4048.0, 'ala_B_c': 4966.0, 'glcn_c': 234.0, 'arg_L_c': 26265.0, 'orn_c': 22555.0, 'lac_L_c': 20864.0, 'cit_c': 2982.0, 'akg_c': 1622.0, 'succ_c': 37881.0}}, 'LabF_115919': {'Label': 'None', 'Metabolites': {'leu_L_c': 3223.0, 'adpac_c': 1860.0, 'g6p_c': 5703.0, 'glu_L_c': 361825.0, 'dhdascb_c': 117739.0, 'amp_c': 2454.0, 'phe_L_c': 4688.0, 'thr_L_c': 43732.0, 'oxa_c': 60405.0, 'gly_c': 724624.0, 'ascb_L_c': 470.0, 'glc_D_c': 156785.0, 'citr_L_c': 3720.0, 'lnlnca_c': 3674.0, 'xylt_c': 1604.0, 'acmana_c': 10845.0, 'tre_c': 1373.0, 'ser_L_c': 487692.0, 'fum_c': 125947.0, 'tyr_L_c': 5462.0, 'tym_c': 18148.0, 'trp_L_c': 2928.0, 'hdca_c': 5267.0, 'xyl_D_c': 18874.0, 'thmpp_c': 147016.0, 'mal_L_c': 19725.0, 'lnlc_c': 486.0, 'ethamp_c': 4196.0, 'dca_c': 3913.0, 'pro_L_c': 997543.0, 'met_L_c': 2929.0, 'ddca_c': 11814.0, 'adn_c': 450.0, 'ocdca_c': 20793.0, '5oxpro_c': 818811.0, 'ttdca_c': 530.0, 'C01601_c': 21336.0, 'val_L_c': 16310.0, 'glyc_R_c': 5239.0, 'spmd_c': 380.0, 'ile_L_c': 4325.0, 'ala_B_c': 4356.0, 'glcn_c': 883.0, 'arg_L_c': 23111.0, 'orn_c': 26214.0, 'lac_L_c': 61129.0, 'cit_c': 2846.0, 'akg_c': 2752.0, 'succ_c': 127485.0}}, 'LabF_115857': {'Label': 'None', 'Metabolites': {'leu_L_c': 5047.0, 'adpac_c': 3689.0, 'g6p_c': 6764.0, 'glu_L_c': 216632.0, 'dhdascb_c': 195527.0, 'amp_c': 2139.0, 'phe_L_c': 5143.0, 'thr_L_c': 63272.0, 'oxa_c': 184586.0, 'gly_c': 718573.0, 'ascb_L_c': 938.0, 'glc_D_c': 54473.0, 'citr_L_c': 3325.0, 'lnlnca_c': 2239.0, 'xylt_c': 415.0, 'acmana_c': 9608.0, 'tre_c': 7826.0, 'ser_L_c': 924261.0, 'fum_c': 299784.0, 'tyr_L_c': 5146.0, 'tym_c': 23469.0, 'trp_L_c': 3265.0, 'hdca_c': 5345.0, 'xyl_D_c': 9212.0, 'thmpp_c': 58672.0, 'mal_L_c': 35638.0, 'lnlc_c': 308.0, 'ethamp_c': 2957.0, 'dca_c': 2131.0, 'pro_L_c': 211130.0, 'met_L_c': 3446.0, 'ddca_c': 4008.0, 'adn_c': 105.0, 'ocdca_c': 21168.0, '5oxpro_c': 896779.0, 'ttdca_c': 713.0, 'C01601_c': 20758.0, 'val_L_c': 38906.0, 'glyc_R_c': 21631.0, 'spmd_c': 169.0, 'ile_L_c': 6427.0, 'ala_B_c': 85013.0, 'glcn_c': 259.0, 'arg_L_c': 23088.0, 'orn_c': 14695.0, 'lac_L_c': 60249.0, 'cit_c': 4752.0, 'akg_c': 1677.0, 'succ_c': 26390.0}}, 'LabF_115831': {'Label': 'None', 'Metabolites': {'leu_L_c': 8635.0, 'adpac_c': 2482.0, 'g6p_c': 7565.0, 'glu_L_c': 208333.0, 'dhdascb_c': 176201.0, 'amp_c': 3291.0, 'phe_L_c': 5480.0, 'thr_L_c': 65762.0, 'oxa_c': 103466.0, 'gly_c': 407513.0, 'ascb_L_c': 888.0, 'glc_D_c': 59201.0, 'citr_L_c': 3654.0, 'lnlnca_c': 2290.0, 'xylt_c': 2467.0, 'acmana_c': 13234.0, 'tre_c': 605.0, 'ser_L_c': 694837.0, 'fum_c': 150350.0, 'tyr_L_c': 4127.0, 'tym_c': 26920.0, 'trp_L_c': 3679.0, 'hdca_c': 5714.0, 'xyl_D_c': 17742.0, 'thmpp_c': 78221.0, 'mal_L_c': 26454.0, 'lnlc_c': 355.0, 'ethamp_c': 7288.0, 'dca_c': 5208.0, 'pro_L_c': 307140.0, 'met_L_c': 5752.0, 'ddca_c': 8879.0, 'adn_c': 408.0, 'ocdca_c': 27789.0, '5oxpro_c': 1233805.0, 'ttdca_c': 759.0, 'C01601_c': 19633.0, 'val_L_c': 24158.0, 'glyc_R_c': 1564.0, 'spmd_c': 651.0, 'ile_L_c': 5212.0, 'ala_B_c': 6287.0, 'glcn_c': 231.0, 'arg_L_c': 50264.0, 'orn_c': 12241.0, 'lac_L_c': 156853.0, 'cit_c': 5044.0, 'akg_c': 1818.0, 'succ_c': 91920.0}}, 'LabF_115836': {'Label': 'None', 'Metabolites': {'leu_L_c': 9063.0, 'adpac_c': 1843.0, 'g6p_c': 7878.0, 'glu_L_c': 202302.0, 'dhdascb_c': 192702.0, 'amp_c': 3217.0, 'phe_L_c': 7063.0, 'thr_L_c': 34745.0, 'oxa_c': 75306.0, 'gly_c': 243905.0, 'ascb_L_c': 948.0, 'glc_D_c': 151306.0, 'citr_L_c': 5738.0, 'lnlnca_c': 4148.0, 'xylt_c': 2439.0, 'acmana_c': 14923.0, 'tre_c': 1001.0, 'ser_L_c': 324449.0, 'fum_c': 71969.0, 'tyr_L_c': 5516.0, 'tym_c': 31206.0, 'trp_L_c': 4524.0, 'hdca_c': 7292.0, 'xyl_D_c': 21555.0, 'thmpp_c': 192159.0, 'mal_L_c': 22466.0, 'lnlc_c': 633.0, 'ethamp_c': 5881.0, 'dca_c': 3785.0, 'pro_L_c': 384956.0, 'met_L_c': 5657.0, 'ddca_c': 10127.0, 'adn_c': 417.0, 'ocdca_c': 24533.0, '5oxpro_c': 1021155.0, 'ttdca_c': 588.0, 'C01601_c': 11662.0, 'val_L_c': 25672.0, 'glyc_R_c': 7033.0, 'spmd_c': 695.0, 'ile_L_c': 4844.0, 'ala_B_c': 4960.0, 'glcn_c': 406.0, 'arg_L_c': 46282.0, 'orn_c': 43280.0, 'lac_L_c': 99844.0, 'cit_c': 4832.0, 'akg_c': 1889.0, 'succ_c': 29028.0}}, 'LabF_115862': {'Label': 'None', 'Metabolites': {'leu_L_c': 4977.0, 'adpac_c': 2318.0, 'g6p_c': 6048.0, 'glu_L_c': 224913.0, 'dhdascb_c': 167064.0, 'amp_c': 2055.0, 'phe_L_c': 5971.0, 'thr_L_c': 77425.0, 'oxa_c': 600349.0, 'gly_c': 827500.0, 'ascb_L_c': 859.0, 'glc_D_c': 46548.0, 'citr_L_c': 3017.0, 'lnlnca_c': 3063.0, 'xylt_c': 1436.0, 'acmana_c': 9918.0, 'tre_c': 728.0, 'ser_L_c': 900614.0, 'fum_c': 237302.0, 'tyr_L_c': 4189.0, 'tym_c': 19259.0, 'trp_L_c': 3681.0, 'hdca_c': 5154.0, 'xyl_D_c': 5242.0, 'thmpp_c': 65792.0, 'mal_L_c': 26344.0, 'lnlc_c': 458.0, 'ethamp_c': 4190.0, 'dca_c': 2779.0, 'pro_L_c': 386358.0, 'met_L_c': 3358.0, 'ddca_c': 3237.0, 'adn_c': 112.0, 'ocdca_c': 18964.0, '5oxpro_c': 842520.0, 'ttdca_c': 508.0, 'C01601_c': 26166.0, 'val_L_c': 29708.0, 'glyc_R_c': 17121.0, 'spmd_c': 556.0, 'ile_L_c': 6143.0, 'ala_B_c': 27673.0, 'glcn_c': 265.0, 'arg_L_c': 20565.0, 'orn_c': 15741.0, 'lac_L_c': 40715.0, 'cit_c': 3322.0, 'akg_c': 1364.0, 'succ_c': 41740.0}}}}
# sample_data = {'study_name': 'Public Test', 'group': 'healthy', 'analysis': {'P4': {'Label': 'breast cancer', 'Metabolites': {'g1p_c': 0.765, 'CE5795_c': 0.765, 'doco13ecoa_c': 0, '3mox4hpac_c': 0.765, 'CE7086_c': 0, 'CE2172_c': 0.432, 'appnn_c': 0, 'retinol_cis_11_c': 0.75443, 'dmgly_c': 0.654323, 'CE5794_c': 0, 'CE2102_c': 0, 'vitd3_c': 0.75443, 'HC02202_c': 0.123, 'tagat_D_c': 0.3423, 'tcynt_c': 0, 'CE7087_c': 0, 'hista_c': 0.75443, 'n8aspmd_c': 0, 'hmbil_c': 0.654323, 'antipyrene_c': 0.654323, 'fe2_c': 0, 'nrvnccoa_c': 0, 'din_c': 0, 'CE2838_c': 0, 'HC01842_c': 0, 'CE2122_c': 0.123, 'CE5072_c': 0, 'CE5796_c': 0, 'ahandrostanglc_c': 0, 'HC01797_c': 0}}, 'P5': {'Label': 'healthy', 'Metabolites': {'g1p_c': 0, 'CE5795_c': 0.765, 'doco13ecoa_c': 0.75443, '3mox4hpac_c': 0.654323, 'CE7086_c': 0, 'CE2172_c': 0.234, 'appnn_c': 0, 'retinol_cis_11_c': 0, 'dmgly_c': 0, 'CE5794_c': 0.3423, 'CE2102_c': 0.657, 'vitd3_c': 0, 'HC02202_c': 0.321, 'tagat_D_c': 0, 'tcynt_c': 0.654323, 'CE7087_c': 0, 'hista_c': 0, 'n8aspmd_c': 0.654323, 'hmbil_c': 0, 'antipyrene_c': 0, 'fe2_c': 0.75443, 'nrvnccoa_c': 0.123, 'din_c': 0.75443, 'CE2838_c': 0, 'HC01842_c': 0.123, 'CE2122_c': 0, 'CE5072_c': 0.75443, 'CE5796_c': 0, 'ahandrostanglc_c': 0, 'HC01797_c': 0}}, 'P3': {'Label': 'breast cancer', 'Metabolites': {'g1p_c': 0, 'CE5795_c': 0, 'doco13ecoa_c': 0, '3mox4hpac_c': 0, 'CE7086_c': 0.657, 'CE2172_c': 0, 'appnn_c': 0.75443, 'retinol_cis_11_c': 0, 'dmgly_c': 0, 'CE5794_c': 0, 'CE2102_c': 0, 'vitd3_c': 0.123, 'HC02202_c': 0, 'tagat_D_c': 0.654323, 'tcynt_c': 0, 'CE7087_c': 0, 'hista_c': 0, 'n8aspmd_c': 0.654323, 'hmbil_c': 0.654323, 'antipyrene_c': 0.654323, 'fe2_c': 0, 'nrvnccoa_c': 0, 'din_c': 0, 'CE2838_c': 0, 'HC01842_c': 0, 'CE2122_c': 0, 'CE5072_c': 0, 'CE5796_c': 0, 'ahandrostanglc_c': 0.654323, 'HC01797_c': 0.123}}, 'P2': {'Label': 'breast cancer', 'Metabolites': {'g1p_c': 0.765, 'CE5795_c': 0, 'doco13ecoa_c': 0, '3mox4hpac_c': 0.654323, 'CE7086_c': 0.657, 'CE2172_c': 0.321, 'appnn_c': 0.75443, 'retinol_cis_11_c': 0.3423, 'dmgly_c': 0, 'CE5794_c': 0, 'CE2102_c': 0, 'vitd3_c': 0.75443, 'HC02202_c': 0, 'tagat_D_c': 0.654323, 'tcynt_c': 0.654323, 'CE7087_c': 0, 'hista_c': 0, 'n8aspmd_c': 0.654323, 'hmbil_c': 0, 'antipyrene_c': 0.654323, 'fe2_c': 0.75443, 'nrvnccoa_c': 0, 'din_c': 0, 'CE2838_c': 0.765, 'HC01842_c': 0, 'CE2122_c': 0, 'CE5072_c': 0.3423, 'CE5796_c': 0.3423, 'ahandrostanglc_c': 0.654323, 'HC01797_c': 0.3423}}, 'P7': {'Label': 'breast cancer', 'Metabolites': {'g1p_c': 0, 'CE5795_c': 0.765, 'doco13ecoa_c': 0.75443, '3mox4hpac_c': 0.654323, 'CE7086_c': 0.75443, 'CE2172_c': 0.765, 'appnn_c': 0.75443, 'retinol_cis_11_c': 0.654323, 'dmgly_c': 0.654323, 'CE5794_c': 0, 'CE2102_c': 0.657, 'vitd3_c': 0.75443, 'HC02202_c': 0, 'tagat_D_c': 0, 'tcynt_c': 0.654323, 'CE7087_c': 0, 'hista_c': 0.75443, 'n8aspmd_c': 0.654323, 'hmbil_c': 0, 'antipyrene_c': 0, 'fe2_c': 0, 'nrvnccoa_c': 0, 'din_c': 0, 'CE2838_c': 0, 'HC01842_c': 0, 'CE2122_c': 0.123, 'CE5072_c': 0, 'CE5796_c': 0, 'ahandrostanglc_c': 0, 'HC01797_c': 0.654323}}, 'P1': {'Label': 'healthy', 'Metabolites': {'g1p_c': 0, 'CE5795_c': 0, 'doco13ecoa_c': 0, '3mox4hpac_c': 0.654323, 'CE7086_c': 0.657, 'CE2172_c': 0.123, 'appnn_c': 0.75443, 'retinol_cis_11_c': 0, 'dmgly_c': 0.654323, 'CE5794_c': 0, 'CE2102_c': 0.657, 'vitd3_c': 0, 'HC02202_c': 0, 'tagat_D_c': 0, 'tcynt_c': 0, 'CE7087_c': 0, 'hista_c': 0, 'n8aspmd_c': 0, 'hmbil_c': 0, 'antipyrene_c': 0.654323, 'fe2_c': 0, 'nrvnccoa_c': 0, 'din_c': 0.75443, 'CE2838_c': 0.765, 'HC01842_c': 0.3423, 'CE2122_c': 0.453, 'CE5072_c': 0, 'CE5796_c': 0.654323, 'ahandrostanglc_c': 0, 'HC01797_c': 0}}, 'P6': {'Label': 'breast cancer', 'Metabolites': {'g1p_c': 0, 'CE5795_c': 0.765, 'doco13ecoa_c': 0, '3mox4hpac_c': 0.123, 'CE7086_c': 0, 'CE2172_c': 0.567, 'appnn_c': 0.75443, 'retinol_cis_11_c': 0, 'dmgly_c': 0, 'CE5794_c': 0.657, 'CE2102_c': 0.657, 'vitd3_c': 0.75443, 'HC02202_c': 0.432, 'tagat_D_c': 0.3423, 'tcynt_c': 0.654323, 'CE7087_c': 0.75443, 'hista_c': 0.75443, 'n8aspmd_c': 0.654323, 'hmbil_c': 0.123, 'antipyrene_c': 0, 'fe2_c': 0, 'nrvnccoa_c': 0.75443, 'din_c': 0, 'CE2838_c': 0.765, 'HC01842_c': 0, 'CE2122_c': 0, 'CE5072_c': 0, 'CE5796_c': 0, 'ahandrostanglc_c': 0.123, 'HC01797_c': 0.75443}}}}




@app.route('/analysis/fva', methods=['POST'])
@jwt_required()
def fva_analysis():
    """
    FVA analysis
    ---
    tags:
      - analysis
    parameters:
        -
          name: authorization
          in: header
          type: string
          required: true
        - in: body
          name: body
          schema:
            id: AnalysisInput
            required:
              - name
              - concentration_changes
            properties:
              name:
                  type: string
                  description: name of analysis
              concentration_changes:
                  type: object
                  description: concentration changes of metabolitics
    responses:
      200:
        description: Analysis info
      404:
        description: Analysis not found
      401:
        description: Analysis is not yours
    """

    # data = request.json  # this workspublic


    if not request.json:
        return "", 404
    # changes = request.json['concentration_changes']

    user = User.query.get(1)
    # metabolomics_data = MetabolomicsData(
    #     metabolomics_data = changes,
    #     owner_email = 'tajtest2019@gmail.com',
    #     is_public = True
    # )
    # db.session.add(metabolomics_data)
    # db.session.commit()
    study = Dataset(name=sample_data['study_name'])
    db.session.add(study)
    db.session.commit()
    for key,value in sample_data["analysis"].items():  # user as key, value {metaboldata , label}
        metabolomics_data = MetabolomicsData(
            metabolomics_data = value["Metabolites"],
            owner_email = 'alperdokay@std.sehir.edu.tr',
            # is_public = True if request.json['public'] else False
            is_public =  True
        )

        db.session.add(metabolomics_data)
        db.session.commit()

        analysis = Analysis(name=key, user=user)
        analysis.name = key
        analysis.status = True
        analysis.type = 'public'
        analysis.start_time = datetime.datetime.now()


        analysis.owner_user_id = user.id
        analysis.owner_email = user.email
        analysis.method_id = 1
        analysis.metabolomics_data_id = metabolomics_data.id
        analysis.dataset_id = 0
        # print (analysis.method_id, analysis.metabolomics_data_id)

        db.session.add(analysis)
        db.session.commit()

        save_analysis.delay(analysis.id, value["Metabolites"])
        print ("ok here")
    return jsonify({'id': analysis.id})




    # # print (analysis.method_id, analysis.metabolomics_data_id)
    #
    # db.session.add(analysis)
    # db.session.commit()
    #
    # save_analysis.delay(analysis.id, data['concentration_changes'])
    # return jsonify({'id': analysis.id})
    #
    #
    # #
    # # temp = "public" if data['public'] else "private"
    # # analysis = Analysis(
    # #     data['name'],
    # #     current_identity,
    # #     type= temp)
    # # db.session.add(analysis)
    # # db.session.commit()
    # # analysis_id = analysis.id
    # # # print (analysis_id)
    # # save_analysis.delay(analysis_id, data['concentration_changes'])
    # # return jsonify({'id': analysis_id})



@app.route('/analysis/set', methods=['POST'])
def user_analysis_set():
    """
    List of analysis of user
    ---
    tags:
        - analysis
    parameters:
        -
          name: authorization
          in: header
          type: string
          required: true
    """
    data = request.json['data']
    analyses = Analysis.get_multiple(data.values())
    print (data,'------------------>1')
    #
    # if len(analyses) != len(request.args):
    #     return '', 401
    X = [i.results_pathway for i in analyses]
    y = [i.name for i in analyses]
    # print (analyses,'------------------>2')
    return AnalysisSchema(many=True).jsonify(analyses)


@app.route('/analysis/visualization', methods=['POST'])
def analysis_visualization():
    """
    List of analysis of user
    ---
    tags:
        - analysis
    parameters:
        -
          name: authorization
          in: header
          type: string
          required: true
    """

    data = request.json['data']
    analyses = Analysis.get_multiple(data.values())
    #
    # if len(analyses) != len(request.args):
    #     return '', 401
    # X = [i.results_pathway for i in analyses]
    # y = [i.name for i in analyses]


    # analyses = list(Analysis.get_multiple(request.args.values()))
    # if len(analyses) != len(request.args):
    #     return '', 401
    X = [i.results_pathway[0] for i in analyses]

    y = [i.name for i in analyses]

    return jsonify(HeatmapVisualization(X, y).clustered_data())


# @app.route('/analysis/<type>')
# def disease_analysis(type: str):
#     """
#     List of disease analysis avaliable in db
#     ---
#     tags:
#         - analysis
#     parameters:
#         -
#           name: authorization
#           in: header
#           type: string
#           required: true
#     """
#     return AnalysisSchema(many=True).jsonify(
#         Analysis.query.filter_by(type=type).with_entities(
#             Analysis.id, Analysis.name, Analysis.status))

#
# @app.route('/analysis/detail/<id>')
# def analysis_detail1(id):
#     """
#     Get analysis detail from id
#     ---
#     tags:
#       - analysis
#     parameters:
#         -
#           name: authorization
#           in: header
#           type: string
#           required: true
#         -
#           name: id
#           in: path
#           type: integer
#           required: true
#     responses:
#       200:
#         description: Analysis info
#       404:
#         description: Analysis not found
#       401:
#         description: Analysis is not yours
#     """
    # analysis = Analysis.query.get(id)
    # if not analysis:
    #     return '', 404
    # if not analysis.authenticated():
    #     return '', 401
    # return AnalysisSchema().jsonify(analysis)

@app.route('/analysis/most-similar-diseases/<id>')
def most_similar_diseases(id: int):
    """
    Calculates most similar disease for given disease id
    ---
    tags:
      - analysis
    parameters:
      -
        name: authorization
        in: header
        type: string
        required: true
      -
        name: id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Most similar diseases
      404:
        description: Analysis not found
      401:
        description: Analysis is not yours
    """
    analysis = Analysis.query.get(id)
    if not analysis:
        return '', 404
    if not analysis.authenticated():
        return '', 401

    row_disease_analyses = Analysis.query.filter_by(
        type='disease').with_entities(Analysis.name,
                                      Analysis.results_pathway).all()

    names, disease_analyses = zip(*[(i[0], i[1][0])
                                    for i in row_disease_analyses])

    sims = similarty_dict(analysis.results_pathway[0], list(disease_analyses))
    top_5 = sorted(zip(names, sims), key=lambda x: x[1], reverse=True)[:5]

    return jsonify(dict(top_5))

@app.route('/analysis/<type>')
def analysis_details(type):
    data = Dataset.query.all()
    returned_data = []
    for item in data:
        analyses = Analysis.query.filter_by(type='public', dataset_id=item.id).with_entities(
            Analysis.id, Analysis.name, Analysis.dataset_id)
        method = Method.query.get(item.method_id)
        if len(list(analyses)) > 0:
            analysis_data = []
            for analysis in analyses:
                analysis_data.append({'id': analysis[0], 'name': analysis[1]})
            returned_data.append({
                'id': item.id,
                'name': item.name,
                'analyses': analysis_data,
                'method': method.name
            })
    return jsonify(returned_data)
    # for test in data:
    #
    #     print(method)
    #     returned_data.append({
    #         'id': test[2],
    #         'name': dataset.name,
    #         'status': test[3],
    #         'method': method.name
    #     })
    #     print(test)

@app.route('/analysis/list')
@jwt_required()
def user_analysis():
    """
    List of analysis of user
    ---
    tags:
        - analysis
    parameters:
        -
          name: authorization
          in: header
          type: string
          required: true
    """
    data = Dataset.query.all()
    returned_data = []
    for item in data:
        analyses = Analysis.query.filter_by(owner_user_id=current_identity.id, type='private', dataset_id=item.id).with_entities(
        Analysis.id, Analysis.name, Analysis.dataset_id)
        method = Method.query.get(item.method_id)
        if len(list(analyses)) > 0:
            analysis_data = []
            for analysis in analyses:
                analysis_data.append({'id': analysis[0], 'name': analysis[1]})
            returned_data.append({
                'id': item.id,
                'name': item.name,
                'analyses': analysis_data,
                'method': method.name
            })
    return jsonify(returned_data)

@app.route('/analysis/detail/<id>')
def analysis_detail(id):
    analysis = Analysis.query.get(id)
    metabolomics_data = MetabolomicsData.query.get(analysis.metabolomics_data_id)
    study = Dataset.query.get(analysis.dataset_id)
    method = Method.query.get(study.method_id)
    data = {
        'case_name': analysis.name,
        'status': study.status,
        'results_pathway': analysis.results_pathway,
        'results_reaction': analysis.results_reaction,
        'method': method.name,
        'fold_changes': metabolomics_data.metabolomics_data,
        'study_name': study.name,
        'analyses': []
    }
    analyses = Analysis.query.filter_by(dataset_id=study.id)
    for analysis in analyses:
        data['analyses'].append({
            'id': analysis.id,
            'name': analysis.name
        })
    # print(jsonify(data))
    return jsonify(data)


@app.route('/id')
def ids():
    # analysis = Analysis.query.get(id)
    # metabolomics_data = MetabolomicsData.query.get(analysis.metabolomics_data_id)
    # study = Dataset.query.get(analysis.dataset_id)
    # method = Method.query.get(study.method_id)
    # data = {
    #     'case_name': analysis.name,
    #     'status': study.status,
    #     'results_pathway': analysis.results_pathway,
    #     'results_reaction': analysis.results_reaction,
    #     'method': method.name,
    #     'fold_changes': metabolomics_data.metabolomics_data,
    #     'study_name': study.name,
    #     'analyses': []
    # }
    # analyses = Analysis.query.filter_by(dataset_id=study.id)
    # for analysis in analyses:
    #     data['analyses'].append({
    #         'id': analysis.id,
    #         'name': analysis.name
    #     })
    # # print(jsonify(data))
    return jsonify({"TAJ":1.000})

@app.route('/analysis/search-by-change', methods=['POST'])
def search_analysis_by_change():
    """
    Search query in db
    ---
    tags:
        - analysis
    parameters:
        -
          name: query
          in: url
          type: string
          required: true
    """
    (data, error) = PathwayChangesScheme().load(request.json, many=True)
    if error:
        return jsonify(error), 400

    return AnalysisSchema(many=True).jsonify(
        Analysis.query.filter_by_change_many(data)
        .filter_by_change_amount_many(data).filter_by_authentication()
        .with_entities(Analysis.id, Analysis.name))
############################################################# test parts
@app.route('/analysis/search-by-metabol', methods=['POST'])
def search_analysis_by_metabol():
    """
    Search query in db
    ---
    tags:
        - analysis
    parameters:
        -
          name: query
          in: url
          type: string
          required: true
    """
    filtered_ids = []

    metabolite_name = "acmana_c"
    metabolite_measurment = 10246.0

    change = "+"## represent up to
    # change = "-" ## represents at least
    # change = "=" ## represents around -10/+10

    ids = db.session.query(MetabolomicsData.id).all()
    for i in ids:  # loop over the Ids
        data = MetabolomicsData.query.filter_by(id=i[0]).first();
        data2 = data.id  # access a single id values
        data3 = MetabolomicsData.query.filter_by(id=data2).first();
        metabolites_data = data3.metabolomics_data
        if metabolite_name in list(metabolites_data) :
            if change == "+" and metabolites_data[metabolite_name] <= metabolite_measurment:
                print (i[0],metabolites_data[metabolite_name])
                filtered_ids.append(i[0])
            elif change == "-" and metabolites_data[metabolite_name] >= metabolite_measurment:
                print (i[0],metabolites_data[metabolite_name])
                filtered_ids.append(i[0])
            elif change == "=" and metabolites_data[metabolite_name] < metabolite_measurment+11 and metabolites_data[metabolite_name] > metabolite_measurment-11 :
                print (i[0],metabolites_data[metabolite_name])
                filtered_ids.append(i[0])

    return ({"1":filtered_ids})


############################################################# new parts (almost ready)

@app.route('/analysis/direct-pathway-mapping', methods=['GET', 'POST'])
def direct_pathway_mapping():
    if not request.json:
        return "", 404
    # changes = request.json['concentration_changes']
    user = User.query.get(1)
    # study_name =
    study = Dataset(name=sample_data['study_name'], method_id=2, status=True)
    db.session.add(study)
    db.session.commit()
    for key,value in sample_data["analysis"].items():  # user as key, value {metaboldata , label}
        metabolomics_data = MetabolomicsData(
            metabolomics_data = value["Metabolites"],
            owner_email = 'alperdokay@std.sehir.edu.tr',
            # is_public = True if request.json['public'] else False
            is_public =  True
        )
        db.session.add(metabolomics_data)
        db.session.commit()

        analysis = Analysis(name =key, user = user)
        analysis.name = key
        # analysis.status = True
        analysis.type = 'public'
        analysis.start_time = datetime.datetime.now()
        analysis.end_time = datetime.datetime.now()

        analysis.owner_user_id = user.id
        analysis.owner_email = user.email
        # analysis.method_id = 2
        analysis.metabolomics_data_id = metabolomics_data.id
        analysis.dataset_id = study.id
        analysis_runs = DirectPathwayMapping(value["Metabolites"])  # Forming the instance
        # fold_changes
        analysis_runs.run()  # Making the analysis
        analysis.results_pathway = [analysis_runs.result_pathways]
        analysis.results_reaction = [analysis_runs.result_reactions]

        db.session.add(analysis)
        db.session.commit()

    # analysis.owner_user_id = user.id
    # analysis.owner_email = user.email
    # analysis.method_id = 2
    # analysis.metabolomics_data_id = metabolomics_data.id
    # analysis.dataset_id = 0
    # analysis.start_time = datetime.datetime.now()
    # analysis.end_time = datetime.datetime.now()

    analysis_id = analysis.id
    return jsonify({'id': analysis.id})






# @app.route('/analysis/set')
# def analysis_set():
# return ""