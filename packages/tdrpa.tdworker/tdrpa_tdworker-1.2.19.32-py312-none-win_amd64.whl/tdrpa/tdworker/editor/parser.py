import ast
import os
import re

class CommandParam:
    def __init__(self, name, param_type, default_value=None, required=False, description=""):
        self.name = name
        self.type = param_type
        self.default = default_value
        self.required = required
        self.description = description

    def __repr__(self):
        return f"Param(name={self.name}, type={self.type}, default={self.default}, required={self.required})"

class CommandDefinition:
    def __init__(self, name, description=""):
        self.name = name
        self.description = description
        self.params = []  # List of CommandParam

    def __repr__(self):
        return f"Command(name={self.name}, params={len(self.params)})"

class ModuleDefinition:
    def __init__(self, name, file_path):
        self.name = name
        self.file_path = file_path
        self.commands = [] # List of CommandDefinition

    def __repr__(self):
        return f"Module(name={self.name}, commands={len(self.commands)})"

class PyiParser:
    def __init__(self, directory):
        self.directory = directory
        self.modules = []

    def parse(self):
        for filename in os.listdir(self.directory):
            if filename.endswith(".pyi") and filename.startswith("_"):
                file_path = os.path.join(self.directory, filename)
                self._parse_file(file_path)
        return self.modules

    def _parse_file(self, file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()
        
        try:
            tree = ast.parse(source)
        except SyntaxError:
            print(f"Error parsing {file_path}")
            return

        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                module_name = node.name
                module_def = ModuleDefinition(module_name, file_path)
                
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        # check for staticmethod
                        is_static = False
                        for dec in item.decorator_list:
                            if isinstance(dec, ast.Name) and dec.id == 'staticmethod':
                                is_static = True
                                break
                        
                        if is_static:
                            cmd_def = self._parse_function(item)
                            module_def.commands.append(cmd_def)
                
                self.modules.append(module_def)

    def _parse_function(self, func_node: ast.FunctionDef):
        cmd_name = func_node.name
        docstring = ast.get_docstring(func_node) or ""
        
        # Parse docstring for descriptions
        description = docstring.strip().split('\n')[0] if docstring else cmd_name
        
        param_docs = {}
        # Simple regex to extract param info from docstring like :param name:[必选参数] desc
        # Matches: :param name:[attributes]description
        param_pattern = re.compile(r':param\s+(\w+):\s*(\[.*?\])?(.*)')
        
        for line in docstring.split('\n'):
            line = line.strip()
            match = param_pattern.match(line)
            if match:
                p_name, p_attr, p_desc = match.groups()
                param_docs[p_name] = {
                    'attr': p_attr,
                    'desc': p_desc.strip()
                }

        cmd_def = CommandDefinition(cmd_name, description)

        # Parse arguments
        args = func_node.args
        # defaults correspond to the last n arguments
        num_defaults = len(args.defaults)
        num_args = len(args.args)
        
        for i, arg in enumerate(args.args):
            arg_name = arg.arg
            if arg_name == 'self':
                continue
            
            # Type annotation
            arg_type = "str" # Default
            if arg.annotation:
                arg_type = self._get_annotation_str(arg.annotation)
            
            # Default value
            default_val = None
            has_default = False
            
            # Calculate if this arg has a default
            # Defaults are aligned to the end of the args list
            if i >= (num_args - num_defaults):
                default_index = i - (num_args - num_defaults)
                default_node = args.defaults[default_index]
                default_val = self._get_literal_value(default_node)
                has_default = True
            
            # Required logic
            # Explicitly "Needed" if docstring says [必选参数] OR if it has no default value (and is not first if method, but these are static)
            # In these pyi files, explicit params usually have no defaults in signature, or sometimes they do.
            # Let's rely on signature: if no default, it's required.
            # Also check docstring for overrides?
            
            p_doc = param_docs.get(arg_name, {})
            p_desc = p_doc.get('desc', "")
            p_attr = p_doc.get('attr', "")
            
            is_required = not has_default
            if "[必选参数]" in p_attr:
                is_required = True
            elif "[可选参数]" in p_attr:
                is_required = False
            
            cmd_def.params.append(CommandParam(
                name=arg_name,
                param_type=arg_type,
                default_value=default_val,
                required=is_required,
                description=p_desc
            ))
            
        return cmd_def

    def _get_annotation_str(self, node):
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_annotation_str(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_annotation_str(node.value)}[{self._get_annotation_str(node.slice)}]"
        elif isinstance(node, ast.Constant):
            return str(node.value)
        elif isinstance(node, ast.BinOp): # Union types: str | int
             return f"{self._get_annotation_str(node.left)} | {self._get_annotation_str(node.right)}"
        return "any"

    def _get_literal_value(self, node):
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.List):
            return [self._get_literal_value(elt) for elt in node.elts]
        elif isinstance(node, ast.Tuple):
            return tuple(self._get_literal_value(elt) for elt in node.elts)
        elif isinstance(node, ast.Dict):
            return {self._get_literal_value(k): self._get_literal_value(v) for k, v in zip(node.keys, node.values)}
        elif isinstance(node, ast.NameConstant): # True, False, None in older python
             return node.value
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub) and isinstance(node.operand, ast.Constant):
            return -node.operand.value # Negative numbers
        return None

if __name__ == "__main__":
    # Test
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parser = PyiParser(current_dir)
    modules = parser.parse()
    for m in modules:
        print(f"Module: {m.name}")
        for c in m.commands[:3]: # Print first 3 commands
            print(f"  Command: {c.name} ({c.description})")
            for p in c.params:
                print(f"    Param: {p}")
