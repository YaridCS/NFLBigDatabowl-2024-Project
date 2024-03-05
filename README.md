NFL Big Databowl 2024 Project

Description: 

The UConn Team's project for the Big Data Bowl 2024 innovatively analyzes NFL defensive performance by focusing on how defenses limit ballcarrier options. Utilizing given player tracking data by the NFL in a particular season, this project aims to quantify defensive positioning and effectiveness beyond traditional metrics. In our  approach, we divided the space around the ballcarrier into sectors, assessing the "danger" posed by defenders and the influence of blockers. By adjusting these sectors to account for biases and visualizing data through animations, we provided a nuanced, dynamic view of defensive play, providing valuable insights for improving football strategies and player evaluations.


Important Notes:

To get the overall dangers for a circle, create the circle inside circle interaction by calling interpret_play(game, play, week). Then call Get_Dangers_And_Centers(circle), which will return a list of the overall danger per frame on the play,followed be ballcarrier's location on every frame. To get the slicewise dangers, call Get_Dangers which resutns the same thing, except the first item it returns is a dictionary of slicewise dangers, rather than overall danger.

Note that it assumes all the data provided to us by the competition is in a file called "Data". We couldn't upload this to github due to the platform's space constraints.

You must run Cleaning.Py and the main included function clean() before doing anything else, everything else is powered by those cleaned files. You then need to run Perform Analysis.py and call the function analyze, which will then populate data so you can run the function inside Correlation.py as done in the main section of the notebooks.
