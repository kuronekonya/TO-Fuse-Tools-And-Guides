This is specifically for adding the ItemParam XML to ItemParam DB with little to no work.

## How to use

### converter.py

This is the main converter. 

1. Select your XML (you can select multiple!)
2. Select output folder
3. Wait for the popup
4. Yay it's in the output folder

### combine_excess_sql.py

This is in case there's a ton of files that you didn't expect and you don't feel like experimenting with the chunks, you can cut the files down by about 1/4. May lag SSMS. Use at your own risk.

1. Put combine_excess_sql.py in the output folder from converter.py
2. Run and wait very briefly
3. Done, check the output_batches folder in the same directory.

### runsql.py

I have no excuse for this. I am lazy. Runs SQL one after another. Requires editing the file and downloading a dependency to complete, but man, is it better than clicking 50-300 files one after another while waiting for SSMS to do its thing. How dull.

1. Open Command Prompt (Left click the start menu and search up "cmd" without quotes and run it)
2. Install the dependency, pyodbc, with ```pip install pyodbc```
3. Go back to runsql.py
4. Right Click > Edit with Notepad or any IDE
5. Change the parameters under === CONFIGURATION === and, optionally, the Driver variable. The variables necessary to change are your DATABASE, USERNAME, and PASSWORD for dbo.ItemParam, if you are running this on the server computer.
6. Save
7. Put in the folder with the bulk SQL files
8. Run that mf
9. Go get a nice treat while you're waiting you deserve it