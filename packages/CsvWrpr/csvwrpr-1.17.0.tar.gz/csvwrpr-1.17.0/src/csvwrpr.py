import os
import sys
from pathlib import Path

import displayfx
from beetools import msg as tls_msg
from beetools import utils as tls_utils

# import logging

_path = Path(sys.argv[0])
_name = _path.stem


class CsvWrpr:
    """Wrpr for CSV Files

    This module copies a csv file into a different structure.  It returns
    the same csv file in a different structure i.e. list, dict or tuple.
    It also manipulates the header of the original csv file by either
    deleting it, adding a header or replacing it.
    """

    def __init__(
        self,
        p_csv_file_name,
        p_key1="",
        p_key2="",
        p_data_delimiter="",
        p_header_delimiter="",
        p_header="",
        p_del_head=False,
        p_struc_type={},
        p_csv_corr_str_file_name="",
        p_replace_header=False,
        p_subset_range=[],
        p_verbose=False,
        p_convert_none=True,
        p_bar_len=tls_utils.BAR_LEN,
        p_msg_width=tls_utils.MSG_LEN,
        p_match_nr_of_fields=False,
    ):
        """Initialize the class

        Parameters
        - p_parent_logger_name
          Name of the parent logger
        - p_csv_file_name
          Name of the file to be manipulated
        - p_key1 = ''
          It is only mandatory for Dict structures.  It will be used as the key.
        - p_key2 = ''
          It is only mandatory for 2 dimensional Dict structures.  It is the
          key in the second dimension.
        - delimiter = ''
          Specifies the delimiter of the csv file.  If it is specified, it
          will try to determine the delimiter from the first row in the csv
          file from the delimiter_list.
        - p_header = ''
          Actual header that will be used in a List format
          If "header" is empty, it assumes the first row in the csv file
          contains the header fields.
          - Lists and Tuples
            None
          - Dict
            Will be used for the keys of the dictionary.
        - p_del_head = ''
          - List and Tuple
            Assumes the first row contains header fields and the first row
            will be deleted.  Practically, if "p_del_head" contains any value,
            the first row will be removed.
          - Dict
            It assumes a header was present in the original csv file and
            is obsolete becbeetools.e the dictionary keys contains the header
            fields.  It will look for a key in the Dict with the value of
            "p_del_head" and delete this record from the Dict.
        - p_struc_type = ''
          - "List" will return the csv file in a list with all values in
            string format i.e [['',''],['','']].
          - "db" return the csv file in a Tuple with all values in string
            format i.e [('',''),('','')].  This is intended for integration
            with database modules where the csv file must be imported into
            a database table.
          - "Dict" or any other value will result in a Dict with the header
            as the keys to the Dict
        - p_csv_corr_str_file_name = ''
          In certain cases the csv file contain undesirable characters for
          instance a name and surname combination separated by a comma.  It
          is actually one field and must be read by as one filed but becbeetools.e
          the delimiter of the scv file is also a comma, it reads it as two
          separate fields.  This parameter gives the opportunity to change
          such strings to something that will execute to desire.
        - p_replace_header = ''
          This cbeetools.es the header from the csv file to be replaced by the
          "header" parameter i.e. the header of the original csv file is
          replaced.
        - p_subset_range[ left, right ]
          There are two parameters in this list.  The left parameter is the
          start and right the end.  Only records where the value of p_key1
          is equal or between these two values will be included.  The
          implication is that the p_key1 parameter must exist and left and
          right must be numbers.
        - p_verbose = False
          Suppress printing progress to screen
        - p_convert_none = True
          When "True" it will convert any field containing the word "NULL"
          or "None" to type None, alternatively it keeps "NULL" and "None" as
          the string content of the field
        - p_bar_len = 50
          Value passed to DisplayFx for the progress bar len
        - p_msg_width
          Value passed to beetools.msg_display to set the maximum width for a message
        """
        self.success = False
        self.bar_len = p_bar_len
        self.msg_width = p_msg_width
        self.combined_field = ""
        self.convert_none = p_convert_none
        self.corr_str_list = []
        self.csv_corr_str_file_name = p_csv_corr_str_file_name
        self.csv_file_fame = p_csv_file_name
        self.data_delimiter = p_data_delimiter
        self.del_head = p_del_head
        self.delimiter_list = [",", ";", "~", "|"]
        self.head = ""
        self.header = p_header
        self.header_delimiter = p_header_delimiter
        self.key1 = p_key1
        self.key2 = p_key2
        self.match_nr_of_fields = p_match_nr_of_fields
        self.nr_of_rows = 0
        self.replace_header = p_replace_header
        self.silent = p_verbose
        self.struc_type = p_struc_type
        self.subset_range = p_subset_range
        self.tail = ""
        self.t_tow = ""
        self.read_csv_corr_str_file()
        (self.head, self.tail) = os.path.split(self.csv_file_fame)
        if self.key2 == "":
            if self.struc_type == [] or self.struc_type == ():
                self.csv_db = []
            else:
                self.csv_db = {}
            self.read_one_key_csv()
        else:
            self.delhead = False
            self.struc_type = []
            self.csv_db = []
            self.read_two_key_csv()

    def append(
        self,
        p_append_path,
        p_key1="",
        p_key2="",
        p_data_delimiter="",
        p_header_delimiter="",
        p_header="",
        p_del_head=False,
        p_csv_corr_str_file_name="",
        p_replace_header=False,
        p_subset_range=[],
    ):
        """Append another csv file to the current data.

        Parameters
         - p_append_path
           Name of the file to be added
         - p_key1 = ''
           It is only mandatory for Dict structures.  It will be used as the key.
         - p_key2 = ''
           It is only mandatory for 2 dimensional Dict structures.  It is the
           key in the second dimension.
         - p_data_delimiter = ''
           Specifies the delimiter of the csv file.  If it is specified, it
           will try to determine the delimiter from the first row in the csv
           file from the delimiter_list.
         - p_header_delimiter = ''
           Specifies the delimiter of the header if different from the
           rest of the file or due to reading it from a different source
         - p_header = ''
           Actual header that will be used in a List format
           If "header" is empty, it assumes the first row in the csv file
           contains the header fields.
         - p_del_head = ''
           - List and Tuple
             Assumes the first row contains header fields and the first row
             will be deleted.  Practically, if "p_del_head" contains any value,
             the first row will be removed.
           - Dict
             It assumes a header was present in the original csv file and
             is obsolete becbeetools.e the dictionary keys contains the header
             fields.  It will look for a key in the Dict with the value of
             "p_del_head" and delete this record from the Dict.
         - struc_type = ''
           - "List" will return the csv file in a list with all values in
             string format i.e [['',''],['','']].
           - "db" return the csv file in a Tuple with all values in string
             format i.e [('',''),('','')].  This is intended for integration
             with database modules where the csv file must be imported into
             a database table.
           - "Dict" or any other value will result in a Dict with the header
             as the keys to the Dict
         - p_csv_corr_str_file_name = ''
           In certain cases the csv file contain undesirable characters for
           instance a name and surname combination separated by a comma.  It
           is actually one field and must be read by as one filed but becbeetools.e
           the delimiter of the scv file is also a comma, it reads it as two
           separate fields.  This parameter gives the opportunity to change
           such strings to something that will execute to desire.
         - p_replace_header = ''
           This cbeetools.es the header from the csv file to be replaced by the
           "header" parameter i.e. the header of the original csv file is
           replaced.
         - p_subset_range[ left, right ]
           There are two parameters in this list.  The left parameter is the
           start and right the end.  Only records where the value of p_key1
           is equal or between these two values will be included.  The
           implication is that the p_key1 parameter must exist and left and
           right must be numbers.
        """
        csv_to_append = CsvWrpr(
            p_append_path,
            p_key1=p_key1,
            p_key2=p_key2,
            p_data_delimiter=p_data_delimiter,
            p_header_delimiter=p_header_delimiter,
            p_header=p_header,
            p_del_head=p_del_head,
            p_struc_type=self.struc_type,
            p_csv_corr_str_file_name=p_csv_corr_str_file_name,
            p_replace_header=p_replace_header,
            p_subset_range=p_subset_range,
        )
        if isinstance(self.csv_db, dict):
            self.csv_db.update(csv_to_append.csv_db)
        self.nr_of_rows = len(self.csv_db)

    def export(self, p_export_file_name, p_export_delimiter="|"):
        """Export all of the current records."""
        if isinstance(self.csv_db, (list, tuple)):
            export_file = open(p_export_file_name, "w+", encoding="utf-8", errors="ignore")
            for i in range(len(self.csv_db)):
                export_str = p_export_delimiter.join(map(str, self.csv_db[i])) + "\n"
                export_file.write(export_str)
            export_file.close()
        elif isinstance(self.csv_db, dict):
            del self.csv_db[self.key1]
            export_list = self.csv_db.keys()
            self.export_sub_set(p_export_file_name, export_list, p_export_delimiter)
        pass

    def export_sub_set(self, p_export_file_name, p_sub_set_list, p_export_delimiter="|"):
        """Description"""
        export_file = open(p_export_file_name, "w+", encoding="utf-8", errors="ignore")
        export_str = p_export_delimiter.join(map(str, self.header)) + "\n"
        export_file.write(export_str)
        list_len = len(p_sub_set_list)
        export_qty = 0
        msg = tls_msg.display(
            f"Writing subset {os.path.split(p_export_file_name)[1]} ({list_len})",
            p_len=self.msg_width,
        )
        dfx = displayfx.DisplayFx(
            list_len,
            p_msg=msg,
            p_verbose=self.silent,
            p_bar_len=self.bar_len,
        )
        # This loop was not tested for a tuple and have to be corrected if found to be not working
        if isinstance(self.csv_db, (list, tuple)):
            field_pos = self.header.index(self.key1)
            for dfx_cntr, sub_set_id in enumerate(p_sub_set_list):
                # Traverse the entire list becbeetools.e there might be more that fulfill the criteria
                # in a list of tuple scenario.
                for csv_db_row in self.csv_db:
                    if sub_set_id == csv_db_row[field_pos]:
                        export_str = p_export_delimiter.join(map(str, csv_db_row)) + "\n"
                        export_file.write(export_str)
                        export_qty += 1
                dfx.update(dfx_cntr)
        elif isinstance(self.csv_db, dict):
            for dfx_cntr, sub_set_id in enumerate(p_sub_set_list):
                export_tow = []
                if sub_set_id in self.csv_db:
                    for field in self.header:
                        export_tow.append(self.csv_db[sub_set_id][field])
                    export_file.write(p_export_delimiter.join(map(str, export_tow)) + "\n")
                    export_qty += 1
                dfx.update(dfx_cntr)
        export_file.close()
        return export_qty

    def read_csv_corr_str_file(self):
        """Parameters"""
        if self.csv_corr_str_file_name:
            corr_file = open(self.csv_corr_str_file_name, encoding="utf-8", errors="ignore")
            raw_corr_data = corr_file.readlines()
            corr_file.close()
            for row in raw_corr_data:
                self.corr_str_list.append(row[:-1].split("~"))

    def read_one_key_csv(self):
        """Description"""

        def fix_row(p_row):
            """Description"""

            def adjust_delimiters(p_row):
                """Split the row in fields"""
                row = p_row
                row = row.split(self.data_delimiter)
                return row

            # end adjust_delimiters

            def replace_contents(p_row):
                """Replace the line target string with correct details"""
                row = p_row
                for corr in self.corr_str_list:
                    row = p_row.replace(corr[0], corr[1])
                return row

            row = replace_contents(p_row)
            row = adjust_delimiters(row)
            if not self.t_tow:
                self.combined_field = ""
                new_row = []
            else:
                new_row = self.t_tow
                self.combined_field = self.combined_field[:-1]
            for i, field in enumerate(row):
                if self.combined_field:
                    field = self.combined_field + self.data_delimiter + field
                    self.combined_field = ""
                if field[:1] == '"':
                    if field[-1:] == '"' and len(field) > 1:
                        new_row.append(field[1:-1])
                    else:
                        self.combined_field = field
                else:
                    new_row.append(field)
            if self.convert_none:
                for i, field in enumerate(new_row):
                    if field in ["NULL", "None"]:
                        new_row[i] = None
            if self.combined_field:
                self.t_tow = new_row
            else:
                self.t_tow = ""
            return new_row

        def get_delimiter():
            """Description"""
            if self.data_delimiter == "":
                delimiter_cntr = 0
                delimiter_pos = 0
                for i, delimiter in enumerate(self.delimiter_list):
                    if str(raw_csv_file_data[0]).count(self.delimiter_list[i]) > delimiter_cntr:
                        delimiter_cntr = str(raw_csv_file_data[0]).count(self.delimiter_list[i])
                        delimiter_pos = i
                self.data_delimiter = self.delimiter_list[delimiter_pos]
                if not self.header_delimiter:
                    self.header_delimiter = self.data_delimiter
            pass

        def append_row_to_list(p_row):
            """Append the corrected row to a list structure"""
            if key1_index is not None:
                if p_row[key1_index].isnumeric():
                    if not self.subset_range or (
                        int(p_row[key1_index]) >= self.subset_range[0]
                        and int(p_row[key1_index]) <= self.subset_range[1]
                    ):
                        self.csv_db.append(p_row)
                else:
                    self.csv_db.append(p_row)
            else:
                self.csv_db.append(p_row)
            pass

        def append_row_to_db(p_row):
            """Append the corrected row to a db (tuple) structure"""
            csv_row = tuple(p_row)
            if key1_index is not None:
                if csv_row[key1_index].isnumeric():
                    if not self.subset_range or (
                        int(csv_row[key1_index]) >= self.subset_range[0]
                        and int(csv_row[key1_index]) <= self.subset_range[1]
                    ):
                        self.csv_db.append(csv_row)
                else:
                    self.csv_db.append(csv_row)
            else:
                self.csv_db.append(csv_row)
            pass

        def append_row_to_dict(p_row):
            """Append the corrected row to a dictionary structure"""
            csv_row = {}
            for j, field in enumerate(self.header):
                csv_row[field] = p_row[j]
            if csv_row[self.key1].isnumeric():
                if not self.subset_range or (
                    int(csv_row[self.key1]) >= self.subset_range[0] and int(csv_row[self.key1]) <= self.subset_range[1]
                ):
                    self.csv_db[csv_row[self.key1]] = csv_row
            else:
                self.csv_db[csv_row[self.key1]] = csv_row
            pass

        def del_header():
            """Delete the header according to parameter switch"""
            if self.del_head:
                if self.struc_type == [] or self.struc_type == ():
                    del self.csv_db[0]
                elif self.struc_type == {}:
                    if self.del_head in self.csv_db.keys():
                        del self.csv_db[self.del_head]
            pass

        def replace_header():
            """Replace the header according to parameter switch"""
            if not self.header:
                self.header = raw_csv_file_data[0].rstrip("\n").replace('"', "").split(self.data_delimiter)
            if self.replace_header:
                if self.struc_type == []:
                    self.csv_db.append(self.header)
                elif self.struc_type == ():
                    self.csv_db.append(tuple(self.header))
                elif self.struc_type == {}:
                    self.csv_db[self.key1] = dict(
                        zip(
                            self.header,
                            [x.strip('\n"') for x in raw_csv_file_data[0].split(self.header_delimiter)],
                        )
                    )
                del raw_csv_file_data[0]
                self.nr_of_rows -= 1
            pass

        if os.path.isfile(self.csv_file_fame):
            csv_file = open(self.csv_file_fame, encoding="utf-8", errors="ignore")
            raw_csv_file_data = csv_file.readlines()
            csv_file.close()
            self.nr_of_rows = len(raw_csv_file_data)
            if self.nr_of_rows:
                get_delimiter()
                # str_end = 0
                replace_header()
                header_len = len(self.header)
                if self.key1:
                    key1_index = self.header.index(self.key1)
                else:
                    key1_index = None
                msg = tls_msg.display(
                    f"Reading {os.path.split(self.csv_file_fame)[1]} ({self.nr_of_rows})",
                    p_len=self.msg_width,
                )
                dfx = displayfx.DisplayFx(
                    self.nr_of_rows,
                    p_msg=msg,
                    p_verbose=self.silent,
                    p_bar_len=self.bar_len,
                )
                for row_cntr, row in enumerate(raw_csv_file_data):
                    fixed_row = fix_row(row.rstrip("\n"))
                    if not self.t_tow:
                        if (self.match_nr_of_fields and header_len == len(fixed_row)) or not self.match_nr_of_fields:
                            if self.struc_type == []:
                                append_row_to_list(fixed_row)
                            elif self.struc_type == ():
                                append_row_to_db(fixed_row)
                            else:
                                append_row_to_dict(fixed_row)
                        elif self.match_nr_of_fields:
                            log_str = '{};{};Unequal fields.  Removed rec #{} from {};"{}";"{}";"{}"'.format(
                                header_len,
                                len(fixed_row),
                                row_cntr,
                                self.csv_file_fame,
                                ",".join(self.header),
                                row,
                                ",".join(fixed_row),
                            )
                    dfx.update(row_cntr)
                self.success = True
            else:
                if not self.silent:
                    log_str = f"File does not have data - {self.csv_file_fame}"
            del_header()
        else:
            if not self.silent:
                log_str = f"File does not exist: {self.csv_file_fame}\n"
                print(log_str)
        return self.csv_db

    def read_two_key_csv(self):
        """Description"""
        log_str = self.read_one_key_csv()
        self.csv_db = {}
        msg = tls_msg.display("Build two key structure", p_len=self.msg_width)
        dfx = displayfx.DisplayFx(
            len(log_str),
            p_msg=msg,
            p_verbose=self.silent,
            p_bar_len=self.bar_len,
        )
        for row_cntr, row in enumerate(log_str):
            row_dict = {}
            for field in self.header:
                row_dict[field] = row[self.header.index(field)]
            if row_dict[self.key1] not in self.csv_db:
                self.csv_db[row_dict[self.key1]] = {row_dict[self.key2]: row_dict}
            else:
                # Cater for duplicate keys.  Assume the last entry is the incorrect one.
                if not row_dict[self.key2] in self.csv_db[row_dict[self.key1]]:
                    self.csv_db[row_dict[self.key1]][row_dict[self.key2]] = row_dict
                else:
                    # Log duplicates.  Insert writing errors to file here if necessary.
                    error_str = "read_two_key_csv Duplicate entry: {} {}".format(
                        row_dict[self.key1],
                        row_dict[self.key2],
                    )
                    print(error_str)
            dfx.update(row_cntr)
