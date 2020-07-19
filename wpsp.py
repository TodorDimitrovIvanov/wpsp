import getopt
import sys
import subprocess
import re
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

    def profiler_result_print_multiple(self, result_list, **kwargs):
        # Comment needed
        result_count = 10

        for key, value in kwargs.items():
            if key is "result_count":
                result_count = value

        for index, dict in enumerate(result_list):
            name = dict.get('name')
            value = dict.get('value')
            extra = dict.get('extra')
            if index <= result_count:
                print("|{:<25}|{:<25}|{}".format(name, value, extra))

    def profiler_result_print_single(self, result_list, target, **kwargs):
        # Comment needed
        result_count = 10

        for key, value in kwargs.items():
            if key is "result_count":
                result_count = value

        for index, item in enumerate(result_list):
            if index <= result_count:
                if item['name'] is target:
                    name = item.get('name')
                    value = item.get('value')
                    extra = item.get('extra')
                    print("|{:<25}|{:<25}|{}".format(name, value, extra))

    def profiler_result_print_by_parent(self, result_list, parent, **kwargs):
        # Comment needed
        result_count = 10

        for key, value in kwargs.items():
            if key is "result_count":
                result_count = value

        for index, item in enumerate(result_list):
            if item['parent'] is parent:
                if index <= result_count:
                    name = item.get('name')
                    value = item.get('value')
                    extra = item.get('extra')
                    print("|{:<25}|{:<25}|{}".format(name, value, extra))

    def profiler_run(self, type, request):
        # The idea behind this function is to install the WP Profiler module for WP Cli and run an automated test with it
        # Since Python 2.4.3 does not support the 'subprocess.check_output' function I used the 'subprocess.Popen' one
        # Since the WP Profile module for WP Cli does not work properly with PHP 7+ I'll instead we use it with PHP Cli 5.6
        # Not sure what implications this may have but from what I can see it completes the test properly

        if type is "stage":
            # If there is a request then we list only the specified stage
            if request != "":
                command = "/usr/local/php56/bin/php-cli wp-cli.phar profile stage " + request + " --spotlight --order=DESC --orderby=time --fields=hook,time,cache_ratio --skip-plugins=sg-cachepress"
            # If there is no request then we set all stages to be listed
            if request is "":
                command = "/usr/local/php56/bin/php-cli wp-cli.phar profile stage  --spotlight --order=DESC --orderby=time --fields=stage,time,cache_ratio  --skip-plugins=sg-cachepress"
        if type is "hook":
            if request != "":
                command = "/usr/local/php56/bin/php-cli wp-cli.phar profile hook " + request + " --all --spotlight --order=DESC --orderby=time --fields=callback,time,location  --skip-plugins=sg-cachepress"
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
            if i >= 3 < len(temp_list) - 3:
                # Comment needed
                timing = re.sub('s', '', temp_list[i+1])
                temp = {
                    'parent': '',
                    'name': temp_list[i],
                    'value': float(timing),
                    'extra': temp_list[i+2]
                }
                results_dict.append(temp)
            else:
                temp = {
                    'parent': '',
                    'name': temp_list[i],
                    'value': temp_list[i + 1],
                    'extra': temp_list[i + 2]
                }
                results_dict.append(temp)

        # Finally we return the result list
        return results_dict


    def analytics(self, cli_args):
        # Self note: Pass the cli arugments with the "sys.argv[1:]" method

        seconds = 0.5
        count = 10

        # Handling cli arguments
        # The 's' character stands for seconds and 'c' for count
        # The former sets the value above which we show results
        # While the latter sets the total number of results we show
        try:
            opts, args = getopt.getopt(cli_args, "hs:c:", ["seconds=", "count="])
        except getopt.GetoptError:
            print 'Usage: wpsp.py -s <float> -c <integer>'
            sys.exit(2)
        for opt, arg in opts:
            if opt == '-h':
                print 'Usage: wpsp.py -s <float> -c <integer>'
                print '-s | --seconds \tTells the script to search for results above N seconds. Default: 0.5'
                print '-c | --count \tTells the script to print only N number of results. Default: 10'
                sys.exit()
            elif opt in ("-s", "--seconds"):
                seconds = float(arg)
            elif opt in ("-c", "--count"):
                if int(arg) < 5:
                    count = 5
                else:
                    count = int(arg)

        profiler_stage_all = self.profiler_run("stage", "")
        results_stages_all = []

        # Comment needed
        for index, dict in enumerate(profiler_stage_all):
            if dict['value'] >= seconds:
                if "total" in dict['name']:
                    pass
                else:
                    results_stages_all.append(dict)
            else:
                pass

        results_hooks_N = []
        results_callbacks_N = []

        # If the initial results have entries that take more than N seconds to load
        if len(results_stages_all) > 0:

            # Here we iterate over the results from the 'results_stages_all' list.
            # This means that we run the profiler for all of the stages and save the results that took more than N seconds to load.
            # Lastly, we store the results along with the stage name within the 'results_hooks_N' list
            for stage in results_stages_all:
                # Ensuring that the stage takes longer than N seconds to load
                # And that the resulting table's header is not included
                if "stage" not in stage['name']:
                    # Here we start another profiler test with the stage that we want to test
                    profiler_stage = self.profiler_run("stage", stage['name'])
                    for index, dict in enumerate(profiler_stage):
                        if len(dict) > 0:
                            if dict['value'] >= seconds:
                                if "total" not in dict['name']:
                                    # Here we save the name of the stage we tested within the hook results dictionary
                                    dict['parent'] = stage['name']
                                    results_hooks_N.append(dict)

            # Here we iterate over the results from the 'results_hooks_N' list.
            # This means that we run the profiler on all of the hooks that take more than N seconds to load.
            # Lastly we store the results along with the name of the hook within the 'results_callbacks_N' list.
            if len(results_hooks_N) > 0:
                # The 'results_hooks_N' list now consists of list like this [ stage_name, result_hook_dict ]
                for hook in results_hooks_N:
                    if "hook" not in hook['name']:
                        # Here we start another profiler test with the hook that we want to test
                        profiler_hook = self.profiler_run("hook", hook['name'])
                        for dict in profiler_hook:
                            if dict['value'] >= seconds:
                                if "total" not in dict['name']:
                                    # Here we save the name of the hook we tested within the callback results dictionary
                                    dict['parent'] = hook['name']
                                    results_callbacks_N.append(dict)
                if len(results_callbacks_N) <= 1:
                    print "\n> Profiler found no callbacks that take longer than [", seconds, "] seconds to load." \
                          "\n> The script will still display the callbacks that take the longest to load"
            else:
                print("\n\t" + "#" * 30 + "\n\tThe WP Cli Profiler results returned no entries above [" + seconds + "]"
                      + "\n\tor one of the website's plugins cause the Profiler to malfunction"
                      + "\n\t" + "#" * 30)

                sys.exit()
            # End of 'if len(results_hooks_N) > 0' block


            # Here we check if the operator has selected the option to save the results
            # If yes then we generate a wp-cli-profiler-results-DATE.json file
            # Otherwise we skip this part over
            # CODE NEEDED BELLOW!!!!!!!!!!!!!

            # Here we print the results from the tests that we run above
            print("\n\033[1;33;49m---- WP Cli Profiler Results ----\033[1;37;49m")
            # First we print the stages that took longer than N seconds to load
            print"\n> Stages that take longer than [", seconds, "] seconds to load:"
            self.profiler_result_print_multiple(results_stages_all, result_count=count)
            print "-" * 50
            # Then we print the hooks that took longer than N seconds to load

            for stage in results_stages_all:
                if "stage" not in stage['name']:
                    # Comment needed
                    print"\n> Hooks within [\033[1;31;49m", stage['name'], "\033[1;37;49m] stage that take longer than [", seconds, "] seconds to load:"
                    self.profiler_result_print_by_parent(results_hooks_N, stage['name'], result_count=count)

                    for hook in results_hooks_N:
                        if hook['parent'] is stage['name'] and "hook" not in hook['name']:
                            # Comment needed
                            print "> Callbacks within [\033[1;31;49m", hook['name'], "\033[1;37;49m] hook in [\033[1;31;49m", stage['name'], "\033[1;37;49m] stage that take longer than [", seconds, "] seconds to load:"
                            self.profiler_result_print_by_parent(results_callbacks_N, hook['name'], result_count=count)
                    print "-" * 50
        else:
            # If there are no stages that took longer than N seconds to load
            # Then there's no point in running the other tests
            print("\n\t" + "#" * 30 + "\n\tThe WP Cli Profiler results returned no entries above [" + seconds + "]"
                  + "\n\tor one of the website's plugins cause the Profiler to malfunction"
                  + "\n\t" + "#" * 30)
            sys.exit()


if __name__ == '__main__':

    profiler_instance = WP_Profiler()
    print("\n\033[1;31;49m---- Running WP Cli Profiler ----\033[1;37;49m")
    profiler_instance.analytics(sys.argv[1:])

    # Here we handle exceptions


    # Here we remove the downloaded wp-cli.phar file
    # And the wpsp.py script file
