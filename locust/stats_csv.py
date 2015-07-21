import csv
from locust import runners
from time import time
from datetime import datetime


def print_all_statistics():
    """
    Runs all print test run statistics methods

    This method is not run by default.
    It can be added to the quitting event in the locust test file by adding these lines:
        from locust.stats_csv import print_all_statistics
        from locust import events
        events.quitting += print_all_statistics

    Once added, this method will print each stats csv file to the directory that the test was run in.
    """
    date_time = get_date_time()
    print_test_run_statistics(date_time)
    print_test_percentiles(date_time)
    print_test_errors(date_time)


def print_test_run_statistics(date_time=None):
    """
    Generates a CSV file with stats for the test that was run

    This method is not run by default.
    It can be added to the quitting event in the locust test file by adding these lines:
        from locust.stats_csv import print_test_run_statistics
        from locust import events
        events.quitting += print_test_run_statistics

    Once added, this method will print a CSV file of stats to the directory that the test was run in.

    This method is included in print_all_statistics()

    Args:
        date_time (str): date_time string
            If None, will be generated automatically.
    """
    if not date_time:
        date_time = get_date_time()
    print_csv(get_test_run_stats_rows(), date_time, "test_run_stats")


def print_test_percentiles(date_time=None):
    """
    Generates a CSV file with percentile stats for the test that was run.

    This method is not run by default.
    It can be added to the quitting event in the locust test file by adding these lines:
        from locust.stats_csv import print_test_percentiles
        from locust import events
        events.quitting += print_test_percentiles

    Once added, this method will print a CSV file of percentile stats to the directory that the test was run in.

    This method is included in print_all_statistics()

    Args:
        date_time (str): date_time string
            If None, will be generated automatically.
    """
    if not date_time:
        date_time = get_date_time()
    print_csv(get_test_percentiles_rows(), date_time, "test_percentiles")


def print_test_errors(date_time=None):
    """
    Generates a CSV file with errors captured on the test run.

    This method is not run by default.
    It can be added to the quitting event in the locust test file by adding these lines:
        from locust.stats_csv import print_test_errors
        from locust import events
        events.quitting += print_test_errors

    Once added, this method will print a CSV file of errors to the directory that the test was run in.

    This method is included in print_all_statistics()

    Args:
        date_time (str): date_time string
            If None, will be generated automatically.
    """
    if not date_time:
        date_time = get_date_time()
    print_csv(get_test_error_rows(), date_time, "test_errors")


def get_test_run_stats_rows():
    """
    Returns statistics rows to be printed to a csv file
    """
    stats = runners.locust_runner.stats

    rows = [['Test Run Statistics\n'], [
        'Method',
        'Name',
        '# requests',
        '# failures',
        'Median response time',
        'Average response time',
        'Min response time',
        'Max response time',
        'Average Content Size',
        'Requests/s'
    ]]

    for key in sorted(stats.entries.keys()):
        entry = stats.entries[key]
        rows.append([
            '{}'.format(entry.method),
            '{}'.format(entry.name),
            '{:d}'.format(entry.num_requests),
            '{:d}'.format(entry.num_failures),
            '{:d}'.format(entry.median_response_time),
            '{:.0f}'.format(entry.avg_response_time),
            '{:d}'.format(entry.min_response_time or 0),
            '{:d}'.format(entry.max_response_time),
            '{:.0f}'.format(entry.avg_content_length),
            '{:.2f}'.format(entry.total_rps)
        ])

    total_stats = runners.locust_runner.stats.aggregated_stats("Total", full_request_history=True)
    rows.append([
        '{}'.format(total_stats.method),
        '{}'.format(total_stats.name),
        '{:d}'.format(total_stats.num_requests),
        '{:d}'.format(total_stats.num_failures),
        '{:d}'.format(total_stats.median_response_time),
        '{:.0f}'.format(total_stats.avg_response_time),
        '{:d}'.format(total_stats.min_response_time or 0),
        '{:d}'.format(total_stats.max_response_time),
        '{:.0f}'.format(total_stats.avg_content_length),
        '{:.2f}'.format(total_stats.total_rps)
    ])

    return rows


def get_test_percentiles_rows():
    """
    Returns percentile rows to be printed to a csv file.
    """
    stats = runners.locust_runner.stats

    rows = [['Test Run Percentiles\n'], [
        'Method',
        'Name',
        '# requests',
        '50%',
        '66%',
        '75%',
        '80%',
        '90%',
        '95%',
        '98%',
        '99%',
        '100%'
    ]]

    for key in sorted(stats.entries.keys()):
        entry = stats.entries[key]
        if entry.num_requests:
            rows.append([
                '{}'.format(entry.method),
                '{}'.format(entry.name),
                '{:6d}'.format(entry.num_requests),
                '{:6d}'.format(entry.get_response_time_percentile(0.50)),
                '{:6d}'.format(entry.get_response_time_percentile(0.66)),
                '{:6d}'.format(entry.get_response_time_percentile(0.75)),
                '{:6d}'.format(entry.get_response_time_percentile(0.80)),
                '{:6d}'.format(entry.get_response_time_percentile(0.90)),
                '{:6d}'.format(entry.get_response_time_percentile(0.95)),
                '{:6d}'.format(entry.get_response_time_percentile(0.98)),
                '{:6d}'.format(entry.get_response_time_percentile(0.99)),
                '{:6d}'.format(entry.max_response_time)
            ])
        else:
            rows.append([
                '{}'.format(entry.method),
                '{}'.format(entry.name),
                '0', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'
            ])

    return rows


def get_test_error_rows():
    """
    Returns errors from the test run to tbe printed to a csv file.
    """
    rows = [['Test Run Errors\n'], [
        'Count',
        'Message',
        'Traceback',
        'Nodes'
    ]]

    for exception in runners.locust_runner.exceptions.itervalues():
        nodes = ', '.join(exception['nodes'])
        rows.append([
            exception['count'],
            exception['msg'],
            exception['traceback'],
            nodes
        ])

    return rows


def print_csv(rows, date_time, test_type):
    """
    Print rows to a csv.

    Args:
        rows [[str, str, ...], [...], ...]: array of string arrays.
            This is passed into csv writer.
        date_time (str): date_time string
        test_type (str): name of the type of stats output being printed.
    """
    file_name = "{0}_{1}.csv".format(test_type, date_time)
    with open(file_name, 'wb') as stats_file:
        stats_writer = csv.writer(stats_file)
        stats_writer.writerows(rows)



def get_date_time():
    """
    Returns a datetime string from the system.
    """
    return datetime.fromtimestamp(time()).strftime('%Y%m%d%H%M%S')
