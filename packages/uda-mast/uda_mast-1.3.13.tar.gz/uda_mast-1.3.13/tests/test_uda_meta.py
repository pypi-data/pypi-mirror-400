import pyuda
import mast

class TestUDAMeta():
    client = pyuda.Client()

    def test_list_signals_all(self):
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, machine='mast')

        assert (hasattr(sig_list[0], 'signal_name') and 
                hasattr(sig_list[0], 'source_alias') and
                hasattr(sig_list[0], 'pass_') and
                hasattr(sig_list[0], 'type') and
                hasattr(sig_list[0], 'shot') and
                hasattr(sig_list[0], 'description') and
                hasattr(sig_list[0], 'generic_name') and
                hasattr(sig_list[0], 'signal_status') and
                hasattr(sig_list[0], 'mds_name'))

    def test_list_signals_mastu_all(self):
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, machine='mastu')

        assert (hasattr(sig_list[0], 'signal_name') and 
                hasattr(sig_list[0], 'source_alias') and
                hasattr(sig_list[0], 'pass_') and
                hasattr(sig_list[0], 'type') and
                hasattr(sig_list[0], 'shot') and
                hasattr(sig_list[0], 'description') and
                hasattr(sig_list[0], 'signal_status'))

    def test_list_signals_one_source(self):
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, alias='amc', machine='mast')

        all_alias = [s.source_alias for s in sig_list]

        assert set(all_alias) == {'amc'}

    def test_list_signals_mastu_one_source(self):
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, alias='amc', machine='mastu')

        all_alias = [s.source_alias for s in sig_list]

        assert set(all_alias) == {'amc'}

    def test_list_signals_search(self):
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, signal_search='%plas%', machine='mast')

        with_plas_name = [s for s in sig_list if 'plas' in s.signal_name.lower()]

        assert len(with_plas_name) == len(sig_list)

    def test_list_signals_mastu_search(self):
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, signal_search='%plas%', machine='mastu')

        with_plas_name = [s for s in sig_list if 'plas' in s.signal_name.lower()]

        assert len(with_plas_name) == len(sig_list)

    def test_list_signals_desc_search(self):
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, description_search='%plas%', machine='mast')

        with_plas_desc = [s for s in sig_list if 'plas' in s.description.lower()]

        assert len(with_plas_desc) == len(sig_list)

    def test_list_signals_mastu_desc_search(self):
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, description_search='%plas%', machine='mastu')

        with_plas_desc = [s for s in sig_list if 'plas' in s.description.lower()]

        assert len(with_plas_desc) == len(sig_list)

    def test_list_signals_one_type(self):
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, signal_type='A', machine='mast')

        all_type = [s.type for s in sig_list if s.type == 'Analysed']

        assert len(all_type) == len(sig_list)

    def test_list_signals_mastu_one_type(self):
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, signal_type='A', machine='mastu')

        all_type = [s.type for s in sig_list if s.type == 'Analysed']

        assert len(all_type) == len(sig_list)

    def test_list_signals_one_shot(self):
        sig_list_all = self.client.list(mast.mast_client.ListType.SIGNALS, machine='mast')
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, shot=30420)

        assert 0 < len(sig_list) < len(sig_list_all)

    def test_list_signals_mastu_one_shot(self):
        sig_list_all = self.client.list(mast.mast_client.ListType.SIGNALS, machine='mastu')
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, shot=44244)

        assert 0 < len(sig_list) < len(sig_list_all)

    def test_list_signals_one_shot_one_source(self):
        sig_list_one_shot = self.client.list(mast.mast_client.ListType.SIGNALS, shot=30420)
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, shot=30420, alias='amc')

        assert 0 < len(sig_list) < len(sig_list_one_shot)

    def test_list_signals_mastu_one_shot_one_source(self):
        sig_list_one_shot = self.client.list(mast.mast_client.ListType.SIGNALS, shot=44226)
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, shot=44226, alias='amc')

        assert 0 < len(sig_list) < len(sig_list_one_shot)

    def test_list_signals_one_shot_search(self):
        sig_list_one_shot = self.client.list(mast.mast_client.ListType.SIGNALS, shot=30420)
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, shot=30420, signal_search='%plas%')

        assert 0 < len(sig_list) < len(sig_list_one_shot)

        all_plas = [s.signal_name for s in sig_list if 'plas' in s.signal_name.lower()]
        assert len(all_plas) == len(sig_list)

    def test_list_signals_mastu_one_shot_search(self):
        sig_list_one_shot = self.client.list(mast.mast_client.ListType.SIGNALS, shot=44226)
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, shot=44226, signal_search='%plas%')

        assert 0 < len(sig_list) < len(sig_list_one_shot)

        all_plas = [s.signal_name for s in sig_list if 'plas' in s.signal_name.lower()]
        assert len(all_plas) == len(sig_list)

    def test_list_signals_one_shot_desc_search(self):
        sig_list_one_shot = self.client.list(mast.mast_client.ListType.SIGNALS, shot=30420)
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, shot=30420, description_search='%plas%')

        assert 0 < len(sig_list) < len(sig_list_one_shot)

        all_plas = [s.signal_name for s in sig_list if 'plas' in s.description.lower()]
        assert len(all_plas) == len(sig_list)

    def test_list_signals_one_shot_one_type(self):
        sig_list_one_shot = self.client.list(mast.mast_client.ListType.SIGNALS, shot=30420)
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, shot=30420, signal_type='A')

        assert 0 < len(sig_list) < len(sig_list_one_shot)

        all_type = [s.type for s in sig_list if s.type == 'Analysed']

        assert len(all_type) == len(sig_list)

        pass_nums = [s.pass_ for s in sig_list]

        assert not (-1 in pass_nums)

    def test_list_signals_mastu_one_shot_one_type(self):
        sig_list_one_shot = self.client.list(mast.mast_client.ListType.SIGNALS, shot=44226)
        sig_list = self.client.list(mast.mast_client.ListType.SIGNALS, shot=44226, signal_type='A')

        assert 0 < len(sig_list) < len(sig_list_one_shot)

        all_type = [s.type for s in sig_list if s.type == 'Analysed']

        assert len(all_type) == len(sig_list)

        pass_nums = [s.pass_ for s in sig_list]

        assert not (-1 in pass_nums)

    def test_list_source_all(self):
        source_list = self.client.list(mast.mast_client.ListType.SOURCES, machine='mast')

        assert (hasattr(source_list[0], 'source_alias') and hasattr(source_list[0], 'type') and hasattr(source_list[0], 'description'))

    def test_list_source_mastu_all(self):
        source_list = self.client.list(mast.mast_client.ListType.SOURCES, machine='mastu')

        assert (hasattr(source_list[0], 'source_alias') and hasattr(source_list[0], 'type'))
#        assert (hasattr(source_list[0], 'source_alias') and hasattr(source_list[0], 'type') and hasattr(source_list[0], 'description'))

    def test_list_source_one_type(self):
        source_list = self.client.list(mast.mast_client.ListType.SOURCES, signal_type='A', machine='mast')

        all_type = [s.type for s in source_list if s.type == 'Analysed']

        assert len(all_type) == len(source_list)

    def test_list_source_mastu_one_type(self):
        source_list = self.client.list(mast.mast_client.ListType.SOURCES, signal_type='A', machine='mastu')

        all_type = [s.type for s in source_list if s.type == 'Analysed']

        assert len(all_type) == len(source_list)

    def test_list_source_one_shot(self):
        all_source_list = self.client.list(mast.mast_client.ListType.SOURCES, machine='mast')
        source_list = self.client.list(mast.mast_client.ListType.SOURCES, shot=27543)

        assert 0 < len(source_list) < len(all_source_list)

        assert (hasattr(source_list[0], 'source_alias') and 
                hasattr(source_list[0], 'type') and
                hasattr(source_list[0], 'pass_') and
                hasattr(source_list[0], 'status') and
                hasattr(source_list[0], 'run_id') and
                hasattr(source_list[0], 'format') and
                hasattr(source_list[0], 'filename') and
                hasattr(source_list[0], 'shot') and
                hasattr(source_list[0], 'description'))

    def test_list_source_mastu_one_shot(self):
        all_source_list = self.client.list(mast.mast_client.ListType.SOURCES, machine='mastu')
        source_list = self.client.list(mast.mast_client.ListType.SOURCES, shot=44226)

        assert 0 < len(source_list) < len(all_source_list)

        assert (hasattr(source_list[0], 'source_alias') and 
                hasattr(source_list[0], 'type') and
                hasattr(source_list[0], 'pass_') and
                hasattr(source_list[0], 'status') and
                hasattr(source_list[0], 'format') and
                hasattr(source_list[0], 'filename') and
                hasattr(source_list[0], 'shot') and
                hasattr(source_list[0], 'description'))


    def test_list_source_one_shot_one_type(self):
        source_list_one_shot = self.client.list(mast.mast_client.ListType.SOURCES, shot=27543)
        source_list = self.client.list(mast.mast_client.ListType.SOURCES, shot=27543, signal_type='A')

        assert 0 < len(source_list) < len(source_list_one_shot)

        all_type = [s.type for s in source_list if s.type == 'Analysed']

        assert len(all_type) == len(source_list)

    def test_list_source_mastu_one_shot_one_type(self):
        source_list_one_shot = self.client.list(mast.mast_client.ListType.SOURCES, shot=44226)
        source_list = self.client.list(mast.mast_client.ListType.SOURCES, shot=44226, signal_type='A')

        assert 0 < len(source_list) < len(source_list_one_shot)

        all_type = [s.type for s in source_list if s.type == 'Analysed']

        assert len(all_type) == len(source_list)

    def test_list_source_one_shot_one_pass(self):
        test_pass = 2

        source_list_one_shot = self.client.list(mast.mast_client.ListType.SOURCES, shot=25003)
        source_list = self.client.list(mast.mast_client.ListType.SOURCES, shot=25003, pass_number=test_pass)

        assert 0 < len(source_list) < len(source_list_one_shot)

        all_pass = [s.pass_ for s in source_list if s.pass_ == test_pass]

        assert len(all_pass) == len(source_list)

    def test_list_source_mastu_one_shot_one_pass(self):
        test_pass = 0

        source_list_one_shot = self.client.list(mast.mast_client.ListType.SOURCES, shot=44226)
        source_list = self.client.list(mast.mast_client.ListType.SOURCES, shot=44226, pass_number=test_pass)

        assert 0 < len(source_list) < len(source_list_one_shot)

        all_pass = [s.pass_ for s in source_list if s.pass_ == test_pass]

        assert len(all_pass) == len(source_list)

    def test_list_archive_directories(self):
        directories_list = self.client.list_archive_directories("$MAST_DATA/30420")
        assert len(directories_list) > 0


    def test_list_archive_file_sources(self):
        files = self.client.list_archive_files("$MAST_DATA/30420/LATEST")
        assert len(files) > 0


    def test_list_archive_file_signals(self):
        filesignals_ida = self.client.list_file_signals("$MAST_DATA/30420/LATEST/amc0304.20")
        assert len(filesignals_ida) > 0

        filesignals_nc = self.client.list_file_signals("$MAST_DATA/30420/LATEST/xma030420.nc")
        assert len(filesignals_nc) > 0

    def test_source_pass_in_range(self):
        from datetime import datetime

        latest_pass = self.client.latest_source_pass_in_range("amc")

        assert (hasattr(latest_pass, 'exp_number') and
                hasattr(latest_pass, 'pass_number') and
                hasattr(latest_pass, 'shot_datetime'))

        shot_start = 20000
        shot_end = 30420
        latest_pass_shots = self.client.latest_source_pass_in_range("amc",
                                                                    shot_start=shot_start,
                                                                    shot_end=shot_end)
        assert (hasattr(latest_pass_shots, 'exp_number') and
                hasattr(latest_pass_shots, 'pass_number') and
                hasattr(latest_pass_shots, 'shot_datetime'))

        assert (min(latest_pass_shots.exp_number) >= shot_start
                and max(latest_pass_shots.exp_number) <= shot_end)

        datetime_start = '2011-01-01 00:00:00'
        datetime_end = '2012-01-01 00:00:00'
        latest_pass_dates = self.client.latest_source_pass_in_range("amc",
                                                                    datetime_start=datetime_start,
                                                                    datetime_end=datetime_end)
        assert (hasattr(latest_pass_dates, 'exp_number') and
                hasattr(latest_pass_dates, 'pass_number') and
                hasattr(latest_pass_dates, 'shot_datetime'))

        start_dt = datetime.strptime(datetime_start, '%Y-%m-%d %H:%M:%S')
        end_dt = datetime.strptime(datetime_end, '%Y-%m-%d %H:%M:%S')

        min_dt = datetime.strptime(latest_pass_dates.shot_datetime[0],
                                   '%Y-%m-%d %H:%M:%S')
        max_dt = datetime.strptime(latest_pass_dates.shot_datetime[-1],
                                   '%Y-%m-%d %H:%M:%S')

        assert (min_dt >= start_dt and max_dt <= end_dt)

    def test_latest_pass(self):
        last_pass = self.client.latest_source_pass("amc", 13400)

        assert (last_pass == 1)


    def test_latest_shot(self):
        last_shot = self.client.latest_shot()

        assert (last_shot > 40000)

    def test_shot_date_time(self):
        date, time = self.client.get_shot_date_time(30420)

        assert (date == '2013-09-25')
        assert (time == '12:35:28')

    def test_list_shots(self):
        mclient = mast.mast_client.MastClient(self.client)

        shot_info = mclient.list_shots(source='epm')
        shots_source = [s.shots for s in shot_info]

        assert (len(shot_info) > 0)
        assert (hasattr(shot_info[0], 'shots') and
                hasattr(shot_info[0], 'date') and
                hasattr(shot_info[0], 'time'))

        shot_info = mclient.list_shots(alias='epm')
        shots_alias = [s.shots for s in shot_info]

        assert (len(shot_info) > 0)
        assert (hasattr(shot_info[0], 'shots') and
                hasattr(shot_info[0], 'date') and
                hasattr(shot_info[0], 'time'))
        assert (shots_source == shots_alias)

        shot_info = mclient.list_shots(signal='/amc/plasma_current')

        assert (len(shot_info) > 0)
        assert (hasattr(shot_info[0], 'shots') and
                hasattr(shot_info[0], 'date') and
                hasattr(shot_info[0], 'time'))

        shot_info = mclient.list_shots(signal_search='%plasma_current%')
        assert (len(shot_info) > 0)
        assert (hasattr(shot_info[0], 'shots') and
                hasattr(shot_info[0], 'date') and
                hasattr(shot_info[0], 'time'))

        shot_start = 43000
        shot_end = 45222
        shot_info = mclient.list_shots(source='epm', shot_start=shot_start, shot_end=shot_end)

        shots = [s.shots for s in shot_info]
        assert (min(shots) >= shot_start and max(shots) <= shot_end)

        datetime_start = '2021-02-01'
        datetime_end = '2021-03-01'
        shot_info = mclient.list_shots(datetime_start=datetime_start,
                                           datetime_end=datetime_end)
        assert (len(shot_info) > 0)
        assert (hasattr(shot_info[0], 'shots') and
                hasattr(shot_info[0], 'date') and
                hasattr(shot_info[0], 'time'))

        time_start = '12:00'
        time_end = '14:00'
        shot_info = mclient.list_shots(time_start=time_start,
                                        time_end=time_end)
        assert (len(shot_info) > 0)
        assert (hasattr(shot_info[0], 'shots') and
                hasattr(shot_info[0], 'date') and
                hasattr(shot_info[0], 'time'))

        shot_info_first = mclient.list_shots(get_first=True, source='xma')
        assert (len(shot_info_first)  > 0)

        shot_info_last = mclient.list_shots(get_last=True, source='xma')
        assert (len(shot_info_last)  > 0)
