import sys
import subprocess
import urllib2
import re
import traceback
from time import sleep
from subprocess import Popen, PIPE
from urllib import URLopener

__result_count__ = 10


########################
# WP Cli Profiler Test #
########################

class wp_cli():

    wp_cli_profiler_results = []

    def wp_cli_download(self):
        # Here we download a local copy of WP Cli
        print("\n\033[1;31;49m---- Downloading WP Cli ----\033[1;37;49m")
        url = 'https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar'
        temp = URLopener()
        temp.retrieve(url, './wp-cli.phar')
        print "\nSuccess: Downloaded"

    def wp_cli_profiler_download(self):
        # Here we download the WP Profile module for WP Cli
        print("\n\033[1;31;49m---- Downloading WP Cli Profiler ----\033[1;37;49m\n")
        process = subprocess.Popen('/usr/local/php56/bin/php-cli wp-cli.phar package install wp-cli/profile-command', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        output, error = process.communicate()
        result = process.returncode
        temp_list = []
        lines = re.split('\t|\n', output)
        for item in lines:
            temp_list.append(item)
        print temp_list [-2]


    def wp_cli_profiler_results_get(self):
        temp_list = []
        for index, item in enumerate(self.wp_cli_profiler_results):
            if index < len(self.wp_cli_profiler_results):
                if index is 0:
                    continue
                if index is len(self.wp_cli_profiler_results)-1:
                    break
                if index is len(self.wp_cli_profiler_results)-2:
                    break
                else:
                    item[1] = re.sub(r'\"|[\ s]', '', item[1])
                    temp_list.append(item)
        return temp_list



    def wp_cli_profiler_run(self, type, request):
        # The idea behind this function is to install the WP Profiler module for WP Cli and run an automated test with it
        self.wp_cli_download()
        self.wp_cli_profiler_download()

        # Since Python 2.4.3 does not support the 'subprocess.check_output' function I used the 'subprocess.Popen' one
        # Since the WP Profile module for WP Cli does not work properly with PHP 7+ I'll instead we use it with PHP Cli 5.6
        # Not sure what implications this may have but from what I can see it completes the test properly
        print("\n\033[1;33;49m---- WP Cli Profiler Results ----\033[1;37;49m")

        if type is "stage":
            # If there is a request then we list only the specified stage
            if request != "":
                command = "/usr/local/php56/bin/php-cli wp-cli.phar profile stage " + request + " --spotlight --order=DESC --orderby=time --fields=hook,time,cache_ratio --skip-plugins=sg-cachepress"
            # If there is no request then we set all stages to be listed
            if request is "":
                command = "/usr/local/php56/bin/php-cli wp-cli.phar profile stage  --spotlight --order=DESC --orderby=time --fields=stage,time,cache_ratio  --skip-plugins=sg-cachepress"
        if type is "hook":
            if request != "":
                command = "/usr/local/php56/bin/php-cli wp-cli.phar profile " + request + " --all --spotlight --order=DESC --orderby=time --fields=callback,time,location  --skip-plugins=sg-cachepress"
            if request is "":
                command = "/usr/local/php56/bin/php-cli wp-cli.phar profile hook --all --spotlight --order=DESC --orderby=time --fields=callback,time,location  --skip-plugins=sg-cachepress"

        process = subprocess.Popen(command, stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        # The 'output' variable is what we receive as results from the command above and it is returned as a string
        # Analogically the 'error' variable returns an error message, provided there is such by running the command
        output, error = process.communicate()
        result = process.returncode

        # Here we split the 'output' variable into a list by using '\n' and '\t' as delimiters
        temp_list = []
        words = re.split('\t|\n', output)
        for item in words:
            temp_list.append(item)

        # Then we crete a list of lists - each internal list contains three rows - the callback, time and location
        results_list = [temp_list[i:i + 3] for i in range(0, len(temp_list), 3)]
        self.wp_cli_profiler_results = results_list

        # Finally we print the number of results set with the '__result_count__' variable in an okay-ish table
        # Also, not having Python 2.7+ on all our servers really, really sucks :(
        temp_counter = 0
        temp_result_len = len(results_list)
        for i, d in enumerate(results_list):
            if temp_counter < __result_count__ + 1:
                line = '| '.join(str(x).ljust(50) for x in d)
                if i == 0:
                    print ('-' * len(line))
                print (line)
                if i == 0:
                    print ('-' * len(line))
                temp_counter += 1
                if i == temp_result_len - 1:
                    print ('-' * len(line))

            else:
                break
        print ("\n")



    # Soon to be deprecated section below


    #########################
    # Google PageSpeed Test #
    #########################

class pagespeed:

    # The name of the database we generated
    db_backup = ""
    # A list of the website's active plugins
    plugins_list = []
    # The website's URL
    site_url = ""
    # A check if the function has been called
    pagespeed_has_started = False
    # The results from running the Google PageSpeed test
    pagespeed_result_list = []
    # The initial results from Google PageSpeed test without active plugins
    pagespeed_initial_result = {}


    def website_db_backup_generate(self):
        # With this method we generate a DB Backup and save its name
        website_db_backup_generate_process = subprocess.Popen('wp db export --skip-plugins --skip-themes', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        website_db_backup_generate_process_result, website_db_backup_generate_process_error_message = website_db_backup_generate_process.communicate()
        website_db_backup_generate_process.wait()
        website_db_backup_generate_process_code = website_db_backup_generate_process.returncode

        # Here we tidy the resulting string so that it contains only the DB name
        db_name = re.search('(?<=\').*.sql', website_db_backup_generate_process_result)

        # Here we set the 'db_backup' class variable to have the value of the 'db_name' process result
        self.db_backup = db_name.group(0)

    def website_db_backup_get(self):
        # Here we return the 'self.db_backup' class variable
        return self.db_backup

    def website_db_backup_restore(self):
        reset = subprocess.Popen('wp db reset', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        restore_command = 'wp db import ' + self.website_db_backup_get()
        restore = subprocess.Popen(restore_command, stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)

    def website_plugins_set(self):
        # With this method we get a list of the website's active plugins
        website_plugins_get_process = subprocess.Popen('wp plugin list --status=active --fields=name --skip-plugins --skip-themes', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        website_plugins_get_process_result, website_plugins_get_process_error_message = website_plugins_get_process.communicate()
        website_plugins_get_process_code = website_plugins_get_process.returncode

        # Here we split the 'plugins' string into a list
        temp_list = []
        words = re.split('\t|\n', website_plugins_get_process_result)
        for item in words:
            temp_list.append(item)
        # Removing the first element from the plugin list as it is 'name'
        if len(temp_list) is 0:
            print "There are no active plugins on the website."
            print "\n\033[1;31;49m---- Exiting ----\033[1;37;49m\n"
            sys.exit()
        temp_list.pop(0)
        # Removing the last element from the plugin list as it is whitespace
        del temp_list[-1]
        # Here we crete a list of lists - each internal list contains three rows of active plugins
        results_list = [temp_list[i:i + 3] for i in range(0, len(temp_list), 3)]
        # Not having Python 2.7+ on all our servers really sucks :(
        # So we manually generate an okay-ish table of the plugin names
        for i, d in enumerate(results_list):
            line = '| '.join(str(x).ljust(50) for x in d)
            print (line)
        print ("\n")
        # Here we set the 'self.plugins_list' class variable to store all of the website's active plugins' names
        # The 'self.plugins_list' class variable that we set is a list
        self.plugins_list = results_list

    def website_plugins_get(self):
        # Here we return the 'self.plugins_list' class variable
        return self.plugins_list

    def website_url_set(self):
        # With this method we extract the website's URL from the website's database
        website_url_set_process = subprocess.Popen('wp option get home --skip-plugins --skip-themes', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        website_url_set_process_result, website_url_set_process_error_message = website_url_set_process.communicate()
        website_url_set_process_code = website_url_set_process.returncode

        # The 'result_url' variable that we set is a string
        website_url_set_process_result = re.sub(r'\r|\n', '', website_url_set_process_result)
        self.site_url = website_url_set_process_result

    def website_url_get(self):
        # Here we return the 'self.site_url' class variable
        return self.site_url

    def pagespeed_get_website_speed(self, raw_response, plugin_name, dynamic_cache_header):
        # With this method we strip down the results from the PageSpeed tests and extract only the 'speed_index' value
        pagespeed_raw_results = re.search('\"speed-index\": {.*}', raw_response, re.DOTALL).group(0)
        pagespeed_speed_index = re.search('\"displayValue\": ".*"', pagespeed_raw_results).group(0)
        pagespeed_stripped_speed_index = re.sub(r'\"displayValue\": ', '', pagespeed_speed_index)
        pagespeed_stripped_speed_index = re.sub(r'\"|[\ s]', '', pagespeed_stripped_speed_index)
        pagespeed_stripped_speed_index = re.search(r'\d\.\d*', pagespeed_stripped_speed_index).group(0)
        # Here we turn the 'pagespeed_stripped_speed_index' value to a float
        # Since we're later going to compare the results
        numeric_result = float(pagespeed_stripped_speed_index)
        # Here we generate a list containing the 'plugin_name' (string) and the 'numeric_result' (float) from the PageSpeed test
        temp_list = {
            'plugin': plugin_name,
            'website_speed': "%.2f" % numeric_result,
            'dynamic_cache_support': dynamic_cache_header
        }
        # The 'temp_list' variable that we return is a list
        return temp_list

    def pagespeed_generate_loading_bar(self, count, total, status=''):
        # Code taken from here: https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
        bar_len = 100
        bar_filled_len = int(round(bar_len * count / total))
        percents = round(100 * count / total, 1)
        bar = '=' * bar_filled_len + '-' * (bar_len - bar_filled_len)
        # Printing the line below clears the screen from the previous output
        # This is necessary as otherwise bits of string are left from the previous output
        sys.stdout.write("\033[K")
        sys.stdout.write('[%s] %s%s - %s\r' % (bar, percents, '%', status))
        sys.stdout.flush()

    def pagespeed_results_get(self):
        return self.pagespeed_result_list

    def pagespeed_run(self):
        # With this method we deactivate all plugins on the website and run a Google PageSpeed test on each step
        # Of course, it automatically generates a DB backup and restores it once the testing is completed

        print("\033[1;31;49m---- Starting PageSpeed Test ----\033[1;37;49m\n")
        # This function generates the DB backup
        self.website_db_backup_generate()
        # Waiting for the DB to be generated
        sleep(5)
        # This function extracts the website's URL
        self.website_url_set()

        # Here we store the 'db_backup' class variable in a local variable
        db_backup_name = self.website_db_backup_get()
        # Here we store the 'site_url' class variable in a local variable
        site_url = self.website_url_get()

        # Finally we print the gathered information and then get and print the active plugins
        print"\n\033[1;31;49mURL\033[1;37;49m: ", site_url, "\033[1;31;40\nmDB Backup\033[1;37;49m: ", db_backup_name, "\n\033[1;31;49mActive Plugins\033[1;37;49m: "
        # Due to aesthetics we generate the active plugins list here
        self.website_plugins_set()
        # Here we store the 'self.plugins_list' class variable in a local variable
        active_plugins_list = self.website_plugins_get()

        # Here we create a local variable that counts the number of active plugins
        plugins_number_total = 0
        for list in active_plugins_list:
            for item in list:
                plugins_number_total += 1
        # The latter is important since each PageSpeed test runs on average for 15 seconds so we first 'si vruzvame gashtite'
        # By asking the operator whether he's notified the client not to make any changes to his website while the procedure is ongoing
        print "The Google PageSpeed test will run for at least [\033[1;33;49m", ((plugins_number_total + 1) * 15), "\033[1;37;49m] seconds. Have you informed the client not to make any changes on his website?"
        operator_input = str(raw_input("Y or N : "))
        if operator_input is 'Y':
            # The 'self.pagespeed_has_started' variable allows us to check if the test has been ran at least once
            # This is useful in scenarios when the test is aborted as in such case we restore the DB automatically
            self.pagespeed_has_started = True

            # Below we prepare the PageSpeed API's URL
            pagespeed_url = 'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=' + self.website_url_get() + '&strategy=mobile'

            # Here we deactivate all plugins on the website:
            process_plugins = subprocess.Popen('wp plugin deactivate --all --skip-plugins --skip-themes', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
            # And then activate the SG Optimizer one
            process_sg = subprocess.Popen('wp plugin activate sg-cachepress --skip-plugins --skip-themes', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)

            # Here we call the curl command in order to review the website's 'X-Proxy-Cache' header.
            dynamic_cache_header_command = 'curl -sIX GET ' + self.website_url_get() + ' --insecure | grep -i \'x-proxy-cache\':'
            dynamic_cache_header_process_first = subprocess.Popen(dynamic_cache_header_command, stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
            dynamic_cache_header_process = subprocess.Popen(dynamic_cache_header_command, stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
            dynamic_cache_header_process_result, dynamic_cache_header_process_error = dynamic_cache_header_process.communicate()
            # Here we sanitize the results from the curl command
            dynamic_cache_header_process_result = re.search('(HIT|MISS)', dynamic_cache_header_process_result).group(0)

            # Here we generated a base test that will be used for comparison when deactivating plugins
            print "\nRunning initial Google PageSpeed test ..."
            pagespeed_base_req = urllib2.Request(pagespeed_url)
            pagespeed_base_res = urllib2.urlopen(pagespeed_base_req)

            # Then we save the results from the initial test
            self.pagespeed_result_list.append(self.pagespeed_get_website_speed(pagespeed_base_res.read(), 'initial-test', dynamic_cache_header_process_result))

            # Lastly, we start iterating over the plugins list, activating each plugin and running a Google PageSpeed test on each step
            active_plugins_list_flattened = [y for x in active_plugins_list for y in x]
            for index, item in enumerate(active_plugins_list_flattened):
                # Here we activate the said plugin
                sys.stdout.flush()
                self.pagespeed_generate_loading_bar(index, plugins_number_total, 'Testing [\033[1;31;49m' + item + "\033[1;37;49m] plugin.")
                command = 'wp plugin activate ' + item + ' --skip-plugins --skip-themes'
                process = subprocess.Popen(command, stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)

                # Here we prepare a request to be sent to the PageSpeed API
                pagespeed_request = urllib2.Request(pagespeed_url)

                # Here we try to catch any error messages returned by the PageSpeed API
                # For example, 500 ISE, 400 Bad Request, etc.
                try:
                    # Clearing the website's cache:
                    process = subprocess.Popen('wp cache flush; wp transient delete --all; rm -rf ./wp-content/cache/*', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)

                    # Here we send a request to the PageSpeed API using the 'urlopen' method from the 'urllib2' library
                    pagespeed_response = urllib2.urlopen(pagespeed_request)

                    # Here we use cURL to check the website's 'x-proxy-cache' header with the plugin being deactivated
                    dynamic_cache_header_command = 'curl -sIX GET ' + self.website_url_get() + ' --insecure | grep -i \'x-proxy-cache\':'
                    dynamic_cache_header_process_first = subprocess.Popen(dynamic_cache_header_command, stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
                    dynamic_cache_header_process = subprocess.Popen(dynamic_cache_header_command, stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
                    dynamic_cache_header_process_result, dynamic_cache_header_process_error = dynamic_cache_header_process.communicate()

                    # Here we sanitize the results from the cURL command
                    dynamic_cache_header_process_result = re.search('(HIT|MISS)', dynamic_cache_header_process_result).group(0)

                    # As a precaution, here we set the script to sleep for 20 seconds. This way we cover scenarios when the PageSpeed API takes longer than 15 seconds to complete
                    sleep(20)

                    # Here we pass the results to be processed by the 'pagespeed_get_website_speed' method
                    # And then save it within the 'self.pagespeed_result_list' class variable
                    self.pagespeed_result_list.append(self.pagespeed_get_website_speed(pagespeed_response.read(), item, dynamic_cache_header_process_result))

                    # Here we reactivate the plugin so that we can have as accurate tests as possible
                    process = subprocess.Popen('wp plugin deactivate ' + item + ' --skip-plugins --skip-themes', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
                except urllib2.URLError:
                    # Below we ensure compatibility between Python 2.4.3 and 2.7.1 ....
                    t,e = sys.exc_info()[:2]
                    print "ERROR: Something went wrong with reviewing the website! Does the domain resolve properly? Does the website load properly?\nFull error message: ", e
                    # In cases of an error we break the iterating for loop
                    break
                except urllib2.HTTPError:
                    # Below we ensure compatibility for Python 2.4.3 ....
                    t, e = sys.exc_info()[:2]
                    print "ERROR: Something went wrong with reviewing the website! The Google PageSpeed API returned and error code.\nFull error message: ", e
                    # In cases of an error we break the iterating for loop
                    break

            # End of 'for small_list in active_plugins_list'
            self.pagespeed_generate_loading_bar(1, 1, 'Google PageSpeed Test completed!')

            # Here we restore the DB backup we generated earlier
            print"\n\n---- PageSpeed test completed. Restoring the [ ", new_pagespeed.website_db_backup_get(), " ] DB Backup ----\n"
            command = 'wp db import ' + new_pagespeed.website_db_backup_get() + ' --skip-plugins --skip-themes'
            process = subprocess.Popen(command, stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
            result, error = process.communicate()
            result_db = process.returncode
            print "\n", result
            print("\n\n\033[1;33;49m---- Google PageSpeed Results ----\033[1;37;49m\n")

            # Here we sort the results dictionary by the 'website_speed' key
            pagespeed_result_list_sorted_reverse = sorted(self.pagespeed_result_list, key=lambda i: i['website_speed'])

            # Here we set the 'self.pagespeed_result_list' class variable to have the same values as 'pagespeed_result_list_sorted_reverse'
            self.pagespeed_result_list = pagespeed_result_list_sorted_reverse

            # Here we retrieve the first item from the list which is the header of the results table
            temp_initial_result = {}
            for item in pagespeed_result_list_sorted_reverse:
                if item['plugin'] is 'initial-test':
                    temp_initial_result = item

            # Here we set the 'self.pagespeed_initial_result' class variable to have the same values as 'temp_initial_result'
            self.pagespeed_initial_result = temp_initial_result

            # Here we print the header of the results table
            first_line = '| ' + temp_initial_result['plugin'].ljust(30) + '| ' + temp_initial_result['website_speed'] + ' sec'.ljust(30) + '| difference'.ljust(30) + '     | dynamic cache'.ljust(30)
            print ('-' * len(first_line)), '\n', first_line, '\n', ('-' * len(first_line))

            # Here we iterate over the results dictionary
            for index, item in enumerate(pagespeed_result_list_sorted_reverse):
                # If item is the header of the table we skip it
                if item['plugin'] is 'initial-test':
                    continue
                # Else we print the item
                line = '| ' + item['plugin'].ljust(30) + '| ' + item['website_speed'] + ' sec'.ljust(30) + '| ' + str(float(item['website_speed']) - float(temp_initial_result['website_speed'])) + ' sec'.ljust(30) + '| ' + item['dynamic_cache_support'].ljust(30)
                print (line)
        else:
            # If the operator has not started the PageSpeed test
            print("\n\033[1;31;49m---- PageSpeed Test Aborted ----\033[1;37;49m\n")
            process = subprocess.Popen('rm -rf ./wpspeed.py', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
            process = subprocess.Popen('rm -rf ./wp-cli.phar', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
            sleep(5)


if __name__ == '__main__':

    ##########################
    # Recommendations Engine #
    ##########################

    def recommendations(wp_cli_test_results, pagespeed_test_results, initial_test_results):
        pagespeed_initial_cache_result = initial_test_results['dynamic_cache_support']
        pagespeed_cache_blocking_plugins_counter = 0
        pagespeed_cache_blocking_plugins = []
        print("\n\033[1;33;49m---- Recommendations ----\033[1;37;49m\n")
        for index, item in enumerate(pagespeed_test_results):
            # If a plugin has blocked the dynamic cache we add it to the 'pagespeed_cache_blocking_plugins' list
            if str(item['plugin'] is 'initial-test'):
                pass
            if re.search('MISS', item['dynamic_cache_support'], re.IGNORECASE):
                pagespeed_cache_blocking_plugins.append(item['plugin'])
                pagespeed_cache_blocking_plugins_counter += 1
        # If the 'pagespeed_cache_blocking_plugins' list is not the same size as the 'pagespeed_test_results' list
        if len(pagespeed_cache_blocking_plugins) is not len(pagespeed_test_results):
            for item in pagespeed_cache_blocking_plugins:
                print "\n> Plugin [\033[1;33;49m" + item + "\033[1;37;49m] is blocking the Dynamic Cache. Try deactivating it."
        elif len(pagespeed_cache_blocking_plugins) == len(pagespeed_test_results):
            print "\n> The SG Optimizer's Dynamic Cache does not work even with all plugins deactivated!\n"

        # Here we generate a list which is to be filled with the results from both speed tests
        total_list = []
        result_count = 0
        for list in wp_cli_test_results:
            for item in pagespeed_test_results:
                if result_count <= len(pagespeed_test_results):
                    result_count += 1
                    # If the name of the plugin from the 'pagespeed_test_results' dictionary is matched with the plugin name from the 'wp_cli_test_results' list's callbacks
                    if str(item['plugin'] is 'sg-cachepress'):
                        pass
                    if str(item['plugin'] is 'initial-test'):
                        pass
                    if (float(initial_test_results['website_speed']) < float(item['website_speed'])):
                        if (float('-0.5') > (float(initial_test_results['website_speed']) - float(item['website_speed'])) or (float(initial_test_results['website_speed']) - float(item['website_speed'])) > float('0.5')):
                            total_list.append({'plugin': item['plugin'], 'speed_wp': float(list[1]), 'speed_gp': float(item['website_speed']),'location': list[2]})
                    else:
                        pass
            # If the WP Profile reports the wp_cron as an issue
            wp_cron_regex = re.match('wp_cron', list[0], re.IGNORECASE)
            if bool(wp_cron_regex):
                print "\n> Replace the WP Cron with a real Cron Job. \nEvidence:"
                print "WP Hook name: " + list[0] + ", Time to load : " + list[1] + ", Location: " + list[2]

        # Then we sort the newly created list by the Google PageSpeed API
        total_list_sorted = sorted(total_list, key=lambda i: i['speed_wp'], reverse=True)
        if len(total_list_sorted) is 0:
            print "\n> Can't provide other recommendations"
        else:
            for index, item in enumerate(total_list_sorted):
                if index <= __result_count__:
                    print "\n> Deactivate or replace [\033[1;33;49m" + item['plugin'] + "\033[1;37;49m] plugin. \nEvidence:"
                    print "Website loading time without plugin: ", initial_test_results['website_speed'], " sec. With plugin: ",  item['speed_gp'],  " secs."

        print "\n\033[1;31;49m---- Exiting ----\033[1;37;49m\n"
        # Finally we cleanup after the script has completed - removing the script itself and wp-cli.phar
        exit_process = subprocess.Popen('rm -rf ./wpspeed.py', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        exit_process_second = subprocess.Popen('rm -rf ./wp-cli.phar', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        sleep(5)


    ########################
    # Start of the program #
    ########################

    # In case of an error message, we ensure that script cleans up after itself and if necessary restore the website to its original state
    try:
        # Creating a new instance of the 'wp_cli' class
        new_wp_cli = wp_cli()

        # Creating a new instance of the 'pagespeed' class
        new_pagespeed = pagespeed()

        # Starting the WP Cli Profiler test
        new_wp_cli.wp_cli_profiler_run()

        # Starting the Google PageSpeed test
        new_pagespeed.pagespeed_run()

        # Starting recommendations

        # The recommendations are based on both tests so if even one is not completed the recommendations method won't run
        if new_pagespeed.pagespeed_has_started:
            recommendations(new_wp_cli.wp_cli_profiler_results_get(), new_pagespeed.pagespeed_results_get(), new_pagespeed.pagespeed_initial_result)
        else:
            print "\n\033[1;31;49m---- Can't generate recommendations without Google PageSpeed test! ----\033[1;37;49m\n"

    # In case the operator stops the process
    except KeyboardInterrupt:
        print "\n\033[1;31;49m---- Exiting ----\033[1;37;49m\n"

        # In case the Google PageSpeed test was started we restore the website's DB
        if new_pagespeed.pagespeed_has_started:
            print "Interrupted! PageSpeed test was not completed. Restoring the [ \033[1;31;49m", new_pagespeed.website_db_backup_get() ,"\033[1;37;49m ] DB Backup"
            command = 'wp db import ' + new_pagespeed.website_db_backup_get() + ' --skip-plugins --skip-themes'
            process = subprocess.Popen(command, stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
            result, error = process.communicate()
            result_db = process.returncode
            print result

        # We remove the script itself along with the wp-cli.phar file that was downloaded
        process = subprocess.Popen('rm -rf ./wpspeed.py', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        process = subprocess.Popen('rm -rf ./wp-cli.phar', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        sleep(5)
    # In case a problem is encountered runtime
    except urllib2.HTTPError:
        # This exception mostly concerns the Google PageSpeed API
        t, e = sys.exc_info()[:2]
        traceback_message = traceback.format_exc()
        print "\n\033[1;31;49m---- Error ----\033[1;37;49m\n"
        print "The scirpt encountered a problem during Google PageSpeed test.\nError Message return by PageSpeed API: ", e, traceback_message

        # In case the Google PageSpeed test was started we restore the website's DB
        if new_pagespeed.pagespeed_has_started:
            print "\nRestoring the [ \033[1;31;49m", new_pagespeed.website_db_backup_get() ,"\033[1;37;49m ] DB Backup"
            new_pagespeed.website_db_backup_restore()

        # We remove the script itself along with the wp-cli.phar file that was downloaded
        process = subprocess.Popen('rm -rf ./wpspeed.py', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        process = subprocess.Popen('rm -rf ./wp-cli.phar', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        sleep(5)
    except urllib2.URLError:
        # This exception mostly concerns the Google PageSpeed API
        t, e = sys.exc_info()[:2]
        traceback_message = traceback.format_exc()
        print "\n\033[1;31;49m---- Error ----\033[1;37;49m\n"
        print "The scirpt encountered a problem during Google PageSpeed test.\nError Message return by PageSpeed API: \n", e, traceback_message

        # In case the Google PageSpeed test was started we restore the website's DB
        if new_pagespeed.pagespeed_has_started:
            print "\nRestoring the [ \033[1;31;49m", new_pagespeed.website_db_backup_get(), "\033[1;37;49m ] DB Backup"
            new_pagespeed.website_db_backup_restore()

        # We remove the script itself along with the wp-cli.phar file that was downloaded
        process = subprocess.Popen('rm -rf ./wpspeed.py', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        process = subprocess.Popen('rm -rf ./wp-cli.phar', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        sleep(5)
    except:
        # Handling general error messages
        t, e = sys.exc_info()[:2]
        traceback_message = traceback.format_exc()
        print "\n\033[1;31;49m---- Error ----\033[1;37;49m\n"
        print "The scirpt encountered a problem during runtime. Please report this to Todor Ivanov via Slack. \nError Message: \n", e, traceback_message

        # In case the Google PageSpeed test was started we restore the website's DB
        if new_pagespeed.pagespeed_has_started:
            print "\nRestoring the [ \033[1;31;49m", new_pagespeed.website_db_backup_get(), "\033[1;37;49m ] DB Backup"
            new_pagespeed.website_db_backup_restore()

        # We remove the script itself along with the wp-cli.phar file that was downloaded
        process = subprocess.Popen('rm -rf ./wpspeed.py', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        process = subprocess.Popen('rm -rf ./wp-cli.phar', stderr=PIPE, stdin=PIPE, stdout=PIPE, shell=True)
        sleep(5)



