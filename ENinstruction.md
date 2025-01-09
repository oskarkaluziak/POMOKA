**POMOKA Application User Guide**

**Introduction**

POMOKA is an application designed for statistical analysis of medical data and visualization of results in the form of survival curves. The program allows you to:

- Load CSV and XLSX files containing patient data.

- Perform statistical analyses, such as Kolmogorov-Smirnov tests, Mann-Whitney U tests, or area under the curve (AUC) analysis.

- Generate reports in PDF or PNG format.

- Edit charts.

**Getting Started**

- Launching the Application

- Once you launch the application, you will see the main window with buttons and options for managing the program.

**Loading Data**

- Click the Upload data button.

- Select a data file (supported formats: CSV, XLSX).

- Specify the row number containing column headers (default is the first row).

The application will display information about the number of rows and columns in the loaded file.

**Setting Preferences and Ranges**

Setting Preferences

- After loading the data, a list of columns from the file will appear.

- Select the columns of interest in the Preferences section.

Setting Ranges

- Click the Set Range button.

- For each selected column, define the data range (e.g., 1-10 for numeric values or SVG, MVG for text values).

If you select the columns age or sex, the program will automatically recognize their special properties.

**Data Analysis**

Selecting Statistical Tests

- In the Tests section, check the tests you want to perform.

Available options:

- Mann-Whitney U test

- AUC

- AUC Interpolated

- Kolmogorov-Smirnov

- Kolmogorov-Smirnov Interpolated

- Average Difference Interpolated

**Running the Analysis**

- Click the Execute button to start the analysis.

The test results will be displayed in the results field and saved within the application.

**Adding Additional Curves**

- Set preferences and ranges for the new data group.

- Click the Add next curve button to add another curve to the existing chart.

**Generating Charts**

Creating Charts

- After the analysis, the program will automatically generate a survival curve chart.

- You can customize its appearance using the chart editing features.

Editing Charts

- Click the Edit Chart button to open the chart editing tool.

The editing options include:

- Adding and removing axis titles.

- Setting axis font.

- Changing chart style (e.g., black and white).

- Adjusting axis ranges.

- Enabling and disabling the legend.

**Generating Reports**

Creating a Report

- Click the Generate Report button.

In the dialog window, set:

- The report name.

- The output format (PDF or PNG).

- Whether the chart should be saved separately.

The report will be saved in the plots directory.

**Report Contents**

The generated report includes:

- Report title.

- Metadata such as the report name and generation date.

- Statistical test results.

- Survival curve chart.

**Ending Your Session**

Closing the Application

- Click the Close the POMOKA app button or press the ESC key.

- The application will ask for confirmation before closing.

Resetting Settings

- If you want to start a new analysis without closing the application, click the Break button in the execution section.

- The program will clear all current settings and results.

**Final Notes**

- Ensure that the input data is correctly formatted and contains all the required columns.

- Before generating a report, make sure the chart has been created and the data has been analyzed.

- **If you encounter any issues with the application, contact the administrator.**