from optexity.schema.automation import Automation

description = "File Upload Example"
endpoint_name = "file_upload"
automation_json = {
    "url": "https://www.azurespeed.com/Azure/UploadLargeFile",
    "parameters": {
        "input_parameters": {
            "target_region_option": ["test_region"],
            "file_path": ["/path/to/test/file.txt"],
        },
        "generated_parameters": {},
    },
    "nodes": [
        {
            "type": "action_node",
            "interaction_action": {
                "select_option": {
                    "command": 'get_by_label("Target region")',
                    "prompt_instructions": "Select an option from the field labeled 'Target region' with the value from the 'target_region_option' variable.",
                    "select_values": ["{target_region_option[0]}"],
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "upload_file": {
                    "command": 'get_by_role("button", name="Test file")',
                    "prompt_instructions": "Click on the 'Test file' button.",
                    "file_path": "{file_path[0]}",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "click_element": {
                    "command": 'get_by_role("button", name="Start test")',
                    "prompt_instructions": "Click the 'Start test' button",
                }
            },
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "assertion_action": {
                "llm": {
                    "extraction_instructions": "Check if the file upload was successful"
                }
            },
            "before_sleep_time": 10.0,
            "end_sleep_time": 0.0,
        },
    ],
}
automation = Automation.model_validate(automation_json)
