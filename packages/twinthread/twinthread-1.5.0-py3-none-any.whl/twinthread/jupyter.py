from IPython import get_ipython
from .string_handling import task_string_to_context, pretty_result
from .exec_task import exec_code
import sys


def confirm(text, default_yes=True):
    choice = input(text + "(Y/n)" if default_yes else "(y/N)")
    choice = choice.lower()
    if choice == "":
        return default_yes
    if choice == "y":
        return True
    elif choice == "n":
        return False
    print("Please respond with 'y' or 'n'.")
    return confirm(text, default_yes)


MODULE_DEFAULT_VALUE = "____MODULE_DEFAULT_VALUE"


def get_notebook_client():
    notebook = sys.modules["__main__"]
    try:
        return notebook.twinthread_client
    except AttributeError:
        pass
    try:
        return notebook.client
    except AttributeError:
        pass

    return None


def register_jupyter():
    try:
        from IPython.core.magic import Magics, magics_class, cell_magic, line_magic

        @magics_class
        class UploadToTwinThread(Magics):
            def __init__(self, shell=None, **kwargs):
                super().__init__(shell=shell, **kwargs)

            def init_task(self, line, cell):
                # If in a jupyter context (which we have to be if we're here) __main__ will be the notebook scope
                client = get_notebook_client()
                if client is None:
                    print(
                        "Unable to upload task. Please initialize `twinthread_client` or `client` in this session."
                    )
                    return
                try:
                    context = task_string_to_context(line.split(" ")[0])
                except Exception as e:
                    print(
                        "Issue parsing task string. Please provide encoded task string: %%twinthread NDcsOTMsMzQ1LDM0NDU="
                    )
                    print(e)
                    return

                return client, context

            def run(self, client, context, code):
                old_context = client.get_context()
                client.set_context(context)
                result = exec_code(code, client)
                client.set_context(old_context)
                print(pretty_result(result))
                return result

            @cell_magic
            def run_task(self, line, cell):
                client, context = self.init_task(line, cell)
                return self.run(client, context, cell)

            @cell_magic
            def upload_task(self, line, cell):
                client, context = self.init_task(line, cell)

                if not confirm("Save this cell to TwinThread?"):
                    return

                if confirm("Test before uploading?"):
                    result = self.run(client, context, cell)
                    if result["errors"] != "":
                        print("\nErrors testing cell. Aborting upload.")
                        return

                task = client.get_task(context)
                client._update_task_code(task, cell)

                print("Cell contents uploaded to TwinThread task")

        ## use ipython load_ext mechanisme here if distributed
        get_ipython().register_magics(UploadToTwinThread)
    except Exception as e:
        pass
