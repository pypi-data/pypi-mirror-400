import datetime


class DateId:
    """Calculate an integer value for months and dates from a base date"""

    def __init__(self, p_base_date_str="2008/01/01", p_target_date_str=None, p_target_day=None):
        """Calculate an integer value for months and dates from a base date"""
        self.base_date_str = p_base_date_str
        self.base_date_str = self.base_date_str.replace("-", "")
        self.base_date_str = self.base_date_str.replace("/", "")
        self.base_date = datetime.date(
            int(self.base_date_str[:4]), int(self.base_date_str[4:6]), int(self.base_date_str[-2:])
        )
        self.day_id = None
        self.month_id = None
        self.target_date = None
        self.target_date_str = None
        if p_target_date_str:
            self.calc_day_id(p_target_date_str=p_target_date_str)
            self.calc_month_id(p_target_date_str=p_target_date_str)
        elif p_target_day is not None:
            self.calc_day_id(p_target_day=p_target_day)
            self.calc_month_id(p_target_day=p_target_day)
        else:
            p_target_date_str = datetime.date.today().strftime("%Y-%m-%d")
            self.calc_day_id(p_target_date_str=p_target_date_str)
            self.calc_month_id(p_target_date_str=p_target_date_str)
        pass

    # end __init__

    def calc_day_id(self, p_target_date_str=None, p_target_day=None):
        """Returns the date id of the target date"""
        if p_target_date_str:
            self.target_date_str = p_target_date_str.replace("-", "")
            self.target_date_str = self.target_date_str.replace("/", "")
            self.target_date = datetime.date(
                int(self.target_date_str[:4]), int(self.target_date_str[4:6]), int(self.target_date_str[-2:])
            )
        elif p_target_day is not None:
            self.specific_date(p_target_day)
        one_day = datetime.timedelta(days=1)
        self.day_id = self.target_date - self.base_date
        if self.target_date >= self.base_date:
            self.day_id += one_day
        return self.day_id.days

    # end calc_day_id

    def generate_range(self, p_start_date_parm, p_end_date_parm):
        """Returns a range of date_id's in Tuple structure"""
        one_day = datetime.timedelta(days=1)
        if isinstance(p_start_date_parm, str):
            start_date_parm = p_start_date_parm.replace("-", "")
            start_date_parm = start_date_parm.replace("/", "")
            start_date = datetime.date(int(start_date_parm[:4]), int(start_date_parm[4:6]), int(start_date_parm[-2:]))
        elif isinstance(p_start_date_parm, int):
            start_date_day = datetime.timedelta(days=p_start_date_parm)
            start_date = self.base_date + start_date_day - one_day
        if isinstance(p_end_date_parm, str):
            end_date_parm = p_end_date_parm.replace("-", "")
            end_date_parm = end_date_parm.replace("/", "")
            end_date = datetime.date(int(end_date_parm[:4]), int(end_date_parm[4:6]), int(end_date_parm[-2:]))
        elif isinstance(p_end_date_parm, int):
            end_date_day = datetime.timedelta(days=p_end_date_parm)
            end_date = self.base_date + end_date_day - one_day
        i_len = end_date - start_date
        process_date = start_date
        days_tbl = []
        months_tbl = []
        old_month_id = self.calc_month_id(process_date.strftime("%Y-%m-%d")) - 1
        for i in range(i_len.days + 1):
            month_id = self.calc_month_id(process_date.strftime("%Y-%m") + "-01")
            day_id = self.calc_day_id(process_date.strftime("%Y-%m-%d"))
            row_days = (day_id, month_id, process_date.year, process_date.month, process_date.day, process_date)
            days_tbl.append(row_days)
            if month_id != old_month_id:
                row_months = (
                    month_id,
                    process_date.year,
                    process_date.month,
                    self.calc_day_id(process_date.strftime("%Y-%m") + "-01"),
                )
                months_tbl.append(row_months)
            process_date += one_day
            old_month_id = month_id
        return days_tbl, months_tbl

    # end generate_range

    def is_leap_year(self, p_target_year):
        """Determines if year is a leap year"""
        if p_target_year % 4 != 0:
            success = False
        elif p_target_year % 100 != 0:
            success = True
        elif p_target_year % 400 == 0:
            success = False
        else:
            success = True
        return success

    # end is_leap_year

    def calc_month_id(self, p_target_date_str=None, p_target_day=None):
        """Returns the month id of the target date"""
        if p_target_date_str:
            self.target_date_str = p_target_date_str.replace("-", "")
            self.target_date_str = self.target_date_str.replace("/", "")
            self.target_date = datetime.date(
                int(self.target_date_str[:4]), int(self.target_date_str[4:6]), int(self.target_date_str[-2:])
            )
        elif p_target_day:
            self.specific_date(p_target_day)
        self.month_id = (self.target_date.year - self.base_date.year) * 12
        if self.target_date >= self.base_date:
            self.month_id += self.target_date.month - self.base_date.month + 1
        else:
            self.month_id += self.target_date.month - 1
        return self.month_id

    # end calc_month_id

    def specific_date(self, p_day_id):
        """Returns the date in string format for the p_day_id"""
        self.day_id = datetime.timedelta(days=p_day_id)
        one_day = datetime.timedelta(days=1)
        if p_day_id > 0:
            self.target_date = self.base_date + self.day_id - one_day
        elif p_day_id < 0:
            self.target_date = self.base_date + self.day_id
        else:
            self.target_date = self.base_date
        self.target_date_str = self.target_date.strftime("%Y%m%d")
        # return self.target_date_str
