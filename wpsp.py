import getopt
import sys
import subprocess
import urllib2
import re
import traceback
from time import sleep
from subprocess import Popen, PIPE
from urllib import URLopener


class WP_Profiler:

    #wp_cli_profiler_results = []

    def __init__(self):
        self.wp_cli_download()
        self.wp_cli_profiler_download()

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

    # Function seems to be deprecated
    # The self.wp_cli_profiler_results variable is not used
    def profiler_results_get(self):
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

    def profiler_results_print(self, result_list, **kwargs):
        temp_counter = 0

        # Comment needed
        result_count = 10

        for key, value in kwargs.items():
            if key is "result_count":
                result_count = value

        for dict_index, dict_ref in enumerate(result_list):
            if dict_index < result_count - 1:
                print("|{:<25}|{:<25}|{}".format(dict_ref['name'], dict_ref['value'], dict_ref['extra']))

        # Code below seems to be deprecated
        '''for index, item in enumerate(result_list):
            if temp_counter < result_count + 1:
                line = '| '.join(str(x).ljust(30) for x in item)
                if index == 0:
                    print ('-' * len(line))
                print (line)
                if index == 0:
                    print ('-' * len(line))
                temp_counter += 1
                if index == temp_result_len - 1:
                    print ('-' * len(line))

            else:
                break
        print ("\n")'''

    def profiler_run(self, type, request):
        # The idea behind this function is to install the WP Profiler module for WP Cli and run an automated test with it
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
        #results_list = [temp_list[i:i + 3] for i in range(0, len(temp_list), 3)]

        results_dict = []

        for i in range(0, len(temp_list)-3, 3):
            temp = {
                'name': temp_list[i],
                'value': temp_list[i+1],
                'extra': temp_list[i+2]
            }
            results_dict.append(temp)

        # Finally we return the result list
        return results_dict


    def analytics(self, cli_args):
        # Self note: Pass the cli arugments with the "sys.argv[1:]" method

        seconds = 1
        count = 10

        # Handling cli arguments
        # The 's' character stands for seconds and 'c' for count
        # The former sets the value above which we show results
        # While the latter sets the total number of results we show
        try:
            opts, args = getopt.getopt(cli_args, "hs:c:", ["seconds=", "count="])
        except getopt.GetoptError:
            print 'Usage: wpsp.py -s <integer> -c <integer>'
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print 'Usage: wpsp.py -s <integer> -c <integer>'
                print '-s | --seconds \tTells the script to search for results above N seconds'
                print '-c | --count \tTells the script to print only N number of results'
                sys.exit()
            elif opt in ("-s", "--seconds"):
                seconds = arg
            elif opt in ("-c", "--count"):
                count = arg




if __name__ == '__main__':

    newwp = WP_Profiler()
    results = newwp.profiler_run("stage", "")
    newwp.profiler_results_print(results)
    #print("The results are: ", results)


    # Here we handle exceptions


    # Here we remove the downloaded wp-cli.phar file
    # And the wpsp.py script file
