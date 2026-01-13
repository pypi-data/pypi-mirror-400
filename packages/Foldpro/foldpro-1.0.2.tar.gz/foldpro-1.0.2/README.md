# Foldpro
Have you ever wished you could parse your directories and find specific types of files?
Foldpro lets you do exactly that. Give it the path to a folder you'd like to organize, and it will create an organized copy under `~/Foldpro Copies`.

These organized copies can be categorized into one (or all) of the following:
- Pictures
- Code Files
- Downloads From Terminal
- Others

# Prerequisites
- macOS
- Python 3.9 or higher

# How to Use
1. Install Foldpro: pip3 install foldpro
2. Follow the prompts until your folders have been organized
3. Run it: foldpro
4. Go to `~/Foldpro Copies` to view the organized copy

**Note:** To exit at any time, enter `e` at any prompt.

# How Foldpro Works
Here are some details about how Foldpro organizes your files:

1. In `all` mode, only folders containing categorized files will remain in the organized copy. Empty folders are removed for neatness.
2. If files in the copy share the same name, Foldpro appends digits to avoid collisions.
3. Symlinks are organized based on their targets. Symlinks whose targets are directories or do not exist will be placed in the `Others` folder to prevent clutter.
