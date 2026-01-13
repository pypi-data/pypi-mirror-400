from optexity.schema.automation import Automation

description = "Peach State Medicaid Insurance Example"
endpoint_name = "peachstate_medicaid_insurance"
automation_json = {
    "url": "https://sso.entrykeyid.com/as/authorization.oauth2?response_type=code&client_id=f6a6219c-be42-421b-b86c-e4fc509e2e87&scope=openid%20profile&state=_igWklSsnrkO5DQfjBMMuN41ksMJePZQ_SM_61wTJlA%3D&redirect_uri=https://provider.pshpgeorgia.com/careconnect/login/oauth2/code/pingcloud&code_challenge_method=S256&nonce=xG41TJjco_x7Vs_MQgcS3bw5njLiJsXCqvO-V8THmY0&code_challenge=ZTaVHaZCNFTejXNJo51RlJ3Kv9dH0tMODPTqO7hiP3A&app_origin=https://provider.pshpgeorgia.com/careconnect/login/oauth2/code/pingcloud&brand=pshpgeorgia",
    "parameters": {
        "input_parameters": {
            "username": [],
            "password": [],
            "plan_type": [],
            "member_id": [],
            "dob": [],
        },
        "generated_parameters": {},
    },
    "nodes": [
        {
            "type": "action_node",
            "interaction_action": {
                "input_text": {
                    "command": 'get_by_test_id("text-field")',
                    "prompt_instructions": "Enter the email in the text field",
                    "input_text": "{username[0]}",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "click_element": {
                    "command": 'get_by_role("button", name="Continue")',
                    "prompt_instructions": "Click the Continue button",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "input_text": {
                    "command": 'get_by_role("textbox", name="Password")',
                    "prompt_instructions": "Enter the password",
                    "input_text": "{password[0]}",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "click_element": {
                    "command": 'get_by_role("button", name="Login")',
                    "prompt_instructions": "Click the Login button",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "select_option": {
                    "command": 'get_by_label("Plan Type")',
                    "prompt_instructions": "Select the Plan Type 8774789",
                    "select_values": ["{plan_type[0]}"],
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "click_element": {
                    "command": 'get_by_role("button", name="GO")',
                    "prompt_instructions": "Click the GO button",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "input_text": {
                    "command": 'get_by_test_id("MemberIDOrLastName")',
                    "prompt_instructions": "Enter the Member ID or Last Name",
                    "input_text": "{member_id[0]}",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "input_text": {
                    "command": 'locator("#tDatePicker")',
                    "prompt_instructions": "Enter the Date of Birth",
                    "input_text": "{dob[0]}",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "click_element": {
                    "command": 'get_by_role("combobox", name="Select Action Type Select")',
                    "prompt_instructions": "Click the Select Action Type Select combobox",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "click_element": {
                    "command": 'get_by_test_id("ActionType-option-0")',
                    "prompt_instructions": "Click the View eligibility & patient info option",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "click_element": {
                    "command": 'get_by_test_id("submitBtn")',
                    "prompt_instructions": "Click the Submit button",
                }
            },
            "end_sleep_time": 1.0,
            "expect_new_tab": True,
            "max_new_tab_wait_time": 10.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "click_element": {
                    "command": 'get_by_label("Eligibility", exact=True).get_by_role("link", name="Authorizations")',
                    "prompt_instructions": "Click the Authorizations link",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "extraction_action": {
                "llm": {
                    "extraction_format": {"authorization_numbers": "List[str]"},
                    "extraction_instructions": "I am giving you an axtree of a webpage that shows the information about authorizations in a tabular format. Status, Auth Nbr, From Date, To Date, Diagnosis, Auth Type, Service. You need to output me a list of all Auth Nbr. Do not output any other information.",
                    "output_variable_names": ["authorization_numbers"],
                }
            },
            "before_sleep_time": 3.0,
            "end_sleep_time": 0.0,
        },
        {
            "type": "for_loop_node",
            "variable_name": "authorization_numbers",
            "nodes": [
                {
                    "type": "action_node",
                    "interaction_action": {
                        "click_element": {
                            "command": 'get_by_role("link", name="{authorization_numbers[index]}")',
                            "prompt_instructions": "Click the Authorizations link for the authorization number {authorization_numbers[index]}",
                        }
                    },
                    "end_sleep_time": 1.0,
                },
                {
                    "type": "action_node",
                    "extraction_action": {
                        "llm": {
                            "extraction_format": {
                                "Auth Nbr": "str",
                                "End Date": "str",
                                "Auth Type": "str",
                                "Start Date": "str",
                                "Auth Status": "str",
                                "Service Type": "str",
                                "Units Approved": "str",
                                "Units Required": "str",
                            },
                            "extraction_instructions": "I am giving you an axtree of a webpage that shows information about authorizations, and I want the 8 following fields. 'Auth Status', 'Auth Nbr', 'Auth Type', 'Service Type', 'Start Date', 'End Date', 'Units Required', 'Units Approved'. Fields 'Auth Status', 'Auth Nbr', 'Auth Type' can be found in the top and rest of the information can be found in the tabular format. You need to output me key-value pairs for all 8 fields.",
                        }
                    },
                    "before_sleep_time": 3.0,
                    "end_sleep_time": 0.0,
                },
                {
                    "type": "action_node",
                    "interaction_action": {"go_back": {}},
                    "end_sleep_time": 1.0,
                },
            ],
        },
    ],
}

automation = Automation.model_validate(automation_json)
