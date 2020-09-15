import unittest
from pathlib import Path
import datetime
import os
import json
import time

from .. import grid_intersect

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
GRID_DIR = Path(Path(os.path.abspath(__file__)).parent.parent, 'grid_files')

class TestGridIntersect(unittest.TestCase):

    def setUp(self):
        
        self.path_to_shapefile = Path(TEST_DIR, 'data', 'ab_bottom.shp')
        self.path_to_shapefile_point = Path(TEST_DIR, 'data', 'point_test_wgs84.shp')
        self.path_to_shapefile_line = Path(TEST_DIR, 'data', 'line_test_wgs84.shp')

        self.wkt_example_output = "POLYGON ((-120.009608150096 53.8741380466235,-109.963161180976 53.901000204295,-109.963161180976 48.9046388774064,-114.073071304707 49.0389496657636,-114.073071304707 49.0389496657636,-120.009608150096 53.8741380466235))"
        self.wkt_example_point = "MULTIPOINT (-112.41556222762 49.859006768082,-111.959840980197 51.7530982026829,-112.173460314927 52.2515433170515,-113.383969878393 52.1233717162138,-113.811208547852 51.0125511756209,-111.119604930262 50.0014196579016,-110.977192040442 50.7989318408915,-111.375948131937 53.3338812796805,-112.401320938638 54.0744283067425,-114.936270377427 53.8608089720131,-118.767177113575 56.0682087642171,-117.585150128072 55.7833829845778)"
        self.wkt_example_line = ("MULTILINESTRING ((-113.668795658033 49.4602506765871,-113.341246011447 49.4032855206593,-112.800077030133 49.2751139198216,-112.857042186061 49.4602506765871,-113.298522144502 49.7023525892805,-113.127626676718 49.8162829011362,-112.814318319115 49.7593177452083,-112.515251250494 49.5884222774248,-112.671905429295 49.887489346046,-112.828559608097 50.243521570595,-112.130736447981 50.1438325477213,-111.888634535287 50.1153499697573,"
                                 "-111.959840980197 50.5141060612522,-112.572216406422 50.6850015290358,-112.657664140313 50.9983098866389,-112.187701603909 51.0410337535848,-111.83166937936 50.8416557078373,-111.54684359972 50.8416557078373,-111.432913287865 51.0125511756209,-111.845910668342 51.0979989095126,-112.173460314927 51.325859533224,-112.059530003071 51.3828246891519,-111.774704223432 51.2973769552601,-111.475637154811 51.340100822206,-111.418671998883 51.4825137120256,"
                                 "-112.159219025945 51.4967550010076,-112.244666759836 51.4967550010076,-112.301631915764 51.5252375789715,-112.629181562349 51.696133046755,-112.572216406422 51.7673394916648,-112.458286094566 51.8243046475927,-112.201942892891 51.9097523814844,-112.144977736963 51.9667175374123,-112.515251250494 52.052165271304,-112.857042186061 52.1376130051958,-112.743111874205 52.3085084729793,-112.643422851331 52.3654736289072,-112.387079649656 52.5078865187268,"
                                 "-112.144977736963 52.8211948763299,-112.358597071692 52.9920903441135,-112.956731208934 52.9920903441135,-113.312763433484 52.9636077661495,-113.1418679657 53.3908464356084,-112.857042186061 53.5047767474641,-112.743111874205 53.6756722152476,-113.28428085552 53.7753612381213,-113.540624057195 53.4620528805182,-114.124516905455 53.4478115915362,-114.096034327491 54.1598760406343,-113.497900190249 54.259565063508,-113.027937653844 54.3450127973998,"
                                 "-113.227315699592 54.5159082651833,-113.882414992762 54.5159082651833,-114.053310460546 54.4019779533276),(-110.89174430655 51.9382349594484,-110.849020439604 52.2088194501056,-111.219293953135 52.2800258950154,-111.091122352298 52.5506103856727,-110.720848838767 52.5506103856727,-110.649642393857 52.6075755416005,-110.663883682839 52.8781600322578,-111.076881063316 52.8211948763299,-111.162328797207 52.8211948763299,-110.948709462478 53.0775380780052,"
                                 "-110.863261728586 53.148744522915,-110.863261728586 53.2911574127346,-110.777813994694 53.4335703025543,-110.948709462478 53.6329483483017,-111.03415719637 53.6329483483017,-111.133846219243 53.6329483483017,-110.777813994694 53.8608089720131,-110.720848838767 53.889291549977,-110.82053786164 53.9747392838688,-111.432913287865 53.889291549977,-111.817428090378 53.533259325428,-111.888634535287 53.4050877245903,-111.845910668342 53.1060206559692,"
                                 "-111.731980356486 52.806953587348,-111.575326177684 52.7499884314201,-111.518361021756 52.2657846060335,-111.461395865829 51.9952001153762,-111.333224264991 51.8243046475927,-111.076881063316 51.8812698035205,-110.991433329424 51.9382349594484,-110.96295075146 51.9667175374123,-110.905985595532 52.0094414043582,-110.877503017568 51.9809588263942))")
        
        self.path_to_shp_complex = Path(TEST_DIR, 'data', 'AB_Agr_Mask_WGS84.shp')

        self.path_to_ab_bottom_dense = Path(TEST_DIR, 'data', 'ab_bottom_dense.shp')
        self.mgrs_gzd_list_1 = ['10U', '11U', '12U']

        self.single_wrs_wkt = "POLYGON ((-115.241934638077 52.4386972294536,-115.284798550801 52.3541285084727,-115.378771459219 52.1687238599776,-115.38 52.1663,-115.973112502371 52.253219332195,-116.240140513323 52.2923516996573,-116.661293079454 52.3540706815603,-118.015034953517 52.5524585745613,-118.016 52.5526,-117.996725395015 52.5959634872517,-117.983329296427 52.6261016691124,-117.434333751106 53.861217063132,-117.387648454031 53.966248387307,-117.381181099434 53.9807984675216,-117.355 54.0397,-117.353576866241 54.0394910785268,-115.973672881992 53.8369159014122,-115.706668847534 53.7977186890061,-114.633 53.6401,-114.651623402903 53.6033567989315,-115.241934638077 52.4386972294536))"
        self.single_wrs_pathrow = "044023"

        self.single_mgrs_wkt = "POLYGON ((-115.532121800527 52.341175347143,-117.0 52.3502933488509,-117.0 53.2492669055972,-115.501552128341 53.2398489094304,-115.532121800527 52.341175347143))"
        self.single_mgrs_tileid = "11UNU"

        self.test_footprint_1 = 'POLYGON((-110.05657077596709 49.01153105441047,-109.99065280721709 53.26747451320431,-110.25432468221709 54.1903679577336,-111.08928561971709 54.34435309167866,-113.59416843221709 54.061607249134155,-114.75871921346709 54.65060027562556,-115.85735202596709 55.16847874827975,-117.28557468221709 55.66732588602491,-119.35100436971709 55.543204417173975,-119.98821140096709 54.59971836352182,-118.31828952596709 53.867715218704966,-116.82414890096709 53.228032103413625,-115.96721530721709 52.23011549549104,-114.78069186971709 51.27802785817801,-114.27063874778048 49.871533466398866,-114.16077546653048 49.27308564086286,-113.63343171653048 48.97110715942032,-110.05657077596709 49.01153105441047))'
        self.test_footprint_2 = 'POLYGON((-117.219827586215 58.718199728247,-116.079310344835 58.8087169696263,-114.938793103456 58.6638893834194,-115.246551724145 58.1750962799711,-116.043103448283 57.7949238661779,-116.604310344835 57.4871652454883,-116.966379310353 56.99837214204,-116.71293103449 56.600096279971,-116.387068965525 56.6544066247986,-115.66293103449 56.3828549006606,-116.55 56.0750962799709,-115.409482758628 56.1294066247985,-115.029310344835 55.5863031765226,-114.268965517249 55.5681997282468,-113.834482758628 55.5138893834192,-113.418103448283 55.2423376592812,-113.182758620697 55.2423376592812,-112.838793103456 55.2785445558329,-112.494827586214 55.5681997282468,-112.168965517249 55.1880273144536,-111.915517241387 55.1699238661778,-111.553448275869 54.7716480041088,-111.028448275869 54.7897514523846,-110.304310344835 54.7897514523846,-109.869827586214 54.5725100730743,-109.88793103449 49.9380273144533,-109.942241379318 48.4897514523842,-112.150862068973 48.4535445558325,-113.707758620697 48.5621652454877,-114.196551724145 48.9785445558325,-114.685344827594 49.3949238661774,-114.92068965518 49.8113031765222,-114.631034482766 50.245785935143,-114.757758620697 50.770785935143,-115.355172413801 50.9699238661775,-115.101724137939 51.2414755903154,-115.22844827587 51.6578549006603,-115.318965517249 52.092337659281,-115.66293103449 52.0742342110051,-115.789655172421 52.5992342110052,-115.536206896559 52.8526824868673,-115.681034482766 53.3052686937638,-115.916379310352 53.3052686937638,-116.930172413801 53.3414755903156,-116.893965517249 53.812165245488,-116.169827586215 54.4095790385915,-114.812068965525 54.6992342110053,-114.323275862076 55.006992831695,-114.631034482766 54.9345790385915,-115.608620689663 55.0613031765226,-116.169827586215 55.006992831695,-116.676724137939 54.8078549006605,-117.002586206904 54.4095790385915,-117.76293103449 54.8078549006605,-118.414655172422 54.9888893834191,-119.175 54.7354411075571,-119.989655172422 54.8621652454881,-119.989655172422 56.6181997282468,-119.319827586215 56.6906135213503,-118.450862068973 56.726820417902,-117.889655172422 56.7630273144537,-117.925862068973 56.9259583489365,-117.744827586215 57.3061307627296,-117.962068965525 57.5776824868676,-118.052586206904 57.921648004109,-117.437068965525 58.04837214204,-117.292241379318 58.2475100730745,-117.219827586215 58.718199728247))'
        self.test_footprint_3_lethbridge = 'POLYGON((-113.09814998548927 50.04236546243994,-113.18878719252052 49.904583052743654,-113.15582820814552 49.78236964180449,-112.57080623548927 49.748662413160886,-112.44721004408302 49.84262935403644,-112.51312801283302 49.998247389145405,-112.73834773939552 50.07586810521376,-113.09814998548927 50.04236546243994))'
        self.test_footprint_2_result_list = ['12U', '11U', '11V']
        self.test_footprint_2_result_list2 = ['12UWV', '12UWU', '12UWF', '12UWE', '12UWD', '12UWC', '12UWB', '12UWA', '12UVV', '12UVU', '12UVG', '12UVF', '12UVE', '12UVD', '12UVC', '12UVB', '12UVA', '12UUV', '12UUU', '12UUG', '12UUF', '12UUE', '12UUD', '12UUC', '12UUB', '12UUA', '12UTV', '12UTU', '12UTE', '12UTD', '12UTC', '12UTB', '12UTA', '11UQV', '11UQU', '11UQT', '11UQS', '11UQR', '11UQQ', '11UPV', '11UPU', '11UPT', '11UPS', '11UPR', '11UPQ', '11VPF', '11VPE', '11UPC', '11VPC', '11UPB', '11UPA', '11UNV', '11UNU', '11UNT', '11VNF', '11VNE', '11VND', '11UNC', '11VNC', '11UNB', '11UNA', '11VMF', '11VME', '11VMD', '11UMC', '11VMC', '11UMB', '11UMA', '11ULC', '11VLC', '11ULB', '11ULA']
        self.test_footprint_2_result_list_single = ['12UWV', '12UWU', '12UWF', '12UWE', '12UWD', '12UWC', '12UWB', '12UWA', '12UVV', '12UVU', '12UVG', '12UVF', '12UVE', '12UVD', '12UVC', '12UVB', '12UVA', '12UUV', '12UUU', '12UUG', '12UUF', '12UUE', '12UUD', '12UUC', '12UUB', '12UUA', '12UTV', '12UTU', '12UTE', '12UTD', '12UTC', '12UTB', '12UTA']

        self.tile_list_small = ['11UQR']  # by lethbridge

        self.SENTINEL2_DATASET_NAME = 'SENTINEL_2A'
        self.SENTINEL2_PLATFORM_NAME = 'Sentinel-2'
        self.LANDSAT8_DATASET_NAME = 'LANDSAT_8_C1'
        self.LANDSAT8_PLATFORM_NAME = 'Landsat-8'


    def test_get_wkt_from_shapefile(self):
        wkt_result = grid_intersect.get_wkt_from_shapefile(str(self.path_to_shapefile))
        print(wkt_result)
        self.assertEqual(wkt_result, self.wkt_example_output)

    def test_get_wkt_from_shapefile_point(self):
        wkt_result = grid_intersect.get_wkt_from_shapefile(str(self.path_to_shapefile_point))
        print(wkt_result)
        self.assertEqual(wkt_result, self.wkt_example_point)

    def test_get_wkt_from_shapefile_line(self):
        wkt_result = grid_intersect.get_wkt_from_shapefile(str(self.path_to_shapefile_line))
        print(wkt_result)
        self.assertEqual(wkt_result, self.wkt_example_line)

    def test_get_wkt_from_shapefile_complex(self):
        pass
        # wkt_result = grid_intersect.get_wkt_from_shapefile(str(Path(TEST_DIR, 'data', 'ab_bottom_dense.shp')))
        # print(wkt_result)
        # with open(Path(TEST_DIR, 'wkt.txt'), 'w') as f:
        #     f.write('WKT, id')
        #     f.write(wkt_result + ', 0')

        # self.assertTrue(True)

    def test_find_mgrs_gzd_intersections(self):
        #load the wkt footprint string
        with open(Path(TEST_DIR, 'data', 'ab_bottom_dense_wkt.txt'), 'r') as f:
            f.readline()
            wkt_line = f.readline()
            wkt_footprint = wkt_line[1:-4]
        
        gzd_list = grid_intersect.find_mgrs_gzd_intersections(wkt_footprint)
        self.assertEqual(gzd_list, self.mgrs_gzd_list_1)

    def test_unzip_mgrs_100km_shp(self):
        gzd = '12U'
        zip_name = f'MGRS_100kmSQ_ID_{gzd}.zip'
        file_name_stem = f'MGRS_100kmSQ_ID{gzd}'
        full_zip_path = Path(GRID_DIR, 'MGRS_100kmSQ_ID', zip_name)
        
        # 1. unzip
        file_name_stem = grid_intersect.unzip_mgrs_100km_shp(full_zip_path)

        file_path = Path(GRID_DIR, file_name_stem + '.shp')
        self.assertTrue(file_path.exists())
        grid_intersect.cleanup()
        self.assertFalse(file_path.exists())

    def test_find_mgrs_intersection_100km(self):
        gzd_list = ['12U', '11U', '10U']

        intersects_10u = ['10UFE']
        intersects_11u = ['11ULU', '11ULV','11UMS','11UMT','11UMU','11UMV','11UNR','11UNS','11UNT','11UNU','11UNV','11UPQ','11UPR','11UPS','11UPT','11UPU','11UPV','11UQQ','11UQR','11UQS','11UQT','11UQU','11UQV']
        intersects_12u = ['12UTA','12UTB','12UTC','12UTD','12UTE','12UTV','12UUA','12UUB','12UUC','12UUD','12UUE','12UUV','12UVA','12UVB','12UVC','12UVD','12UVE','12UVV','12UWA','12UWB','12UWC','12UWD','12UWE','12UWV']
        
        intersect_12u_set = set(intersects_12u)
        intersect_11u_set = set(intersects_11u)
        intersect_10u_set = set(intersects_10u)

        with open(Path(TEST_DIR, 'data', 'ab_bottom_dense_wkt.txt'), 'r') as f:
            f.readline()
            wkt_line = f.readline()
            wkt_footprint = wkt_line[1:-4]

        intersection_list_12u = grid_intersect.find_mgrs_intersection_100km(wkt_footprint, '12U')
        intersect_12u_set_test = set(intersection_list_12u)
        self.assertEqual(intersect_12u_set_test, intersect_12u_set)

        intersection_list_11u = grid_intersect.find_mgrs_intersection_100km(wkt_footprint, '11U')
        intersect_11u_set_test = set(intersection_list_11u)
        self.assertEqual(intersect_11u_set_test, intersect_11u_set)

        intersection_list_10u = grid_intersect.find_mgrs_intersection_100km(wkt_footprint, '10U')
        intersect_10u_set_test = set(intersection_list_10u)
        self.assertEqual(intersect_10u_set_test, intersect_10u_set)

    def test_find_mgrs_intersections(self):

        intersects_list = ['10UFE',
                           '11ULU', '11ULV','11UMS','11UMT','11UMU','11UMV','11UNR','11UNS','11UNT','11UNU','11UNV','11UPQ','11UPR','11UPS','11UPT','11UPU','11UPV','11UQQ','11UQR','11UQS','11UQT','11UQU','11UQV',
                           '12UTA','12UTB','12UTC','12UTD','12UTE','12UTV','12UUA','12UUB','12UUC','12UUD','12UUE','12UUV','12UVA','12UVB','12UVC','12UVD','12UVE','12UVV','12UWA','12UWB','12UWC','12UWD','12UWE','12UWV']
        
        intersect_set = set(intersects_list)

        with open(Path(TEST_DIR, 'data', 'ab_bottom_dense_wkt.txt'), 'r') as f:
            f.readline()
            wkt_line = f.readline()
            wkt_footprint = wkt_line[1:-4]

        intersection_list_all = grid_intersect.find_mgrs_intersection(wkt_footprint)
        print(intersection_list_all)
        intersect_all_set = set(intersection_list_all)
        self.assertEqual(intersect_all_set, intersect_set)

    def test_find_wrs_intersection(self):
        intersects_list = ['043022','047022','041025','040026','041024','041023','041022','039025','039024','039023','041026','044022','046023','046022','039026','042022','044025','044024','044023','042026','042025','042024','042023','040025','040024','040023','040022','045024','045023','045022','043025','043024','038026','043023','047023']
        intersect_set = set(intersects_list)

        with open(Path(TEST_DIR, 'data', 'ab_bottom_dense_wkt.txt'), 'r') as f:
            f.readline()
            wkt_line = f.readline()
            wkt_footprint = wkt_line[1:-4]

        intersection_list_all = grid_intersect.find_wrs_intersection(wkt_footprint)
        print(intersection_list_all)
        intersect_all_set = set(intersection_list_all)
        self.assertEqual(intersect_all_set, intersect_set)

    def test_get_wkt_for_wrs_tile__valid_pathrow(self):
        """
        For a given path row, return a wkt footprint
        """
        wkt_result = grid_intersect.get_wkt_for_wrs_tile(self.single_wrs_pathrow)

        self.assertEqual(wkt_result, self.single_wrs_wkt)

    def test_get_wkt_for_wrs_tile__invalid_pathrow(self):
        """
        For a given path row, return a wkt footprint
        """
        wkt_result = grid_intersect.get_wkt_for_wrs_tile("AAB003")

        self.assertEqual(wkt_result, None)

    def test_get_wkt_for_mgrs_tile__valid_100km_id(self):

        wkt_result = grid_intersect.get_wkt_for_mgrs_tile(self.single_mgrs_tileid)
        print(wkt_result)
        print('help')
        self.assertEqual(wkt_result, self.single_mgrs_wkt)

    def test_convert_mgrs_to_wrs(self):
        test_mgrs = '11UMT'
        result_wrs = ['046024', '044024', '045024', '046023', '045023']
        result_set = set(result_wrs)

        wrs_overlapping = grid_intersect.convert_mgrs_to_wrs(test_mgrs)
        wrs_set = set(wrs_overlapping)

        self.assertEqual(result_set, wrs_set)

    def test_convert_wrs_to_mgrs(self):
        test_wrs = '044024'
        result_mgrs = ['11ULS', '11UMT', '11UNT', '11UNU', '11ULT',
                        '11UMU', '11UMS', '11UNS', '11UPT']
        result_set = set(result_mgrs)

        mgrs_overlapping = grid_intersect.convert_wrs_to_mgrs(test_wrs)
        mgrs_set = set(mgrs_overlapping)
        self.assertEqual(result_set, mgrs_set)

    def test_convert_wrs_to_mgrs_list(self):
        test_wrs_list = ['044024', '043024','042024']
        test_result_mgrs = ['11UQU','11ULT','11UMT','11UPS','11UMU','11UMS','11UNS','11UPT','11UQT','11UPU','11UNT','11UNU','12UTB','12UUB','12UUD','12UVC','12UUC','12UTD','11UQS','12UTC','11ULS']
        test_result_set = set(test_result_mgrs)

        mgrs_overlapping = grid_intersect.convert_wrs_to_mgrs_list(test_wrs_list)

        mgrs_overlapping_set = set(mgrs_overlapping)

        self.assertEqual(test_result_set, mgrs_overlapping_set)

    def test_convert_mgrs_to_wrs_list(self):
        test_mgrs_list = ['11UQU','11UPT','12UWF','11UQT','12UVF','12UUE','12UVE','12UTD','12UWE','12UTC','12UUD','11UNA','12UUC','11UPV','11UPA','11UPU','11UNV','12UUF']
        test_result_wrs = ['041022','042023','042024','043024','041024','044022','043023','046021','046022','045022','043022','045021','044021','045023','044024','041021','042021','044023','042022','043021','040022','040023','039022','039023','041023']
        test_result_set = set(test_result_wrs)

        wrs_overlapping = grid_intersect.convert_mgrs_to_wrs_list(test_mgrs_list)

        wrs_overlapping_set = set(wrs_overlapping)

        self.assertEqual(test_result_set, wrs_overlapping_set)

    def test_create_shapefile_from_tile_list(self):
        test_mgrs_list = ['11UQU','11UPT','12UWF','11UQT','12UVF','12UUE','12UVE','12UTD','12UWE','12UTC','12UUD','11UNA','12UUC','11UPV','11UPA','11UPU','11UNV','12UUF']
        test_wrs_list = ['041022','042023','042024','043024','041024','044022','043023','046021','046022','045022','043022','045021','044021','045023','044024','041021','042021','044023','042022','043021','040022','040023','039022','039023','041023']
        test_mixed_list = ['11UQU','11UPT','12UWF','11UQT','12UVF','12UUE','12UVE','12UTD','046021','046022','045022','043022','045021','044021','045023','044024','041021','042021']
        grid_intersect.create_shapefile_from_tile_list(test_mgrs_list)

        self.assertTrue(Path('tile_coverage.shp').exists())

        grid_intersect.create_shapefile_from_tile_list(test_wrs_list, 'wrs_tile.shp')
        self.assertTrue(Path('wrs_tile.shp').exists())

        grid_intersect.create_shapefile_from_tile_list(test_mixed_list, Path(TEST_DIR, 'mixed_list.shp'))
        self.assertTrue(Path(TEST_DIR, 'mixed_list.shp').exists())

        for root, dirs, files in os.walk(".", topdown=False):
            for f in files:
                if Path(f).stem in ['wrs_tile', 'tile_coverage', 'mixed_list']:
                    print('found a file to cleanup')
                    print(Path(root, f))
                    os.remove(Path(root, f))


if __name__ == '__main__':
    unittest.main()