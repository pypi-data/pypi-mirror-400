from optexity.schema.automation import Automation

description = "Supabase Login Example"
endpoint_name = "supabase_login"
automation_json = {
    "url": "https://supabase.com",
    "parameters": {
        "input_parameters": {},
        "secure_parameters": {
            "username": [
                {
                    "onepassword": {
                        "vault_name": "optexity_automation",
                        "item_name": "supabase",
                        "field_name": "username",
                    }
                }
            ],
            "password": [
                {
                    "onepassword": {
                        "vault_name": "optexity_automation",
                        "item_name": "supabase",
                        "field_name": "password",
                    }
                }
            ],
        },
        "generated_parameters": {},
    },
    "nodes": [
        {
            "type": "action_node",
            "interaction_action": {
                "click_element": {
                    "command": 'get_by_role("link", name="Sign in")',
                    "prompt_instructions": "Click the Sign in link",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "input_text": {
                    "command": 'get_by_role("textbox", name="Email")',
                    "prompt_instructions": "Enter the email",
                    "input_text": "{username[0]}",
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
                    "press_enter": True,
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "assertion_action": {
                "llm": {"extraction_instructions": "Check if the login was successful"}
            },
            "end_sleep_time": 0.0,
        },
    ],
}

automation = Automation.model_validate(automation_json)
