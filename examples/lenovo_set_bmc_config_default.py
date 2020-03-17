###
#
# Lenovo Redfish examples - Set BMC configuration default
#
# Copyright Notice:
#
# Copyright 2018 Lenovo Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
###

import sys
import redfish
import json
import lenovo_utils as utils

def lenovo_set_bmc_config_default(ip, login_account, login_password):
    """set BMC configuration default
        :params ip: BMC IP address
        :type ip: string
        :params login_account: BMC user name
        :type login_account: string
        :params login_password: BMC user password
        :type login_password: string
        :returns: returns set bmc configuration default result when succeeded or error message when failed
        """

    result = {}
    login_host = "https://" + ip

    # Connect using the BMC address, account name, and password
    # Create a REDFISH object
    REDFISH_OBJ = redfish.redfish_client(base_url=login_host, username=login_account,
                                         password=login_password, default_prefix='/redfish/v1')

    # Login into the server and create a session
    try:
        REDFISH_OBJ.login(auth=utils.g_AUTH)
    except:
        result = {'ret': False, 'msg': "Please check if the username, password, IP are correct\n"}
        return result
    # Get ServiceBase resource
    response_base_url = REDFISH_OBJ.get('/redfish/v1', None)
    # Get response_base_url
    if response_base_url.status == 200:
        manager_url = response_base_url.dict['Managers']['@odata.id']
    else:
        error_message = utils.get_extended_error(response_base_url)
        result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
            '/redfish/v1', response_base_url.status, error_message)}
        REDFISH_OBJ.logout()
        return result
    response_manager_url = REDFISH_OBJ.get(manager_url, None)
    bmc_time_detail = []
    if response_manager_url.status == 200:
        for request in response_manager_url.dict['Members']:
            request_url = request['@odata.id']
            response_url = REDFISH_OBJ.get(request_url, None)
            if response_url.status == 200:
                # get bmc configuratino url
                oem_resource = response_url.dict['Oem']['Lenovo']
                config_url = oem_resource['Configuration']['@odata.id']
                response_config_url = REDFISH_OBJ.get(config_url, None)
                if response_config_url.status == 200:
                    #set bmc configuration default
                    reset_default_url = response_config_url.dict['Actions']['#LenovoConfigurationService.ResetToDefault']['target']
                    reset_body = {}
                    response_reset_default_url = REDFISH_OBJ.post(reset_default_url, body=reset_body)
                    if response_reset_default_url.status == 200 or response_reset_default_url.status == 204:
                        result = {'ret': True,
                                  'msg': "Reset bmc configuration default successfully"}
                        REDFISH_OBJ.logout()
                        return result
                    else:
                        error_message = utils.get_extended_error(response_reset_default_url)
                        result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                            reset_default_url, response_reset_default_url.status, error_message)}
                        REDFISH_OBJ.logout()
                        return result
                else:
                    error_message = utils.get_extended_error(response_config_url)
                    result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                        config_url, response_config_url.status, error_message)}
                    REDFISH_OBJ.logout()
                    return result
            else:
                error_message = utils.get_extended_error(response_url)
                result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
                    request_url, response_url.status, error_message)}
                REDFISH_OBJ.logout()
                return result
        return result
    else:
        error_message = utils.get_extended_error(response_manager_url)
        result = {'ret': False, 'msg': "Url '%s' response Error code %s\nerror_message: %s" % (
            manager_url, response_manager_url.status, error_message)}
        REDFISH_OBJ.logout()
        return result

if __name__ == '__main__':
    # Get parameters from config.ini or command line
    argget = utils.create_common_parameter_list()
    args = argget.parse_args()
    parameter_info = utils.parse_parameter(args)

    # Get connection info from the parameters user specified
    ip = parameter_info['ip']
    login_account = parameter_info["user"]
    login_password = parameter_info["passwd"]

    # set bmc configuration default and check result
    result = lenovo_set_bmc_config_default(ip, login_account, login_password)
    if result['ret'] is True:
        del result['ret']
        sys.stdout.write(json.dumps(result['msg'], sort_keys=True, indent=2))
    else:
        sys.stderr.write(result['msg'])