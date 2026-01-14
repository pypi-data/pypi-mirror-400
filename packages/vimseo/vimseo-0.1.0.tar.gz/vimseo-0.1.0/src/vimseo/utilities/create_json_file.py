# Copyright 2021 IRT Saint Exupéry, https://www.irt-saintexupery.com
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License version 3 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

# Copyright (c) 2019 IRT-AESE.
# All rights reserved.
#
# Contributors:
#    INITIAL AUTHORS - API and implementation and/or documentation
#        :author: XXXXXXXXXXX
#    OTHER AUTHORS   - MACROSCOPIC CHANGES
"""Create a JSON file to define the JSON grammar of inputs, options or outputs."""

from __future__ import annotations

import logging
import os
import pathlib

from gemseo.core.grammars.json_grammar import JSONGrammar

LOGGER = logging.getLogger("VIMS")


class JsonFile:
    def __init__(
        self, name, grammar_type, properties, path="./", required=None, bounds=None
    ):
        """Constructor :param name : grammar name :param grammar_type : the type of
        grammar : input, options or output :param properties : a dictionary, the keys are
        the properties name, the values are the default values of the properties :param
        path : the path to the folder where the json file will be saved :param required :
        a list of required properties if only specific properties are required.

        By default, all properties are considered as required
        :param bounds : a dictionary, the keys are the properties name, the values are
            the lower and upper bounds of the properties
        """

        # super(JsonFile, self).__init__()
        self.name = name
        self.path = path
        if "input" in grammar_type.lower():
            self.io.grammar_type = "_input"
            self.json_name = os.path.join(self.path, self.name + self.io.grammar_type)
            schema = self.create_grammar_with_arrays(properties, required)
            if bounds is None:
                self.write_json_file(schema, properties)
            else:
                self.write_json_file_with_bounds(schema, properties, bounds)
        elif "option" in grammar_type.lower():
            self.io.grammar_type = "_options"
            self.json_name = os.path.join(self.path, self.name + self.io.grammar_type)
            schema = self.create_schema_from_properties(properties, required)
            self.write_json_file_no_array(schema, properties)
        elif "output" in grammar_type.lower():
            self.io.grammar_type = "_output"
            self.json_name = os.path.join(self.path, self.name + self.io.grammar_type)
            schema = self.create_grammar_with_arrays(properties, required)
            self.write_json_file(schema, properties)
        else:
            LOGGER.info("Invalid grammar type")

    def create_grammar_with_arrays(self, properties, required):
        """Create the new grammar using JSONGrammar :param properties : a dictionary, the
        keys are the properties name, the values are the default values of the properties
        :param required : a list of required properties if only specific properties are
        required.

        By default, all properties are considered as required
        :return schema: schema containing the grammar as a dictionary, all the properties
            are defined as arrays. The arrays can contain any type of items. The item
            type is based on the type of the property value.
        """

        grammar = JSONGrammar(self.json_name)
        grammar.update_from_data(properties)
        schema = grammar.schema
        schema.update({"name": self.name + self.io.grammar_type})
        if required is not None:
            schema.update({"required": required})
        return schema

    def create_schema_from_properties(self, properties, required):
        """Create a new schema containing the new grammar :param properties : a
        dictionary, the keys are the properties name, the values are the default values
        of the properties :param required : a list of required properties if only
        specific properties are required.

        By default, all properties are considered as required
        :return schema: schema containing the grammar as a dictionary, the property type
            is based on the type of the property value.
        """

        schema = {}
        schema["properties"] = {}
        for p in properties:
            if isinstance(properties[p], str):
                schema["properties"][p] = {"type": "string"}
            elif isinstance(properties[p], float):
                schema["properties"][p] = {"type": "number"}
            elif isinstance(properties[p], int):
                schema["properties"][p] = {"type": "integer"}
            else:
                schema["properties"][p] = {"type": "object"}
        schema.update({"name": self.name + self.io.grammar_type})
        if required is None:
            required = properties.keys()
        schema.update({"required": required})
        return schema

    def write_json_file(self, schema, properties):
        with pathlib.Path(self.json_name + ".json").open("w") as json_file:
            json_file.write("{\n")
            json_file.write('    "name": "' + schema["name"] + '",\n')
            json_file.write(
                '    "required": ' + str(schema["required"]).replace("'", '"') + ",\n"
            )
            json_file.write('    "properties":{\n')
            lines = []
            for p in schema["properties"]:
                lines.extend((
                    '        "' + p + '": {\n',
                    '            "description": "",\n',
                    '            "type": "array",\n',
                    '            "items": {\n',
                ))
                type = schema["properties"][p]["type"]
                lines.append('                "type": "' + type + '",\n')
                if type == "string":
                    lines.append(
                        '                "default": "' + str(properties[p]) + '"\n'
                    )
                else:
                    lines.append(
                        '                "default": ' + str(properties[p]) + "\n"
                    )
                lines.append("            }\n        },\n")
            lines[-1] = "            }\n        }\n"
            json_file.writelines(lines)
            json_file.write("    },\n")
            json_file.write(
                '    "$schema": "http://json-schema.org/draft-04/schema",\n'
            )
            json_file.write('    "type": "object",\n')
            json_file.write('    "id": "#' + schema["name"] + '"\n}')

    def write_json_file_no_array(self, schema, properties):
        with pathlib.Path(self.json_name + ".json").open("w") as json_file:
            json_file.write("{\n")
            json_file.write('    "name": "' + schema["name"] + '",\n')
            json_file.write(
                '    "required": ' + str(schema["required"]).replace("'", '"') + ",\n"
            )
            json_file.write('    "properties":{\n')
            lines = []
            for p in schema["properties"]:
                lines.extend((
                    '        "' + p + '": {\n',
                    '            "description": "",\n',
                ))
                type = schema["properties"][p]["type"]
                lines.append('            "type": "' + type + '",\n')
                if type == "string":
                    lines.append(
                        '            "default": "' + str(properties[p]) + '"\n'
                    )
                else:
                    lines.append('            "default": ' + str(properties[p]) + "\n")
                lines.append("            },\n")
            lines[-1] = "            }\n"
            json_file.writelines(lines)
            json_file.write("    },\n")
            json_file.write(
                '    "$schema": "http://json-schema.org/draft-04/schema",\n'
            )
            json_file.write('    "type": "object",\n')
            json_file.write('    "id": "#' + schema["name"] + '"\n}')

    def write_json_file_with_bounds(self, schema, properties, bounds):
        with pathlib.Path(self.json_name + ".json").open("w") as json_file:
            json_file.write("{\n")
            json_file.write('    "name": "' + schema["name"] + '",\n')
            json_file.write(
                '    "required": ' + str(schema["required"]).replace("'", '"') + ",\n"
            )
            json_file.write('    "properties":{\n')
            lines = []
            for p in schema["properties"]:
                lines.extend((
                    '        "' + p + '": {\n',
                    '            "description": "",\n',
                    '            "type": "array",\n',
                    '            "items": {\n',
                ))
                type = schema["properties"][p]["type"]
                lines.append('                "type": "' + type + '",\n')
                if type == "string":
                    lines.append('                "enum": [\n')
                    lines.extend(
                        '                    "' + e + '",\n' for e in bounds[p][:-1]
                    )
                    lines.extend((
                        '                    "'
                        + bounds[p][-1]
                        + '"\n                ],\n',
                        '                "default": "' + str(properties[p]) + '"\n',
                    ))
                else:
                    lines.extend((
                        '                "maximum": ' + str(max(bounds[p])) + ",\n",
                        '                "minimum": ' + str(min(bounds[p])) + ",\n",
                        '                "default": ' + str(properties[p]) + "\n",
                    ))
                lines.append("            }\n        },\n")
            lines[-1] = "            }\n        }\n"
            json_file.writelines(lines)
            json_file.write("    },\n")
            json_file.write(
                '    "$schema": "http://json-schema.org/draft-04/schema",\n'
            )
            json_file.write('    "type": "object",\n')
            json_file.write('    "id": "#' + schema["name"] + '"\n}')
