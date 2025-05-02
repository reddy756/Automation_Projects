import os
import shutil
import glob

def copy_python_files(file_list, input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
        print(f"Created output folder: {output_folder}")
    
    for file_prefix in file_list:
        # Use glob to find files starting with the prefix and ending with .py
        matching_files = glob.glob(os.path.join(input_folder, f"{file_prefix}*.py"))
        
        if matching_files:
            for input_file_path in matching_files:
                file_name = os.path.basename(input_file_path)
                output_file_path = os.path.join(output_folder, file_name)
                shutil.copy(input_file_path, output_file_path)
                os.remove(input_file_path)
                print(f"Copied: {file_name} to {output_folder}")
        else:
            print(f"No files found starting with: {file_prefix}")


if __name__ == '__main__':
    # FilesInt=[1616208,1241448,1479129,1371585,1722270,1580124,1028855,1017843,4671276,5550080,2508980,4513161]
    file_list = ['1019470','1041351','1043002','1054453','1060462','1066842','1072276','1073627','1075006','1099936','1179371','1183964','1228213','1253935','1290945','1325766','1338415','1357702','1364199','1374230','1384236','1394776','1401792','1406195','1409068','1411229','1421807','1441585','1477059','1504976','1525978','1531946','1543034','1550974','1558592','1568185','1610820','1640624','1646064','1646494','1681394','1690565','1709971','1722776','1724925','1731834','1756380','1760448','1762217','1765421','1769050','1771333','1771847','1786684','1802432','1823424','1880463','1921699','1925515','1965529','1998395','2003659','2035998','2039559','2044260','2050796','2089431','2153028','2157348','2169253','2188820','2221060','2334607','2348910','2379858','2410552','2458895','2460713','2471161','2531343','2538668','2588092','2777879','2883775','2971811','3102544','3166039','3201902','3422315','3480737','3520513','3629799','3677661','3678780','3689641','3834536','3960451','4084324','4289661','4567851','4664918','4704082','5017834','5077008','5092764','5240840','5310267','5514899','5579184','5606405','5606429','5606459','5606484','5606514','5606532','5606543','5606544','5606554','5606558','5606560','5606561','5606562','5606576']

    input_folder =""
    output_folder = "C:\\Users\\Abdullah.Habeeb\\OneDrive - GlobalData PLC\\Desktop\\10&11&14_04Tier"
    copy_python_files(file_list, input_folder, output_folder)