from optexity.schema.automation import Automation

description = "Download PDF URL Example"
endpoint_name = "download_pdf_url"
automation_json = {
    "url": "about:blank",
    "parameters": {
        "input_parameters": {
            "pdf_url": ["https://s24.q4cdn.com/216390268/files/doc_downloads/test.pdf"]
        },
        "generated_parameters": {},
    },
    "nodes": [
        {
            "type": "action_node",
            "interaction_action": {"go_to_url": {"url": "{pdf_url[0]}"}},
            "end_sleep_time": 1.0,
        },
        {
            "type": "action_node",
            "interaction_action": {
                "download_url_as_pdf": {"download_filename": "example.pdf"}
            },
            "end_sleep_time": 1.0,
        },
    ],
}

automation = Automation.model_validate(automation_json)
