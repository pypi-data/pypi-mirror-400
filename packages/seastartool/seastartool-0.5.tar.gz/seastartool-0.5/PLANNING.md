


Core to SeaSTAR are three components:

- CLI interpreter
- TUI interpreter
- GUI interpreter

Each allows a different way to interact with a Job

Each job is split into the following components:

- JSON definition of job inputs and outputs, help text, prompts, and preferred CLI options
- Job python script
- Job assets for GUI

Internally jobs should aim to use the provider pattern to process data piece by piece. Files should ideally not be loaded entirely into memory.


## Semantic types

Give hints as to what GUI elements should be used.

MULTIPLE_FILES - Selecting input files

SINGLE_FOLDER - Selecting an input or output directory

SWITCH - A simple, isolated true/false option

CHOICE - A simple choice between a few categories

BRANCH - A more complex choice that might impact other elements or change how the form is laid out

VALUE - Self explanatory, the default form control will be used for the data type. If a default value is supplied it will be a single input field with the default value. If it is a required field it will be a single imput field that will refuse to continue without content. If it is an optional field without a default value, it will be a checkbox combined with an input field.



