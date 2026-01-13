import datetime
import sys


class FixDate:
    """Attempts to correct dates and convert to standard format"""

    def __init__(
        self,
        p_in_date_str,
        p_out_format="%Y%m%d",
        p_in_format="YMD",
        p_set_day_to_one=True,
    ):
        """Description"""
        self.success = False
        self.success = False
        self.comp_pos_day = False
        self.comp_pos_month = False
        self.comp_pos_year = False
        self.date = None
        self.date_str = None
        self.day = None
        self.even_day_months = [4, 6, 9, 11]
        self.in_date_str = p_in_date_str
        self.in_format = p_in_format
        self.leap_day_months = [2]
        self.month = None
        self.month_dict = {
            "JAN": 1,
            "FEB": 2,
            "MAR": 3,
            "APR": 4,
            "MAY": 5,
            "JUN": 6,
            "JUL": 7,
            "AUG": 8,
            "SEP": 9,
            "OCT": 10,
            "NOV": 11,
            "DEC": 12,
        }
        self.separators = "/-."
        self.set_day_to_one = p_set_day_to_one
        self.un_even_day_months = [0, 1, 3, 5, 7, 8, 10, 12]
        self.year = None
        self._get_comp_pos()
        if self._get_components():
            if self._fix_type_errors():
                self._fix_century()
                try:
                    self.date = datetime.date(self.year, self.month, self.day)
                    self.date_str = self.date.strftime(p_out_format)
                    self.success = True
                except ValueError:
                    if self.year > 0 and self.month > 0 and self.day > 0:
                        self._check_day_and_month_swap()
                        try:
                            self.date = datetime.date(self.year, self.month, self.day)
                            self.date_str = self.date.strftime(p_out_format)
                            self.success = True
                        except ValueError:
                            if self.set_day_to_one:
                                self._set_day_to_one()
                                try:
                                    self.date = datetime.date(self.year, self.month, self.day)
                                    self.date_str = self.date.strftime(p_out_format)
                                    self.success = True
                                except ValueError:
                                    print(
                                        "Scenario not foreseen.  Forced system exit:\nYear: {}, Month: {}, Day: {}".format(
                                            self.year, self.month, self.day
                                        )
                                    )
                                    self.success = False
                                    sys.exit()
        # if not self.success:
        #     self.day = None
        #     self.month = None
        #     self.year = None
        #     self.date = None
        #     self.date_str = None
        pass

    # end __init__

    def _check_day_and_month_swap(self):
        """Description"""
        if self.month < 1 or self.month > 12:
            if self.day >= 1 or self.day <= 12:
                if (
                    (self.day in self.un_even_day_months and self.month >= 1 and self.month <= 31)
                    or (self.day in self.even_day_months and self.month >= 1 and self.month <= 30)
                    or (self.day in self.leap_day_months and self.month >= 1 and self.month <= 28)
                ):
                    t_month = self.month
                    self.month = self.day
                    self.day = t_month
                else:
                    self.month = None
            else:
                self.month = None
        pass

    # end _check_day_and_month_swap

    def _fix_century(self):
        """Description"""
        if len(str(self.year)) < 4:
            # d_fmt = int( datetime.datetime.now().strftime( '%y' ))
            if self.year > int(datetime.datetime.now().strftime("%y")) and self.month > 0 and self.day > 0:
                self.year = self.year + 1900
            else:
                self.year = self.year + 2000
        pass

    # end _fix_century

    def _fix_type_errors(self):
        """Description"""
        try:
            self.year = int(self.year)
            try:
                self.month = int(self.month)
                try:
                    self.day = int(self.day)
                    success = True
                except ValueError:
                    success = False
            except ValueError:
                success = False
        except ValueError:
            success = False
        return success

    # end _fix_type_errors

    def _get_components(self):
        """Description"""

        def insert_seperators():
            """Description"""
            if len(self.in_date_str) == 6:
                self.in_date_str = self.in_date_str[:2] + "/" + self.in_date_str[2:]
                self.in_date_str = self.in_date_str[:5] + "/" + self.in_date_str[5:]
            elif len(self.in_date_str) == 8:
                if self.comp_pos_year == 0:
                    self.in_date_str = self.in_date_str[:4] + "/" + self.in_date_str[4:]
                    self.in_date_str = self.in_date_str[:7] + "/" + self.in_date_str[7:]
                elif self.comp_pos_year == 2:
                    self.in_date_str = self.in_date_str[:2] + "/" + self.in_date_str[2:]
                    self.in_date_str = self.in_date_str[:5] + "/" + self.in_date_str[5:]
                elif self.comp_pos_year == 1:
                    self.in_date_str = self.in_date_str[:2] + "/" + self.in_date_str[2:]
                    self.in_date_str = self.in_date_str[:7] + "/" + self.in_date_str[7:]
            pass

        # end insert_seperators

        def swap_year_and_day():
            """Description"""
            tmp = self.comp_pos_day
            self.comp_pos_day = self.comp_pos_year
            self.comp_pos_year = tmp
            pass

        # end swap_year_and_day

        success = False
        if self.in_date_str is not None:
            components = False
            self.in_date_str = self.in_date_str.strip()
            if self.in_date_str.isnumeric():
                insert_seperators()
            if self.in_date_str:
                for sep in self.separators:
                    self.in_date_str = self.in_date_str.replace(sep, "/")
                components = self.in_date_str.split("/")
                if len(components) == 3:
                    success = True
                    if components[self.comp_pos_month].upper() in self.month_dict:
                        if self.in_format == "YMD":
                            self.in_format = "DMY"
                            swap_year_and_day()
                        components[self.comp_pos_month] = self.month_dict[components[self.comp_pos_month].upper()]
                        success = True
                    if len(components[self.comp_pos_day]) == 4:
                        swap_year_and_day()
                if success:
                    self.day = components[self.comp_pos_day]
                    self.month = components[self.comp_pos_month]
                    self.year = components[self.comp_pos_year]
        return success

    # end _get_components

    def _get_comp_pos(self):
        """Description"""
        self.comp_pos_day = self.in_format.upper().find("D")
        self.comp_pos_month = self.in_format.upper().find("M")
        self.comp_pos_year = self.in_format.upper().find("Y")
        pass

    # end _get_comp_pos

    def _is_leap_year(self):
        """Description"""
        if self.year % 4 == 0 and self.year % 100 != 0:
            if self.year % 400 == 0:
                return True
        elif self.year % 4 != 0:
            return False

    # end _is_leap_year

    def _set_day_to_one(self):
        """Description"""
        if self.day < 1:
            self.day = 1
        elif self.month in self.un_even_day_months and self.day > 31:
            self.day = 31
        elif self.month in self.even_day_months and self.day > 30:
            self.day = 30
        elif self.month in self.leap_day_months:
            if self._is_leap_year():
                if self.day > 29:
                    self.day = 28
            else:
                if self.day > 28:
                    self.day = 28
        pass

    # end _set_day_to_one


# end FixDate
