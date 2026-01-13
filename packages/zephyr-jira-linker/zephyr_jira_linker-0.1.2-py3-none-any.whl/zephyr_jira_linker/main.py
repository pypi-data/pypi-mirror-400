import base64
import json
import logging
import os
import re
import sys
from logging.handlers import RotatingFileHandler
from typing import Any, Dict

import requests

# Configuration Variables - Replace with your actual values
JIRA_BASE_URL = os.environ.get("JIRA_BASE_URL", "")
JIRA_EMAIL = os.environ.get("JIRA_EMAIL", "")
JIRA_API_TOKEN = os.environ.get("JIRA_API_TOKEN", "")
ZEPHYR_SCALE_TOKEN = os.environ.get("ZEPHYR_SCALE_TOKEN", "")
ZEPHYR_SCALE_BASE_URL = "https://api.zephyrscale.smartbear.com/v2"
LOGS_DIR = "logs"
LOG_FILE = f"{LOGS_DIR}/zephyr_test_status.log"
DEFAULT_COMPONENT_ID = "14404"
MAX_RESULTS = 1000

# Custom Field IDs
CUSTOMFIELD_TESTCASE_LINK = "customfield_13292"
CUSTOMFIELD_CODE_CHANGES = "customfield_13242"
CUSTOMFIELD_IMPLEMENTOR = "customfield_10810"
CUSTOMFIELD_PULL_REQUEST = "customfield_12500"
CUSTOMFIELD_STORY_POINTS = "customfield_10004"
CUSTOMFIELD_SPRINT = "customfield_10007"

# Status Constants
STATUS_PASS = "Pass"
STATUS_FAIL = "Fail"
STATUS_INPROGRESS = "In Progress"
STATUS_NOTEXECUTED = "Not Executed"
STATUS_BLOCKED = "Blocked"

# Global variables
start_time = ""
test_count = 0
pass_count = 0
fail_count = 0
broken_count = 0
testitems = {}
failed_tests = []
broken_tests = []
zephyr_cycle_id = ""
zephyr_execution_keys = {}
previous_failed_id = ""
previous_failed_comment = ""
jira_email = ""
jira_token = ""
jira_base_url = JIRA_BASE_URL
project_key = "PROJECT"
jira_ticket_details = {}

class ZephyrLog:

    def __init__(self):
        self.logger = logging.getLogger("zephyr_logger")
        self.logger.setLevel(logging.INFO)
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        if not os.path.exists(LOGS_DIR):
            os.makedirs(LOGS_DIR)
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        date_format = "%Y-%m-%d %H:%M:%S"
        formatter = logging.Formatter(log_format, date_format)
        max_bytes = 10 * 1024 * 1024
        backup_count = 5
        file_handler = RotatingFileHandler(LOG_FILE, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8")
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def warning(self, message: str) -> None:
        self.logger.warning(message)

    def error(self, message: str) -> None:
        self.logger.error(message)

    def debug(self, message: str) -> None:
        self.logger.debug(message)

zephyrlog = ZephyrLog()

token = ZEPHYR_SCALE_TOKEN
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
base_url = ZEPHYR_SCALE_BASE_URL
max_count = MAX_RESULTS

def setup_jira_auth():
    global jira_email, jira_token

    jira_email = JIRA_EMAIL
    jira_token = JIRA_API_TOKEN

    if jira_email and jira_token:
        jira_credentials = base64.b64encode(f"{jira_email}:{jira_token}".encode()).decode()
        return {"Authorization": f"Basic {jira_credentials}", "Content-Type": "application/json"}
    else:
        return {"Content-Type": "application/json"}

jira_headers = setup_jira_auth()

def extract_text_from_jira_field(field_value) -> str:
    if not field_value:
        return ""

    if isinstance(field_value, str):
        return field_value

    if isinstance(field_value, dict):
        return extract_text_from_adf(field_value)

    return str(field_value)

def extract_text_from_adf(adf_object: dict) -> str:
    text_parts = []

    try:
        node_type = adf_object.get("type", "")

        if node_type == "text":
            text = adf_object.get("text", "")
            text_parts.append(text)

        elif node_type in ["paragraph", "heading", "bulletList", "orderedList", "listItem"]:
            content = adf_object.get("content", [])
            for child in content:
                if isinstance(child, dict):
                    text_parts.append(extract_text_from_adf(child))

        elif "content" in adf_object:
            content = adf_object.get("content", [])
            for item in content:
                if isinstance(item, dict):
                    text_parts.append(extract_text_from_adf(item))

    except Exception as e:
        logging.warning(f"Error extracting text from ADF object: {str(e)}")
        return ""

    return " ".join(text_parts).strip()

def extract_pull_request_state(pr_field_value: str) -> str:
    if not pr_field_value or not isinstance(pr_field_value, str):
        return ""

    try:
        if "state=" in pr_field_value:
            state_start = pr_field_value.find("state=")
            if state_start != -1:
                state_part = pr_field_value[state_start + 6 :]
                state_end = min(
                    state_part.find(",") if state_part.find(",") != -1 else len(state_part),
                    state_part.find("}") if state_part.find("}") != -1 else len(state_part),
                )
                if state_end > 0:
                    return state_part[:state_end].strip()

        if "json=" in pr_field_value:
            json_start = pr_field_value.find("json=")
            if json_start != -1:
                json_part = pr_field_value[json_start + 5 :]
                if json_part.startswith('"') and '"' in json_part[1:]:
                    json_content = json_part[1 : json_part.find('"', 1)]
                elif json_part.startswith("{") and json_part.endswith("}"):
                    json_content = json_part
                else:
                    json_content = ""

                if json_content:
                    try:
                        json_data = json.loads(json_content)
                        state = (
                            json_data.get("cachedValue", {})
                            .get("summary", {})
                            .get("pullrequest", {})
                            .get("overall", {})
                            .get("state", "")
                        )
                        if state:
                            return state
                    except json.JSONDecodeError:
                        pass

        for possible_state in ["MERGED", "OPEN", "CLOSED", "DECLINED", "DRAFT"]:
            if f'"{possible_state}"' in pr_field_value or f"state={possible_state}" in pr_field_value:
                return possible_state

    except Exception as e:
        logging.warning(f"Error extracting pull request state: {str(e)}")

    return ""

def get_ticket_details(issue_key: str) -> Dict[str, Any]:
    email = JIRA_EMAIL
    api_token = JIRA_API_TOKEN
    ticket_details = {
        "issue_key": issue_key,
        "summary": "",
        "implementor": "",
        "reporter": "",
        "reviewer": "",
        "status": "",
        "description": "",
        "code_changes": "",
        "comments": [],
        "story_points": "",
        "sprint": "",
        "assignee": "",
        "time_spent": "",
        "time_spent_seconds": 0,
        "original_estimate": "",
        "remaining_estimate": "",
        "priority": "",
        "labels": [],
        "components": [],
        "pull_request_state": "",
        "testcase_link": "",
    }

    global jira_headers
    if email and api_token:
        jira_credentials = base64.b64encode(f"{email}:{api_token}".encode()).decode()
        jira_headers = {"Authorization": f"Basic {jira_credentials}", "Content-Type": "application/json"}

    try:
        jira_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

        resp = requests.get(jira_url, headers=jira_headers, timeout=30)

        if resp.status_code == 200:
            issue_data = resp.json()

            ticket_details["summary"] = issue_data.get("fields", {}).get("summary", "")

            assignee = issue_data.get("fields", {}).get("assignee")
            if assignee:
                ticket_details["implementor"] = assignee.get("displayName", "")

            status = issue_data.get("fields", {}).get("status")
            if status:
                ticket_details["status"] = status.get("name", "")

            description_field = issue_data.get("fields", {}).get("description", "")
            ticket_details["description"] = extract_text_from_jira_field(description_field)

            assignee = issue_data.get("fields", {}).get("assignee")
            creator = issue_data.get("fields", {}).get("creator")
            reporter = issue_data.get("fields", {}).get("reporter")
            custom_fields = issue_data.get("fields", {})

            if reporter and isinstance(reporter, dict):
                ticket_details["reporter"] = reporter.get("displayName", "")
            elif creator and isinstance(creator, dict):
                ticket_details["reporter"] = creator.get("displayName", "")
            else:
                ticket_details["reporter"] = ""

            implementor_field = custom_fields.get(CUSTOMFIELD_IMPLEMENTOR)
            if implementor_field and isinstance(implementor_field, dict) and implementor_field.get("displayName"):
                ticket_details["implementor"] = implementor_field.get("displayName", "")
            elif creator:
                ticket_details["implementor"] = creator.get("displayName", "")
            else:
                ticket_details["implementor"] = ""

            if assignee and isinstance(assignee, dict) and assignee.get("displayName"):
                ticket_details["assignee"] = assignee.get("displayName", "")
            else:
                ticket_details["assignee"] = ""

            story_points = issue_data.get("fields", {}).get(CUSTOMFIELD_STORY_POINTS)
            story_points = int(story_points) if story_points is not None else ""
            ticket_details["story_points"] = story_points

            timetracking = issue_data.get("fields", {}).get("timetracking", {})
            if timetracking:
                ticket_details["time_spent"] = timetracking.get("timeSpent", "")
                ticket_details["time_spent_seconds"] = timetracking.get("timeSpentSeconds", 0)
                ticket_details["original_estimate"] = timetracking.get("originalEstimate", "")
                ticket_details["remaining_estimate"] = timetracking.get("remainingEstimate", "")
            else:
                ticket_details["time_spent"] = ""
                ticket_details["time_spent_seconds"] = 0
                ticket_details["original_estimate"] = ""
                ticket_details["remaining_estimate"] = ""

            priority = issue_data.get("fields", {}).get("priority")
            if priority and isinstance(priority, dict):
                ticket_details["priority"] = priority.get("name", "")
            else:
                ticket_details["priority"] = ""

            labels = issue_data.get("fields", {}).get("labels", [])
            ticket_details["labels"] = labels if isinstance(labels, list) else []

            components = issue_data.get("fields", {}).get("components", [])
            if isinstance(components, list):
                component_names = [comp.get("name", "") for comp in components if isinstance(comp, dict)]
                ticket_details["components"] = component_names
            else:
                ticket_details["components"] = []

            pr_field = custom_fields.get(CUSTOMFIELD_PULL_REQUEST)
            if pr_field and isinstance(pr_field, str):
                ticket_details["pull_request_state"] = extract_pull_request_state(pr_field)
            else:
                ticket_details["pull_request_state"] = ""

            testcase_link = custom_fields.get(CUSTOMFIELD_TESTCASE_LINK)
            if testcase_link and isinstance(testcase_link, str):
                ticket_details["testcase_link"] = testcase_link
            else:
                ticket_details["testcase_link"] = ""

            sprint_field = issue_data.get("fields", {}).get(CUSTOMFIELD_SPRINT)
            if sprint_field and isinstance(sprint_field, list) and len(sprint_field) > 0:
                active_sprint = next((sprint for sprint in sprint_field if sprint.get("state") == "active"), None)
                if active_sprint:
                    ticket_details["sprint"] = active_sprint.get("name", "")
                else:
                    ticket_details["sprint"] = sprint_field[-1].get("name", "")
            else:
                ticket_details["sprint"] = ""

            reviewer_candidates = [
                "customfield_13244",
                "customfield_10200",
                "customfield_12345",
                "customfield_10811",
                "customfield_13245",
                "customfield_10100",
            ]

            for field_id in reviewer_candidates:
                candidate = custom_fields.get(field_id)
                if candidate and isinstance(candidate, dict) and candidate.get("displayName"):
                    ticket_details["reviewer"] = candidate.get("displayName", "")
                    break

            code_changes_field = custom_fields.get(CUSTOMFIELD_CODE_CHANGES)
            if code_changes_field:
                detailed_changes = extract_text_from_jira_field(code_changes_field)
                if detailed_changes and isinstance(detailed_changes, str):
                    ticket_details["code_changes"] = detailed_changes
            else:
                ticket_details["code_changes"] = ticket_details["description"]

            comments_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}/comment"
            comments_resp = requests.get(comments_url, headers=jira_headers, timeout=30)
            if comments_resp.status_code == 200:
                comments_data = comments_resp.json()
                comments = comments_data.get("comments", [])

                recent_comments = comments[-10:] if len(comments) > 10 else comments
                for comment in recent_comments:
                    comment_body_raw = comment.get("body", "")
                    comment_body = extract_text_from_jira_field(comment_body_raw)
                    ticket_details["comments"].append(comment_body)

        else:
            logging.error(f"Failed to retrieve ticket details for {issue_key}: {resp.status_code} {resp.text}")

    except Exception as e:
        logging.error(f"Error on retrieving ticket details for {issue_key}: {str(e)}")

    return ticket_details

def get_testcases_from_issue(issue_key: str) -> list:
    testcases = []
    try:
        url = f"{base_url}/issuelinks/{issue_key}/testcases"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200 or resp.status_code == 201:
            json_data = resp.json()
            for tc in json_data:
                testcases.append(tc.get("key"))
        else:
            zephyrlog.error(f"Error in getting testcases from issue: {resp.status_code} {resp.content.decode('utf-8')}")
    except Exception as e:
        zephyrlog.error(f"Error in getting testcases from issue: {str(e)}")
    return testcases

def extract_testcase_ids_from_description(description: str) -> list:
    testcase_ids = []
    try:
        if not description or not isinstance(description, str):
            zephyrlog.warning("Description is empty or not a string")
            return testcase_ids

        pattern = r"\b([A-Z]+-T\d+)\b"
        matches = re.findall(pattern, description, re.IGNORECASE)

        if matches:
            testcase_ids = list(dict.fromkeys([match.upper() for match in matches]))
            zephyrlog.info(f"Extracted {len(testcase_ids)} testcase ID(s) from description: {testcase_ids}")
        else:
            zephyrlog.info("No testcase IDs found in description")

    except Exception as e:
        zephyrlog.error(f"Error extracting testcase IDs from description: {str(e)}")

    return testcase_ids

def get_testcase_ids_from_issue(issue_key: str) -> list:
    testcase_ids = []
    try:
        zephyrlog.info(f"Retrieving testcase IDs from issue: {issue_key}")

        ticket_details = get_ticket_details(issue_key)

        if not ticket_details:
            zephyrlog.error(f"Failed to retrieve ticket details for issue {issue_key}")
            return testcase_ids

        description = ticket_details.get("description", "")
        zephyrlog.info(f"Description: {description}")
        if not description:
            zephyrlog.warning(f"No description found for issue {issue_key}")
            return testcase_ids

        testcase_ids = extract_testcase_ids_from_description(description)

        if testcase_ids:
            zephyrlog.info(f"Found {len(testcase_ids)} testcase ID(s) in issue {issue_key}: {testcase_ids}\n")
        else:
            zephyrlog.info(f"No testcase IDs found in issue {issue_key} description")

    except Exception as e:
        zephyrlog.error(f"Error getting testcase IDs from issue: {str(e)}")

    return testcase_ids

def link_testcases_to_issue(issue_key: str, testcase_keys: list) -> bool:
    try:
        if not issue_key or not isinstance(issue_key, str):
            zephyrlog.error("Invalid issue_key: must be a non-empty string")
            return False

        if not re.match(r"^" + project_key + r"-\d+$", issue_key):
            zephyrlog.error(f"Invalid issue key format: {issue_key}. Must be in {project_key}-number format")
            return False

        if not testcase_keys or not isinstance(testcase_keys, list):
            zephyrlog.error("Invalid testcase_keys: must be a non-empty list")
            return False

        if len(testcase_keys) == 0:
            zephyrlog.error("testcase_keys list is empty")
            return False

        zephyrlog.info(f"Linking {len(testcase_keys)} testcase(s) to issue {issue_key}")

        issue_id = None
        try:
            ticket_details = get_ticket_details(issue_key)
            if ticket_details and "id" in ticket_details:
                issue_id = ticket_details.get("id")
            else:
                if JIRA_EMAIL and JIRA_API_TOKEN:
                    jira_credentials = base64.b64encode(f"{JIRA_EMAIL}:{JIRA_API_TOKEN}".encode()).decode()
                    jira_headers_temp = {"Authorization": f"Basic {jira_credentials}", "Content-Type": "application/json"}
                    jira_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

                    jira_resp = requests.get(jira_url, headers=jira_headers_temp, timeout=10)
                    if jira_resp.status_code == 200:
                        issue_data = jira_resp.json()
                        issue_id = issue_data.get("id")
                        zephyrlog.info(f"Retrieved issue ID {issue_id} for issue key {issue_key}")
                    else:
                        zephyrlog.error(f"Failed to get issue ID from Jira: {jira_resp.status_code}")
                else:
                    zephyrlog.error("JIRA_EMAIL and JIRA_API_TOKEN environment variables not set")

            if not issue_id:
                zephyrlog.error(f"Could not retrieve issue ID for issue key {issue_key}")
                return False

        except Exception as e:
            zephyrlog.error(f"Error retrieving issue ID: {str(e)}")
            return False

        success_count = 0
        failed_count = 0

        for testcase_key in testcase_keys:
            try:
                url = f"{base_url}/testcases/{testcase_key}/links/issues"
                request_body = {"issueId": issue_id}

                response = requests.post(url, headers=headers, json=request_body, timeout=5)

                if response.status_code in (200, 201):
                    zephyrlog.info(f"Successfully linked testcase {testcase_key} to issue {issue_key} (ID: {issue_id})")
                    success_count += 1
                else:
                    error_msg = response.content.decode("utf-8") if response.content else "No error details"
                    if (
                        "already" in error_msg.lower()
                        or "duplicate" in error_msg.lower()
                        or response.status_code == 400
                    ):
                        zephyrlog.info(f"Testcase {testcase_key} is already linked to issue {issue_key}")
                        success_count += 1
                    else:
                        zephyrlog.error(
                            f"Failed to link testcase {testcase_key} to issue {issue_key}: {response.status_code} - {error_msg}"
                        )
                        failed_count += 1

            except requests.exceptions.RequestException as e:
                zephyrlog.error(f"Request error linking testcase {testcase_key} to issue {issue_key}: {str(e)}")
                if hasattr(e, "response") and e.response is not None:
                    try:
                        error_details = e.response.text
                        zephyrlog.error(f"Error details: {error_details}")
                    except Exception:
                        pass
                failed_count += 1

        if success_count > 0:
            try:
                all_linked_testcases = get_testcases_from_issue(issue_key)
                if all_linked_testcases:
                    update_jira_testcase_link_field(issue_key, all_linked_testcases)
                else:
                    update_jira_testcase_link_field(issue_key, testcase_keys)
            except Exception as e:
                zephyrlog.warning(f"Failed to update 'Link to Test Case' field in Jira issue: {str(e)}")

        if success_count > 0 and failed_count == 0:
            zephyrlog.info(f"Successfully linked {success_count} testcase(s) to issue {issue_key}")
            return True
        elif success_count > 0:
            zephyrlog.warning(f"Linked {success_count} testcase(s), but {failed_count} failed")
            return False
        else:
            zephyrlog.error(f"Failed to link any testcases to issue {issue_key}")
            return False

    except Exception as e:
        zephyrlog.error(f"Error in link_testcases_to_issue: {str(e)}")
        return False

def verify_customfield_13292(issue_key: str) -> dict:
    result = {
        "success": False,
        "field_value": None,
        "field_url": None,
        "field_title": None,
        "has_default_value": False,
        "message": "",
    }

    try:
        jira_email = JIRA_EMAIL
        jira_token = JIRA_API_TOKEN
        if not jira_email or not jira_token:
            result["message"] = "JIRA_EMAIL and JIRA_API_TOKEN environment variables not set"
            zephyrlog.error(result["message"])
            return result

        jira_credentials = base64.b64encode(f"{jira_email}:{jira_token}".encode()).decode()
        jira_headers_temp = {"Authorization": f"Basic {jira_credentials}", "Content-Type": "application/json"}
        jira_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

        response = requests.get(jira_url, headers=jira_headers_temp, timeout=10)

        if response.status_code != 200:
            result["message"] = f"Failed to retrieve issue: HTTP {response.status_code}"
            zephyrlog.error(result["message"])
            return result

        issue_data = response.json()
        field_value = issue_data.get("fields", {}).get(CUSTOMFIELD_TESTCASE_LINK)

        result["field_value"] = field_value

        if field_value is None:
            result["message"] = "Field is empty (not set)"
            zephyrlog.info(result["message"])
            result["success"] = True
            return result

        if isinstance(field_value, dict):
            result["field_url"] = field_value.get("url", "")
            result["field_title"] = field_value.get("title", "")
        else:
            result["field_url"] = str(field_value)

        if result["field_url"] and "na.com" in result["field_url"].lower():
            result["has_default_value"] = True
            result["message"] = "Field contains default 'http://na.com' value"
        else:
            result["message"] = "Field contains valid testcase link"
            zephyrlog.info(f"VERIFICATION PASSED: {result['message']}")
            if result["field_url"]:
                zephyrlog.info(f"Link URL: {result['field_url']}")

        result["success"] = True
        return result

    except Exception as e:
        result["message"] = f"Error verifying field: {str(e)}"
        zephyrlog.error(result["message"])
        return result

def update_jira_testcase_link_field(issue_key: str, testcase_keys: list) -> bool:
    try:
        if not testcase_keys or len(testcase_keys) == 0:
            zephyrlog.warning("No testcase keys provided to update Jira link field")
            return False

        jira_email = JIRA_EMAIL
        jira_token = JIRA_API_TOKEN
        if not jira_email or not jira_token:
            zephyrlog.error("JIRA_EMAIL and JIRA_API_TOKEN environment variables not set")
            return False

        jira_credentials = base64.b64encode(f"{jira_email}:{jira_token}".encode()).decode()
        jira_headers_temp = {"Authorization": f"Basic {jira_credentials}", "Content-Type": "application/json"}

        testcase_key = testcase_keys[0] if testcase_keys else None
        if not testcase_key:
            zephyrlog.warning("No testcase key provided to update Jira link field")
            return False

        testcase_id = None
        try:
            testcase_info = get_testcase_info(testcase_key)
            if testcase_info and "id" in testcase_info:
                testcase_id = testcase_info.get("id")
                zephyrlog.info(f"Retrieved testcase ID {testcase_id} for testcase key {testcase_key}")
            else:
                zephyrlog.warning(
                    f"Could not retrieve testcase ID for {testcase_key}, will try to construct URL with key"
                )
        except Exception as e:
            zephyrlog.warning(f"Error getting testcase ID: {str(e)}, will try to construct URL with key")

        if testcase_id:
            link_value = f"{JIRA_BASE_URL}/projects/{project_key}?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page#!/v2/testCase/{testcase_id}"
        else:
            zephyrlog.warning("Using testcase key instead of ID for URL construction")
            link_value = f"{JIRA_BASE_URL}/projects/{project_key}?selectedItem=com.atlassian.plugins.atlassian-connect-plugin:com.kanoah.test-manager__main-project-page#!/v2/testCase/{testcase_key}"

        if len(testcase_keys) > 1:
            zephyrlog.info(
                f"Multiple testcases provided, but 'Link to Test Case' field only supports one link. Using first testcase: {testcase_key}"
            )
        elif len(testcase_keys) == 0:
            zephyrlog.error("No testcase keys provided to update Jira link field")
            link_value = "http://na.com"

        jira_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

        needs_clearing = False
        current_field_value = None
        try:
            get_response = requests.get(jira_url, headers=jira_headers_temp, timeout=10)
            if get_response.status_code == 200:
                current_issue_data = get_response.json()
                current_field_value = current_issue_data.get("fields", {}).get(CUSTOMFIELD_TESTCASE_LINK)
                if current_field_value:
                    if isinstance(current_field_value, dict):
                        current_url = current_field_value.get("url", "")
                    else:
                        current_url = str(current_field_value)

                    if current_url == link_value:
                        zephyrlog.info(f"Field already contains the desired link '{link_value}' - skipping update\n")
                        return True

                    if isinstance(current_field_value, str) and "na.com" in current_field_value.lower():
                        zephyrlog.info("Detected default 'http://na.com' value - will clear and update\n")
                        needs_clearing = True
                    elif isinstance(current_field_value, dict):
                        zephyrlog.info("Field appears to be a URL field (object format)\n")
                        if current_field_value.get("url", "").lower() == "http://na.com":
                            needs_clearing = True
        except Exception as e:
            zephyrlog.warning(f"Could not retrieve current field value: {str(e)}")

        if needs_clearing:
            try:
                clear_payload = {"fields": {CUSTOMFIELD_TESTCASE_LINK: None}}
                zephyrlog.info("Clearing default 'http://na.com' value from field...\n")
                clear_response = requests.put(jira_url, headers=jira_headers_temp, json=clear_payload, timeout=10)
                if clear_response.status_code in (200, 204):
                    zephyrlog.info("Successfully cleared default value\n")
                else:
                    zephyrlog.warning(f"Could not clear field (may not be necessary): {clear_response.status_code}")
            except Exception as e:
                zephyrlog.warning(f"Error clearing field: {str(e)}")

        zephyrlog.info(f"Updating 'Link to Test Case' field with URL: {link_value}\n")

        update_payload = {"fields": {CUSTOMFIELD_TESTCASE_LINK: link_value}}

        response = requests.put(jira_url, headers=jira_headers_temp, json=update_payload, timeout=10)

        if response.status_code in (200, 204):
            return True
        else:
            error_msg = response.content.decode("utf-8") if response.content else "No error details"
            zephyrlog.error(
                f"Failed to update 'Link to Test Case' field in issue {issue_key}: {response.status_code} - {error_msg}"
            )
            return False

    except Exception as e:
        zephyrlog.error(f"Error updating Jira testcase link field: {str(e)}")
        return False

def update_jira_code_changes_field(issue_key: str, code_changes: str) -> bool:
    try:
        if not issue_key or not isinstance(issue_key, str):
            zephyrlog.error("Invalid issue_key: must be a non-empty string")
            return False

        if not code_changes or not isinstance(code_changes, str):
            zephyrlog.error("Invalid code_changes: must be a non-empty string")
            return False

        if not re.match(r"^" + project_key + r"-\d+$", issue_key):
            zephyrlog.error(f"Invalid issue key format: {issue_key}. Must be in {project_key}-number format")
            return False

        jira_email = JIRA_EMAIL
        jira_token = JIRA_API_TOKEN
        if not jira_email or not jira_token:
            zephyrlog.error("JIRA_EMAIL and JIRA_API_TOKEN environment variables not set")
            return False

        jira_credentials = base64.b64encode(f"{jira_email}:{jira_token}".encode()).decode()
        jira_headers_temp = {"Authorization": f"Basic {jira_credentials}", "Content-Type": "application/json"}

        jira_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

        current_field_value = None
        try:
            get_response = requests.get(jira_url, headers=jira_headers_temp, timeout=10)
            if get_response.status_code == 200:
                current_issue_data = get_response.json()
                current_field_value = current_issue_data.get("fields", {}).get(CUSTOMFIELD_CODE_CHANGES)

                if current_field_value:
                    current_text = ""
                    if isinstance(current_field_value, dict):
                        try:
                            current_text = extract_text_from_jira_field(current_field_value)
                        except:
                            current_text = str(current_field_value)
                    else:
                        current_text = str(current_field_value)

                    if current_text.strip() == code_changes.strip():
                        zephyrlog.info(f"Field already contains the desired code changes - skipping update\n")
                        return True
        except Exception as e:
            zephyrlog.warning(f"Could not retrieve current field value: {str(e)}")

        zephyrlog.info(f"Updating 'Code Changes' field with: {code_changes}")

        adf_content = {
            "type": "doc",
            "version": 1,
            "content": [
                {
                    "type": "paragraph",
                    "content": [
                        {
                            "type": "text",
                            "text": code_changes
                        }
                    ]
                }
            ]
        }

        update_payload = {"fields": {CUSTOMFIELD_CODE_CHANGES: adf_content}}

        response = requests.put(jira_url, headers=jira_headers_temp, json=update_payload, timeout=10)

        if response.status_code in (200, 204):
            zephyrlog.info(f"Successfully updated 'Code Changes' field for issue {issue_key}\n")
            return True
        else:
            error_msg = response.content.decode("utf-8") if response.content else "No error details"
            zephyrlog.error(
                f"Failed to update 'Code Changes' field in issue {issue_key}: {response.status_code} - {error_msg}"
            )
            return False

    except Exception as e:
        zephyrlog.error(f"Error updating Jira code changes field: {str(e)}")
        return False

def update_jira_testcase_link_field_na(issue_key: str) -> bool:
    try:
        jira_email = JIRA_EMAIL
        jira_token = JIRA_API_TOKEN
        if not jira_email or not jira_token:
            zephyrlog.error("JIRA_EMAIL and JIRA_API_TOKEN environment variables not set")
            return False

        jira_credentials = base64.b64encode(f"{jira_email}:{jira_token}".encode()).decode()
        jira_headers_temp = {"Authorization": f"Basic {jira_credentials}", "Content-Type": "application/json"}

        link_value = "http://na.com"

        jira_url = f"{JIRA_BASE_URL}/rest/api/3/issue/{issue_key}"

        get_response = requests.get(jira_url, headers=jira_headers_temp, timeout=10)
        if get_response.status_code == 200:
            current_issue_data = get_response.json()
            current_field_value = current_issue_data.get("fields", {}).get(CUSTOMFIELD_TESTCASE_LINK)

            if current_field_value:
                if isinstance(current_field_value, dict):
                    current_url = current_field_value.get("url", "")
                else:
                    current_url = str(current_field_value)

                if "na.com" in current_url.lower():
                    zephyrlog.info("Field already contains 'http://na.com' - skipping update\n")
                    return True
        else:
            zephyrlog.warning(f"Could not retrieve current field value: HTTP {get_response.status_code}")

        zephyrlog.info(f"Updating 'Link to Test Case' field with URL: {link_value}\n")
        update_payload = {"fields": {CUSTOMFIELD_TESTCASE_LINK: link_value}}
        response = requests.put(jira_url, headers=jira_headers_temp, json=update_payload, timeout=10)

        if response.status_code in (200, 204):
            return True
        else:
            error_msg = response.content.decode("utf-8") if response.content else "No error details"
            zephyrlog.error(
                f"Failed to update 'Link to Test Case' field in issue {issue_key}: {response.status_code} - {error_msg}"
            )
            return False

    except Exception as e:
        zephyrlog.error(f"Error updating Jira testcase link field with 'http://na.com' link: {str(e)}")
        return False

def get_testcase_info(testcase_id: str) -> Dict[str, Any]:
    testcase_info = {}
    try:
        testcase_response = {}
        url = f"{base_url}/testcases/{testcase_id}"
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200 or response.status_code == 201:
            response_data = response.content.decode("utf-8")
            testcase_response = json.loads(response_data)
        else:
            zephyrlog.error(f"Error: {response.status_code} {response.content.decode('utf-8')}")
            return None

        if not testcase_response or not isinstance(testcase_response, dict):
            zephyrlog.error(f"Invalid response structure for testcase {testcase_id}")
            return None

        test_status_url = testcase_response.get("status", {}).get("self", "")
        if test_status_url:
            test_status = get_testcase_status(test_status_url)
        else:
            test_status = ""
            zephyrlog.warning(f"No status URL found for testcase {testcase_id}")

        custom_fields = testcase_response.get("customFields", {})
        testcase_info = {}
        testcase_info["testcase_id"] = testcase_id
        testcase_info["name"] = testcase_response.get("name", "")
        testcase_info["test_method"] = custom_fields.get("Test Method", "Manual")
        testcase_info["testcase_status"] = test_status
        testcase_info["id"] = testcase_response.get("id", "")
        testcase_info["key"] = testcase_response.get("key", "")

        testcase_info["project"] = testcase_response.get("project", {}).get("id", "")
        testcase_info["priority"] = testcase_response.get("priority", {}).get("id", "")
        testcase_info["status"] = testcase_response.get("status", {}).get("id", "")

        if testcase_response.get("component") is None:
            zephyrlog.warning(
                f"No component found for testcase {testcase_id}. Setting Velocity Web App as default component."
            )
            testcase_info["component"] = DEFAULT_COMPONENT_ID
        else:
            testcase_info["component"] = testcase_response.get("component", {}).get("id", "")

        testcase_info["folder"] = testcase_response.get("folder", {}).get("id", "")
        if testcase_response["owner"] == None:
            testcase_info["owner"] = None
            zephyrlog.warning(f"No owner found for testcase {testcase_id}")
        else:
            testcase_info["owner"] = testcase_response.get("owner", {}).get("accountId", "")

        testcase_info["test_script"] = testcase_response.get("testScript", {}).get("self", "")

        testcase_info["objective"] = testcase_response.get("objective", "")
        testcase_info["precondition"] = testcase_response.get("precondition", "")
        testcase_info["estimatedTime"] = testcase_response.get("estimatedTime", "")
        if testcase_response.get("labels") is None:
            zephyrlog.warning(f"No labels found for testcase {testcase_id}")
            testcase_info["labels"] = []
        else:
            testcase_info["labels"] = testcase_response.get("labels", [])

        testcase_info["test_type"] = custom_fields.get("Test Type", [])
        testcase_info["test_data"] = custom_fields.get("Test Data", "")
        testcase_info["tc_component"] = custom_fields.get("TC Component", [])
        testcase_info["execution_priority"] = custom_fields.get("Execution priority", "Low")
        testcase_info["service"] = custom_fields.get("Service", [])
        testcase_info["cannot_be_automated"] = custom_fields.get("Cannot be Automated", "")
        testcase_info["can_be_automated"] = custom_fields.get("Can-be Automated", "")
    except Exception as e:
        zephyrlog.error(f"Error on getting testcase info for {testcase_id}: {e}")
        return None
    return testcase_info

def get_testcase_status(url: str) -> str:
    test_status = ""
    try:
        response = requests.get(url, headers=headers, timeout=5)
        response_data = response.content.decode("utf-8")
        test_status_data = json.loads(response_data)
        test_status = test_status_data["name"]
    except Exception as e:
        zephyrlog.error(f"Error in getting testcase status: {str(e)}")
    return test_status



def extract_issue_key_from_branch(branch_name: str, project_key: str = "PROJECT") -> str:

    if not branch_name or not isinstance(branch_name, str):
        return ""

    pattern = rf"{project_key}-\d+"
    match = re.search(pattern, branch_name, re.IGNORECASE)

    if match:
        issue_key = match.group(0).upper()
        zephyrlog.info(f"Extracted issue key '{issue_key}' from branch name '{branch_name}'\n")
        return issue_key
    else:
        zephyrlog.warning(f"No issue key found in branch name '{branch_name}'\n")
        return ""


def process_branch_testcase_linking(branch_name: str, project_key_param: str = "PROJECT") -> bool:
    global project_key  # Declare global to modify the global variable
    project_key = project_key_param  # Set the global variable to the parameter value

    try:
        zephyrlog.info("=" * 60)
        zephyrlog.info(f"Processing branch: {branch_name}")
        zephyrlog.info("=" * 60)

        if branch_name.startswith("dependabot"):
            zephyrlog.info("Dependabot branch detected, skipping")
            return True

        zephyrlog.info("Step 1: Extracting issue key from branch name...")
        issue_key = extract_issue_key_from_branch(branch_name, project_key)

        if not issue_key:
            zephyrlog.error(f"Could not extract issue key from branch name: {branch_name}")
            zephyrlog.info(f"Branch name should contain an issue key in format: {project_key}-number")
            return False

        if not re.match(r"^" + project_key + r"-\d+$", issue_key):
            zephyrlog.error(f"Invalid issue key format: {issue_key}")
            zephyrlog.info(f"Issue key must be in {project_key}-number format")
            return False

        zephyrlog.info("Step 2: Verifying issue exists...")
        jira_ticket_details_local = get_ticket_details(issue_key)
        jira_ticket_details = jira_ticket_details_local
        if not jira_ticket_details_local:
            zephyrlog.error(f"Failed to retrieve issue {issue_key}")
            return False

        zephyrlog.info(f"Issue verified: {issue_key}\n")

        zephyrlog.info("Step 3: Extracting testcase IDs from issue description and links...")
        testcase_ids_from_description = get_testcase_ids_from_issue(issue_key)
        existing_linked_testcases = get_testcases_from_issue(issue_key)
        if not testcase_ids_from_description:
            zephyrlog.warning("No testcases found in description and no existing linked testcases")
            update_jira_testcase_link_field_na(issue_key)
            update_jira_code_changes_field(issue_key, jira_ticket_details_local["code_changes"])
        else:
            update_jira_testcase_link_field(issue_key, testcase_ids_from_description)
            update_jira_code_changes_field(issue_key, "Implemented new testscripts for the issue")

        if testcase_ids_from_description:
            zephyrlog.info("Step 4: Checking currently linked testcases...")
            common_testcases = [tc for tc in existing_linked_testcases if tc in testcase_ids_from_description]
            if common_testcases:
                zephyrlog.info(
                    f"Found {len(common_testcases)} already linked testcase(s): {common_testcases}"
                )
            else:
                zephyrlog.info("No common testcases found between existing linked testcases and testcase IDs from description\n")

            testcases_to_link = [
                tc_id for tc_id in testcase_ids_from_description if tc_id not in existing_linked_testcases
            ]

            if testcases_to_link:
                zephyrlog.info(f"Step 5: Linking {len(testcases_to_link)} new testcase(s) to issue...")
                zephyrlog.info(f"Testcases to link: {testcases_to_link}")

                success = link_testcases_to_issue(issue_key, testcases_to_link)

                if not success:
                    zephyrlog.error(f"Failed to link some testcases to issue {issue_key}")
            else:
                zephyrlog.info("All testcases from description are already linked to the issue")

        zephyrlog.info("Step 6: Verifying 'Link to Test Case' field...")
        verification_result = verify_customfield_13292(issue_key)

        if verification_result["success"]:
            if verification_result["has_default_value"]:
                if testcase_ids_from_description:
                    zephyrlog.error("VERIFICATION FAILED: Field still contains default 'http://na.com' value!")
                else:
                    zephyrlog.info("VERIFICATION PASSED: Field contains default 'http://na.com' value")
            elif verification_result["field_value"]:
                zephyrlog.info("VERIFICATION PASSED: Field contains valid testcase link\n")
            else:
                zephyrlog.info("Field is empty (not set)\n")
        else:
            zephyrlog.warning(f"Could not verify field: {verification_result['message']}\n")

        zephyrlog.info("Step 7: Reviewing all linked testcases...")
        all_linked_testcases = get_testcases_from_issue(issue_key)

        if all_linked_testcases:
            zephyrlog.info(f"Found {len(all_linked_testcases)} linked testcase(s) to review")

            for test_id in all_linked_testcases:
                zephyrlog.info(f"Processing test case: {test_id}")
                testcase_info = get_testcase_info(test_id)
                if testcase_info:
                    pass
                else:
                    zephyrlog.error(f"Failed to get information for test case: {test_id}")
        else:
            zephyrlog.warning(f"No test cases found linked to issue {issue_key}")
        print("\n")

        zephyrlog.info("Step 8: Checking linked testcases status...")
        linked_testcases = get_testcases_from_issue(issue_key)
        if linked_testcases:
            zephyrlog.info(f"Successfully linked {len(linked_testcases)} testcase(s) to issue {issue_key}")
            zephyrlog.info(f"Linked testcases: {', '.join(linked_testcases)}")
        else:
            zephyrlog.info(f"No testcases linked to issue {issue_key}")

        zephyrlog.info("=" * 60)
        zephyrlog.info("Branch testcase linking process completed successfully")
        zephyrlog.info("=" * 60)

        return True

    except Exception as e:
        zephyrlog.error(f"Error processing branch {branch_name}: {str(e)}")
        import traceback

        zephyrlog.error(traceback.format_exc())
        return False

def main():
    """Main entry point for the zephyr-jira-linker command-line tool."""
    global project_key  # Declare global to modify the global variable

    if len(sys.argv) < 2:
        zephyrlog.error("Please provide the branch name or issue key as an argument")
        zephyrlog.info("Usage: zephyr-jira-linker <branch_name_or_issue_key>")
        zephyrlog.info("")
        zephyrlog.info("This script will:")
        zephyrlog.info("- Extract issue key from branch name or use issue key directly")
        zephyrlog.info("- Extract testcase IDs from issue description")
        zephyrlog.info("- Link testcases to the issue")
        zephyrlog.info("- Update the 'Link to Test Case' field")
        zephyrlog.info("- Update the 'Code Changes' field")
        zephyrlog.info("- Review all linked testcases")
        sys.exit(1)

    input_arg = sys.argv[1].strip()

    # Check if input is already an issue key (format: PROJECT-123)
    issue_key_pattern = r'^[A-Z]+-\d+$'
    if re.match(issue_key_pattern, input_arg):
        # Direct issue key provided
        issue_key = input_arg.upper()
        project_key = issue_key.split("-")[0]  # Set the global variable
        zephyrlog.info(f"Direct issue key provided: {issue_key}")

        # Create a mock branch name for processing
        branch_name = f"feature/{issue_key.lower()}"
        success = process_branch_testcase_linking(branch_name, project_key_param=project_key)
    else:
        # Assume it's a branch name
        branch_name = input_arg
        project_key = input_arg.split("-")[0].strip()
        success = process_branch_testcase_linking(branch_name, project_key_param=project_key)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
