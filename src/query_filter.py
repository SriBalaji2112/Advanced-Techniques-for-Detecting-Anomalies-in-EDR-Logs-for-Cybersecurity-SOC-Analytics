from src.importing import *

# Function to parse the command and extract conditions
def parse_command(command):
    # Split the command into conditions while keeping logical operators separate
    condition_parts = re.split(r"\s+(and|or)\s+", command.strip())
    parsed_conditions = []

    for part in condition_parts:
        # Regular expression to capture the conditions
        pattern = r"^(.*?)\s+(contains|not\s+contains|equals|not\s+equals|in|not\s+in|==|!=|>|<|>=|<=)\s+(.*)$"
        match = re.match(pattern, part.strip())

        if match:
            column_name, operator, value = match.groups()
            parsed_conditions.append((column_name.strip(), operator, value.strip()))  # Strip any extra spaces
        else:
            # Add logical operators (and/or) to the list
            if part.strip() in ["and", "or"]:
                parsed_conditions.append(part.strip())
            else:
                print(f"Warning: Condition '{part}' is not valid.")

    return parsed_conditions


# Function to convert parsed conditions to a query string
def conditions_to_query(conditions):
    query_parts = []

    for cond in conditions:
        # Handle logical operators directly
        if cond in ["and", "or"]:
            query_parts.append(cond)
            continue

        column, operator, value = cond

        # Wrap column names in backticks to handle spaces
        column = f"`{column}`"

        # Handle lists for in/not in
        if operator in ["in", "not in"]:
            # Convert value string to a Python list if it represents one
            if value.startswith("[") and value.endswith("]"):
                value = eval(value)  # Convert string to a list (ensure it's safe)
            query_parts.append(
                f"{'~' if operator == 'not in' else ''}{column}.isin({value})"
            )
        # Handle string and logical operators
        elif operator == "not contains":
            query_parts.append(f"~{column}.str.contains('{value}')")
        elif operator == "contains":
            query_parts.append(f"{column}.str.contains('{value}')")
        elif operator in ["not equals", "!="]:
            query_parts.append(f"{column} != '{value}'")
        elif operator in ["equals", "=="]:
            query_parts.append(f"{column} == '{value}'")
        elif operator == ">":
            query_parts.append(f"{column} > {value}")
        elif operator == "<":
            query_parts.append(f"{column} < {value}")
        elif operator == ">=":
            query_parts.append(f"{column} >= {value}")
        elif operator == "<=":
            query_parts.append(f"{column} <= {value}")

    # Join the query parts with logical operators
    return " ".join(query_parts)

def build(df, command):
    parsed_conditions = parse_command(command)
    query_string = conditions_to_query(parsed_conditions)
    print(f"Parsed Condition: {query_string}")
    try:
        filtered_df = df.query(query_string)
        print("Filtered DataFrame:")
        return filtered_df
    except Exception as e:
        print(f"Error applying condition: {e}")
        return(f"Error applying condition: {e}")
    # print("-" * 40)

