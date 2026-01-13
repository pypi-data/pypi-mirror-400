# Backtick - Programming Language
# By splot.dev

import re
import math
import random
import requests
import time
import sqlite3
from platformdirs import user_data_dir
from pathlib import Path

class Backtick:
    def __init__(self):
        Backtick.sql_query_db("""
        CREATE TABLE IF NOT EXISTS storage (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            value TEXT
        );
        """)
    @staticmethod
    def sql_query_db(query, insert=None):
        data_dir = Path(user_data_dir("backtick_programming_language", "splot.dev"))
        data_dir.mkdir(parents=True, exist_ok=True)
        db_path = data_dir / "backtick_programming_language_storage.sqlite"

        if not isinstance(query, str):
            raise TypeError("Query must be string.")
        
        with sqlite3.connect(db_path) as conn:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode=WAL;")
            conn.execute("PRAGMA synchronous=FULL;")
            cursor = conn.cursor()
            if insert is not None:
                cursor.execute(query, insert)
            else:
                cursor.execute(query)

            if query.strip().lower().startswith("select"):
                return cursor.fetchall()
            else:
                conn.commit()
                return True
    def tokenize(self, code):
        
        # This will turn the code into a Python object for easier running.
        
        if not isinstance(code, str):
            return ("Code input must be string.",None, False)

        code_no_comments = re.sub("#.*$", "", code,flags=re.MULTILINE)
        code_newline_replaced = code_no_comments.replace("\n", ";;")
        code_split = code_newline_replaced.split(";;")

        tokens = []
        line = 0
        uses_special_commands = False
        
        for command in code_split:
            if command:
                command_name = ""
                command_args = []
                count = 0
                escaped = False
                for char in command:
                    if escaped:
                        if not command_args == []:
                            command_args[-1]["value"] = command_args[-1]["value"] + char
                        else:
                            command_name = command_name + char
                        escaped = False
                    else:
                        if char == "|":
                            escaped = True
                        else:
                            if count == 0 and (char in ["\\", "<", ">"]):
                                return (f"Command {line+1}, character {count+1}: first character must be command.", None, False)
                            elif char in ["\\", "<", ">"]:
                                command_args.append({"type": char, "value":""})
                            elif not command_args == []:
                                command_args[-1]["value"] = command_args[-1]["value"] + char
                            else:
                                command_name = command_name + char
                            
                    count += 1
                if command_name.startswith("_"):
                    uses_special_commands = True

                tokens.append({"name": command_name, "arguments": command_args})
            else:
                tokens.append({}) 
            line += 1
        return (tokens, uses_special_commands, True)
    def run(self, tokens):

        # This will run this tokens.
        
        if not isinstance(tokens, list):
            return ("Tokens must be list.", False)
        
        try:
            jumpareas = {}

            line = 0
            for token in tokens:
                if token == {}:
                    line+=1
                    continue
                
                if token["name"] == "~":
                    if not len(token["arguments"]) == 1:
                        return (f"Command {line+1}: invalid argument amount, must have 1.", False)
                    if not token["arguments"][0]["type"] == ">":
                        return (f"Command {line+1}: must be string.", False)                    
                        
                    jumpareas[token["arguments"][0]["value"]]=line
                line += 1

            variables = {"`j": 0.0, "`l": 1.0, "n":0.0, "s": ""}
            
            line = 0
            token = tokens[line]
            loop = False
            loopline = None
            loopend = None
            while True:
                if line >= len(tokens):
                    break
                token = tokens[line]

                if token == {}:
                    line += 1
                    continue
                if token["name"] == "~":
                    line += 1
                    continue
                elif token["name"] == "+":
                    value_one = None
                    value_two = None
                    if not len(token["arguments"]) == 3:
                        return (f"Command {line+1}: invalid argument amount, must have 3.", False)
                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument 1 must be variable.", False)
                    if (token["arguments"][1]["type"] == ">" and token["arguments"][2]["type"] == "<") or (token["arguments"][1]["type"] == "<" and token["arguments"][2]["type"] == ">"):
                        return (f"Command {line+1}: argument 2 and 3 must be strings and strings, integers and variables, numbers and numbers or variables and variables.", False)                    
                    if not token["arguments"][0]["value"] in variables:
                        return (f"Command {line+1}: argument 1 does not exist as a variable.", False)
                    if token["arguments"][1]["type"] == "\\":
                        if not token["arguments"][1]["value"] in variables:
                            return (f"Command {line+1}: argument 2 does not exist as a variable.", False)
                        else:
                            value_one = variables[token["arguments"][1]["value"]]
                    else:
                        value_one = token["arguments"][1]["value"]
                    if token["arguments"][2]["type"] == "\\":
                        if not token["arguments"][2]["value"] in variables:
                            return (f"Command {line+1}: argument 3 does not exist as a variable.", False)
                        else:
                            value_two = variables[token["arguments"][2]["value"]]
                    else:
                        value_two = token["arguments"][2]["value"]
                        
                    if token["arguments"][1]["type"] == "<":
                        value_one = float(value_one)
                    if token["arguments"][2]["type"] == "<":
                        value_two = float(value_two)

                    if not ((isinstance(value_one, float) and isinstance(value_two, float)) or (isinstance(value_one, str) and isinstance(value_two, str))):
                        return (f"Command {line+1}: Invalid type matching.", False)
                    
                    variables[token["arguments"][0]["value"]] = value_one + value_two
                elif token["name"] == "-":
                    value_one = None
                    value_two = None
                    if not len(token["arguments"]) == 3:
                        return (f"Command {line+1}: invalid argument amount, must have 3.", False)
                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument 1 must be variable.", False)
                    if (token["arguments"][1]["type"] == ">" and token["arguments"][2]["type"] == ">") or (token["arguments"][1]["type"] == ">" and token["arguments"][2]["type"] == "<") or (token["arguments"][1]["type"] == "<" and token["arguments"][2]["type"] == ">"):
                        return (f"Command {line+1}: argument 2 and 3 must be, integers and variables, numbers and numbers or variables and variables.", False)                    
                    if not token["arguments"][0]["value"] in variables:
                        return (f"Command {line+1}: argument 1 does not exist as a variable.", False)
                    if token["arguments"][1]["type"] == "\\":
                        if not token["arguments"][1]["value"] in variables:
                            return (f"Command {line+1}: argument 2 does not exist as a variable.", False)
                        else:
                            value_one = variables[token["arguments"][1]["value"]]
                    else:
                        value_one = token["arguments"][1]["value"]
                    if token["arguments"][2]["type"] == "\\":
                        if not token["arguments"][2]["value"] in variables:
                            return (f"Command {line+1}: argument 3 does not exist as a variable.", False)
                        else:
                            value_two = variables[token["arguments"][2]["value"]]
                    else:
                        value_two = token["arguments"][2]["value"]
                        
                    if token["arguments"][1]["type"] == "<":
                        value_one = float(value_one)
                    if token["arguments"][2]["type"] == "<":
                        value_two = float(value_two)

                    if not ((isinstance(value_one, float) and isinstance(value_two, float))):
                        return (f"Command {line+1}: Invalid type matching.", False)
                    
                    variables[token["arguments"][0]["value"]] = value_one - value_two
                elif token["name"] == "*":
                    value_one = None
                    value_two = None
                    if not len(token["arguments"]) == 3:
                        return (f"Command {line+1}: invalid argument amount, must have 3.", False)
                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument 1 must be variable.", False)
                    if (token["arguments"][1]["type"] == ">" and token["arguments"][2]["type"] == ">") or (token["arguments"][1]["type"] == ">" and token["arguments"][2]["type"] == "<") or (token["arguments"][1]["type"] == "<" and token["arguments"][2]["type"] == ">"):
                        return (f"Command {line+1}: argument 2 and 3 must be, integers and variables, numbers and numbers or variables and variables.", False)                    
                    if not token["arguments"][0]["value"] in variables:
                        return (f"Command {line+1}: argument 1 does not exist as a variable.", False)
                    if token["arguments"][1]["type"] == "\\":
                        if not token["arguments"][1]["value"] in variables:
                            return (f"Command {line+1}: argument 2 does not exist as a variable.", False)
                        else:
                            value_one = variables[token["arguments"][1]["value"]]
                    else:
                        value_one = token["arguments"][1]["value"]
                    if token["arguments"][2]["type"] == "\\":
                        if not token["arguments"][2]["value"] in variables:
                            return (f"Command {line+1}: argument 3 does not exist as a variable.", False)
                        else:
                            value_two = variables[token["arguments"][2]["value"]]
                    else:
                        value_two = token["arguments"][2]["value"]
                        
                    if token["arguments"][1]["type"] == "<":
                        value_one = float(value_one)
                    if token["arguments"][2]["type"] == "<":
                        value_two = float(value_two)

                    if not ((isinstance(value_one, float) and isinstance(value_two, float))):
                        return (f"Command {line+1}: Invalid type matching.", False)
                    
                    variables[token["arguments"][0]["value"]] = value_one * value_two
                    
                elif token["name"] == "/":
                    value_one = None
                    value_two = None
                    if not len(token["arguments"]) == 3:
                        return (f"Command {line+1}: invalid argument amount, must have 3.", False)
                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument 1 must be variable.", False)
                    if (token["arguments"][1]["type"] == ">" and token["arguments"][2]["type"] == ">") or (token["arguments"][1]["type"] == ">" and token["arguments"][2]["type"] == "<") or (token["arguments"][1]["type"] == "<" and token["arguments"][2]["type"] == ">"):
                        return (f"Command {line+1}: argument 2 and 3 must be, integers and variables, numbers and numbers or variables and variables.", False)                    
                    if not token["arguments"][0]["value"] in variables:
                        return (f"Command {line+1}: argument 1 does not exist as a variable.", False)
                    if token["arguments"][1]["type"] == "\\":
                        if not token["arguments"][1]["value"] in variables:
                            return (f"Command {line+1}: argument 2 does not exist as a variable.", False)
                        else:
                            value_one = variables[token["arguments"][1]["value"]]
                    else:
                        value_one = token["arguments"][1]["value"]
                    if token["arguments"][2]["type"] == "\\":
                        if not token["arguments"][2]["value"] in variables:
                            return (f"Command {line+1}: argument 3 does not exist as a variable.", False)
                        else:
                            value_two = variables[token["arguments"][2]["value"]]
                    else:
                        value_two = token["arguments"][2]["value"]
                        
                    if token["arguments"][1]["type"] == "<":
                        value_one = float(value_one)
                    if token["arguments"][2]["type"] == "<":
                        value_two = float(value_two)

                    if not ((isinstance(value_one, float) and isinstance(value_two, float))):
                        return (f"Command {line+1}: invalid type matching.", False)

                    if value_two == 0.0:
                        return (f"Command {line+1}: cannot perform division by 0.", False)
                    
                    variables[token["arguments"][0]["value"]] = value_one / value_two
                elif token["name"] == "[":
                    if loop:
                        return (f"Command {line+1}: already in loop, cannot nest loops.", False)
                    if not len(token["arguments"]) == 0:
                        return (f"Command {line+1}: no arguments needed for loops.", False)
                    
                    if len(tokens) <= (line+1):
                        return (f"Command {line+1}: cannot have a loop starter at the last line.", False)
                    
                    loop = True
                    loopline = line + 1
                elif token["name"] == "]":
                    if not loop:
                        return (f"Command {line+1}: you are not in a loop, so you cannot end it.", False)
                    if not len(token["arguments"]) == 0:
                        return (f"Command {line+1}: no arguments needed for loops.", False)
                    loopend = line
                    if float(variables["`l"]) == 0.0:
                        loop = False
                        loopline = None
                        line = loopend
                        loopend = None
                    else:
                        line = loopline-1
                elif token["name"] == ":":
                    if loop:
                        return (f"Command {line+1}: you cannot jump while in a loop.", False)
                    if not len(token["arguments"]) == 1:
                        return (f"Command {line+1}: you must have one argument.", False)
                    if not token["arguments"][0]["type"] == ">":
                        return (f"Command {line+1}: argument 1 must be a string", False)

                    if not (token["arguments"][0]["value"] in jumpareas):
                        return (f"Command {line+1}: missing jump area", False)
                    
                    if float(variables["`j"]) == 0.0:
                        line = int(jumpareas[token["arguments"][0]["value"]]) - 1
                    else:
                        pass
                elif token["name"] == "=":
                    if not len(token["arguments"]) == 2:
                        return (f"Command {line+1}: you must have two arguments.", False)
                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument 1 must be a variable", False)

                    value = None
                    if token["arguments"][1]["type"] == "\\":
                        value = variables[token["arguments"][1]["value"]]
                    elif token["arguments"][1]["type"] == "<":
                        value = float(token["arguments"][1]["value"])
                    elif token["arguments"][1]["type"] == ">":
                        value = token["arguments"][1]["value"]

                    variables[token["arguments"][0]["value"]] = value
                elif token["name"] == "%":
                    if not len(token["arguments"]) == 4:
                        return (f"Command {line+1}: you must have 4 arguments.", False)
                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument 1 must be a variable", False)
                    
                    value = None
                    if token["arguments"][1]["type"] == "\\":
                        value = variables[token["arguments"][1]["value"]]
                    elif token["arguments"][1]["type"] == "<":
                        value = float(token["arguments"][1]["value"])
                    elif token["arguments"][1]["type"] == ">":
                        value = token["arguments"][1]["value"]

                    
                    oneif = token["arguments"][2]["value"]
                    if token["arguments"][2]["type"] == "\\":
                        oneif = variables[token["arguments"][2]["value"]]
                    elif token["arguments"][2]["type"] == "<":
                        oneif = float(token["arguments"][2]["value"])
                    elif token["arguments"][2]["type"] == ">":
                        oneif = token["arguments"][2]["value"]
                        
                    twoif = token["arguments"][3]["value"]
                    if token["arguments"][3]["type"] == "\\":
                        twoif = variables[token["arguments"][3]["value"]]
                    elif token["arguments"][3]["type"] == "<":
                        twoif = float(token["arguments"][3]["value"])
                    elif token["arguments"][3]["type"] == ">":
                        twoif = token["arguments"][3]["value"]

                    if oneif == twoif:
                        variables[token["arguments"][0]["value"]] = value
                elif token["name"] == ",":
                    if not len(token["arguments"]) == 4:
                        return (f"Command {line+1}: you must have 4 arguments.", False)
                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument 1 must be a variable", False)
                    
                    value = None
                    if token["arguments"][1]["type"] == "\\":
                        value = variables[token["arguments"][1]["value"]]
                    elif token["arguments"][1]["type"] == "<":
                        value = float(token["arguments"][1]["value"])
                    elif token["arguments"][1]["type"] == ">":
                        value = token["arguments"][1]["value"]

                    
                    oneif = token["arguments"][2]["value"]
                    if token["arguments"][2]["type"] == "\\":
                        oneif = variables[token["arguments"][2]["value"]]
                    elif token["arguments"][2]["type"] == "<":
                        oneif = float(token["arguments"][2]["value"])
                    elif token["arguments"][2]["type"] == ">":
                        oneif = token["arguments"][2]["value"]
                        
                    twoif = token["arguments"][3]["value"]
                    if token["arguments"][3]["type"] == "\\":
                        twoif = variables[token["arguments"][3]["value"]]
                    elif token["arguments"][3]["type"] == "<":
                        twoif = float(token["arguments"][3]["value"])
                    elif token["arguments"][3]["type"] == ">":
                        twoif = token["arguments"][3]["value"]

                    if oneif > twoif:
                        variables[token["arguments"][0]["value"]] = value
                elif token["name"] == ".":
                    if not len(token["arguments"]) == 4:
                        return (f"Command {line+1}: you must have 4 arguments.", False)
                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument 1 must be a variable", False)
                    
                    value = None
                    if token["arguments"][1]["type"] == "\\":
                        value = variables[token["arguments"][1]["value"]]
                    elif token["arguments"][1]["type"] == "<":
                        value = float(token["arguments"][1]["value"])
                    elif token["arguments"][1]["type"] == ">":
                        value = token["arguments"][1]["value"]

                    
                    oneif = token["arguments"][2]["value"]
                    if token["arguments"][2]["type"] == "\\":
                        oneif = variables[token["arguments"][2]["value"]]
                    elif token["arguments"][2]["type"] == "<":
                        oneif = float(token["arguments"][2]["value"])
                    elif token["arguments"][2]["type"] == ">":
                        oneif = token["arguments"][2]["value"]
                        
                    twoif = token["arguments"][3]["value"]
                    if token["arguments"][3]["type"] == "\\":
                        twoif = variables[token["arguments"][3]["value"]]
                    elif token["arguments"][3]["type"] == "<":
                        twoif = float(token["arguments"][3]["value"])
                    elif token["arguments"][3]["type"] == ">":
                        twoif = token["arguments"][3]["value"]

                    if oneif < twoif:
                        variables[token["arguments"][0]["value"]] = value
                elif token["name"] == "!":
                    if not len(token["arguments"]) == 1:
                        return (f"Command {line+1}: must have one argument.", False)
                    one = token["arguments"][0]["value"]
                    if token["arguments"][0]["type"] == "\\":
                        one = variables[token["arguments"][0]["value"]]
                    elif token["arguments"][0]["type"] == "<":
                        one = token["arguments"][0]["value"]
                    elif token["arguments"][0]["type"] == ">":
                        one = token["arguments"][0]["value"]

                    print(one)
                elif token["name"] == "?":
                    if not len(token["arguments"]) == 1:
                        return (f"Command {line+1}: must have one argument.", False)
                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: first argument must be variable.", False)
                    userinput = input(">> ")

                    variables[token["arguments"][0]["value"]] = userinput
                elif token["name"] == "^":
                    if not len(token["arguments"]) == 3:
                        return (f"Command {line+1}: must have three arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument one must be a variable", False)
                    
                    if not token["arguments"][1]["type"] == "\\":
                        return (f"Command {line+1}: argument two must be a variable", False)

                    three = token["arguments"][2]["value"]
                    if token["arguments"][2]["type"] == "\\":
                        three = variables[token["arguments"][2]["value"]]
                    elif token["arguments"][2]["type"] == "<":
                        three = float(token["arguments"][2]["value"])
                    elif token["arguments"][2]["type"] == ">":
                        return (f"Command {line+1}: argument three cannot be a string", False)
                    
                    if 0 > int(three) or (int(three) >= len(variables[token["arguments"][1]["value"]])):
                        return (f"Command {line+1}: argument three must be a valid character number in argument two's variable", False)

                    variables[token["arguments"][0]["value"]] = variables[token["arguments"][1]["value"]][int(three)]
                elif token["name"] == "&":
                    if not len(token["arguments"]) == 3:
                        return (f"Command {line+1}: must have three arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument one must be a variable", False)

                    two = token["arguments"][1]["value"]
                    if token["arguments"][1]["type"] == "\\":
                        two = variables[token["arguments"][1]["value"]]
                    elif token["arguments"][1]["type"] == "<":
                        try:
                            two = int(token["arguments"][1]["value"])
                        except:
                            return (f"Command {line+1}: argument two must be a integer", False)
                    elif token["arguments"][1]["type"] == ">":
                        return (f"Command {line+1}: argument two cannot be a string", False)

                    three = token["arguments"][2]["value"]
                    if token["arguments"][2]["type"] == "\\":
                        three = variables[token["arguments"][2]["value"]]
                    elif token["arguments"][2]["type"] == "<":
                        try:
                            three = int(token["arguments"][2]["value"])
                        except:
                            return (f"Command {line+1}: argument three must be a integer", False)
                    elif token["arguments"][2]["type"] == ">":
                        return (f"Command {line+1}: argument three cannot be a string", False)

                    if two >= three:
                        return (f"Command {line+1}: argument two cannot be larger or equal to argument three.", False)

                    if not (isinstance(two, int) and isinstance(three, int)):
                        return (f"Command {line+1}: argument two and argument three must be integers.", False)

                    variables[token["arguments"][0]["value"]] = float(random.randint(two, three))
                elif token["name"] == "@":
                    if not len(token["arguments"]) == 1:
                        return (f"Command {line+1}: must have one argument.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument one must be a variable", False)

                    variables[token["arguments"][0]["value"]] = float(time.time())
                elif token["name"] == "_import":
                    if not len(token["arguments"]) == 1:
                        return (f"Command {line+1}: must have one argument.", False)

                    if not token["arguments"][0]["type"] == ">":
                        return (f"Command {line+1}: argument one must be a string", False)

                    try:
                        with open(token["arguments"][0]["value"], 'r') as f:
                            content = f.read()
                        tokenizer_result = self.tokenize(str(content))
                        if tokenizer_result[2] == False:
                            return (f"Command {line+1}: tokenization failed", False)
                        run_result = self.run(tokenizer_result[0])
                        if run_result[1] == False:
                            return (f"Command {line+1}: running failed", False)
                    except Exception as e:
                        return (f"Command {line+1}: file reading and/or running failed: {e}", False)
                elif token["name"] == "_get":
                    if not len(token["arguments"]) == 2:
                        return (f"Command {line+1}: must have two arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument one must be a variable", False)

                    one = None
                    if token["arguments"][1]["type"] == ">":
                        one = token["arguments"][1]["value"]
                    elif token["arguments"][1]["type"] == "\\":
                        if isinstance(variables[token["arguments"][1]["value"]], str):
                            one = variables[token["arguments"][1]["value"]]
                        else:
                            return (f"Command {line+1}: argument two must be a string or string variable", False)
                    else:
                        return (f"Command {line+1}: argument two must be a string or string variable", False)
                    
                    try:
                        response = requests.get(one, timeout = 10)
                    except Exception as e:
                        return (f"Command {line+1}: GET request failed: {e}", False)

                    variables[token["arguments"][0]["value"]] = response.text
                elif token["name"] == "_post":
                    if not len(token["arguments"]) == 3:
                        return (f"Command {line+1}: must have three arguments.", False)
                        
                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument one must be a variable", False)

                    one = None
                    if token["arguments"][1]["type"] == ">":
                        one = token["arguments"][1]["value"]
                    elif token["arguments"][1]["type"] == "\\":
                        if isinstance(variables[token["arguments"][1]["value"]], str):
                            one = variables[token["arguments"][1]["value"]]
                        else:
                            return (f"Command {line+1}: argument two must be a string or string variable", False)
                    else:
                        return (f"Command {line+1}: argument two must be a string or string variable", False)

                    two = None
                    if token["arguments"][2]["type"] == ">":
                        two = token["arguments"][2]["value"]
                    elif token["arguments"][2]["type"] == "\\":
                        if isinstance(variables[token["arguments"][2]["value"]], str):
                            two = variables[token["arguments"][2]["value"]]
                        else:
                            return (f"Command {line+1}: argument three must be a string or string variable", False)
                    else:
                        return (f"Command {line+1}: argument three must be a string or string variable", False)
                    
                    try:
                        response = requests.post(one, data=two, timeout=10)
                    except Exception as e:
                        return (f"Command {line+1}: POST request failed: {e}", False)
                    
                    variables[token["arguments"][0]["value"]] = response.text
                elif token["name"] == "_dkv":
                    if not len(token["arguments"]) == 1:
                        return (f"Command {line+1}: must have one argument.", False)

                    one = token["arguments"][0]["value"]
                    if token["arguments"][0]["type"] == "\\":
                        one = variables[token["arguments"][0]["value"]]
                    elif token["arguments"][0]["type"] == "<":
                        return (f"Command {line+1}: argument one cannot be a number.", False)
                    elif token["arguments"][0]["type"] == ">":
                        one = token["arguments"][0]["value"]
                    
                    if isinstance(one, float) or isinstance(one, int):
                        return (f"Command {line+1}: argument one cannot be a number.", False)
                    
                    try:
                        Backtick.sql_query_db("""
                        DELETE FROM storage WHERE key = ?;
                        """, (one,))
                    except Exception as e:
                        return (f"Command {line+1}: database error {e}", False)
                elif token["name"] == "_ekv":
                    if not len(token["arguments"]) == 2:
                        return (f"Command {line+1}: must have two arguments.", False)
                    one = token["arguments"][0]["value"]
                    if token["arguments"][0]["type"] == "\\":
                        one = variables[token["arguments"][0]["value"]]
                    elif token["arguments"][0]["type"] == "<":
                        return (f"Command {line+1}: argument one cannot be a number.", False)
                    elif token["arguments"][0]["type"] == ">":
                        one = token["arguments"][0]["value"]
                    
                    if isinstance(one, float) or isinstance(one, int):
                        return (f"Command {line+1}: argument one cannot be a number.", False)

                    two = token["arguments"][1]["value"]
                    if token["arguments"][1]["type"] == "\\":
                        two = variables[token["arguments"][1]["value"]]
                    elif token["arguments"][1]["type"] == "<":
                        two = float(token["arguments"][1]["value"])
                    elif token["arguments"][1]["type"] == ">":
                        two = token["arguments"][1]["value"]
                    
                    try:
                        Backtick.sql_query_db("""
                        INSERT INTO storage (key, value)
                        VALUES (?, ?)
                        ON CONFLICT(key) DO UPDATE SET value=excluded.value;
                        """, (one, two))
                    except Exception as e:
                        return (f"Command {line+1}: database error {e}", False)
                elif token["name"] == "_rkv":
                    if not len(token["arguments"]) == 2:
                        return (f"Command {line+1}: must have two arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument one must be a variable.", False)

                    if not token["arguments"][0]["value"] in variables:
                        return (f"Command {line+1}: argument one must be an existing variable.", False)

                    two = token["arguments"][1]["value"]
                    if token["arguments"][1]["type"] == "\\":
                        two = variables[token["arguments"][1]["value"]]
                    elif token["arguments"][1]["type"] == "<":
                        return (f"Command {line+1}: argument two cannot be a number.", False)
                    elif token["arguments"][1]["type"] == ">":
                        two = token["arguments"][1]["value"]
                    
                    try:
                        output = Backtick.sql_query_db("""
                        SELECT value FROM storage WHERE key = ?
                        """, (two,))
                    except Exception as e:
                        return (f"Command {line+1}: database error {e}", False)
                    
                    if output == []:
                        return (f"Command {line+1}: key does not exist", False)

                    variables[token["arguments"][0]["value"]] = output[0][0]
                elif token["name"] == "_uf":
                    if not len(token["arguments"]) == 1:
                        return (f"Command {line+1}: must have one argument.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: argument one must be a variable.", False)

                    file_path = str(input("Enter a file path to upload to this program. >> "))

                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                    except Exception as e:
                        return (f"Command {line+1}: file opening error {e}", False)

                    variables[token["arguments"][0]["value"]] = str(content)
                elif token["name"] == "_df":
                    if not len(token["arguments"]) == 1:
                        return (f"Command {line+1}: must have one argument.", False)
                    
                    one = token["arguments"][0]["value"]
                    if token["arguments"][0]["type"] == "\\":
                        one = variables[token["arguments"][0]["value"]]
                    elif token["arguments"][0]["type"] == "<":
                        try:
                            one = str(int(token["arguments"][0]["value"]))
                        except:
                            one = str(token["arguments"][0]["value"])
                    elif token["arguments"][0]["type"] == ">":
                        one = token["arguments"][0]["value"]
                    
                    file_path = Path(str(input("Enter a file path to download to. >> ")))

                    if file_path.exists():
                        return (f"Command {line+1}: file path already exists, cannot download", False)

                    with open(file_path, "w") as f:
                        f.write(one)
                elif token["name"] == "∆":
                    if not len(token["arguments"]) == 4:
                        return (f"Command {line+1}: must have four arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: Argument 1 must be a variable", False)
                    
                    if not token["arguments"][1]["type"] == "\\":
                        return (f"Command {line+1}: Argument 2 must be a variable", False)
                    
                    one = token["arguments"][2]["value"]
                    if token["arguments"][2]["type"] == "\\":
                        if isinstance(variables[token["arguments"][2]["value"]], str):
                            one = variables[token["arguments"][2]["value"]]
                        else:
                            return (f"Command {line+1}: Argument 3 must be a string", False)
                    elif token["arguments"][2]["type"] == "<":
                        return (f"Command {line+1}: Argument 3 must be a string", False)
                    elif token["arguments"][2]["type"] == ">":
                        one = token["arguments"][2]["value"]
                    
                    two = token["arguments"][3]["value"]
                    if token["arguments"][3]["type"] == "\\":
                        if isinstance(variables[token["arguments"][3]["value"]], int) or isinstance(variables[token["arguments"][3]["value"]], float):
                            two = variables[token["arguments"][3]["value"]]
                        else:
                            return (f"Command {line+1}: Argument 4 must be a number", False)
                    elif token["arguments"][3]["type"] == "<":
                        two = float(token["arguments"][3]["value"])
                    elif token["arguments"][3]["type"] == ">":
                        return (f"Command {line+1}: Argument 4 must be a number", False)

                    variables[token["arguments"][1]["value"]] = variables[token["arguments"][0]["value"]].split(one)[int(two)]
                elif token["name"] == "å":
                    if not len(token["arguments"]) == 2:
                        return (f"Command {line+1}: must have two arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: Argument 1 must be a variable", False)
                    
                    two = token["arguments"][1]["value"]
                    if token["arguments"][1]["type"] == "\\":
                        if isinstance(variables[token["arguments"][1]["value"]], int) or isinstance(variables[token["arguments"][1]["value"]], float):
                            two = variables[token["arguments"][1]["value"]]
                        else:
                            return (f"Command {line+1}: Argument 2 must be a number", False)
                    elif token["arguments"][1]["type"] == "<":
                        two = float(token["arguments"][1]["value"])
                    elif token["arguments"][1]["type"] == ">":
                        return (f"Command {line+1}: Argument 2 must be a number", False)

                    variables[token["arguments"][0]["value"]] = abs(two)
                elif token["name"] == "¡":
                    if not len(token["arguments"]) == 2:
                        return (f"Command {line+1}: must have two arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: Argument 1 must be a variable", False)
                    
                    two = token["arguments"][1]["value"]
                    if token["arguments"][1]["type"] == "\\":
                        if isinstance(variables[token["arguments"][1]["value"]], int) or isinstance(variables[token["arguments"][1]["value"]], float):
                            two = variables[token["arguments"][1]["value"]]
                        else:
                            return (f"Command {line+1}: Argument 2 must be a number", False)
                    elif token["arguments"][1]["type"] == "<":
                        two = int(token["arguments"][1]["value"])
                    elif token["arguments"][1]["type"] == ">":
                        return (f"Command {line+1}: Argument 2 must be a number", False)

                    variables[token["arguments"][0]["value"]] = chr(two)
                elif token["name"] == "ª":
                    if not len(token["arguments"]) == 2:
                        return (f"Command {line+1}: must have two arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: Argument 1 must be a variable", False)
                    
                    two = token["arguments"][1]["value"]
                    if token["arguments"][1]["type"] == "\\":
                        if isinstance(variables[token["arguments"][1]["value"]], str):
                            two = variables[token["arguments"][1]["value"]]
                        else:
                            return (f"Command {line+1}: Argument 2 must be a string", False)
                    elif token["arguments"][1]["type"] == "<":
                        return (f"Command {line+1}: Argument 2 must be a string", False)
                    elif token["arguments"][1]["type"] == ">":
                        two = token["arguments"][1]["value"]

                    variables[token["arguments"][0]["value"]] = ord(two)
                elif token["name"] == "§":
                    if not len(token["arguments"]) == 3:
                        return (f"Command {line+1}: must have three arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: Argument 1 must be a variable", False)
                    
                    two = token["arguments"][1]["value"]
                    if token["arguments"][1]["type"] == "\\":
                        two = variables[token["arguments"][1]["value"]]
                    elif token["arguments"][1]["type"] == "<":
                        two = float(token["arguments"][1]["value"])
                    elif token["arguments"][1]["type"] == ">":
                        two = token["arguments"][1]["value"]
                    
                    three = token["arguments"][2]["value"]
                    if token["arguments"][2]["type"] == "\\":
                        if isinstance(variables[token["arguments"][2]["value"]], str):
                            three = variables[token["arguments"][2]["value"]]
                        else:
                            return (f"Command {line+1}: Argument 3 must be a string", False)
                    elif token["arguments"][2]["type"] == "<":
                        return (f"Command {line+1}: Argument 3 must be a string", False)
                    elif token["arguments"][2]["type"] == ">":
                        three = token["arguments"][2]["value"]

                    if three == "<":
                        variables[token["arguments"][0]["value"]] = float(two)
                    elif three == "<<":
                        variables[token["arguments"][0]["value"]] = int(two)
                    elif three == "<<<":
                        if float(two).is_integer():
                            variables[token["arguments"][0]["value"]] = int(two)
                        else:
                            variables[token["arguments"][0]["value"]] = float(two)
                    elif three == ">":
                        variables[token["arguments"][0]["value"]] = str(two)
                    else:
                        return (f"Command {line+1}: Argument 3 contents must be a non variable type", False)
                elif token["name"] == "¢":
                    if not len(token["arguments"]) == 2:
                        return (f"Command {line+1}: must have two arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: Argument 1 must be a variable", False)

                    if token["arguments"][1]["type"] == ">":
                        variables[token["arguments"][0]["value"]] = ">"
                    elif token["arguments"][1]["type"] == "<":
                        variables[token["arguments"][0]["value"]] = "<"
                    elif token["arguments"][1]["type"] == "\\":
                        if isinstance(variables[token["arguments"][1]["value"]], float) or isinstance(variables[token["arguments"][1]["value"]], int):
                            variables[token["arguments"][0]["value"]] = "<"
                        elif isinstance(variables[token["arguments"][1]["value"]], str):
                            variables[token["arguments"][0]["value"]] = ">"
                elif token["name"] == "∫":
                    if not len(token["arguments"]) == 2:
                        return (f"Command {line+1}: must have two arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: Argument 1 must be a variable", False)

                    if token["arguments"][1]["type"] == ">":
                        variables[token["arguments"][0]["value"]] = float(len(token["arguments"][1]["value"]))
                    elif token["arguments"][1]["type"] == "<":
                        return (f"Command {line+1}: Argument 2 cannot be number", False)
                    elif token["arguments"][1]["type"] == "\\":
                        variables[token["arguments"][0]["value"]] = float(len(variables[token["arguments"][1]["value"]]))
                elif token["name"] == "ƒ":
                    if not len(token["arguments"]) == 2:
                        return (f"Command {line+1}: must have two arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: Argument 1 must be a variable", False)

                    if token["arguments"][1]["type"] == ">":
                        return (f"Command {line+1}: Argument 2 cannot be string", False)
                    elif token["arguments"][1]["type"] == "<":
                        variables[token["arguments"][0]["value"]] = float(math.factorial(int(token["arguments"][1]["value"])))
                    elif token["arguments"][1]["type"] == "\\":
                        variables[token["arguments"][0]["value"]] = float(math.factorial(int(variables[token["arguments"][1]["value"]])))
                elif token["name"] == "√":
                    if not len(token["arguments"]) == 2:
                        return (f"Command {line+1}: must have two arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: Argument 1 must be a variable", False)

                    if token["arguments"][1]["type"] == ">":
                        return (f"Command {line+1}: Argument 2 cannot be string", False)
                    elif token["arguments"][1]["type"] == "<":
                        variables[token["arguments"][0]["value"]] = float(math.sqrt(float(token["arguments"][1]["value"])))
                    elif token["arguments"][1]["type"] == "\\":
                        variables[token["arguments"][0]["value"]] = float(math.sqrt(float(variables[token["arguments"][1]["value"]])))
                elif token["name"] == "«":
                    if not len(token["arguments"]) == 3:
                        return (f"Command {line+1}: must have three arguments.", False)

                    if not token["arguments"][0]["type"] == "\\":
                        return (f"Command {line+1}: Argument 1 must be a variable", False)

                    one = None
                    if token["arguments"][1]["type"] == ">":
                        return (f"Command {line+1}: Argument 2 cannot be string", False)
                    elif token["arguments"][1]["type"] == "<":
                        one = token["arguments"][1]["value"]
                    elif token["arguments"][1]["type"] == "\\":
                        one = variables[token["arguments"][1]["value"]]
                    
                    if token["arguments"][2]["type"] == ">":
                        return (f"Command {line+1}: Argument 3 cannot be string", False)
                    elif token["arguments"][2]["type"] == "<":
                        variables[token["arguments"][0]["value"]] = float(float(one) ** float(token["arguments"][2]["value"]))
                    elif token["arguments"][2]["type"] == "\\":
                        variables[token["arguments"][0]["value"]] = float(float(one) ** float(variables[token["arguments"][2]["value"]]))
                else:
                    return (f"Command {line+1}: invalid command.", False)
                line += 1
            
            return (True, True)
        except KeyboardInterrupt:
            return (f"User stopped program.", False)
        except Exception as e:
            return (f"Uncaught error: {e}.", False)