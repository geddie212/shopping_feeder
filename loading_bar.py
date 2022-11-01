import sys
import config

progress = config.progress

class ProgressBar:

    def __init__(self, total_records):
        self.total_records = total_records
        self.product_length = len(total_records)-1
        self.start_bar = '|'
        self.end_bar = '|'
        self.remaining_bar = '-'
        self.remaining_bar *= len(total_records)
        self.loading_bar = ''
        self.total_records_print = len(total_records)

    def print_progress_bar(self, current_record, custom_message):
        global progress
        self.loading_bar += '█'
        self.remaining_bar = self.remaining_bar[:-1]
        progress = f'{current_record} of {self.total_records_print} {custom_message}\n\n{self.start_bar}{self.loading_bar}{self.remaining_bar}{self.end_bar}'
        return progress