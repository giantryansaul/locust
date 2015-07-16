import csv
from locust import runners
from time import time
from datetime import datetime

def request_stats_csv():
    """
    Generates a CSV file with stats for the test that was run

    This method is not run by default. It can be added to the quitting event in the locust test file by adding these lines:
        from locust import request_stats_csv, events
        events.quitting += request_stats_csv

    Once added, this method will print a CSV file of stats to the current directory
    """
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

    stats = runners.locust_runner.stats
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

    rows.append(['\nTest Run Percentiles\n'])
    rows.append([
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
    ])

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

    rows.append(['\nTest Run Errors\n'])
    rows.append([
        'Count',
        'Message',
        'Traceback',
        'Nodes'
    ])

    for exception in runners.locust_runner.exceptions.itervalues():
        nodes = ', '.join(exception['nodes'])
        rows.append([
            exception['count'],
            exception['msg'],
            exception['traceback'],
            nodes
        ])

    file_name = "test_results_{0}.csv".format(datetime.fromtimestamp(time()).strftime('%Y%m%d%H%M%S'))
    with open(file_name, 'wb') as stats_file:
        stats_writer = csv.writer(stats_file)
        stats_writer.writerows(rows)
