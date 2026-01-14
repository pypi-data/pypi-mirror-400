import time
import math
import datetime
import pandas as pd
from uuid import uuid4
from threading import Thread


class ErrorLogs:
    """ Register Python Error Logs """

    def __init__(self, project_name, pipeline, ip_address, request_url, sql_con, timeout=30*60, print_sql=False):
        """ Initialize the class
        :param project_name: Name of the project being run. it must be already declared in PythonEmailProjectSeverity
        :param pipeline: Pipeline name being run. It must identify the process being executed uniquely
        :param ip_address: IP Address
        :param request_url: URL requested by the client
        :param sql_con: Connection to the Database to upload the Logs
        :param timeout: Time in seconds after which an unsuccessful log will be sent
        :param print_sql: Print the SQL statement sent to the server
        """
        self.log_df = pd.DataFrame({'ProjectName': [project_name], 'Successful': [0], 'Sent': [0],
                                    'IPAddress': [str(ip_address).replace("'", '"')],
                                    'RequestUrl': [str(request_url).replace("'", '"')],
                                    'StartedDate': [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")]})
        self.sql_con = sql_con
        self.timeout = timeout
        self.print_sql = print_sql
        self.guid = str(uuid4())
        self.pipeline = pipeline
        self.failure_type = []
        self.completed = False
        Thread(target=self.start_threading).start()

    def start_threading(self):
        """ Start a threading to update on failure if the script breaks or the pipeline gets blocked
        """
        step = 10
        time_range = math.ceil(self.timeout / step)
        for times in range(time_range):
            time.sleep(step)
            if self.completed:
                break

        if not self.completed:
            elapsed_time = str(datetime.timedelta(seconds=round(self.timeout)))[2:]
            self.on_failure(error_message=f'The pipeline failed to succeed after running '
                                          f'for {elapsed_time} minutes')

    def on_success(self, pipeline=None):
        """ Update log on success
        :param pipeline: Pipeline name being run. It must identify the process being executed uniquely
        """
        if not self.completed:
            if pipeline is not None:
                self.pipeline = pipeline
            successful_columns = {'Successful': 1, 'Resolved': 1, 'Pipeline': self.pipeline, 'GuidKey': self.guid,
                                  'FinishedDate': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}
            self.log_df = self.log_df.assign(**successful_columns)
            self.completed = True
            self.sql_con.insert(self.log_df, 'Staging', 'Logs', print_sql=self.print_sql)

    def on_failure(self, error_message, pipeline=None, section=None, critical=True, proposed_solution=None):
        """ Update log on failure
        :param error_message: Error message to be sent in the Log
        :param pipeline: Pipeline name being run. It must identify the process being executed uniquely
        :param section: Indicate the script section. Useful to locate the error
        :param critical: Indicate whether it should avoid sending successful logs
        :param proposed_solution: Proposed solution to the error message
        """
        if pipeline is not None:
            self.pipeline = pipeline
        unsuccessful_columns = {'Successful': 0, 'Section': section, 'Pipeline': self.pipeline,
                                'GuidKey': self.guid, 'Critical': 1 if critical is True else 0,
                                'FinishedDate': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"),
                                'ErrorMessage': str(error_message).replace("'", '"')}
        self.log_df = self.log_df.assign(**unsuccessful_columns)
        if proposed_solution is not None:
            self.log_df = self.log_df.assign(**{'ProposedSolution': proposed_solution})
        self.completed = True
        self.sql_con.insert(self.log_df, 'Staging', 'Logs', print_sql=self.print_sql)
        self.failure_type.append(self.completed)

    @staticmethod
    def register_failure(email_log, section, error_, solutions=None, pipeline=None):
        """Register a failure in the email log
        :param email_log: Instance of PythonEmailProjectSeverity
        :param section: Indicate the script section. Useful to locate the error
        :param error_: Error message to be sent in the Log
        :param solutions: List of solutions for the error messages
        :param pipeline: Pipeline name being run. It must identify the process being executed uniquely
        """
        solution_header = list(filter(lambda x: section.startswith(x), list(solutions.keys())))
        if len(solution_header) > 0:
            proposed_solution = solutions[solution_header[0]]
            email_log.on_failure(error_, section=section, proposed_solution=proposed_solution, pipeline=pipeline)
        else:
            email_log.on_failure(error_, section=section, pipeline=pipeline)
