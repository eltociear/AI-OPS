import json
import subprocess


class Tool:
    name: str
    tool_description: str
    args_description: str
    examples: str

    @staticmethod
    def load_tool(path: str):
        """Get tool description from json file"""
        with open(path, 'r', encoding='utf-8') as fp:
            tool_data = json.load(fp)

            tool = Tool()
            tool.name = tool_data['name']
            tool.tool_description = ''.join(tool_data['tool_description'])
            tool.args_description = ''.join(tool_data['args_description'])
            tool.examples = ''.join(tool_data['examples'])

            return tool

    @staticmethod
    def run(*args):
        """Execute a tool"""
        if not isinstance(args[0], str):
            raise ValueError(f'Argument must be a string found {type(args[0])}')

        command = args[0].encode('utf-8').decode('utf-8')
        arguments = command.split()
        result = subprocess.run(arguments, capture_output=True)

        stdout = result.stdout.decode('utf-8', errors='replace')
        stderr = result.stderr.decode('utf-8', errors='replace')

        if len(stderr) > 0:
            return f'{stdout}\n{stderr}'
        return stdout

    def get_documentation(self):
        """Used to provide documentation for the Agent LLM"""
        return f"""
Tool: {self.name}
Description: 
    {self.tool_description}
Arguments:
    {self.args_description}          
Usage Examples: 
    {self.examples}"""

