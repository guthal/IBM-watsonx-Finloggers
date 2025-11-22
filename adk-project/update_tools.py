#!/usr/bin/env python3
"""Script to update all tool functions with expected_credentials"""

with open('tools/financial_analysis_tool.py', 'r') as f:
    content = f.read()

# Replace simple @tool() with proper decorator
new_decorator = '''@tool(
    permission=ToolPermission.READ_ONLY,
    expected_credentials=[ExpectedCredentials(
        app_id="fmp_financial_api",
        type=ConnectionType.API_KEY_AUTH
    )]
)'''

# Replace all @tool() (except the one already updated)
content = content.replace('@tool()\n', f'{new_decorator}\n')

# Remove connection parameter from all function signatures
import re
content = re.sub(r'(def \w+\([^)]+), connection: Dict\[str, Any\] = None\)', r'\1)', content)

# Remove connection argument from make_fmp_request calls
content = re.sub(r'make_fmp_request\(([^,]+), ([^,]+), connection\)', r'make_fmp_request(\1, \2)', content)

with open('tools/financial_analysis_tool.py', 'w') as f:
    f.write(content)

print("Tool file updated successfully!")
