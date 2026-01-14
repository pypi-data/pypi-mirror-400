from collections.abc import Iterator, Mapping, Sequence
import csv
import datetime as dt
import numpy as np


class CsvRecorder:
    '''Iteratively record a set of sampled signals in a CSV formatted file.

    The output file is opened on instantiation and the fields (columns) to
    save in the file are automatically determined on the first call to
    write_data. When recording is complete call close.

    Args:
        filename: name of CSV file
    '''

    def __init__(self, filename: str) -> None:
        self._filename = filename
        self._fp = open(filename, 'w', newline='')
        self._writer = csv.writer(self._fp, delimiter=',')
        self._header = None

    def close(self) -> None:
        '''Close the file.

        No more data can be written after calling close.
        '''
        self._fp.close()
        self._writer = None

    def write_data(self, data: Mapping[str|int, Sequence[int|float]]) -> None:
        '''Write a block of samples to the file.

        The data is provided in a dictionary of sample arrays, each having
        the same length (number of samples). The keys represent signal names
        which correspond to fields/columns in the CSV file. The CSV header is
        written on the first call to write_data which determines the set of
        fields and order of fields for the file. Each subsequent call to
        write_data must have the same fields and appends the samples to the
        CSV file.

        Args:
            data: block of samples to write
        '''
        if self._writer is None:
            raise Exception(f'CSV file closed')
        if self._header is None:
            self._header = list(data.keys())
            self._writer.writerow(self._header)

        n_rows = len(data[self._header[0]])
        for i in range(n_rows):
            row = []
            for k in self._header:
                val = data[k][i]
                if val.is_integer():
                    val = int(val)
                row.append(val)
            self._writer.writerow(row)


class CsvRecording:
    '''Load a set of sampled signals from a CSV formatted file.

    The CSV file is expected to represent a set of sampled signals or
    time series with uniform sampling rate. Several ways of of storing
    timestamps are supported to accommodate various formats used by
    FieldLine software as well as files from other sources. In all
    supported cases the time field(s) are converted to a floating point
    value in seconds and available through the 'time' key. If the file
    contains a 'time' column then it is interpreted as a float and used
    unaltered. Columns which are recognized as representing magnetic
    field values are automatically converted to units of Tesla as the
    file is read.

    By default the samplerate of the file is computed as the mean time
    between samples using available timestamps. For short recordings
    with rx_t columns this may be inaccurate due to sample buffering
    during the recording. This can be solved by providing the
    samplerate if is known or ignoring the time stream and computing
    your own separately.

    Data is retrievable by stream/channel/column name by indexing an
    object of this type. The object also supports iteration and will
    iterate through all streams except time. This makes for convenient
    signal processing or plotting, for example::

        csv_recording = CsvRecording('some_file.csv')
        t = csv_recording['time']
        for stream in csv_recording:
            do_something(t, csv_recording[stream])

    Args:
        filename: name of CSV file
        time_zero: subtract the first timestamp from all times if True
        fs: samplerate in Hz, 0 to estimate from timestamps
        limit: max number of samples to read from file, 0 for all
    '''

    def __init__(self, filename: str,
                 time_zero: bool = False,
                 fs: float = 0.0,
                 limit: int = 0) -> None:
        self._filename = filename
        self._fs = fs
        self._data = []
        self._time = []
        self.ch_names = []
        system_date_time = False
        date_col_i = 0
        time_col_i = 1
        time_from_n = False
        n_samples = 0
        with open(self._filename, newline='') as csvfile:
            reader = csv.reader((line.replace('\0','') for line in csvfile))
            header = next(reader)

            if 'System_Date' in header and 'System_Time' in header:
                system_date_time = True
                date_col_i = header.index('System_Date')
                time_col_i = header.index('System_Time')

            for col in header:
                if col.lower() != 'time' and col != 'System_Date' and col != 'System_Time' and col != 'n':
                    self.ch_names.append(col)
                    self._data.append([])
                if 'rx_t' in col:
                    time_from_n = True

            for row in reader:
                for i,col in enumerate(header):
                    if col.lower() == 'time':
                        self._time.append(float(row[i]))
                    elif col == 'n':
                        self._time.append(int(row[i]))
                    elif col not in ['System_Date', 'System_Time']:
                        if col.endswith('-18') or 'dds_output_freq' in col or 'rf_freq' in col or 'larmor_freq' in col:
                            val = float(row[i]) * 4e-3 / (2**32-1) / 6.99583
                            self._data[self.ch_names.index(col)].append(val)
                        elif col.endswith('-23') or 'mag_mz' in col or 'mag' in col:
                            val = float(row[i]) * 1e-13
                            self._data[self.ch_names.index(col)].append(val)
                        else:
                            self._data[self.ch_names.index(col)].append(float(row[i]))
                if system_date_time:
                    ts = dt.datetime.strptime(f'{row[date_col_i]} {row[time_col_i]}', '%Y-%m-%d %H:%M:%S.%f')
                    self._time.append(ts.timestamp())
                n_samples += 1
                if limit > 0 and n_samples > limit:
                    break
        if time_from_n:
            if self._fs == 0:
                rx_t_ch = None
                for ch in self.ch_names:
                    if 'rx_t' in ch:
                        rx_t_ch = ch
                        break
                if rx_t_ch is not None:
                    ts = np.mean(np.diff(self._data[self.ch_names.index(rx_t_ch)]))
                    if ts > 0:
                        self._fs = 1/ts
            if self._fs != 0:
                self._time = [ n/self._fs for n in self._time ]

        if self._fs == 0:
            self._fs = float(1/np.mean(np.diff(self._time)))

        if time_zero:
            self._time = [ t - self._time[0] for t in self._time ]

    def samplerate(self) -> float:
        '''Get the file samplerate.

        Samplerate is either provided at instantiation or computed as
        the mean period between samples.

        Returns:
            float: samplerate in Hz
        '''
        return self._fs

    def __getitem__(self, index: str) -> Sequence[float]:
        '''Get the data samples for a stream.

        Args:
            index: stream/channel/column name

        Returns:
            Sequence[float]: data samples
        '''
        if index == 'time':
            return self._time
        else:
            return self._data[self.ch_names.index(index)]

    def __iter__(self) -> Iterator[str]:
        '''Get an iterator for data streams.

        Returns:
            Iterator[str]: iterator of non-time stream names
        '''
        return iter(self.ch_names)

    def stream_matches_critera(self, stream_list: Sequence[str], stream: str) -> bool:
        '''Check if a stream name matches a list of criteria.

        Args:
            stream_list: list of stream names or substrings to match in stream names
            stream: stream name to check for matches in stream_list criteria

        Returns:
            bool: True if stream matches criteria in stream_list, False otherwise
        '''
        # check for exact matches
        if stream in stream_list:
            return True

        # check for substring matches
        for stream_filter in stream_list:
            if stream_filter in stream:
                return True

        return False

    def match_streams(self, criteria: Sequence[str]) -> Sequence[str]:
        '''Return a list of streams matching specified criteria.

        Criteria list may include exact stream names and stream name substrings.
        Exact matches take priority and when found are removed from substring
        searches on remaining streams. An empty list of criteria will return
        all stream names.

        Args:
            criteria: list of stream names or substrings to find

        Returns:
            Sequence[str]: list of stream names found to match criteria
        '''
        if len(criteria) == 0:
            return self.ch_names
        else:
            ret_ch = []
            search_channels = []
            # add exact matches and remove them from the running for partial matches
            for ch in criteria:
                if ch in self.ch_names:
                    ret_ch.append(ch)
                else:
                    search_channels.append(ch)

            # check remaining args for partial matches
            for ch in self.ch_names:
                if self.stream_matches_critera(search_channels, ch):
                    ret_ch.append(ch)

            return ret_ch

