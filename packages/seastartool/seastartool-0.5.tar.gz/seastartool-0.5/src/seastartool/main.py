import sys
import importlib
import os
import json
import time
import math

def base_cli():
    python_file_loc = os.path.dirname(os.path.realpath(__file__))

    job_dirs = os.scandir(os.path.join(python_file_loc, "jobs"))
    found_job_modules = {}
    module_io_defs = {}
    for job_dir in job_dirs:
        if job_dir.is_dir():
            if not job_dir.name.startswith("__"):
                full_job_dir = os.path.join(python_file_loc, "jobs", job_dir.name)
                with open(os.path.join(full_job_dir, "io.json"), "r") as io_json_fp:
                    module_io_defs[job_dir.name] = json.loads(io_json_fp.read())
                    #print("loading jobs." + job_dir.name)
                    found_job_modules[job_dir.name] = "seastartool.jobs." + job_dir.name
                    #options = {}
                    #found_job_modules[job_dir.name].MainJob(options)



    #for
    #found_job_modules[module_name] = importlib.import_module(module_path)

    eargs = sys.argv[1:]
    help_flag = False
    ehelp_msg = "No command specified"

    mode = "command"
    mode_stack = []
    capture_heap = []
    command = None
    capture_option = None
    multiple_capture_switch = False
    options = {}
    io_def = None
    gui_flag = False

    for arg in eargs:
        if arg.startswith("--"):
            if multiple_capture_switch:
                multiple_capture_switch = False
                mode = mode_stack.pop() # Break out of the current multiple capture
            if arg == "--help":
                command = "help"
                ehelp_msg = None
                help_flag = True
                break
            if arg == "--gui":
                gui_flag = True
            else:
                option_recognised = False
                if io_def is not None:
                    for io_def_key in io_def["inputs"].keys():
                        if "cli_arg" in io_def["inputs"][io_def_key].keys():
                            if io_def["inputs"][io_def_key]["cli_arg"] == arg[2:]:
                                capture_option = io_def_key
                                if "multiple" in io_def["inputs"][io_def_key].keys():
                                    multiple_capture_switch = io_def["inputs"][io_def_key]["multiple"]
                                if io_def["inputs"][io_def_key]["type"] == "BOOLEAN":
                                    options[io_def_key] = True
                                else:
                                    mode_stack.append(mode)
                                    if multiple_capture_switch:
                                        mode = "multi_capture"
                                    else:
                                        mode = "single_capture"
                                option_recognised = True
                                break

                if not option_recognised:
                    ehelp_msg = "Unrecognised option \"" + arg + "\""
                    help_flag = True
                    break
        elif arg.startswith("-"):
            if multiple_capture_switch:
                multiple_capture_switch = False
                mode = mode_stack.pop() # Break out of the current multiple capture
            if arg == "-h":
                command = "help"
                ehelp_msg = None
                help_flag = True
                break
            else:
                option_recognised = False
                if io_def is not None:
                    for io_def_key in io_def["inputs"].keys():
                        if "cli_short" in io_def["inputs"][io_def_key].keys():
                            if io_def["inputs"][io_def_key]["cli_short"] == arg[1:]:
                                capture_option = io_def_key
                                if "multiple" in io_def["inputs"][io_def_key].keys():
                                    multiple_capture_switch = io_def["inputs"][io_def_key]["multiple"]
                                if io_def["inputs"][io_def_key]["type"] == "BOOLEAN":
                                    options[io_def_key] = True
                                else:
                                    mode_stack.append(mode)
                                    if multiple_capture_switch:
                                        mode = "multi_capture"
                                    else:
                                        mode = "single_capture"
                                option_recognised = True
                                break

                if not option_recognised:
                    ehelp_msg = "Unrecognised option \"" + arg + "\""
                    help_flag = True
                    break
        else:
            if mode == "command":
                if arg == "help":
                    command = "help"
                    ehelp_msg = None
                    help_flag = True
                    break
                else:
                    if arg in module_io_defs.keys():
                        io_def = module_io_defs[arg]
                        command = arg
                        ehelp_msg = None
                    else:
                        ehelp_msg = "Unrecognised command \"" + arg + "\""
                        help_flag = True
                        break
            elif mode == "multi_capture":
                capture_heap.append(arg)
                options[capture_option] = capture_heap
            elif mode == "single_capture":
                options[capture_option] = arg
                mode = mode_stack.pop()

    if command is None:
        if not gui_flag:
            help_flag = True

    if not help_flag:
        if io_def is not None:
            for option_key in io_def["inputs"].keys():
                if option_key not in options.keys():
                    if "default" in io_def["inputs"][option_key].keys():
                        options[option_key] = io_def["inputs"][option_key]["default"]
                    elif "required" in io_def["inputs"][option_key].keys():
                        if io_def["inputs"][option_key]["required"]:
                            help_flag = True
                            ehelp_msg = "Missing required option \"" + option_key +  "\", specified by"
                            if "cli_arg" in io_def["inputs"][option_key]:
                                ehelp_msg += " \"--" + io_def["inputs"][option_key]["cli_arg"] + " <value>\""
                            if "cli_short" in io_def["inputs"][option_key]:
                                ehelp_msg += " \"-" + io_def["inputs"][option_key]["cli_short"] + " <value>\""
                            if "hint" in io_def["inputs"][option_key].keys():
                                ehelp_msg += "\nHint: " + io_def["inputs"][option_key]["hint"]

    if help_flag:
        print("")
        print("SeaSTAR")
        print("Sea-faring System for Tagging, Attribution and Redistribution")
        print("")
        print("Copyright 2025, A Baldwin <alewin@noc.ac.uk>, National Oceanography Centre")
        print("This program comes with ABSOLUTELY NO WARRANTY. This is free software,")
        print("and you are welcome to redistribute it under the conditions of the")
        print("GPL version 3 license.")
        print("")
        if ehelp_msg is not None:
            print("ERROR")
            print(ehelp_msg)
            print("")
        #print("Common usage:")
        #print("    ifcbproc parquet <roi_file> [roi_file...] -o <output_path>")
        #print("    ifcbproc ecotaxa <roi_file> [roi_file...] -o <output_zip_file> [--table example_metadata.csv --join \"tables.example_metadata.filename = file.basename\" [--hide tables.example_metadata.filename]]")
        #print("    ifcbproc features <roi_file> [roi_file...] [-o <output_path>]")
        #print("")
    else:
        if gui_flag:
            from .gui import SeaSTARGUI # Avoid loading the GUI if the user doesn't want it!
            gui = SeaSTARGUI(python_file_loc=python_file_loc)
            gui.enter_mainloop()
        else:
            job_start_time = time.time()
            print("Preparing job...")

            def prf(prop, etr):
                bar_w = 16
                bar_x = round(bar_w * prop)
                bar_l = "#"*bar_x
                bar_r = "_"*(bar_w - bar_x)
                percent = f"{prop:.2%}"
                secs = round(etr)
                timestr = f"about {secs}s remaining..."
                if secs < 3:
                    timestr = "only a few seconds remaining..."
                if secs > 60:
                    mins = math.floor(secs / 60)
                    secs = secs - (mins * 60)
                    timestr = f"about {mins}min {secs}s remaining..."
                if secs > 3600:
                    hrs = math.floor(mins / 60)
                    mins = mins - (hrs * 60)
                    timestr = f"about {hrs}hr {mins}min remaining..."

                print(f"\r[{bar_l}{bar_r}] {percent} done, {timestr}".ljust(79, " "), end="")

            main_job_object = importlib.import_module(found_job_modules[command]).MainJob(options, prf)
            print("Processing...")
            main_job_object.execute()
            job_end_time = time.time()

            secs = round(job_end_time - job_start_time)
            timestr = f"{secs}s"
            if secs > 60:
                mins = math.floor(secs / 60)
                secs = secs - (mins * 60)
                timestr = f"{mins}min {secs}s"
            if secs > 3600:
                hrs = math.floor(mins / 60)
                mins = mins - (hrs * 60)
                timestr = f"{hrs}hr {mins}min"

            print(f"\rFinished in  {timestr}".ljust(79, " "))
            print("Done!")

