"""
CMIS Shell implementation with interactive command support.
"""

import cmd
import os
import shlex

try:
    import readline

    HAS_READLINE = True
except ImportError:
    HAS_READLINE = False

import pathlib

from cmissh.model import CmisClient


class CmisShell(cmd.Cmd):
    """Interactive shell for CMIS repository operations."""

    intro = "CMIS Shell. Type 'help' for help, 'connect' to connect to a repository."
    prompt = "|:> "

    def __init__(self, verbose=False):
        super().__init__()
        self.client: CmisClient | None = None
        self.repository = None
        self.current_object = None
        self.current_path = "/"
        self.verbose = verbose
        self.dir_stack = []
        self.local_dir_stack = []

        # Setup readline if available
        if HAS_READLINE:
            try:
                # Enable tab completion
                readline.parse_and_bind("tab: complete")
                # Setup history file
                history_file = os.path.expanduser("~/.cmissh_history")
                try:
                    readline.read_history_file(history_file)
                    readline.set_history_length(1000)
                except (FileNotFoundError, PermissionError, OSError):
                    pass
                # Save history on exit (with error handling)
                import atexit

                def safe_write():
                    try:
                        readline.write_history_file(history_file)
                    except (PermissionError, OSError):
                        pass

                atexit.register(safe_write)
            except (PermissionError, OSError):
                pass

    def _require_connection(self):
        """Check if connected to a repository."""
        if self.client is None:
            print("Error: Not connected to a repository. Use 'connect' first.")
            return False
        return True

    def _require_repository(self):
        """Check if a repository is selected."""
        if not self._require_connection():
            return False
        if self.repository is None:
            print("Error: No repository selected. Use 'cd <repository>' to select one.")
            return False
        return True

    def _update_prompt(self):
        """Update the prompt based on current context."""
        if self.repository is None:
            self.prompt = "|:> "
        else:
            repo_name = self.repository.getRepositoryId()
            if self.current_object:
                obj_name = self.current_object.getName()
                self.prompt = f"|{repo_name}:{obj_name}> "
            else:
                self.prompt = f"|{repo_name}> "

    def _resolve_path(self, path):
        """Convert relative path to absolute path."""
        if not path:
            return None
        if path.startswith("/"):
            # Already absolute
            return path
        # Relative path - make it absolute based on current location
        if self.current_object:
            current_path = self.current_object.getPaths()[0]
            if current_path.endswith("/"):
                return current_path + path
            return current_path + "/" + path
        # At root
        return "/" + path

    # Connection commands

    def do_connect(self, arg):
        """
        Connect to a CMIS repository.
        Usage: connect [username:password@]<url>
        Example: connect admin:admin@http://localhost:8080/alfresco/api/-default-/public/cmis/versions/1.1/atom
        """
        if not arg:
            print("Error: Repository URL required")
            print("Usage: connect [username:password@]<url>")
            return

        # Parse connection string
        username = "admin"
        password = "admin"
        url = arg

        if "@" in arg:
            auth, url = arg.rsplit("@", 1)
            if ":" in auth:
                username, password = auth.split(":", 1)

        try:
            self.client = CmisClient(url, username, password)
            print(f"Connected to {url}")
            self._update_prompt()
        except Exception as e:
            print(f"Error connecting to repository: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def do_disconnect(self, arg):
        """
        Disconnect from the current repository.
        Usage: disconnect
        """
        if self.client:
            self.client = None
            self.repository = None
            self.current_object = None
            self.current_path = "/"
            self._update_prompt()
            print("Disconnected")
        else:
            print("Not connected")

    # Navigation commands

    def do_ls(self, arg):
        """
        List contents of current folder or available repositories.
        Usage: ls [path]
        """
        if not self._require_connection():
            return

        try:
            if self.repository is None:
                # List repositories
                repos = self.client.getRepositories()
                print("Available repositories:")
                for repo in repos:
                    print(f"  {repo['repositoryId']}")
            else:
                # List folder contents
                if arg:
                    obj = self.repository.getObjectByPath(arg)
                else:
                    obj = self.current_object or self.repository.getRootFolder()

                if hasattr(obj, "getChildren"):
                    for child in obj.getChildren():
                        name = child.getName()
                        obj_type = child.getProperties().get("cmis:baseTypeId", "")
                        if obj_type == "cmis:folder":
                            print(f"  {name}/")
                        else:
                            print(f"  {name}")
                else:
                    print(f"Error: {obj.getName()} is not a folder")

        except Exception as e:
            print(f"Error: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def do_cd(self, arg):
        """
        Change current directory or select repository.
        Usage: cd <path|repository>
        """
        if not self._require_connection():
            return

        if not arg:
            # Go to root
            if self.repository:
                self.current_object = self.repository.getRootFolder()
                self.current_path = "/"
                self._update_prompt()
            return

        try:
            if self.repository is None:
                # Select a repository
                repos = self.client.getRepositories()
                # Find repository by ID
                repo_found = False
                for repo_info in repos:
                    if repo_info["repositoryId"] == arg:
                        # Get the actual repository object
                        self.repository = self.client.getRepository(arg)
                        self.current_object = self.repository.getRootFolder()
                        self.current_path = "/"
                        print(f"Entered repository: {arg}")
                        self._update_prompt()
                        repo_found = True
                        break
                if not repo_found:
                    print(f"Error: Repository '{arg}' not found")
            else:
                # Navigate to path
                if arg == "..":
                    # Go to parent
                    if self.current_object:
                        parent = self.current_object.getParent()
                        if parent:
                            self.current_object = parent
                            self._update_prompt()
                    return

                # Absolute or relative path
                if arg.startswith("/"):
                    obj = self.repository.getObjectByPath(arg)
                else:
                    if self.current_object:
                        current_path = self.current_object.getPaths()[0]
                        if current_path.endswith("/"):
                            path = current_path + arg
                        else:
                            path = current_path + "/" + arg
                        obj = self.repository.getObjectByPath(path)
                    else:
                        obj = self.repository.getObjectByPath("/" + arg)

                if obj.getProperties().get("cmis:baseTypeId") == "cmis:folder":
                    self.current_object = obj
                    self.current_path = obj.getPaths()[0]
                    self._update_prompt()
                else:
                    print(f"Error: {arg} is not a folder")

        except Exception as e:
            print(f"Error: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def do_pwd(self, arg):
        """
        Print working directory.
        Usage: pwd
        """
        if not self._require_repository():
            return

        if self.current_object:
            paths = self.current_object.getPaths()
            if paths:
                print(paths[0])
        else:
            print("/")

    def do_pushd(self, arg):
        """
        Push current directory to stack and change to new directory.
        Usage: pushd <path>
        """
        if not self._require_repository():
            return

        if not arg:
            print("Error: Path required")
            return

        # Save current location
        self.dir_stack.append((self.current_object, self.current_path))

        # Change to new directory
        self.do_cd(arg)

    def do_popd(self, arg):
        """
        Pop directory from stack and return to it.
        Usage: popd
        """
        if not self._require_repository():
            return

        if not self.dir_stack:
            print("Error: Directory stack is empty")
            return

        self.current_object, self.current_path = self.dir_stack.pop()
        self._update_prompt()

    # Local directory commands

    def do_lpwd(self, arg):
        """
        Print local working directory.
        Usage: lpwd
        """
        print(os.getcwd())

    def do_lcd(self, arg):
        """
        Change local working directory.
        Usage: lcd <path>
        """
        if not arg:
            arg = os.path.expanduser("~")

        try:
            os.chdir(arg)
            print(f"Local directory: {os.getcwd()}")
        except Exception as e:
            print(f"Error: {e}")

    def do_lls(self, arg):
        """
        List local directory contents.
        Usage: lls [path]
        """
        path = arg if arg else "."
        try:
            entries = os.listdir(path)
            for entry in sorted(entries):
                full_path = os.path.join(path, entry)
                if os.path.isdir(full_path):
                    print(f"  {entry}/")
                else:
                    print(f"  {entry}")
        except Exception as e:
            print(f"Error: {e}")

    def do_lpushd(self, arg):
        """
        Push local directory to stack and change to new directory.
        Usage: lpushd <path>
        """
        if not arg:
            print("Error: Path required")
            return

        self.local_dir_stack.append(os.getcwd())
        self.do_lcd(arg)

    def do_lpopd(self, arg):
        """
        Pop local directory from stack and return to it.
        Usage: lpopd
        """
        if not self.local_dir_stack:
            print("Error: Local directory stack is empty")
            return

        path = self.local_dir_stack.pop()
        os.chdir(path)
        print(f"Local directory: {os.getcwd()}")

    # Information commands

    def do_id(self, arg):
        """
        Display information about current object.
        Usage: id [path]
        """
        if not self._require_repository():
            return

        try:
            if arg:
                obj = self.repository.getObjectByPath(arg)
            else:
                obj = self.current_object

            if obj:
                obj_id = obj.getObjectId()
                obj_type = obj.getProperties().get("cmis:objectTypeId", "unknown")
                print(f"Object {obj_id} of type {obj_type}")
            else:
                print("No current object")

        except Exception as e:
            print(f"Error: {e}")

    # File operation commands

    def do_mkdir(self, arg):
        """
        Create a new folder.
        Usage: mkdir <folder_name>
        """
        if not self._require_repository():
            return

        if not arg:
            print("Error: Folder name required")
            return

        try:
            parent = self.current_object or self.repository.getRootFolder()
            properties = {"cmis:objectTypeId": "cmis:folder"}
            new_folder = parent.createFolder(arg, properties)
            print(f"Created folder: {arg}")
        except Exception as e:
            print(f"Error creating folder: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def do_mkfile(self, arg):
        """
        Create a new empty document.
        Usage: mkfile <file_name>
        Alias: mkdoc
        """
        if not self._require_repository():
            return

        if not arg:
            print("Error: File name required")
            return

        try:
            parent = self.current_object or self.repository.getRootFolder()
            properties = {"cmis:objectTypeId": "cmis:document", "cmis:name": arg}
            new_doc = parent.createDocument(properties)
            print(f"Created document: {arg}")
        except Exception as e:
            print(f"Error creating document: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def do_mkdoc(self, arg):
        """Alias for mkfile."""
        self.do_mkfile(arg)

    def do_rm(self, arg):
        """
        Remove an object.
        Usage: rm <name>
        Alias: del
        """
        if not self._require_repository():
            return

        if not arg:
            print("Error: Object name required")
            return

        try:
            # Get the object by path
            if arg.startswith("/"):
                obj = self.repository.getObjectByPath(arg)
            else:
                parent = self.current_object or self.repository.getRootFolder()
                parent_path = parent.getPaths()[0]
                if parent_path.endswith("/"):
                    path = parent_path + arg
                else:
                    path = parent_path + "/" + arg
                obj = self.repository.getObjectByPath(path)

            name = obj.getName()
            obj.delete()
            print(f"Removed: {name}")

        except Exception as e:
            print(f"Error removing object: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def do_del(self, arg):
        """Alias for rm."""
        self.do_rm(arg)

    def do_get(self, arg):
        """
        Download a document's content stream to local file.
        Usage: get <document_name> [local_path]
        Alias: getstream
        """
        if not self._require_repository():
            return

        args = shlex.split(arg) if arg else []
        if not args:
            print("Error: Document name required")
            return

        doc_name = args[0]
        local_path = args[1] if len(args) > 1 else doc_name

        try:
            # Get the document
            if doc_name.startswith("/"):
                obj = self.repository.getObjectByPath(doc_name)
            else:
                parent = self.current_object or self.repository.getRootFolder()
                parent_path = parent.getPaths()[0]
                if parent_path.endswith("/"):
                    path = parent_path + doc_name
                else:
                    path = parent_path + "/" + doc_name
                obj = self.repository.getObjectByPath(path)

            # Get content stream
            content_stream = obj.getContentStream()
            if content_stream:
                pathlib.Path(local_path).write_bytes(content_stream.read())
                print(f"Object stream saved to local file: {local_path}")
            else:
                print("Error: Document has no content stream")

        except Exception as e:
            print(f"Error downloading document: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def do_getstream(self, arg):
        """Alias for get."""
        self.do_get(arg)

    def do_put(self, arg):
        """
        Upload a local file as a new document or update existing document's content.
        Usage: put <local_file> [remote_name]
        Alias: setstream
        """
        if not self._require_repository():
            return

        args = shlex.split(arg) if arg else []
        if not args:
            print("Error: Local file path required")
            return

        local_path = args[0]
        remote_name = args[1] if len(args) > 1 else os.path.basename(local_path)

        if not os.path.exists(local_path):
            print(f"Error: Local file '{local_path}' not found")
            return

        try:
            parent = self.current_object or self.repository.getRootFolder()

            # Try to get existing document
            parent_path = parent.getPaths()[0]
            if parent_path.endswith("/"):
                path = parent_path + remote_name
            else:
                path = parent_path + "/" + remote_name

            try:
                obj = self.repository.getObjectByPath(path)
                # Update existing document
                with open(local_path, "rb") as f:
                    obj.setContentStream(f)
                print(f"Updated content stream: {remote_name}")
            except:
                # Create new document
                with open(local_path, "rb") as f:
                    properties = {
                        "cmis:objectTypeId": "cmis:document",
                    }
                    parent.createDocument(remote_name, properties, contentFile=f)
                print(f"Created document: {remote_name}")

        except Exception as e:
            print(f"Error uploading file: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def do_setstream(self, arg):
        """Alias for put."""
        self.do_put(arg)

    def do_cat(self, arg):
        """
        Read and display a document's content stream to the console.
        Usage: cat <document_name>
        """
        if not self._require_repository():
            return

        if not arg:
            print("Error: Document name required")
            return

        try:
            # Get the document
            if arg.startswith("/"):
                obj = self.repository.getObjectByPath(arg)
            else:
                parent = self.current_object or self.repository.getRootFolder()
                parent_path = parent.getPaths()[0]
                if parent_path.endswith("/"):
                    path = parent_path + arg
                else:
                    path = parent_path + "/" + arg
                obj = self.repository.getObjectByPath(path)

            # Get and display content stream
            content_stream = obj.getContentStream()
            if content_stream:
                content = content_stream.read()
                # Try to decode as text
                try:
                    print(content.decode("utf-8"))
                except:
                    print(content.decode("latin-1"))
            else:
                print("Error: Document has no content stream")

        except Exception as e:
            print(f"Error reading document: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def do_tree(self, arg):
        """
        Display repository tree structure.
        Usage: tree [path] [depth]
        Alias: dump
        """
        if not self._require_repository():
            return

        args = shlex.split(arg) if arg else []
        path = args[0] if len(args) > 0 else None
        max_depth = int(args[1]) if len(args) > 1 else 3

        try:
            if path:
                obj = self.repository.getObjectByPath(path)
            else:
                obj = self.current_object or self.repository.getRootFolder()

            self._print_tree(obj, 0, max_depth)

        except Exception as e:
            print(f"Error displaying tree: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def _print_tree(self, obj, depth, max_depth):
        """Recursively print tree structure."""
        if depth >= max_depth:
            return

        indent = "  " * depth
        name = obj.getName()
        obj_type = obj.getProperties().get("cmis:baseTypeId", "")

        if obj_type == "cmis:folder":
            print(f"{indent}{name}/")
            try:
                for child in obj.getChildren():
                    self._print_tree(child, depth + 1, max_depth)
            except:
                pass
        else:
            print(f"{indent}{name}")

    def do_dump(self, arg):
        """Alias for tree."""
        self.do_tree(arg)

    # Property commands

    def do_props(self, arg):
        """
        Display all properties of an object.
        Usage: props [path]
        """
        if not self._require_repository():
            return

        try:
            if arg:
                abs_path = self._resolve_path(arg)
                obj = self.repository.getObjectByPath(abs_path)
            else:
                obj = self.current_object

            if not obj:
                print("Error: No current object")
                return

            properties = obj.getProperties()
            print(f"\nProperties of {obj.getName()}:\n")
            for key, value in sorted(properties.items()):
                print(f"{key} = {value}")

        except Exception as e:
            print(f"Error: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def do_propget(self, arg):
        """
        Get a specific property value from an object.
        Usage: propget <property_name> [path]
        Alias: getp
        """
        if not self._require_repository():
            return

        args = shlex.split(arg) if arg else []
        if not args:
            print("Error: Property name required")
            return

        prop_name = args[0]
        obj_path = args[1] if len(args) > 1 else None

        try:
            if obj_path:
                abs_path = self._resolve_path(obj_path)
                obj = self.repository.getObjectByPath(abs_path)
            else:
                obj = self.current_object

            if not obj:
                print("Error: No current object")
                return

            properties = obj.getProperties()
            if prop_name in properties:
                print(f"{prop_name} = {properties[prop_name]}")
            else:
                print(f"Error: Property '{prop_name}' not found")

        except Exception as e:
            print(f"Error: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def do_getp(self, arg):
        """Alias for propget."""
        self.do_propget(arg)

    def do_propset(self, arg):
        """
        Set a property value on an object.
        Usage: propset <property_name> <value> [path]
        Alias: setp
        """
        if not self._require_repository():
            return

        args = shlex.split(arg) if arg else []
        if len(args) < 2:
            print("Error: Property name and value required")
            return

        prop_name = args[0]
        prop_value = args[1]
        obj_path = args[2] if len(args) > 2 else None

        try:
            if obj_path:
                obj = self.repository.getObjectByPath(obj_path)
            else:
                obj = self.current_object

            if not obj:
                print("Error: No current object")
                return

            # Update the property
            properties = {prop_name: prop_value}
            obj.updateProperties(properties)
            print(f"Updated {prop_name} = {prop_value}")

        except Exception as e:
            print(f"Error: {e}")
            if self.verbose:
                import traceback

                traceback.print_exc()

    def do_setp(self, arg):
        """Alias for propset."""
        self.do_propset(arg)

    # Utility commands

    def do_help(self, arg):
        """Show help for commands."""
        if arg:
            # Show help for specific command
            try:
                func = getattr(self, f"do_{arg}")
                print(func.__doc__)
            except AttributeError:
                print(f"No help available for '{arg}'")
        else:
            # Show list of commands
            print("\nAvailable commands:\n")
            print("Connection:")
            print("  connect, disconnect")
            print("\nNavigation:")
            print("  ls, cd, pwd, pushd, popd, tree")
            print("\nFile operations:")
            print("  mkdir, mkfile, rm, get, put, cat")
            print("\nProperties:")
            print("  props, propget, propset")
            print("\nLocal file system:")
            print("  lpwd, lcd, lls, lpushd, lpopd")
            print("\nInformation:")
            print("  id, help")
            print("\nOther:")
            print("  exit, quit")
            print("\nType 'help <command>' for detailed help on a command.")

    def do_exit(self, arg):
        """
        Exit the shell.
        Usage: exit
        """
        print("Bye")
        return True

    def do_quit(self, arg):
        """
        Exit the shell.
        Usage: quit
        """
        return self.do_exit(arg)

    def do_EOF(self, arg):
        """Handle Ctrl-D."""
        print()
        return self.do_exit(arg)

    def emptyline(self):
        """Do nothing on empty line."""

    def default(self, line):
        """Handle unknown commands."""
        print(f"Unknown command: {line}")
        print("Type 'help' for available commands")
