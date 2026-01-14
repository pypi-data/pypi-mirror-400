import os
from readdat import READDATHOME
from readdat.database.codatabase import CodataBase


SQLITEFILETEST = "codatabase_test.sqlite"  # WILL BE ERASED !! 

def test_readdat_home():
    assert os.path.isdir(READDATHOME)
    assert os.path.isfile(os.path.join(READDATHOME, '__init__.py'))
    

def cleanup():
    if os.path.isfile(SQLITEFILETEST):
        os.remove(SQLITEFILETEST)
        

def test_cleanup_codatabase():
    cleanup()
    assert not os.path.isfile(SQLITEFILETEST)
    
        
def test_create_codatabase():        
    with CodataBase(SQLITEFILETEST, create=True) as db:
        db.create_tables(sure=True)

    assert os.path.isfile(SQLITEFILETEST)

    expected_table_names = ['CONFIG', 'PATHS', 'FILES', 'FILEATTRS', 'TRACES', 'TRACEATTRS', 'POINTS', 'FEATURES']
    with CodataBase(SQLITEFILETEST) as db:
        actual_table_names = db.table_list()

    for table_name in expected_table_names:
        assert table_name in actual_table_names

    for table_name in actual_table_names:
        assert table_name in expected_table_names
        
    cleanup()

        
def test_set_root_dir():
    expecte_root_dir = os.path.join(READDATHOME, 'filesamples')
    with CodataBase(SQLITEFILETEST, create=True) as db:        
        db.create_tables(sure=True)
        db.set_root_dir(expecte_root_dir)

    with CodataBase(SQLITEFILETEST) as db:
        root_dir = db.selectscalar('select VALUE from CONFIG where FIELD="ROOTDIR"')
    assert root_dir == expecte_root_dir
    
    cleanup()

        
def test_find_files():        
    expected_root_dir = os.path.join(READDATHOME, 'filesamples')
    with CodataBase(SQLITEFILETEST, create=True) as db:        
        db.create_tables(sure=True)
        db.set_root_dir(expected_root_dir)
        db.find_files(file_search_path="*.sg2", exclude_files_like="*_cdz.sg2")
        
    expected_file_list = [
        os.path.join(expected_root_dir, 'seg2file.sg2'),
        os.path.join(expected_root_dir, 'seg2file_coda.sg2'),
        os.path.join(expected_root_dir, 'seg2file_coda1.sg2'),
        os.path.join(expected_root_dir, 'seg2file_musc.sg2'),        
        os.path.join(expected_root_dir, 'seg2file_musc1.sg2'),                
        os.path.join(expected_root_dir, 'seg2file_ondulys.sg2'),
        # os.path.join(expected_root_dir, 'seg2file_cdz.sg2'),
        os.path.join(expected_root_dir, 'seg2file_tomag.sg2'),
        os.path.join(expected_root_dir, 'seg2file_must.sg2'),
        os.path.join(expected_root_dir, 'dataset', 'seg2file.sg2'),
        os.path.join(expected_root_dir, 'dataset', 'part1', 'seg2file.sg2'),                       
        os.path.join(expected_root_dir, 'dataset', 'part1', 'part11', 'seg2file.sg2'),                   
        os.path.join(expected_root_dir, 'dataset', 'part1', 'part12', 'seg2file.sg2'),           
        os.path.join(expected_root_dir, 'dataset', 'part2', 'seg2file.sg2'),      
        os.path.join(expected_root_dir, 'dataset', 'part3', 'seg2file.sg2'),                            
        ]
    for filename in expected_file_list:
        assert os.path.isfile(filename)
        
    actual_file_list = []
    with CodataBase(SQLITEFILETEST) as db:
        root_dir = db.selectscalar('select VALUE from CONFIG where FIELD="ROOTDIR"')
        for pathname, filename in db.select('select PATHNAME, FILENAME from FILES join PATHS using (PATHID)'):
            fullfilename = os.path.join(root_dir, pathname, filename)
            assert os.path.isfile(fullfilename)
            actual_file_list.append(fullfilename)
    assert len(actual_file_list)
    
    for actual_file_name in actual_file_list:
        assert actual_file_name in expected_file_list
        
    for expected_file_name in expected_file_list:
        assert expected_file_name in actual_file_list        
        
    cleanup()

    
def test_extract_headers():     
    expected_root_dir = os.path.join(READDATHOME, 'filesamples')
    with CodataBase(SQLITEFILETEST, create=True) as db:        
        db.create_tables(sure=True)
        db.set_root_dir(expected_root_dir)
        db.find_files(file_search_path="*.sg2", exclude_files_like="*_cdz.sg2")
        db.extract_header(acquisition_system=None, timezone="Europe/Paris")

    with CodataBase(SQLITEFILETEST) as db:
        assert db.selectscalar('select count(*) from traces') == 1078
    
    cleanup()

        
