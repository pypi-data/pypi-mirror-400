#!python
from typing import Optional, Any
import os, sys, warnings, fnmatch, struct

import numpy as np
from matplotlib.axes import Axes
import matplotlib.pyplot as plt

from tqdm.auto import tqdm

from obspy.core import UTCDateTime, AttribDict

from dbpack.database import Database
from sqlite3 import IntegrityError, OperationalError

from readdat import read
from tempoo.timetick import timetick

from readdat.seg2.read_seg2 import ACQUISITION_SYSTEMS

def explore_stats_recurs(stats, path=""):
    for key, value in stats.items():
        if isinstance(value, (dict, AttribDict)):
            for ppath, kkey, vvalue in explore_stats_recurs(value, path=".".join([path, key])):
                yield ppath, kkey, vvalue

        elif key == "NOTE" and hasattr(value, "__iter__"):
            for n, vvalue in enumerate(value):
                if "=" in vvalue:
                    kkey = vvalue.split('=')[0]
                    vvalue = "=".join(vvalue.split('=')[1:])
                else:
                    kkey = vvalue.split()[0]
                    vvalue = " ".join(vvalue.split()[1:])
                yield f"{path}.{key}[{n}]", kkey, vvalue
        else:
            yield path, key, value


class CodataBase(Database):

    def create_tables(self, sure=False):
        if not sure:
            assert input('format all tables, are you sure?') == "y", "abort"

        self.cursor.execute('drop view if exists TIMEVIEW')
        self.cursor.execute('drop table if exists FEATURES')

        self.cursor.execute('drop table if exists TRACEATTRS')
        self.cursor.execute('drop table if exists TRACES')

        self.cursor.execute('drop table if exists FILEATTRS')
        self.cursor.execute('drop table if exists FILES')
        self.cursor.execute('drop table if exists PATHS')

        self.cursor.execute('drop table if exists POINTS')

        self.cursor.execute('drop table if exists CONFIG')

        self.cursor.execute('''
            create table CONFIG (
                FIELD    varchar primary key,
                VALUE    glob
                ) ''')

        self.cursor.execute('''
            create table PATHS (
                PATHID   integer primary key autoincrement,
                PATHNAME varchar unique not null
                ) ''')

        self.cursor.execute('''
            create table FILES (
                FILEID   integer primary key autoincrement,
                PATHID   integer references PATHS(PATHID),
                FILENAME varchar not null,
                FORMAT   varchar,
                NTRACES  integer,
                constraint U unique (PATHID, FILENAME)
                ) ''')

        self.cursor.execute('''
            create table FILEATTRS (
                 FATTRID    integer primary key autoincrement,
                 FILEID     integer references FILES(FILEID),
                 FIELD      varchar not null,
                 VALUE      glob,
                 PATH       varchar,                 
                 -- prevent several time the same field for one file
                 constraint U unique (FILEID, FIELD)                 
                 ) ''')

        self.cursor.execute('''
            create table TRACES (
                 TRACEID    integer primary key autoincrement,
                 FILEID     integer references FILES(FILEID),
                 TIMESTAMP         real not null, 
                 STARTTIME         varchar not null,
                 TRACEINDEX        integer not null, -- from 0
                 CHANNEL           glob,  -- name or number ?    
                 NSAMPLES          integer not null,
                 SAMPLE_INTERVAL   real not null, -- seconds
                 RECPOINT          integer REFERENCES POINTS (POINTID),
                 SRCPOINT          integer REFERENCES POINTS (POINTID),
                 constraint U unique (FILEID, TRACEINDEX)
                 )''')

        self.cursor.execute('''
            create table FEATURES (
                 TRACEID    integer primary key references TRACES (TRACEID),
                 NAME       varchar not null, 
                 VALUE      blob)''')

        self.cursor.execute('''
            create table TRACEATTRS (
                 TRATTRID    integer primary key autoincrement,
                 TRACEID     integer references TRACES(TRACEID),
                 FIELD       varchar not null,
                 VALUE       glob,
                 PATH       varchar,
                 -- prevent several time the same field for one file
                 constraint U unique (TRACEID, FIELD)                 
                 ) ''')

        self.cursor.execute('''
            create table POINTS (
                 POINTID     integer primary key autoincrement,
                 POINTNAME   varchar unique,                
                 X  real, -- meters
                 Y  real, -- meters
                 Z  real, -- meters
                 constraint Q unique (POINTNAME, X, Y, Z)
                 ) ''')

        self.cursor.execute('''
            create view TIMEVIEW (STARTTIME, TIMESTAMP, YEAR, MONTH, DAY, HOUR, MINUTE, SECOND, MICROSECOND, UTC)
            as             
            select distinct
                starttime, timestamp,
                CAST(SUBSTR(starttime, 1, 4) as INT) as YEAR, 
                CAST(SUBSTR(starttime, 6, 2) as INT) as MONTH, 
                CAST(SUBSTR(starttime, 9, 2) as INT) as DAY, 
                CAST(SUBSTR(starttime, 12, 2) as INT) as HOUR, 
                CAST(SUBSTR(starttime, 15, 2) as INT) as MINUTE, 
                CAST(SUBSTR(starttime, 18, 2) as INT) as SECOND, 
                CAST(SUBSTR(starttime, 21, 6) as INT) as MICROSECOND, 
                CASE WHEN (starttime LIKE "%UTC+%" ) 
                    THEN CAST(SUBSTR(starttime, 33, 2) as INT)
                    ELSE NULL 
                    END as UTC
                from TRACES
            ''')

    def config(self, field:str, value: Any, allow_overwrite: bool =True):
        """
        Insert new item in the configuration table
        """
        field = field.upper().strip()

        replace_statement = ""
        if allow_overwrite:
            replace_statement = " or replace "

        self.begin_transaction()
        try:
            self.cursor.execute(
                f'''insert 
                 {replace_statement}
                 into CONFIG (FIELD, VALUE) values (?, ?)
                ''', (field, value))

            if self.verbose:
                print(f"{field:>20s}->{value}")

            self.commit()

        except:
            self.rollback(raise_an_error=True)

    def get_config(self, field: str):

        answer = self.cursor.execute(
            f'select VALUE from CONFIG '
            f'where FIELD="{field}" limit 1'
            ).fetchall()

        if len(answer) == 0:
            # answer is []
            raise KeyError(f"{field} not found in the CONFIG table")
        else:
            # answer is [(value,)]
            value, = answer[0]
        return value

    def set_root_dir(self, root_dir:str):
        if os.path.isdir(root_dir):
            root_dir = os.path.realpath(root_dir)
        else:
            raise ValueError(f"{root_dir} is not a directory")

        self.config("ROOTDIR", root_dir, allow_overwrite=True)

    def find_files(self, file_search_path: str = "*", exclude_files_like=None):
        root_dir = self.selectscalar("select VALUE from CONFIG where FIELD='ROOTDIR'")
        assert os.path.isdir(root_dir), root_dir

        sel = self.cursor.execute('select pathid, pathname from PATHS')
        known_pathids = {pathname: pathid for pathid, pathname in sel}

        self.begin_transaction()
        try:
            for dirname, dirs, files in os.walk(root_dir, followlinks=True):
                if self.verbose:
                    print(f'entering {dirname} : {len(files)} files')

                for filename in fnmatch.filter(files, file_search_path):
                    if exclude_files_like is not None:
                        if fnmatch.fnmatch(filename, exclude_files_like):
                            if self.verbose:
                                print(f'ignore {filename}')
                            continue

                    # remove everything before rootdir in the pathname
                    pathname = dirname.split(root_dir)[-1].strip(os.path.sep).strip()
                    # pathname = os.path.join(root_dir, pathname) ???

                    try:
                        # try to load from known values
                        pathid = known_pathids[pathname]

                    except KeyError:
                        # not found, add a new entry
                        self.execute('insert into PATHS(PATHNAME) values (?)', (pathname,))
                        pathid = known_pathids[pathname] = self.cursor.lastrowid

                    fileformat = filename.split('.')[-1].upper()

                    self.execute(
                        'insert or ignore into FILES(PATHID, FILENAME, FORMAT) values (?, ?, ?)',
                        (pathid, filename, fileformat))
                        
                    if self.verbose:
                        if self.cursor.lastrowid != 0:
                            print(f'insert {pathid=}, {filename=}, {fileformat=}')                        
                        else:
                            print(f'file already known {pathid=}, {filename=}, {fileformat=}')                                                    
            self.commit()
        except:
            self.rollback()

    def extract_header(self, acquisition_system="CODA", timezone="Europe/Paris"):
        rootdir = self.selectscalar("select VALUE from CONFIG where FIELD='ROOTDIR'")
        assert os.path.isdir(rootdir)

        file_list = self.select('''
            select fileid, pathname, filename, format 
                from FILES join PATHS using (PATHID)
               	left join (select FILEID, COUNT(*) as N from TRACES group by FILEID) using (FILEID)
                where N is NULL
            ''')
        if file_list is None:
            if self.verbose:
                print('no header data to extract')
            return
        file_list = list(file_list)

        selection = self.cursor.execute('select pointid, x, y, z from POINTS')
        known_points = {(x, y, z): pointid for pointid, x, y, z in selection}

        self.begin_transaction()
        try:
            iterator = tqdm(enumerate(file_list), desc='extracting headers', total=len(file_list))
            # iterator = enumerate(file_list)

            for nfile, (fileid, pathname, filename, fileformat) in iterator:
                fullfilename = os.path.join(rootdir, pathname, filename)

                if not os.path.isfile(fullfilename):
                    warnings.warn(f'file {fullfilename} was missing')
                    # raise IOError(fullfilename)
                    continue

                if self.verbose:
                    print(fullfilename, fileformat)

                if fileformat == "SG2":
                    fileformat = "SEG2"

                try:
                    stream = read(
                        fullfilename,
                        format=fileformat,
                        acquisition_system=acquisition_system,
                        timezone=timezone,
                        headonly=False)
                except (ValueError, NotImplementedError, struct.error, OSError, IOError) as err:
                    warnings.warn(f'could not read file {fullfilename}')
                    continue

                self.cursor.execute('''
                    update FILES set NTRACES=? where FILEID=?
                    ''', (len(stream), fileid))

                if hasattr(stream, "stats"):
                    for path, field, value in explore_stats_recurs(stream.stats['seg2'], path="seg2"):
                        # print('**', path, field, value)
                        fileattrs = (fileid, path, field, value)

                        self.cursor.execute('''
                             insert or replace into 
                                FILEATTRS (FILEID, PATH, FIELD, VALUE) 
                                VALUES (?, ?, ?, ?)
                            ''', fileattrs)

                for traceindex, trace in enumerate(stream):
                    if timezone is None:
                        # the date is "Naive" => means read as if it was UTC+0
                        starttime = str(trace.stats.starttime) + "_UTC+0?"
                        timestamp = trace.stats.starttime.timestamp
                    else:
                        starttime = str(trace.stats.starttime) + "_UTC+0"
                        timestamp = trace.stats.starttime.timestamp

                    channel = trace.stats.channel

                    recpoint_xyz = (trace.stats.receiver_x, trace.stats.receiver_y, trace.stats.receiver_z)
                    srcpoint_xyz = (trace.stats.source_x, trace.stats.source_y, trace.stats.source_z)

                    try:
                        recpointid = known_points[recpoint_xyz]

                    except KeyError:
                        self.execute('insert into POINTS (X, Y, Z) values (?, ?, ?)', recpoint_xyz)
                        recpointid = known_points[recpoint_xyz] = self.cursor.lastrowid

                    try:
                        srcpointid = known_points[srcpoint_xyz]

                    except KeyError:
                        self.execute('insert into POINTS (X, Y, Z) values (?, ?, ?)', srcpoint_xyz)
                        srcpointid = known_points[srcpoint_xyz] = self.cursor.lastrowid

                    trace_tup = (fileid, traceindex,
                           starttime, timestamp,
                           channel,
                           trace.stats.npts, trace.stats.delta,
                           recpointid, srcpointid,
                           )

                    # if self.verbose:
                    #     print(trace_tup)

                    self.cursor.execute('''
                        insert into TRACES (
                            FILEID, TRACEINDEX, 
                            STARTTIME, TIMESTAMP,
                            CHANNEL,
                            NSAMPLES, SAMPLE_INTERVAL,
                            RECPOINT, SRCPOINT)
                        values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', trace_tup)
                    traceid = self.cursor.lastrowid

                    for path, field, value in explore_stats_recurs(trace.stats['seg2'], path="seg2"):
                        traceattrib_tup = (traceid, path, field, str(value))

                        self.cursor.execute('''
                            insert into TRACEATTRS (
                                TRACEID, PATH, FIELD, VALUE )
                            values (?, ?, ?, ?)
                            ''', traceattrib_tup)

                if nfile and not nfile % 30:
                    self.savepoint()

            self.commit()
        except:
            self.rollback()

    def add_one_point(self, pointname, x, y, z):
        self.begin_transaction()
        try:
            if self.verbose:
                print('add point ', pointname, x, y, z)
            self.execute('''
                insert or replace into POINTS (POINTNAME, X, Y, Z)
                values (?,?,?,?)''', (pointname, x, y, z))
            self.commit()

        except:
            self.rollback(True)

    def add_points_from_csv(self, csv_file:str, delimiter=",", comments="#", dytpe="str", **kwargs):

        # assume POINTNAME, X, Y, Z, ...
        data = np.genfromtxt(
            csv_file, delimiter=delimiter,
            comments=comments, dtype=dytpe,
            **kwargs)[:, :4].astype(object)

        data[:, 1:4] = data[:, 1:4].astype(float)  # expect x, y, z in meters
        self.begin_transaction()
        try:
            self.executemany('''
                insert or ignore into POINTS (POINTNAME, X, Y, Z)
                values (?,?,?,?)''', data)
            self.commit()

        except:
            self.rollback(True)

    @staticmethod
    def sql_time_range(starttime: Optional[UTCDateTime] = None,
                       endtime: Optional[UTCDateTime] = None) -> str:
        """Shortcut to convert a pair of UTCDateTimes (eventually None)
        into a SQL statement
        """
        sql = []
        if starttime is not None:
            sql.append(f'timestamp >= {starttime.timestamp}')

        if endtime is not None:
            sql.append(f'timestamp <= {endtime.timestamp}')

        return " and ".join(sql)

    def show_filetimes(self, ax: Optional[Axes] = None, duration=1*60., sql_completion=""):
        """
        This method displays the number of traces found along time
        """
        if ax is None:
            ax = plt.gca()

        cmd = f'''
            select AVG(timestamp), count(*) as nfiles 
                from  TRACES 
                {sql_completion}
                group by ROUND(timestamp / {duration}) * {duration}
            '''
        print(cmd)
        timestamp, nfiles = self.select2arrays(cmd, (float, int))

        ax.bar(
            x=timestamp,
            height=nfiles,
            width=duration,
            align="center", edgecolor="k")
        ax.set_ylabel(f'Number of Traces per {duration} seconds')
        ax.set_xlabel('Time [UTC]')
        ax.grid(True, linestyle=":")
        timetick(ax, "x")

    def show_pump_levels(self, ax: Optional[Axes] = None, *args, **kwargs):

        if ax is None:
            ax = plt.gca()

        timestamp, pump_levels = self.select2arrays(f'''
            select TIMESTAMP, VALUE from FILEATTRS 
                join (select distinct FILEID, TIMESTAMP from TRACES) using (FILEID)
                where FIELD="PUMP_LEVEL"
                order by TIMESTAMP
            ''', (float, float))

        ax.plot(
            timestamp,
            pump_levels,
            *args,
            **kwargs)
        ax.set_xlabel('Time [UTC]')
        ax.set_ylabel('Pump Level')
        ax.grid(True, linestyle=":")
        timetick(ax, "x")

    def show_timeline(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx() #fig.add_subplot(212, sharex=ax1)
        self.show_filetimes(ax1)
        self.show_pump_levels(ax2, "k.-")

    # def add_point(self, pointname: str, x: float, y: float, z: float):
    #     if self.transaction_open:



if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description=f"CoDataBase: "
                    f"Create/Update/Query a SqLite database "
                    f"from readdat.database.codatabase")

    # positional argument
    parser.add_argument(
        'database_filename',
        metavar='<database_filename.sqlite>',
        type=str,
        help=f'the name of the local sqlite database file, required!')

    parser.add_argument(
        '--build',
        nargs=1,
        metavar=('<root_dir>'),
        dest="build",  # attribute of the args NameSpace to send arguments to
        help='create a new database, load files from the given directory, and exit')

    default_system = "AUTO"
    parser.add_argument(
        '--acquisition_system', '-s',
        metavar=f'<acquisition_system>',
        default=default_system,
        choices=ACQUISITION_SYSTEMS,
        dest="acquisition_system",  # attribute of the args NameSpace to send arguments to
        help=f'''specify the acquisition system to use 
            for --build or --update
            default {default_system}
            ''')

    parser.add_argument(
        '--config',
        nargs='*',
        metavar='[<field> <value>]',
        dest="config",  # attribute of the args NameSpace to send arguments to
        help='see or modify the config table with the input data')

    parser.add_argument(
        '--addpoints',
        metavar='<csv_file>',
        dest="addpoints",  # attribute of the args NameSpace to send arguments to
        help='add new points in the data base from a csv file')

    parser.add_argument(
        '--addpoint',
        nargs=4,
        metavar='<pointname> <x> <y> <z>',
        dest="addonepoint",  # attribute of the args NameSpace to send arguments to
        help='add 1 new point in the data base ')

    parser.add_argument(
        '--update',
        action="store_true",
        dest="update",  # attribute of the args NameSpace to send arguments to
        help='update an existing database and exit')

    parser.add_argument(
        '--verbose', '-v',
        action="store_true",
        default=False,
        dest="verbose",  # attribute of the args NameSpace to send arguments to
        help='Database becomes verbose')

    # PLOTS
    parser.add_argument(
        '--timeline', '-t',
        action="store_true",
        dest="show_timeline",  # attribute of the args NameSpace to send arguments to
        help='plot the number of files as a function of time')

    parser.add_argument(
        '--pump_levels',
        action="store_true",
        dest="show_pump_levels",  # attribute of the args NameSpace to send arguments to
        help='plot the pump levels as a function of time, if any')

    # ========================================
    if not len(sys.argv) > 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    print(args)

    if not args.database_filename.endswith(".sqlite"):
        raise ValueError('database name does not end with .sqlite')

    # ========================================
    if args.acquisition_system is not None:
        if args.acquisition_system.upper() == "NONE":
            args.acquisition_system = None

        if args.build is None and args.update is None:
            raise ValueError('--acquisition_system must be used with --build or --update')

    # ========================================
    if args.build is not None:
        root_dir, = args.build

        if not os.path.isdir(root_dir):
            raise IOError(f'{root_dir=} is not a valid directory')
        root_dir = os.path.realpath(root_dir)

        if os.path.exists(args.database_filename):
            assert os.path.isfile(args.database_filename), "must be a file"
            if input(f'{args.database_filename=} exists, overwrite? y/[n]') != "y":
                sys.exit(1)
            os.remove(args.database_filename)

        with CodataBase(args.database_filename, create=True, verbose=args.verbose) as db:
            db.create_tables(sure=True)
            db.set_root_dir(root_dir=root_dir)
            db.find_files(file_search_path="*.sg2")
            db.extract_header(acquisition_system=args.acquisition_system, timezone="Europe/Paris")
        sys.exit(0)

    # ========================================
    # after this point the database must exist
    if not os.path.isfile(args.database_filename):
        raise IOError(f'{args.database_filename=} is not a valid sqlite file')

    # ========================================
    if args.update:
        with CodataBase(args.database_filename, create=False) as db:
            db.find_files(file_search_path="*.sg2")
            db.extract_header(acquisition_system=args.acquisition_system, timezone="Europe/Paris")
        sys.exit(0)

    # ========================================
    if args.config is not None:
        if len(args.config) == 0:
            with CodataBase(args.database_filename) as db:
                for field, value in db.select('select field, value from CONFIG'):
                    print(f"{field:>20s}: {value}")

        elif len(args.config) == 2:
            field, value = args.config

            with CodataBase(args.database_filename) as db:
                db.config(field, value)

        else:
            parser.print_help()
            sys.exit(1)

        sys.exit(0)

    # ========================================
    if args.addpoints is not None:
        csv_file = args.addpoints

        with CodataBase(args.database_filename) as db:
            db.add_points_from_csv(csv_file)

    # ========================================
    if args.addonepoint is not None:
        pointname, x, y, z = args.addonepoint

        with CodataBase(args.database_filename) as db:
            db.add_one_point(pointname, x, y, z)

    # ========================================
    if args.show_timeline is True:

        with CodataBase(args.database_filename) as db:
            db.show_timeline()
        plt.show()
        sys.exit(0)

    # ========================================
    if args.show_pump_levels is True:

        with CodataBase(args.database_filename) as db:
            db.show_pump_levels(color="r", linewidth=4)
        plt.show()
        sys.exit(0)
